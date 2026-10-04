# Milestone 3 Review & Adversarial Audit Report (Reviewer 2: Preview, Avatar & Component Builder)

## Verdict: APPROVE

---

## 1. Observation

### 1.1 Dynamic Bot Identity & Avatar Resolution (`MessagePreview.tsx` & `globalStore.ts`)
- **Direct Code Inspection (`hoho_manager/client/src/components/preview/MessagePreview.tsx:41-48`)**:
  ```tsx
  const defaultDiscordAvatar = botIdentity?.id
    ? `https://cdn.discordapp.com/embed/avatars/${(BigInt(botIdentity.id) >> 22n) % 6n}.png`
    : null;
  const effectiveAvatar =
    data.avatar_url || botIdentity?.avatar || defaultDiscordAvatar;
  const effectiveUsername =
    data.username || botIdentity?.username || "Message Builder";
  const isV2 = mode === EDITOR_MODES.V2;
  ```
- **Error Handling & Fallback (`MessagePreview.tsx:75-81`)**:
  ```tsx
  onError={(e) => {
    if (defaultDiscordAvatar && e.currentTarget.src !== defaultDiscordAvatar) {
      e.currentTarget.src = defaultDiscordAvatar;
    } else {
      e.currentTarget.style.display = "none";
    }
  }}
  ```
- **Global Store Hydration (`hoho_manager/client/src/store/globalStore.ts:31-50, 67-81`)**:
  `loadInitialBotIdentity` retrieves `bot_identity_cache` synchronously from `localStorage` on store instantiation, deserializing `id`, `username`, and `avatar`. `setBotIdentity` maintains this cache by persisting changes or removing the key on `null`.
- **Auto-fetch Bootstrap (`hoho_manager/client/src/App.tsx:402-416`)**:
  `fetchIdentity()` queries `/api/send/identity` via `api.discord.identity()` on application mount and dispatches `useGlobalStore.getState().setBotIdentity(...)`.

### 1.2 Unified Preview Rendering (`MessagePreview.tsx`)
- **Direct Code Inspection (`MessagePreview.tsx:102-116`)**:
  ```tsx
  <div className="mt-0.5 space-y-2">
    {/* Unified preview: render content, embeds, and components whenever present */}
    {payload.content && (
      <Markdown content={payload.content} className="text-[15px] text-[#dbdee1]" />
    )}

    {data.embeds &&
      data.embeds.map((embed) => <EmbedPreview key={embed._id} embed={embed} />)}

    {data.components &&
      data.components.map((component) => (
        <div key={component._id}>
          <TopLevelComponent component={component} />
        </div>
      ))}
  </div>
  ```
  The previous bifurcation where `isV2` hid `payload.content` and `data.embeds` has been completely eliminated. Content, embeds, and components render concurrently within a single Discord chat bubble envelope.

### 1.3 Embed Author Hyperlinks & Button Emoji Rendering
- **Embed Author Links (`hoho_manager/client/src/components/preview/EmbedPreview.tsx:57-67`)**:
  ```tsx
  {embed.author.url ? (
    <a
      href={embed.author.url}
      target="_blank"
      rel="noreferrer"
      className="text-sm font-semibold hover:underline"
    >
      {embed.author.name}
    </a>
  ) : (
    <span className="text-sm font-semibold">{embed.author.name}</span>
  )}
  ```
- **Button Emoji Resolution (`hoho_manager/client/src/components/preview/ActionRowPreview.tsx:30-61`)**:
  `renderEmoji` handles string formatted Discord custom emojis (`/^<(a?):(\w+):(\d+)>$/`), unicode emoji strings (`👍`), and object emojis (`{ id, name, animated }`), rendering custom emojis via `https://cdn.discordapp.com/emojis/${id}.${animated ? "gif" : "png"}?size=24` and unicode emojis inline in `ButtonPreview` alongside link icons and text labels.

### 1.4 Visual Action Rows & Reordering Controls (`DiscohookComponentsEditor.tsx`)
- **Horizontal Reordering (`DiscohookComponentsEditor.tsx:281-308`)**:
  ```tsx
  <button
    type="button"
    disabled={childIndex === 0}
    onClick={() =>
      child._id &&
      row._id &&
      moveComponentById(child._id, -1, row._id)
    }
    className="p-0.5 text-[#949ba4] hover:text-white disabled:opacity-20 transition-colors"
    title="Move Left"
  >
    <ChevronLeft size={12} />
  </button>
  <button
    type="button"
    disabled={childIndex === rowChildren.length - 1}
    onClick={() =>
      child._id &&
      row._id &&
      moveComponentById(child._id, 1, row._id)
    }
    className="p-0.5 text-[#949ba4] hover:text-white disabled:opacity-20 transition-colors"
    title="Move Right"
  >
    <ChevronRight size={12} />
  </button>
  ```
  Interacts with `useMessageStore.moveComponentById` and `tree.ts:moveComponent`, safely reordering sibling elements within the parent action row.
- **Action Flow Status Badges (`DiscohookComponentsEditor.tsx:92-106`)**:
  `getFlowBadge` dynamically reflects the component state:
  - `🔗 Link` (`bg-[#4e5058]`) for URL buttons.
  - `📋 Modal` (`bg-[#5865f2]`) if the assigned Action Flow contains an `open_modal` step.
  - `⚡ Flow` (`bg-[#23a55a]`) for any non-modal multi-step workflow.
  - `No Action` (`bg-[#35373c]`) if unassigned.
- **Support for All 5 Select Menu Types (`DiscohookComponentsEditor.tsx:27-36, 381-397`)**:
  `SELECT_TYPE_MAP` defines:
  1. `ComponentType.StringSelect` (`3`) — ListFilter icon
  2. `ComponentType.UserSelect` (`5`) — User icon
  3. `ComponentType.RoleSelect` (`6`) — Shield icon
  4. `ComponentType.ChannelSelect` (`8`) — Hash icon
  5. `ComponentType.MentionableSelect` (`7`) — AtSign icon
  Each type is exposed in the "Add Select Menu" dropdown and receives dedicated card rendering with custom placeholder preview and delete actions.

### 1.5 Interactive Modal Mockup & Step Controls (`StepList.tsx`)
- **Discord Modal Mockup (`StepList.tsx:109-160`)**:
  `DiscordModalPreview` visually mimics Discord's modal dialog box (`#313338` background, `#2b2d31` header/footer, `✕` dismiss button, required asterisks in `#da373c`, short input fields vs paragraph textareas, Cancel / Submit buttons).
- **Question Reordering (`StepList.tsx:277-284, 347-363`)**:
  `moveInput(fieldIdx, -1)` and `moveInput(fieldIdx, 1)` reorder questions in place with disabled bounds handling.
- **Character Limits (`StepList.tsx:409-434`)**:
  Dedicated numeric input fields for `Min Length (0 - 4000)` and `Max Length (1 - 4000)`, formatted into Discord payload schema as `min_length` and `max_length`.
- **Variable Syntax Helper Pills (`StepList.tsx:435-450`)**:
  Clickable/visual pills displaying `{{customId}}` and `{{input.customId}}` for downstream step interpolation.

### 1.6 Independent Verification Command Execution
Direct commands executed in shell:
1. `npm test --workspace client`:
   - Result: Exit code 0.
   - 7 test files passed, 66 tests passed (including all 20 tests in `layout_discohook.test.ts`).
2. `npm run typecheck --workspace client`:
   - Result: Exit code 0, 0 TypeScript compiler errors.
3. `npm run build --workspace client`:
   - Result: Exit code 0, Vite production bundle compiled in 2.36s (`dist/assets/index-CFwDVpeE.js: 397.85 kB`).
4. `npm test --workspace server`:
   - Result: Exit code 0, 20 test files passed, 222 tests passed across Tiers 1-4.

---

## 2. Logic Chain

1. **Avatar Resolution Fidelity**:
   - Discord's default embed avatar algorithm uses `(BigInt(snowflake) >> 22n) % 6n`.
   - `MessagePreview.tsx` lines 41-48 correctly apply this formula when `botIdentity.id` is available and fallback to `effectiveAvatar`.
   - The image tag includes an `onError` event handler ensuring that broken remote image URLs smoothly drop down to the CDN default avatar and ultimately the SVG `<Bot />` icon without leaving an unsightly broken image glyph.
2. **Unified Document Presentation**:
   - Discohook’s primary differentiator is that users edit both content/embeds and interactive components together.
   - The elimination of `!isV2` gates in `MessagePreview.tsx:102-116` allows rich embeds and action buttons to render in a unified Discord message bubble.
3. **Component Builder Usability**:
   - Action row layouts in Discord have strict constraints: up to 5 buttons per row, or exactly 1 select menu per row.
   - `DiscohookComponentsEditor.tsx` enforces this by disabling "Add Select Menu" if buttons exist, and disabling "Add Button" if full or if a select menu is present.
   - The Move Left and Move Right buttons allow horizontal rearrangement without having to delete and re-add buttons.
4. **Modal Workflow Designer**:
   - `StepList.tsx` provides immediate visual validation of what an end user will see when clicking a button that triggers `open_modal`.
   - Form inputs enforce the 5-field limit (`inputFields.length < 5`), while allowing question reordering and bounds-checked min/max string limits.
5. **Absence of Integrity Violations**:
   - Scanned all source and test files for mock cheats, facade objects, hardcoded bypasses, or fabricated test scores.
   - `layout_discohook.test.ts` executes real state mutations in Zustand stores and checks actual output payloads from `toDiscordPayload` and `stripInternal`.

---

## 3. Caveats & Adversarial Findings

### 3.1 Adversarial Challenge: Unguarded `BigInt(botIdentity.id)` Modulo
- **Assumption Challenged**: `botIdentity.id` in `localStorage` is always a valid numeric snowflake string.
- **Attack Scenario**: If a developer, admin, or corrupted localStorage contains a non-numeric string (e.g., `id: "unknown"` or `id: "bot_test"`), `BigInt("unknown")` throws an unhandled `SyntaxError: Cannot convert unknown to a BigInt` during component rendering.
- **Blast Radius**: `MessagePreview` will throw a runtime error and crash the preview pane until localStorage is cleared.
- **Mitigation (Recommended for M4)**:
  Wrap the calculation in a numeric check or try/catch helper:
  ```ts
  const defaultDiscordAvatar = botIdentity?.id && /^\d+$/.test(botIdentity.id)
    ? `https://cdn.discordapp.com/embed/avatars/${(BigInt(botIdentity.id) >> 22n) % 6n}.png`
    : null;
  ```
  *Severity: Minor (does not block M3 since production API returns valid Discord snowflake IDs).*

### 3.2 Non-Investigated Scope
- Milestone 3 scope is strictly client-side UI and layout refactoring. No server-side files were altered during this milestone.
- Backend settings endpoints and security features previously verified in M1 and M2 continue to pass 100% of the 222 server tests.

---

## 4. Conclusion

The refactor implemented by Worker M3 meets all requirements set forth in `ORIGINAL_REQUEST.md`, `PROJECT.md`, and the Reviewer 2 dispatch:
1. Dynamic bot identity and snowflake avatar resolution are properly implemented and hydrated.
2. The preview pane is unified across Classic and Components V2 modes.
3. Embed author hyperlinks and button emojis render with Discord fidelity.
4. Action Row builder features horizontal reordering, informative flow badges, and support for all 5 select menu types.
5. Modal action configuration includes a visual Discord modal mockup, field reordering, and character limits.
6. All automated test suites, typechecks, and production builds pass cleanly with 0 errors.

**Official Verdict**: **APPROVE**

---

## 5. Verification Method

To independently verify this verdict:
```bash
# 1. Run Client test suite
npm test --workspace client
# Expected: 7 passed test files, 66 passed tests

# 2. Run TypeScript static typechecker on Client
npm run typecheck --workspace client
# Expected: Exit code 0, 0 errors

# 3. Compile Client production build
npm run build --workspace client
# Expected: Vite build succeeds in ~2-3 seconds

# 4. Run Server E2E and regression test suite
npm test --workspace server
# Expected: 20 passed test files, 222 passed tests
```
