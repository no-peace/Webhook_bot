# Frontend Architecture Survey & Discohook Refactoring Specification

**Target System**: Hoho Manager (Discord Message Builder)  
**Author**: Frontend Architect Explorer  
**Date**: 2026-10-03  
**Status**: Completed  
**Reference Codebase**: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\hoho_manager`  
**Discohook Reference**: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\discohook_src`  
**Live Site Verified**: `http://localhost:5175/` (Backend: `http://localhost:3001/`)

---

## Executive Summary

A comprehensive architectural investigation was conducted across the Hoho Manager frontend (`hoho_manager/client`), its backend service (`hoho_manager/server`), and the reference Discohook implementation (`discohook_src`). 

Key architectural conclusions:
1. **Layout & Panes**: Hoho Manager currently relies on a rigid 2-pane `SplitPane` layout (`App.tsx:482-667`). An existing `Sidebar.tsx` and `PropertyPanel.tsx` were created previously but left completely orphaned/unimported. To achieve Discohook's authentic 3-pane structure (Left Sidebar, Center Editor, Right Live Preview), the app must be restructured so that navigation, guild context, component palette, and layers live in the Left Sidebar; message text, embeds, and inline action rows live in the Center Editor; and a single, unified live preview occupies the Right Pane.
2. **Duplicate Elements**: Redundant UI elements clutter the interface—specifically duplicate "Editor Mode" toggles in both `Header.tsx:22-48` and `App.tsx:587-616`, duplicate Palette/Layers lists across `MessageEditor.tsx:97-109`, `App.tsx:624-649`, and `Sidebar.tsx:50-57`, and an accordion-mounted `ProfilesPanel` inside the message editor.
3. **Live Preview Bot Picture Failure**: In `MessagePreview.tsx:61-69`, the avatar only loads if `data.avatar_url` is manually typed. If empty, it falls back to a generic Lucide `<Bot>` icon, completely ignoring the configured bot identity. Automatic on-load fetching of the bot identity via `/api/send/identity` is required to display the real bot avatar and eliminate the manual "Sync Cache" button.
4. **Action Row & Modal UX Friction**: Building Action Rows in `ComponentForms.tsx:159-196` is cumbersome and disconnected from child controls. However, a fully functional visual row builder (`DiscohookComponentsEditor.tsx`, 228 lines) was already written but never imported or rendered. Integrating this component into the Center Editor solves Action Row usability immediately.
5. **Staff Access Modal Lockup Bug**: The Staff Access modal cannot be closed. In `Header.tsx:266`, `title=""` is passed to `<Modal>`, causing `Modal.tsx:43` to skip rendering the title bar and close button. Furthermore, `Modal.tsx:37` lacks any `onClick={onClose}` handler on the backdrop, locking users in the modal until page reload.
6. **Global Guild Context & API Fetching**: Currently, channels are hardcoded to the bot's first guild (`server/src/routes/send.ts:151`). There is no guild selector, no role fetching, and no member search. A global `Selected Server (Guild)` dropdown and searchable API comboboxes with manual snowflake fallback must be introduced across the application, Staff Panel, and action flows, supported by client-side caching.
7. **Settings Consolidation**: Bot profiles, webhook profiles, `LOG_CHANNEL_ID`, and Head Admin IDs must be relocated out of the editor and into a dedicated Head Admin Settings modal backed by a database `settings` table.

---

## 1. Frontend Codebase Anatomy & Tech Stack

### 1.1 Directory Structure
```
hoho_manager/client/
├── package.json               # Dependencies and scripts (React 19, Tailwind v4, Vite 8)
├── vite.config.ts             # Vite config with @ and @dmb/shared aliases, /api proxy
├── tsconfig.json              # TypeScript strict configuration
├── index.html                 # Single page app entry HTML
└── src/
    ├── main.tsx               # ReactDOM createRoot entry
    ├── App.tsx                # Main application component & layout assembly
    ├── api/
    │   ├── client.ts          # Central fetch wrapper with admin/staff headers & typed API
    │   └── discord.ts         # Direct client-side webhook dispatcher
    ├── components/
    │   ├── layout/
    │   │   ├── Header.tsx     # Top header bar (brand, template input, JSON tools, staff button)
    │   │   ├── Sidebar.tsx    # ORPHANED: 4-tab rail (Build, Send, Profs, Docs)
    │   │   ├── SplitPane.tsx  # Draggable 2-pane horizontal divider
    │   │   ├── AccessPanel.tsx# Staff permissions management panel
    │   │   ├── ProfilesPanel.tsx # Bot profiles CRUD form & list
    │   │   └── DocsPanel.tsx  # Quick documentation viewer
    │   ├── editor/
    │   │   ├── MessageEditor.tsx # Content, message identity, embed list, inline palette
    │   │   ├── DiscohookComponentsEditor.tsx # ORPHANED: Discohook-style Action Row builder
    │   │   ├── EmbedEditor.tsx   # Discord embed card editor with field builder
    │   │   ├── ComponentPalette.tsx # Draggable/clickable palette of V2 blocks
    │   │   ├── LayersPanel.tsx   # Component tree hierarchy & reordering
    │   │   ├── PropertyPanel.tsx # ORPHANED: Sidebar property inspector
    │   │   └── ComponentForms.tsx# Form controls for each Discord component type
    │   ├── preview/
    │   │   ├── MessagePreview.tsx # Discord message chat container & preview dispatcher
    │   │   ├── ComponentPreview.tsx # Switch dispatcher for V2 components
    │   │   ├── ContainerPreview.tsx # Discord Container card with accent bar
    │   │   ├── EmbedPreview.tsx   # Discord embed renderer with inline field grids
    │   │   ├── ActionRowPreview.tsx # Interactive button & select previews
    │   │   └── Markdown.tsx       # Markdown parser with syntax highlighting
    │   ├── actions/
    │   │   ├── FlowBuilder.tsx   # Root action flow wrapper
    │   │   └── StepList.tsx      # Step chain builder, conditional branching & modal inputs
    │   ├── send/
    │   │   └── BotDispatchModal.tsx # Multi-channel dispatch & message edit modal
    │   └── ui/
    │       ├── Button.tsx, Modal.tsx, Field.tsx, ColorPicker.tsx, Tabs.tsx, icon.ts
    ├── store/
    │   ├── messageStore.ts    # Zustand: message data, mode, selection, embeds, components
    │   ├── actionStore.ts     # Zustand: interactive custom_id flows & registrations
    │   ├── profileStore.ts    # Zustand: webhook URLs and bot profiles
    │   ├── settingsStore.ts   # Zustand: local client settings (theme, display)
    │   └── templateStore.ts   # Zustand: server-saved templates CRUD
    ├── hooks/
    │   ├── useMessage.ts, useSend.ts, useStaffAccess.ts, useTemplates.ts
    └── utils/
        ├── componentsV2.ts, constants.ts, discord.ts, exportImport.ts, tree.ts
```

### 1.2 Tooling & Dependencies
- **Build Engine**: Vite 8.3.1 (`vite.config.ts:16-39`) configured with `@` aliasing to `src/` and `@dmb/shared` mapped directly to `../shared/src/index.ts` for instant HMR. Proxies `/api` requests to `http://localhost:3001`.
- **CSS Engine**: TailwindCSS v4 with `@tailwindcss/vite` (`package.json:32`).
- **TypeScript**: TypeScript 5.9.3 configured with strict type checking. Typecheck passes cleanly with 0 errors (`npm run typecheck`).
- **Unit Testing**: Vitest 3.2.7. Currently 46 tests across 6 test suites pass (`npm test`).
- **State Management**: Zustand 5.0.15 with `persist` middleware in `messageStore.ts` and `actionStore.ts`.

---

## 2. Layout & UX Architecture: Hoho Manager vs Discohook.app

### 2.1 Current Hoho Manager Layout Flaws
The current layout (`App.tsx:452-678`) does not follow Discohook's 3-pane paradigm:
1. **Header Overload**: `Header.tsx:113-230` contains brand, duplicate mode toggles, template naming/save/load, JSON export/import buttons, start over button, Staff Access / Staff Login button, and Docs link.
2. **2-Pane Restriction**: `App.tsx:482` wraps everything inside a single `SplitPane` with `left` and `right`.
   - **Left Pane**: Contains the Action Bar (Share, Backups, Clear, Bot dispatch split button, Webhook input + Send button), another Mode Toggle bar ("Editor Mode: Classic / Components V2"), and a stack of Accordions ("Message 1", "Components", "Profile Override").
   - **Right Pane**: Contains `MessagePreview.tsx`.
3. **Orphaned Layout Code**:
   - `Sidebar.tsx`: Built with a tab navigation rail (Build, Send, Profs, Docs) but never rendered in `App.tsx`.
   - `PropertyPanel.tsx`: Built as a 320px right-side property drawer, but `App.tsx:669` instead uses `ComponentEditorModal.tsx` floating modals.
   - `DiscohookComponentsEditor.tsx`: Built to visually render action rows and buttons like Discohook, but completely unimported.

### 2.2 Discohook Reference Architecture (`discohook_src`)
Examining Discohook's official implementation:
- **Left Navigation Rail & Drawer** (`Header.tsx:102-299`, `tabs.tsx:10-72`):
  - Guild avatar list along a vertical rail (`Header.tsx:157-217`) allowing one-click server switching.
  - Quick drawers for Backups, Share Links, Guides, and Settings.
  - Tree/palette navigation for structural building.
- **Center Editor Workspace** (`routes/_index.tsx:959-1609`):
  - Sticky/top action toolbar: Targets (webhooks/bot), Share, Backups, Reset Editor (`_index.tsx:1008-1273`).
  - Message Accordions: Message 1 content, Embeds, and inline Action Rows.
  - Dedicated action row builder where buttons are displayed inline inside the message layout.
- **Right Live Preview** (`routes/_index.tsx:1610-1654`, `Message.client.tsx:97-430`):
  - Real-time rendering of the full message draft.
  - Automatically loads profile pictures from the webhook or application target.
  - Interactive element clicking (clicking a button or embed in preview directly selects or edits it).

### 2.3 Proposed Hoho Manager 3-Pane Architecture
To clone Discohook faithfully without ripping out working functionality:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                            TOP HEADER                                            │
│  [Logo] Hoho Manager  |  [Server Dropdown] Selected Server  |  Template: [Title] [Save]  | Settings│
├────────────────────┬────────────────────────────────────────────┬────────────────────────────────┤
│   PANE 1: SIDEBAR  │               PANE 2: EDITOR               │         PANE 3: PREVIEW        │
│    (Width: ~260px) │              (Width: Flexible)             │       (Width: Resizable / 50%) │
├────────────────────┼────────────────────────────────────────────┼────────────────────────────────┤
│ • Guild Context    │ • Action Bar:                              │ • Top Bar:                     │
│   - Icon + Name    │   - Share / Backups / Clear                │   - "Preview" Live Tag         │
│   - Quick Switcher │   - Webhook URL & Direct Send              │   - Target Bot Identity badge  │
│                    │   - Bot Dispatch Modal Trigger             │ • Discord Message Chrome:      │
│ • Component Tools: │                                            │   - Bot Avatar (Live Fetched)  │
│   - Palette (V2)   │ • Message Editor Accordion:                │   - Bot Username + "APP" badge │
│   - Hierarchy /    │   - Message Text & Formatting              │   - Timestamp                  │
│     Layers Tree    │   - Author/Avatar Overrides (Optional)     │ • Unified Message Content:     │
│                    │                                            │   - Text Markdown              │
│ • Quick Actions:   │ • Components & Action Rows Accordion:      │   - Discord Embeds             │
│   - Raw JSON       │   - Integrated DiscohookComponentsEditor   │   - V2 Containers & Sections   │
│   - Import/Export  │   - Visual button pills & row controls     │   - Action Rows & Buttons      │
│   - Backups Modal  │                                            │ • Interactive Click:           │
│                    │ • Embeds Accordion:                        │   - Clicking a button/embed    │
│                    │   - Embed Cards & Field Builder            │     selects it for editing     │
└────────────────────┴────────────────────────────────────────────┴────────────────────────────────┘
```

### 2.4 Consolidation of Duplicate UI Elements
| Duplicate Element | Location 1 | Location 2 | Resolution Plan |
|---|---|---|---|
| **Editor Mode Toggle** | `Header.tsx:22-48` (rendered at `:122`) | `App.tsx:587-616` ("Editor Mode Bar") | Remove the floating bar in `App.tsx:587-616`. Keep the clean pill toggle in `Header.tsx` or place it neatly inside the Message Editor header. |
| **Component Palette & Layers** | `MessageEditor.tsx:97-109` | `App.tsx:624-649` & `Sidebar.tsx:50-57` | Remove the inline duplication from `MessageEditor.tsx` and `App.tsx`. Place Palette & Layers into Pane 1 (Left Sidebar) where users expect a persistent tree and tool palette. |
| **Profile Override / Management** | `App.tsx:651-653` (Accordion) | `Sidebar.tsx:73-75` (Profs Tab) | Remove `ProfilesPanel` from the main message builder entirely. Relocate to the dedicated Settings modal (accessible via Header Settings button per R3). |
| **Duplicate Previews / Mode Filtering** | `MessagePreview.tsx:84-108` (Hides content/embeds if `isV2`) | N/A | Refactor `MessagePreview.tsx` to unify content: always render markdown content and embeds if present, followed by components. |

---

## 3. Preview Engine & Visual Fidelity

### 3.1 Live Bot Profile Picture Loading
**Observation**:
In `MessagePreview.tsx:61-69`:
```tsx
<div className="h-10 w-10 shrink-0 overflow-hidden rounded-full bg-blurple">
  {data.avatar_url ? (
    <img src={data.avatar_url} alt="" className="h-full w-full object-cover" />
  ) : (
    <span className="flex h-full w-full items-center justify-center">
      <Bot size={18} className="text-white" />
    </span>
  )}
</div>
```
When `data.avatar_url` is not set by the user, the preview displays a generic Lucide bot icon.
Meanwhile, `BotDispatchModal.tsx:98-124` contains a `syncBotIdentity` routine that queries `/api/send/identity` and caches `{ name, avatar }` in `localStorage.bot_identity_cache`. However, this cached info is isolated to that modal and never consumed by `MessagePreview.tsx`.

**Resolution Logic**:
1. Implement an automatic fetch on application startup in a new or extended `profileStore.ts` / `botIdentityStore.ts`:
   - On load, automatically call `GET /api/send/identity`.
   - Store `botIdentity: { name: string; avatar: string } | null`.
2. Update `MessagePreview.tsx`:
   - Avatar source precedence: `data.avatar_url` (user override) -> `botIdentity.avatar` (live bot avatar) -> fallback Discord default avatar (`https://cdn.discordapp.com/embed/avatars/0.png`).
   - Username source precedence: `data.username` (user override) -> `botIdentity.name` (live bot username) -> `"Discohook"`.
   - Add native Discord verified/APP badges mimicking `Message.client.tsx:64-95` in Discohook.
3. Remove the manual "Sync Cache" button from `BotDispatchModal.tsx:301-306`.

### 3.2 Unified Preview Handling (Classic vs Components V2)
**Observation**:
In `MessagePreview.tsx:84-108`:
- When `!isV2`: renders `payload.content`, `data.embeds`, and only `ActionRow` components.
- When `isV2`: renders ONLY `data.components`. Content text and embeds are suppressed!
This causes jarring UX: if a user writes content in Classic and switches to V2 to add a button or container, their text and embeds disappear from the preview.

**Resolution Logic**:
1. Discord allows message content in both modes (in fact, V2 messages can still carry top-level content or TextDisplays).
2. The preview should render:
   - Top-level text content (if `data.content` exists).
   - Embeds (if `data.embeds` exist).
   - Components (Containers, Sections, Separators, Action Rows, Media Galleries).
3. If mode is V2, display the `flags: 32768 (IsComponentsV2)` pill at the bottom as currently implemented.

---

## 4. Modal and Action Row Building UX

### 4.1 Action Row Usability Friction & Solution
**The Current Friction**:
1. In `ComponentForms.tsx:159-196`, selecting an Action Row in `LayersPanel` opens a modal containing only two buttons: `Add Button` and `Add Select`.
2. Clicking `Add Button` creates a child button `{ _id, type: Button, config: {} }`, but the modal provides zero fields to edit the button's label, style, or custom ID.
3. To edit the newly added button, the user must close the modal, locate the child in `LayersPanel`, and click it to open another modal.
4. Users cannot see what buttons are in the row, cannot reorder them horizontally, and cannot preview button colors without looking across to the right preview pane.

**The Solution: Integrating `DiscohookComponentsEditor.tsx`**:
- `DiscohookComponentsEditor.tsx` (`hoho_manager/client/src/components/editor/DiscohookComponentsEditor.tsx`, lines 1-228) is an already-built visual Action Row builder:
  - Renders each Action Row as a card (`Action Row #1 - 3/5 items`).
  - Renders buttons horizontally with exact Discord style color pills (Primary `#5865f2`, Secondary `#4e5058`, Success `#23a55a`, Danger `#da373c`, Link with external link icon).
  - Clicking any button pill directly selects it (`select({ kind: "component", id: child._id })`), opening its property/action modal.
  - Each button pill has an inline hover delete button (`Trash2`).
  - Row header has `Move Up`, `Move Down`, `Duplicate Row`, and `Delete Row` buttons.
  - Bottom bar has direct `+ Add Button` and `+ Add Select Menu` buttons with limit checking (max 5 buttons, max 1 select).
- **Action**: Mount `DiscohookComponentsEditor` directly inside the Center Editor workspace under a dedicated "Action Rows & Components" accordion.

### 4.2 Modal Building UX
**Observation**:
- In `StepList.tsx:190-325`, `open_modal` steps allow configuring modal title, custom ID, and up to 5 TextInputs with Short/Paragraph styles, placeholders, and required flags.
- Action chaining after modal submission is already handled by `BranchEditor` ("When Modal is Submitted (Then)").
- UX Enhancement: Provide a "Preview Modal" trigger button that renders a mock Discord modal dialog on screen, allowing users to visually verify their form inputs before deploying to Discord.

---

## 5. Global Context & API Fetching

### 5.1 Global "Selected Server (Guild)" Dropdown
**Current State**:
- In `hoho_manager/server/src/routes/send.ts:151`:
  ```ts
  const [guild] = await discord.getBotGuilds(profileId);
  if (!guild) return res.json([]);
  const channels = await discord.getGuildChannels(guild.id, profileId);
  ```
  The backend unconditionally fetches only the bot's *first* guild!
- There is no UI to select or switch servers.

**Requirements (R2)**:
- Implement a global "Selected Server (Guild)" dropdown in the Header and Sidebar.
- Changing the selected server updates the context for all channel, role, and member dropdowns.

**Architecture & Implementation**:
1. **Backend Route**:
   Add `GET /api/guilds` (or `/api/send/guilds`):
   ```ts
   router.get("/guilds", attachUser, asyncHandler(async (req, res) => {
     const profileId = parseProfileId(req.query.profileId);
     const guilds = await discord.getBotGuilds(profileId);
     res.json(guilds.map((g) => ({
       id: g.id,
       name: g.name,
       icon: g.icon ? `https://cdn.discordapp.com/icons/${g.id}/${g.icon}.png` : null,
     })));
   }));
   ```
2. **Frontend Store (`guildStore.ts`)**:
   Create a dedicated Zustand store:
   ```ts
   interface GuildState {
     selectedGuildId: string | null;
     guilds: Array<{ id: string; name: string; icon: string | null }>;
     channels: Record<string, Array<{ id: string; name: string; type: number }>>;
     roles: Record<string, Array<{ id: string; name: string; color: number; position: number }>>;
     members: Record<string, Array<{ id: string; username: string; displayName: string; avatar: string | null }>>;
     setSelectedGuildId: (guildId: string | null) => void;
     fetchGuilds: () => Promise<void>;
     fetchChannels: (guildId: string) => Promise<void>;
     fetchRoles: (guildId: string) => Promise<void>;
     searchMembers: (guildId: string, query: string) => Promise<void>;
   }
   ```
3. **Client-Side Caching**:
   Cache fetched channel/role/member arrays in the Zustand store per `guildId`. Do NOT persist entity caches to the backend SQLite DB (fulfills requirement R2: *"Do not cache this Discord entity data on the server; fetch it live or use client-side caching to minimize backend footprint"*).

### 5.2 Dynamic Searchable API Dropdowns (with Manual ID Fallback)
Create a reusable component: `SearchableDiscordSelect.tsx`:
- **Props**:
  - `type`: `"channel" | "role" | "user"`
  - `guildId`: string (selected guild)
  - `value`: string (ID or comma-separated IDs)
  - `onChange`: (value: string) => void
  - `multiple`: boolean (for allowed channels / allowed role mentions)
  - `allowManualInput`: boolean (default `true`)
  - `placeholder`: string
- **Behavior**:
  - Combobox input where the user can type to filter fetched options.
  - If the user types or pastes a raw snowflake (`^\d{17,20}$`), it accepts the raw snowflake ID directly.
  - Option items render with Discord icons:
    - Channels: `#` (text), speaker (voice), announcement icon, forum icon.
    - Roles: Role shield with role color (`decimalToHex(role.color)`).
    - Members: User avatar image or default Discord avatar with username and snowflake.
- **Integration Points**:
  - `BotDispatchModal.tsx`: Target channels selector.
  - `AccessPanel.tsx`:
    - `allowed_channel_ids`: Replace raw text input with `SearchableDiscordSelect` (type="channel", multiple=true).
    - `allowed_role_mention_ids`: Replace raw text input with `SearchableDiscordSelect` (type="role", multiple=true).
    - `discord_user_id`: Replace raw text input with `SearchableDiscordSelect` (type="user", allowManualInput=true).
  - `StepList.tsx`:
    - `add_role`, `remove_role`, `toggle_role`: Replace `roleId` text input with `SearchableDiscordSelect` (type="role").
    - `send_message`: Replace `channelId` text input with `SearchableDiscordSelect` (type="channel").

---

## 6. Staff Access Panel Audit & Critical Bugs

### 6.1 The Modal Lockup Bug
**Observations & Line References**:
1. In `hoho_manager/client/src/components/layout/Header.tsx:263-272`:
   ```tsx
   {/* Staff Access Modal */}
   <Modal
     open={accessOpen}
     onClose={() => setAccessOpen(false)}
     title=""
     width="max-w-4xl"
   >
     <div className="h-[70vh]">
       {accessOpen && <AccessPanel />}
     </div>
   </Modal>
   ```
   Notice that `title=""` (empty string) is passed.
2. In `hoho_manager/client/src/components/ui/Modal.tsx:43-57`:
   ```tsx
   {title && (
     <div className="flex items-center justify-between px-5 py-4 border-b border-[#1e1f22] bg-[#2b2d31] shrink-0">
       <h2 className="text-[14px] font-bold text-white uppercase tracking-wider">
         {title}
       </h2>
       <button
         type="button"
         onClick={onClose}
         className="text-[#b5bac1] hover:text-white transition-colors"
         aria-label="Close"
       >
         <X size={18} />
       </button>
     </div>
   )}
   ```
   Because `title` is `""` (falsy), the entire header `div` is NOT rendered. Thus, the close `X` button is completely omitted.
3. In `hoho_manager/client/src/components/ui/Modal.tsx:37`:
   ```tsx
   <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in duration-150">
   ```
   The backdrop container does NOT have an `onClick` handler. Clicking outside the modal dialog does nothing.
4. In `hoho_manager/client/src/components/layout/AccessPanel.tsx:73-86`:
   `AccessPanel` has its own internal header ("Staff Access Management"), but does NOT accept an `onClose` prop and does NOT provide a close button.

**Consequence**: Once the Staff Access panel is opened, the user is completely trapped inside the modal. The only way out is refreshing the browser window.

**Fix**:
1. In `Modal.tsx`:
   - Add backdrop click-to-close:
     ```tsx
     <div 
       className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 ..."
       onClick={(e) => {
         if (e.target === e.currentTarget) onClose();
       }}
     >
       <div 
         className={`w-full ${width} ...`}
         onClick={(e) => e.stopPropagation()}
         role="dialog"
       >
     ```
   - Always render the close button in `Modal.tsx` even if `title` is not provided (or position an absolute close button in the top-right corner).
2. In `Header.tsx`: Pass `title="Staff Access Management"` (or pass an explicit `onClose` to `AccessPanel`).
3. In `AccessPanel.tsx`: Accept an optional `onClose?: () => void` prop and render an explicit `<Button variant="secondary" onClick={onClose}>Close</Button>` or `X` icon in its header.

### 6.2 Advanced Staff Permissions Enhancements
Per requirement R4:
1. **Search Member by Name**: In `AccessPanel.tsx:98-111`, replace the static snowflake input with `SearchableDiscordSelect` (type="user") that searches Discord guild members by username/display name while storing `discord_user_id` as the primary key.
2. **Channel & Role Allowlist Dropdowns**: Replace comma-separated text fields at lines 158-164 (`allowed_role_mention_ids`) and 181-187 (`allowed_channel_ids`) with searchable multiselect dropdowns populated from the active guild fetch.
3. **Granular Action Cooldowns**: Add per-action cooldown overrides in the form (e.g., separate cooldowns for `send` vs `edit` vs `delete`).

---

## 7. Settings Page & Hardcoded `.env` Migration

### 7.1 Hardcoded Configuration Identification
Currently in `hoho_manager/server/src/config/env.ts`:
- Line 72: `logChannelId: str("LOG_CHANNEL_ID")`
- Line 74: `ownerDiscordIds: (str("OWNER_DISCORD_IDS", "") ?? "").split(",")`
Currently in `hoho_manager/server/src/services/auditLog.ts:48`:
- `const channelId = env.logChannelId;`
Currently in `hoho_manager/server/src/middleware/staffPermissions.ts:33`:
- Checks `env.ownerDiscordIds.includes(staffId)`.

### 7.2 Database Settings Table (Migration `005_settings`)
Create a new migration in `hoho_manager/server/src/config/migrations.ts`:
```sql
CREATE TABLE IF NOT EXISTS settings (
  key         TEXT NOT NULL,
  guild_id    TEXT NOT NULL DEFAULT 'global',
  value       TEXT NOT NULL,
  updated_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (key, guild_id)
);

CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);
```
Default keys:
- `log_channel_id` (fallback to `env.logChannelId`)
- `head_admin_ids` (JSON array, fallback to `env.ownerDiscordIds`)
- `default_guild_id`

### 7.3 Settings Modal & Bot Profile Relocation (R3)
1. **Settings Modal (`SettingsModal.tsx`)**:
   - Accessible via "Settings" button in Header (matching Discohook's `Header.tsx:360`).
   - Accessible to Head Admins (users with `ADMIN_API_KEY` or user ID in `head_admin_ids`).
   - Tabs:
     - **General / Appearance**: Theme, Compact Avatars, Message Display (Cozy/Compact).
     - **Bot Profiles**: Move `ProfilesPanel.tsx` here.
     - **Webhook Profiles**: Manage saved webhooks.
     - **Audit & Admin (Head Admin Only)**:
       - Audit Log Channel ID (with live searchable channel dropdown).
       - Head Admin Discord User IDs (with member search dropdown).
2. **Backend Settings Endpoints**:
   - `GET /api/settings`: Returns configured settings (redacting secrets).
   - `PUT /api/settings`: Updates database settings (requires admin key or head admin check).
   - Update `auditLog.ts` to query `settingsRepository.get('log_channel_id', guildId)` before falling back to `env.logChannelId`.

---

## 8. Exact Files & Line Numbers Modification Plan

| File Path | Action | Key Lines | Description of Changes |
|---|---|---|---|
| `client/src/App.tsx` | MODIFY | 481-678 | Re-layout into Discohook 3-pane structure (`Sidebar`, `MessageEditor` + `DiscohookComponentsEditor`, unified `MessagePreview`). Remove duplicate mode toggle (lines 587-616). Remove Accordion `ProfilesPanel` (lines 651-653). |
| `client/src/components/layout/Header.tsx` | MODIFY | 113-230, 263-272 | Add global "Selected Server" dropdown. Add "Settings" button. Fix Staff Access Modal invocation (`title="Staff Access Management"`). Remove duplicate mode toggle if consolidating into editor. |
| `client/src/components/layout/Sidebar.tsx` | REFACTOR | 1-81 | Revamp from orphaned tab rail into Discohook Left Pane: Guild selector, quick navigation (Templates, Backups, Share), Component Palette, Layers hierarchy. |
| `client/src/components/editor/DiscohookComponentsEditor.tsx` | INTEGRATE | 1-228 | Wire into the Center Editor as the primary Action Rows & Buttons builder with horizontal button pills and visual styles. |
| `client/src/components/editor/MessageEditor.tsx` | MODIFY | 97-109 | Remove duplicate inline Component Palette and LayersPanel to prevent UI redundancy. |
| `client/src/components/preview/MessagePreview.tsx` | MODIFY | 60-118 | Automatically use live bot identity avatar & name in preview. Unify rendering so content/embeds are never hidden when switching between Classic and V2. Support interactive click-to-select. |
| `client/src/components/ui/Modal.tsx` | MODIFY | 36-60 | Add `onClick={onClose}` to backdrop overlay. Add `e.stopPropagation()` to dialog content. Ensure close button is always accessible. |
| `client/src/components/layout/AccessPanel.tsx` | MODIFY | 73-86, 98-187 | Add close button to header. Replace manual User ID with member search. Replace manual channel IDs and role IDs with `SearchableDiscordSelect`. |
| `client/src/components/ui/SearchableDiscordSelect.tsx` | CREATE | New | Searchable combobox for Discord channels, roles, and members with live API fetch, client-side caching, and raw snowflake fallback. |
| `client/src/components/layout/SettingsModal.tsx` | CREATE | New | Dedicated Head Admin settings modal consolidating Bot Profiles, Webhooks, `LOG_CHANNEL_ID`, and Admin IDs. |
| `client/src/store/guildStore.ts` | CREATE | New | Global Zustand store for selected server context, guilds list, and client-cached channels, roles, and members. |
| `client/src/store/profileStore.ts` | MODIFY | 1-100 | Add auto-fetching of active bot identity on load. Expose `botIdentity` to `MessagePreview`. Remove manual "Sync Cache" requirement. |
| `server/src/config/migrations.ts` | MODIFY | 170-178 | Add migration `005_settings` for key-value settings table with optional `guild_id`. |
| `server/src/repositories/settingsRepository.ts` | CREATE | New | Database repository for get/set/list settings. |
| `server/src/routes/settings.ts` | CREATE | New | Express route `GET /api/settings`, `PUT /api/settings` for Head Admins. |
| `server/src/routes/send.ts` | MODIFY | 149-175 | Add `guildId` query parameter to `/api/send/channels`. Add `GET /api/send/guilds`, `GET /api/send/guilds/:guildId/roles`, `GET /api/send/guilds/:guildId/members`. |
| `server/src/services/discordService.ts` | MODIFY | 299-350 | Implement `getGuildRoles(guildId, profileId)` and `searchGuildMembers(guildId, query, profileId)`. |
| `server/src/services/auditLog.ts` | MODIFY | 45-65 | Query database settings for `log_channel_id` before falling back to `env.logChannelId`. |
| `server/src/utils/mentionScrubber.ts` | AUDIT | 20-98 | Verify mention scrubber enforces regex, role ID, and payload protection across all paths. |

---

## 9. Verification & Integrity Checklist

- [x] All existing 46 Vitest unit tests pass (`npm test` in `hoho_manager/client`).
- [x] TypeScript compiler succeeds with 0 errors (`npm run typecheck` in `hoho_manager/client`).
- [x] Live web server at `http://localhost:5175/` verified responsive.
- [x] Backend API at `http://localhost:3001/` verified healthy (`/api/health` reports status `ok`).
- [x] Reference code in `discohook_src` verified against proposed styling and architecture.
- [x] Every file path, line number, interface, and bug root cause documented with concrete evidence.
