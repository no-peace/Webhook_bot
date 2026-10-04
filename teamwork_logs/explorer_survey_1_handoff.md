# Handoff Report: Frontend & Discohook Layout Survey

**Agent**: `explorer_survey_1` (Frontend Architect Explorer)  
**Parent / Recipient**: `9905eadb-ba91-4495-92f1-aa467294c8a6`  
**Date**: 2026-10-03  
**Status**: Task Complete (Hard Handoff)  
**Deliverable Document**: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_survey_1\report.md`

---

## 1. Observation

1. **Current Layout & Panes**:
   - In `hoho_manager/client/src/App.tsx:482-667`, the entire main area is wrapped in a 2-pane `<SplitPane initialRatio={0.5} left={...} right={<MessagePreview />} />`.
   - `hoho_manager/client/src/components/layout/Sidebar.tsx:1-81` is completely orphaned and never imported or rendered anywhere in the application.
   - `hoho_manager/client/src/components/editor/PropertyPanel.tsx:1-130` is also orphaned and never imported.

2. **Duplicate UI Elements**:
   - "Editor Mode" toggles are duplicated in two adjacent locations:
     - `hoho_manager/client/src/components/layout/Header.tsx:22-48` (`ModeToggle`, rendered at line 122).
     - `hoho_manager/client/src/App.tsx:587-616` ("Editor Mode Bar" with Classic and Components V2 buttons).
   - Component Palette and Layers Panel are duplicated across three locations:
     - `hoho_manager/client/src/components/editor/MessageEditor.tsx:97-109` (renders `<ComponentPalette />` and `<LayersPanel />` inside "Message 1" when in V2 mode).
     - `hoho_manager/client/src/App.tsx:624-649` (renders an Accordion containing `<ComponentPalette />` and `<LayersPanel />`).
     - `hoho_manager/client/src/components/layout/Sidebar.tsx:50-57` (renders `<ComponentPalette />` and `<LayersPanel />` in the Build tab).
   - `ProfilesPanel.tsx` is mounted in an Accordion inside the main editor (`App.tsx:651-653`) and in `Sidebar.tsx:73-75`.

3. **Preview Engine Shortcomings & Bot Avatar**:
   - In `hoho_manager/client/src/components/preview/MessagePreview.tsx:61-69`:
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
     The avatar only loads if `data.avatar_url` is manually typed. If empty, it unconditionally renders a generic `<Bot>` icon.
   - In `hoho_manager/client/src/components/preview/MessagePreview.tsx:84-108`:
     When `mode === 'v2'`, `payload.content` and `data.embeds` are suppressed. When `mode !== 'v2'`, non-ActionRow components are suppressed.

4. **Action Row & Modal UX Friction**:
   - In `hoho_manager/client/src/components/editor/ComponentForms.tsx:159-196`, `ActionRowForm` only provides `Add Button` and `Add Select` buttons, giving users no inline way to see, style, or reorder child buttons.
   - In `hoho_manager/client/src/components/editor/DiscohookComponentsEditor.tsx:1-228`, a fully formed, Discohook-style visual Action Row builder with horizontal button pills, style badges (`bg-[#5865f2]`, `bg-[#4e5058]`, etc.), drag/reorder, and delete controls exists, but is NOT imported or used anywhere.

5. **Staff Access Modal Lockup Bug**:
   - In `hoho_manager/client/src/components/layout/Header.tsx:263-272`:
     ```tsx
     <Modal open={accessOpen} onClose={() => setAccessOpen(false)} title="" width="max-w-4xl">
       <div className="h-[70vh]">{accessOpen && <AccessPanel />}</div>
     </Modal>
     ```
     `title` is passed as `""` (empty string).
   - In `hoho_manager/client/src/components/ui/Modal.tsx:43`:
     `{title && (<div className="flex items-center justify-between ..."><button onClick={onClose} ...><X size={18} /></button></div>)}`
     Because `title` is falsy, the header and close button are never rendered.
   - In `hoho_manager/client/src/components/ui/Modal.tsx:37`:
     `<div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in duration-150">`
     The backdrop has no `onClick` handler. Clicking outside does not close the modal.
   - `hoho_manager/client/src/components/layout/AccessPanel.tsx:73-86` has no close button of its own.

6. **Static ID Inputs & Missing Server Context**:
   - `server/src/routes/send.ts:151` unconditionally fetches channels from the first guild: `const [guild] = await discord.getBotGuilds(profileId)`. There is no endpoint for `/api/guilds`, `/api/guilds/:id/roles`, or `/api/guilds/:id/members`.
   - In `client/src/components/layout/AccessPanel.tsx:98-187`, `discord_user_id`, `allowed_role_mention_ids`, and `allowed_channel_ids` are plain text inputs requiring manual snowflake copying.
   - In `client/src/components/actions/StepList.tsx:24-32`, action steps (`add_role`, `remove_role`, `toggle_role`, `send_message`) use static ID text inputs.

7. **Hardcoded Configurations in Code**:
   - `server/src/config/env.ts:72` hardcodes `logChannelId: str("LOG_CHANNEL_ID")`.
   - `server/src/config/env.ts:74` hardcodes `ownerDiscordIds: (str("OWNER_DISCORD_IDS", "") ?? "").split(",")`.
   - There is no database `settings` table in `server/src/config/migrations.ts:18-177`.

8. **Live Verification**:
   - Live URL `http://localhost:5175/` verified responding with the Vite application.
   - Backend API `/api/health` responded: `{"status":"ok","environment":"development","uptimeSeconds":3358,"database":{"connected":true,"users":1},"discord":{"publicKeyConfigured":true,"botTokenConfigured":true,"applicationIdConfigured":true}}`.
   - Client tests run and pass: `npm test` passed 46 tests across 6 files.
   - Client typecheck: `npm run typecheck` passed with 0 errors.

---

## 2. Logic Chain

1. **Layout Synthesis**:
   - *Observation 1* shows the app is restricted to a 2-pane split with orphaned files (`Sidebar.tsx`, `PropertyPanel.tsx`).
   - *Discohook Reference* (`discohook_src/packages/site/app/routes/_index.tsx:959-1654`) operates with a 3-pane structure: Left Sidebar (navigation, guild rail, component layers/palette), Center Editor (message content, embeds, inline action rows), Right Live Preview (Discord-fidelity message rendering).
   - *Inference*: Rebuilding `Sidebar.tsx` into Pane 1, keeping `MessageEditor` + `DiscohookComponentsEditor` in Pane 2, and `MessagePreview` in Pane 3 creates the exact 3-pane Discohook layout without breaking existing React code.

2. **Deduplication Logic**:
   - *Observation 2* demonstrates that users currently see two sets of Editor Mode buttons side-by-side and duplicate component trees.
   - *Inference*: Removing the Editor Mode bar from `App.tsx:587-616` and consolidating the Component Palette and Layers into Pane 1 (Left Sidebar) removes visual clutter and establishes clear component ownership.

3. **Bot Avatar & Preview Logic**:
   - *Observation 3* shows `MessagePreview.tsx:63` only checks `data.avatar_url`.
   - *Inference*: Automatically calling `/api/send/identity` on load and storing the bot's username and avatar in a store allows `MessagePreview` to fallback to the bot's profile picture when `data.avatar_url` is empty, perfectly matching Discord's native rendering and fulfilling Acceptance Criteria R1 & R2.

4. **Action Row UX Logic**:
   - *Observation 4* shows `ActionRowForm` is barely functional, whereas `DiscohookComponentsEditor.tsx` is completely built and matches Discohook.
   - *Inference*: Integrating `DiscohookComponentsEditor.tsx` directly into the Center Editor solves Action Row nesting and editing immediately with zero new form UI needed.

5. **Staff Access Modal Fix**:
   - *Observation 5* proves why the modal is completely unclosable (`title=""` prevents header from rendering, and backdrop has no click handler).
   - *Inference*: Adding `onClick={onClose}` to the backdrop in `Modal.tsx:37`, guaranteeing a close button regardless of `title`, and adding an explicit close button to `AccessPanel.tsx` eliminates the lockup.

6. **Dynamic Discord Entity Fetching**:
   - *Observation 6* reveals hardcoded single-guild channel fetching and manual ID text fields.
   - *Inference*: Adding backend routes for guilds, roles, and members, creating a `SearchableDiscordSelect` component with client-side caching and manual snowflake fallback, and adding a global Guild dropdown fulfills R2 and R4.

7. **Settings Migration Logic**:
   - *Observation 7* shows `LOG_CHANNEL_ID` and `OWNER_DISCORD_IDS` are hardcoded in `.env`.
   - *Inference*: Creating migration `005_settings`, a `settingsRepository`, and a dedicated Head Admin Settings modal allows managing bot profiles and system configs from the UI rather than restarting servers.

---

## 3. Caveats

1. **Discord Guild Rate Limits**: Discord limits fetching guild members on large servers without the `Server Members Intent` or using `/guilds/{id}/members/search?query=...&limit=20`. Member search should always be debounced and use the search endpoint rather than requesting all members.
2. **Client-Side vs Backend Caching**: The user specification explicitly mandated: *"Do not cache this Discord entity data on the server; fetch it live or use client-side caching to minimize backend footprint"*. Caching must remain inside the client Zustand store / sessionStorage.
3. **Admin vs Staff Context**: Non-admins use `x-staff-id` while admins use `x-admin-key`. The Settings modal must restrict configuration editing (`LOG_CHANNEL_ID`, admin IDs) to authorized Head Admins only.

---

## 4. Conclusion

The existing codebase is structurally sound and ready for the Discohook refactor. Rather than rewriting the app, the required changes consist of:
1. Adapting `App.tsx` and `Sidebar.tsx` into Discohook's 3-pane structure.
2. Eliminating duplicate mode toggles and palette components.
3. Wiring up the already-written `DiscohookComponentsEditor.tsx` into the editor.
4. Patching `Modal.tsx` and `Header.tsx` to fix the critical Staff Access lockup bug.
5. Auto-fetching bot identity on startup so the Live Preview renders the real bot avatar.
6. Adding the global Guild dropdown and `SearchableDiscordSelect` comboboxes across the app and Staff Panel.
7. Migrating bot profile management and `.env` settings into a database-backed Settings modal.

All exact files, line numbers, interfaces, and architecture diagrams have been fully authored in `report.md`.

---

## 5. Verification Method

To verify these findings and the eventual implementation:
1. **Automated Client Tests**:
   ```bash
   cd hoho_manager/client && npm test
   ```
   Ensures all 46 existing Vitest tests continue to pass.
2. **TypeScript Compilation**:
   ```bash
   cd hoho_manager/client && npm run typecheck
   ```
   Must complete with code 0 and zero TypeScript errors.
3. **Live UI Inspection**:
   - Open `http://localhost:5175/`.
   - Verify Left Sidebar contains Guild context, Component Palette, and Layers.
   - Verify Center Editor contains Message body, Action Rows (with visual button pills), and Embeds.
   - Verify Right Preview displays the live bot avatar fetched from `/api/send/identity`.
   - Open Staff Access panel: click outside on the backdrop or click "Close" to confirm it closes without refreshing.
