# Handoff Report: Backend, Database & Settings Survey

**Sender**: `explorer_survey_2` (Backend & Database Explorer)  
**Recipient**: `9905eadb-ba91-4495-92f1-aa467294c8a6` (Orchestrator)  
**Working Directory**: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_survey_2`  
**Handoff Type**: Hard (Investigation & Survey Complete)  

---

## 1. Observation

1. **Framework & Architecture**:
   - The backend is implemented with Express 5.2.1 and better-sqlite3 13.0.3 in TypeScript ESM (`hoho_manager/server/package.json:22`).
   - Server entry point is `hoho_manager/server/src/index.ts`. It executes `validateEnv()`, `initializeDatabase()`, and mounts `createApp()` on port 3001.
   - Live backend probe (`http://localhost:3001/api/health`) responded:
     `{"status":"ok","environment":"development","uptimeSeconds":3355,"database":{"connected":true,"users":1},"discord":{"publicKeyConfigured":true,"botTokenConfigured":true,"applicationIdConfigured":true}}`
   - Live frontend is active at `http://localhost:5175/` and proxies `/api` requests to `http://localhost:3001` via `client/vite.config.ts:28-33`.

2. **Database & Migrations**:
   - Database layer uses an asynchronous `DatabaseClient` abstraction in `server/src/config/database.ts:31-44` wrapping synchronous SQLite WAL-mode connections.
   - Four migrations currently exist in `server/src/config/migrations.ts:18-176`:
     - `001_init`: `users`, `webhook_profiles`, `bot_profiles`, `templates`, `action_definitions`, `action_logs`, `flow_states`.
     - `002_interaction_receipts`: `interaction_receipts`.
     - `003_message_scoped_actions`: `action_definitions.message_id`.
     - `004_staff_access`: `staff_access`, `staff_cooldowns`.

3. **Environment Variable Usages**:
   - `LOG_CHANNEL_ID`: Defined in `server/.env.example:39`, parsed in `server/src/config/env.ts:72`, consumed statically in `server/src/services/auditLog.ts:153,161`.
   - `OWNER_DISCORD_IDS`: Defined in `server/.env.example:40`, parsed in `server/src/config/env.ts:73-78`, but **unwired to any auth check or middleware**.
   - `DISCORD_BOT_TOKEN`, `DISCORD_PUBLIC_KEY`, `DISCORD_APPLICATION_ID`, `ADMIN_API_KEY`, `ENCRYPTION_KEY`: Parsed in `server/src/config/env.ts` and consumed across routes, crypto, and services.

4. **Profiles & Settings UI Placement**:
   - `ProfilesPanel.tsx` is currently imported directly in `client/src/App.tsx:23,652` and `client/src/components/layout/Sidebar.tsx:6,74` under an accordion inside the main editing column.
   - `/api/profiles` routes in `server/src/routes/profiles.ts:9` are guarded by `requireAdminKey` which rejects anyone without `x-admin-key`.
   - No dedicated Settings database table or `/api/settings` route currently exists.

5. **Discord API Entity Fetching**:
   - `routes/send.ts:149-175` (`GET /api/send/channels`) hardcodes `const [guild] = await discord.getBotGuilds(profileId)` (taking only the first guild).
   - No endpoints currently exist to list guilds for a global selector, list roles for a selected guild, or search guild members.

6. **Test Suite Baseline**:
   - Executing `npm test --workspace server` passed 95 tests across 12 test files (`variableInterpolation.test.ts`, `migrations.test.ts`, `verifyDiscordSignature.test.ts`, `discordService.test.ts`, `crypto.test.ts`, `actionRepository.test.ts`, `branches.test.ts`, `validation.test.ts`, `profileService.test.ts`, `flow.test.ts`, `interactionHandler.test.ts`, `send.test.ts`).
   - Executing `npm run typecheck` across all 4 workspaces (`shared`, `server`, `client`, `bot`) succeeded with 0 errors.

---

## 2. Logic Chain

1. **Settings Database Strategy**:
   - *From Observation 3*: `LOG_CHANNEL_ID` and `OWNER_DISCORD_IDS` are hardcoded in `.env`, requiring process restarts for changes.
   - *Therefore*: Migration `005_settings` must add a `settings` table keyed on `guild_id` (`'__global__'` for global defaults, or Discord snowflake for per-guild overrides), containing `log_channel_id`, `head_admin_ids` (JSON array), `bot_profile_id`, and `extra_settings` (JSON blob).
   - *From Observation 2*: `initializeDatabase()` in `server/src/config/database.ts` can seed `'__global__'` from `env.logChannelId` and `env.ownerDiscordIds`, guaranteeing automatic migration of existing configurations without data loss.

2. **Security & Authorization Model**:
   - *From Observation 3 & 4*: Currently only `x-admin-key` callers can access admin routes; `OWNER_DISCORD_IDS` is unused.
   - *Therefore*: A new middleware `requireHeadAdmin` in `server/src/middleware/auth.ts` must validate that the caller either supplies a valid `x-admin-key` OR supplies an `x-staff-id` present in `settings.head_admin_ids`.
   - *Applying this*: Mounting `requireHeadAdmin` on `/api/settings`, `/api/profiles`, and `/api/access` guarantees that authorized Head Admins can manage settings and profiles from the UI, while staff members lacking Head Admin status are forbidden.

3. **Audit Log Dynamic Routing**:
   - *From Observation 3*: `auditLog.ts:153` checks `if (!env.logChannelId || !env.discord.botToken)`.
   - *Therefore*: `auditLog` should resolve the channel ID dynamically through `settingsService.getEffectiveLogChannelId(ctx.guildId)` (checking guild setting -> global setting -> env fallback), enabling immediate channel updates from the UI without restarts.

4. **Dynamic Discord Entity Fetching**:
   - *From Observation 5*: `routes/send.ts` only reads the first guild and does not support role or member search.
   - *Therefore*: Create `server/src/routes/discord.ts` with `/guilds`, `/guilds/:guildId/channels`, `/guilds/:guildId/roles`, and `/guilds/:guildId/members`. Extend `discordService.ts` with `getGuildRoles` and `searchGuildMembers`. Do not cache server-side, fulfilling Requirement R2.

---

## 3. Caveats

1. **Large Discord Guild Member Searches**:
   - Discord's `/guilds/:guildId/members/search` REST endpoint requires the `GuildMembers` gateway intent for certain queries or large guilds (>1000 members). If an unprivileged bot token is used, member search may return limited results. The frontend must allow fallback manual ID string entry as specified in Requirement R2.
2. **Postgres Forward Compatibility**:
   - Although SQLite is currently used, all SQL adheres to the dialect-neutral async abstraction in `database.ts`. Migration `005_settings` must avoid SQLite-specific proprietary extensions.
3. **No Caveats on Test Stability**:
   - All 95 existing server tests pass consistently.

---

## 4. Conclusion

The Hoho Manager backend is well-structured, modular, and fully prepared for the R2, R3, and R4 refactor:
1. Migration `005_settings` will establish a database-backed Settings table supporting global and per-guild configurations.
2. `settingsService.ts` will dynamically resolve `log_channel_id`, `head_admin_ids`, and audit log destinations with fast in-memory caching.
3. `requireHeadAdmin` will enforce access control for both master key callers and Discord snowflake Head Admins.
4. Bot & Webhook profile management can be seamlessly consolidated into the Head Admin Settings area.
5. The live test suite passes 100%, and TypeScript compiles cleanly across all packages.

Full detailed blueprints, code schemas, and impact tables are recorded in `report.md`.

---

## 5. Verification Method

To independently verify the facts and stability reported:
1. **Run Server Test Suite**:
   ```bash
   npm test --workspace server
   ```
   *Expected outcome*: 12 test suites passed, 95 tests passed, 0 failures.
2. **Run Monorepo Typecheck**:
   ```bash
   npm run typecheck
   ```
   *Expected outcome*: Zero TypeScript compilation errors across `@dmb/shared`, `server`, `client`, and `bot`.
3. **Inspect Live Health Endpoint**:
   ```bash
   curl http://localhost:3001/api/health
   curl http://localhost:5175/api/health
   ```
   *Expected outcome*: Status `ok`, database connected, Discord credentials configured.
4. **Inspect Files Documented**:
   - `hoho_manager/server/src/config/migrations.ts`
   - `hoho_manager/server/src/config/database.ts`
   - `hoho_manager/server/src/config/env.ts`
   - `hoho_manager/server/src/services/auditLog.ts`
   - `hoho_manager/server/src/middleware/auth.ts`
   - `hoho_manager/server/src/routes/profiles.ts`
   - `hoho_manager/server/src/routes/send.ts`
