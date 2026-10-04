# Backend, Database & Settings Survey Report

**Explorer**: explorer_survey_2 (Backend & Database Explorer)  
**Date**: 2026-10-03  
**Target Codebase**: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\hoho_manager`  
**Specification Ref**: `.agents/teamwork/ORIGINAL_REQUEST.md` (Requirements R2, R3, R4)  

---

## 1. Executive Summary

This report delivers a comprehensive investigation of the **Hoho Manager** backend, database, configuration, and security architecture to support the upcoming refactor:
1. Cloning the Discohook 3-pane layout and experience.
2. Replacing hardcoded `.env` variables (`LOG_CHANNEL_ID`, Head Admin IDs) with a database-backed Settings table supporting global and per-guild configurations.
3. Enabling dynamic Discord API entity fetching (guilds, channels, roles, members) via the bot with zero server-side caching.
4. Consolidating Bot and Webhook profile management into a dedicated Head Admin Settings area.
5. Hardening staff access controls, mention scrubbing, and audit logging across all execution paths.

The existing backend is built with **Node.js (>=20), TypeScript (ES2022/ESM), and Express 5** (`express: ^5.2.1`), backed by an asynchronous repository layer over **better-sqlite3** (`better-sqlite3: ^13.0.3`) in WAL mode. The codebase includes a robust suite of **12 Vitest test files (95 tests passing)** and full TypeScript compilation without errors.

---

## 2. Backend Architecture Map

### 2.1 Framework & Runtime
- **Runtime**: Node.js >= 20, ES Modules (`"type": "module"` in `package.json`).
- **Framework**: Express 5.2.1 (`hoho_manager/server/src/app.ts`).
- **Monorepo Structure**: `npm workspaces` containing:
  - `shared`: `@dmb/shared` domain types, constants, custom ID serialization.
  - `server`: Express API, SQLite repository layer, Discord interactions endpoint.
  - `client`: Vite + React + Tailwind + Zustand frontend.
  - `bot`: Sapphire/discord.js gateway worker for slash commands and gateway-relayed interactions.

### 2.2 Server Entry Point & Lifecycle
- **Entry point**: `hoho_manager/server/src/index.ts`
- **Boot Sequence**:
  1. `validateEnv()` in `src/config/env.ts` (lines 109–141) evaluates presence of `DISCORD_PUBLIC_KEY`, `DISCORD_BOT_TOKEN`, `DISCORD_APPLICATION_ID`, `ADMIN_API_KEY`, `ENCRYPTION_KEY`.
  2. `initializeDatabase()` in `src/config/database.ts` (lines 156–174) runs idempotent migrations via `runMigrations()` and seeds the `local-admin` record in `users`.
  3. `createApp()` in `src/app.ts` builds and configures Express middlewares and route mounts.
  4. Server listens on `env.port` (default `3001`).
  5. Background Sweeper: `setInterval` sweeps expired flow states and interaction receipts every 10 minutes (`flowRepository.pruneExpired()`, `interactionReceiptRepository.pruneExpired()`).
  6. Graceful Shutdown: `SIGINT` and `SIGTERM` listeners drain HTTP connections, close the SQLite database (`db.close()`), and terminate.

### 2.3 Routing Structure & Middleware Pipeline
In `hoho_manager/server/src/app.ts` (lines 38–93), the middleware pipeline order is load-bearing:
1. **Security & CORS**: `helmet` (lines 38–44) and `cors` (lines 46–60).
2. **Interaction Endpoint**: Mounted at `/api/interactions` **before** JSON body parsers (`app.use("/api/interactions", interactionsRouter)`). Discord Ed25519 signatures cover raw request bytes, verified in `middleware/verifyDiscordSignature.ts`.
3. **Body Parsers**: `express.json({ verify: (req, _res, buf) => (req.rawBody = buf) })` with a 2MB limit.
4. **Rate Limiting**: `apiLimiter` mounted on `/api` (lines 73–74) enforcing `RATE_LIMIT_WINDOW_MS` / `RATE_LIMIT_MAX`.
5. **Route Mounts**:
   - `GET /api/health` -> `healthRouter` (`src/routes/health.ts`): Readiness probe, uptime, DB connection, config flags.
   - `GET /api/config` -> `configRouter` (`src/routes/config.ts`): Action handler registry & feature capabilities.
   - `POST /api/send`, `GET /api/send/channels`, `GET /api/send/channels/:channelId/messages`, `GET /api/send/identity` -> `sendRouter` (`src/routes/send.ts`).
   - `GET /api/templates/*` -> `templatesRouter` (`src/routes/templates.ts`): Template CRUD.
   - `GET|POST|PATCH|DELETE /api/profiles/*` -> `profilesRouter` (`src/routes/profiles.ts`): Webhook and Bot profiles.
   - `GET|POST|PATCH|DELETE /api/access/*` -> `accessRouter` (`src/routes/access.ts`): Staff Access controls and permission checks.

---

## 3. Database Setup & Persistence Analysis

### 3.1 Driver & Abstraction Layer
- **Engine**: SQLite 3 via `better-sqlite3: ^13.0.3` (`hoho_manager/server/src/config/database.ts`).
- **Pragmas**:
  - `journal_mode = WAL` (concurrent reads during writes)
  - `foreign_keys = ON` (referential integrity)
  - `busy_timeout = 5000` (5-second lock queue before throwing)
  - `synchronous = NORMAL`
- **DatabaseClient Interface** (lines 31–44):
  ```typescript
  export interface DatabaseClient {
    query<T>(sql: string, params?: QueryParams): Promise<T[]>;
    get<T>(sql: string, params?: QueryParams): Promise<T | undefined>;
    run(sql: string, params?: QueryParams): Promise<RunResult>;
    exec(sql: string): Promise<void>;
    transaction<T>(fn: () => T): Promise<T>;
    close(): Promise<void>;
  }
  ```
  Every method is explicitly asynchronous to decouple repository implementations from synchronous SQLite specifics and facilitate eventual PostgreSQL migration.

### 3.2 Migrations History (`hoho_manager/server/src/config/migrations.ts`)
Migrations are tracked in `schema_migrations (id TEXT PRIMARY KEY, applied_at TEXT)`:
1. `001_init`:
   - `users`: id, discord_id, username, avatar, role ('admin'|'editor'|'viewer'), created_at, updated_at.
   - `webhook_profiles`: id, user_id, name, url, guild_id, channel_id, avatar_url, is_default, created_at, updated_at.
   - `bot_profiles`: id, user_id, name, token_encrypted, public_key, application_id, default_guild_id, is_active, created_at, updated_at.
   - `templates`: id, user_id, name, description, data, preview_image_url, is_public, created_at, updated_at.
   - `action_definitions`: id, template_id, custom_id, action_type, config, execution_order, created_at.
   - `action_logs`: id, action_definition_id, interaction_id, user_id, guild_id, channel_id, status, response, executed_at.
   - `flow_states`: token, template_id, step, variables, expires_at, created_at.
2. `002_interaction_receipts`:
   - `interaction_receipts`: interaction_id, response_json, expires_at, created_at.
3. `003_message_scoped_actions`:
   - Adds `message_id TEXT` to `action_definitions` with index `(message_id, custom_id)`.
4. `004_staff_access`:
   - `staff_access`: id, discord_user_id (UNIQUE), discord_username, granted_by_discord_id, is_active, expires_at, cooldown_seconds, can_send_messages, can_edit_messages, can_delete_messages, can_manage_templates, allowed_channel_ids (JSON), can_mention_everyone, can_mention_here, can_mention_roles, allowed_role_mention_ids (JSON), max_messages_per_hour, notes, created_at, updated_at.
   - `staff_cooldowns`: discord_user_id, action, last_at, count_this_hour, hour_bucket, PRIMARY KEY (discord_user_id, action).

---

## 4. Comprehensive Environment Variable Audit

The table below lists all environment variables defined, where they are consumed, and the refactor requirements:

| Variable | Defined In | Consumed In | Current Usage & Limitation | Refactor Action |
|---|---|---|---|---|
| `LOG_CHANNEL_ID` | `server/.env.example:39`, `server/src/config/env.ts:72` | `server/src/services/auditLog.ts:153,161` | Hardcoded channel ID where bot posts audit logs. Process must be restarted to change it. No guild scoping. | **Migrate to DB Settings**. Support global & per-guild configuration. Keep `env.logChannelId` only as seed/fallback. |
| `OWNER_DISCORD_IDS` | `server/.env.example:40`, `server/src/config/env.ts:73` | Declared in `env.ts`, but **never hooked into auth or staff checks**. | Intended as Head Admins/Owners who bypass staff limits and access settings. | **Migrate to DB Settings** (`head_admin_ids`). Allow editing via UI. Wire into `requireHeadAdmin` middleware. |
| `DISCORD_BOT_TOKEN` | `server/.env:22`, `bot/.env:4` | `services/discordService.ts`, `services/auditLog.ts`, `bot/src/index.ts` | Default bot token for API and Gateway. | Retain in `.env` as default fallback; bot profiles in DB already store encrypted tokens per profile. |
| `DISCORD_PUBLIC_KEY` | `server/.env:16`, `server/src/config/env.ts:91` | `middleware/verifyDiscordSignature.ts:58` | Verifies Ed25519 signature on incoming Discord interactions. | Retain in `.env` as global default; fallbacks to `bot_profiles.public_key`. |
| `DISCORD_APPLICATION_ID` | `server/.env:19`, `server/src/config/env.ts:92` | `services/discordService.ts:92,99` | Used in interaction token lookups and bot token resolution. | Retain in `.env` as global default. |
| `ADMIN_API_KEY` | `server/.env:27`, `server/src/config/env.ts:95` | `middleware/auth.ts:77`, `middleware/staffPermissions.ts:43`, `utils/crypto.ts:22` | Master API key (`x-admin-key`) used for admin access and bot-to-server relay. | Retain as secret master key; supplement with Discord snowflake Head Admin authentication. |
| `ENCRYPTION_KEY` | `server/.env:31`, `server/src/config/env.ts:96` | `utils/crypto.ts:22` | AES-256-GCM symmetric key for encrypting bot tokens in `bot_profiles`. | Retain in `.env` (cryptographic secret should remain in server environment). |
| `DATABASE_URL` | `server/.env:11`, `server/src/config/env.ts:89` | `config/database.ts:38,61` | Path to SQLite file (`./data/dev.sqlite`). | Retain in `.env`. |
| `PORT` | `server/.env:3`, `server/src/config/env.ts:82` | `server/src/index.ts:26` | Port Express listens on (default 3001). | Retain in `.env`. |
| `CLIENT_ORIGIN` | `server/.env:6`, `server/src/config/env.ts:83` | `server/src/app.ts:51` | Allowed CORS origins. | Retain in `.env`. |
| `RATE_LIMIT_*` | `server/.env:35-36`, `server/src/config/env.ts:97` | `middleware/rateLimit.ts` | Window ms and max hits for API limiter. | Retain in `.env`. |

---

## 5. Database Migration & Settings Architecture Plan

### 5.1 Migration 005_settings Schema Design
Append migration `005_settings` to `hoho_manager/server/src/config/migrations.ts`:

```sql
CREATE TABLE IF NOT EXISTS settings (
  guild_id        TEXT PRIMARY KEY,  -- '__global__' for global defaults, or Discord guild snowflake
  log_channel_id  TEXT,
  head_admin_ids  TEXT NOT NULL DEFAULT '[]', -- JSON array of Discord user IDs: ["123456789..."]
  bot_profile_id  INTEGER REFERENCES bot_profiles(id) ON DELETE SET NULL,
  extra_settings  TEXT NOT NULL DEFAULT '{}', -- Extensible JSON blob for arbitrary configurations
  created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_settings_guild ON settings(guild_id);
```

### 5.2 Seeding & Backward Compatibility Strategy
During `initializeDatabase()` in `hoho_manager/server/src/config/database.ts`:
1. Check if `SELECT * FROM settings WHERE guild_id = '__global__'` exists.
2. If absent:
   ```typescript
   await db.run(
     `INSERT INTO settings (guild_id, log_channel_id, head_admin_ids)
      VALUES ('__global__', @logChannelId, @headAdminIds)`,
     {
       logChannelId: env.logChannelId ?? null,
       headAdminIds: JSON.stringify(env.ownerDiscordIds ?? []),
     }
   );
   ```
   This automatically migrates any values configured in `.env` into the database on first boot without manual data entry.

### 5.3 Settings Repository (`server/src/repositories/settingsRepository.ts`)
Create `SettingsRepository` inheriting from `BaseRepository`:
- `findGlobal(): Promise<GuildSettingsRecord | undefined>`
- `findByGuildId(guildId: string): Promise<GuildSettingsRecord | undefined>`
- `listAll(): Promise<GuildSettingsRecord[]>`
- `upsert(guildId: string, data: UpdateSettingsInput): Promise<GuildSettingsRecord>`
- `delete(guildId: string): Promise<boolean>`

### 5.4 Dynamic Settings Service (`server/src/services/settingsService.ts`)
Provides high-performance, cached configuration resolution:
- **In-Memory Cache**: Caches resolved settings with instant invalidation upon updates.
- **Hierarchical Fallback Resolution**:
  ```typescript
  getEffectiveSettings(guildId?: string): Promise<ResolvedSettings>
  ```
  1. Checks guild-specific row `settings WHERE guild_id = @guildId`.
  2. Falls back to `settings WHERE guild_id = '__global__'`.
  3. Falls back to static `env.logChannelId` and `env.ownerDiscordIds`.
- **Head Admin Check**:
  ```typescript
  isHeadAdmin(discordUserId: string): Promise<boolean>
  ```
  Returns `true` if `discordUserId` is included in `head_admin_ids` of global settings or `env.ownerDiscordIds`.
- **Effective Log Channel**:
  ```typescript
  getEffectiveLogChannelId(guildId?: string): Promise<string | undefined>
  ```
  Returns resolved log channel ID for audit embeds.

### 5.5 Head Admin Authorization Middleware
In `server/src/middleware/auth.ts`, create `requireHeadAdmin`:
```typescript
export const requireHeadAdmin: RequestHandler = asyncHandler(async (req, res, next) => {
  // 1. Master admin key header
  const adminKey = req.get("x-admin-key");
  if (adminKey && safeEqual(adminKey, env.adminApiKey)) {
    req.staffContext = { isAdmin: true, staffId: null };
    return next();
  }

  // 2. Head Admin via Discord ID header
  const staffId = req.get("x-staff-id");
  if (staffId && /^\d{17,20}$/.test(staffId)) {
    const isHead = await settingsService.isHeadAdmin(staffId);
    if (isHead) {
      req.staffContext = { isAdmin: true, staffId };
      return next();
    }
  }

  return next(ApiError.forbidden("Access denied: Requires authorized Head Admin credentials"));
});
```
This enables authorized Head Admins to access settings via their Discord ID (passed by the UI as `x-staff-id`) without needing to paste the raw `ADMIN_API_KEY` into browser local storage.

### 5.6 Dynamic Audit Log Integration (`server/src/services/auditLog.ts`)
Refactor `auditLog` from static `env.logChannelId` to dynamic resolution:
```typescript
export const auditLog = (ctx: AuditContext): void => {
  void (async () => {
    const logChannelId = await settingsService.getEffectiveLogChannelId(ctx.guildId);
    const botToken = env.discord.botToken;
    if (!logChannelId || !botToken) {
      log.info(`[AUDIT] ${ctx.event} actor=${ctx.actorDiscordId ?? "?"} reason=${ctx.reason ?? "-"}`);
      return;
    }

    const body = buildEmbed(ctx);
    fetch(`https://discord.com/api/v10/channels/${logChannelId}/messages`, {
      method: "POST",
      headers: {
        Authorization: `Bot ${botToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    }).catch((err) => {
      log.warn(`Audit log delivery failed: ${err instanceof Error ? err.message : String(err)}`);
    });
  })();
};
```
Delivery remains fire-and-forget, non-blocking, and immediately reflects UI database modifications without server restart.

---

## 6. Bot & Webhook Profile Consolidation Under Settings

### 6.1 Current State
- Profile endpoints in `hoho_manager/server/src/routes/profiles.ts`:
  - Webhooks: `GET /api/profiles/webhooks`, `POST /api/profiles/webhooks`, `PATCH /api/profiles/webhooks/:id`, `POST /api/profiles/webhooks/:id/default`, `DELETE /api/profiles/webhooks/:id`
  - Bots: `GET /api/profiles/bots`, `POST /api/profiles/bots`, `PATCH /api/profiles/bots/:id`, `DELETE /api/profiles/bots/:id`
- Currently guarded by `router.use(attachUser, requireAdminKey)`.
- UI: `ProfilesPanel.tsx` is embedded directly in the main `Sidebar.tsx` (lines 73–75) and `App.tsx` (line 652).

### 6.2 Consolidation Plan
1. **Backend Route Guard**: Change `requireAdminKey` in `routes/profiles.ts` to `requireHeadAdmin`. This enables authorized Head Admins (identified via `x-staff-id` matching `head_admin_ids`) to list, create, edit, and delete bot/webhook profiles.
2. **Unified Settings Router**: Mount a dedicated `/api/settings` router in `server/src/routes/settings.ts`:
   - `GET /api/settings?guildId=...`: returns resolved settings + global settings.
   - `PATCH /api/settings`: updates `log_channel_id`, `head_admin_ids`, `bot_profile_id`, `extra_settings`.
   - `GET /api/settings/auth`: returns `{ isHeadAdmin: boolean, isAdminKey: boolean }` so frontend knows whether to render the Settings tab/button.
3. **Frontend Relocation**: Move `ProfilesPanel.tsx` (and webhook management) out of `Sidebar.tsx` and place them inside the new Head Admin Settings page/modal (`client/src/components/settings/SettingsModal.tsx`).

---

## 7. Dynamic Discord API Entity Fetching Architecture (R2 & R4)

### 7.1 Requirements Alignment
- **R2**: Implement global "Selected Server (Guild)" dropdown; replace manual ID fields (channels, roles, users) with searchable API dropdowns; no server-side caching (live fetch or client caching); auto-fetch Bot Identity on load.
- **R4**: Search members by name; dropdowns for `allowed_channel_ids` and `allowed_role_mention_ids` using live server fetch.

### 7.2 Discord Service Extensions (`server/src/services/discordService.ts`)
Add the following functions:
1. `getGuildRoles(guildId: string, profileId?: number | null)`:
   Calls `GET /guilds/${guildId}/roles`. Returns `[{ id, name, color, position, hoist }]`.
2. `searchGuildMembers(guildId: string, query: string, limit = 25, profileId?: number | null)`:
   Calls `GET /guilds/${guildId}/members/search?query=${encodeURIComponent(query)}&limit=${limit}`.
   Returns `[{ id, username, global_name, nickname, avatar }]`.
3. `getGuildChannels(guildId: string, profileId?: number | null)`:
   Already exists (line 306), but update to return full channel types (text = 0, voice = 2, category = 4, announcement = 5, forum = 15).

### 7.3 Discord Route Endpoints (`server/src/routes/discord.ts`)
Create a dedicated router mounted at `/api/discord`:
- `GET /api/discord/guilds`: Fetches list of mutual guilds the bot is in (`/users/@me/guilds`).
- `GET /api/discord/guilds/:guildId/channels`: Fetches live channels for selected guild. If requested by a staff member (not Head Admin), filters channels against `staff_access.allowed_channel_ids`.
- `GET /api/discord/guilds/:guildId/roles`: Fetches live roles for selected guild.
- `GET /api/discord/guilds/:guildId/members?q=...`: Searches members by username/nickname for selected guild.
- `GET /api/discord/identity`: Fetches bot identity `{ id, username, avatar }`. Accessible on app load.

### 7.4 Mention Scrubbing & Execution Path Security
In `server/src/utils/mentionScrubber.ts`:
- Ensure scrubbing covers:
  1. Root `content` string.
  2. Embed fields (`title`, `description`, `fields[].name`, `fields[].value`, `footer.text`, `author.name`).
  3. Component V2 structures (`TextDisplay.content`, `Section.accessory`, `Button.label`, `Select.placeholder`, `Select.options[].label`, `Select.options[].description`).
  4. Role mention regex: `/<@&(\d+)>/g` stripped unless role ID is present in `allowed_role_mention_ids`.
  5. `@everyone` and `@here` converted to zero-width space equivalents (`@\u200beveryone`, `@\u200bhere`).
  6. `allowed_mentions` in outgoing Discord payload strictly sanitized so Discord API will not broadcast pings even if raw markdown bypassed text regex.
- Ensure all send paths pass through the backend:
  - In `client/src/hooks/useSend.ts`, webhook sending must be routed through `/api/send` (`mode: "webhook"`) whenever staff mode is active, ensuring mention scrubbing, rate limiting, and audit logging cannot be bypassed by client-side direct webhook POSTs.

---

## 8. Detailed File-by-File Impact Matrix

The following table lists every backend file to be created or modified:

| Action | File Path | Functions / Classes / Lines | Description |
|---|---|---|---|
| **CREATE** | `server/src/repositories/settingsRepository.ts` | `SettingsRepository`, `settingsRepository` | Repository for `settings` table supporting global and per-guild CRUD. |
| **CREATE** | `server/src/services/settingsService.ts` | `settingsService` (`getGlobalSettings`, `getSettingsForGuild`, `updateSettings`, `isHeadAdmin`, `getEffectiveLogChannelId`) | Service with in-memory caching, fallback resolution, and audit log integration. |
| **CREATE** | `server/src/routes/settings.ts` | `settingsRouter` (`GET /`, `PATCH /`, `GET /auth`) | Head Admin settings API. |
| **CREATE** | `server/src/routes/discord.ts` | `discordRouter` (`GET /guilds`, `GET /guilds/:id/channels`, `GET /guilds/:id/roles`, `GET /guilds/:id/members`, `GET /identity`) | Live Discord entity fetching for R2 and R4 dropdowns. |
| **MODIFY** | `shared/src/types.ts` | Lines 298–368 | Add `GuildSettingsRecord`, `UpdateSettingsInput`, `DiscordRoleSummary`, `DiscordMemberSummary`. |
| **MODIFY** | `server/src/config/migrations.ts` | Lines 170–178 | Add migration `005_settings` for `settings` table. |
| **MODIFY** | `server/src/config/database.ts` | Lines 156–174 (`initializeDatabase`) | Seed `__global__` settings row from `env.logChannelId` and `env.ownerDiscordIds`. |
| **MODIFY** | `server/src/middleware/auth.ts` | Lines 57–84 | Add `requireHeadAdmin` middleware verifying `x-admin-key` or `x-staff-id` via `settingsService.isHeadAdmin()`. |
| **MODIFY** | `server/src/middleware/staffPermissions.ts` | Lines 54–65 | Allow Head Admins (`settingsService.isHeadAdmin(staffId)`) to bypass staff restrictions just like `x-admin-key`. |
| **MODIFY** | `server/src/services/auditLog.ts` | Lines 152–171 (`auditLog`) | Dynamically resolve `logChannelId` via `settingsService.getEffectiveLogChannelId(ctx.guildId)`. |
| **MODIFY** | `server/src/services/discordService.ts` | Lines 300–335 | Add `getGuildRoles`, `searchGuildMembers`, and export `DiscordRoleSummary`. |
| **MODIFY** | `server/src/routes/profiles.ts` | Line 9 | Replace `requireAdminKey` with `requireHeadAdmin` to allow Head Admin staff to manage profiles. |
| **MODIFY** | `server/src/routes/access.ts` | Lines 11–135 | Replace `requireAdminKey` with `requireHeadAdmin` to allow Head Admins to manage staff access. |
| **MODIFY** | `server/src/app.ts` | Lines 76–83 | Mount `/api/settings` and `/api/discord` routers. |
| **MODIFY** | `server/src/routes/send.ts` | Lines 149–175 | Update `/channels` to accept `guildId` query parameter or point to `/api/discord/guilds/:guildId/channels`. |

---

## 9. Verification & Safety Strategy

1. **Existing Test Suite Integrity**:
   - `npm test --workspace server` currently executes 12 test files with 95 passing tests.
   - Any modifications to `migrations.ts`, `auth.ts`, `discordService.ts`, or `routes/send.ts` must maintain 100% pass rate.
2. **New Unit & Integration Tests**:
   - `server/src/config/migrations.test.ts`: Test that `005_settings` table is created with proper columns and index.
   - `server/src/services/settingsService.test.ts`: Test global fallback resolution, per-guild overrides, cache invalidation, and `isHeadAdmin()` checks.
   - `server/src/middleware/auth.test.ts`: Test `requireHeadAdmin` against both `x-admin-key` and `x-staff-id`.
   - `server/src/routes/discord.test.ts`: Test guild, channel, role, and member endpoints with mock Discord API responses.
3. **TypeScript Compilation**:
   - Run `npm run typecheck` across all workspaces to guarantee zero type errors.

---

## 10. Live Environment Inspection (`http://localhost:5175/` & `http://localhost:3001/`)

### 10.1 Active Process & Service Mapping
Inspection of the running development environment confirmed:
1. **Frontend Server**: Live on `http://localhost:5175/` (Vite dev server running with React fast refresh).
2. **Backend Server**: Live on `http://localhost:3001/` (Express API process running with nodemon/tsx).
3. **Reverse Proxy Tunnel**: In `client/vite.config.ts` (lines 28–33), `/api` requests are proxied directly to `http://localhost:3001` with `changeOrigin: true`. Verified live by fetching `http://localhost:5175/api/health` which successfully returned the Express API's response:
   ```json
   {
     "status": "ok",
     "environment": "development",
     "uptimeSeconds": 3391,
     "database": { "connected": true, "users": 1 },
     "discord": {
       "publicKeyConfigured": true,
       "botTokenConfigured": true,
       "applicationIdConfigured": true
     }
   }
   ```
4. **Action Registry**: Verified live via `http://localhost:3001/api/config` returning 16 registered action handlers (`dud`, `modal_submit`, `add_role`, `remove_role`, `toggle_role`, `send_ephemeral_reply`, `send_dm`, `open_modal`, `send_message`, `send_webhook_message`, `delete_message`, `create_thread`, `wait`, `set_variable`, `check`, `stop`).
5. **Database State**: Single `local-admin` seeded user present in SQLite `dev.sqlite`.
6. **Network Path Forwarding**: Because Vite proxies all `/api/*` routes, adding the proposed `/api/settings` and `/api/discord` routes will immediately be accessible to the browser client at `http://localhost:5175/api/settings` and `http://localhost:5175/api/discord` with zero CORS hurdles in local development.

