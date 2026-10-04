# Milestone 3 (Iteration 2) Handoff: Sidebar Collapse & True Discohook Dual-Pane Proportions

## 1. Observation

1. **User Requirement & Explicit Override**:
   - `ORIGINAL_REQUEST.md:70-71`:
     ```markdown
     USER CORRECTION: "i dont want 3 pane layout but like discohook layout only". 
     Please ensure your UI layout perfectly mirrors Discohook.app's specific layout proportions and structure, rather than a generic 3-pane layout.
     ```

2. **Official Discohook Reference Implementation**:
   - Inspected `discohook_src/packages/site/app/routes/_index.tsx:953-965`:
     ```tsx
     <Header user={user} setShowHistoryModal={setShowHistory} />
     <div className={twJoin("h-[calc(100%_-_3rem)]", settings.forceDualPane ? "flex" : "md:flex")}>
       <div className={twMerge("py-4 h-full overflow-y-scroll", settings.forceDualPane ? "w-1/2" : twJoin("md:w-1/2", tab === "editor" ? "" : "hidden md:block"))} ref={editorRef}>
     ```
   - Inspected `discohook_src/packages/site/app/routes/_index.tsx:1610-1620`:
     ```tsx
       <div className={twMerge("h-full flex-col border-s-gray-400 dark:border-s-[#1E1F22]", settings.forceDualPane ? "flex w-1/2 border-s-2" : twJoin("md:w-1/2 md:border-s-2", tab === "preview" ? "flex" : "hidden md:flex"))} ref={previewRef}>
         <div className="overflow-y-scroll grow p-4 pb-8">
     ```
   - Inspected `discohook_src/packages/site/app/components/Drawer.tsx:24-41`:
     ```tsx
     <Dialog.Popup
       className={twJoin(
         "box-border fixed z-[31] translate-x-0 translate-y-0 top-0 left-0 rounded-r-xl",
         "w-96 md:w-1/3 max-w-[min(35rem,_calc(100vw_-_3rem))]",
         "h-screen max-h-screen overflow-y-auto",
         "bg-gray-50 text-black dark:bg-gray-800 dark:text-gray-50 shadow",
         "transition-all",
         "data-[starting-style]:-translate-x-full",
         "data-[ending-style]:-translate-x-full",
       )}
     >
     ```
   - Direct observation: In Discohook.app, the main workbench is strictly a 50/50 dual pane (`w-1/2` Editor, `w-1/2` Live Preview). There is **no pinned sidebar** on desktop. The drawer is an on-demand slide-over overlay triggered via the top Header.

3. **Defects in Hoho Manager Codebase**:
   - `hoho_manager/client/src/App.tsx:507-513`:
     ```tsx
     {/* Left Pane: Discohook Sidebar (Guild select, elements/layers, templates, settings/staff) */}
     <div
       className={`${
         mobileView === "sidebar" ? "flex" : "hidden"
       } md:flex h-full w-72 shrink-0 flex-col`}
     >
       <Sidebar />
     </div>
     ```
     `md:flex` permanently pins `Sidebar` at 288px (`w-72`), forcing a 3-pane layout on desktop and reducing Editor and Preview widths to ~490px.
   - Duplicate Server Selector:
     - `Header.tsx:130-138`: `<SearchableDiscordSelect type="guild" value={selectedGuildId || ""} ... />`
     - `Sidebar.tsx:30-41`: `<SearchableDiscordSelect type="guild" value={selectedGuildId || ""} ... />`
   - Duplicate Settings, Staff Access & Docs:
     - `Header.tsx:201-244`: Settings button, Staff Access button, and Docs link.
     - `Sidebar.tsx:142-170`: Duplicate Settings button, duplicate Staff Access button, duplicate Docs link, and redundant modal state instances (`<SettingsModal>` and `<Modal><AccessPanel /></Modal>`).
   - Duplicate Reset Actions:
     - `App.tsx:548-554`: "Clear" button calls `handleClearAll` (resets `messageStore` and `actionStore`, but omits `detachTemplate()`).
     - `Header.tsx:193-198`: "Start over" button calls `resetDocument` (resets `messageStore`, `actionStore`, and calls `detachTemplate()`).
   - Static Sections in Sidebar:
     - `Sidebar.tsx:71-86` renders Component Palette and Layers & Hierarchy inside static `<section>` tags without collapsible accordions.

4. **Monorepo Baseline Health**:
   - `npm run typecheck --workspace client`: Exit code 0 (0 errors).
   - `npm run build --workspace client`: Exit code 0 (Vite build successful in 2.06s).
   - `npm test --workspace client`: Exit code 0 (9 test files, 130 tests passed).

---

## 2. Logic Chain

1. **User Requirement & Discord Fidelity**:
   - The user explicitly commanded: *"i dont want 3 pane layout but like discohook layout only"*.
   - Reference code verification confirms Discohook is a 50/50 dual pane (Editor 50%, Live Preview 50%).
   - Discord messages require ~550px to render without premature column wrapping of embeds and action rows. When a 288px sidebar is permanently docked, a 1280px-1366px screen allocates under 500px to preview, breaking fidelity.

2. **Collapsible Architecture Reasoning**:
   - Introducing `isSidebarOpen: boolean` (defaulting to `false`) in `useGlobalStore` allows the desktop application to launch in the authentic 50/50 dual-pane mode requested by the user.
   - When collapsed (`isSidebarOpen === false`):
     - The sidebar container is `w-0 md:hidden`.
     - `<SplitPane />` occupies 100% of the screen width. With `initialRatio={0.5}`, the Editor is exactly 50% and the Live Preview is exactly 50%.
   - When opened (`isSidebarOpen === true`):
     - On desktop (`md:`), it docks alongside at `w-72` with smooth transitions (`transition-[width,transform] duration-200`).
     - On mobile (`< md`), it renders as an overlay slide-over drawer with a semi-transparent backdrop (`fixed inset-0 bg-black/60 backdrop-blur-sm z-30`), preventing screen squishing.
   - Putting `isSidebarOpen` in `useGlobalStore` enables multi-surface control:
     - Header toggle button (`PanelLeft` / `PanelLeftClose`)
     - Sidebar header collapse button (`ChevronLeft`)
     - Keyboard shortcut (`Ctrl+B` / `Cmd+B`)
     - Mobile drawer interactions

3. **Deduplication Reasoning**:
   - The top Header is sticky and always visible. Therefore, placing the single authoritative "Selected Server" dropdown, Settings button, Staff Access button, and Docs link in `Header.tsx` guarantees continuous access whether the sidebar is collapsed or expanded.
   - Removing them from `Sidebar.tsx` eliminates redundant state, duplicate API calls, and dual modal instances.

4. **Sidebar Accordion Reasoning**:
   - Replacing static `<section>` tags with collapsible accordions (`paletteOpen`, `layersOpen`) resolves Reviewer 1's gate failure point #5, allowing users to fold palette or hierarchy sections.

---

## 3. Caveats

- All findings and architectural proposals are strictly confined to `hoho_manager/client` (`App.tsx`, `Header.tsx`, `Sidebar.tsx`, `globalStore.ts`). No backend or bot changes are required.
- The unit test suite (`layout_discohook.test.ts`) currently tests headless stores and utilities. Worker M3 should add unit tests for `isSidebarOpen` in `globalStore.ts` and verify that the layout components mount cleanly.
- Defaulting `isSidebarOpen` to `false` directly satisfies the user correction for dual pane on launch; users who prefer the sidebar permanently open can toggle it, and the preference can be persisted in `localStorage`.

---

## 4. Conclusion

The solution to Reviewer 1's gate failure is clear and concrete:
1. **Add `isSidebarOpen: boolean` (default `false`) and toggle actions to `useGlobalStore`** with `localStorage` persistence.
2. **Add a `PanelLeft` toggle button in `Header.tsx`** with active highlight and tooltip.
3. **Refactor desktop layout in `App.tsx`**:
   - When collapsed, sidebar is hidden, giving `<SplitPane />` 100% width (50/50 Editor and Preview).
   - When expanded, sidebar smoothly docks at `w-72` on desktop and acts as overlay drawer on mobile.
   - Add `Ctrl+B` / `Cmd+B` keyboard shortcut.
4. **Deduplicate UI controls**:
   - Retain guild dropdown, Settings, Staff Access, and Docs in `Header.tsx`.
   - Remove duplicate guild dropdown, duplicate footer buttons, and duplicate modal instances from `Sidebar.tsx`.
   - Consolidate "Clear" in `App.tsx` with "Start over" in `Header.tsx` to call store resets and `useTemplateStore.getState().detach()`.
5. **Implement collapsible accordions in `Sidebar.tsx`** for Component Palette and Layers & Hierarchy.

---

## 5. Verification Method

To independently verify after Worker M3 implements changes:
1. **Typecheck**:
   ```pwsh
   npm run typecheck --workspace client
   ```
   Must output 0 TypeScript compilation errors.
2. **Production Build**:
   ```pwsh
   npm run build --workspace client
   ```
   Must produce production bundles in `dist/` without errors.
3. **Unit Tests**:
   ```pwsh
   npm test --workspace client
   ```
   All test files must pass.
4. **Monorepo Tests**:
   ```pwsh
   npm test
   ```
   All 288 tests monorepo-wide must pass.
5. **Layout Inspection**:
   - In browser at `http://localhost:5175/`:
     - App loads with Sidebar collapsed: Editor on left (50%), Preview on right (50%).
     - Clicking the Header `PanelLeft` button smoothly opens the Sidebar (`w-72`).
     - Pressing `Ctrl+B` collapses the Sidebar back to 50/50 dual pane.
     - Only ONE "Selected Server" dropdown is visible on screen.
     - Only ONE "Settings" button and ONE "Staff Access" button are visible on screen.
     - Inside Sidebar, "Component Palette" and "Layers & Hierarchy" can be folded/unfolded.
