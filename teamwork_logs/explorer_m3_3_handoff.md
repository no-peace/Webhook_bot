# Milestone 3 Handoff: Unified Live Preview, Bot Avatar & Tests

**Agent**: Explorer 3 (Unified Live Preview, Bot Avatar & Tests)  
**Date**: 2026-10-03  
**Working Directory**: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m3_3`  
**Handoff Type**: Hard (Investigation Complete)  

---

## 1. Observation

1. **Bot Avatar Omission in Live Preview**:
   - In `client/src/components/preview/MessagePreview.tsx` lines 39–40 and 60–69:
     ```tsx
     const authorName = data.username || "Message Builder";
     const isV2 = mode === EDITOR_MODES.V2;
     ...
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
     `MessagePreview` strictly checks `data.avatar_url` (manual webhook override string) and renders a generic `<Bot>` icon whenever `data.avatar_url` is empty. It never accesses bot identity or default Discord avatars.
   - In `client/src/store/globalStore.ts` lines 3–6:
     ```ts
     interface GlobalState {
       selectedGuildId: string | null;
       setSelectedGuildId: (id: string | null) => void;
     }
     ```
     `useGlobalStore` does not define `botIdentity`, despite the interface contract in `PROJECT.md` line 61–64 specifying `botIdentity: { username: string, avatar: string | null, id: string } | null`.
   - In `client/src/App.tsx` lines 406–418:
     ```tsx
     const fetchIdentity = async () => {
       try {
         const { default: api } = await import("./api/client");
         const identity = await api.discord.identity();
         if (identity) {
           localStorage.setItem("bot_identity_cache", JSON.stringify({
             name: identity.username,
             avatar: identity.avatar,
           }));
         }
       } catch (err) {
         console.error("Failed to auto-fetch bot identity", err);
       }
     };
     fetchIdentity();
     ```
     `App.tsx` auto-fetches bot identity on load, but dumps it into `localStorage.setItem("bot_identity_cache", ...)` without storing it in `useGlobalStore`, and `MessagePreview` never reads it.

2. **Bifurcated Preview Mode Logic**:
   - In `client/src/components/preview/MessagePreview.tsx` lines 84–108:
     ```tsx
     {/* Classic message body */}
     {!isV2 && payload.content && (
       <Markdown content={payload.content} className="text-[15px] text-[#dbdee1]" />
     )}

     {!isV2 &&
       data.embeds.map((embed) => <EmbedPreview key={embed._id} embed={embed} />)}

     {/* Components V2 body */}
     {isV2 &&
       data.components.map((component) => (
         <div key={component._id}>
           <TopLevelComponent component={component} />
         </div>
       ))}

     {/* Classic action rows appear under the content/embeds. */}
     {!isV2 &&
       data.components
         .filter((component) => component.type === ComponentType.ActionRow)
         .map((component) => (
           <div key={component._id}>
             <AutoComponent component={component} />
           </div>
         ))}
     ```
     When `isV2 === true`, `!isV2` suppresses all `payload.content` and `data.embeds`. When `isV2 === false`, all non-ActionRow components are filtered out. Switching between modes produces the illusion of wiped data.

3. **UI Duplication & Dead Code**:
   - `Header.tsx` lines 26–52 renders `ModeToggle` (Classic / Components V2).
   - `App.tsx` lines 603–632 renders a duplicate "Mode Toggle Bar" (Classic / Components V2).
   - `ComponentPalette` and `LayersPanel` are rendered in three places:
     - `Sidebar.tsx` lines 50–57 ("Build" tab).
     - `MessageEditor.tsx` lines 97–109 (embedded in Message 1 if V2).
     - `App.tsx` lines 640–666 (Accordion "Components (Buttons, Menus & Layers)").
   - `DiscohookComponentsEditor.tsx` (228 lines) implements visual Action Row management with button style badges, move up/down, duplicate, and delete, but is never rendered anywhere in the application.

4. **Discord Parity Nuances**:
   - `EmbedPreview.tsx` line 56: Renders `<span className="text-sm font-semibold">{embed.author.name}</span>` without wrapping in `<a href={embed.author.url}>` when `embed.author.url` is present.
   - `ActionRowPreview.tsx` line 44: Renders only `{button.label ?? (isLink ? "Link" : "Button")}` without rendering `button.emoji`.
   - `MessagePreview.tsx` does not consume `useSettingsStore` settings (`fontSize`, `messageDisplay`).

5. **Test Baseline Execution**:
   - `npm test --workspace client`: 7 passed test files (61 passed tests) in 1.80s.
   - `npm test --workspace server`: 20 passed test files (222 passed tests) in 4.73s.
   - `client/tests/layout_discohook.test.ts` (15 tests) tests Zustand stores and utilities directly in Node; no tests fail or depend on DOM rendering. Zero tests currently cover `botIdentity` or avatar fallback formulas.

---

## 2. Logic Chain

1. **From Observation 1 to Bot Avatar Resolution**:
   - Acceptance Criteria state: `[ ] The Bot profile picture correctly loads in the Preview.`
   - `MessagePreview.tsx` currently falls back to `<Bot>` icon because it only inspects `data.avatar_url`.
   - The backend `/api/discord/identity` route already returns `{ id, username, avatar: "https://cdn.discordapp.com/avatars/..." }`.
   - Auto-fetch in `App.tsx` writes this to `localStorage` but not to `useGlobalStore`.
   - Therefore, adding `botIdentity` to `useGlobalStore`, hydrating it synchronously on mount, and updating `MessagePreview` to resolve avatar via `data.avatar_url || botIdentity?.avatar || getDefaultDiscordAvatar(botIdentity?.id)` directly fulfills the acceptance criteria without adding server load.

2. **From Observation 2 to Unified Preview Consolidation**:
   - Requirement R1 states: *"Consolidate duplicate UI elements (e.g. Editor Mode buttons, duplicate Previews). Use a single, unified Preview that gracefully handles both Classic and V2 data."*
   - Currently, `MessagePreview.tsx` splits rendering based on `isV2`, hiding embeds in V2 and hiding non-ActionRows in Classic.
   - If `MessagePreview` unifies the body so that `Markdown` (content), `EmbedPreview` (embeds), and `TopLevelComponent` (components) all render whenever present in the document, any message document (Classic, V2, or hybrid) will render completely and accurately without mode-switching data loss.

3. **From Observation 3 to UI Consolidation**:
   - Discohook's 3-pane layout specifies:
     - Left Pane (Sidebar): Guild selector, Component Palette, Layers Panel, navigation.
     - Center Pane (Editor): Message body, Embeds, Visual Action Rows.
     - Right Pane (Preview): Live Discord message preview.
   - Removing the duplicate Mode Toggle from `App.tsx` (retaining it in `Header.tsx`), removing duplicate palettes from `MessageEditor.tsx` and `App.tsx`, and embedding `DiscohookComponentsEditor` into the Center Editor resolves all duplications and brings `DiscohookComponentsEditor` into active use.

4. **From Observation 4 & 5 to Test Suite Stability**:
   - All 61 existing client tests run in Vitest `node` environment without DOM simulation.
   - Preserving the exact method signatures and return shapes of `useSettingsStore`, `useProfileStore`, `useMessageStore`, and `stripInternal`/`toDiscordPayload` guarantees zero regressions across the 61 client tests.
   - Adding 5 targeted unit tests in `layout_discohook.test.ts` for `botIdentity`, `getDefaultDiscordAvatar`, and author resolution will verify the new functionality under the same zero-regression standard.

---

## 3. Caveats

1. **Node Environment in Client Vitest**: Vitest client tests run in `environment: "node"`, not `jsdom`. Component rendering with `@testing-library/react` is not configured in `client/package.json`. Tests must continue testing stores, pure helper functions, and transformation logic.
2. **Offline Fallback for Avatars**: If Discord's CDN is unreachable or image loading fails, the `<img>` tag must include an `onError` handler falling back to Discord's default embed avatar or svg icon to prevent broken image icons.
3. **No Caveats on Backend**: The backend identity routes (`/api/discord/identity` and `/api/send/identity`) are fully implemented and covered by Tier 1 E2E tests (`server/tests/e2e/tier1_features.test.ts:191-246`).

---

## 4. Conclusion

1. **Bot Avatar & Identity**: Expand `useGlobalStore` with `botIdentity: { id: string; username: string; avatar: string | null } | null`, initialize it synchronously from `localStorage`, and resolve author and avatar in `MessagePreview` with automatic fallback to Discord's official embed avatar formula `https://cdn.discordapp.com/embed/avatars/${(BigInt(id) >> 22n) % 6n}.png`.
2. **Unified Preview**: Eliminate the `!isV2` vs `isV2` render bifurcation in `MessagePreview.tsx`. Render text content (Markdown), embeds (`EmbedPreview`), and components (`TopLevelComponent`) uniformly based on document contents.
3. **Consolidate Duplicate UI**: Remove duplicate Mode Toggle Bar from `App.tsx`, remove duplicate `ComponentPalette` / `LayersPanel` from `MessageEditor.tsx` and `App.tsx` accordion, and integrate `DiscohookComponentsEditor` into the editor flow.
4. **Discord Native Parity**: Add `author.url` link handling in `EmbedPreview.tsx` and button emoji rendering in `ActionRowPreview.tsx`.

---

## 5. Verification Method

To independently verify the investigation and test subsequent Worker implementations:

### Test Execution Commands
```bash
# 1. Run all client tests
npm test --workspace client

# 2. Run specifically the Discohook layout test suite
npx vitest run client/tests/layout_discohook.test.ts

# 3. Run all server E2E and unit tests
npm test --workspace server

# 4. Verify monorepo-wide pass rate
npm test
```

### Manual Visual Verification (on http://localhost:5175/)
1. Open http://localhost:5175/.
2. Check that the Preview pane displays the bot's avatar and username (or default Discord embed avatar) rather than the generic `<Bot>` icon.
3. Add message content and an embed, switch between Classic and Components V2 modes, and verify that the preview does not hide or discard existing content or embeds.
4. Check that only a single Mode Toggle exists in the application header.
5. In the Center Editor, verify that `DiscohookComponentsEditor` renders visual Action Rows with button pills and style badges.
