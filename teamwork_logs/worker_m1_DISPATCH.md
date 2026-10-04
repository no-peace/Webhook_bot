# Task Assignment: Milestone 1 — Backend Security, Database Settings & Dynamic Discord API

## Working Directory
`C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\worker_m1`

## Mandatory Reference Documents
- Master Specification: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\ORIGINAL_REQUEST.md`
- Project Architecture & Interface Contracts: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\PROJECT.md`
- Backend Survey: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_survey_2\report.md`
- Security & Bot Survey: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_survey_3\report.md`

## File Ownership
You exclusively own and may edit files in:
- `hoho_manager/packages/shared/`
- `hoho_manager/server/`

## Scope of Work (Milestone 1)

1. **Database Migration 005_settings & Settings Service**:
   - Create migration `005_settings` in `server/src/config/migrations.ts` adding a `settings` table with columns: `guild_id TEXT PRIMARY KEY`, `log_channel_id TEXT`, `head_admin_ids TEXT` (JSON array of snowflake IDs), `bot_profile_id TEXT`, `extra_settings TEXT`, `created_at INTEGER`, `updated_at INTEGER`.
   - Seed `'__global__'` in database initialization from `env.logChannelId` and `env.ownerDiscordIds`.
   - Create `server/src/services/settingsService.ts` providing `getSettings(guildId)`, `updateSettings(guildId, data)`, and `getEffectiveLogChannelId(guildId)`.
   - Update `server/src/services/auditLog.ts` to dynamically resolve `log_channel_id` from `settingsService` (guild -> global -> env fallback).

2. **Authorization Middleware & Settings API**:
   - In `server/src/middleware/auth.ts`, implement `requireHeadAdmin` middleware: allows request if caller provides valid `x-admin-key` OR `x-staff-id` matching an ID in `head_admin_ids` from `settingsService`.
   - Create `server/src/routes/settings.ts` mounting `GET /api/settings` and `PUT /api/settings` protected by `requireHeadAdmin`. Mount on app under `/api/settings`.
   - Protect `/api/profiles` and `/api/access` with `requireHeadAdmin` where appropriate.

3. **Live Discord Entity Fetching Endpoints (No Server-Side Caching)**:
   - In `server/src/services/discordService.ts`, add methods:
     - `getGuildRoles(guildId: string, profileId?: string): Promise<DiscordRole[]>`
     - `searchGuildMembers(guildId: string, query: string, profileId?: string): Promise<DiscordMember[]>`
   - Create `server/src/routes/discord.ts` with:
     - `GET /api/discord/guilds`
     - `GET /api/discord/guilds/:guildId/channels`
     - `GET /api/discord/guilds/:guildId/roles`
     - `GET /api/discord/guilds/:guildId/members/search` (accepts `?query=`)
   - Ensure zero server-side caching of Discord entity data (R2).
   - In `server/src/routes/send.ts:151`, support optional `guildId` query parameter rather than hardcoding the first guild.

4. **Security Fixes & Zero-Bypass Mention Scrubbing**:
   - **Fix Channel Allowlist Default-Deny**: In `server/src/middleware/staffPermissions.ts:140`, fix `const allAllowed = allowed.includes("*") || allowed.length === 0;`. When `allowed.length === 0`, it MUST default to DENY ALL. Only `allowed.includes("*")` allows all channels.
   - **Case-Insensitive Mention Scrubbing**: In `server/src/utils/mentionScrubber.ts`, update regexes to `/@everyone/gi` and `/@here/gi`.
   - **Component V2 Flow Scrubbing**: In `server/src/routes/send.ts`, scrub `body.flows` action parameters using `scrubMentions` before registering in `actionRepository`.
   - **Allowed Mentions Sanitization**: In `server/src/utils/mentionScrubber.ts:sanitizeAllowedMentions`, respect `perms.can_mention_roles` and `allowed_role_mention_ids` properly.
   - **Granular Cooldowns & Hourly Limits**: Extend staff permissions schema and `staffPermissions.ts` to support per-action-type cooldowns and hourly rate limits (`send`, `edit`, `delete`, `templates`).

5. **Run Builds & Tests**:
   - Run `npm test --workspace server` and `npm run typecheck`.
   - Ensure all existing tests pass and add unit/integration tests for the new features.

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Completion Deliverables
Write `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\worker_m1\handoff.md` with:
1. Exact files modified and created.
2. Build and test execution commands and results.
3. Verification details.
Send a message back when complete.


## 2026-10-03T09:58:06Z
Read your task assignment in C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\worker_m1\DISPATCH.md.
Follow all instructions, file ownership rules, and the MANDATORY INTEGRITY WARNING.
Implement Milestone 1 (Backend Security, Database Settings & Dynamic Discord API).
Run the build and test suites (npm test --workspace server, npm run typecheck).
Write your handoff report to C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\worker_m1\handoff.md and notify me via send_message when done.
