# Milestone 3 (Iteration 2) Deep Architecture Analysis: Sidebar Collapse & True Discohook Dual-Pane Proportions

## 1. Executive Summary

During Milestone 3 Iteration 1 review, Reviewer 1 issued a `REQUEST_CHANGES` gate failure due to violation of the explicit user correction:
```markdown
USER CORRECTION: "i dont want 3 pane layout but like discohook layout only"
Please ensure your UI layout perfectly mirrors Discohook.app's specific layout proportions and structure, rather than a generic 3-pane layout.
```

In the Iteration 1 implementation, `App.tsx:507-513` permanently pinned a 288px sidebar (`w-72 md:flex`) on desktop, forcing a rigid 3-pane layout. This squished both the Editor pane and the Live Discord Preview pane down to ~490px widths on standard laptops, causing premature text wrapping and ruining Discord embed fidelity. Furthermore, multiple UI controls were duplicated across `Header.tsx` and `Sidebar.tsx` (such as the Selected Server dropdown, Settings, Staff Access, and Docs).

By inspecting the official reference source code in `discohook_src/packages/site/app/routes/_index.tsx` (lines 953–965 and 1610–1620), we observed the ground-truth architecture:
1. **The workbench is strictly a 50/50 dual pane**:
   - `w-1/2` (or `md:w-1/2`) hosts the Editor (`MessageEditor.client`).
   - `w-1/2` (or `md:w-1/2`) hosts the Live Discord Preview (`Message.client`).
2. **There is NO pinned sidebar**:
   - The drawer (`Drawer.tsx`) is an on-demand slide-over panel opened via a button in `Header.tsx`.
   - When closed, the screen is 100% dual pane (50% Editor, 50% Preview).

This document specifies the exact technical architecture, state flow, JSX layout, and CSS/Tailwind classes for Worker M3 to implement the authentic Discohook dual-pane experience with a collapsible sidebar and clean deduplication.

---

## 2. Forensic Analysis: Reference Discohook vs. Hoho Manager

### 2.1 The Official Discohook Reference Implementation
In `discohook_src/packages/site/app/routes/_index.tsx`:
```tsx
<Header user={user} setShowHistoryModal={setShowHistory} />
<div className={twJoin("h-[calc(100%_-_3rem)]", settings.forceDualPane ? "flex" : "md:flex")}>
  {/* Left Pane: 50% width Editor */}
  <div className={twMerge("py-4 h-full overflow-y-scroll", settings.forceDualPane ? "w-1/2" : twJoin("md:w-1/2", tab === "editor" ? "" : "hidden md:block"))} ref={editorRef}>
    ...
  </div>
  {/* Right Pane: 50% width Live Preview */}
  <div className={twMerge("h-full flex-col border-s-gray-400 dark:border-s-[#1E1F22]", settings.forceDualPane ? "flex w-1/2 border-s-2" : twJoin("md:w-1/2 md:border-s-2", tab === "preview" ? "flex" : "hidden md:flex"))} ref={previewRef}>
    ...
  </div>
</div>
```
And in `discohook_src/packages/site/app/components/Drawer.tsx`:
```tsx
<Dialog.Popup
  className={twJoin(
    "box-border fixed z-[31] translate-x-0 translate-y-0 top-0 left-0 rounded-r-xl",
    "w-96 md:w-1/3 max-w-[min(35rem,_calc(100vw_-_3rem))]",
    "h-screen max-h-screen overflow-y-auto",
    "bg-gray-50 dark:bg-gray-800 shadow transition-all",
    "data-[starting-style]:-translate-x-full data-[ending-style]:-translate-x-full",
  )}
>
```
Key Takeaway: Discohook's primary layout is a **clean 50/50 dual pane**. Auxiliary navigation and tools live in an on-demand slide-over drawer triggered from the top navbar.

### 2.2 Defects in Hoho Manager Iteration 1
1. **Pinned 3-Pane**:
   `App.tsx:507-513` rendered:
   ```tsx
   <div className={`${mobileView === "sidebar" ? "flex" : "hidden"} md:flex h-full w-72 shrink-0 flex-col`}>
     <Sidebar />
   </div>
   ```
   On desktop (`md:`), `md:flex` forced the 288px column to be permanently visible with no toggle button or collapse state.
2. **Duplicated UI Controls**:
   - `Header.tsx:130-138` and `Sidebar.tsx:30-41` both rendered `<SearchableDiscordSelect type="guild" />`.
   - `Header.tsx:201-214` and `Sidebar.tsx:142-160` both rendered Settings and Staff Access buttons, and both rendered duplicate modal instances (`<SettingsModal>` and `<Modal><AccessPanel /></Modal>`).
   - `Header.tsx:239-244` and `Sidebar.tsx:161-168` both rendered Docs links.
   - `App.tsx:548-554` ("Clear") and `Header.tsx:193-198` ("Start over") executed separate reset flows with inconsistent template detachment.
3. **Static Sections in Sidebar**:
   `Sidebar.tsx:71-86` used static `<section>` tags rather than collapsible accordions as claimed in the previous handoff.

---

## 3. Architecture Specification

### 3.1 State Management: `isSidebarOpen` in `globalStore.ts`

The sidebar collapse state must be accessible to `Header.tsx` (toggle button), `Sidebar.tsx` (close button), `App.tsx` (layout styling), and keyboard shortcuts. Therefore, it belongs in `useGlobalStore`:

```typescript
// hoho_manager/client/src/store/globalStore.ts

interface GlobalState {
  selectedGuildId: string | null;
  setSelectedGuildId: (id: string | null) => void;
  botIdentity: BotIdentity | null;
  setBotIdentity: (identity: BotIdentity | null) => void;
  // NEW: Collapsible sidebar state
  isSidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
}
```

Implementation details:
- **Default value**: `false` (or persisted via `localStorage.getItem("hoho_sidebar_open") === "true"`).
- **Defaulting to `false`** ensures that when the user visits the app, they immediately see the clean 50/50 dual-pane Discohook layout!
- **Persistence**: Store changes in `localStorage.setItem("hoho_sidebar_open", String(updated))`.
- **Keyboard shortcut**: In `App.tsx`, listen for `(e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "b"` to call `toggleSidebar()`.

---

### 3.2 Header Integration: `Header.tsx`

#### 3.2.1 Toggle Button
Add a sidebar toggle button on the left of the Header (before the Brand Icon):
```tsx
import { PanelLeft, PanelLeftClose } from "lucide-react";
// In Header component:
const { isSidebarOpen, toggleSidebar } = useGlobalStore();

<button
  type="button"
  onClick={toggleSidebar}
  className={`flex h-8 w-8 items-center justify-center rounded-lg border transition-colors shrink-0 ${
    isSidebarOpen
      ? "bg-[#5865f2] text-white border-[#5865f2] shadow-sm"
      : "bg-transparent text-[#949ba4] hover:text-[#dbdee1] hover:bg-[#35373c]/60 border-transparent"
  }`}
  title={isSidebarOpen ? "Collapse Sidebar (Ctrl+B)" : "Open Sidebar (Elements & Templates) (Ctrl+B)"}
  aria-label="Toggle sidebar"
  aria-expanded={isSidebarOpen}
>
  {isSidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeft size={18} />}
</button>
```

#### 3.2.2 Single Authoritative Guild Selector & Actions
- Retain `<SearchableDiscordSelect type="guild" />` in `Header.tsx:130-138`.
- Retain Settings, Staff Access, Docs, and Start Over in `Header.tsx`.
- Because the Header is sticky and always visible, these global controls remain permanently accessible whether the sidebar is collapsed or expanded.

---

### 3.3 Sidebar Refactor: `Sidebar.tsx`

#### 3.3.1 Clean Deduplication
1. **Remove Duplicate Guild Selector**: Delete lines 30–41.
2. **Remove Duplicate Settings, Staff Access & Modals**:
   - Delete `settingsOpen` and `accessOpen` states from `Sidebar.tsx`.
   - Remove `<SettingsModal>` and `<Modal><AccessPanel /></Modal>` instances from `Sidebar.tsx`.
   - Remove footer buttons for Settings, Staff Access, and Docs.
3. **Add Header with Title & Collapse Chevron**:
   ```tsx
   <div className="p-3 border-b border-[#1e1f22] bg-[#1e1f22] shrink-0 flex items-center justify-between">
     <div className="flex items-center gap-2">
       <Blocks size={16} className="text-[#5865f2]" />
       <span className="text-xs font-bold uppercase tracking-wider text-[#dbdee1]">
         Tools & Palette
       </span>
     </div>
     <button
       type="button"
       onClick={() => setSidebarOpen(false)}
       className="p-1 rounded text-[#949ba4] hover:text-white hover:bg-[#35373c] transition-colors"
       title="Collapse Sidebar (Ctrl+B)"
     >
       <ChevronLeft size={16} />
     </button>
   </div>
   ```

#### 3.3.2 Collapsible Section Accordions
Replace the static `<section>` tags in lines 71–86 with collapsible accordions:
```tsx
const [paletteOpen, setPaletteOpen] = useState(true);
const [layersOpen, setLayersOpen] = useState(true);

{activeTab === "elements" && (
  <div className="p-3 space-y-3">
    {/* Component Palette Collapsible Accordion */}
    <div className="rounded border border-[#1e1f22] bg-[#232428] overflow-hidden">
      <button
        type="button"
        onClick={() => setPaletteOpen(!paletteOpen)}
        className="w-full flex items-center justify-between p-2.5 bg-[#1e1f22]/60 hover:bg-[#1e1f22] transition-colors text-left"
      >
        <span className="text-[11px] font-bold uppercase tracking-wider text-[#949ba4]">
          Component Palette
        </span>
        {paletteOpen ? <ChevronDown size={14} className="text-[#949ba4]" /> : <ChevronRight size={14} className="text-[#949ba4]" />}
      </button>
      {paletteOpen && (
        <div className="p-2.5 border-t border-[#1e1f22]">
          <ComponentPalette />
        </div>
      )}
    </div>

    {/* Layers & Hierarchy Collapsible Accordion */}
    <div className="rounded border border-[#1e1f22] bg-[#232428] overflow-hidden">
      <button
        type="button"
        onClick={() => setLayersOpen(!layersOpen)}
        className="w-full flex items-center justify-between p-2.5 bg-[#1e1f22]/60 hover:bg-[#1e1f22] transition-colors text-left"
      >
        <span className="text-[11px] font-bold uppercase tracking-wider text-[#949ba4]">
          Layers & Hierarchy
        </span>
        {layersOpen ? <ChevronDown size={14} className="text-[#949ba4]" /> : <ChevronRight size={14} className="text-[#949ba4]" />}
      </button>
      {layersOpen && (
        <div className="p-2.5 border-t border-[#1e1f22]">
          <LayersPanel />
        </div>
      )}
    </div>
  </div>
)}
```

---

### 3.4 Workbench Layout Refactor: `App.tsx`

#### 3.4.1 Keyboard Shortcut & State
```tsx
const { isSidebarOpen, setSidebarOpen, toggleSidebar } = useGlobalStore();

// Keyboard shortcut: Ctrl+B / Cmd+B to toggle sidebar
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "b") {
      e.preventDefault();
      toggleSidebar();
    }
  };
  window.addEventListener("keydown", handleKeyDown);
  return () => window.removeEventListener("keydown", handleKeyDown);
}, [toggleSidebar]);
```

#### 3.4.2 Main Layout Structure
```tsx
<main className="flex min-h-0 flex-1 overflow-hidden relative">
  {/* Mobile Backdrop Overlay */}
  {isSidebarOpen && (
    <div
      className="fixed inset-0 bg-black/60 z-30 md:hidden backdrop-blur-sm"
      onClick={() => setSidebarOpen(false)}
      aria-hidden="true"
    />
  )}

  {/* Collapsible Sidebar: Overlay Drawer on Mobile, Docked Collapsible on Desktop */}
  <div
    className={`
      fixed inset-y-0 left-0 z-40 md:static md:z-auto
      h-full shrink-0 flex-col bg-[#2b2d31] border-r border-[#1e1f22]
      transition-[width,transform] duration-200 ease-in-out
      ${
        isSidebarOpen
          ? "w-72 flex translate-x-0"
          : "w-0 -translate-x-full md:translate-x-0 md:hidden"
      }
      ${mobileView === "sidebar" ? "!flex !w-72 !translate-x-0" : ""}
    `}
  >
    <Sidebar />
  </div>

  {/* Center & Right Panes: SplitPane hosting Editor & Live Preview */}
  <div
    className={`
      ${mobileView === "sidebar" ? "hidden" : "flex"}
      md:flex flex-1 min-w-0 h-full
    `}
  >
    <SplitPane
      initialRatio={0.5}
      left={
        <div
          className={`${
            mobileView === "editor" ? "flex" : "hidden"
          } md:flex flex-col h-full bg-[#2b2d31] border-r border-[#1e1f22] w-full min-w-0`}
        >
          {/* Action Bar */}
          ...
          {/* Editor Workspace */}
          <div className="flex-1 overflow-y-auto custom-scrollbar">
            <Accordion title="Message 1" defaultOpen={true}>
              <MessageEditor />
            </Accordion>
          </div>
        </div>
      }
      right={
        <div
          className={`${
            mobileView === "preview" ? "flex" : "hidden"
          } md:flex flex-col h-full bg-[#313338] w-full min-w-0`}
        >
          <MessagePreview />
        </div>
      }
    />
  </div>
</main>
```

#### 3.4.3 Mathematical Proportions Analysis:
1. **When `isSidebarOpen === false` (Default)**:
   - Sidebar width = 0.
   - Container width for `<SplitPane />` = 100% of the viewport width.
   - Left Pane (Editor) = 50% of viewport width.
   - Right Pane (Preview) = 50% of viewport width.
   - On a standard 1366px screen: Editor = 683px, Preview = 683px (ample room for 550px Discord message width + 130px padding).
   - Clean, true Discohook dual pane!
2. **When `isSidebarOpen === true`**:
   - Sidebar docks smoothly at `w-72` (288px).
   - Remaining viewport width is handed to `<SplitPane />`.
   - `<SplitPane />` preserves percentage-based ratio (0.5), so Editor and Preview remain perfectly balanced at 50/50 of the remaining width.
   - Divider dragging via pointer events continues to clamp between 25% and 75% without jitter.

---

### 3.5 Action Bar & Reset Consolidation

In `App.tsx`:
```tsx
const handleClearAll = () => {
  if (confirm("Are you sure you want to clear all message contents and reset?")) {
    useMessageStore.getState().reset();
    useActionStore.getState().reset();
    useTemplateStore.getState().detach();
  }
};
```
This ensures that clicking "Clear" in the Action Bar completely clears the stores AND detaches any active template, matching the behavior of "Start over" in `Header.tsx`.

---

## 4. Verification Matrix

| Verification Target | Expected Behavior | Verification Command / Check |
|---|---|---|
| 1. Default Workbench | Desktop loads in authentic 50/50 dual-pane mode without pinned 3rd pane | Visual inspection / DOM check: `isSidebarOpen === false` |
| 2. Sidebar Toggle | Clicking `PanelLeft` button in Header toggles `isSidebarOpen` smoothly | Clicking toggle opens/closes sidebar without layout jump |
| 3. Keyboard Shortcut | Pressing `Ctrl+B` or `Cmd+B` toggles sidebar | Keydown event triggers `toggleSidebar` |
| 4. Deduplicated Guild Select | Only 1 guild dropdown rendered (in Header) | Grep `<SearchableDiscordSelect type="guild"` returns 1 occurrence |
| 5. Deduplicated Settings/Staff | Only 1 set of Settings & Staff buttons/modals rendered | Check Header has buttons, Sidebar footer has none |
| 6. Collapsible Accordions | Palette and Layers sections can be folded in Sidebar | Verify accordions toggle with chevrons |
| 7. TypeScript Compilation | Monorepo compiles cleanly | `npm run typecheck --workspace client` (0 errors) |
| 8. Production Build | Vite production build succeeds | `npm run build --workspace client` (exit code 0) |
| 9. Unit & Stress Tests | Client and Monorepo test suites pass | `npm test` (all 288 tests pass) |

---

## 5. Worker M3 Step-by-Step Implementation Guide

1. **Step 1: Update `globalStore.ts`**:
   - Add `isSidebarOpen: boolean` (default: `false` or loaded from `localStorage`).
   - Add `setSidebarOpen: (open: boolean) => void`.
   - Add `toggleSidebar: () => void`.
2. **Step 2: Update `Header.tsx`**:
   - Import `PanelLeft, PanelLeftClose` from `lucide-react`.
   - Add toggle button to Header next to brand icon with active styling and tooltip.
3. **Step 3: Update `Sidebar.tsx`**:
   - Remove duplicate `<SearchableDiscordSelect type="guild" />`.
   - Remove duplicate Settings/Staff Access buttons, Docs link, and modal instances.
   - Add Header bar with title and `ChevronLeft` collapse button.
   - Wrap "Component Palette" and "Layers & Hierarchy" with collapsible accordions.
4. **Step 4: Update `App.tsx`**:
   - Read `isSidebarOpen` from `useGlobalStore`.
   - Add `Ctrl+B` / `Cmd+B` keyboard listener.
   - Update layout JSX: Sidebar collapses cleanly on desktop and acts as overlay drawer on mobile.
   - Update `handleClearAll` to include `useTemplateStore.getState().detach()`.
5. **Step 5: Add Unit Tests in `tests/layout_discohook.test.ts`**:
   - Assert `isSidebarOpen` defaults to false, toggles, and persists in localStorage.
6. **Step 6: Build & Test**:
   - Run typecheck, build, and test commands.
