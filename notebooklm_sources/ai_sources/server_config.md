# Repository Context Group: server_config
# Source Repository: no-peace/Hoho_manager

### File: `server/src/config/database.ts`
```ts
import fs from "node:fs";
import path from "node:path";
import Database from "better-sqlite3";
import { env } from "./env.js";
import { migrations } from "./migrations.js";
import { logger } from "../utils/logger.js";

/**
 * Database access layer.
 *
 * The rest of the app never imports `better-sqlite3` directly. Everything goes
 * through the small query surface below, and every method is **async** even
 * though SQLite is synchronous. That deliberate choice means swapping in `pg`
 * later requires rewriting this file, not every repository.
 *
 *   SQLite   ->  parameters are `?` (positional) or `@name` (named)
 *   Postgres ->  parameters are `$1, $2, ...`
 *
 * Repositories therefore use named parameters where practical.
 */

/** Named (`{ userId: 1 }`) or positional (`[1]`) bind parameters. */
export type QueryParams = Record<string, unknown> | readonly unknown[];

export interface RunResult {
  changes: number;
  lastInsertRowid: number;
}

/** The dialect-neutral surface repositories are written against. */
export interface DatabaseClient {
  /** Run a statement that returns rows. */
  query<T>(sql: string, params?: QueryParams): Promise<T[]>;
  /** Run a statement expected to return at most one row. */
  get<T>(sql: string, params?: QueryParams): Promise<T | undefined>;
  /** Run a write statement. */
  run(sql: string, params?: QueryParams): Promise<RunResult>;
  /** Execute one or more statements with no parameters (DDL, pragmas). */
  exec(sql: string): Promise<void>;
  /** Wrap a synchronous callback in a transaction. */
  transaction<T>(fn: () => T): Promise<T>;
  /** Close the connection (graceful shutdown and the migrate CLI). */
  close(): Promise<void>;
}

let instance: Database.Database | null = null;

const log = logger.child("db");

/** Open (or reuse) the SQLite connection. */
const open = (): Database.Database => {
  if (instance) return instance;

  if (/^postgres/i.test(env.databaseUrl)) {
    throw new Error(
      "DATABASE_URL points at Postgres but no Postgres driver is wired up yet. " +
        "Implement a `pg` adapter in config/database.ts before switching.",
    );
  }

  fs.mkdirSync(path.dirname(env.databaseUrl), { recursive: true });

  const connection = new Database(env.databaseUrl);
  // WAL keeps reads from blocking writes; the rest are sane durability defaults.
  connection.pragma("journal_mode = WAL");
  connection.pragma("foreign_keys = ON");
  connection.pragma("busy_timeout = 5000");
  connection.pragma("synchronous = NORMAL");

  instance = connection;
  log.info(`Connected to SQLite at ${env.databaseUrl}`);
  return connection;
};

/** `better-sqlite3` takes positional args; named params arrive as one object. */
const spread = (params?: QueryParams): unknown[] =>
  params === undefined ? [] : Array.isArray(params) ? [...params] : [params];

export const db: DatabaseClient = {
  async query<T>(sql: string, params?: QueryParams): Promise<T[]> {
    return open().prepare(sql).all(...spread(params)) as T[];
  },

  async get<T>(sql: string, params?: QueryParams): Promise<T | undefined> {
    return open().prepare(sql).get(...spread(params)) as T | undefined;
  },

  async run(sql: string, params?: QueryParams): Promise<RunResult> {
    const result = open().prepare(sql).run(...spread(params));
    return {
      changes: result.changes,
      lastInsertRowid: Number(result.lastInsertRowid),
    };
  },

  async exec(sql: string): Promise<void> {
    open().exec(sql);
  },

  async transaction<T>(fn: () => T): Promise<T> {
    // `better-sqlite3` is synchronous, so the callback must be too — keep
    // transactional work free of `await`.
    return open().transaction(fn)();
  },

  async close(): Promise<void> {
    if (!instance) return;
    instance.close();
    instance = null;
    log.info("Closed SQLite connection");
  },
};

interface MigrationRow {
  id: string;
}

/** Apply any migrations whose id is not yet recorded. Safe to run every boot. */
export const runMigrations = async (): Promise<{ applied: number }> => {
  const connection = open();

  connection.exec(
    `CREATE TABLE IF NOT EXISTS schema_migrations (
       id         TEXT PRIMARY KEY,
       applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
     );`,
  );

  const applied = new Set(
    connection
      .prepare("SELECT id FROM schema_migrations")
      .all()
      .map((row) => (row as MigrationRow).id),
  );

  let appliedCount = 0;
  for (const migration of migrations) {
    if (applied.has(migration.id)) continue;

    log.info(`Applying migration ${migration.id}`);
    connection.transaction(() => {
      connection.exec(migration.sql);
      connection.prepare("INSERT INTO schema_migrations (id) VALUES (?)").run(migration.id);
    })();
    appliedCount += 1;
  }

  return { applied: appliedCount };
};

interface CountRow {
  count: number;
}

/** Ensure the schema exists and a usable admin row is present. */
export const initializeDatabase = async (): Promise<DatabaseClient> => {
  await runMigrations();

  const admin = await db.get<{ id: number }>(
    "SELECT id FROM users WHERE discord_id = @discordId",
    { discordId: "local-admin" },
  );

  if (!admin) {
    await db.run(
      `INSERT INTO users (discord_id, username, role)
       VALUES (@discordId, @username, @role)`,
      { discordId: "local-admin", username: "Local Admin", role: "admin" },
    );
    log.info("Seeded local admin user (discord_id=local-admin)");
  }

  return db;
};

/** Count helper used by the health endpoint and the migrate CLI. */
export const countUsers = async (): Promise<number> => {
  const row = await db.get<CountRow>("SELECT COUNT(*) AS count FROM users");
  return row?.count ?? 0;
};

```

### File: `server/src/config/env.ts`
```ts
import path from "node:path";
import { fileURLToPath } from "node:url";
import { config as loadDotenv } from "dotenv";

/**
 * Centralised, validated environment configuration.
 *
 * Every other module imports `env` from here instead of touching
 * `process.env` directly, so a missing value surfaces in one place with a
 * useful message rather than as `undefined` deep inside a request handler.
 */

const here = path.dirname(fileURLToPath(import.meta.url));
/** `server/` — the package root (config/ -> src/ -> server/). */
export const serverRoot = path.resolve(here, "../..");

// Load `server/.env` explicitly so the app behaves the same no matter which
// directory it was started from.
loadDotenv({ path: path.join(serverRoot, ".env") });

const str = (key: string, fallback?: string): string | undefined => {
  const raw = process.env[key];
  return raw === undefined || raw === "" ? fallback : raw;
};

const int = (key: string, fallback: number): number => {
  const raw = str(key);
  if (raw === undefined) return fallback;
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const nodeEnv = str("NODE_ENV", "development") ?? "development";
const isProd = nodeEnv === "production";

/** Resolve `DATABASE_URL` to an absolute path (Postgres URLs are passed through). */
const resolveDatabase = (): string => {
  const value = str("DATABASE_URL", "./data/dev.sqlite") ?? "./data/dev.sqlite";
  if (/^postgres(ql)?:\/\//i.test(value)) return value;
  return path.isAbsolute(value) ? value : path.join(serverRoot, value);
};

export interface DiscordEnv {
  readonly publicKey: string | undefined;
  readonly applicationId: string | undefined;
  readonly botToken: string | undefined;
}

export interface RateLimitEnv {
  readonly windowMs: number;
  readonly max: number;
}

export interface Env {
  readonly nodeEnv: string;
  readonly isProd: boolean;
  readonly isDev: boolean;
  readonly port: number;
  readonly clientOrigins: readonly string[];
  readonly databaseUrl: string;
  readonly discord: DiscordEnv;
  readonly adminApiKey: string;
  readonly encryptionKey: string | undefined;
  readonly rateLimit: RateLimitEnv;
}

export const env: Env = Object.freeze({
  nodeEnv,
  isProd,
  isDev: !isProd,
  port: int("PORT", 3001),
  clientOrigins: Object.freeze(
    (str("CLIENT_ORIGIN", "http://localhost:5173") ?? "")
      .split(",")
      .map((origin) => origin.trim())
      .filter(Boolean),
  ),
  databaseUrl: resolveDatabase(),
  discord: Object.freeze({
    publicKey: str("DISCORD_PUBLIC_KEY"),
    applicationId: str("DISCORD_APPLICATION_ID"),
    botToken: str("DISCORD_BOT_TOKEN"),
  }),
  adminApiKey: str("ADMIN_API_KEY", "dev-admin-key") ?? "dev-admin-key",
  encryptionKey: str("ENCRYPTION_KEY"),
  rateLimit: Object.freeze({
    windowMs: int("RATE_LIMIT_WINDOW_MS", 60_000),
    max: int("RATE_LIMIT_MAX", 120),
  }),
});

/**
 * Validate the environment and return human-readable warnings.
 *
 * We warn instead of throwing so the editor can still be developed against a
 * server that has no Discord credentials yet.
 */
export const validateEnv = (): string[] => {
  const warnings: string[] = [];

  if (!env.discord.publicKey) {
    warnings.push(
      "DISCORD_PUBLIC_KEY is not set — /api/interactions will reject every request. " +
        "Set it before pointing Discord at this server.",
    );
  }
  if (!env.discord.botToken) {
    warnings.push(
      "DISCORD_BOT_TOKEN is not set — bot-mode sending and all actions are disabled.",
    );
  }
  if (!env.discord.applicationId) {
    warnings.push(
      "DISCORD_APPLICATION_ID is not set — application command routes are limited.",
    );
  }
  if (env.isProd && env.adminApiKey === "dev-admin-key") {
    warnings.push(
      "ADMIN_API_KEY is still the development default. Change it before deploying.",
    );
  }
  if (env.isProd && !env.encryptionKey) {
    warnings.push(
      "ENCRYPTION_KEY is not set. Stored bot tokens are encrypted with a key derived " +
        "from ADMIN_API_KEY; set a dedicated key before deploying.",
    );
  }

  return warnings;
};

```

### File: `server/src/config/migrate.ts`
```ts
/**
 * Migration CLI: `npm run migrate`
 *
 * Creates the SQLite file if needed, applies pending migrations, seeds the local
 * admin user, then exits. Safe to run repeatedly.
 */
import { countUsers, db, initializeDatabase } from "./database.js";
import { env, validateEnv } from "./env.js";
import { logger } from "../utils/logger.js";

const main = async (): Promise<void> => {
  logger.info(`Environment: ${env.nodeEnv}`);
  for (const warning of validateEnv()) logger.warn(warning);

  await initializeDatabase();

  logger.info(`Database ready — ${await countUsers()} user(s) present.`);
  await db.close();
};

main().catch((error: unknown) => {
  logger.error("Migration failed", error);
  process.exitCode = 1;
});

```

### File: `server/src/config/migrations.ts`
```ts
/**
 * Ordered, idempotent migrations.
 *
 * Each entry runs exactly once and is recorded in `schema_migrations`, so adding
 * a migration means appending an object here — never editing an applied one.
 *
 * The SQL sticks to a conservative SQLite subset (INTEGER/TEXT, explicit
 * indices, foreign keys) so it maps cleanly onto PostgreSQL later.
 * `config/database.ts` is the only place that knows the dialect.
 */

export interface Migration {
  id: string;
  sql: string;
}

export const migrations: readonly Migration[] = [
  {
    id: "001_init",
    sql: `
      -- Users. Single admin today, real accounts in Phase 4.
      CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id    TEXT    UNIQUE NOT NULL,
        username      TEXT    NOT NULL,
        avatar        TEXT,
        role          TEXT    NOT NULL DEFAULT 'admin',   -- 'admin' | 'editor' | 'viewer'
        created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      -- Saved webhook destinations. The URL contains a token, so it is treated
      -- as a credential and only ever returned to its owner.
      CREATE TABLE IF NOT EXISTS webhook_profiles (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name        TEXT    NOT NULL,
        url         TEXT    NOT NULL,
        guild_id    TEXT,
        channel_id  TEXT,
        avatar_url  TEXT,
        is_default  INTEGER NOT NULL DEFAULT 0,
        created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      -- Bot credentials. The token is encrypted at rest (AES-256-GCM).
      CREATE TABLE IF NOT EXISTS bot_profiles (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name             TEXT    NOT NULL,
        token_encrypted  TEXT    NOT NULL,
        public_key       TEXT    NOT NULL,
        application_id   TEXT    NOT NULL,
        default_guild_id TEXT,
        is_active        INTEGER NOT NULL DEFAULT 1,
        created_at       TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at       TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      -- Message templates. "data" holds a full Discohook-compatible QueryData blob.
      CREATE TABLE IF NOT EXISTS templates (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name              TEXT    NOT NULL,
        description       TEXT,
        data              TEXT    NOT NULL,
        preview_image_url TEXT,
        is_public         INTEGER NOT NULL DEFAULT 0,
        created_at        TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at        TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      -- Actions bound to a component's custom_id, scoped to a template.
      CREATE TABLE IF NOT EXISTS action_definitions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        template_id     INTEGER REFERENCES templates(id) ON DELETE CASCADE,
        custom_id       TEXT    NOT NULL,
        action_type     TEXT    NOT NULL,
        config          TEXT    NOT NULL DEFAULT '{}',
        execution_order INTEGER NOT NULL DEFAULT 0,
        created_at      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      -- Audit trail for every executed interaction.
      CREATE TABLE IF NOT EXISTS action_logs (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        action_definition_id INTEGER REFERENCES action_definitions(id) ON DELETE SET NULL,
        interaction_id       TEXT    NOT NULL,
        user_id              TEXT    NOT NULL,
        guild_id             TEXT,
        channel_id           TEXT,
        status               TEXT    NOT NULL,
        response             TEXT,
        executed_at          TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      -- Multi-step flow state, keyed by interaction token until it expires.
      CREATE TABLE IF NOT EXISTS flow_states (
        token       TEXT PRIMARY KEY,
        template_id INTEGER REFERENCES templates(id) ON DELETE CASCADE,
        step        INTEGER NOT NULL DEFAULT 0,
        variables   TEXT NOT NULL DEFAULT '{}',
        expires_at  TEXT NOT NULL,
        created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      CREATE INDEX IF NOT EXISTS idx_templates_user    ON templates(user_id);
      CREATE INDEX IF NOT EXISTS idx_actions_template  ON action_definitions(template_id);
      CREATE INDEX IF NOT EXISTS idx_actions_custom_id ON action_definitions(custom_id);
      CREATE INDEX IF NOT EXISTS idx_logs_interaction  ON action_logs(interaction_id);
      CREATE INDEX IF NOT EXISTS idx_webhooks_user     ON webhook_profiles(user_id);
    `,
  },
];

```

