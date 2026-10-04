# Handoff Report: Discohook UI Specification Extraction

**Agent**: `spec_miner_r3_1` (Discohook Spec Miner)  
**Parent**: `orchestrator_3` (`d6685582-f7eb-443b-9c86-c4628e3bad79`)  
**Date**: 2026-10-03  
**Working Directory**: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\spec_miner_r3_1`  

---

## 1. Observation

Direct code observations from authoritative sources:
- `discohook_src/packages/site/app/routes/_index.tsx`
- `discohook_src/packages/site/app/components/Header.tsx`
- `discohook_src/packages/site/app/components/Drawer.tsx`
- `discohook_src/packages/site/app/modals/Modal.tsx`
- `discohook_src/packages/site/app/components/Button.tsx`
- `discohook_src/packages/site/app/components/tabs.tsx`
- `discohook_src/packages/site/app/components/TextInput.tsx`
- `discohook_src/packages/site/app/components/collapsible.ts`
- `discohook_src/packages/site/app/components/editor/MessageEditor.client.tsx`
- `discohook_src/packages/site/tailwind.config.ts`
- `discohook_src/packages/site/app/styles/app.css`
- `discohook_src/packages/site/app/root.tsx`
- `hoho_manager/client/src/App.tsx`
- `hoho_manager/client/src/components/layout/Header.tsx`
- `hoho_manager/client/src/components/layout/Sidebar.tsx`
- `hoho_manager/client/src/components/editor/MessageEditor.tsx`
- `hoho_manager/client/src/components/ui/SearchableDiscordSelect.tsx`
- `hoho_manager/server/src/services/discordService.ts`

### 1.1 Sticky Top Header Observation
In `discohook_src/packages/site/app/components/Header.tsx`:
- Line 78:
  ```tsx
  <div className={twJoin(
    "sticky top-0 left-0 z-20 bg-slate-50 dark:bg-[#1E1F22] border-2 border-slate-50 dark:border-[#1E1F22] shadow-md w-full px-4 h-12 flex",
    ...
  )}>
  ```
- Height: exactly `h-12` (48px / 3rem).
- Left: Logo in `h-8 w-8 my-auto mr-4`.
- Center / Right container: `grow flex overflow-x-auto ms-6 items-center`.
- Center buttons:
  - Settings: `Button` with `discordstyle={ButtonStyle.Secondary}`, `me-2`, triggers `setSettingsOpen(true)`.
  - History: `Button` with `discordstyle={ButtonStyle.Secondary}`, `me-2`, triggers `setShowHistoryModal(true)`.
  - Help: `Button` with `discordstyle={ButtonStyle.Secondary}`, `ms-auto`, triggers `setHelpOpen(true)`.
  - Donate / Discord link: `Button` with `discordstyle={ButtonStyle.Secondary}`, `ms-2`.
- Right / Profile button:
  - `button` with `className="flex my-auto ltr:-mx-2 rtl:mr-2 rtl:-ml-2 py-1 px-2 rounded-lg shrink-0 hover:bg-gray-200 hover:dark:bg-gray-700 transition"`, triggers `setDrawerOpen(true)`.
  - Contains Avatar `h-7 w-7 rounded-full` + user name `hidden sm:block text-base font-medium ms-1.5`.

### 1.2 Main Body 50/50 Split Layout Observation
In `discohook_src/packages/site/app/routes/_index.tsx`:
- Line 775: `<div className="h-screen overflow-hidden">`
- Line 952: `<Header user={user} setShowHistoryModal={setShowHistory} />`
- Lines 953-967:
  ```tsx
  <div
    className={twJoin(
      "h-[calc(100%_-_3rem)]",
      settings.forceDualPane ? "flex" : "md:flex",
    )}
  >
    <div
      className={twMerge(
        "py-4 h-full overflow-y-scroll",
        settings.forceDualPane
          ? "w-1/2"
          : twJoin("md:w-1/2", tab === "editor" ? "" : "hidden md:block"),
      )}
      ref={editorRef}
    >
      <div className="px-4">
        {/* Editor contents */}
      </div>
    </div>
  ```
- Lines 1610-1654:
  ```tsx
    <div
      className={twMerge(
        "h-full flex-col",
        "border-s-gray-400 dark:border-s-[#1E1F22]",
        settings.forceDualPane
          ? "flex w-1/2 border-s-2"
          : twJoin(
              "md:w-1/2 md:border-s-2",
              tab === "preview" ? "flex" : "hidden md:flex",
            ),
      )}
      ref={previewRef}
    >
      <div className="overflow-y-scroll grow p-4 pb-8">
        {/* Preview contents */}
      </div>
    </div>
  </div>
  ```
- No sidebar occupies the main body space. It is strictly 50% left and 50% right.
- On viewports < `md` (768px), it collapses gracefully into a tabbed layout (`tab === 'editor'` vs `tab === 'preview'`), toggled by buttons at the top of each pane.

### 1.3 Off-Canvas Drawer Observation
In `discohook_src/packages/site/app/components/Drawer.tsx` & `modals/Modal.tsx`:
- Lines 24-43 of `Drawer.tsx`:
  ```tsx
  <Dialog.Popup
    className={twJoin(
      "box-border fixed z-[31] translate-x-0 translate-y-0 top-0",
      props.anchor === "left"
        ? "left-0 rounded-r-xl"
        : props.anchor === "right"
          ? "right-0 rounded-l-xl"
          : "start-0 rounded-e-xl",
      "w-96 md:w-1/3 max-w-[min(35rem,_calc(100vw_-_3rem))]",
      "h-screen max-h-screen overflow-y-auto",
      "bg-gray-50 text-black dark:bg-gray-800 dark:text-gray-50 shadow",
      "transition-all",
      "data-[starting-style]:-translate-x-full",
      "data-[ending-style]:-translate-x-full",
    )}
  >
  ```
- Backdrop in `Modal.tsx`:
  ```tsx
  export const dialogBackdropClassName = twJoin(
    "fixed z-30 inset-0 bg-black opacity-20 dark:opacity-70 transition-opacity",
    "data-[starting-style]:opacity-0 data-[ending-style]:opacity-0",
  );
  ```
- In contrast, in `hoho_manager/client/src/App.tsx:510-524`, the sidebar was rendered as an inline docked pane on desktop (`md:static md:z-auto w-72`), occupying 288px of horizontal width and forcing SplitPane into cramped space, causing clipping on narrow split screens.

### 1.4 Classic vs Components V2 Mode Toggle Observation
In `discohook_src/packages/site/app/components/editor/MessageEditor.client.tsx`:
- Line 703:
  ```tsx
  {isComponentsV2(message.data) ? (
    <ComponentMessageEditor {...childProps} />
  ) : (
    <StandardMessageEditor {...childProps} />
  )}
  ```
- `isComponentsV2` checks `new MessageFlagsBitField(message.flags ?? 0).has(MessageFlags.IsComponentsV2)` (1 << 15).
- In `StandardMessageEditor`:
  - `TextArea` for message content (2000 chars limit).
  - Profile section (Username, Avatar URL, Thread name).
  - Embeds section (`EmbedEditor` list, Add Embed button).
  - Attachments section.
- In `ComponentMessageEditor`:
  - Components hierarchy list: TextDisplay, Container, MediaGallery, File, Separator, ActionRow.
  - ButtonSelect for adding components.
  - Character counter (4000 total characters limit for TextDisplay).
  - Total component limit (20 max components).
- In `hoho_manager/client/src/components/editor/MessageEditor.tsx:18-125`:
  `MessageEditor` unconditionally rendered `TextArea` + `EmbedEditor` + `<DiscohookComponentsEditor />` regardless of `mode`. The mode toggle in `Header.tsx` updated `useMessageStore.mode`, but `MessageEditor.tsx` completely ignored `mode`.

### 1.5 Discord Member Search API Observation
In `hoho_manager/server/src/services/discordService.ts:373-385`:
```ts
const rawMembers = await apiRequest<any[]>(
  "GET",
  `/guilds/${encodeURIComponent(guildId)}/members/search?query=${encodeURIComponent(query)}&limit=25`,
  { token },
);
return rawMembers.map((m) => ({
  id: m.user?.id ?? m.id,
  username: m.user?.username ?? m.username ?? "",
  global_name: m.user?.global_name ?? null,
  nickname: m.nick ?? null,
  avatar: m.user?.avatar ?? m.avatar ?? null,
}));
```
In `hoho_manager/client/src/components/ui/SearchableDiscordSelect.tsx:58`:
```ts
const res = await api.discord.searchMembers(guildId, search);
setMemberResults(
  res.members.map((m) => ({
    id: m.user.id, // BUG: m is already the member summary object; m.user is undefined!
    name: m.nick || m.user.username, // BUG: throws TypeError reading property of undefined!
  }))
);
```
`m` returned by the server is already flat: `{ id, username, global_name, nickname, avatar }`. Reading `m.user.id` crashes with TypeError, causing the catch block to swallow the error and leave `memberResults` empty!

---

## 2. Logic Chain

1. **Bug Root Cause Analysis**:
   - **Sidebar clipping on split-screen**:
     In `hoho_manager`, `App.tsx` has `isSidebarOpen = true` by default and applies `md:static md:z-auto w-72`. On screens between 768px and 1200px (e.g. split-screen laptop at ~1000px), 288px is stolen by the inline sidebar. The remaining 712px is split between Editor and Preview, squeezing both into ~350px each, which breaks layout and clips content.
     In Discohook, the drawer is **never** inline. It is `fixed z-[31]` with backdrop `fixed z-30 inset-0`. When closed, it takes 0px of space. The Editor and Preview take 100% of the screen width (50% each).
   - **Mode toggle doing nothing**:
     `Header.tsx` dispatches `setMode(option.id)` to `messageStore`. But `MessageEditor.tsx` does not read `mode` from `messageStore`. It renders embeds and components builder at the same time. Switching mode must selectively render `StandardMessageEditor` (content + embeds) or `ComponentMessageEditor` (components V2 tree).
   - **Member search failing**:
     `SearchableDiscordSelect.tsx` line 58 reads `m.user.id` instead of `m.id`. Because the server already formatted the member into `{ id, username, global_name, nickname, avatar }`, `m.user` is undefined, throwing `TypeError: Cannot read properties of undefined (reading 'id')`. This causes search to silently fail.
   - **Sticky Top Header layout deviation**:
     `Header.tsx` currently contains an inline template name input, raw JSON buttons, and staff login crammed into the header bar, while missing Discohook's standard button layout (Settings, History, Help, Discord/Docs, and user profile avatar button).

2. **Architectural Parity Requirements**:
   - Align layout container with Discohook's `h-screen overflow-hidden` + header `h-12` + main `h-[calc(100%_-_3rem)]`.
   - Make Sidebar a true off-canvas Drawer with `fixed z-[31]`, backdrop `fixed z-30`, `Ctrl+B` toggle, outside click dismissal, and default to collapsed on viewports ≤ 1100px.
   - Split MessageEditor into Classic view (content + embeds) and Components V2 view (action rows, buttons, selects, text display), controlled by the Mode toggle.

---

## 3. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Layout | Sticky Top Header | Fixed-height navigation bar with brand, navigation buttons, and user drawer trigger | Window scroll | Top-pinned bar (`h-12`, `z-20`) | Fixed height, horizontal overflow scrolls if cramped | `discohook_src/.../Header.tsx:78` |
| 2 | Layout | 50/50 Body Split | Two equal-width panes for Editor and Preview filling viewport height below header | Viewport resize | 50% left editor, 50% right preview (`calc(100% - 3rem)`) | Under `md` breakpoint, collapses to single active tab | `discohook_src/.../_index.tsx:953` |
| 3 | Layout | Independent Pane Scrolling | Editor and Preview scroll independently without whole-page scrollbars | Pane scroll | Scrollable containers (`overflow-y-scroll` / `overflow-y-auto`) | No double scrollbars or window blowout | `discohook_src/.../_index.tsx:961,1623` |
| 4 | Navigation | Off-Canvas Drawer | Slide-over drawer on the left overlaying content with backdrop | Drawer toggle / Ctrl+B | Overlay drawer (`w-96 md:w-1/3`, `z-[31]`) | Outside click or Esc dismisses | `discohook_src/.../Drawer.tsx:24` |
| 5 | Navigation | Backdrop Dismiss | Darkened background behind drawer/modals that captures clicks to close | Pointer click on backdrop | Dismisses drawer/modal | Backdrop opacity transitions | `discohook_src/.../Modal.tsx:10` |
| 6 | Navigation | Ctrl+B Drawer Shortcut | Keyboard shortcut toggles sidebar drawer visibility | Keyboard `Ctrl+B` / `Cmd+B` | Toggles `isSidebarOpen` | Prevents default browser bookmark shortcut | Requirements & Header |
| 7 | Editor | Classic Message Mode | Standard Discord webhook message editor (Content text, username/avatar, Embeds) | User typing, embed additions | Message JSON payload with `content` & `embeds` | Max 2000 chars, max 10 embeds, max 6000 embed chars | `MessageEditor.client.tsx:1242` |
| 8 | Editor | Components V2 Mode | Component hierarchy builder for interactive Discord elements | Component selection & configuration | Message JSON payload with `flags: 32768` & `components` | Max 20 components, max 4000 text characters | `MessageEditor.client.tsx:1767` |
| 9 | Editor | Mode Switching Toggle | Tab selector between Classic and Components V2 modes | User tab click | Sets active editor mode | Preserves shared message state | `Header.tsx:25` & `tabs.tsx:38` |
| 10 | API / Search | REST Guild Member Search | Discord REST endpoint search without requiring privileged gateway intents | Guild ID + query string | Array of members `{ id, username, global_name, nickname }` | Returns empty array if bot lacks permission or not found | `discordService.ts:366` |
| 11 | API / Search | Manual Snowflake Fallback | Allows typing raw 17–20 digit Discord snowflake ID when search yields no match | Raw numeric snowflake string | Sets ID as selected value | Validates snowflake regex `^\d{17,20}$` | `SearchableDiscordSelect.tsx:101` |
| 12 | Theming | Discord Dark Mode Tokens | Canonical Discord dark theme color tokens and classes | Tailwind configuration | High-fidelity Discord look & feel | Fallback to Discord native dark | `tailwind.config.ts:31` |
| 13 | UI Components | Discord Styled Buttons | Buttons styled matching Discord's native Primary, Secondary, Danger, Success | `discordstyle` enum | Styled button element (`h-8`, `px-4`, `rounded-lg`) | Disabled states have opacity 0.5 | `discohook_src/.../Button.tsx:26` |
| 14 | UI Components | Discord Text Inputs | Inputs and textareas styled with Discord dark background and borders | Text input | Styled input (`h-9`, `px-3.5`, `rounded-lg`) | Border highlight on focus (`focus:border-blurple`) | `discohook_src/.../TextInput.tsx:9` |

---

## 4. Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Sidebar on Split-Screen (≤1100px) | Viewport width 1024px, sidebar opened | Fixed sidebar squishes editor and preview if inline; when off-canvas drawer, editor + preview maintain 50/50 ratio without clipping. |
| 2 | Sidebar Outside Click | Click on darkened backdrop outside drawer popup | Backdrop captures pointerdown/click and sets `isOpen = false`, smoothly animating drawer out. |
| 3 | Ctrl+B with Text Field Focused | Pressing Ctrl+B while typing in a textarea | If typing markdown, textarea might format bold; outside input, Ctrl+B toggles sidebar drawer. Handler should check active element or use global hotkey listener. |
| 4 | Member Search Without Guild Selected | User opens member search without selecting a server | Search cannot query guild members; UI must gracefully fall back to manual ID entry prompt. |
| 5 | Member Search Result Parsing | API returns `{ id, username, global_name, nickname }` | Accessing `m.user.id` crashes with TypeError; accessing `m.id` and `m.nickname ?? m.global_name ?? m.username` succeeds. |
| 6 | Switching Classic → Components V2 | Message already has text content and embeds | Content is preserved or converted into TextDisplay component; embeds hidden while in V2 mode. |
| 7 | Mobile Viewport (<768px) | Viewport width 375px | Dual 50/50 panes collapse into single pane view (`tab === "editor"` or `tab === "preview"`) with top toggle button. |
| 8 | Long Message Content Scrolling | Embed editor with 10 embeds or 20 components | Left pane scrolls internally (`overflow-y-auto`); right preview and top header remain fixed. |

---

## 5. Caveats

- **Intents Limitation**: The Discord bot does not have privileged gateway intents (`GUILD_MEMBERS`, `MESSAGE_CONTENT`). All member searching must strictly use the REST search endpoint (`GET /guilds/{guildId}/members/search?query=...`).
- **Nesting Components**: Components V2 in Discord allows nested components inside ActionRows, Containers, and Sections. The V2 mode editor must support rendering and adding components to these parents.
- No caveats regarding Discohook UI source code: `discohook_src` is fully available and directly inspected.

---

## 6. Conclusion & Exact Implementation Specifications

### 6.1 Top Sticky Header
- **Container**:
  ```tsx
  <header className="sticky top-0 left-0 z-20 bg-slate-50 dark:bg-[#1E1F22] border-b-2 border-slate-50 dark:border-[#1E1F22] shadow-md w-full px-4 h-12 flex items-center justify-between font-sans shrink-0">
  ```
- **Left**:
  - Logo + App title: `<div className="h-8 w-8 my-auto mr-3"><Logo /></div>`
  - Sidebar Drawer Toggle Button: `<button onClick={toggleSidebar} title="Toolbox (Ctrl+B)"><PanelLeft size={18} /></button>`
- **Center**:
  - Settings Button: Opens Settings Modal (Admin / Profile / Database configs)
  - Backups / History Button: Opens Templates / Backups Modal
  - Mode Switch: Pill tabs for `Classic` / `Components V2`
  - Selected Server: Compact dropdown for Guild selection
- **Right**:
  - Staff / Help / Docs buttons
  - User Avatar / Profile Button: clicking opens user account / staff access panel.

### 6.2 Main Body 50/50 Split
- **Container**:
  ```tsx
  <div className="h-[calc(100vh_-_3rem)] flex flex-row overflow-hidden w-full">
  ```
- **Left Pane (Editor)**:
  ```tsx
  <div className="w-full md:w-1/2 h-full overflow-y-auto custom-scrollbar bg-[#2b2d31] flex flex-col min-w-0">
  ```
  Contains top action bar (Share, Clear, Bot/Webhook send split button), followed by `MessageEditor`.
- **Right Pane (Live Preview)**:
  ```tsx
  <div className="w-full md:w-1/2 h-full overflow-y-auto custom-scrollbar bg-[#313338] border-s-2 border-s-gray-300 dark:border-s-[#1E1F22] flex flex-col min-w-0">
  ```
  Contains `MessagePreview`.
- **No inline sidebar**: The sidebar does NOT render in this container.

### 6.3 Off-Canvas Drawer (Toolbox / Sidebar)
- **Positioning**:
  ```tsx
  {/* Backdrop */}
  {isSidebarOpen && (
    <div
      className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm transition-opacity"
      onClick={() => setIsSidebarOpen(false)}
    />
  )}

  {/* Drawer Popup */}
  <div
    className={`fixed top-0 left-0 z-[31] h-screen w-80 max-w-[calc(100vw-3rem)] bg-[#2b2d31] border-r border-[#1e1f22] shadow-2xl transition-transform duration-300 ease-in-out ${
      isSidebarOpen ? "translate-x-0" : "-translate-x-full pointer-events-none"
    }`}
  >
    <Sidebar onClose={() => setIsSidebarOpen(false)} />
  </div>
  ```
- **Keyboard listener**:
  ```ts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "b") {
        e.preventDefault();
        toggleSidebar();
      }
      if (e.key === "Escape" && isSidebarOpen) {
        setIsSidebarOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isSidebarOpen, toggleSidebar]);
  ```

### 6.4 Mode Toggle in MessageEditor
- In `MessageEditor.tsx`:
  Read `mode` from `useMessageStore`:
  ```tsx
  const mode = useMessageStore((state) => state.mode);
  ```
  - If `mode === EDITOR_MODES.CLASSIC`:
    Render Text Content + Identity + Embeds.
  - If `mode === EDITOR_MODES.V2`:
    Render Identity + Components V2 Builder (`DiscohookComponentsEditor` / Component Palette / Action Rows).

### 6.5 Member Search Fix
- In `SearchableDiscordSelect.tsx`:
  Change lines 56–61 to:
  ```ts
  const res = await api.discord.searchMembers(guildId, search);
  setMemberResults(
    (res.members || []).map((m: any) => ({
      id: m.id,
      name: m.nickname ? `${m.nickname} (${m.username})` : (m.global_name ? `${m.global_name} (${m.username})` : m.username),
    }))
  );
  ```

---

## 7. Verification Method

To verify the specifications and implementation:
1. **Typecheck & Build**:
   ```pwsh
   cd hoho_manager
   npm run build
   ```
   Must pass with 0 TypeScript errors.
2. **Narrow Viewport Test**:
   Resize browser to 1000px and 768px.
   Confirm sidebar defaults to closed, does not consume screen width, and opening it overlays smoothly over content without causing horizontal scrollbars or clipping the preview.
3. **Drawer Dismissal Test**:
   - Click outside on backdrop -> Drawer closes.
   - Press `Ctrl+B` -> Drawer toggles open and closed.
   - Click Close icon -> Drawer closes.
4. **Mode Toggle Test**:
   - Click "Classic" -> Editor shows Content and Embeds sections only.
   - Click "Components V2" -> Editor shows Component builder (Action Rows, Buttons, Text Display) only.
   - Preview reflects the corresponding mode.
5. **Member Search Test**:
   - Open Staff Access panel -> click "Grant Access" -> type username in member search -> verify results are populated from `GET /guilds/{guildId}/members/search`.
