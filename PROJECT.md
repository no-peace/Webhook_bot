# Project: Hoho Manager — Discohook Layout Clone & Security Refactor

## Architecture
- **Frontend (`hoho_manager/client`)**: React 18, TypeScript, TailwindCSS, Lucide icons, Zustand/Context state. Discohook 3-pane layout: Left Sidebar (Guild selector, navigation, component palette, layers), Center Editor (message body, embeds, visual Action Rows), Right Live Preview (Discord-fidelity message rendering with dynamic bot avatar).
- **Backend (`hoho_manager/server`)**: Express 5 (ESM), TypeScript, better-sqlite3 (WAL mode) with dialect-neutral `DatabaseClient` abstraction. Endpoints for `/api/send`, `/api/discord`, `/api/settings`, `/api/profiles`, `/api/access`, `/api/interactions`.
- **Bot Worker (`hoho_manager/bot`)**: `@sapphire/framework` Discord bot listening to gateway events, relaying interactions to backend, and executing `/send` commands.
- **Shared (`hoho_manager/packages/shared`)**: Shared TypeScript schemas, Discord types, and validation rules.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | 3-Pane Layout | Discohook-style 3 panes: Sidebar, Editor, Preview | M3 | R1 |
| F2 | Deduplicate Mode & UI | Consolidate duplicate mode toggles, palettes, and previews into single unified workflow | M3 | R1 |
| F3 | Bot Avatar Live Preview | Preview correctly loads bot profile picture via auto-fetched bot identity | M3 | R1 |
| F4 | Visual Action Rows & Modals | Intuitive Action Row builder with button pills, style badges, drag/reorder, and nested components | M3 | R1 |
| F5 | Global Server (Guild) Dropdown | Global "Selected Server" selector driving channel/role/member context | M2 | R2 |
| F6 | Dynamic Discord API Fetching | Searchable dropdowns for channels, roles, and members without server-side entity caching | M1, M2 | R2 |
| F7 | Manual ID Fallback | Channel, role, and member inputs accept manual snowflake ID strings alongside dropdowns | M2 | R2 |
| F8 | Auto-Fetch Bot Identity | Automatically fetch bot profile on load, removing manual "Sync Cache" button | M2 | R2 |
| F9 | Head Admin Settings Area | Dedicated Settings page/modal accessible only to authorized Head Admins | M1, M2 | R3 |
| F10 | Bot & Webhook Profile Relocation | Move bot and webhook profile management from main UI into Settings area | M2 | R3 |
| F11 | Database-Backed Settings Migration | Migration 005_settings and settingsService to store `LOG_CHANNEL_ID` and Head Admin IDs in DB rather than `.env` | M1 | R3 |
| F12 | Staff Search by Name | Search/fetch members by name in Staff Access flow with snowflake ID as primary key | M1, M2 | R4 |
| F13 | Strict Zero-Bypass Mention Scrubbing | Prevent mention bypasses across bot messages, webhooks, component flows, role IDs, regex (case-insensitive) | M1 | R4 |
| F14 | Granular Cooldowns & Rate Limits | Configure cooldowns and max-action per hour per action type (send, edit, delete, templates) | M1, M2 | R4 |
| F15 | Allowed Channel & Role Mention Dropdowns | Dynamic server-fetched dropdowns for `allowed_channel_ids` and `allowed_role_mention_ids` | M2 | R4 |
| F16 | Staff Access Modal Close & Backdrop Fix | Working Close button and backdrop dismiss for Staff Access modal (no UI trap) | M2 | R4 |
| F17 | Fix Channel Allowlist Security Bug | Remove default-allow flaw in `staffPermissions.ts:140` when `allowed.length === 0` | M1 | R4 |
| F18 | Comprehensive E2E Test Suite | Opaque-box test suite covering Tiers 1-4 with 100% pass rate + Tier 5 adversarial hardening | M4 | All |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Backend Security, Database Settings & Dynamic Discord API | Migration 005_settings, settingsService, requireHeadAdmin auth, /api/discord endpoints (guilds, roles, member search), fix channel allowlist default-deny bug, zero-bypass mention scrubber (case-insensitive, flows, webhook routing), granular rate limits | Survey | PLANNED |
| M2 | Frontend Global Context, Dynamic Dropdowns & Settings Page | Global Selected Guild dropdown, SearchableDiscordSelect with client caching and manual ID fallback, auto-fetch bot identity, Head Admin Settings modal (profile management + DB settings update), Staff Access modal fix (backdrop + close), staff member search by name, granular permission toggles | M1 | PLANNED |
| M3 | Discohook 3-Pane Layout, Unified Preview & Component V2 Integration | Re-layout client into Discohook 3 panes (Sidebar, Editor, unified Preview), eliminate duplicate mode toggles and palettes, integrate DiscohookComponentsEditor for visual Action Rows, live bot avatar rendering in preview | M2 | PLANNED |
| M4 | E2E Test Suite Verification & Adversarial Hardening | Run comprehensive E2E test suite across Tiers 1-4 (100% pass), execute Tier 5 adversarial testing with Challenger, run Forensic Integrity Audit | M3 | PLANNED |

## Interface Contracts

### 1. Discord Entity API
- `GET /api/discord/guilds`: Returns list of available guilds `{ guilds: Array<{ id: string, name: string, icon: string | null }> }`.
- `GET /api/discord/guilds/:guildId/channels`: Returns `{ channels: Array<{ id: string, name: string, type: number, parent_id: string | null }> }`.
- `GET /api/discord/guilds/:guildId/roles`: Returns `{ roles: Array<{ id: string, name: string, color: number, position: number }> }`.
- `GET /api/discord/guilds/:guildId/members/search?query=:q`: Returns `{ members: Array<{ id: string, username: string, global_name: string | null, nickname: string | null, avatar: string | null }> }`.
- Live fetching without server-side caching of entities.

### 2. Settings API
- `GET /api/settings?guildId=:guildId`: Returns `{ log_channel_id: string | null, head_admin_ids: string[], bot_profile_id: string | null, is_head_admin: boolean }`.
- `PUT /api/settings`: Payload `{ guildId?: string, log_channel_id?: string, head_admin_ids?: string[], bot_profile_id?: string }`. Guarded by `requireHeadAdmin` (`x-admin-key` OR caller's `x-staff-id` in `head_admin_ids`).

### 3. Mention Scrubbing & Staff Permissions
- `scrubMentions(content, perms)`:
  - Strips `@everyone` and `@here` using case-insensitive regex `/@everyone/gi` and `/@here/gi` if `can_mention_everyone === 0`.
  - Strips user/role mentions unless explicitly allowed or present in `allowed_role_mention_ids`.
  - Applied to `sanitizedMessage.content`, embeds, AND `flows` action parameters.
- All client sends (including webhooks) dispatched through backend `/api/send` with staff headers to ensure consistent scrubbing and logging.
- Channel check: `allowed.length === 0` means **DENY ALL** (default-deny), NOT allow all.

### 4. Client Layout & Global Store
- `useGlobalStore`:
  - `selectedGuildId: string | null`
  - `botIdentity: { username: string, avatar: string | null, id: string } | null`
  - `discordCache: Record<string, { data: any, timestamp: number }>` (client-side cache with 60s TTL)
- `Modal.tsx`:
  - Backdrop `onClick={onClose}`.
  - Header close button always rendered when `onClose` is provided.

## Code Layout
- `hoho_manager/packages/shared/src/`: Types and schemas (`types.ts`, `schemas.ts`, `discord.ts`).
- `hoho_manager/server/src/`:
  - `config/`: `database.ts`, `migrations.ts`, `env.ts`.
  - `middleware/`: `auth.ts` (`requireHeadAdmin`), `staffPermissions.ts` (channel check fix).
  - `services/`: `settingsService.ts`, `discordService.ts`, `auditLog.ts`.
  - `routes/`: `settings.ts`, `discord.ts`, `send.ts`, `profiles.ts`, `access.ts`.
  - `utils/`: `mentionScrubber.ts`.
- `hoho_manager/client/src/`:
  - `components/layout/`: `Sidebar.tsx`, `Header.tsx`, `AccessPanel.tsx`, `SettingsModal.tsx`.
  - `components/editor/`: `MessageEditor.tsx`, `DiscohookComponentsEditor.tsx`, `ComponentPalette.tsx`, `LayersPanel.tsx`.
  - `components/preview/`: `MessagePreview.tsx`.
  - `components/ui/`: `Modal.tsx`, `SearchableDiscordSelect.tsx`.
  - `stores/`: `useGlobalStore.ts`.
  - `App.tsx`: 3-pane layout assembly.
- `hoho_manager/tests/`: E2E test suite and runner scripts.
