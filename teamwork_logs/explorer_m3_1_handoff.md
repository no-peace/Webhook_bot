# Milestone 3 Handoff: Discohook 3-Pane Structure Refactor (Explorer 1)

## 1. Observation

1. **Current 2-Pane Layout in `App.tsx`**:
   - `hoho_manager/client/src/App.tsx:498-680`: Layout uses `<SplitPane initialRatio={0.5} left={...} right={...} />`.
   - Left side contains Editor workspace (`sm:flex flex-col h-full bg-[#2b2d31] border-r border-[#1e1f22] w-full min-w-0`).
   - Right side contains `<MessagePreview />` (`sm:flex flex-col h-full bg-[#313338] w-full min-w-0`).
   - `Sidebar.tsx` is **not imported and not mounted** in `App.tsx` (verified via `grep_search` across `hoho_manager/client/src`).

2. **Duplicate Editor Mode Toggles**:
   - `hoho_manager/client/src/components/layout/Header.tsx:26-52`: `<ModeToggle />` rendered at line 128 in top header.
   - `hoho_manager/client/src/App.tsx:604-632`: Duplicate "Editor Mode" bar rendered between Action Bar and Editor Workspace:
     ```tsx
     <div className="px-3 py-2 bg-[#232428] border-b border-[#1e1f22] flex items-center justify-between">
       <span className="text-[11px] font-bold uppercase tracking-wider text-[#949ba4]">Editor Mode</span>
       <div className="flex bg-[#1e1f22] p-0.5 rounded border border-[#111214]">
         <button onClick={() => setMode(EDITOR_MODES.CLASSIC)} ...>Classic</button>
         <button onClick={() => setMode(EDITOR_MODES.V2)} ...>Components V2</button>
       </div>
     </div>
     ```

3. **Triple Duplicate of ComponentPalette and LayersPanel**:
   - `hoho_manager/client/src/components/layout/Sidebar.tsx:52, 55`: In tab 'build'.
   - `hoho_manager/client/src/App.tsx:656, 663`: In Accordion "Components (Buttons, Menus & Layers)".
   - `hoho_manager/client/src/components/editor/MessageEditor.tsx:104, 106`: Inside `MessageEditor` when `isV2` is active.

4. **Orphaned Action Rows Builder Component**:
   - `hoho_manager/client/src/components/editor/DiscohookComponentsEditor.tsx:18-228`: Contains complete visual Action Row and button builder (5-row limit, 5-items per row limit, style pills, drag/move, duplicate, delete, click-to-edit).
   - This component is not imported anywhere in `client/src` (confirmed via `grep_search`).

5. **Static Bot Icon in MessagePreview**:
   - `hoho_manager/client/src/components/preview/MessagePreview.tsx:61-69`:
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
   - When `data.avatar_url` is not set, it falls back to `<Bot size={18} className="text-white" />`.
   - `App.tsx:406-420` auto-fetches bot identity via `api.discord.identity()` and caches it to `localStorage.getItem("bot_identity_cache")`, but `MessagePreview` never reads it, nor is it stored in `useGlobalStore`.

6. **Outdated Sidebar Contents and Mismatched Theme**:
   - `hoho_manager/client/src/components/layout/Sidebar.tsx:15, 73-75`: Contains `bg-white dark:bg-gray-900`, `border-gray-200 dark:border-[#404248]`, and renders `<ProfilesPanel />`.
   - Per Milestone 2 / R3, Bot & Webhook profile management was moved to `SettingsModal.tsx`.

7. **Test Suite Baseline**:
   - Test command: `npm test` in `hoho_manager/client` passed 7 test files, 61 tests (`tests/layout_discohook.test.ts` passed 15 tests).
   - Typecheck command: `npm run typecheck` passed with code 0 (0 errors).

---

## 2. Logic Chain

1. **Premise 1 (R1 & F1)**: The requirement mandates a 3-pane structure: Left Sidebar (Guild selector, navigation, palette/layers/templates, settings/staff), Center Editor (content, embeds, Action Rows), Right Preview (unified live preview).
   - Observation 1 shows that `App.tsx` only renders a 2-pane split and leaves `Sidebar.tsx` completely detached.
   - Therefore, `App.tsx` must be restructured to mount `<Sidebar />` as a fixed/collapsible Left Pane (`w-72 shrink-0`), with `<SplitPane />` hosting the Center Editor and Right Preview.

2. **Premise 2 (R1 & F2)**: Duplicate UI elements must be consolidated into a single unified workflow.
   - Observation 2 shows the Editor Mode toggle rendered twice (in Header and in App). The toggle in `App.tsx` takes up vertical space and should be removed, leaving the single toggle in `Header.tsx`.
   - Observation 3 shows `ComponentPalette` and `LayersPanel` duplicated across three places.
   - Observation 4 shows `DiscohookComponentsEditor` is orphaned.
   - Therefore, `ComponentPalette` and `LayersPanel` should reside solely in the Left Sidebar's Elements tab. The Center Editor should replace the duplicate palette accordion with `<DiscohookComponentsEditor />`, giving users the visual Action Row builder requested by F4.

3. **Premise 3 (R1 & F3)**: Live Preview must load the bot's profile picture and display real bot identity.
   - Observation 5 shows `MessagePreview` only checks `data.avatar_url`, ignoring the auto-fetched bot identity.
   - Therefore, `botIdentity` should be stored in `useGlobalStore` and cached in `localStorage`. `MessagePreview` will resolve `effectiveAvatar = data.avatar_url || botIdentity?.avatar || cachedBot?.avatar || null`, displaying the bot's avatar and username.

4. **Premise 4 (R3 & Clean Theme)**: Sidebar must adhere to Discord dark theme and exclude obsolete profile management.
   - Observation 6 shows `Sidebar.tsx` has light-mode classes and an obsolete `ProfilesPanel`.
   - Therefore, `Sidebar.tsx` must be refactored to Discord dark theme (`#2b2d31`, `#1e1f22`), top Guild selector (`SearchableDiscordSelect`), Elements and Templates navigation tabs, and footer triggers for Settings, Staff Access, and Docs.

---

## 3. Caveats

- **Tablet / Mobile Breakpoints**: Screens narrower than 640px currently use a two-button mobile switcher ("Editor" vs "Preview"). On small screens, the Left Sidebar should be accessible via a 3-way toggle ("Sidebar" | "Editor" | "Preview") or a sidebar toggle drawer button so mobile users can still access templates and settings.
- **Component V2 Flag**: Discord's Component V2 format requires `flags: 32768 (IsComponentsV2)`. When users build messages in Classic mode, buttons and select menus are nested under Action Rows (`type: 1`). `DiscohookComponentsEditor` correctly targets `ActionRow` (`ComponentType.ActionRow`), ensuring full compatibility with both classic webhooks and Component V2.
- No other areas outside `hoho_manager/client/src/` require modification.

---

## 4. Conclusion

The client codebase is well-structured and already possesses the core components needed (`DiscohookComponentsEditor.tsx`, `SplitPane.tsx`, `SearchableDiscordSelect.tsx`, `SettingsModal.tsx`, `AccessPanel.tsx`). The refactor to the 3-pane Discohook layout requires adapting the existing components into their intended slots without tearing out the underlying state engine.

The Worker should apply 5 coordinated modifications:
1. `hoho_manager/client/src/store/globalStore.ts`: Add `botIdentity` state & setter.
2. `hoho_manager/client/src/components/preview/MessagePreview.tsx`: Use live bot avatar and unified content/embeds rendering.
3. `hoho_manager/client/src/components/layout/Sidebar.tsx`: Rebuild as Discord dark-theme Left Pane with Guild selector, Elements tab (Palette + Layers), Templates tab, and Settings/Staff footer.
4. `hoho_manager/client/src/components/editor/MessageEditor.tsx`: Remove lines 96-109 (duplicate palette/layers).
5. `hoho_manager/client/src/App.tsx`: Mount `Sidebar` in 3-pane layout, remove duplicate Mode toggle (lines 604-632), mount `DiscohookComponentsEditor` in the Center Editor accordion, and update `setBotIdentity` on load.

---

## 5. Verification Method

### Concrete Verification Commands
From `hoho_manager/client`:
1. **Vitest Test Suite**:
   ```pwsh
   npm test
   ```
   *Expected*: All 7 test files and 61 tests pass (including `tests/layout_discohook.test.ts`).
2. **TypeScript Compilation**:
   ```pwsh
   npm run typecheck
   ```
   *Expected*: Exits with code 0 and 0 type errors.
3. **Vite Production Build**:
   ```pwsh
   npm run build
   ```
   *Expected*: Exits with code 0 and builds `dist/` bundle without errors.

### Files to Inspect Post-Implementation
- `hoho_manager/client/src/App.tsx`: Confirm 3 panes are rendered (`<Sidebar />` as Left Pane, `<SplitPane />` housing Center Editor and Right Preview).
- `hoho_manager/client/src/components/layout/Sidebar.tsx`: Confirm top Guild select, Elements & Templates tabs, and footer Settings/Staff buttons.
- `hoho_manager/client/src/components/editor/DiscohookComponentsEditor.tsx`: Confirm it is rendered in Center Editor.
- `hoho_manager/client/src/components/preview/MessagePreview.tsx`: Confirm bot profile picture loads from auto-fetched bot identity.

### Invalidation Conditions
- If `npm test` fails any of the 15 tests in `layout_discohook.test.ts`.
- If `typecheck` produces any errors.
- If `Sidebar.tsx` is left unmounted in `App.tsx`.
- If `ComponentPalette` remains in `MessageEditor.tsx`.
