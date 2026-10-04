# Technical Analysis: Action Rows, Modals & Component V2 Editor

**Agent**: Explorer 2 (`explorer_m3_2`)  
**Mission**: Investigate Action Rows, Modals, and Component V2 editor architecture, data structures, and UX gaps to establish a complete, actionable implementation plan for Milestone 3.  
**Date**: 2026-10-03  

---

## Executive Summary

1. **`DiscohookComponentsEditor.tsx` is completely orphaned**: An initial implementation of visual Action Rows exists in `hoho_manager/client/src/components/editor/DiscohookComponentsEditor.tsx`, but it is **never imported or rendered** anywhere in the application. Users currently cannot visually view or build Action Rows with button pills in the main editor.
2. **Action Row Visual Deficiencies**:
   - The current `DiscohookComponentsEditor.tsx` implementation does not support horizontal button reordering (only row-level up/down reordering).
   - Button pills do not display Action Flow indicator badges (users cannot tell if a button has actions attached, is a modal trigger, or is a link).
   - Select menus in Action Rows render broken button pills with fallback label "Untitled Button" and default badges, and only `StringSelect` is supported.
   - Action Rows nested inside Component V2 `Container` nodes are ignored by `components.filter(c => c.type === ComponentType.ActionRow)`.
3. **Modals Architecture & UX Deficiencies**:
   - Modals are created as `open_modal` steps inside the interactive action flow (`FlowBuilder.tsx` / `StepList.tsx`).
   - The modal builder in `StepList.tsx` provides form fields for title, custom ID, and up to 5 inputs, but **completely lacks a visual Discord-fidelity modal preview**, input reordering controls, and variable mapping guidance.
   - The server (`actionExecutor.ts`) parses modal submissions into `{custom_id}`, `{input.custom_id}`, and `{modal.custom_id}` and runs the `then` branch, but the client UI does not explain this to the user.
4. **Integration with `useMessageStore.ts` and `toDiscordPayload`**:
   - The data model (`MessageData`, `ComponentNode`, `FlowStep`, `FlowRegistration`) is clean and fully supports Discord Action Rows and Component V2.
   - In Classic mode, `toDiscordPayload` strips internal IDs and preserves top-level Action Rows alongside content/embeds. In V2 mode, all components are sent with flag `MessageFlags.IsComponentsV2`.
5. **Concrete Worker Plan**: A 5-step, fully specified blueprint is provided below to mount `DiscohookComponentsEditor` into `MessageEditor.tsx`, upgrade button pills and select menu cards with horizontal reordering and flow badges, add an interactive visual Discord Modal Preview and question reorderer to `StepList.tsx`, and verify via automated tests.

---

## 1. Architectural Survey of Existing Components

### 1.1 `MessageEditor.tsx` (`hoho_manager/client/src/components/editor/MessageEditor.tsx`)
- **Role**: Center panel editor for message data.
- **Current Structure**:
  - Lines 32–44: Problem/validation banner.
  - Lines 47–56: Content textarea (`data.content`).
  - Lines 58–94: Collapsible "Message Identity (Optional)" (Username, Avatar URL, Thread name).
  - Lines 97–109: Conditionally embeds `<ComponentPalette />` and `<LayersPanel />` if `isV2`.
  - Lines 112–140: Embeds section with "Add embed" button and `<EmbedEditor />` list.
- **Critical Gap**: In Discohook, visual Action Rows are a core section directly below embeds in the message editor. Currently, `MessageEditor.tsx` has NO Action Row section!

### 1.2 `DiscohookComponentsEditor.tsx` (`hoho_manager/client/src/components/editor/DiscohookComponentsEditor.tsx`)
- **Role**: Visual Action Row container and button builder.
- **Current Status**: **Orphaned** (0 imports in the repository).
- **Features Implemented**:
  - Filters root components: `actionRows = components.filter(c => c.type === ComponentType.ActionRow)`.
  - Cap of 5 Action Rows (`actionRows.length < 5`).
  - Row header with Row #, item count badge (`rowChildren.length/5 items`), Move Up (`ChevronUp`), Move Down (`ChevronDown`), Duplicate (`Copy`), and Delete (`Trash2`).
  - Horizontal pill list for row children with style color dot, label, quick delete, and click-to-select (`select({ kind: "component", id: child._id })`).
  - "Add Button" and "Add Select Menu" buttons.
- **Flaws to Remediate**:
  1. No horizontal reordering of buttons inside a row (no Left / Right move controls).
  2. No Action Flow badges on pills (no indication whether a button triggers an ephemeral reply, adds a role, opens a modal, or has a link).
  3. Select menus render as broken button pills: `getStyleBadge(child.style)` returns default; `child.label` is undefined for select menus (selects have `placeholder`); only `StringSelect` is offered in the add button.
  4. Only inspects root components; ignores Action Rows nested inside Component V2 `Container` nodes.

### 1.3 `ComponentPalette.tsx` (`hoho_manager/client/src/components/editor/ComponentPalette.tsx`)
- **Role**: Catalog of available Component V2 blocks.
- **Groups**:
  - *Content*: Text Display (10), Section (9), Media Gallery (12), File (13).
  - *Layout*: Separator (14), Container (17).
  - *Interactive*: Action Row (1), Button (2), String Select (3), User Select (5), Role Select (6), Mentionable Select (7), Channel Select (8).
- **Behavior**: Selection-aware (`selected = findComponent(components, selection.id)`). Disables invalid types based on `canNestIn` and `canAddToActionRow`.
- **Deduplication Gap**: Currently rendered in `App.tsx:656` AND in `MessageEditor.tsx:104` AND in `Sidebar.tsx:52`. It should live cleanly in the Left Sidebar ("Build" tab).

### 1.4 `LayersPanel.tsx` (`hoho_manager/client/src/components/editor/LayersPanel.tsx`)
- **Role**: Recursive treeview of the component hierarchy (`LayerRow`).
- **Features**: Indented tree nodes (`style={{ marginLeft: depth * 12 }}`), Move Up/Down, Duplicate, Delete, selection highlights.
- **Deduplication Gap**: Duplicated in `MessageEditor.tsx:106` AND `App.tsx:662` AND `Sidebar.tsx:55`. Belongs in the Left Sidebar ("Layers" tab).

### 1.5 `ComponentForms.tsx` & `PropertyPanel.tsx` (`hoho_manager/client/src/components/editor/`)
- `ComponentForms.tsx`:
  - `ActionRowForm` (lines 159–195): Extremely basic placeholder (shows control count and "Add Button"/"Add Select").
  - `ButtonForm` (lines 200–248): Configures Label, Style, URL (if Link), SKU ID (if Premium), Disabled.
  - `StringSelectForm` (lines 250–337): Configures Placeholder, Options list (label, value), Min/Max values.
  - `EntitySelectForm` (lines 340–372): Configures Placeholder, Min/Max values for User/Role/Channel/Mentionable select menus.
- `PropertyPanel.tsx` vs `ComponentEditorModal` (`App.tsx:254–364`):
  - When `selection.kind === "component"`, `ComponentEditorModal` opens with two tabs: "Component Properties" and "Action Flow (When Clicked)" (`FlowBuilder`).
  - This flow works smoothly for editing button/select properties and flows.

---

## 2. Action Rows: Deep Dive into Nesting, Badges, and Reordering

### 2.1 Discord Rules & Limits
- **Row limit**: Maximum 5 Action Rows per message (or container).
- **Row contents**:
  - Up to 5 Buttons, OR
  - Exactly 1 Select Menu (String, User, Role, Channel, or Mentionable).
- Buttons and Select Menus cannot coexist in the same Action Row.

### 2.2 Button Styles & Visual Badges
In `hoho_manager/shared/src/constants.ts`:
- `Primary` (1): Discord Blurple (`#5865f2`)
- `Secondary` (2): Discord Grey (`#4e5058`)
- `Success` (3): Discord Green (`#23a55a`)
- `Danger` (4): Discord Red (`#da373c`)
- `Link` (5): Grey (`#4e5058`) with `ExternalLink` icon
- `Premium` (6): Discord Store item

### 2.3 Visual Action Flow Badges
Currently, pills only show the style color dot and label. Users cannot tell what a button does without clicking it.
**Recommended Badge Addition**:
By inspecting `flows[child.custom_id]` from `useActionStore`:
- If `child.style === ButtonStyle.Link`: show `🔗 Link` badge.
- If flow exists and has an `open_modal` step: show `📋 Modal` badge (amber/blue).
- If flow has 1+ other steps: show `⚡ Action` badge or `⚡ N steps` badge (purple/blurple).
- If no flow (`custom_id === "action:dud"` or empty): show subtle muted `Dud` or `No Action` indicator.

### 2.4 Button Horizontal Reordering
- The store already implements `moveComponentById(id: string, direction: number, parentId?: string | null)`:
  - Inside `useMessageStore.ts:310`, it calls `moveInTree(components, id, direction, parentId)`.
  - For a button inside an Action Row: `moveComponentById(buttonId, -1, rowId)` moves it left; `moveComponentById(buttonId, 1, rowId)` moves it right!
- **UI Enhancement**:
  Add `ChevronLeft` and `ChevronRight` buttons to the button pill hover overlay or pill actions:
  ```tsx
  <button
    type="button"
    disabled={itemIndex === 0}
    onClick={(e) => {
      e.stopPropagation();
      moveComponentById(child._id, -1, row._id);
    }}
    title="Move Left"
    className="p-0.5 rounded hover:bg-[#35373c] text-[#949ba4] disabled:opacity-20"
  >
    <ChevronLeft size={12} />
  </button>
  <button
    type="button"
    disabled={itemIndex === rowChildren.length - 1}
    onClick={(e) => {
      e.stopPropagation();
      moveComponentById(child._id, 1, row._id);
    }}
    title="Move Right"
    className="p-0.5 rounded hover:bg-[#35373c] text-[#949ba4] disabled:opacity-20"
  >
    <ChevronRight size={12} />
  </button>
  ```

### 2.5 Full Select Menu Support in Action Rows
Currently `DiscohookComponentsEditor.tsx` only offers `addActionRowChild(row._id, ComponentType.StringSelect)`.
When rendered:
- A select menu has `placeholder` instead of `label`.
- It should render as a wide pill or card:
  - Select icon (`ListFilter` for String, `UserRound` for User, `Shield` for Role, `Hash` for Channel, `AtSign` for Mentionable).
  - Type badge: e.g. `String Select` / `Role Select`.
  - Placeholder text: e.g. `"${child.placeholder || 'Select an option'}"`.
  - Option count badge (for StringSelect: `${child.options?.length || 0} options`).
- Add Select Menu should provide a dropdown or selection modal with all 5 types:
  - String Select (3)
  - User Select (5)
  - Role Select (6)
  - Channel Select (8)
  - Mentionable Select (7)

### 2.6 Nested Action Rows (Component V2 Containers)
In Components V2, an Action Row can sit inside a `Container` (`CONTAINER_CHILD_TYPES` includes `ComponentType.ActionRow`).
- When gathering Action Rows:
  ```ts
  // Collect both top-level action rows and action rows nested in containers
  const getAllActionRows = (components: ComponentNode[]): Array<{ row: ComponentNode; parentId: string | null }> => {
    const rows: Array<{ row: ComponentNode; parentId: string | null }> = [];
    for (const comp of components) {
      if (comp.type === ComponentType.ActionRow) {
        rows.push({ row: comp, parentId: null });
      } else if (comp.type === ComponentType.Container && Array.isArray(comp.components)) {
        for (const child of comp.components) {
          if (child.type === ComponentType.ActionRow) {
            rows.push({ row: child, parentId: comp._id ?? null });
          }
        }
      }
    }
    return rows;
  };
  ```
  This allows `DiscohookComponentsEditor` to display and manage all Action Rows, with a label indicating whether a row is top-level or inside a container card!

---

## 3. Modals: Deep Dive into Creation, Configuration, and Intuitive Building

### 3.1 Interaction Lifecycle of a Discord Modal
1. **Trigger**: User clicks a button or select menu in Discord.
2. **Callback**: Server action executor matches `custom_id` and runs `openModal.ts` (`server/src/actions/openModal.ts`).
3. **Discord Response**: Returns `InteractionResponseType.Modal: 9`:
   ```json
   {
     "type": 9,
     "data": {
       "custom_id": "app_modal",
       "title": "Application Form",
       "components": [
         {
           "type": 1,
           "components": [
             {
               "type": 4,
               "custom_id": "field_reason",
               "label": "Why should we accept you?",
               "style": 2,
               "placeholder": "Explain...",
               "required": true
             }
           ]
         }
       ]
     }
   }
   ```
4. **Submission**: User submits the modal dialog on Discord. Discord dispatches `InteractionType.ModalSubmit: 5` with `custom_id: "app_modal"`.
5. **Variable Extraction** (`server/src/services/actionExecutor.ts:111–126`):
   - Extracts all text input values:
     ```ts
     variables[comp.custom_id] = val;
     variables[`input.${comp.custom_id}`] = val;
     variables[`modal.${comp.custom_id}`] = val;
     ```
6. **Execution of Next Steps**:
   - `actionExecutor` looks up the registered flow for `app_modal` (which was registered by `toRegistrations()` from `open_modal`'s `config.then` branch).
   - Executes follow-up actions like `send_message`, `send_dm`, `add_role`, where messages can use templates like `Application submitted by {{user.mention}}: {{field_reason}}`!

### 3.2 What Makes Modal Building Intuitive?
Currently in `StepList.tsx` (lines 190–325), `open_modal` is just a list of input boxes. To make it **highly intuitive**:
1. **Interactive Discord Modal Mockup / Preview**:
   - Add a "Discord Modal Preview" card side-by-side or below the question builder.
   - Shows a Discord modal window with:
     - Window bar: Modal Title and close 'X'.
     - Inputs styled with Discord dark palette:
       - Field label in uppercase/bold with red `*` when required.
       - Text input (single-line or textarea) with placeholder.
       - Discord character limits.
     - Bottom buttons: "Cancel" and Blurple "Submit".
   - As the user types labels or placeholders, the preview updates in real-time!
2. **Question Reordering**:
   - Currently, if a user wants question 2 to become question 1, they have to retype it.
   - Adding `ChevronUp` and `ChevronDown` buttons on each question card allows instant reordering:
     ```tsx
     const moveInput = (from: number, to: number) => {
       if (to < 0 || to >= inputFields.length) return;
       const next = [...inputFields];
       const [moved] = next.splice(from, 1);
       next.splice(to, 0, moved);
       updateInputs(next);
     };
     ```
3. **Advanced Input Options**:
   - Add Min Length (`min_length`) and Max Length (`max_length`) inputs (1–4000).
   - Add Default Pre-filled Value (`value`) input.
4. **Variable Help Badges**:
   - Show a visible pill on each question: `Variable: {{customId}}`.
   - Tooltip / hint: "In the 'When Modal is Submitted' actions below, use `{{customId}}` to include the user's answer."
5. **Modal Presets**:
   - Quick preset buttons: "Support Ticket", "Staff Application", "Bug Report", "User Feedback".
   - Clicking pre-fills Title, custom IDs, and standard questions.

---

## 4. Integration with Store & Payload Generation

### 4.1 Data Model
- `MessageData` (`shared/src/types.ts:112`):
  ```ts
  export interface MessageData {
    content: string;
    embeds: EmbedData[];
    components: ComponentNode[];
    username: string;
    avatar_url: string;
    thread_name: string;
  }
  ```
- `ComponentNode` (`shared/src/types.ts:80`):
  ```ts
  export interface ComponentNode {
    _id?: string;
    _action_custom_id?: string;
    type: number;
    content?: string;
    media?: EmbedMedia;
    file?: EmbedMedia;
    items?: GalleryItem[];
    accessory?: ComponentNode;
    components?: ComponentNode[];
    accent_color?: number | null;
    divider?: boolean;
    spacing?: number;
    style?: number;
    label?: string;
    custom_id?: string;
    url?: string;
    sku_id?: string;
    disabled?: boolean;
    placeholder?: string;
    min_values?: number;
    max_values?: number;
    options?: SelectOption[];
  }
  ```

### 4.2 Payload Generation (`toDiscordPayload`)
In `client/src/utils/discord.ts:63–92`:
- In `mode === "classic"`:
  ```ts
  if (data.content) payload.content = data.content;
  if (data.embeds.length > 0) payload.embeds = stripInternal(data.embeds);
  const classicComponents = data.components.filter(
    (component) => component.type === ComponentType.ActionRow
  );
  if (classicComponents.length > 0) payload.components = stripInternal(classicComponents);
  ```
- In `mode === "v2"`:
  ```ts
  payload.components = stripInternal(data.components ?? []);
  payload.flags = MessageFlags.IsComponentsV2;
  ```
- `stripInternal()` drops all `_id` and `_*` internal properties cleanly.

### 4.3 Action Flows & Registration
In `client/src/store/actionStore.ts:287–314`:
- `toRegistrations()` extracts all flows keyed by `customId`.
- When an `open_modal` step has a `then` branch:
  ```ts
  if (step.type === "open_modal" && step.config?.then && Array.isArray(step.config.then)) {
    const modalCustomId = step.config.customId?.trim();
    if (modalCustomId) {
      registrations.push({
        customId: modalCustomId,
        steps: step.config.then.map(stripStep),
      });
    }
  }
  ```
- Dispatched via `useSend.ts:61` as `flows: useActionStore.getState().toRegistrations()` to `/api/send`.
- Fully supported by server `actionRepository.registerFlows()`.

---

## 5. Comprehensive Gap Analysis

| ID | Issue | Location | User Impact | Fix Strategy |
|---|---|---|---|---|
| **GAP-AR1** | `DiscohookComponentsEditor` is unmounted | `DiscohookComponentsEditor.tsx` / `MessageEditor.tsx` | Visual Action Rows cannot be built or viewed in the main editor | Import and mount `<DiscohookComponentsEditor />` in `MessageEditor.tsx` directly beneath embeds |
| **GAP-AR2** | Buttons cannot be reordered horizontally | `DiscohookComponentsEditor.tsx:136–178` | Users cannot reorder buttons within a row without deleting and re-adding | Add Move Left / Move Right buttons using `moveComponentById(child._id, -1, row._id)` |
| **GAP-AR3** | Button pills lack action badges | `DiscohookComponentsEditor.tsx:136–178` | Users cannot see which buttons have flows/modals attached | Connect to `useActionStore.flows` and display `⚡ Flow`, `📋 Modal`, or `🔗 Link` badges |
| **GAP-AR4** | Select menus render broken in rows | `DiscohookComponentsEditor.tsx:136–178` | Select menus display as "Untitled Button" with broken badge; only StringSelect supported | Add full support for all 5 select types with distinct select cards displaying type, placeholder, and option count |
| **GAP-AR5** | Container-nested Action Rows ignored | `DiscohookComponentsEditor.tsx:28` | In V2 mode, Action Rows inside Containers disappear from builder | Recursively search for Action Rows across root and containers |
| **GAP-MD1** | No visual preview for Modals | `StepList.tsx:190–325` | Users cannot see what the modal looks like to Discord members | Add a visual Discord Modal Mockup preview component in `StepList.tsx` |
| **GAP-MD2** | Modal inputs cannot be reordered | `StepList.tsx:265–320` | Users cannot reorder modal questions | Add Move Up / Move Down buttons to each question card |
| **GAP-MD3** | Missing modal input length controls | `StepList.tsx:265–320` | Cannot set min/max character lengths or pre-filled defaults | Add inputs for `min_length`, `max_length`, and default `value` |
| **GAP-MD4** | Missing variable mapping guidance | `StepList.tsx:265–320` | Users don't know how to use submitted modal values in follow-up actions | Add `Variable: {{key}}` badge and contextual explanation of `{input.key}` syntax |
| **GAP-UI1** | Duplicate palettes & layers | `MessageEditor.tsx:97–109` vs `App.tsx:640` | Clutters editor and violates Discohook layout clone | Remove duplicate palettes from `MessageEditor.tsx`; keep them in dedicated sidebar/drawer |

---

## 6. Concrete Implementation Plan for the Worker

### Phase 1: Enhance `DiscohookComponentsEditor.tsx`
1. **Update Imports & Store Hooks**:
   - Import `useActionStore` to inspect `flows[child.custom_id]`.
   - Import `ChevronLeft`, `ChevronRight`, `Sparkles`, `ListFilter`, `UserRound`, `Shield`, `Hash`, `AtSign`, `ExternalLink`.
2. **Support Horizontal Button Reordering**:
   - In each button pill, render Left / Right arrows:
     - Left disabled if index is 0.
     - Right disabled if index is `rowChildren.length - 1`.
     - Calls `moveComponentById(child._id, direction, row._id)`.
3. **Display Action & Modal Badges**:
   - Inspect `flows[child.custom_id]`:
     - If `child.style === ButtonStyle.Link`: badge `🔗 Link`.
     - Else if flow contains `open_modal` step: badge `📋 Modal`.
     - Else if flow has 1+ steps: badge `⚡ Flow (${steps.length})`.
     - Else: subtle badge `No Action`.
4. **Render Select Menus Properly**:
   - Check if `child.type` is in select menu types.
   - Render a full-width select card:
     - Shows menu type icon (`ListFilter`, `UserRound`, etc.) and label.
     - Shows placeholder string.
     - For string select: shows option count badge (`${child.options?.length || 0} options`).
     - Delete button.
5. **Multi-Select Add Menu**:
   - Provide a dropdown or button group for adding select menus:
     - String Select (3)
     - User Select (5)
     - Role Select (6)
     - Channel Select (8)
     - Mentionable Select (7)
6. **Support Container-Nested Rows**:
   - Scan root components and containers for Action Rows so none are missed in V2 mode.

### Phase 2: Mount `DiscohookComponentsEditor` in `MessageEditor.tsx`
1. In `hoho_manager/client/src/components/editor/MessageEditor.tsx`:
   - Import `DiscohookComponentsEditor`.
   - Remove duplicate `<ComponentPalette />` and `<LayersPanel />` from lines 97–109.
   - Insert `<DiscohookComponentsEditor />` as a dedicated section below Embeds:
     ```tsx
     {/* Action Rows & Interactive Components */}
     <section className="bg-[#232428] rounded border border-[#1e1f22] p-2.5 space-y-2.5">
       <DiscohookComponentsEditor />
     </section>
     ```
   - This makes Action Rows immediately accessible in both Classic and V2 modes!

### Phase 3: Enhance Modal Builder in `StepList.tsx`
1. **Add Discord Modal Live Preview Component (`DiscordModalPreview`)**:
   - Displays a Discord dialog mockup:
     - Header: Modal Title (or "Application Form") + Close 'X'.
     - Inputs: Each input rendered with:
       - Upper case label + red asterisk `*` if required.
       - Discord dark input box (`bg-[#1e1f22] border border-[#3f4147] rounded p-2 text-xs text-[#dbdee1]`).
       - Short (single-line) vs Paragraph (multi-line textarea with resize-none and 0/4000 counter).
       - Placeholder text.
     - Footer: "Cancel" button + Blurple "Submit" button (`bg-[#5865f2]`).
2. **Add Reordering to Modal Inputs**:
   - Add Move Up (`ChevronUp`) and Move Down (`ChevronDown`) buttons to each modal input card.
   - Swaps input array items and updates config.
3. **Add Input Controls**:
   - Min Length / Max Length number inputs.
   - Default pre-filled value input.
4. **Add Variable Syntax Pills & Help Banner**:
   - Show `Variable: {{${input.customId}}}` pill on each input.
   - Banner explaining: "In follow-up actions (Send Message, DM, Reply), use `{{${input.customId}}}` or `{{input.${input.customId}}}` to insert the user's submitted text."

### Phase 4: Deduplicate Layout in `App.tsx` & `Sidebar.tsx`
1. Ensure `Sidebar.tsx` holds the Component Palette and Layers tree for structural V2 building.
2. In `App.tsx`, keep the unified 3-pane layout clean without duplicate palettes inside the message accordion.

### Phase 5: Verification & Testing
1. Add new automated tests in `hoho_manager/client/tests/layout_discohook.test.ts`:
   - Test Action Row button horizontal reordering via `moveComponentById(id, direction, rowId)`.
   - Test select menu insertion across all 5 select types.
   - Test modal input reordering and formatting in `formatModalComponents`.
   - Test modal variable registration in `toRegistrations()`.
2. Run `npm test -- --run` across both client and server workspaces to confirm 100% pass rate.

---

## 7. Code Blueprints for Implementation

### Blueprint A: Button Pill with Horizontal Reordering & Badges (`DiscohookComponentsEditor.tsx`)
```tsx
{rowChildren.map((child: ComponentNode, itemIndex: number) => {
  const isSelected = selection?.kind === "component" && selection.id === child._id;
  const isButton = child.type === ComponentType.Button;
  const styleInfo = getStyleBadge(child.style);
  const isLink = isLinkButton(child);
  const flow = flows[child.custom_id ?? ""] ?? [];
  const hasModal = flow.some(s => s.type === "open_modal");
  const hasActions = flow.length > 0;

  return (
    <div
      key={child._id}
      onClick={() => child._id && select({ kind: "component", id: child._id })}
      className={`group relative flex items-center gap-2 pl-2 pr-1.5 py-1.5 rounded-md border cursor-pointer select-none transition-all ${
        isSelected
          ? "bg-[#5865f2]/20 border-[#5865f2] shadow-sm"
          : "bg-[#2b2d31] hover:bg-[#35373c] border-[#1e1f22] hover:border-[#383a40]"
      }`}
    >
      {/* Style color pill */}
      <div className={`w-3.5 h-3.5 rounded flex items-center justify-center text-white text-[9px] ${styleInfo.bg}`}>
        {isLink && <ExternalLink size={9} />}
      </div>

      {/* Label / Name */}
      <span className="text-xs font-semibold text-white max-w-[120px] truncate">
        {child.label || (child.placeholder ? child.placeholder : componentLabel(child))}
      </span>

      {/* Action / Modal flow badge */}
      {isLink ? (
        <span className="text-[9px] bg-[#4e5058] text-[#dbdee1] px-1 py-0.5 rounded font-mono">Link</span>
      ) : hasModal ? (
        <span className="text-[9px] bg-[#f0b232]/20 text-[#f0b232] border border-[#f0b232]/30 px-1 py-0.5 rounded font-semibold">Modal</span>
      ) : hasActions ? (
        <span className="text-[9px] bg-[#5865f2]/20 text-[#5865f2] border border-[#5865f2]/30 px-1 py-0.5 rounded font-semibold">⚡ Flow</span>
      ) : null}

      {/* Reorder Buttons: Left & Right */}
      <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          type="button"
          disabled={itemIndex === 0}
          onClick={(e) => {
            e.stopPropagation();
            if (child._id && row._id) moveComponentById(child._id, -1, row._id);
          }}
          className="p-0.5 rounded hover:bg-[#1e1f22] text-[#949ba4] hover:text-white disabled:opacity-20"
          title="Move Left"
        >
          <ChevronLeft size={12} />
        </button>
        <button
          type="button"
          disabled={itemIndex === rowChildren.length - 1}
          onClick={(e) => {
            e.stopPropagation();
            if (child._id && row._id) moveComponentById(child._id, 1, row._id);
          }}
          className="p-0.5 rounded hover:bg-[#1e1f22] text-[#949ba4] hover:text-white disabled:opacity-20"
          title="Move Right"
        >
          <ChevronRight size={12} />
        </button>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            if (child._id) removeComponentById(child._id);
          }}
          className="p-0.5 hover:text-[#f28b8b] text-[#949ba4] transition-colors ml-0.5"
          title="Remove"
        >
          <Trash2 size={12} />
        </button>
      </div>
    </div>
  );
})}
```

### Blueprint B: Discord Modal Live Preview Mockup (`StepList.tsx`)
```tsx
const DiscordModalPreview: React.FC<{
  title: string;
  inputs: ModalInputField[];
}> = ({ title, inputs }) => {
  return (
    <div className="bg-[#313338] border border-[#1e1f22] rounded-lg shadow-2xl overflow-hidden font-sans max-w-md w-full mx-auto my-3">
      {/* Modal Header */}
      <div className="px-4 py-3 bg-[#2b2d31] border-b border-[#1e1f22] flex items-center justify-between">
        <span className="text-sm font-bold text-white tracking-wide truncate">
          {title.trim() || "Submission Form"}
        </span>
        <span className="text-[#949ba4] text-xs">✕</span>
      </div>

      {/* Modal Body */}
      <div className="p-4 space-y-3 max-h-64 overflow-y-auto custom-scrollbar">
        {inputs.length === 0 ? (
          <p className="text-xs text-[#949ba4] text-center py-4 italic">
            No inputs configured yet.
          </p>
        ) : (
          inputs.map((inp, idx) => (
            <div key={idx} className="space-y-1">
              <label className="text-[11px] font-bold uppercase tracking-wider text-[#b5bac1] flex items-center gap-1">
                {inp.label.trim() || `Question ${idx + 1}`}
                {inp.required !== false && <span className="text-[#da373c]">*</span>}
              </label>
              {inp.style === 2 ? (
                <textarea
                  readOnly
                  rows={2}
                  placeholder={inp.placeholder || "Type your answer..."}
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded p-2 text-xs text-[#dbdee1] placeholder-[#6d6f78] resize-none pointer-events-none"
                />
              ) : (
                <input
                  readOnly
                  type="text"
                  placeholder={inp.placeholder || "Type your answer..."}
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded p-2 text-xs text-[#dbdee1] placeholder-[#6d6f78] pointer-events-none"
                />
              )}
            </div>
          ))
        )}
      </div>

      {/* Modal Footer */}
      <div className="px-4 py-3 bg-[#2b2d31] border-t border-[#1e1f22] flex items-center justify-end gap-2">
        <span className="px-3 py-1 text-xs text-white hover:underline cursor-pointer">
          Cancel
        </span>
        <button
          type="button"
          disabled
          className="px-4 py-1.5 rounded bg-[#5865f2] text-white text-xs font-semibold shadow opacity-90 cursor-default"
        >
          Submit
        </button>
      </div>
    </div>
  );
};
```
