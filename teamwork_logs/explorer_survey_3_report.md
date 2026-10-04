# Comprehensive Survey & Architectural Analysis: Discord Bot API, Staff Access & Mention Scrubbing

**Explorer**: `explorer_survey_3`  
**Target Project**: Hoho Manager (`webhook_bot`)  
**Workspace Root**: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot`  
**Live Site Tested**: `http://localhost:5175/` (Vite Proxy + Express API on port 3001)  
**Date**: 2026-10-03  

---

## Executive Summary

Hoho Manager is a hybrid Discord message construction and dispatch application combining a Discohook-style visual editor, Components V2 interactive builders, action chaining workflows, and a staff access control matrix. 

This survey rigorously investigated three core subsystems:
1. **Discord Bot Client Architecture & Live REST Fetching**: Analyzed the multi-process design (Sapphire Gateway worker + Express REST API), mapped current entity-fetching limits (hardcoded single guild, missing role fetching, missing member searching), and designed live, server-cache-free fetching with manual ID fallbacks.
2. **Staff Access & Granular Permissions**: Analyzed `staff_access` database models, permission middleware, and UI flows. Identified a critical authorization bug where an empty allowed-channels array permits all channels, as well as a UX flaw preventing the Staff Access modal from closing. Designed granular cooldowns and hourly limits per action type (`send`, `edit`, `delete`, `templates`) and member selection by name.
3. **Mention Scrubbing & Security Bypass Defense**: Evaluated all message execution pathways. Discovered multiple severe mention bypass vectors (case-sensitivity flaws in regex, client-direct webhook bypasses, unscrubbed Component V2 action flows, and broken role allowlist logic in `sanitizeAllowedMentions`). Designed a unified, zero-bypass backend mention scrubbing system.

---

## 1. Discord Bot Client Architecture Mapping

### 1.1 Process & Network Topology

The architecture divides responsibilities across three discrete layers to maintain security boundaries and support deployments without public IPv4 addresses:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   BROWSER / CLIENT (Vite + React)                      │
│   - Zustand State (Message, Profile, Action, Settings)                 │
│   - Live Preview (Discord UI rendering)                                │
│   - Client-side Cache for Discord Guilds / Channels / Roles / Members  │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ HTTP (REST + JSON)
                                     │ x-admin-key OR x-staff-id
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                BACKEND API (Express.js - Port 3001)                    │
│   - Token Resolver (AES-256-GCM encrypted Bot Tokens & Env fallback)   │
│   - Action Executor & Flow Engine (`actionExecutor.ts`)                │
│   - Staff Access Middleware & Audit Logger (`staffPermissions.ts`)     │
│   - REST Gateway Proxy to Discord API v10                              │
└──────────────┬──────────────────────────────────────────▲──────────────┘
               │                                          │
    POST /interactions/callback               POST /api/interactions/relay
    Outbound REST Calls (Bot/Webhook)         (Admin key authenticated)
               │                                          │
               ▼                                          │
┌──────────────────────────────┐        ┌─────────────────┴──────────────┐
│       DISCORD REST API       │        │  GATEWAY WORKER (Sapphire)     │
│   https://discord.com/api/v10│        │   - Gateway WebSocket (WSS)    │
│                              │        │   - Intents: Guilds            │
│                              │        │   - Slash commands (/send)     │
│                              │        │   - Raw packet listener        │
└──────────────▲───────────────┘        └─────────────────▲──────────────┘
               │                                          │
               └────────────── WebSocket ─────────────────┘
```

### 1.2 The Bot Gateway Worker (`hoho_manager/bot/src/`)
- **Framework & Entry**: Utilizes `@sapphire/framework` (`SapphireClient`) in `hoho_manager/bot/src/index.ts:37-45`.
- **Intents**: Configured strictly with `[GatewayIntentBits.Guilds]`. Privileged intents (`GuildMembers`, `MessageContent`) are currently omitted.
- **Commands**:
  - `commands/send.ts:52`: `/send` slash command does *not* talk directly to Discord REST. It calls `api.sendMessage` (`bot/src/lib/api.ts:109`), passing `{ mode: "bot", channelId, payload }` to the backend Express `/api/send` endpoint with `x-admin-key`. This centralizes payload validation, audit logging, and token storage in one place.
- **Interaction Relay Mechanism**:
  - `listeners/interactionRelay.ts:13-39`: Captures `raw` gateway packets where `packet.t === 'INTERACTION_CREATE'`. It serializes BigInts to strings and forwards the raw payload to `POST /api/interactions/relay` on the Express API.
  - **Zero Public Address Capability**: When running locally without Cloudflare Tunnel or public IP, Discord interactions received over the outbound WebSocket are relayed to Express, and Express responds directly using Discord's interaction callback endpoint (`https://discord.com/api/v10/interactions/{id}/{token}/callback`).

### 1.3 Discord REST Layer (`hoho_manager/server/src/services/discordService.ts`)
- **API Base**: Target Discord REST API v10 (`DISCORD_API_BASE = "https://discord.com/api/v10"`).
- **Resilience**: `apiRequest` (`discordService.ts:119-195`) handles exponential backoff for network drops, honors Discord 429 rate limits by parsing `retry_after` in milliseconds (capped at 10s), and retries 5xx upstream errors up to 3 times.
- **Token Resolution Hierarchy**: `resolveBotToken(profileId)` (`discordService.ts:71-87`):
  1. If `profileId` is provided: queries `botProfileRepository.revealToken(profileId)`, decrypting the AES-256-GCM token from the database.
  2. If `profileId` is omitted: falls back to `env.discord.botToken` (`DISCORD_BOT_TOKEN`).
  3. If missing: throws `ApiError(503, "No bot token is configured on the server")`.

---

## 2. Dynamic Discord API Fetching Analysis

### 2.1 Current State vs Requirement Gaps

| Entity | Discord REST Endpoint | Current Service Method | Current Route | Gap Analysis |
|---|---|---|---|---|
| **Bot Identity** | `GET /users/@me` | `getBotIdentity(token)` (`discordService.ts:335`) | `GET /api/send/identity` (`send.ts:204`) | Route exists but requires manual click of "Sync Cache" in `BotDispatchModal.tsx:98`. Must be auto-fetched on client load. |
| **Guilds (Servers)** | `GET /users/@me/guilds` | `getBotGuilds(profileId)` (`discordService.ts:299`) | None exposed directly | Currently, `send.ts:151` calls `const [guild] = await discord.getBotGuilds(profileId)` and arbitrarily takes the **first guild**. There is NO endpoint to retrieve all bot guilds. |
| **Channels** | `GET /guilds/{guild.id}/channels` | `getGuildChannels(guildId, profileId)` (`discordService.ts:306`) | `GET /api/send/channels` (`send.ts:149`) | Hardcoded to only inspect `guild[0]`. No `guildId` query parameter accepted. Does not return channels for user-selected guild. |
| **Roles** | `GET /guilds/{guild.id}/roles` | **DOES NOT EXIST** | **DOES NOT EXIST** | Completely missing in `discordService.ts` and routes. Required for role selection, mention allowlists, and action chaining. |
| **Members (Search/List)** | `GET /guilds/{guild.id}/members/search?query={q}&limit={limit}` | `getGuildMember(guildId, userId)` (`discordService.ts:358`) | **DOES NOT EXIST** | Only single-user snowflake lookup exists. Cannot search members by name/nickname. |

### 2.2 Strict Architectural Constraints: No Server-Side Caching

- **Mandate**: **Do not cache Discord entity data (guilds, channels, roles, members) in SQLite or server memory.**
- **Rationale**:
  - Prevents stale cache sync issues when roles/channels/members change on Discord.
  - Minimizes backend footprint and zero-state complexity.
  - Prevents storing Discord member lists or channel structures in server databases.
- **Client-Side Caching Strategy**:
  - The client may cache entity lists in session memory / Zustand store (`useDiscordEntityStore`) keyed by `{ guildId, botProfileId }` with a short TTL (e.g., 60 seconds) or refetch on user interaction / dropdown open.
- **Manual ID Fallback**:
  - All channel, role, user, and guild selectors must allow typing or pasting an arbitrary Discord Snowflake ID (`/^\d{17,20}$/`). If the live fetch fails or the entity is hidden/unlisted, the manually input ID must be preserved and submitted.

---

## 3. Staff Access & Permissions System Analysis

### 3.1 Data Model & Migrations (`hoho_manager/server/src/repositories/staffRepository.ts`)

Defined in Migration `004_staff_access` (`migrations.ts:138-176`):
- `staff_access` schema:
  - `discord_user_id` (TEXT UNIQUE NOT NULL - primary identifier)
  - `discord_username` (TEXT NOT NULL)
  - `granted_by_discord_id` (TEXT NOT NULL)
  - `is_active` (INTEGER DEFAULT 1)
  - `expires_at` (TEXT NULL)
  - `cooldown_seconds` (INTEGER DEFAULT 30) — *Current: single global integer*
  - `can_send_messages` (INTEGER DEFAULT 1)
  - `can_edit_messages` (INTEGER DEFAULT 0)
  - `can_delete_messages` (INTEGER DEFAULT 0)
  - `can_manage_templates` (INTEGER DEFAULT 0)
  - `allowed_channel_ids` (TEXT DEFAULT '[]' — JSON array)
  - `can_mention_everyone` (INTEGER DEFAULT 0)
  - `can_mention_here` (INTEGER DEFAULT 0)
  - `can_mention_roles` (INTEGER DEFAULT 0)
  - `allowed_role_mention_ids` (TEXT DEFAULT '[]' — JSON array)
  - `max_messages_per_hour` (INTEGER DEFAULT 10) — *Current: single global integer*
  - `notes` (TEXT NULL)
- `staff_cooldowns` schema:
  - `discord_user_id`, `action`, `last_at`, `count_this_hour`, `hour_bucket` (PRIMARY KEY: `[discord_user_id, action]`)

### 3.2 Security Flaws & Gaps Identified in Staff Access

#### Flaw 1: Critical Inversion in Channel Allowlist Checking
- **Location**: `hoho_manager/server/src/middleware/staffPermissions.ts:138-142`
```typescript
let allowed: string[];
try { allowed = JSON.parse(record.allowed_channel_ids); } catch { allowed = []; }
const allAllowed = allowed.includes("*") || allowed.length === 0; // empty = all denied by default
if (!allAllowed && !allowed.includes(channelId)) { ... }
```
- **Vulnerability**: The comment claims `empty = all denied by default`, but `allowed.length === 0` makes `allAllowed = true`! Therefore, when a staff member has an empty allowlist `[]`, **they are mistakenly granted access to EVERY channel on the Discord server!**
- **Fix**: `const allAllowed = allowed.includes("*");`. If `allowed.length === 0`, all channels must be denied.

#### Flaw 2: Global vs Granular Cooldowns & Hourly Limits
- **Location**: `staffRepository.ts:10` and `staffPermissions.ts:157-188`
- **Current Behavior**: `cooldown_seconds` (e.g. 30s) and `max_messages_per_hour` (e.g. 10) apply uniformly across all actions.
- **Requirement**: "granular cooldowns, and max-actions-per-hour per action type" (`send`, `edit`, `delete`, `templates`).
- **Solution**:
  - Add `granular_cooldowns` (`TEXT DEFAULT '{}'`) and `granular_rate_limits` (`TEXT DEFAULT '{}'`) to `staff_access`.
  - In `staffPermissions.ts`, lookup `granular[action] ?? record.cooldown_seconds`.

#### Flaw 3: Template Management Permission Never Checked
- **Location**: `hoho_manager/server/src/routes/templates.ts:11`
- **Vulnerability**: `templates.ts` applies `router.use(attachUser)`, but NEVER checks `requireStaffPermission("templates")` on `POST /`, `PUT /:id`, or `DELETE /:id`. Any authenticated staff user can manipulate templates regardless of `can_manage_templates`.

#### Flaw 4: Staff Access Modal Cannot Be Closed (UX Bug)
- **Location**: `Header.tsx:263-272` & `Modal.tsx:37-57` & `AccessPanel.tsx:72-86`
- **Root Cause**:
  1. `Header.tsx` renders `<Modal open={accessOpen} title="" width="max-w-4xl">`.
  2. In `Modal.tsx:43`, `{title && (` checks for truthiness. When `title === ""`, the entire title bar—including the `X` button—is omitted!
  3. In `Modal.tsx:37`, the backdrop `div` does not handle `onClick={onClose}`.
  4. In `AccessPanel.tsx`, there is no "Close" button in the header.
  - **Result**: The user is trapped inside the Staff Access modal with no exit mechanism.

---

## 4. Mention Scrubbing System Analysis

### 4.1 All Execution Pathways & Attack Vectors

```
Path 1: Webhook Message Direct (Browser -> Discord)
[Client: useSend.ts] ──> sendWebhookDirect ──> Discord API
* VULNERABILITY: Bypasses server entirely! No mention scrubbing or staff checks run!

Path 2: Bot / Webhook Message Proxied (Browser -> Express -> Discord)
[Client: useSend.ts] ──> POST /api/send ──> scrubMentions ──> Discord API
* VULNERABILITY: Regex is case-sensitive! @Everyone bypasses filter!
* VULNERABILITY: body.flows attached to components are NOT scrubbed!

Path 3: Action Execution Flows (User clicks button -> Bot Gateway -> Action Executor)
[Discord User] ──> [Sapphire Gateway] ──> POST /api/interactions/relay
                   ──> executeCustomId ──> runSteps (sendMessage / sendWebhookMessage)
* VULNERABILITY: Unscrubbed stored payloads in action_definitions fire with bot token!

Path 4: Variable Interpolation Injection
[Modal Input / User Nick] ──> replaceVariables({input}) ──> Message Content
* VULNERABILITY: End-user submits "@everyone" in modal text input -> injected directly into bot message!
```

### 4.2 Comprehensive Vulnerability Catalog

#### 1. Case-Sensitivity Ping Bypass
- **Location**: `hoho_manager/server/src/utils/mentionScrubber.ts:25-32`
```typescript
if (!perms.can_mention_everyone && result.includes("@everyone")) {
  result = result.replace(/@everyone/g, "@\u200beveryone");
}
if (!perms.can_mention_here && result.includes("@here")) {
  result = result.replace(/@here/g, "@\u200bhere");
}
```
- **Vulnerability**: `result.includes("@everyone")` is strictly lowercase. Discord parses mentions case-insensitively. Typing `@Everyone`, `@EVERYONE`, `@Here`, or `@HERE` bypasses the replacement completely, triggering a full guild-wide ping.
- **Fix**: Use regex with flag `/i`: `/@everyone/gi` and `/@here/gi`.

#### 2. Client-Direct Webhook Bypass
- **Location**: `hoho_manager/client/src/hooks/useSend.ts:75-77`
```typescript
} else {
  result = await sendWebhookDirect(webhookUrl, payload, { threadId: threadId || undefined });
}
```
- **Vulnerability**: When the user selects "Webhook" send mode, the client sends directly to `https://discord.com/api/v10/webhooks/...` via browser `fetch`. It completely avoids `/api/send`, bypassing all staff permissions, mention scrubbers, and audit logs.
- **Fix**: All staff message dispatches must be proxied through `/api/send` with `{ mode: "webhook", webhookUrl, payload }`.

#### 3. Unscrubbed Component Action Flows
- **Location**: `hoho_manager/server/src/routes/send.ts:60-96`
- **Vulnerability**: In `send.ts`, `scrubMentions` is executed on `sanitizedMessage`. However, `body.flows` (which contains action payloads for `send_message`, `send_webhook_message`, `send_ephemeral_reply`, `send_dm`) is passed untouched to `actionRepository.registerFlows(messageId, flows)`. A staff member without `@everyone` permission can attach a button with an action flow sending `@everyone`, bypassing all checks when clicked.
- **Fix**: Recursively scrub all message payloads inside `body.flows` prior to database registration.

#### 4. Logic Flaw in `sanitizeAllowedMentions`
- **Location**: `hoho_manager/server/src/utils/mentionScrubber.ts:75-97`
```typescript
let roles: string[] | undefined;
if (perms.can_mention_roles) {
  try { roles = JSON.parse(perms.allowed_role_mention_ids); } catch { roles = []; }
}
const allowedMentions: Record<string, unknown> = {
  parse,
  ...(roles && roles.length > 0 ? { roles } : {}),
};
```
- **Flaws**:
  1. If `can_mention_roles === 1` and `allowed_role_mention_ids` is `[]` (meaning "Any role allowed"), `parse` never receives `"roles"`, and `roles` is empty. Discord suppresses all role pings.
  2. In `scrubString:42`, `result.replace(ROLE_MENTION_RE, ...)` checks `if (allowedIds.includes(roleId))`. When `allowedIds` is `[]`, it scrubs all roles even though `can_mention_roles === 1`!
  3. If `can_mention_roles === 0`, but specific roles are in `allowed_role_mention_ids`, `if (perms.can_mention_roles)` evaluates to false, so allowed roles are discarded!
- **Fix**: Clarify permission flags:
  - `can_mention_roles === 1`: allows mentioning ANY role (`parse: ["roles"]`).
  - `can_mention_roles === 0` with `allowed_role_mention_ids`: allows mentioning ONLY specified roles (`parse: []`, `roles: allowed_role_mention_ids`).

#### 5. Component V2 Deep Structure Traversal
- **Locations**: Components V2 payloads contain text across multiple nesting levels:
  - `TextDisplay` (`type: 10`): `content`
  - `Button` (`type: 2`): `label`
  - `StringSelect` (`type: 3`): `placeholder`, `options[].label`, `options[].description`, `options[].value`
  - `Container` / `Section` / `ActionRow`: recursive `components` arrays
  - `MediaGallery`: `items[].description`
- **Fix**: `scrubObject` must traverse all object keys, ensuring no nested text node can harbor an unscrubbed mention.

---

## 5. Detailed Implementation Blueprint

### 5.1 Backend Changes & Additions

#### A. `hoho_manager/server/src/services/discordService.ts`
Add endpoints for roles, guild member search, and bot identity:
1. `getGuildRoles(guildId: string, profileId?: number | null): Promise<DiscordRoleSummary[]>`
   - Endpoint: `GET /guilds/${guildId}/roles`
2. `searchGuildMembers(guildId: string, query: string, profileId?: number | null): Promise<DiscordMemberSummary[]>`
   - Endpoint: `GET /guilds/${guildId}/members/search?query=${encodeURIComponent(query)}&limit=25`
3. `getGuildMembers(guildId: string, limit?: number, profileId?: number | null): Promise<DiscordMemberSummary[]>`
   - Endpoint: `GET /guilds/${guildId}/members?limit=${limit ?? 50}`
4. Update `getGuildChannels` to accept `guildId` dynamically.

#### B. New Dedicated Discord Entity Router: `hoho_manager/server/src/routes/discord.ts`
Mount under `/api/discord`:
- `GET /api/discord/guilds`: returns bot's guilds (`getBotGuilds`).
- `GET /api/discord/guilds/:guildId/channels`: returns channels for selected guild with staff filtering.
- `GET /api/discord/guilds/:guildId/roles`: returns roles for selected guild.
- `GET /api/discord/guilds/:guildId/members?query=...`: searches members by name/nickname.
- `GET /api/discord/identity`: returns active bot username and avatar URL.

#### C. `hoho_manager/server/src/utils/mentionScrubber.ts`
Rewrite `scrubString` and `sanitizeAllowedMentions`:
- Regex:
  - `/@everyone/gi` -> `@\u200beveryone`
  - `/@here/gi` -> `@\u200bhere`
  - `/<@&(\d+)>/g` -> validate against allowed role IDs.
- Ensure strict construction of `allowed_mentions` object.
- Export `scrubFlows(flows: StoredActionDefinition[], perms: MentionPermissions): StoredActionDefinition[]`.

#### D. `hoho_manager/server/src/middleware/staffPermissions.ts`
- Fix line 140:
  ```typescript
  const allAllowed = allowed.includes("*");
  if (!allAllowed && (allowed.length === 0 || !allowed.includes(channelId))) {
    return next(ApiError.forbidden(`You are not allowed to send to channel ${channelId}`));
  }
  ```
- Support granular cooldowns and rate limits per action (`send`, `edit`, `delete`, `templates`).

#### E. `hoho_manager/server/src/routes/templates.ts`
- Apply `requireStaffPermission("templates")` to modifying routes (`POST /`, `PUT /:id`, `DELETE /:id`).
- Scrub mentions from `body.data` and `body.actions` when created/updated by staff.

#### F. Database Migrations (`migrations.ts`)
- Add migration `005_granular_staff_and_settings`:
  - `ALTER TABLE staff_access ADD COLUMN granular_cooldowns TEXT NOT NULL DEFAULT '{}';`
  - `ALTER TABLE staff_access ADD COLUMN granular_rate_limits TEXT NOT NULL DEFAULT '{}';`
  - `CREATE TABLE IF NOT EXISTS app_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL, guild_id TEXT, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);`

### 5.2 Frontend Changes & Additions

#### A. Global Server/Guild Context (`useProfileStore.ts` & UI)
- Add `selectedGuildId: string | null` and `setSelectedGuildId` in `profileStore.ts`.
- Auto-fetch bot identity on mount in `App.tsx` / `Header.tsx` and store in `useProfileStore`.
- Update `MessagePreview.tsx` to automatically display the bot's live Discord avatar and name when no custom username/avatar override is set.

#### B. Replace Static ID Inputs with Searchable Dropdowns
- In `BotDispatchModal.tsx`:
  - Use `selectedGuildId` to fetch `/api/discord/guilds/:guildId/channels`.
  - Channel selector becomes searchable dropdown with fallback to manual ID.
- In `AccessPanel.tsx`:
  - Replace raw snowflake input with member search dropdown querying `/api/discord/guilds/:guildId/members?query=...` while binding snowflake ID as primary key.
  - Replace `allowed_channel_ids` with multi-select channel dropdown with manual ID fallback.
  - Replace `allowed_role_mention_ids` with multi-select role dropdown with manual ID fallback.
  - Add granular cooldown and hourly action configuration UI.

#### C. Modal Fixes (`Modal.tsx` & `AccessPanel.tsx`)
- In `Modal.tsx`:
  - Add backdrop click handler: `onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}`.
  - Ensure title header is rendered or close button is available when `title=""`.
- In `AccessPanel.tsx`:
  - Add explicit "Close" button calling `onClose` prop.
- In `Header.tsx`:
  - Pass `title="Staff Access Management"` and `onClose={() => setAccessOpen(false)}`.

#### D. Webhook Dispatch Routing
- In `useSend.ts`:
  - Ensure webhook messages for staff members route through `/api/send` (`mode: "webhook"`) instead of `sendWebhookDirect`, guaranteeing mention scrubbing and audit logging.

---

## 6. Verification and Validation Plan

1. **Automated Vitest Suite**:
   - `npm test`: Verify all existing 155 tests in shared, server, and client continue to pass.
   - Add new tests in `server/src/utils/mentionScrubber.test.ts` testing case-insensitive mentions (`@Everyone`, `@HERE`), role mention filtering, and component action flow scrubbing.
   - Add new tests in `server/src/middleware/staffPermissions.test.ts` verifying empty channel allowlist denials and granular cooldowns.
2. **REST API Endpoint Testing**:
   - Verify `GET /api/discord/guilds`, `GET /api/discord/guilds/:guildId/channels`, `GET /api/discord/guilds/:guildId/roles`, and `GET /api/discord/guilds/:guildId/members?query=...`.
3. **Staff Access & Modal Interaction Testing**:
   - Open Staff Access modal on `http://localhost:5175/`, verify close button works and clicking backdrop closes modal.
   - Test adding staff member via searchable name lookup.
