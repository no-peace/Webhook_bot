# Repository Context Group: server_repositories
# Source Repository: no-peace/Hoho_manager

### File: `server/src/repositories/actionRepository.ts`
```ts
import type {
  ActionConfig,
  ActionDefinitionRecord,
  ActionType,
  FlowRegistration,
  StoredActionDefinition,
} from "@dmb/shared";
import { BaseRepository, parseJson, parseJsonList } from "./baseRepository.js";

/**
 * Action definitions + the execution audit log.
 *
 * A definition binds a component `custom_id` to a handler and its config.
 * Several definitions can share a `custom_id` — they run in `execution_order`,
 * which is how multi-step flows are expressed.
 */

interface ActionRow {
  id: number;
  template_id: number | null;
  custom_id: string;
  action_type: string;
  config: string;
  execution_order: number;
  created_at: string;
}

export interface ActionLogRow {
  id: number;
  action_definition_id: number | null;
  interaction_id: string;
  user_id: string;
  guild_id: string | null;
  channel_id: string | null;
  status: string;
  response: string | null;
  executed_at: string;
}

export interface CreateActionInput {
  templateId?: number | null;
  customId: string;
  actionType: ActionType;
  config?: ActionConfig;
  executionOrder?: number;
}

export interface LogActionInput {
  actionDefinitionId?: number | null;
  interactionId: string;
  userId: string;
  guildId?: string | null;
  channelId?: string | null;
  status: "success" | "failed" | "pending";
  response?: unknown;
}

const hydrate = (row: ActionRow | undefined): ActionDefinitionRecord | undefined =>
  parseJson<ActionDefinitionRecord>(row as unknown as ActionDefinitionRecord, ["config"]);

export class ActionRepository extends BaseRepository {
  async create({
    templateId = null,
    customId,
    actionType,
    config = {},
    executionOrder = 0,
  }: CreateActionInput): Promise<ActionDefinitionRecord | undefined> {
    const { lastInsertRowid } = await this.db.run(
      `INSERT INTO action_definitions (template_id, custom_id, action_type, config, execution_order)
       VALUES (@templateId, @customId, @actionType, @config, @executionOrder)`,
      {
        templateId,
        customId,
        actionType,
        config: JSON.stringify(config ?? {}),
        executionOrder,
      },
    );
    return this.findById(lastInsertRowid);
  }

  /** Replace every action bound to a template in one call. */
  async replaceForTemplate(
    templateId: number,
    actions: StoredActionDefinition[] = [],
  ): Promise<ActionDefinitionRecord[]> {
    await this.deleteByTemplate(templateId);

    const created: ActionDefinitionRecord[] = [];
    for (const [index, action] of actions.entries()) {
      const definition = await this.create({
        templateId,
        customId: action.customId,
        actionType: action.actionType,
        config: action.config ?? {},
        executionOrder: action.executionOrder ?? index,
      });
      if (definition) created.push(definition);
    }
    return created;
  }

  async findById(id: number): Promise<ActionDefinitionRecord | undefined> {
    const row = await this.db.get<ActionRow>(
      "SELECT * FROM action_definitions WHERE id = @id",
      { id },
    );
    return hydrate(row);
  }

  /**
   * All steps bound to a custom_id, in execution order.
   *
   * Precedence matters: a flow registered at send time (`template_id IS NULL`,
   * the freshest definition of what this button does) wins over steps owned by a
   * saved template. Without that, sending a template-backed message ad-hoc would
   * execute both sets and double up every action.
   */
  async findByCustomId(customId: string): Promise<ActionDefinitionRecord[]> {
    const registered = await this.db.query<ActionRow>(
      `SELECT * FROM action_definitions
        WHERE custom_id = @customId AND template_id IS NULL
        ORDER BY execution_order ASC`,
      { customId },
    );
    if (registered.length > 0) {
      return parseJsonList(registered as unknown as ActionDefinitionRecord[], ["config"]);
    }

    const rows = await this.db.query<ActionRow>(
      "SELECT * FROM action_definitions WHERE custom_id = @customId ORDER BY execution_order ASC",
      { customId },
    );
    return parseJsonList(rows as unknown as ActionDefinitionRecord[], ["config"]);
  }

  /**
   * Register the flows an ad-hoc message ships with, replacing any previous
   * ad-hoc registration for the same components. Template-owned rows are left
   * untouched.
   */
  async registerFlows(flows: FlowRegistration[] = []): Promise<number> {
    let written = 0;

    for (const flow of flows) {
      await this.db.run(
        "DELETE FROM action_definitions WHERE custom_id = @customId AND template_id IS NULL",
        { customId: flow.customId },
      );

      for (const [index, step] of (flow.steps ?? []).entries()) {
        await this.create({
          templateId: null,
          customId: flow.customId,
          actionType: step.type,
          config: step.config ?? {},
          executionOrder: index,
        });
        written += 1;
      }
    }

    return written;
  }

  async listByTemplate(templateId: number): Promise<ActionDefinitionRecord[]> {
    const rows = await this.db.query<ActionRow>(
      `SELECT * FROM action_definitions
        WHERE template_id = @templateId
        ORDER BY execution_order ASC`,
      { templateId },
    );
    return parseJsonList(rows as unknown as ActionDefinitionRecord[], ["config"]);
  }

  async deleteByTemplate(templateId: number): Promise<number> {
    const { changes } = await this.db.run(
      "DELETE FROM action_definitions WHERE template_id = @templateId",
      { templateId },
    );
    return changes;
  }

  /** Append to the audit trail. Never let a log failure break an interaction. */
  async log({
    actionDefinitionId = null,
    interactionId,
    userId,
    guildId = null,
    channelId = null,
    status,
    response = null,
  }: LogActionInput): Promise<void> {
    try {
      await this.db.run(
        `INSERT INTO action_logs
           (action_definition_id, interaction_id, user_id, guild_id, channel_id, status, response)
         VALUES
           (@actionDefinitionId, @interactionId, @userId, @guildId, @channelId, @status, @response)`,
        {
          actionDefinitionId,
          interactionId,
          userId,
          guildId,
          channelId,
          status,
          response: response == null ? null : JSON.stringify(response),
        },
      );
    } catch {
      // Logging is best-effort; a failure here must not fail the interaction.
    }
  }

  async listLogs({
    limit = 50,
    offset = 0,
  }: { limit?: number; offset?: number } = {}): Promise<ActionLogRow[]> {
    const rows = await this.db.query<ActionLogRow>(
      "SELECT * FROM action_logs ORDER BY executed_at DESC LIMIT @limit OFFSET @offset",
      { limit, offset },
    );
    return parseJsonList(rows as unknown as ActionLogRow[], ["response"]);
  }
}

export const actionRepository = new ActionRepository();

```

### File: `server/src/repositories/baseRepository.ts`
```ts
import { db, type DatabaseClient } from "../config/database.js";

/**
 * Shared plumbing for repositories.
 *
 * Subclasses get the query surface (`this.db`) plus the two helpers every
 * repository needs: turning JSON columns into objects on read, and building a
 * partial `UPDATE` from a whitelist of fields.
 *
 * Parameter style is named (`@name`). Migrating to Postgres means changing
 * `config/database.ts` and the placeholder translation in one place.
 */
export abstract class BaseRepository {
  protected readonly db: DatabaseClient = db;
}

/**
 * Parse the given JSON columns on a row.
 *
 * The column genuinely changes type (`string` -> `object`), so this is the one
 * place where a cast is unavoidable — callers pass the domain type they expect.
 */
export const parseJson = <T>(row: T | undefined, columns: readonly string[]): T | undefined => {
  if (!row) return undefined;

  const result = { ...(row as Record<string, unknown>) };
  for (const column of columns) {
    const value = result[column];
    if (typeof value === "string") {
      try {
        result[column] = JSON.parse(value) as unknown;
      } catch {
        result[column] = null;
      }
    }
  }
  return result as T;
};

/** Map a list of rows through {@link parseJson}. */
export const parseJsonList = <T>(rows: T[], columns: readonly string[]): T[] =>
  rows.map((row) => parseJson(row, columns) as T);

/**
 * Build `SET a = @a, b = @b` for the keys present in `data`, restricted to
 * `allowed`. Prevents mass-assignment from request bodies.
 */
export const buildUpdate = (
  data: Record<string, unknown>,
  allowed: readonly string[],
): string | null => {
  const keys = allowed.filter((key) => data[key] !== undefined);
  if (keys.length === 0) return null;
  return keys.map((key) => `${key} = @${key}`).join(", ");
};

```

### File: `server/src/repositories/flowRepository.ts`
```ts
import type { FlowStateRecord } from "@dmb/shared";
import { BaseRepository, parseJson } from "./baseRepository.js";

/**
 * Short-lived state for multi-step interactions (modals, wizard-like flows).
 *
 * Discord interaction tokens are valid for 15 minutes, so entries are keyed by
 * token and carry an `expires_at`; {@link pruneExpired} clears stale rows.
 */

/** A row as stored: `variables` is still a JSON string. */
export interface FlowRow {
  token: string;
  template_id: number | null;
  step: number;
  variables: string;
  expires_at: string;
  created_at: string;
}

export interface SaveFlowInput {
  token: string;
  templateId?: number | null;
  step?: number;
  variables?: Record<string, unknown>;
  /** Defaults to Discord's 15-minute interaction-token lifetime. */
  ttlSeconds?: number;
}

const DEFAULT_TTL_SECONDS = 900;

const hydrate = (row: FlowRow | undefined): FlowStateRecord | undefined =>
  parseJson<FlowStateRecord>(row as unknown as FlowStateRecord, ["variables"]);

export class FlowRepository extends BaseRepository {
  async save({
    token,
    templateId = null,
    step = 0,
    variables = {},
    ttlSeconds = DEFAULT_TTL_SECONDS,
  }: SaveFlowInput): Promise<FlowStateRecord | undefined> {
    const expiresAt = new Date(Date.now() + ttlSeconds * 1000).toISOString();

    await this.db.run(
      `INSERT INTO flow_states (token, template_id, step, variables, expires_at)
       VALUES (@token, @templateId, @step, @variables, @expiresAt)
       ON CONFLICT(token) DO UPDATE SET
         step       = @step,
         variables  = @variables,
         expires_at = @expiresAt`,
      { token, templateId, step, variables: JSON.stringify(variables ?? {}), expiresAt },
    );
    return this.get(token);
  }

  async get(token: string): Promise<FlowStateRecord | undefined> {
    const row = await this.db.get<FlowRow>(
      "SELECT * FROM flow_states WHERE token = @token AND expires_at > CURRENT_TIMESTAMP",
      { token },
    );
    return hydrate(row);
  }

  async advance(
    token: string,
    { variables }: { variables?: Record<string, unknown> } = {},
  ): Promise<FlowStateRecord | undefined> {
    const existing = await this.get(token);
    if (!existing) return undefined;

    return this.save({
      token,
      templateId: existing.template_id,
      step: existing.step + 1,
      variables: variables ? { ...existing.variables, ...variables } : existing.variables,
    });
  }

  async remove(token: string): Promise<boolean> {
    const { changes } = await this.db.run("DELETE FROM flow_states WHERE token = @token", {
      token,
    });
    return changes > 0;
  }

  async pruneExpired(): Promise<number> {
    const { changes } = await this.db.run(
      "DELETE FROM flow_states WHERE expires_at <= CURRENT_TIMESTAMP",
    );
    return changes;
  }
}

export const flowRepository = new FlowRepository();

```

### File: `server/src/repositories/index.ts`
```ts
/**
 * Single import point for persistence.
 *
 * Services receive this object rather than importing repositories individually,
 * which keeps the dependency direction one-way (routes -> services ->
 * repositories) and makes swapping the storage backend a single-file change.
 *
 * The interface is declared explicitly rather than inferred so the emitted
 * declaration file stays nameable — an inferred `Object.freeze({...})` type would
 * leak the classes' private members and break `declaration: true`.
 */
import { actionRepository, ActionRepository } from "./actionRepository.js";
import { flowRepository, FlowRepository } from "./flowRepository.js";
import {
  botProfileRepository,
  BotProfileRepository,
  webhookProfileRepository,
  WebhookProfileRepository,
} from "./profileRepository.js";
import { templateRepository, TemplateRepository } from "./templateRepository.js";
import { userRepository, UserRepository } from "./userRepository.js";

export interface Repositories {
  users: UserRepository;
  templates: TemplateRepository;
  actions: ActionRepository;
  flows: FlowRepository;
  webhookProfiles: WebhookProfileRepository;
  botProfiles: BotProfileRepository;
}

export const repositories: Repositories = Object.freeze({
  users: userRepository,
  templates: templateRepository,
  actions: actionRepository,
  flows: flowRepository,
  webhookProfiles: webhookProfileRepository,
  botProfiles: botProfileRepository,
});

export {
  actionRepository,
  ActionRepository,
  botProfileRepository,
  BotProfileRepository,
  flowRepository,
  FlowRepository,
  templateRepository,
  TemplateRepository,
  userRepository,
  UserRepository,
  webhookProfileRepository,
  WebhookProfileRepository,
};

export default repositories;

```

### File: `server/src/repositories/profileRepository.ts`
```ts
import type { BotProfileRecord, WebhookProfileRecord } from "@dmb/shared";
import { decrypt, encrypt } from "../utils/crypto.js";
import { BaseRepository, buildUpdate } from "./baseRepository.js";

/**
 * Webhook destinations.
 *
 * The URL contains a token, which is why a webhook can only ever *send*. It is
 * still treated as a credential: never logged, and only returned to the owner.
 */

export interface CreateWebhookInput {
  userId: number;
  name: string;
  url: string;
  guildId?: string | null;
  channelId?: string | null;
  avatarUrl?: string | null;
  isDefault?: number;
}

export type UpdateWebhookInput = Partial<
  Pick<WebhookProfileRecord, "name" | "url" | "guild_id" | "channel_id" | "avatar_url" | "is_default">
>;

const WEBHOOK_UPDATABLE = [
  "name",
  "url",
  "guild_id",
  "channel_id",
  "avatar_url",
  "is_default",
] as const;

export class WebhookProfileRepository extends BaseRepository {
  async create({
    userId,
    name,
    url,
    guildId = null,
    channelId = null,
    avatarUrl = null,
    isDefault = 0,
  }: CreateWebhookInput): Promise<WebhookProfileRecord | undefined> {
    const { lastInsertRowid } = await this.db.run(
      `INSERT INTO webhook_profiles (user_id, name, url, guild_id, channel_id, avatar_url, is_default)
       VALUES (@userId, @name, @url, @guildId, @channelId, @avatarUrl, @isDefault)`,
      { userId, name, url, guildId, channelId, avatarUrl, isDefault: isDefault ? 1 : 0 },
    );
    return this.findById(lastInsertRowid);
  }

  async findById(id: number): Promise<WebhookProfileRecord | undefined> {
    return this.db.get<WebhookProfileRecord>(
      "SELECT * FROM webhook_profiles WHERE id = @id",
      { id },
    );
  }

  async listByUser(userId: number): Promise<WebhookProfileRecord[]> {
    return this.db.query<WebhookProfileRecord>(
      `SELECT * FROM webhook_profiles
        WHERE user_id = @userId
        ORDER BY is_default DESC, created_at ASC`,
      { userId },
    );
  }

  async findDefault(userId: number): Promise<WebhookProfileRecord | undefined> {
    return this.db.get<WebhookProfileRecord>(
      "SELECT * FROM webhook_profiles WHERE user_id = @userId AND is_default = 1 LIMIT 1",
      { userId },
    );
  }

  async update(
    id: number,
    data: UpdateWebhookInput,
  ): Promise<WebhookProfileRecord | undefined> {
    const setClause = buildUpdate(data as Record<string, unknown>, WEBHOOK_UPDATABLE);
    if (!setClause) return this.findById(id);

    await this.db.run(
      `UPDATE webhook_profiles SET ${setClause}, updated_at = CURRENT_TIMESTAMP WHERE id = @id`,
      { ...data, id },
    );
    return this.findById(id);
  }

  /** Promote one profile to default, demoting any previous default. */
  async setDefault(id: number, userId: number): Promise<WebhookProfileRecord | undefined> {
    await this.db.run(
      "UPDATE webhook_profiles SET is_default = 0, updated_at = CURRENT_TIMESTAMP WHERE user_id = @userId",
      { userId },
    );
    await this.db.run(
      `UPDATE webhook_profiles
          SET is_default = 1, updated_at = CURRENT_TIMESTAMP
        WHERE id = @id AND user_id = @userId`,
      { id, userId },
    );
    return this.findById(id);
  }

  async delete(id: number): Promise<boolean> {
    const { changes } = await this.db.run("DELETE FROM webhook_profiles WHERE id = @id", { id });
    return changes > 0;
  }
}

/* ── Bot profiles ─────────────────────────────────────────────────────────── */

/** A row as stored: includes the encrypted token. Never returned to clients. */
export interface BotRow extends BotProfileRecord {
  token_encrypted: string;
}

/** What the API returns: metadata plus a "is a token stored?" flag. */
export type PublicBotProfile = BotProfileRecord & { has_token: boolean };

export interface CreateBotInput {
  userId: number;
  name: string;
  /** Plaintext token; encrypted before it touches the database. */
  token: string;
  publicKey: string;
  applicationId: string;
  defaultGuildId?: string | null;
  isActive?: number;
}

export interface UpdateBotInput {
  name?: string;
  token?: string;
  public_key?: string;
  application_id?: string;
  default_guild_id?: string | null;
  is_active?: number;
}

const BOT_UPDATABLE = [
  "name",
  "public_key",
  "application_id",
  "default_guild_id",
  "is_active",
] as const;

/**
 * Bot credentials.
 *
 * The token is encrypted with AES-256-GCM before it touches the database, and
 * every read strips it. Use {@link revealToken} when a request genuinely needs to
 * authenticate against Discord — never to return to a client.
 */
export class BotProfileRepository extends BaseRepository {
  private toPublic(row: BotRow | undefined): PublicBotProfile | undefined {
    if (!row) return undefined;
    const { token_encrypted, ...safe } = row;
    return { ...safe, has_token: Boolean(token_encrypted) };
  }

  async create({
    userId,
    name,
    token,
    publicKey,
    applicationId,
    defaultGuildId = null,
    isActive = 1,
  }: CreateBotInput): Promise<PublicBotProfile | undefined> {
    const { lastInsertRowid } = await this.db.run(
      `INSERT INTO bot_profiles
         (user_id, name, token_encrypted, public_key, application_id, default_guild_id, is_active)
       VALUES
         (@userId, @name, @token, @publicKey, @applicationId, @defaultGuildId, @isActive)`,
      {
        userId,
        name,
        token: encrypt(token),
        publicKey,
        applicationId,
        defaultGuildId,
        isActive: isActive ? 1 : 0,
      },
    );
    return this.findById(lastInsertRowid);
  }

  async findById(id: number): Promise<PublicBotProfile | undefined> {
    const row = await this.db.get<BotRow>("SELECT * FROM bot_profiles WHERE id = @id", { id });
    return this.toPublic(row);
  }

  /** Raw row including the encrypted token — internal use only. */
  async findRawById(id: number): Promise<BotRow | undefined> {
    return this.db.get<BotRow>("SELECT * FROM bot_profiles WHERE id = @id", { id });
  }

  /** Decrypt and return the bot token for an outgoing Discord request. */
  async revealToken(id: number): Promise<string | null> {
    const row = await this.findRawById(id);
    if (!row) return null;
    return decrypt(row.token_encrypted);
  }

  async findActiveByUser(userId: number): Promise<PublicBotProfile | undefined> {
    const row = await this.db.get<BotRow>(
      `SELECT * FROM bot_profiles
        WHERE user_id = @userId AND is_active = 1
        ORDER BY id ASC
        LIMIT 1`,
      { userId },
    );
    return this.toPublic(row);
  }

  async listByUser(userId: number): Promise<PublicBotProfile[]> {
    const rows = await this.db.query<BotRow>(
      "SELECT * FROM bot_profiles WHERE user_id = @userId ORDER BY created_at ASC",
      { userId },
    );
    return rows.map((row) => this.toPublic(row) as PublicBotProfile);
  }

  async update(id: number, data: UpdateBotInput): Promise<PublicBotProfile | undefined> {
    const setClause = buildUpdate(data as Record<string, unknown>, BOT_UPDATABLE);
    const params: Record<string, unknown> = { ...data, id };
    let tokenClause = "";

    // A supplied token is re-encrypted; an absent one leaves the stored value alone.
    if (data.token) {
      tokenClause = ", token_encrypted = @token_encrypted";
      params.token_encrypted = encrypt(data.token);
    }

    if (!setClause && !tokenClause) return this.findById(id);

    await this.db.run(
      `UPDATE bot_profiles
          SET ${setClause ?? "id = id"}${tokenClause}, updated_at = CURRENT_TIMESTAMP
        WHERE id = @id`,
      params,
    );
    return this.findById(id);
  }

  async delete(id: number): Promise<boolean> {
    const { changes } = await this.db.run("DELETE FROM bot_profiles WHERE id = @id", { id });
    return changes > 0;
  }
}

export const webhookProfileRepository = new WebhookProfileRepository();
export const botProfileRepository = new BotProfileRepository();

```

### File: `server/src/repositories/templateRepository.ts`
```ts
import type { QueryData, TemplateRecord } from "@dmb/shared";
import { BaseRepository, buildUpdate, parseJson } from "./baseRepository.js";

/**
 * Message templates.
 *
 * `data` is the full Discohook-compatible `QueryData` document, serialised to a
 * TEXT column and parsed back on read so callers always deal with plain objects.
 */

/** A row as stored: `data` is still a JSON string. */
export interface TemplateRow {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  data: string;
  preview_image_url: string | null;
  is_public: number;
  created_at: string;
  updated_at: string;
}

/** The list view omits the (potentially large) document body. */
export interface TemplateSummary {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  preview_image_url: string | null;
  is_public: number;
  created_at: string;
  updated_at: string;
}

export interface CreateTemplateInput {
  userId: number;
  name: string;
  description?: string | null;
  data: QueryData | Record<string, unknown>;
  previewImageUrl?: string | null;
  isPublic?: number;
}

export type UpdateTemplateInput = Partial<
  Pick<TemplateRow, "name" | "description" | "preview_image_url" | "is_public">
>;

const UPDATABLE = ["name", "description", "preview_image_url", "is_public"] as const;

const hydrate = (row: TemplateRow | undefined): TemplateRecord | undefined =>
  parseJson<TemplateRecord>(row as unknown as TemplateRecord, ["data"]);

export class TemplateRepository extends BaseRepository {
  async create({
    userId,
    name,
    description = null,
    data,
    previewImageUrl = null,
    isPublic = 0,
  }: CreateTemplateInput): Promise<TemplateRecord | undefined> {
    const { lastInsertRowid } = await this.db.run(
      `INSERT INTO templates (user_id, name, description, data, preview_image_url, is_public)
       VALUES (@userId, @name, @description, @data, @previewImageUrl, @isPublic)`,
      {
        userId,
        name,
        description,
        data: JSON.stringify(data ?? {}),
        previewImageUrl,
        isPublic: isPublic ? 1 : 0,
      },
    );
    return this.findById(lastInsertRowid);
  }

  async findById(id: number): Promise<TemplateRecord | undefined> {
    const row = await this.db.get<TemplateRow>("SELECT * FROM templates WHERE id = @id", { id });
    return hydrate(row);
  }

  async findByUser(userId: number): Promise<TemplateSummary[]> {
    return this.db.query<TemplateSummary>(
      `SELECT id, user_id, name, description, preview_image_url, is_public, created_at, updated_at
         FROM templates
        WHERE user_id = @userId
        ORDER BY updated_at DESC`,
      { userId },
    );
  }

  /** Lightweight substring search — swap for FTS/`ILIKE` when moving to Postgres. */
  async search({
    userId,
    q,
    limit = 25,
  }: {
    userId: number;
    q?: string | null;
    limit?: number;
  }): Promise<TemplateSummary[]> {
    return this.db.query<TemplateSummary>(
      `SELECT id, user_id, name, description, preview_image_url, is_public, created_at, updated_at
         FROM templates
        WHERE user_id = @userId
          AND (@q IS NULL OR name LIKE @like OR description LIKE @like)
        ORDER BY updated_at DESC
        LIMIT @limit`,
      { userId, q: q ?? null, like: `%${q ?? ""}%`, limit },
    );
  }

  /** Replace the stored message document (`data`). */
  async updateData(
    id: number,
    data: QueryData | Record<string, unknown>,
  ): Promise<TemplateRecord | undefined> {
    await this.db.run(
      "UPDATE templates SET data = @data, updated_at = CURRENT_TIMESTAMP WHERE id = @id",
      { data: JSON.stringify(data ?? {}), id },
    );
    return this.findById(id);
  }

  async update(id: number, data: UpdateTemplateInput): Promise<TemplateRecord | undefined> {
    const setClause = buildUpdate(data as Record<string, unknown>, UPDATABLE);
    if (!setClause) return this.findById(id);

    await this.db.run(
      `UPDATE templates SET ${setClause}, updated_at = CURRENT_TIMESTAMP WHERE id = @id`,
      { ...data, id },
    );
    return this.findById(id);
  }

  async delete(id: number): Promise<boolean> {
    const { changes } = await this.db.run("DELETE FROM templates WHERE id = @id", { id });
    return changes > 0;
  }
}

export const templateRepository = new TemplateRepository();

```

### File: `server/src/repositories/userRepository.ts`
```ts
import type { UserRecord, UserRole } from "@dmb/shared";
import { BaseRepository, buildUpdate } from "./baseRepository.js";

/**
 * Users repository.
 *
 * There is a single `local-admin` row today, but the shape is already
 * multi-user: `role` is what the RBAC middleware checks, so adding real accounts
 * later is additive.
 */

export interface CreateUserInput {
  discordId: string;
  username: string;
  avatar?: string | null;
  role?: UserRole;
}

export type UpdateUserInput = Partial<Pick<UserRecord, "username" | "avatar" | "role">>;

const UPDATABLE = ["username", "avatar", "role"] as const;

export class UserRepository extends BaseRepository {
  async findById(id: number): Promise<UserRecord | undefined> {
    return this.db.get<UserRecord>("SELECT * FROM users WHERE id = @id", { id });
  }

  async findByDiscordId(discordId: string): Promise<UserRecord | undefined> {
    return this.db.get<UserRecord>("SELECT * FROM users WHERE discord_id = @discordId", {
      discordId,
    });
  }

  async list(): Promise<UserRecord[]> {
    return this.db.query<UserRecord>("SELECT * FROM users ORDER BY created_at ASC");
  }

  async create({
    discordId,
    username,
    avatar = null,
    role = "editor",
  }: CreateUserInput): Promise<UserRecord | undefined> {
    const { lastInsertRowid } = await this.db.run(
      `INSERT INTO users (discord_id, username, avatar, role)
       VALUES (@discordId, @username, @avatar, @role)`,
      { discordId, username, avatar, role },
    );
    return this.findById(lastInsertRowid);
  }

  /** Insert-or-update keyed on `discord_id`; useful for login flows. */
  async upsert({
    discordId,
    username,
    avatar = null,
    role = "editor",
  }: CreateUserInput): Promise<UserRecord | undefined> {
    await this.db.run(
      `INSERT INTO users (discord_id, username, avatar, role)
       VALUES (@discordId, @username, @avatar, @role)
       ON CONFLICT(discord_id) DO UPDATE SET
         username   = @username,
         avatar     = @avatar,
         updated_at = CURRENT_TIMESTAMP`,
      { discordId, username, avatar, role },
    );
    return this.findByDiscordId(discordId);
  }

  async update(id: number, data: UpdateUserInput): Promise<UserRecord | undefined> {
    const setClause = buildUpdate(data as Record<string, unknown>, UPDATABLE);
    if (!setClause) return this.findById(id);

    await this.db.run(
      `UPDATE users SET ${setClause}, updated_at = CURRENT_TIMESTAMP WHERE id = @id`,
      { ...data, id },
    );
    return this.findById(id);
  }

  async setRole(id: number, role: UserRole): Promise<UserRecord | undefined> {
    return this.update(id, { role });
  }

  async delete(id: number): Promise<boolean> {
    const { changes } = await this.db.run("DELETE FROM users WHERE id = @id", { id });
    return changes > 0;
  }
}

export const userRepository = new UserRepository();

```

