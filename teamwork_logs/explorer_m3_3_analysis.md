# Milestone 3 Deep Dive Analysis: Unified Live Preview, Bot Avatar & Tests

**Author**: Explorer 3 (Unified Live Preview, Bot Avatar & Tests)  
**Date**: 2026-10-03  
**Target Codebase**: `hoho_manager/client/` and `hoho_manager/server/`  

---

## 1. Executive Summary

This investigation analyzed the live message preview system, bot avatar resolution pipeline, UI component duplication, and test suites across `hoho_manager` client and server. 

### Key Findings:
1. **Bot Avatar Disconnect**: `MessagePreview.tsx` currently only checks `data.avatar_url` (manual webhook override) and falls back to a generic Lucide `<Bot>` icon. It never reads `botIdentity` from the backend, nor does `useGlobalStore` expose `botIdentity` state, despite the server endpoints (`GET /api/discord/identity` and `GET /api/send/identity`) already existing and passing tests.
2. **Bifurcated Preview Mode Logic**: `MessagePreview.tsx` contains mutually exclusive `{!isV2 && ...}` vs `{isV2 && ...}` render branches. When in V2 mode, top-level text `payload.content` and `data.embeds` are suppressed. When in Classic mode, non-ActionRow components are hidden. Switching modes causes apparent data loss in the preview.
3. **Pervasive UI Duplication**:
   - **Editor Mode Buttons**: Duplicated in both `Header.tsx` (lines 26–52) and `App.tsx` (lines 603–632).
   - **Component Palette & Layers Panel**: Rendered in three separate locations: `Sidebar.tsx` (lines 50–57), `MessageEditor.tsx` (lines 97–109), and `App.tsx` (lines 640–666).
   - **Visual Action Row Builder Omission**: `DiscohookComponentsEditor.tsx` was created for visual Action Row building (button pills, style badges, select menus) but is never rendered anywhere in the application.
4. **Discord Native Parity Deficits**:
   - Lack of Discord default avatar fallback algorithm (`https://cdn.discordapp.com/embed/avatars/${(BigInt(botId) >> 22n) % 6n}.png`).
   - Missing author link handling in `EmbedPreview.tsx` when `embed.author.url` is present.
   - Missing button emoji rendering in `ActionRowPreview.tsx` when `button.emoji` is set.
   - Ignoring `useSettingsStore` settings (`fontSize`, `messageDisplay: 'cozy' | 'compact'`).
5. **Test Suite Baseline & Coverage**:
   - 283 total tests pass (222 server, 61 client).
   - `client/tests/layout_discohook.test.ts` (15 tests) tests pure Zustand stores and utility functions in a Node Vitest environment; none of the existing tests will break if store APIs remain backward compatible.
   - Zero tests currently verify `botIdentity` store integration or author/avatar fallback resolution in the client.

---

## 2. Preview Architecture & Component Inventory

### 2.1 File Map & Responsibilities
| File Path | Role | Key Behaviors & Gaps |
|---|---|---|
| `client/src/components/preview/MessagePreview.tsx` | Root preview pane | Renders Discord message container, author avatar, APP badge, timestamp, body, and component hierarchy. **Bug**: Split into mutually exclusive `!isV2` vs `isV2` blocks; ignores `botIdentity`. |
| `client/src/components/preview/EmbedPreview.tsx` | Discord Embed | Border accent color, title link, description Markdown, inline field grid (1/2/3 cols), image, thumbnail, footer with timestamp. High fidelity; missing `author.url` anchor. |
| `client/src/components/preview/ActionRowPreview.tsx` | Action Rows & Buttons | Maps ButtonStyle (1..5) to Discord colors (Blurple, Gray, Green, Red). Renders Select Menus. **Gap**: Does not render `button.emoji`. |
| `client/src/components/preview/ComponentPreview.tsx` | V2 Blocks dispatcher | Handles `TextDisplay`, `Separator`, `Section`, `MediaGallery`, `File`, delegating ActionRows to `ActionRowPreview`. |
| `client/src/components/preview/ContainerPreview.tsx` | V2 Container Card | Rounded card with absolute left accent bar, recursively rendering children via `AutoComponent`. |
| `client/src/components/preview/Markdown.tsx` | Discord Markdown Engine | AST-free recursive tokenizer handling bold, italic, code, underline, strike, spoiler, links, bare URLs, user/role/channel mentions, timestamps (`<t:...>`), and custom emojis (`<:name:id>`). |

### 2.2 Analysis of `MessagePreview.tsx`
Lines 39–40 & 60–69:
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
Lines 83–108:
```tsx
<div className="mt-0.5 space-y-2">
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
</div>
```

#### Defect 1: Avatar Resolution Fails Default Discord & Bot Profile Pictures
- When `data.avatar_url` is empty (the standard case when sending via bot rather than webhook override), it displays `<Bot size={18} className="text-white" />` inside a blurple circle.
- The user's bot avatar is completely invisible in the preview, directly violating Acceptance Criteria: `[ ] The Bot profile picture correctly loads in the Preview.`

#### Defect 2: Data Loss Illusion Across Mode Switching
- If a user starts in Classic mode, crafts 3 rich embeds and an Action Row with buttons, and then switches to V2 mode (e.g. to try out containers), lines 88–89 hide all embeds because `!isV2` evaluates to false!
- Conversely, if a user builds Components V2 containers and switches to Classic mode, lines 101–107 hide all containers because they filter `c.type === ComponentType.ActionRow`.
- If a user types text in `data.content` in V2 mode, `payload.content` is omitted by `toDiscordPayload` and hidden by `!isV2`, causing the text to vanish from the preview.

---

## 3. UI Element Duplication Audit

The application currently has three major duplicate UI structures:

### 3.1 Editor Mode Toggles
1. **`Header.tsx` (lines 26–52)**:
   - Component: `ModeToggle`
   - Buttons: `Classic` and `Components V2`
   - Styled with blurple pill toggle.
2. **`App.tsx` (lines 603–632)**:
   - "Mode Toggle Bar" above the editor accordion.
   - Identical buttons: `Classic` and `Components V2` (with Sparkles icon).
- **Consolidation Solution**: Keep the mode toggle in the top header (`Header.tsx`) where global document controls live. Eliminate lines 603–632 in `App.tsx`.

### 3.2 Component Palette & Layers Panel
1. **`Sidebar.tsx` (lines 50–57)**:
   - Rendered in the "Build" tab of the sidebar.
2. **`MessageEditor.tsx` (lines 97–109)**:
   - Conditionally rendered inside the Message 1 editor if `isV2`.
3. **`App.tsx` (lines 640–666)**:
   - Rendered inside an Accordion below Message 1: `"Components (Buttons, Menus & Layers)"`.
- **Consolidation Solution**:
  - The Discohook 3-pane paradigm assigns structural hierarchy to the **Left Sidebar**: the Left Sidebar is the natural home for the draggable Component Palette and the Layers tree hierarchy.
  - The Center Editor should host `MessageEditor` (Content, Embeds) and `DiscohookComponentsEditor` (Visual Action Rows & Buttons).
  - Remove `ComponentPalette` and `LayersPanel` from `MessageEditor.tsx` and from `App.tsx`'s redundant accordion.

### 3.3 Redundant Previews / Split Preview Logic
- In `App.tsx`, `SplitPane` has `right={<MessagePreview />}`.
- Inside `MessagePreview`, the preview is bifurcated into two separate rendering models.
- **Consolidation Solution**: Convert `MessagePreview` into a unified renderer that displays:
  1. Top-level content (Markdown) if `data.content` or `payload.content` exists.
  2. Embeds if `data.embeds.length > 0`.
  3. Components (Containers, Action Rows, Sections, etc.) using `TopLevelComponent`.
  Both Classic and V2 data render seamlessly without toggle barriers.

---

## 4. Bot Avatar & Identity Resolution Pipeline

### 4.1 Backend Endpoints
The backend provides two identity endpoints:
1. `GET /api/discord/identity` (`server/src/routes/discord.ts:142`):
   - Returns `{ id: string, username: string, avatar: string | null }`.
   - `avatar` is already formatted as `https://cdn.discordapp.com/avatars/${data.id}/${data.avatar}.png`.
2. `GET /api/send/identity` (`server/src/routes/send.ts:229`):
   - Returns `{ name: string, avatar: string }`.

### 4.2 Client State Gap: `useGlobalStore.ts`
Currently `client/src/store/globalStore.ts` contains only:
```ts
interface GlobalState {
  selectedGuildId: string | null;
  setSelectedGuildId: (id: string | null) => void;
}
```
In `PROJECT.md` line 61–64, the interface contract states:
```markdown
- `useGlobalStore`:
  - `selectedGuildId: string | null`
  - `botIdentity: { username: string, avatar: string | null, id: string } | null`
  - `discordCache: Record<string, { data: any, timestamp: number }>`
```
`botIdentity` is completely missing from `useGlobalStore`!

### 4.3 Proposed Complete Avatar & Author Resolution Specification

```ts
export interface BotIdentity {
  id: string;
  username: string;
  avatar: string | null;
}

/**
 * Computes Discord's default embed avatar URL based on the user/bot snowflake.
 * Formula: (BigInt(snowflake) >> 22n) % 6n (returns 0 through 5).
 */
export const getDefaultDiscordAvatar = (snowflake?: string | null): string => {
  if (!snowflake || !/^\d{17,20}$/.test(snowflake)) {
    return "https://cdn.discordapp.com/embed/avatars/0.png";
  }
  try {
    const index = Number((BigInt(snowflake) >> 22n) % 6n);
    return `https://cdn.discordapp.com/embed/avatars/${Math.abs(index)}.png`;
  } catch {
    return "https://cdn.discordapp.com/embed/avatars/0.png";
  }
};

/**
 * Resolves the preview's author name and avatar URL based on strict precedence:
 * 1. Explicit message override (data.username, data.avatar_url)
 * 2. Active bot profile identity (botIdentity from Discord API)
 * 3. Selected bot profile name from useProfileStore
 * 4. Default Discord fallback
 */
export const resolveAuthorInfo = ({
  dataUsername,
  dataAvatarUrl,
  botIdentity,
  sendMode,
  selectedBotProfileName,
}: {
  dataUsername?: string;
  dataAvatarUrl?: string;
  botIdentity?: BotIdentity | null;
  sendMode?: string;
  selectedBotProfileName?: string;
}) => {
  const isWebhook = sendMode === "webhook";

  // Username resolution
  const name =
    dataUsername?.trim() ||
    (isWebhook ? "Captain Hook" : botIdentity?.username || selectedBotProfileName || "HoHo Bot");

  // Avatar URL resolution
  const defaultFallback = getDefaultDiscordAvatar(botIdentity?.id);
  const avatar =
    dataAvatarUrl?.trim() ||
    (isWebhook
      ? "https://cdn.discordapp.com/embed/avatars/0.png"
      : botIdentity?.avatar || defaultFallback);

  return { name, avatar, defaultFallback };
};
```

---

## 5. Discord Native Rendering Parity Inspection

| Element | Discord Native Specification | Current Status in `hoho_manager` | Recommended Refinement |
|---|---|---|---|
| **Avatar** | 40x40 circular (`rounded-full`), Discord CDN avatar or default 0..5 embed avatar | Displays Lucide `<Bot>` when `data.avatar_url` is not typed | Resolve via `botIdentity` + `getDefaultDiscordAvatar` |
| **Author Name** | 15–16px font-medium `#f2f3f5` | Displays `"Message Builder"` when `data.username` is not typed | Resolve via `botIdentity?.username` or `"HoHo Bot"` |
| **APP Badge** | Blurple `#5865f2`, 10px font-semibold, white text, 3px border-radius, labeled "APP" | `<span className="rounded bg-blurple px-1 py-px text-[10px] font-semibold text-white">APP</span>` | **Compliant**; matches current Discord client style |
| **Timestamp** | 12px `#949ba4`, "Today at HH:MM" | `Today at {now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}` | **Compliant**; ticks every minute |
| **Content Markdown** | 15–16px `#dbdee1`, line-height 1.375rem, whitespace-pre-wrap | `<Markdown content={...} className="text-[15px] text-[#dbdee1]" />` | **Compliant**; handles all common Discord tokens |
| **Embed Border** | 4px solid left accent bar, default `#202225` | `style={{ borderLeftColor: accent }}` with 4px border | **Compliant** |
| **Embed Author Link** | If `author.url` exists, author name is a clickable link | Only renders `<span className="text-sm font-semibold">{embed.author.name}</span>` | Wrap in `<a href={embed.author.url}>` if present |
| **Embed Inline Fields** | Up to 3 consecutive inline fields per row in grid | `groupFields` helper accurately chunks inline fields into `grid-cols-2` and `grid-cols-3` | **Compliant** |
| **Embed Footer** | Bullet `•` separator between footer text and timestamp | `<span>{embed.footer.text}</span><span>•</span><span>{date}</span>` | **Compliant** |
| **Action Row Buttons** | 5 styles: Primary (Blurple), Secondary (Gray), Success (Green), Danger (Red), Link (Gray + ExternalLink) | `BUTTON_CLASSES` correctly styles all 5 | **Compliant** |
| **Button Emojis** | Buttons can have unicode or custom Discord emoji alongside or in place of label | ButtonPreview only renders `button.label` | Add emoji rendering: `<img src="https://cdn.discordapp.com/emojis/{id}.png" />` or unicode char |
| **Select Menus** | 40px height, `#1e1f22` bg, `#3f4147` border, chevron down | `SelectPreview` renders 40px tall pill with chevron | **Compliant** |
| **Display Mode Settings** | Compact mode hides 40px avatar and places timestamp before username | Currently ignores `useSettingsStore` display settings | Apply `settings.messageDisplay === "compact"` layout when enabled |

---

## 6. Test Suite Analysis & Regression Prevention

### 6.1 Monorepo Test Baseline
- **Total Test Files**: 27 (20 server, 7 client)
- **Total Passing Tests**: 283 (222 server, 61 client)
- **Workspace execution**:
  - `npm test --workspace client` -> 7 files passed, 61 tests passed in 1.80s.
  - `npm test --workspace server` -> 20 files passed, 222 tests passed in 4.73s.

### 6.2 Inspection of `client/tests/layout_discohook.test.ts`
The test file has 4 suites covering 15 tests:
1. `F1 & F2: Layout Configuration & Unified Editor State`:
   - Checks `useSettingsStore` default theme (`dark`), default display (`cozy`).
   - Checks `updateSettings` (`compact`, font size 14, `compactAvatars: true`).
   - Checks `useMessageStore.setContent`.
   - Checks `useMessageStore.setMode("v2")` and `setMode("classic")`.
2. `F3: Bot Profile Picture & Identity Resolution`:
   - Checks `useProfileStore.setBotProfileId(42)`.
   - Checks `useProfileStore.setSendMode("bot")`.
   - Checks `useProfileStore.setSendMode("webhook")` and `setWebhookUrl`.
3. `F4: Visual Action Rows & Component V2 Building`:
   - Checks `newButton` factory defaults.
   - Checks Action Row child button nesting.
   - Checks `stripInternal` stripping `_id`.
   - Checks `validateMessage` 2000 character content limit.
   - Checks `toDiscordPayload` transformation.
4. `F7: Manual Snowflake Fallback Logic`:
   - Checks `SNOWFLAKE_REGEX.test` for 18 and 19-digit snowflakes.
   - Checks `SNOWFLAKE_REGEX.test` rejection of invalid inputs.
   - Checks `useProfileStore.setChannelId` whitespace trimming.

### 6.3 Risk Assessment: What Could Break During M3 Refactor
1. **Zustand Persist in Node environment**:
   - In Node.js, `localStorage` is undefined. Zustand's persist middleware logs `[zustand persist middleware] Unable to update item...`. This is normal and doesn't fail tests, but any new store tests must avoid assuming persistent storage is available in Node.
2. **Backward Compatibility of Store Signatures**:
   - `useSettingsStore.getState().settings` must remain intact.
   - `useProfileStore.getState().botProfileId`, `sendMode`, `webhookUrl`, `channelId` must remain intact.
   - `useMessageStore.getState().data`, `mode`, `setContent`, `setMode` must remain intact.
3. **No DOM / React Rendering in Node Vitest**:
   - Vitest config uses `environment: "node"`. Tests must test pure logic, stores, and utility functions, NOT JSX rendering with `render(<MessagePreview />)` unless `jsdom` or `happy-dom` is configured.

### 6.4 New Tests Recommended for Milestone 3
Add to `layout_discohook.test.ts`:
1. `useGlobalStore` tracks `botIdentity: { id, username, avatar }`.
2. `getDefaultDiscordAvatar` correctly maps snowflakes to indices `0..5`.
3. `resolveAuthorInfo` returns explicit message overrides when present.
4. `resolveAuthorInfo` returns `botIdentity` when message overrides are absent.
5. `resolveAuthorInfo` falls back to default Discord avatar when `avatar` is null.
6. Unified preview validation helper: verifies document with both embeds and Action Rows passes validation and builds valid payload in Classic mode.

---

## 7. Concrete Recommendations for the Worker

### Recommendation 1: Update `useGlobalStore.ts`
Add `botIdentity` and `fetchBotIdentity` to `useGlobalStore`:
```ts
export interface BotIdentity {
  id: string;
  username: string;
  avatar: string | null;
}

interface GlobalState {
  selectedGuildId: string | null;
  botIdentity: BotIdentity | null;
  setSelectedGuildId: (id: string | null) => void;
  setBotIdentity: (identity: BotIdentity | null) => void;
  fetchBotIdentity: (profileId?: number) => Promise<void>;
}
```
Initialize `botIdentity` from `localStorage.getItem("bot_identity_cache")` so it renders synchronously on mount, and auto-fetch from `api.discord.identity(profileId)`.

### Recommendation 2: Refactor `MessagePreview.tsx` to Unified Rendering & Bot Avatar
1. Subscribe to `useGlobalStore((state) => state.botIdentity)` and `useProfileStore((state) => ({ sendMode: state.sendMode, botProfileId: state.botProfileId }))`.
2. Resolve author using `resolveAuthorInfo`:
   - Name: `data.username || botIdentity?.username || "HoHo Bot"`
   - Avatar: `data.avatar_url || botIdentity?.avatar || getDefaultDiscordAvatar(botIdentity?.id)`
   - Graceful `<img onError={(e) => { e.currentTarget.src = defaultFallback; }} />` fallback.
3. Replace bifurcated `!isV2` vs `isV2` blocks with a unified render stack:
   - Always render `payload.content || data.content` (via `<Markdown />`) if present.
   - Always render `data.embeds` (via `<EmbedPreview />`) if present.
   - Always render top-level `data.components` (via `<TopLevelComponent />`) if present.
   - If empty, show the friendly `"Nothing to preview yet."` placeholder.
4. Support compact display if `settings.messageDisplay === "compact"` (from `useSettingsStore`).

### Recommendation 3: Consolidate Duplicate UI Elements
1. **Mode Toggles**: Remove the duplicate Mode Toggle Bar from `App.tsx` (lines 603–632). Keep the sleek `ModeToggle` in `Header.tsx`.
2. **Component Palette & Layers Panel**: Remove them from `MessageEditor.tsx` and from `App.tsx`'s redundant accordion. Place them cleanly in the Left Sidebar (`Sidebar.tsx`).
3. **Visual Action Rows**: Place `DiscohookComponentsEditor` directly into the Center Editor (inside an Accordion or section after Embeds).

### Recommendation 4: Minor Parity Enhancements in Sub-Components
1. In `EmbedPreview.tsx`: Add anchor link `<a href={embed.author.url}>` when `embed.author.url` is present.
2. In `ActionRowPreview.tsx`: Render `button.emoji` when present (custom Discord emoji CDN or unicode).
