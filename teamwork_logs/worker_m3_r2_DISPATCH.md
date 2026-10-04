## 2026-10-03T12:58:37Z
You are a Worker subagent for Milestone 3 (Iteration 2) of the Hoho Manager project.
Your assigned role is: Worker M3 (Discohook Dual-Pane & UI Deduplication).
Your working directory is: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\worker_m3_r2

MANDATORY FIRST STEP:
Read C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\ORIGINAL_REQUEST.md
Pay special attention to user correction: "i dont want 3 pane layout but like discohook layout only"
Read C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\PROJECT.md
Read the Gate failure report from Reviewer 1: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\reviewer_m3_1\handoff.md
Read the 3 Explorer handoffs for Iteration 2:
- C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m3_r2_1\handoff.md
- C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m3_r2_2\handoff.md
- C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m3_r2_3\handoff.md

FILE OWNERSHIP:
You have exclusive write access to:
- `hoho_manager/client/src/**`
- `hoho_manager/client/tests/**`

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

IMPLEMENTATION TASKS:
1. `hoho_manager/client/src/store/globalStore.ts`:
   - Add `isSidebarOpen: boolean` (default `false`) with `localStorage` persistence.
   - Add actions: `setIsSidebarOpen: (open: boolean) => void`, `toggleSidebar: () => void`.

2. `hoho_manager/client/src/components/layout/Header.tsx`:
   - Add a `PanelLeft` toggle button (with active state styling and tooltip "Toggle Sidebar (Ctrl+B)") that calls `toggleSidebar()`.
   - Ensure the authoritative Server (Guild) Selector remains here: `<SearchableDiscordSelect type="guild" value={selectedGuildId || ""} ... />`.
   - Ensure authoritative Settings modal trigger, Staff Access modal trigger, and Documentation link remain here.
   - Remove "Start over" button (deduplicated; unified into the Editor Action Bar).

3. `hoho_manager/client/App.tsx`:
   - Refactor desktop layout to authentic Discohook 50/50 dual pane:
     - When `!isSidebarOpen`: the desktop sidebar is cleanly collapsed/hidden. The `<SplitPane />` with Editor (50%) and Live Discord Preview (50%) expands to occupy 100% of the screen width!
     - When `isSidebarOpen`: on desktop (`md:`), the sidebar renders docked alongside at `w-72` with smooth transitions (`transition-[width] duration-200`). On mobile, it renders as an overlay drawer with backdrop.
     - Add `Ctrl+B` / `Cmd+B` keyboard shortcut listener to toggle sidebar.
   - In Editor Action Bar (lines 548-554): ensure "Clear" button resets document and calls `useTemplateStore.getState().detach()`.
   - Harmonize `BackupsModal` to consume `templateStore` / `useTemplates` so there is no conflicting disjoint backup system.

4. `hoho_manager/client/src/components/layout/Sidebar.tsx`:
   - Remove duplicate Server Selector (`SearchableDiscordSelect type="guild"`).
   - Remove duplicate Settings button, Staff Access button, and Docs link.
   - Remove duplicate modal states (`isSettingsOpen`, `isStaffOpen`) and duplicate `<SettingsModal>` / `<AccessPanel>` elements.
   - Add a header collapse button (`ChevronLeft` or `PanelLeftClose`) that calls `toggleSidebar()` / `setIsSidebarOpen(false)`.
   - Replace static `<section>` tags with interactive collapsible accordions (`CollapsibleSection` or similar) with chevron toggles for "Component Palette" and "Layers & Hierarchy" so users can fold/unfold either section.

5. `hoho_manager/client/src/components/preview/MessagePreview.tsx`:
   - Harden avatar snowflake calculation:
     `const defaultDiscordAvatar = botIdentity?.id && /^\d+$/.test(botIdentity.id) ? \`https://cdn.discordapp.com/embed/avatars/\${(BigInt(botIdentity.id) >> 22n) % 6n}.png\` : null;`
     with try/catch fallback so malformed IDs safely evaluate to null without throwing SyntaxError.

6. `hoho_manager/client/tests/adversarial_layout_state_avatar.test.ts`:
   - Update Test 6 (around line 664) from `.toThrow(SyntaxError)` to `.not.toThrow()` and assert graceful fallback markup without avatar crash (as detailed in `explorer_m3_r2_3/handoff.md`).

7. Add unit tests in `hoho_manager/client/tests/layout_discohook.test.ts`:
   - Test `isSidebarOpen` state, toggling, and persistence in `globalStore`.
   - Test hardened snowflake regex guard for non-numeric IDs.

8. VERIFICATION COMMANDS (Run and document all):
   - `npm test --workspace client`
   - `npm run typecheck --workspace client`
   - `npm run build --workspace client`
   - `npm test --workspace server`
   - `npm test`
   All commands MUST pass with exit code 0.

OUTPUT:
Write your full report and handoff to:
`C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\worker_m3_r2\handoff.md`
Report all passing test outputs, files modified, and verification results in handoff.md, then send a completion message to parent.
