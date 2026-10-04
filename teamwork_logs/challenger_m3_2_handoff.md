# Challenger 2 Handoff Report: Action Rows, Modals & Component Limits

**Verdict**: `APPROVE`  
**Role**: Challenger 2 (Action Rows, Modals & Component Limits)  
**Target Milestone**: Milestone 3 (Discohook Layout Clone & Component Integration)  
**Date**: 2026-10-03  

---

## 1. Observation

1. **Test Suite Execution Results**:
   - Authored new adversarial stress test suite in `hoho_manager/client/tests/adversarial_action_rows_modals_limits.test.ts` (42 comprehensive automated tests).
   - Executed test suite via command:
     `npx vitest run tests/adversarial_action_rows_modals_limits.test.ts`
     ```
     ✓ tests/adversarial_action_rows_modals_limits.test.ts (42 tests) 132ms
      Test Files  1 passed (1)
           Tests  42 passed (42)
        Duration  2.64s
     Exit Code: 0
     ```
   - Executed worker Milestone 3 test suite:
     `npx vitest run tests/layout_discohook.test.ts`
     ```
     ✓ tests/layout_discohook.test.ts (20 tests) 59ms
      Test Files  1 passed (1)
           Tests  20 passed (20)
     Exit Code: 0
     ```
   - Executed client TypeScript typecheck:
     `npm run typecheck --workspace client` (`tsc -p tsconfig.json --noEmit`)
     ```
     Exit Code: 0 (0 errors)
     ```
   - Executed client production build:
     `npm run build --workspace client` (`vite build`)
     ```
     ✓ 1938 modules transformed.
     dist/assets/index-CFwDVpeE.js   397.85 kB │ gzip: 115.54 kB
     Exit Code: 0
     ```
   - Executed server test suite:
     `npm test --workspace server`
     ```
     Test Files  20 passed (20)
          Tests  222 passed (222)
     Exit Code: 0
     ```

2. **Code Observations**:
   - **Action Row Limits (`hoho_manager/client/src/utils/discord.ts:168-177`)**:
     ```ts
     if (component.type === ComponentType.ActionRow) {
       actionRowCount += 1;
       if (actionRowCount > 5) {
         errors.push(`${componentPath}: A message cannot contain more than 5 Action Rows`);
       }
       const children = component.components ?? [];
       if (children.length === 0) {
         errors.push(`${componentPath}: Action Row needs at least one button or select menu`);
       }
       if (children.length > Limits.components.actionRowButtons) {
         errors.push(`${componentPath}: Action Row allows at most ${Limits.components.actionRowButtons} controls`);
       }
     ```
     Validates both top-level and container-nested Action Rows (`depth + 1` recursion). Exactly 5 Action Rows and exactly 5 buttons per row pass with 0 errors; 6 Action Rows or 6 buttons per row trigger explicit Discord limit errors.
   - **Component Capacity & Nesting Gating (`hoho_manager/client/src/utils/componentsV2.ts:370-380`)**:
     ```ts
     export const canAddToActionRow = (
       children: readonly ComponentNode[],
       childType: number,
     ): boolean => {
       if (!canNestIn(ComponentType.ActionRow, childType)) return false;
       if (children.length >= Limits.components.actionRowButtons) return false;
       if (childType === ComponentType.Button) {
         return children.every((child) => child.type === ComponentType.Button);
       }
       return children.length === 0;
     };
     ```
     Prevents adding >5 buttons and strictly blocks mixing buttons with select menus or adding multiple select menus to one row.
   - **Horizontal Button Reordering (`hoho_manager/client/src/utils/tree.ts:114-132`)**:
     ```ts
     const target = index + direction;
     if (target < 0 || target >= list.length) return { components: components ?? [], found: false };

     const reordered = [...list];
     const current = reordered[index];
     const swap = reordered[target];
     if (!current || !swap) return { components: components ?? [], found: false };
     reordered[index] = swap;
     reordered[target] = current;
     ```
     Guards index 0 moving left (`target < 0`) and last index moving right (`target >= list.length`), resulting in an exact no-op without mutating state or throwing errors.
   - **5 Select Menu Types (`hoho_manager/client/src/utils/componentsV2.ts:125-167`)**:
     Factory functions create:
     - `newStringSelect()` -> `type: 3`
     - `newUserSelect()` -> `type: 5`
     - `newRoleSelect()` -> `type: 6`
     - `newMentionableSelect()` -> `type: 7`
     - `newChannelSelect()` -> `type: 8`
     `validateMessage` accepts all 5 types (`discord.ts:195-204`) while enforcing that StringSelect has at least 1 option and that `min_values <= max_values`.
   - **Modal Form Limits & Reordering (`hoho_manager/client/src/components/actions/StepList.tsx:91-107, 277-284`)**:
     `formatModalComponents` enforces `fields.slice(0, 5)` to strictly restrict modal text inputs to at most 5 Action Rows. `moveInput` safely handles `target < 0` and `target >= inputFields.length`.
   - **Internal Metadata Stripping (`hoho_manager/client/src/utils/discord.ts:43-54`)**:
     ```ts
     export const stripInternal = (value: unknown): unknown => {
       if (Array.isArray(value)) return value.map(stripInternal);
       if (value === null || typeof value !== "object") return value;

       const output: Record<string, unknown> = {};
       for (const [key, nested] of Object.entries(value as Record<string, unknown>)) {
         if (key.startsWith("_")) continue; // `_id`, `_action`, ...
         if (nested === undefined) continue;
         output[key] = stripInternal(nested);
       }
       return output;
     };
     ```
     Recursively removes all keys beginning with `_` (`_id`, `_action_custom_id`, etc.) across arbitrarily nested component trees, select options, gallery items, and embed fields.

---

## 2. Logic Chain

1. *Action Row and Control Limits Verification*:
   - Per Discord API specification, messages may have at most 5 Action Rows, and each Action Row may contain at most 5 buttons or exactly 1 select menu.
   - Observation 1 and 2 show that `validateMessage` enforces `actionRowCount <= 5` and `children.length <= 5`.
   - Our adversarial test cases 1.1–1.10 empirically verified that 5 rows / 5 buttons succeed, 6 rows / 6 buttons fail, container-nested rows count toward the limit, empty rows are rejected, and non-interactive components inside Action Rows are blocked.

2. *Horizontal Button Reordering Verification*:
   - In a graphical message builder, buttons must support horizontal reordering within an action row without corrupting data or throwing when attempting to move past array boundaries.
   - Observation 1 and 2 show `moveComponent` guards `target < 0` and `target >= list.length`.
   - Adversarial tests 2.1–2.7 proved that moving the first button left (-1) or the last button right (+1) is a clean no-op, single-button rows are safe, middle buttons can traverse bidirectionally across all 5 slots, container-nested rows reorder correctly, and separate rows remain completely isolated.
   - Button style switching via `buttonStylePatch` safely moves `custom_id` into `_action_custom_id` when switching to Link style and restores it when switching back.

3. *5 Select Menu Types Parity & Wire Serialization*:
   - Discord supports 5 distinct select menu types: String (3), User (5), Role (6), Mentionable (7), and Channel (8).
   - Tests 3.1–3.10 verified that factories for all 5 types emit the correct integer codes (`3, 5, 6, 7, 8`), `validateMessage` requires options only for StringSelect while allowing auto-populated options for Types 5–8, exclusivity is enforced (a select menu cannot share an Action Row with another component), `min_values > max_values` is rejected, and all 5 select menu types can simultaneously sit across 5 Action Rows and serialize to valid Discord payloads.

4. *Modal Inputs & Reordering Verification*:
   - Discord modals support up to 5 text inputs (one per Action Row).
   - Tests 4.1–4.8 confirmed `formatModalComponents` truncates at `slice(0, 5)`, question reordering guards against edge overflow, character limits (`min_length: 0`, `max_length: 4000`) are preserved without loss, `DiscordModalPreview` renders clean Discord modal UI markup, and `useActionStore.toRegistrations()` creates registrations for both the button trigger and the modal submission handler while stripping internal IDs.

5. *Deep Payload Cleansing Verification*:
   - Discord rejects payloads containing unknown property keys (such as client editor tracking IDs).
   - Tests 5.1–5.7 confirmed that `stripInternal` scrubs `_id` and `_action_custom_id` across 10+ levels of nested Containers, Action Rows, Buttons, StringSelect options, MediaGallery items, and Embed fields.
   - Regex testing confirmed `JSON.stringify(stripped)` contains 0 occurrences of `"_id":` or `"_action...":`, `null` values are preserved, `undefined` values are omitted, and `toDiscordPayload` correctly bifurcates between Classic (content/embeds/action rows) and V2 (`MessageFlags.IsComponentsV2` + components).

---

## 3. Caveats

- We observed that a concurrent challenger test file (`tests/adversarial_layout_state_avatar.test.ts`) exhibited failures related to React 19 SSR `renderToStaticMarkup` evaluating Zustand 5's `getServerSnapshot()` rather than `getState()` for avatar resolution, and expecting Containers in Classic mode payloads (which Discord does not support). That file belongs to Challenger 1's domain and does not affect the Action Row, Modal, or Component Limits domain evaluated here.
- The 42 tests in `tests/adversarial_action_rows_modals_limits.test.ts` pass with 100% success rate without any changes to product source code.

---

## 4. Conclusion

**VERDICT: `APPROVE`**

The implementation of Action Rows, horizontal button reordering, 5 Select Menu types, modal inputs, and payload serialization in Milestone 3 satisfies all Discord API constraints and project requirements. All boundary conditions, limit violations, and serialization routines behave as expected under rigorous empirical adversarial stress-testing.

---

## 5. Verification Method

To independently execute and verify the Challenger 2 adversarial test harness:

```bash
# 1. Run Challenger 2 Adversarial Stress Test Suite (42 tests)
npx vitest run tests/adversarial_action_rows_modals_limits.test.ts

# 2. Run Worker Milestone 3 Test Suite (20 tests)
npx vitest run tests/layout_discohook.test.ts

# 3. Verify Client TypeScript Typechecking
npm run typecheck --workspace client

# 4. Verify Client Production Build
npm run build --workspace client

# 5. Verify Server E2E and Unit Test Suite (222 tests)
npm test --workspace server
```
