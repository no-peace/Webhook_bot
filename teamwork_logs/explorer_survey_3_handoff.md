# Handoff Report — Discord Bot API, Staff Access & Mention Scrubbing Survey

**Agent**: `explorer_survey_3`  
**Handoff Type**: Hard (Task complete)  
**Date**: 2026-10-03  

---

## 1. Observation

1. **Test Suite Status**: Executed `npm test` from `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\hoho_manager`. All 155 tests passed (14 in `@dmb/shared`, 95 in `server`, 46 in `client`).
2. **Bot Architecture**: 
   - Gateway worker (`hoho_manager/bot/src/index.ts:37-45`) connects using `@sapphire/framework` with `intents: [GatewayIntentBits.Guilds]`.
   - Gateway worker listens to `raw` packets (`bot/src/listeners/interactionRelay.ts:13-28`) and relays `INTERACTION_CREATE` to `POST /api/interactions/relay` with `x-admin-key`.
   - `/send` command (`bot/src/commands/send.ts:52`) calls `api.sendMessage` (`bot/src/lib/api.ts:109`) hitting backend Express `POST /api/send`.
3. **Entity Fetching**:
   - `discordService.ts:299-318` provides `getBotGuilds(profileId)` and `getGuildChannels(guildId, profileId)`.
   - `send.ts:151` hardcodes taking the first guild: `const [guild] = await discord.getBotGuilds(profileId);` and fetches channels only for `guild.id`. It accepts no `guildId` parameter.
   - `discordService.ts` contains NO method to fetch guild roles (`GET /guilds/{guildId}/roles`).
   - `discordService.ts:358` only has `getGuildMember(guildId, userId, token)`. It has NO member search (`GET /guilds/{guildId}/members/search`) or member list endpoint.
   - `send.ts:204-220` exposes `GET /api/send/identity`, but `BotDispatchModal.tsx:98-124` only syncs identity when the user manually clicks `syncBotIdentity`.
4. **Staff Access & Channel Allowlist Logic Bug**:
   - In `server/src/middleware/staffPermissions.ts:139-141`:
     ```typescript
     try { allowed = JSON.parse(record.allowed_channel_ids); } catch { allowed = []; }
     const allAllowed = allowed.includes("*") || allowed.length === 0; // empty = all denied by default
     if (!allAllowed && !allowed.includes(channelId)) { ... }
     ```
     `allowed.length === 0` makes `allAllowed = true`, allowing empty channel lists to access ALL channels instead of denying them.
5. **Staff Access Modal UX Trap**:
   - In `client/src/components/layout/Header.tsx:263-272`:
     ```tsx
     <Modal open={accessOpen} onClose={() => setAccessOpen(false)} title="" width="max-w-4xl">
       <div className="h-[70vh]">{accessOpen && <AccessPanel />}</div>
     </Modal>
     ```
   - In `client/src/components/ui/Modal.tsx:43`: `{title && (` only renders title and the `X` button when `title` is truthy. When `title=""`, no close button exists.
   - In `Modal.tsx:37`: The backdrop `div` lacks an `onClick={onClose}` handler.
   - In `AccessPanel.tsx:72-86`: There is no close button in the panel header. Users cannot close the modal.
6. **Mention Scrubbing Flaws**:
   - Case-sensitivity: In `server/src/utils/mentionScrubber.ts:25-32`:
     ```typescript
     if (!perms.can_mention_everyone && result.includes("@everyone")) {
       result = result.replace(/@everyone/g, "@\u200beveryone");
     ```
     `result.includes("@everyone")` is case-sensitive. `@Everyone` and `@HERE` bypass the filter.
   - Direct Webhook Bypass: In `client/src/hooks/useSend.ts:76`:
     ```typescript
     result = await sendWebhookDirect(webhookUrl, payload, { threadId: threadId || undefined });
     ```
     Sends directly to Discord, bypassing `/api/send`, mention scrubbing, and staff permissions entirely.
   - Unscrubbed Component Flows: In `server/src/routes/send.ts:60-96`, `sanitizedMessage` is scrubbed with `scrubMentions`, but `body.flows` (`parseFlowRegistrations(body.flows)`) is passed unscrubbed into `actionRepository.registerFlows(messageId, flows)`.
   - `sanitizeAllowedMentions` logic flaw in `server/src/utils/mentionScrubber.ts:80-94`: `parse` never includes `"roles"`, and if `allowed_role_mention_ids` is empty when `can_mention_roles === 1`, all role mentions are stripped.

---

## 2. Logic Chain

1. **Discord API Live Fetching**:
   - From Observations 3, the current system cannot support a global "Selected Server" dropdown because the backend only ever inspects the first guild (`[guild] = ...`) and lacks endpoints for roles and member searching.
   - Implementing `GET /guilds/{guildId}/roles` and `GET /guilds/{guildId}/members/search` in `discordService.ts` and exposing them under `/api/discord/*` allows the frontend to populate searchable dropdowns live without storing any Discord entity records in the database.
2. **Staff Access Permission & UX Fixes**:
   - From Observation 4, `allowed.length === 0` in `staffPermissions.ts:140` inverts security logic, granting unauthorized access to all channels. Removing `|| allowed.length === 0` enforces the intended default-deny behavior.
   - From Observation 5, fixing `Modal.tsx` backdrop click and adding an explicit close button in `AccessPanel.tsx` restores normal modal dismissal.
   - Adding granular fields for cooldowns and hourly rate limits per action (`send`, `edit`, `delete`, `templates`) in `staff_access` fulfills the granular control requirement.
3. **Mention Scrubbing Zero-Bypass Defense**:
   - From Observation 6, Discord parses mentions case-insensitively. Switching `mentionScrubber.ts` to `/@everyone/gi` and `/@here/gi` closes the `@Everyone` bypass.
   - Routing all client sends (including webhooks) through backend `/api/send` closes the direct browser bypass.
   - Scrubbing `body.flows` before storing action definitions in `actionRepository` closes the Component V2 flow bypass.
   - Correcting `sanitizeAllowedMentions` ensures that Discord only permits mentions explicitly authorized by staff permissions.

---

## 3. Caveats

- **Privileged Intents**: Discord member searching via REST (`GET /guilds/{guildId}/members/search?query=...`) requires the `GuildMembers` intent in some configurations or sufficient bot permissions (`MANAGE_GUILD` or `MODERATE_MEMBERS`). For small servers, bots can search members without privileged gateway intent, but in large servers with >10,000 members, Discord Developer Portal "Server Members Intent" must be toggled if full listing is required.
- **Client Cache Invalidation**: Since Discord entity data is not cached on the server, high frequency switching between dropdowns could trigger Discord 429 rate limits if client-side caching is not employed. The client should hold an in-memory cache with a 30-60 second TTL.

---

## 4. Conclusion

1. **Bot & REST Layer**: The Sapphire gateway relay architecture functions well for headless operation, but the REST service requires new endpoints for guild listing, guild roles, and member searching.
2. **Staff Access**: The channel allowlist default-deny bug and modal closure trap must be fixed immediately. Granular cooldowns and hourly limits can be accommodated via JSON columns or dedicated table columns in migration `005`.
3. **Mention Scrubbing**: The existing scrubber has multiple critical bypasses (case sensitivity, client-side webhook bypass, unscrubbed action flows). A unified multi-stage scrubber will close all attack vectors.

A comprehensive technical blueprint and implementation roadmap is documented in `report.md`.

---

## 5. Verification Method

1. **Automated Tests**:
   - Run the workspace test suite:
     ```bash
     cd C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\hoho_manager
     npm test
     ```
   - Verify that all 155 tests pass without regressions.
2. **Code Inspection**:
   - Check `hoho_manager/server/src/middleware/staffPermissions.ts:140` to confirm channel allowlist logic.
   - Check `hoho_manager/client/src/components/ui/Modal.tsx:37-43` and `AccessPanel.tsx:73-85` to confirm modal close behaviors.
   - Check `hoho_manager/server/src/utils/mentionScrubber.ts:25-32` to confirm case-insensitive regex usage.
3. **Live UI Verification**:
   - Inspect `http://localhost:5175/`:
     - Test opening and closing the Staff Access Panel.
     - Inspect API response on `/api/health` and `/api/config`.
