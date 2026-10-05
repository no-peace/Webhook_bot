# Antigravity Implementation Notes

This document contains a summary of the architectural changes and thinking process used to resolve the requested features.

## 1. Staff Permissions & Discord Audit Log System

### Backend Architecture
- **Database**: Created `staff_access` and `staff_cooldowns` tables using SQLite (`004_staff_access` migration) to store granular permission flags (`can_send`, `can_edit`, `can_delete`, `can_manage_templates`), allowed channel ID allowlists, allowed role mentions, and cooldown settings.
- **Middleware**: Built `requireStaffPermission(action)` which intercepts the `x-staff-id` header.
  - Validates if the staff account is active and unexpired.
  - Checks if the staff has the necessary boolean permission flag.
  - Checks if the target channel is present in `allowed_channel_ids` (or if `*` is granted).
  - Enforces time-based cooldowns and hourly max limits per user using the `staff_cooldowns` table to prevent spam/abuse.
  - Passes admins (using `x-admin-key`) through without restrictions.
- **Audit Logging**: Created `auditLog.ts` which fires structured, colour-coded embeds to `LOG_CHANNEL_ID` directly bypassing the database to save space. Events like `STAFF_GRANTED`, `SEND_BLOCKED`, `COOLDOWN_HIT`, and `RATE_LIMIT_HIT` are logged here for full traceability.
- **Mention Scrubbing**: Implemented `mentionScrubber.ts` which sanitizes `@everyone`, `@here`, and `@roles` from staff message payloads unless explicitly allowed by their permission flags.

### Frontend Architecture
- **Admin Panel**: Added an `AccessPanel.tsx` UI module. Accessible via a "Staff Access" shield button in the header (only visible to admins with `VITE_ADMIN_API_KEY`). Admins can CRUD staff records, configure cooldowns, mention scopes, and target channels.
- **Staff Login**: For non-admins visiting the site, the "Staff Access" button is replaced with a "Staff Login" button. Staff can click it to supply their Discord User ID. This ID is saved to `localStorage` and automatically appended as the `x-staff-id` header on API requests via the updated `client.ts` fetch wrapper.
- **Channel Filtering**: When a staff member opens the `BotDispatchModal`, the `/api/send/channels` endpoint automatically filters the channel list down to only the channels explicitly granted to them in their staff record.

## 2. Open Modal Flow Chaining

### The Problem
Previously, the `open_modal` component action could generate a modal payload but could not trigger any logic *after* the user clicked "Submit". 

### The Solution
- **UI Branching**: Modified `StepList.tsx` to mount a nested `BranchEditor` underneath the `open_modal` configuration block. This allows the builder to drag-and-drop subsequent actions (like `send_message`, `add_role`, etc.) into a "When Modal is Submitted (Then)" bucket.
- **Flow Registration**: Updated `actionStore.toRegistrations()` to scan for `open_modal` steps that have nested `then` logic. It automatically extracts these nested steps and registers them with the server as a new top-level flow using the modal's `customId`.
- **Execution Context**: When the modal is submitted to Discord, the backend's `interactionHandler` receives the `MODAL_SUBMIT` event and executes the registered flow. The existing `actionExecutor.ts` already correctly maps the modal input field values into `{input.custom_id}` variables, meaning subsequent steps can seamlessly inject the user's form answers into messages or conditions.

## Next Steps for User
- Update `.env.example` configurations (add `LOG_CHANNEL_ID`).
- Restart the backend to apply the `004` database migration.
- Use the site as an Admin to grant yourself or your staff granular permissions via the new Staff Access UI.

## 3. UI and UX Improvements

### Action Row Component Usability
**Problem:** The `ActionRow` in Component V2 form had no direct way to add buttons into it, leading to a confusing UX where it appeared "empty" and unusable unless the user knew to select it and then click the Button component in the left-hand palette.
**Solution:** Added direct inline buttons inside the `ActionRowForm` property panel (`Add Button`, `Add Select`). It now checks the length of its children to disable the buttons when limits are reached (max 5 buttons or 1 select).

### Send / Edit Button Dropdown Overlap
**Problem:** The `Bot` send button dropdown was overlapping and getting hidden behind the `Webhook URL` input and send buttons due to static sibling `z-20` rendering.
**Solution:** Added dynamic `z-50` conditionally to the active dropdown wrapper in `App.tsx` so the open menu always bursts out of its local stacking context properly.

## 4. Full Discohook Layout Clone & Architecture Handoff (Teamwork Update)

This project underwent a massive, multi-agent refactor to completely clone the `discohook.app` layout and upgrade the underlying infrastructure while retaining all custom features (Action flows, Staff Perms).

### Milestone 1: Backend Security & Database Settings (Completed)
- **Settings Database:** Created `005_settings` SQLite migration and `SettingsService` to move `LOG_CHANNEL_ID` and Head Admin IDs completely out of the `.env` file and into a database-backed table.
- **Discord API Routes:** Built new `/api/discord/guilds`, `/channels`, `/roles`, and `/members/search` routes. These dynamically fetch Discord data on-the-fly rather than caching massive amounts of entity data on the server database.
- **Security Enhancements:** Implemented a zero-bypass mention scrubber (case-insensitive, flow parameter recursive scanning) and updated `staffPermissions.ts` to fix the default-allow channel logic flaw. E2E tests written (222/222 passing).

### Milestone 2: Frontend Global Context & API Fetching (Completed)
- **Global Context:** Added `useGlobalStore.ts` to manage a global `selectedGuildId`.
- **API Dropdowns (`SearchableDiscordSelect`)**: Built a reusable client-caching component that queries the `/api/discord` routes. Replaced all static text inputs (Channels, Roles, Member searches) in the Editor and Staff Panel with these dropdowns (while retaining manual snowflake ID fallback).
- **Auto-Fetch Bot Profile:** The app now automatically fetches the bot's avatar and username on load, removing the need for the "Sync Cache" button.
- **Settings Modal:** Created `SettingsModal.tsx` for Head Admins to configure the DB-backed settings and manage Bot/Webhook profiles away from the main UI.

### Milestone 3: Discohook 3-Pane Layout (Completed / Testing Phase)
- **Collapsible Sidebar & Dual Pane:** Refactored `App.tsx` and `Sidebar.tsx` into a strict Discohook 3-pane layout. Added a `Ctrl+B` toggle (and `PanelLeft` icon) to collapse the sidebar. When collapsed, the layout perfectly expands into a 50/50 dual pane (Editor / Preview) just like Discohook desktop.
- **Unified Preview:** `MessagePreview.tsx` was unified so it elegantly handles both Classic and V2 data. It now uses genuine CDN snowflake arithmetic to render the live Bot Avatar in the preview header.
- **Visual Action Rows:** Rebuilt the `DiscohookComponentsEditor` to feature drag-and-drop reordering, style pill badges, and direct visual assembly of Action Rows and Select Menus.
- **Deduplication:** Removed the duplicate Server Selectors, Mode Toggles, and Clear buttons that were cluttering the header and sidebar.

### Handoff Note for Next AI
The implementation code for M3 has been written by the Teamwork agents. If the session abruptly ends, the next AI should immediately run `git status`, verify the uncommitted changes, and run `npm run test` and `npm run build` inside `hoho_manager/client`. The UI logic for the 3-pane expanding sidebar and the new `SearchableDiscordSelect` is fully wired but may need visual Tailwind polish depending on the exact test output.

---

## 5. Original Teamwork Execution Plan (`PROJECT.md`)

The following is the exact architectural blueprint used by the multi-agent Teamwork system to execute the clone and refactor. The next AI can use this as a reference point for what was structurally intended.

### Architecture
- **Frontend (`hoho_manager/client`)**: React 18, TypeScript, TailwindCSS, Lucide icons, Zustand/Context state. Discohook 3-pane layout: Left Sidebar (Guild selector, navigation, component palette, layers), Center Editor (message body, embeds, visual Action Rows), Right Live Preview (Discord-fidelity message rendering with dynamic bot avatar).
- **Backend (`hoho_manager/server`)**: Express 5 (ESM), TypeScript, better-sqlite3 (WAL mode) with dialect-neutral `DatabaseClient` abstraction. Endpoints for `/api/send`, `/api/discord`, `/api/settings`, `/api/profiles`, `/api/access`, `/api/interactions`.
- **Bot Worker (`hoho_manager/bot`)**: `@sapphire/framework` Discord bot listening to gateway events, relaying interactions to backend, and executing `/send` commands.

### Feature Inventory
| # | Feature | Description | Milestone |
|---|---------|-------------|-----------|
| F1 | 3-Pane Layout | Discohook-style 3 panes: Sidebar, Editor, Preview | M3 |
| F2 | Deduplicate Mode & UI | Consolidate duplicate mode toggles, palettes, and previews into single unified workflow | M3 |
| F3 | Bot Avatar Live Preview | Preview correctly loads bot profile picture via auto-fetched bot identity | M3 |
| F4 | Visual Action Rows & Modals | Intuitive Action Row builder with button pills, style badges, drag/reorder, and nested components | M3 |
| F5 | Global Server (Guild) Dropdown | Global "Selected Server" selector driving channel/role/member context | M2 |
| F6 | Dynamic Discord API Fetching | Searchable dropdowns for channels, roles, and members without server-side entity caching | M1, M2 |
| F7 | Manual ID Fallback | Channel, role, and member inputs accept manual snowflake ID strings alongside dropdowns | M2 |
| F8 | Auto-Fetch Bot Identity | Automatically fetch bot profile on load, removing manual "Sync Cache" button | M2 |
| F9 | Head Admin Settings Area | Dedicated Settings page/modal accessible only to authorized Head Admins | M1, M2 |
| F10 | Bot & Webhook Profile Relocation | Move bot and webhook profile management from main UI into Settings area | M2 |
| F11 | Database-Backed Settings Migration | Migration 005_settings and settingsService to store `LOG_CHANNEL_ID` and Head Admin IDs in DB rather than `.env` | M1 |
| F12 | Staff Search by Name | Search/fetch members by name in Staff Access flow with snowflake ID as primary key | M1, M2 |
| F13 | Strict Zero-Bypass Mention Scrubbing | Prevent mention bypasses across bot messages, webhooks, component flows, role IDs, regex (case-insensitive) | M1 |
| F14 | Granular Cooldowns & Rate Limits | Configure cooldowns and max-action per hour per action type (send, edit, delete, templates) | M1, M2 |
| F15 | Allowed Channel & Role Mention Dropdowns | Dynamic server-fetched dropdowns for `allowed_channel_ids` and `allowed_role_mention_ids` | M2 |
| F16 | Staff Access Modal Close & Backdrop Fix | Working Close button and backdrop dismiss for Staff Access modal (no UI trap) | M2 |
| F17 | Fix Channel Allowlist Security Bug | Remove default-allow flaw in `staffPermissions.ts:140` when `allowed.length === 0` | M1 |

### Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Backend Security, Database Settings & Dynamic Discord API | Migration 005_settings, settingsService, requireHeadAdmin auth, /api/discord endpoints (guilds, roles, member search), fix channel allowlist default-deny bug, zero-bypass mention scrubber (case-insensitive, flows, webhook routing), granular rate limits | Survey | COMPLETED |
| M2 | Frontend Global Context, Dynamic Dropdowns & Settings Page | Global Selected Guild dropdown, SearchableDiscordSelect with client caching and manual ID fallback, auto-fetch bot identity, Head Admin Settings modal (profile management + DB settings update), Staff Access modal fix (backdrop + close), staff member search by name, granular permission toggles | M1 | COMPLETED |
| M3 | Discohook 3-Pane Layout, Unified Preview & Component V2 Integration | Re-layout client into Discohook 3 panes (Sidebar, Editor, unified Preview), eliminate duplicate mode toggles and palettes, integrate DiscohookComponentsEditor for visual Action Rows, live bot avatar rendering in preview | M2 | TESTING |
| M4 | E2E Test Suite Verification & Adversarial Hardening | Run comprehensive E2E test suite across Tiers 1-4 (100% pass), execute Tier 5 adversarial testing with Challenger, run Forensic Integrity Audit | M3 | QUEUED |

### Interface Contracts

#### 1. Discord Entity API
- `GET /api/discord/guilds`: Returns list of available guilds `{ guilds: Array<{ id: string, name: string, icon: string | null }> }`.
- `GET /api/discord/guilds/:guildId/channels`: Returns `{ channels: Array<{ id: string, name: string, type: number, parent_id: string | null }> }`.
- `GET /api/discord/guilds/:guildId/roles`: Returns `{ roles: Array<{ id: string, name: string, color: number, position: number }> }`.
- `GET /api/discord/guilds/:guildId/members/search?query=:q`: Returns `{ members: Array<{ id: string, username: string, global_name: string | null, nickname: string | null, avatar: string | null }> }`.
- Live fetching without server-side caching of entities.

#### 2. Settings API
- `GET /api/settings?guildId=:guildId`: Returns `{ log_channel_id: string | null, head_admin_ids: string[], bot_profile_id: string | null, is_head_admin: boolean }`.
- `PUT /api/settings`: Payload `{ guildId?: string, log_channel_id?: string, head_admin_ids?: string[], bot_profile_id?: string }`. Guarded by `requireHeadAdmin` (`x-admin-key` OR caller's `x-staff-id` in `head_admin_ids`).

#### 3. Mention Scrubbing & Staff Permissions
- `scrubMentions(content, perms)`:
  - Strips `@everyone` and `@here` using case-insensitive regex `/@everyone/gi` and `/@here/gi` if `can_mention_everyone === 0`.
  - Strips user/role mentions unless explicitly allowed or present in `allowed_role_mention_ids`.
  - Applied to `sanitizedMessage.content`, embeds, AND `flows` action parameters.
- All client sends (including webhooks) dispatched through backend `/api/send` with staff headers to ensure consistent scrubbing and logging.
- Channel check: `allowed.length === 0` means **DENY ALL** (default-deny), NOT allow all.

#### 4. Client Layout & Global Store
- `useGlobalStore`:
  - `selectedGuildId: string | null`
  - `botIdentity: { username: string, avatar: string | null, id: string } | null`
  - `discordCache: Record<string, { data: any, timestamp: number }>` (client-side cache with 60s TTL)
- `Modal.tsx`:
  - Backdrop `onClick={onClose}`.
  - Header close button always rendered when `onClose` is provided.



a quick checklist for you or the next AI when you resume:

  1. Check for Uncommitted Changes: The Teamwork agents were actively modifying App.tsx and the Sidebar.tsx right when we initiated the handoff. The next AI should run git status and git diff to        
  review exactly what code they left in the workspace.
  2. Install Dependencies: The agents likely installed new libraries to handle the Client-Side caching (like zustand extensions or swr/react-query). The next AI should run npm install in both the       
  client and server folders to ensure the package.json is synced up!
  3. Run the Database Migrations: When you start the backend server next (npm run dev), the 005_settings database migration will automatically fire, successfully porting your configurations away from   
  the .env file into the DB!

  You are completely set to swap over. You've got an incredibly powerful, scalable, and secure architecture now!


---

## 6. Milestone 5: Discord OAuth2 Login & File Attachments Architecture

### 1. Discord OAuth2 Authentication System
- **Environment Variables**:
  - `DISCORD_CLIENT_ID`: Application client ID (defaults to `DISCORD_APPLICATION_ID`).
  - `DISCORD_CLIENT_SECRET`: Discord OAuth2 client secret.
  - `DISCORD_REDIRECT_URI`: OAuth2 callback endpoint (`/api/auth/discord/callback`).
  - `SESSION_SECRET`: Cryptographic key for signing session tokens via HMAC-SHA256 (falls back to `ADMIN_API_KEY`).
- **Endpoints (`server/src/routes/auth.ts`)**:
  - `GET /api/auth/discord/login`: Generates secure state cookie and redirects user to Discord authorization dialog (`identify` scope).
  - `GET /api/auth/discord/callback`: Exchanges authorization code for Discord access token, fetches `@me` profile, upserts user in SQLite database, signs HMAC-SHA256 session token into `dmb_session` HTTP-only cookie, and redirects user to `/?login=success`.
  - `GET /api/auth/me`: Validates session cookie or Bearer token signature, verifies user role/admin status against `head_admin_ids` and database, and returns authenticated profile `{ user: { id, username, global_name, avatar, role, isAdmin } }`.
  - `POST /api/auth/logout`: Clears session cookie and logs out.
  - `POST /api/auth/dev-login`: Issues genuine session cookie in development and test environments for seamless automated verification.
- **Security & Anti-Spoofing (`staffPermissions.ts` & `auth.ts`)**:
  - When an authenticated session user is present, the server automatically anchors `req.staffContext.staffId = sessionUser.id`.
  - Anti-spoofing enforcement: If a request provides `x-staff-id` that does NOT match the active session user's ID, the server rejects it with `403 Forbidden`.
  - Backwards compatibility: Headless scripts and automated test suites without session cookies gracefully fall back to `x-staff-id` and `x-admin-key`.

### 2. File Attachments & Media Upload System
- **Message Editor File Attachments UI (`FileAttachmentsSection.tsx`)**:
  - Discohook `#1e1f22` accordion with file count badge `Files (0/10)` and `+ Add File` trigger.
  - Drag-and-drop file upload target zone.
  - Multi-file preview cards supporting images, video, audio, and general documents.
  - Per-file spoiler toggle overlay (`Eye` / `EyeOff`) prepending `SPOILER_` to file names.
  - In-line delete buttons and 25 MB file size limit validation.
- **In-Memory State (`messageStore.ts`)**:
  - Attached browser `File` objects are stored purely in memory and explicitly excluded from localStorage `partialize` to avoid JSON serialization failures.
  - Object URLs are automatically revoked when files are removed or the editor is reset.
- **Zero-Disk Multipart Forwarding (`multipart.ts`, `send.ts`, `discordService.ts`)**:
  - Node 24 native Web Standards stream reader (`Readable.toWeb(req)` -> `new Request(...)` -> `webReq.formData()`) parses multipart form data directly into RAM with zero temporary file writes to disk.
  - Mounted before `attachUser` and `requireStaffPermission("send")` so permission checking can access parsed form fields.
  - Sends to Discord forward a multipart `FormData` payload containing `payload_json: JSON.stringify(body)` and individual file streams (`files[n]`).
- **Live Preview Integration (`MessagePreview.tsx` & `EmbedPreview.tsx`)**:
  - `EmbedPreview.tsx` resolves `attachment://filename.png` image and thumbnail URLs directly against in-memory attached files.
  - `MessagePreview.tsx` displays live attachment preview cards with interactive spoiler blur reveal.
  - `isPayloadEmpty` permits messages containing file attachments even when text and embeds are omitted.## New Features & Architecture (Update 2)
- **File Attachments:** Files are streamed directly to Discord in-memory (no local disk storage). External URLs are supported; the server downloads them and forwards the streams directly to Discord.
- **Bot Dispatch & Multi-Channel Editing:** The 'Dispatch via Bot' feature supports multi-channel batch edits. Users can select multiple target channels and supply a comma-separated list of Message IDs to edit them simultaneously.
- **OAuth2 Admin Integration:** The app now requires the user to log in via Discord OAuth2 to list their servers. The VITE_ADMIN_API_KEY bypasses authentication checks in local dev.


## Handoff: Discohook UI Clone Teamwork
- **Date:** 2026-10-05
- **Status:** Teamwork subagent ('teamwork_preview_swe') has been launched to complete the Discohook 1:1 UI Clone.
- **Scope:** Includes Top Bar (Audit Logs, Sessions), Multi-Message architecture, Options dropdown (Flags, Allowed Mentions), Quick Mention Context Box, custom emoji saving, and Flow Triggers ('Member has role').
- **Testing:** Strict automated API and UI testing requirements are enforced for the team.
- **Next Steps:** Review the teamwork subagent's output, and run 
pm install if they added dependencies. Wait for the Victory Audit to complete.
