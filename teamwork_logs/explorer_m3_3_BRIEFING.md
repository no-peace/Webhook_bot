# BRIEFING — 2026-10-03T12:05:00Z

## Mission
Investigate the live message preview and test suite in hoho_manager (client & server) for Milestone 3 (Unified Live Preview, Bot Avatar & Tests).

## 🔒 My Identity
- Archetype: explorer
- Roles: Explorer 3 (Unified Live Preview, Bot Avatar & Tests)
- Working directory: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m3_3
- Original parent: bdcb2697-610e-4719-ab5a-2e90935cb4e6
- Milestone: Milestone 3

## 🔒 Key Constraints
- Read-only investigation — do NOT implement / modify source code
- Files for content delivery, Messages for coordination
- Handoff must follow 5-component structure (Observation, Logic Chain, Caveats, Conclusion, Verification Method)
- System prompt protection strictly enforced

## Current Parent
- Conversation ID: bdcb2697-610e-4719-ab5a-2e90935cb4e6
- Updated: 2026-10-03T12:01:02Z

## Investigation State
- **Explored paths**:
  - `hoho_manager/client/src/components/preview/` (`MessagePreview.tsx`, `EmbedPreview.tsx`, `ActionRowPreview.tsx`, `ComponentPreview.tsx`, `ContainerPreview.tsx`, `Markdown.tsx`)
  - `hoho_manager/client/src/components/editor/` (`DiscohookComponentsEditor.tsx`, `MessageEditor.tsx`, `ComponentPalette.tsx`, `LayersPanel.tsx`)
  - `hoho_manager/client/src/components/layout/` (`Sidebar.tsx`, `Header.tsx`, `SplitPane.tsx`)
  - `hoho_manager/client/src/store/` (`globalStore.ts`, `messageStore.ts`, `profileStore.ts`, `settingsStore.ts`, `discordCacheStore.ts`)
  - `hoho_manager/client/src/App.tsx`
  - `hoho_manager/client/tests/layout_discohook.test.ts`
  - `hoho_manager/server/tests/e2e/tier1_features.test.ts`
  - `hoho_manager/server/src/routes/discord.ts`, `routes/send.ts`, `services/discordService.ts`, `utils/validation.ts`
- **Key findings**:
  - `MessagePreview.tsx` only reads `data.avatar_url` (manual webhook override) and falls back to Lucide `<Bot>` icon. `botIdentity` is not exposed in `useGlobalStore`, and Discord default CDN avatar formula `(snowflake >> 22n) % 6n` is not implemented.
  - `MessagePreview.tsx` contains mutually exclusive `!isV2` vs `isV2` blocks that suppress content/embeds in V2 and hide non-ActionRows in Classic, causing apparent data loss on mode switch.
  - Editor Mode toggles are duplicated in both `Header.tsx` and `App.tsx`.
  - `ComponentPalette` and `LayersPanel` are rendered in 3 separate places (`Sidebar.tsx`, `MessageEditor.tsx`, and `App.tsx`).
  - `DiscohookComponentsEditor.tsx` was created for visual Action Rows with button pills and style badges, but is never rendered anywhere.
  - Existing tests (283 passed monorepo-wide) run in Vitest `node` environment without DOM simulation.
- **Unexplored areas**: None for this mission.

## Key Decisions Made
- Formulated concrete, self-contained architecture recommendations for Worker:
  1. Add `botIdentity` & `fetchBotIdentity` to `useGlobalStore.ts` with local cache fallback.
  2. Implement `resolveAuthorInfo` and `getDefaultDiscordAvatar` helper.
  3. Refactor `MessagePreview.tsx` to a single unified render stack handling text, embeds, and components simultaneously.
  4. Remove duplicate Mode Toggle from `App.tsx` and duplicate palettes from `MessageEditor.tsx` and `App.tsx`.
  5. Integrate `DiscohookComponentsEditor.tsx` into the editor workflow.

## Artifact Index
- DISPATCH.md — Initial dispatch record
- BRIEFING.md — Persistent context & working memory
- analysis.md — Comprehensive technical analysis report
- handoff.md — 5-component self-contained handoff report
