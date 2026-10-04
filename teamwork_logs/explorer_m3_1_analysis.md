# Milestone 3 Architecture & Layout Analysis: Discohook 3-Pane Structure

## 1. Executive Summary

Milestone 3 requires refactoring the Hoho Manager frontend (`hoho_manager/client/`) to match the **Discohook.app 3-pane architecture** (Left Sidebar, Center Editor, Right Live Preview), eliminate duplicate UI elements, integrate `DiscohookComponentsEditor` for visual Action Rows, and provide live bot avatar rendering in the preview.

### Core Discoveries
1. **Existing Panes**: `App.tsx` currently renders only **2 panes** inside a single `SplitPane` (Editor on left, Live Preview on right). The component `Sidebar.tsx` was written previously but is **completely omitted and unmounted** in `App.tsx`.
2. **Duplicate Component Palettes & Layers**: `ComponentPalette` and `LayersPanel` are duplicated across **three separate files**:
   - `Sidebar.tsx` (lines 52, 55)
   - `App.tsx` (lines 656, 663) in an accordion
   - `MessageEditor.tsx` (lines 104, 106) embedded directly inside the message body
3. **Orphaned Component**: `DiscohookComponentsEditor.tsx` was created to provide a rich visual Action Row builder (row reordering, 5 items per row limit, style badges, link buttons, select menus), but is **unreferenced anywhere in the codebase**.
4. **Duplicate Mode Toggles**: The "Editor Mode" (Classic vs Components V2) toggle exists simultaneously in `Header.tsx` (lines 26-52) AND in `App.tsx` (lines 604-632), creating redundant UI clutter.
5. **Bot Avatar in Preview**: `App.tsx` (lines 406-420) auto-fetches bot identity on load and writes to `localStorage.getItem("bot_identity_cache")`, but `MessagePreview.tsx` ignores it, falling back to a static generic `<Bot />` icon instead of rendering the live bot profile picture.
6. **Outdated Sidebar Elements**: `Sidebar.tsx` contains an outdated `ProfilesPanel` tab (violating Milestone 2 / R3, which consolidated profile management into `SettingsModal.tsx`) and light-mode styles (`bg-white dark:bg-gray-900`) discordant with the Discord dark theme.

---

## 2. Current vs. Target Layout Architecture

### Current Layout (`App.tsx`)
```
+-------------------------------------------------------------------------------------------------+
| Header (Logo, ModeToggle, GuildSelect, TemplateBar, JSONIcons, Settings, Staff, Docs)           |
+------------------------------------------------+------------------------------------------------+
| SplitPane Left (sm:w-1/2):                     | SplitPane Right (sm:w-1/2):                    |
| - Action Bar (Share, Backups, Clear, Bot, Wh)  | - MessagePreview                               |
| - Duplicate Mode Toggle Bar                    |   - Generic Bot Icon (no live avatar)          |
| - Message 1 Accordion (MessageEditor)          |   - Embeds & Markdown                          |
|   - Duplicate Palette & Layers (if V2)         |                                                |
| - Duplicate Components Accordion               |                                                |
|   - Duplicate Palette & Layers                 |                                                |
+------------------------------------------------+------------------------------------------------+
*(Sidebar.tsx is completely UNMOUNTED)*
```

### Target Discohook 3-Pane Layout
```
+---------------------------------------------------------------------------------------------------------------+
| HEADER (h-12): Logo | Mode Toggle (Classic / V2) | Template Bar | Quick JSON Controls (Export/Import/Reset)    |
+-----------------------------------+---------------------------------------------------+-----------------------+
| LEFT PANE: SIDEBAR                | CENTER PANE: EDITOR                               | RIGHT PANE: PREVIEW   |
| (w-72 shrink-0 bg-[#2b2d31])      | (flex-1 bg-[#2b2d31] overflow-y-auto)             | (flex-1 bg-[#313338]) |
|                                   |                                                   |                       |
| 1. Top: Selected Server (Guild)   | 1. Top Action Bar:                                | 1. Header:            |
|    SearchableDiscordSelect        |    - Webhook URL input & Send/Edit split button   |    - Preview title    |
|                                   |    - Bot Send/Edit split button                   |    - Mode badge       |
| 2. Tab Navigation:                |    - Share (JSON copy) & Clear buttons            |                       |
|    - Elements (Palette & Layers)  |                                                   | 2. Discord Chat Box:  |
|    - Templates / Backups List     | 2. Accordions:                                    |    - Live Bot Avatar  |
|    - Quick Targets / Config       |    - Accordion 1: Message 1 (Content & Identity)  |      (CDN image or    |
|                                   |      (TextArea, Username, Avatar, Thread)         |       custom override)|
| 3. Active Tab Content:            |    - Accordion 2: Embeds (EmbedEditor list)       |    - Bot Name & [APP] |
|    - ComponentPalette             |    - Accordion 3: Action Rows & Components        |    - Markdown Text    |
|    - LayersPanel                  |      (<DiscohookComponentsEditor />)              |    - Embed Cards      |
|                                   |                                                   |    - Real Discord     |
| 4. Anchored Footer:               | 3. Modals:                                        |      Action Rows      |
|    - Settings button              |    - ComponentEditorModal (Button props & Flow)   |      (styled buttons) |
|    - Staff Access button          |    - BotDispatchModal                             |    - V2 Components    |
|    - Docs link                    |                                                   |                       |
+-----------------------------------+---------------------------------------------------+-----------------------+
```

---

## 3. Detailed Component & File Analysis

### 3.1 `hoho_manager/client/src/App.tsx`
- **Location**: `hoho_manager/client/src/App.tsx`
- **Current Issues**:
  1. Only mounts `Header` and `SplitPane` (lines 498-680). `Sidebar` is not imported or rendered.
  2. Lines 604-632 render a duplicate "Editor Mode" bar directly under the Action Bar:
     ```tsx
     <div className="px-3 py-2 bg-[#232428] border-b border-[#1e1f22] flex items-center justify-between">
       <span className="text-[11px] font-bold uppercase tracking-wider text-[#949ba4]">Editor Mode</span>
       <div className="flex bg-[#1e1f22] p-0.5 rounded border border-[#111214]">
         <button onClick={() => setMode(EDITOR_MODES.CLASSIC)} ...>Classic</button>
         <button onClick={() => setMode(EDITOR_MODES.V2)} ...>Components V2</button>
       </div>
     </div>
     ```
  3. Lines 640-666 render an accordion "Components (Buttons, Menus & Layers)" containing `ComponentPalette` and `LayersPanel`.
  4. Auto-fetches bot identity on load (lines 406-420) and saves to `localStorage.getItem("bot_identity_cache")`, but does not set it in Zustand store.
- **Required Changes**:
  1. Import `Sidebar` from `./components/layout/Sidebar`.
  2. Change layout container to:
     ```tsx
     <div className="flex h-screen flex-col bg-[#313338] text-[#dbdee1] font-sans overflow-hidden">
       <Header />
       {/* Mobile Switcher */}
       ...
       <div className="flex min-h-0 flex-1 overflow-hidden">
         {/* Left Pane (Sidebar) */}
         <aside className={`${mobileView === "sidebar" ? "flex" : "hidden"} sm:flex w-72 shrink-0 border-r border-[#1e1f22] bg-[#2b2d31] flex-col h-full overflow-hidden`}>
           <Sidebar />
         </aside>

         {/* Center & Right Panes (SplitPane) */}
         <main className="flex min-h-0 flex-1 min-w-0">
           <SplitPane
             initialRatio={0.5}
             left={<CenterEditorWorkspace ... />}
             right={<RightPreviewWorkspace ... />}
           />
         </main>
       </div>
     </div>
     ```
  3. Remove the duplicate "Editor Mode" toggle (lines 604-632).
  4. Replace the duplicate Palette/Layers accordion with `<DiscohookComponentsEditor />`:
     ```tsx
     <Accordion title="Action Rows & Components" defaultOpen={true}>
       <DiscohookComponentsEditor />
     </Accordion>
     ```

### 3.2 `hoho_manager/client/src/components/layout/Sidebar.tsx`
- **Location**: `hoho_manager/client/src/components/layout/Sidebar.tsx`
- **Current Issues**:
  1. Uses mismatched light/dark styles (`bg-white dark:bg-gray-900`, `border-gray-200 dark:border-[#404248]`).
  2. Tab rail has `build`, `send`, `profiles`, and a link to `docs`.
  3. `profiles` tab contains `ProfilesPanel`. Milestone 2 / R3 specifically requires moving bot and webhook profile management into `SettingsModal.tsx`.
  4. Lacks the **Global Server (Guild) Selector** which Discohook places at the top of the sidebar.
  5. Lacks the **Staff Access & Settings buttons** in the sidebar footer.
- **Required Changes**:
  1. Convert to full Discord dark styling (`bg-[#2b2d31]`, `border-[#1e1f22]`, `text-[#dbdee1]`).
  2. Top Section: Add `<SearchableDiscordSelect type="guild" value={selectedGuildId || ""} onChange={setSelectedGuildId} placeholder="Select Server..." />`.
  3. Navigation Tabs:
     - **Elements**: Contains `<ComponentPalette />` and `<LayersPanel />`.
     - **Templates**: Lists saved templates/backups with quick load, save, delete, and JSON export/import.
     - **Targets**: Quick summary of active webhook/bot dispatch targets.
  4. Remove `ProfilesPanel` tab.
  5. Bottom Footer: Add buttons for:
     - Settings (opens `SettingsModal`)
     - Staff Access (opens `AccessPanel`)
     - Documentation link (`/docs`)

### 3.3 `hoho_manager/client/src/components/editor/MessageEditor.tsx`
- **Location**: `hoho_manager/client/src/components/editor/MessageEditor.tsx`
- **Current Issues**:
  Lines 96-109 render duplicate `ComponentPalette` and `LayersPanel` when `isV2` is true:
  ```tsx
  {isV2 && (
    <section className="bg-[#232428] rounded border border-[#1e1f22] p-2.5 space-y-2.5">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold uppercase tracking-wide text-[#5865f2] flex items-center gap-1.5">
          <Layers size={13} /> Components (V2)
        </h3>
      </div>
      <ComponentPalette />
      <div className="border-t border-[#1e1f22] pt-2">
        <LayersPanel />
      </div>
    </section>
  )}
  ```
- **Required Changes**:
  Remove lines 96-109 completely. Palette and Layers belong exclusively in the Left Sidebar. The Center Editor handles Action Rows via `DiscohookComponentsEditor`.

### 3.4 `hoho_manager/client/src/components/editor/DiscohookComponentsEditor.tsx`
- **Location**: `hoho_manager/client/src/components/editor/DiscohookComponentsEditor.tsx`
- **Current Status**:
  Fully implemented with 228 lines of robust Action Row building code:
  - 5-row maximum enforcement with row counter (`X / 5 Rows`)
  - 5-items per row enforcement (`X / 5 items`)
  - Style badge pills (Primary blurple, Secondary grey, Success green, Danger red, Link with external icon)
  - Row reordering up/down (`moveComponentById`)
  - Row duplication (`duplicateComponentById`)
  - Item deletion (`removeComponentById`)
  - Selection handling triggering `<ComponentEditorModal />`
  - Add Button and Add Select Menu controls
- **Required Changes**:
  Mount this component inside `App.tsx` within an "Action Rows & Components" Accordion in the Center Editor Pane.

### 3.5 `hoho_manager/client/src/components/preview/MessagePreview.tsx`
- **Location**: `hoho_manager/client/src/components/preview/MessagePreview.tsx`
- **Current Issues**:
  1. **Avatar**: Only checks `data.avatar_url`. If empty, renders a static `<Bot size={18} />` icon. It never reads the auto-fetched bot identity avatar from `api.discord.identity()`.
  2. **Author Name**: Falls back to `"Message Builder"` rather than the bot's actual username.
  3. **V2 Content Visibility**: If `isV2` is true, lines 84-89 skip rendering `payload.content` and `data.embeds`, causing any user-entered text or embeds to vanish when switching modes.
- **Required Changes**:
  1. Read `botIdentity` from `useGlobalStore` (and fallback to `localStorage.getItem("bot_identity_cache")`).
  2. Compute:
     ```ts
     const effectiveAvatar = data.avatar_url || botIdentity?.avatar || cachedBot?.avatar || null;
     const authorName = data.username || botIdentity?.username || cachedBot?.name || "Message Builder";
     ```
  3. Render `<img src={effectiveAvatar} alt="" className="h-full w-full object-cover" />` when `effectiveAvatar` is present.
  4. In the message body, render Markdown content and Embeds whenever present (`payload.content || data.content`), so both Classic and V2 data render gracefully in a single unified preview.

### 3.6 `hoho_manager/client/src/store/globalStore.ts`
- **Location**: `hoho_manager/client/src/store/globalStore.ts`
- **Current State**:
  Only tracks `selectedGuildId`.
- **Required Changes**:
  Extend `GlobalState` to store `botIdentity`:
  ```ts
  interface BotIdentity {
    id: string;
    username: string;
    avatar: string | null;
  }

  interface GlobalState {
    selectedGuildId: string | null;
    setSelectedGuildId: (id: string | null) => void;
    botIdentity: BotIdentity | null;
    setBotIdentity: (identity: BotIdentity | null) => void;
  }
  ```

---

## 4. Duplicate UI Elements Consolidation Matrix

| # | Element | Current Duplicate Locations | Consolidated Location |
|---|---|---|---|
| 1 | **Editor Mode Toggle** | `Header.tsx:26` & `App.tsx:604` | Single toggle in `Header.tsx` (top-left beside Brand) |
| 2 | **Component Palette** | `Sidebar.tsx:52`, `App.tsx:656`, `MessageEditor.tsx:104` | Left Sidebar ("Elements" tab) |
| 3 | **Layers Panel** | `Sidebar.tsx:55`, `App.tsx:663`, `MessageEditor.tsx:106` | Left Sidebar ("Elements" tab below Palette) |
| 4 | **Action Rows Builder** | Orphaned (`DiscohookComponentsEditor.tsx`) | Center Editor Pane ("Action Rows & Components" Accordion) |
| 5 | **Profiles Management** | `Sidebar.tsx:73` (`ProfilesPanel`) & `SettingsModal.tsx` | Strictly in `SettingsModal.tsx` (Profiles tab) per R3 |
| 6 | **Server (Guild) Selector**| `Header.tsx:130` only | Top of Left Sidebar as primary server selector |
| 7 | **Staff & Settings Triggers**| `Header.tsx:201` only | Anchored in Left Sidebar footer + Header |

---

## 5. Responsive Behavior & Container Height Specifications

1. **Outer Viewport**:
   - `h-screen overflow-hidden` on root container. Prevents double scrollbars.
2. **Left Sidebar**:
   - Desktop (`md` / `lg`): `w-72 shrink-0 border-r border-[#1e1f22] bg-[#2b2d31]`
   - Mobile (`< 640px`): Managed by mobile switcher (`mobileView: "sidebar" | "editor" | "preview"`).
3. **Center Editor Pane**:
   - Flex column with `h-full overflow-hidden`.
   - Top action bar: `shrink-0`.
   - Main editor workspace: `flex-1 overflow-y-auto custom-scrollbar`.
4. **Right Preview Pane**:
   - Flex column with `h-full overflow-hidden bg-[#313338]`.
   - Preview header: `shrink-0`.
   - Live preview body: `flex-1 overflow-y-auto custom-scrollbar`.
5. **SplitPane Divider**:
   - `SplitPane.tsx` provides pointer-event drag resizing between Center and Right panes with keyboard accessibility (`ArrowLeft` / `ArrowRight`).

---

## 6. Implementation Action Plan for Worker

1. **Step 1: Global Store Update** (`hoho_manager/client/src/store/globalStore.ts`)
   - Add `botIdentity` state and `setBotIdentity` action.
2. **Step 2: Live Avatar in Preview** (`hoho_manager/client/src/components/preview/MessagePreview.tsx`)
   - Read `botIdentity` / cache.
   - Fall back from `data.avatar_url` -> `botIdentity.avatar` -> default bot icon.
   - Display bot username from `data.username` -> `botIdentity.username` -> `"Message Builder"`.
   - Unify rendering of content, embeds, and components.
3. **Step 3: Refactor Sidebar** (`hoho_manager/client/src/components/layout/Sidebar.tsx`)
   - Remove light-theme classes and `ProfilesPanel`.
   - Add Guild selector at top.
   - Add navigation tabs (Elements with `ComponentPalette` & `LayersPanel`, Templates with backups/saved list).
   - Add footer with Settings, Staff Access, Docs triggers.
4. **Step 4: Clean Up MessageEditor** (`hoho_manager/client/src/components/editor/MessageEditor.tsx`)
   - Remove lines 96-109 (duplicate palette and layers).
5. **Step 5: Assemble 3-Pane Layout in App.tsx** (`hoho_manager/client/src/App.tsx`)
   - Mount `<Sidebar />` as Left Pane.
   - Remove duplicate "Editor Mode" bar (lines 604-632).
   - Mount `<DiscohookComponentsEditor />` in Center Pane.
   - Pass fetched identity to `setBotIdentity`.
6. **Step 6: Test Suite Verification**
   - Run `npm test` and `npm run typecheck` in `hoho_manager/client`.
