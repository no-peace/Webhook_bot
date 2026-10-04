# Frontend Layout & UI Investigation Report

## 1. Observation

### 1.1 R1: Sidebar Split-Screen & Clipping Observations
- **File**: `hoho_manager/client/src/App.tsx`
  - Lines 500–507 (Backdrop):
    ```tsx
    {isSidebarOpen && (
      <div
        className="fixed inset-0 bg-black/60 z-30 md:hidden backdrop-blur-sm"
        onClick={() => setIsSidebarOpen(false)}
        aria-hidden="true"
      />
    )}
    ```
    *Observation*: The backdrop overlay is conditionally rendered with `md:hidden`. At viewports $\ge 768\text{px}$ (Tailwind's `md` breakpoint), the backdrop is hidden from the DOM layout.
  - Lines 510–525 (Sidebar Container):
    ```tsx
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
    ```
    *Observation*: When `isSidebarOpen` is `true`, on viewports $\ge 768\text{px}$, the classes `md:static md:z-auto w-72 flex translate-x-0` apply. The sidebar is docked directly into the main flex row, consuming 288px of horizontal width.
  - Line 527–555 (SplitPane Container):
    ```tsx
    <div className={`${mobileView === "sidebar" ? "hidden" : "flex"} md:flex flex-1 min-w-0 h-full`}>
      <SplitPane initialRatio={0.5} ... />
    </div>
    ```
    *Observation*: The remaining viewport width is divided 50/50 between Editor and Preview. On an 800px–1100px split-screen laptop window, subtracting 288px leaves only 512px–812px total, allocating only 256px–406px per pane. Discord message components, embed cards, action row buttons, and header inputs require at least 450px–500px, causing severe horizontal clipping and wrapping.
  - **File**: `hoho_manager/client/src/store/globalStore.ts`
    - Lines 23–41:
      ```ts
      const loadInitialState = (): { selectedGuildId: string | null; isSidebarOpen: boolean } => {
        try {
          if (typeof localStorage !== "undefined") {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (raw) {
              const parsed = JSON.parse(raw);
              if (parsed && typeof parsed === "object") {
                return {
                  selectedGuildId: typeof parsed.selectedGuildId === "string" ? parsed.selectedGuildId : null,
                  isSidebarOpen: Boolean(parsed.isSidebarOpen),
                };
              }
            }
          }
        } catch { }
        return { selectedGuildId: null, isSidebarOpen: false };
      };
      ```
      *Observation*: `isSidebarOpen` restores directly from `localStorage.getItem("hoho_global_state")`. If opened previously on a desktop monitor, it opens automatically on split-screen or narrow laptop screens. There is no viewport width check (`window.innerWidth <= 1100`).
  - **Reference**: `discohook_src/packages/site/app/components/Drawer.tsx`
    - Lines 24–41:
      ```tsx
      <Dialog.Popup
        className={twJoin(
          "box-border fixed z-[31] translate-x-0 translate-y-0 top-0",
          props.anchor === "left" ? "left-0 rounded-r-xl" : ...,
          "w-96 md:w-1/3 max-w-[min(35rem,_calc(100vw_-_3rem))]",
          "h-screen max-h-screen overflow-y-auto",
          "bg-gray-50 text-black dark:bg-gray-800 dark:text-gray-50 shadow",
          "transition-all",
          "data-[starting-style]:-translate-x-full",
          "data-[ending-style]:-translate-x-full",
        )}
      >
      ```
      *Observation*: Discohook implements the sidebar as an off-canvas overlay `Drawer` with a `DialogBackdrop`. It is never a static flex child inside the editor row.

---

### 1.2 R2: Classic / Components V2 Mode Toggle Observations
- **File**: `hoho_manager/client/src/components/layout/Header.tsx`
  - Lines 25–51 (`ModeToggle`):
    ```tsx
    const ModeToggle: React.FC = () => {
      const mode = useMessageStore((state) => state.mode);
      const setMode = useMessageStore((state) => state.setMode);
      return (
        <div className="flex items-center rounded-lg bg-[#1e1f22] p-0.5 border border-[#111214]" role="group" aria-label="Editor mode">
          {[
            { id: EDITOR_MODES.CLASSIC, label: "Classic" },
            { id: EDITOR_MODES.V2, label: "Components V2" },
          ].map((option) => (
            <button
              key={option.id}
              type="button"
              aria-pressed={mode === option.id}
              onClick={() => setMode(option.id)}
              className={...}
            >
              {option.label}
            </button>
          ))}
        </div>
      );
    };
    ```
    *Observation*: `ModeToggle` invokes `setMode(option.id)`, updating `useMessageStore.getState().mode`.
- **File**: `hoho_manager/client/src/components/editor/MessageEditor.tsx`
  - Lines 18–127:
    ```tsx
    export const MessageEditor = () => {
      const { data, problems } = useMessage();
      const setField = useMessageStore((state) => state.setField);
      const addEmbed = useMessageStore((state) => state.addEmbed);
      const [identityOpen, setIdentityOpen] = useState(false);

      return (
        <div className="space-y-3">
          {/* Problems */}
          {/* Section: Message Text Content (always rendered) */}
          {/* Section: Collapsible Identity (always rendered) */}
          {/* Section: Embeds (always rendered) */}
          {/* Section: DiscohookComponentsEditor (always rendered) */}
          <section className="pt-2">
            <DiscohookComponentsEditor />
          </section>
        </div>
      );
    };
    ```
    *Observation*: `MessageEditor.tsx` does NOT import, subscribe to, or check `mode`. It unconditionally renders both the Embeds section (Classic) and `<DiscohookComponentsEditor />` (Components V2) simultaneously. Clicking "Classic" or "Components V2" alters Zustand state, but `MessageEditor.tsx` produces the exact same DOM tree.
- **Reference**: `discohook_src/packages/site/app/components/editor/MessageEditor.client.tsx`
  - Lines 703–707:
    ```tsx
    {isComponentsV2(message.data) ? (
      <ComponentMessageEditor {...childProps} />
    ) : (
      <StandardMessageEditor {...childProps} />
    )}
    ```
    *Observation*: Discohook cleanly switches the entire editor subtree between `StandardMessageEditor` (content text + embeds) and `ComponentMessageEditor` (Components V2 builder).

---

### 1.3 R3: Member/User Search Bug Observations
- **File**: `hoho_manager/client/src/components/ui/SearchableDiscordSelect.tsx`
  - Lines 52–67:
    ```tsx
    useEffect(() => {
      if (type === "member" && open && guildId && search.length >= 2) {
        const timeout = setTimeout(async () => {
          try {
            const res = await api.discord.searchMembers(guildId, search);
            setMemberResults(
              res.members.map((m) => ({
                id: m.user.id,
                name: m.nick || m.user.username,
              }))
            );
          } catch {
            // ignore
          }
        }, 500);
        return () => clearTimeout(timeout);
      }
    }, [search, type, open, guildId]);
    ```
- **File**: `hoho_manager/server/src/services/discordService.ts`
  - Lines 366–386:
    ```ts
    export const searchGuildMembers = async (
      guildId: string,
      query: string,
      profileId: number | string | null = null,
    ): Promise<DiscordMemberSummary[]> => {
      const pid = profileId != null ? Number(profileId) : null;
      const token = await resolveBotToken(pid);
      const rawMembers = await apiRequest<any[]>(
        "GET",
        `/guilds/${encodeURIComponent(guildId)}/members/search?query=${encodeURIComponent(query)}&limit=25`,
        { token },
      );
      if (!rawMembers) return [];
      return rawMembers.map((m) => ({
        id: m.user?.id ?? m.id,
        username: m.user?.username ?? m.username ?? "",
        global_name: m.user?.global_name ?? null,
        nickname: m.nick ?? null,
        avatar: m.user?.avatar ?? m.avatar ?? null,
      }));
    };
    ```
  - `hoho_manager/server/src/routes/discord.ts:133-136`:
    ```ts
    const members = await discord.searchGuildMembers(guildId, query, profileId);
    return res.json({ members });
    ```
  *Observation*: The backend returns `members` as an array of flat objects: `{ id, username, global_name, nickname, avatar }`. There is NO nested `m.user` property. In `SearchableDiscordSelect.tsx:58`, evaluating `m.user.id` throws an uncaught `TypeError: Cannot read properties of undefined (reading 'id')`. The `catch` block silently catches and ignores the exception, leaving `memberResults` empty (`[]`). Consequently, member searches return 0 results regardless of query.

---

### 1.4 R4: Discohook Exact Layout Discrepancies
- **Header Layout Discrepancies**:
  - In `discohook_src/packages/site/app/components/Header.tsx:76–385`:
    - Height: `h-12` (48px), `sticky top-0 z-20`, `bg-[#1E1F22]`.
    - Left: Logo + Drawer toggle button (or user avatar/login).
    - Center: Settings button, History modal button, Help modal button.
    - Right: User avatar or Staff/Login button.
  - In `hoho_manager/client/src/components/layout/Header.tsx:109–246`:
    - Contains 11 distinct items across a single row: Toggle button, Sparkles logo, "HoHo Manager", ModeToggle, SearchableDiscordSelect (Guild), Template Name input, Save button, Load button, Raw JSON button, Import JSON button, Export JSON button, Settings button, Staff Access button, Docs link.
    - Clutters the interface and causes horizontal overflow/wrapping on screens $< 1300\text{px}$.
- **Workspace Layout Discrepancies**:
  - In Discohook (`discohook_src/packages/site/app/routes/_index.tsx:953–965` & `1610–1620`):
    - Main container: `h-[calc(100%_-_3rem)] md:flex`.
    - Left: `w-1/2` Editor (`py-4 h-full overflow-y-scroll`).
    - Right: `w-1/2` Live Preview (`h-full flex-col md:w-1/2 md:border-s-2 border-s-[#1E1F22]`).
    - The sidebar is rendered as an off-canvas `Drawer`, taking 0 horizontal space from the workspace.
  - In `hoho_manager/client/src/App.tsx:510–540`:
    - When `isSidebarOpen` is true on desktop, the sidebar is rendered inline (`md:static w-72`), reducing editor/preview space to 50% of the remainder.
    - Duplicate template controls: `App.tsx` has `BackupsModal` (with Save template, Import JSON, Export JSON, and list of templates), while `Header.tsx` independently has Save, Load, Import JSON, Export JSON, and Raw JSON editor.

---

## 2. Logic Chain

1. **R1 Sidebar Split-Screen Bug**:
   - *Premise 1*: `App.tsx:512` sets `md:static md:z-auto` and `w-72` when `isSidebarOpen` is true.
   - *Premise 2*: Tailwind `md` triggers at $768\text{px}$. At $768\text{px} \le \text{viewport} \le 1100\text{px}$, the sidebar occupies 288px fixed width in the main flex container.
   - *Premise 3*: `App.tsx:503` sets `md:hidden` on the backdrop, disabling the backdrop overlay on all viewports $\ge 768\text{px}$.
   - *Premise 4*: `globalStore.ts:32` restores `isSidebarOpen` directly from `localStorage` without evaluating `window.innerWidth`.
   - *Conclusion*: On split-screen or narrow windows ($\le 1100\text{px}$), the sidebar opens by default, steals 288px from the workspace, cannot be closed via clicking outside, and squashes the Editor + Preview panes, clipping content.
   - *Required Fix*: Convert the sidebar into an off-canvas overlay `Drawer` across all viewports (`fixed inset-y-0 left-0 z-50`), remove `md:static` and `md:hidden` on the backdrop, add an Escape key listener, and default `isSidebarOpen` to `false` when `window.innerWidth <= 1100`.

2. **R2 Classic / Components V2 Mode Toggle Bug**:
   - *Premise 1*: `Header.tsx:39` executes `setMode(option.id)`, updating `useMessageStore.getState().mode`.
   - *Premise 2*: `MessageEditor.tsx` renders content text (lines 42–49), embeds (lines 91–119), and components (lines 122–124) without checking `useMessageStore((state) => state.mode)`.
   - *Conclusion*: Mode switching changes store state but has 0 effect on UI rendering, appearing broken to the user.
   - *Required Fix*: Wire `mode` in `MessageEditor.tsx`. In Classic mode (`mode === "classic"`), render standard text content and the embed editor. In Components V2 mode (`mode === "v2"`), render the component builder (`DiscohookComponentsEditor`), action rows, buttons, select menus, and flow bindings. Render the mode toggle prominently at the top of the editor workspace as well as in the header.

3. **R3 Member Search Bug**:
   - *Premise 1*: `discordService.ts:379–385` returns `members` as flat objects `{ id, username, global_name, nickname, avatar }`.
   - *Premise 2*: `SearchableDiscordSelect.tsx:58` maps `m.user.id`, triggering `TypeError: Cannot read properties of undefined (reading 'id')`.
   - *Premise 3*: The error is swallowed in `catch {}`, resulting in an empty array `[]`.
   - *Conclusion*: Member searches always fail and show no results.
   - *Required Fix*: Update mapper in `SearchableDiscordSelect.tsx` to `m.id || m.user?.id` and name to `m.nickname || m.global_name || m.username || m.id`. Correct TypeScript definition in `api/client.ts`. Support manual snowflake fallback when no guild is selected.

4. **R4 Layout Parity & Deduplication**:
   - *Premise 1*: Discohook isolates toolbar utilities into a 3-part header (Logo/Drawer on left, Settings/History/Help in center, Account on right).
   - *Premise 2*: In HoHo Manager, template saving, loading, JSON import, and export are duplicated in both `Header.tsx` and `App.tsx`'s Action Bar (`BackupsModal`).
   - *Conclusion*: Header clutter degrades UX and splits user attention.
   - *Required Fix*: Consolidate template actions into the Action Bar's "Backups" modal, clean the Header to match Discohook's structure, and ensure the main body is an undisturbed 50/50 Editor/Preview split.

5. **R5 Professional Polish (Applied Skills)**:
   - *Premise 1*: `web-design-guidelines` requires accessible icon buttons (`aria-label`), visible focus states (`focus-visible:ring-2`), non-breaking characters (`…`), tabular numerals (`tabular-nums`), and keyboard dismissal (`Escape`).
   - *Premise 2*: `frontend-design` and `tailwind-design-system` prescribe Discord surface hierarchy (`#1E1F22`, `#2B2D31`, `#313338`) and explicit CSS transition targets (`transition-transform`, `transition-opacity`).
   - *Conclusion*: Polish must be applied across Drawer, Header, Editor, and Preview controls.

---

## 3. Caveats

- **Backend Intents**: The bot lacks privileged Server Members Intent, Presence Intent, and Message Content Intent. All member search solutions must rely strictly on `GET /guilds/{guildId}/members/search?query=...` via the Discord REST API.
- **Classic Action Rows**: Discord API allows classic messages to include Action Rows (up to 5 buttons or 1 select menu). In Classic mode, action rows can optionally be supported beneath embeds, while Components V2 mode provides the complete top-level component architecture (`MessageFlags.IsComponentsV2`).
- **Storage Migration**: Existing users may have `hoho_global_state` in `localStorage` with `isSidebarOpen: true`. The store initialization must explicitly guard against wide-screen state leaking into narrow viewport windows.

---

## 4. Conclusion

The frontend issues stem from three distinct defects:
1. **R1**: An invalid responsive pattern in `App.tsx` where the sidebar is statically docked at `md` ($\ge 768\text{px}$) rather than behaving as an off-canvas overlay `Drawer`, combined with a suppressed backdrop (`md:hidden`) and unconstrained `localStorage` restoration.
2. **R2**: A disconnected UI component where `MessageEditor.tsx` completely ignores Zustand's `mode` state, failing to toggle between Classic (content + embeds) and Components V2 (Action Rows + component builder).
3. **R3**: A client-server schema mismatch in `SearchableDiscordSelect.tsx` where flat member records are accessed as nested `m.user.id`, causing silent runtime errors.
4. **R4 & R5**: Header clutter and duplicate template controls that deviate from Discohook's clean 50/50 dual pane and professional design standards.

### Concrete Implementation Blueprint:

#### 1. Drawer Conversion (`App.tsx` & `globalStore.ts`)
- In `globalStore.ts`:
  ```ts
  const isNarrow = typeof window !== "undefined" && window.innerWidth <= 1100;
  const initialOpen = isNarrow ? false : Boolean(parsed.isSidebarOpen);
  ```
- In `App.tsx`:
  - Render backdrop whenever `isSidebarOpen` is true without `md:hidden`:
    ```tsx
    {isSidebarOpen && (
      <div
        className="fixed inset-0 bg-black/60 z-40 backdrop-blur-sm transition-opacity duration-200"
        onClick={() => setIsSidebarOpen(false)}
        aria-hidden="true"
      />
    )}
    ```
  - Render Sidebar wrapper as an overlay Drawer across all viewports:
    ```tsx
    <div
      className={`
        fixed inset-y-0 left-0 z-50 h-full w-80 max-w-[calc(100vw-3rem)]
        bg-[#2b2d31] border-r border-[#1e1f22] shadow-2xl
        transition-transform duration-200 ease-in-out flex flex-col
        ${isSidebarOpen ? "translate-x-0" : "-translate-x-full"}
      `}
      role="dialog"
      aria-modal="true"
      aria-label="Toolbox Drawer"
    >
      <Sidebar />
    </div>
    ```
  - Listen for `Escape` key:
    ```tsx
    useEffect(() => {
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === "Escape" && isSidebarOpen) {
          setIsSidebarOpen(false);
        }
      };
      window.addEventListener("keydown", handleKeyDown);
      return () => window.removeEventListener("keydown", handleKeyDown);
    }, [isSidebarOpen, setIsSidebarOpen]);
    ```

#### 2. Mode Switching in `MessageEditor.tsx`
- In `MessageEditor.tsx`:
  ```tsx
  export const MessageEditor = () => {
    const { data, problems } = useMessage();
    const mode = useMessageStore((state) => state.mode);
    const setMode = useMessageStore((state) => state.setMode);
    const setField = useMessageStore((state) => state.setField);
    const addEmbed = useMessageStore((state) => state.addEmbed);
    const [identityOpen, setIdentityOpen] = useState(false);

    return (
      <div className="space-y-3">
        {/* Editor Mode Tabs at Top of Editor */}
        <div className="flex rounded-lg bg-[#1e1f22] p-1 border border-[#111214]" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={mode === EDITOR_MODES.CLASSIC}
            onClick={() => setMode(EDITOR_MODES.CLASSIC)}
            className={`flex-1 py-1.5 text-xs font-semibold rounded transition-colors ${
              mode === EDITOR_MODES.CLASSIC
                ? "bg-[#5865f2] text-white shadow-sm"
                : "text-[#949ba4] hover:text-[#dbdee1]"
            }`}
          >
            Classic Mode
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === EDITOR_MODES.V2}
            onClick={() => setMode(EDITOR_MODES.V2)}
            className={`flex-1 py-1.5 text-xs font-semibold rounded transition-colors ${
              mode === EDITOR_MODES.V2
                ? "bg-[#5865f2] text-white shadow-sm"
                : "text-[#949ba4] hover:text-[#dbdee1]"
            }`}
          >
            Components V2 Mode
          </button>
        </div>

        {/* Problems Display */}
        {problems.length > 0 && (...)}

        {/* Mode-Specific Rendering */}
        {mode === EDITOR_MODES.CLASSIC ? (
          <>
            {/* Standard Message Text Content */}
            <section className="bg-[#232428] rounded border border-[#1e1f22] p-2.5">
              <TextArea label="Content" limit={Limits.content} rows={4} ... />
            </section>

            {/* Message Identity */}
            <section className="bg-[#232428] rounded border border-[#1e1f22]">...</section>

            {/* Embeds Editor */}
            <section className="space-y-2">...</section>
          </>
        ) : (
          <>
            {/* Components V2 Builder */}
            <section className="bg-[#232428] rounded border border-[#1e1f22]">...</section>
            <section className="pt-1">
              <DiscohookComponentsEditor />
            </section>
          </>
        )}
      </div>
    );
  };
  ```

#### 3. Member Search Fix in `SearchableDiscordSelect.tsx`
- In `SearchableDiscordSelect.tsx:57–61`:
  ```ts
  const res = await api.discord.searchMembers(guildId, search);
  setMemberResults(
    (res.members || []).map((m: any) => ({
      id: String(m.id || m.user?.id || ""),
      name: String(m.nickname || m.global_name || m.username || m.user?.username || m.id || "Unknown"),
    }))
  );
  ```
- In `api/client.ts:240–244`:
  ```ts
  searchMembers: (guildId: string, query: string, profileId?: number) =>
    request<{
      members: Array<{
        id: string;
        username: string;
        global_name: string | null;
        nickname: string | null;
        avatar: string | null;
      }>;
    }>(
      `/api/discord/guilds/${guildId}/members/search?query=${encodeURIComponent(query)}${profileId ? `&profileId=${profileId}` : ""}`
    ),
  ```

#### 4. Header & Workspace Consolidation
- Clean `Header.tsx` to mirror Discohook:
  - Left: Logo + Drawer button (`PanelLeft`) + "HoHo Manager".
  - Center: Server (Guild) Select dropdown + Settings modal button + Docs link.
  - Right: Staff Login / Staff Access status badge.
- Delegate template management to the Action Bar's "Backups" button (`BackupsModal`), eliminating duplicate save/export bars from the top header.
- Main workspace remains a dedicated 50/50 dual pane (`SplitPane` Editor | Preview) unconstrained by any static sidebar.

---

## 5. Verification Method

To verify these fixes independently:

1. **Verify TypeScript Build**:
   ```bash
   cd hoho_manager/client
   npm run build
   ```
   *Expected Result*: Exits with code 0, 0 TypeScript errors.

2. **Run Unit & Adversarial Test Suite**:
   ```bash
   cd hoho_manager/client
   npm test
   ```
   *Expected Result*: All 132 tests in the suite pass.

3. **Verify Narrow Viewport (Split-Screen) Behavior**:
   - In browser at `http://localhost:5173/`, resize window to $\le 1100\text{px}$ (e.g. 960px).
   - Ensure the sidebar defaults to CLOSED.
   - Verify the Editor + Live Preview panes take 100% of the viewport with no horizontal scrollbar or clipped inputs.
   - Press `Ctrl+B` or click the sidebar toggle button: verify the sidebar smoothly slides in as an overlay Drawer over the content with a darkened backdrop.
   - Click the backdrop or press `Escape`: verify the drawer immediately closes.

4. **Verify Mode Switching**:
   - Click "Classic": verify only the standard text content and Embeds editor appear; verify `DiscohookComponentsEditor` is hidden.
   - Click "Components V2": verify the interactive component builder (Action Rows, Buttons, Select Menus) appears.
   - Switch back and forth: verify state in both modes remains intact without data loss.

5. **Verify Member Search**:
   - Open Staff Access or Head Admin Settings.
   - Select a server.
   - Search for a member by username in "Search or enter user IDs...": verify matching members are returned with their usernames/nicknames and snowflake IDs.
   - Enter a 17-20 digit snowflake manually: verify "Use ID: {snowflake}" appears and successfully adds the ID.
