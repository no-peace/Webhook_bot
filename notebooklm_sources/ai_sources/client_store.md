# Repository Context Group: client_store
# Source Repository: no-peace/Hoho_manager

### File: `client/src/store/actionStore.test.ts`
```ts
import { beforeEach, describe, expect, it } from "vitest";
import type { FlowStep } from "@dmb/shared";
import { createStep, useActionStore } from "./actionStore";

/**
 * Flow serialisation.
 *
 * A `check` step keeps its branches inside its own config, so the wire format is
 * a tree living in a flat `action_definitions` row. Two things can go wrong
 * quietly there: editor-only `_id`s leak into the database, and nested steps get
 * dropped because a shallow map never looked inside `config.then` / `config.else`.
 * Both are pinned here.
 */

const stopStep = (content: string): FlowStep => {
  const step = createStep("stop");
  return { ...step, config: { ...step.config, content } };
};

const checkStep = (then: FlowStep[], elseSteps: FlowStep[]): FlowStep => {
  const step = createStep("check");
  return { ...step, config: { ...step.config, then, else: elseSteps } };
};

beforeEach(() => {
  useActionStore.getState().reset();
});

describe("createStep defaults", () => {
  it("gives a check step empty branches so it persists a branchable shape", () => {
    const step = createStep("check");
    expect(step.config.then).toEqual([]);
    expect(step.config.else).toEqual([]);
    expect(step.config.function).toBe("equals");
  });

  it("gives a set_variable step a static mode", () => {
    expect(createStep("set_variable").config.varType).toBe("static");
  });

  it("gives a stop step an empty content field", () => {
    expect(createStep("stop").config).toEqual({ content: "" });
  });
});

describe("toRegistrations — nested branches", () => {
  it("keeps branch steps and drops every editor id, at every depth", () => {
    const inner = checkStep([stopStep("inner-then")], [stopStep("inner-else")]);
    const outer = checkStep([inner], [stopStep("outer-else")]);

    useActionStore.getState().setFlow("action:check", [outer]);

    const [registration] = useActionStore.getState().toRegistrations();
    expect(registration).toBeDefined();

    // Nothing editor-only survived, at the top level or inside the branches.
    expect(JSON.stringify(registration)).not.toContain("_id");

    const top = registration!.steps[0]!;
    expect(top.type).toBe("check");

    const thenBranch = top.config.then as FlowStep[];
    expect(thenBranch).toHaveLength(1);
    expect(thenBranch[0]!.type).toBe("check");
    expect(thenBranch[0]!.config.else).toEqual([{ type: "stop", config: { content: "inner-else" } }]);
  });

  it("normalises a hand-edited branch that is not an array to an empty one", () => {
    const damaged: FlowStep = {
      type: "check",
      config: { function: "equals", conditions: [], then: "nope", else: null },
    };

    useActionStore.getState().setFlow("action:check", [damaged]);
    const [registration] = useActionStore.getState().toRegistrations();

    expect(registration!.steps[0]!.config.then).toEqual([]);
    expect(registration!.steps[0]!.config.else).toEqual([]);
  });
});

describe("loadFromList / toList round trip", () => {
  it("restores a nested flow and re-serialises it identically", () => {
    const original = checkStep([stopStep("yes")], [stopStep("no")]);
    useActionStore.getState().setFlow("action:check", [original]);

    // What a template save would write, then read back on load.
    const stored = useActionStore.getState().toList();
    useActionStore.getState().reset();
    useActionStore.getState().loadFromList(stored);

    const reloaded = useActionStore.getState().getFlow("action:check");
    expect(reloaded).toHaveLength(1);
    // The editor needs ids again for React keys and reordering.
    expect(reloaded[0]!._id).toBeTruthy();

    expect(useActionStore.getState().toList()).toEqual(stored);
  });
});

```

### File: `client/src/store/actionStore.ts`
```ts
import { create } from "zustand";
import type {
  ActionHandlerMeta,
  ActionType,
  FlowRegistration,
  FlowStep,
  StoredActionDefinition,
} from "@dmb/shared";
import { api } from "../api/client";
import { uid } from "../utils/constants";

/**
 * Action flows, keyed by the component `custom_id` they belong to.
 *
 * A flow is an **ordered list of steps** (Discohook-style): a button can add a
 * role, then DM the user, then reply — all from one click. Two representations
 * have to be kept in sync:
 *
 *   - In memory: `FlowStep[]`, with editor-only `_id`s so the list can reorder.
 *   - On the wire: a flat list of `StoredActionDefinition`s carrying an
 *     `execution_order`, which is what the server reads back on a click.
 *
 * `custom_id` is capped at 100 characters, which is far too small for a chain, so
 * only the *first* step's params can ride inline there. Everything else is
 * registered server-side: saved templates persist their steps, and ad-hoc sends
 * register theirs through `/api/send` (see {@link toRegistrations}).
 */

/**
 * Used until `/api/config` responds, and if the backend is unreachable.
 * Kept aligned with `server/src/actions/index.ts`.
 */
const FALLBACK_TYPES: ActionHandlerMeta[] = [
  { type: "dud", description: "Do nothing" },
  { type: "add_role", description: "Give the member who clicked a role" },
  { type: "remove_role", description: "Take a role away from the member who clicked" },
  { type: "toggle_role", description: "Add the role if absent, remove it if present" },
  { type: "send_ephemeral_reply", description: "Show the clicker a private message" },
  { type: "send_dm", description: "DM the member who clicked" },
  { type: "open_modal", description: "Open a form the user can fill in" },
  { type: "send_message", description: "Send a message as the bot" },
  { type: "send_webhook_message", description: "Send a message through a saved webhook" },
  { type: "delete_message", description: "Delete the message carrying the component" },
  { type: "create_thread", description: "Start a thread from the message" },
  { type: "wait", description: "Pause before the next step" },
  { type: "set_variable", description: "Store a value for later steps" },
  { type: "check", description: "Branch or stop the flow based on a condition" },
  { type: "stop", description: "End the flow here" },
];

/** The two config keys a `check` step stores its sub-chains under. */
export const BRANCH_KEYS = ["then", "else"] as const;

/** A sensible default config for a freshly added step. */
const defaultConfig = (type: ActionType): Record<string, unknown> => {
  switch (type) {
    case "add_role":
    case "remove_role":
    case "toggle_role":
      return { roleId: "" };
    case "send_ephemeral_reply":
    case "send_dm":
      return { content: "" };
    case "open_modal":
      return { title: "Form", customId: "modal:form" };
    case "send_message":
      return { content: "" };
    case "send_webhook_message":
      return { content: "" };
    case "create_thread":
      return { name: "" };
    case "wait":
      return { seconds: 1 };
    case "set_variable":
      return { name: "", value: "", varType: "static" };
    case "check":
      // Empty branches make the server fall back to "a failed check ends the
      // flow", which is the pre-branching behaviour — so a step is never
      // silently a no-op while the user is still wiring it up.
      return {
        function: "equals",
        conditions: [{ a: "", b: "", loose: false }],
        then: [],
        else: [],
      };
    case "stop":
      return { content: "" };
    default:
      return {};
  }
};

export const createStep = (type: ActionType = "dud"): FlowStep => ({
  _id: uid(),
  type,
  config: defaultConfig(type),
});

export interface ActionState {
  actionTypes: ActionHandlerMeta[];
  typesLoaded: boolean;
  /** `{ [customId]: FlowStep[] }` — the ordered chain for each component. */
  flows: Record<string, FlowStep[]>;

  fetchActionTypes(): Promise<void>;

  getFlow(customId: string): FlowStep[];
  setFlow(customId: string, steps: FlowStep[]): void;
  addStep(customId: string, type?: ActionType): void;
  updateStep(customId: string, index: number, patch: Partial<FlowStep>): void;
  removeStep(customId: string, index: number): void;
  moveStep(customId: string, index: number, direction: number): void;
  /** Move a flow when its component's `custom_id` changes. */
  renameFlow(oldCustomId: string, nextCustomId: string): void;
  removeFlow(customId: string): void;

  /** Flatten every flow for the template API. */
  toList(): StoredActionDefinition[];
  /** Rebuild flows from a loaded template, preserving step order. */
  loadFromList(list: StoredActionDefinition[]): void;
  /** Flows for an ad-hoc send, so the server can execute multi-step chains. */
  toRegistrations(): FlowRegistration[];

  reset(): void;
}

/**
 * Serialise one step, dropping editor-only `_id`s **recursively**.
 *
 * A `check` step carries its branches inside `config.then` / `config.else`, so a
 * shallow strip would leave nested `_id`s in the persisted JSON. The server
 * ignores them, but they would round-trip into the database and change every
 * time the editor reloaded, making template diffs noisy for no benefit.
 */
const stripStep = (step: FlowStep): { type: ActionType; config: Record<string, unknown> } => ({
  type: step.type,
  config: stripConfig(step.config ?? {}),
});

const stripConfig = (config: Record<string, unknown>): Record<string, unknown> => {
  const next: Record<string, unknown> = {};

  for (const [key, value] of Object.entries(config)) {
    if ((BRANCH_KEYS as readonly string[]).includes(key)) {
      next[key] = Array.isArray(value) ? value.map((entry) => stripStep(entry as FlowStep)) : [];
      continue;
    }
    next[key] = value;
  }

  return next;
};

/** Give every step — including nested branch steps — a fresh editor `_id`. */
const hydrateStep = (step: FlowStep): FlowStep => ({
  ...step,
  _id: step._id ?? uid(),
  config: hydrateConfig(step.config ?? {}),
});

const hydrateConfig = (config: Record<string, unknown>): Record<string, unknown> => {
  const next: Record<string, unknown> = { ...config };

  for (const key of BRANCH_KEYS) {
    const value = next[key];
    if (Array.isArray(value)) {
      next[key] = value.map((entry) => hydrateStep(entry as FlowStep));
    }
  }

  return next;
};

export const useActionStore = create<ActionState>()((set, get) => ({
  actionTypes: FALLBACK_TYPES,
  typesLoaded: false,
  flows: {},

  fetchActionTypes: async () => {
    try {
      const response = await api.config();
      if (Array.isArray(response.actionTypes) && response.actionTypes.length > 0) {
        set({ actionTypes: response.actionTypes, typesLoaded: true });
      }
    } catch {
      // Offline or backend down: the fallback list keeps the editor usable.
      set({ typesLoaded: false });
    }
  },

  getFlow: (customId) => get().flows[customId] ?? [],

  setFlow: (customId, steps) =>
    set((state) => {
      const flows = { ...state.flows };
      if (steps.length === 0) delete flows[customId];
      else flows[customId] = steps;
      return { flows };
    }),

  addStep: (customId, type = "dud") =>
    set((state) => ({
      flows: {
        ...state.flows,
        [customId]: [...(state.flows[customId] ?? []), createStep(type)],
      },
    })),

  updateStep: (customId, index, patch) =>
    set((state) => {
      const existing = state.flows[customId];
      if (!existing || !existing[index]) return {};

      const steps = [...existing];
      steps[index] = { ...steps[index], ...patch } as FlowStep;
      return { flows: { ...state.flows, [customId]: steps } };
    }),

  removeStep: (customId, index) =>
    set((state) => {
      const existing = state.flows[customId];
      if (!existing) return {};

      const steps = existing.filter((_, i) => i !== index);
      const flows = { ...state.flows };
      if (steps.length === 0) delete flows[customId];
      else flows[customId] = steps;
      return { flows };
    }),

  moveStep: (customId, index, direction) =>
    set((state) => {
      const existing = state.flows[customId];
      const target = index + direction;
      if (!existing || target < 0 || target >= existing.length) return {};

      const steps = [...existing];
      const a = steps[index];
      const b = steps[target];
      if (!a || !b) return {};
      steps[index] = b;
      steps[target] = a;
      return { flows: { ...state.flows, [customId]: steps } };
    }),

  renameFlow: (oldCustomId, nextCustomId) =>
    set((state) => {
      if (oldCustomId === nextCustomId) return {};
      const existing = state.flows[oldCustomId];
      if (!existing) return {};

      const flows = { ...state.flows };
      delete flows[oldCustomId];
      flows[nextCustomId] = existing;
      return { flows };
    }),

  removeFlow: (customId) =>
    set((state) => {
      if (!state.flows[customId]) return {};
      const flows = { ...state.flows };
      delete flows[customId];
      return { flows };
    }),

  toList: () =>
    Object.entries(get().flows).flatMap(([customId, steps]) =>
      steps.map((step, index) => ({
        customId,
        actionType: step.type,
        config: stripConfig(step.config ?? {}),
        executionOrder: index,
      })),
    ),

  loadFromList: (list) =>
    set(() => {
      const grouped: Record<string, FlowStep[]> = {};
      for (const item of list) {
        (grouped[item.customId] ??= []).push(
          hydrateStep({ type: item.actionType, config: item.config ?? {} }),
        );
      }
      // Order within each custom_id is whatever the server returned, which is
      // already sorted by execution_order.
      return { flows: grouped };
    }),

  toRegistrations: () =>
    Object.entries(get().flows)
      .filter(([, steps]) => steps.length > 0)
      .map(([customId, steps]) => ({ customId, steps: steps.map(stripStep) })),

  reset: () => set({ flows: {} }),
}));

export default useActionStore;

```

### File: `client/src/store/messageStore.ts`
```ts
import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  ComponentNode,
  DiscordMessagePayload,
  EmbedData,
  EmbedField,
  MessageData,
  TargetData,
} from "@dmb/shared";
import { ComponentType, DEFAULT_EMBED_COLOR, EDITOR_MODES, uid } from "../utils/constants";
import type { EditorMode } from "../utils/constants";
import { createComponent, newButton } from "../utils/componentsV2";
import { toDiscordPayload, validateMessage } from "../utils/discord";
import {
  findComponent,
  insertComponent,
  moveComponent as moveInTree,
  removeComponent as removeFromTree,
  updateComponent as updateInTree,
} from "../utils/tree";

/**
 * The message document — the single source of truth for both the editor and the
 * live preview.
 *
 * The shape mirrors Discord closely, with one editor-only addition: every embed
 * and component carries an `_id`. React keys, selection and updates all key off
 * it, so reordering components never causes an edit to land on the wrong element.
 * `stripInternal()` removes those ids at the payload boundary.
 *
 * Persisted to localStorage so a refresh (or a crash) never loses work.
 */

export type Selection =
  | { kind: "embed"; id: string }
  | { kind: "component"; id: string }
  | null;

export interface SendState {
  status: "idle" | "sending" | "success" | "error";
  error: string | null;
  result: unknown;
}

export interface LoadDocumentInput {
  data: MessageData;
  mode?: EditorMode;
  targets?: TargetData[];
}

export interface MessageState {
  mode: EditorMode;
  data: MessageData;
  targets: TargetData[];
  selection: Selection;
  send: SendState;

  setMode(mode: EditorMode): void;

  setField<K extends keyof MessageData>(key: K, value: MessageData[K]): void;
  setContent(content: string): void;

  addEmbed(): void;
  updateEmbed(id: string, patch: Partial<EmbedData>): void;
  removeEmbed(id: string): void;
  duplicateEmbed(id: string): void;
  moveEmbed(id: string, direction: number): void;
  addEmbedField(embedId: string): void;
  updateEmbedField(embedId: string, fieldId: string, patch: Partial<EmbedField>): void;
  removeEmbedField(embedId: string, fieldId: string): void;

  addComponent(type: number, parentId?: string | null): void;
  addActionRowChild(parentId: string, type?: number): void;
  updateComponentById(id: string, patch: Partial<ComponentNode>): void;
  removeComponentById(id: string): void;
  moveComponentById(id: string, direction: number, parentId?: string | null): void;
  duplicateComponentById(id: string): void;

  select(selection: Selection): void;

  setTargetUrl(index: number, url: string): void;
  addTarget(): void;
  removeTarget(index: number): void;

  setSendState(patch: Partial<SendState>): void;
  resetSendState(): void;

  reset(): void;
  load(input: LoadDocumentInput): void;

  getPayload(): DiscordMessagePayload;
  getValidationErrors(): string[];
}

const newEmbed = (): EmbedData => ({
  _id: uid(),
  title: "",
  description: "",
  color: DEFAULT_EMBED_COLOR,
  fields: [],
});

const newEmbedField = (): EmbedField => ({
  _id: uid(),
  name: "Field name",
  value: "Field value",
  inline: false,
});

const emptyData = (): MessageData => ({
  content: "",
  embeds: [],
  components: [],
  username: "",
  avatar_url: "",
  thread_name: "",
});

const idleSendState = (): SendState => ({ status: "idle", error: null, result: null });

/** Deep-copy a component tree with fresh editor ids. */
const reid = (component: ComponentNode): ComponentNode => ({
  ...(structuredClone(component) as ComponentNode),
  _id: uid(),
  ...(Array.isArray(component.components)
    ? { components: component.components.map(reid) }
    : {}),
  ...(Array.isArray(component.options)
    ? { options: component.options.map((option) => ({ ...option, _id: uid() })) }
    : {}),
  ...(Array.isArray(component.items)
    ? { items: component.items.map((item) => ({ ...item, _id: uid() })) }
    : {}),
});

export const useMessageStore = create<MessageState>()(
  persist(
    (set, get) => ({
      /* ── State ────────────────────────────────────────────────────────── */
      mode: EDITOR_MODES.CLASSIC,
      data: emptyData(),
      targets: [{ url: "" }],
      selection: null,
      send: idleSendState(),

      /* ── Mode ─────────────────────────────────────────────────────────── */

      setMode: (mode) => set({ mode, selection: null }),

      /* ── Scalar fields ────────────────────────────────────────────────── */

      setField: (key, value) => set((state) => ({ data: { ...state.data, [key]: value } })),

      setContent: (content) => get().setField("content", content),

      /* ── Embeds ───────────────────────────────────────────────────────── */

      addEmbed: () =>
        set((state) => {
          const embed = newEmbed();
          return {
            data: { ...state.data, embeds: [...state.data.embeds, embed] },
            selection: { kind: "embed", id: embed._id as string },
          };
        }),

      updateEmbed: (id, patch) =>
        set((state) => ({
          data: {
            ...state.data,
            embeds: state.data.embeds.map((embed) =>
              embed._id === id ? { ...embed, ...patch } : embed,
            ),
          },
        })),

      removeEmbed: (id) =>
        set((state) => ({
          data: {
            ...state.data,
            embeds: state.data.embeds.filter((embed) => embed._id !== id),
          },
          selection: state.selection?.id === id ? null : state.selection,
        })),

      duplicateEmbed: (id) =>
        set((state) => {
          const index = state.data.embeds.findIndex((embed) => embed._id === id);
          const source = state.data.embeds[index];
          if (index === -1 || !source) return {};

          const copy: EmbedData = {
            ...(structuredClone(source) as EmbedData),
            _id: uid(),
            fields: (source.fields ?? []).map((field) => ({ ...field, _id: uid() })),
          };

          const embeds = [...state.data.embeds];
          embeds.splice(index + 1, 0, copy);
          return {
            data: { ...state.data, embeds },
            selection: { kind: "embed", id: copy._id as string },
          };
        }),

      /** `direction` is -1 for up, +1 for down. */
      moveEmbed: (id, direction) =>
        set((state) => {
          const embeds = [...state.data.embeds];
          const index = embeds.findIndex((embed) => embed._id === id);
          const target = index + direction;
          const a = embeds[index];
          const b = embeds[target];
          if (index === -1 || !a || !b) return {};

          embeds[index] = b;
          embeds[target] = a;
          return { data: { ...state.data, embeds } };
        }),

      addEmbedField: (embedId) =>
        set((state) => ({
          data: {
            ...state.data,
            embeds: state.data.embeds.map((embed) =>
              embed._id === embedId
                ? { ...embed, fields: [...(embed.fields ?? []), newEmbedField()] }
                : embed,
            ),
          },
        })),

      updateEmbedField: (embedId, fieldId, patch) =>
        set((state) => ({
          data: {
            ...state.data,
            embeds: state.data.embeds.map((embed) =>
              embed._id === embedId
                ? {
                    ...embed,
                    fields: (embed.fields ?? []).map((field) =>
                      field._id === fieldId ? { ...field, ...patch } : field,
                    ),
                  }
                : embed,
            ),
          },
        })),

      removeEmbedField: (embedId, fieldId) =>
        set((state) => ({
          data: {
            ...state.data,
            embeds: state.data.embeds.map((embed) =>
              embed._id === embedId
                ? { ...embed, fields: (embed.fields ?? []).filter((field) => field._id !== fieldId) }
                : embed,
            ),
          },
        })),

      /* ── Components ───────────────────────────────────────────────────── */

      /**
       * Add a component from the palette.
       * @param parentId nest inside this component, else the top level
       */
      addComponent: (type, parentId = null) =>
        set((state) => {
          const component = createComponent(type);
          const { components } = insertComponent(state.data.components, parentId, component);
          return {
            data: { ...state.data, components },
            selection: { kind: "component", id: component._id as string },
          };
        }),

      /** Add a button or select into a specific ActionRow. */
      addActionRowChild: (parentId, type = ComponentType.Button) =>
        set((state) => {
          const child = type === ComponentType.Button ? newButton() : createComponent(type);
          const { components } = insertComponent(state.data.components, parentId, child);
          return {
            data: { ...state.data, components },
            selection: { kind: "component", id: child._id as string },
          };
        }),

      updateComponentById: (id, patch) =>
        set((state) => {
          const { components } = updateInTree(state.data.components, id, () => patch);
          return { data: { ...state.data, components } };
        }),

      removeComponentById: (id) =>
        set((state) => {
          const { components } = removeFromTree(state.data.components, id);
          return {
            data: { ...state.data, components },
            selection: state.selection?.id === id ? null : state.selection,
          };
        }),

      moveComponentById: (id, direction, parentId = null) =>
        set((state) => {
          const { components, found } = moveInTree(
            state.data.components,
            id,
            direction,
            parentId,
          );
          return found ? { data: { ...state.data, components } } : {};
        }),

      /**
       * Duplicate a component (and any children) with fresh ids, inserting it
       * directly after the original.
       */
      duplicateComponentById: (id) =>
        set((state) => {
          const source = findComponent(state.data.components, id);
          if (!source) return {};

          const copy = reid(source);
          const list = state.data.components;
          const index = list.findIndex((component) => component._id === id);

          let components: ComponentNode[];
          if (index !== -1) {
            components = [...list];
            components.splice(index + 1, 0, copy);
          } else {
            components = insertComponent(list, null, copy).components;
          }

          return {
            data: { ...state.data, components },
            selection: { kind: "component", id: copy._id as string },
          };
        }),

      /* ── Selection & targets ──────────────────────────────────────────── */

      select: (selection) => set({ selection }),

      setTargetUrl: (index, url) =>
        set((state) => {
          const targets = [...state.targets];
          targets[index] = { url };
          return { targets };
        }),

      addTarget: () => set((state) => ({ targets: [...state.targets, { url: "" }] })),

      removeTarget: (index) =>
        set((state) => ({ targets: state.targets.filter((_, i) => i !== index) })),

      /* ── Send state ───────────────────────────────────────────────────── */

      setSendState: (patch) => set((state) => ({ send: { ...state.send, ...patch } })),
      resetSendState: () => set({ send: idleSendState() }),

      /* ── Whole-document operations ────────────────────────────────────── */

      reset: () =>
        set({
          mode: EDITOR_MODES.CLASSIC,
          data: emptyData(),
          targets: [{ url: "" }],
          selection: null,
          send: idleSendState(),
        }),

      /** Replace the document (after importing a backup). */
      load: ({ data, mode, targets }) =>
        set({
          mode: mode ?? EDITOR_MODES.CLASSIC,
          data: { ...emptyData(), ...data },
          targets: targets && targets.length > 0 ? targets : [{ url: "" }],
          selection: null,
        }),

      /* ── Derived values ───────────────────────────────────────────────── */

      /** The exact body to send to Discord. */
      getPayload: () => toDiscordPayload(get().data, get().mode),

      /** Problems that would make Discord reject the message. */
      getValidationErrors: () => validateMessage(get().data, get().mode),
    }),
    {
      name: "dmb:message",
      // Only the document is worth persisting; transient send/selection state
      // should reset on reload.
      partialize: (state) => ({
        mode: state.mode,
        data: state.data,
        targets: state.targets,
      }),
      version: 1,
    },
  ),
);

export default useMessageStore;

```

### File: `client/src/store/profileStore.ts`
```ts
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { api, type BotProfile, type WebhookProfile } from "../api/client";
import { SEND_MODES } from "../utils/constants";
import type { SendModeValue } from "../utils/constants";

/**
 * Where a message is sent from, and the profiles available to send it with.
 *
 * Two modes exist side by side:
 *   - `webhook` — sent straight from the browser, no backend involved
 *   - `bot`     — proxied through `/api/send` so the token stays server-side
 *
 * The webhook URL is persisted for convenience. It *is* a credential, so it only
 * ever lives in this browser's localStorage and is never sent anywhere except
 * Discord itself.
 */
export interface ProfileState {
  sendMode: SendModeValue;
  webhookUrl: string;
  channelId: string;
  botProfileId: number | null;
  threadId: string;

  webhookProfiles: WebhookProfile[];
  botProfiles: BotProfile[];
  status: "idle" | "loading" | "error";
  error: string | null;

  setSendMode(mode: SendModeValue): void;
  setWebhookUrl(url: string): void;
  setChannelId(channelId: string): void;
  setBotProfileId(id: number | null): void;
  setThreadId(threadId: string): void;

  fetchProfiles(): Promise<void>;
  useWebhookProfile(profile: WebhookProfile): void;
  reset(): void;
}

export const useProfileStore = create<ProfileState>()(
  persist(
    (set, get) => ({
      sendMode: SEND_MODES.WEBHOOK,
      webhookUrl: "",
      channelId: "",
      botProfileId: null,
      threadId: "",

      webhookProfiles: [],
      botProfiles: [],
      status: "idle",
      error: null,

      setSendMode: (sendMode) => set({ sendMode }),
      setWebhookUrl: (webhookUrl) => set({ webhookUrl: webhookUrl.trim() }),
      setChannelId: (channelId) => set({ channelId: channelId.trim() }),
      setBotProfileId: (botProfileId) => set({ botProfileId }),
      setThreadId: (threadId) => set({ threadId }),

      fetchProfiles: async () => {
        set({ status: "loading" });
        try {
          const [webhooks, bots] = await Promise.all([
            api.profiles.listWebhooks(),
            // Bot profiles are admin-only; a 403 here is expected and harmless.
            api.profiles.listBots().catch(() => ({ profiles: [] as BotProfile[] })),
          ]);
          set({
            webhookProfiles: webhooks.profiles,
            botProfiles: bots.profiles,
            status: "idle",
            error: null,
          });
        } catch (error) {
          set({
            status: "error",
            error: error instanceof Error ? error.message : String(error),
          });
        }
      },

      /** Apply a saved profile's URL to the active target. */
      useWebhookProfile: (profile) => get().setWebhookUrl(profile.url),

      reset: () =>
        set({ webhookUrl: "", channelId: "", botProfileId: null, threadId: "", error: null }),
    }),
    {
      name: "dmb:profile",
      // Cached profile lists are excluded: they are refetched from the server.
      partialize: (state) => ({
        sendMode: state.sendMode,
        webhookUrl: state.webhookUrl,
        channelId: state.channelId,
        botProfileId: state.botProfileId,
        threadId: state.threadId,
      }),
      version: 1,
    },
  ),
);

export default useProfileStore;

```

### File: `client/src/store/templateStore.ts`
```ts
import { create } from "zustand";
import {
  api,
  type TemplateDetailResponse,
  type TemplateSummary,
} from "../api/client";

/**
 * Saved message templates, backed by the server.
 *
 * Kept separate from the editor document: saving is an explicit action, and the
 * `dirty` flag is what tells the user their current work differs from what is
 * stored. Actions ride along with the template because a button without its
 * action config is useless.
 */

/** Strip the (large) document body before caching a summary in the list. */
const toSummary = (template: TemplateDetailResponse["template"]): TemplateSummary => ({
  id: template.id,
  user_id: template.user_id,
  name: template.name,
  description: template.description,
  preview_image_url: template.preview_image_url,
  is_public: template.is_public,
  created_at: template.created_at,
  updated_at: template.updated_at,
});

export interface TemplateState {
  templates: TemplateSummary[];
  currentId: number | null;
  currentName: string;
  dirty: boolean;
  status: "idle" | "loading" | "error";
  error: string | null;

  setCurrentName(name: string): void;
  markDirty(): void;

  fetchTemplates(query?: string): Promise<void>;
  /** Persist the current document. */
  save(document: { data: unknown; actions: unknown[] }): Promise<TemplateDetailResponse["template"]>;
  /** Fetch a full template and hand it back for the caller to load. */
  load(id: number): Promise<TemplateDetailResponse["template"]>;
  remove(id: number): Promise<void>;
  /** Forget the loaded template without discarding the document on screen. */
  detach(): void;
}

export const useTemplateStore = create<TemplateState>()((set, get) => ({
  templates: [],
  currentId: null,
  currentName: "",
  dirty: false,
  status: "idle",
  error: null,

  setCurrentName: (currentName) => set({ currentName, dirty: true }),
  markDirty: () => set({ dirty: true }),

  fetchTemplates: async (query) => {
    set({ status: "loading", error: null });
    try {
      const response = await api.templates.list(query);
      set({ templates: response.templates, status: "idle" });
    } catch (error) {
      set({
        status: "error",
        error: error instanceof Error ? error.message : String(error),
      });
    }
  },

  save: async (document) => {
    const { currentId, currentName } = get();
    if (!currentName.trim()) throw new Error("Give the template a name before saving.");

    const body = {
      name: currentName.trim(),
      data: document.data,
      actions: document.actions,
    };

    const response = currentId
      ? await api.templates.update(currentId, body)
      : await api.templates.create(body);

    const template = response.template;
    set((state) => ({
      currentId: template.id,
      dirty: false,
      templates: [
        toSummary(template),
        ...state.templates.filter((existing) => existing.id !== template.id),
      ],
    }));

    return template;
  },

  load: async (id) => {
    set({ status: "loading", error: null });
    try {
      const response = await api.templates.get(id);
      const template = response.template;
      set({
        currentId: template.id,
        currentName: template.name,
        dirty: false,
        status: "idle",
      });
      return template;
    } catch (error) {
      set({
        status: "error",
        error: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }
  },

  remove: async (id) => {
    await api.templates.remove(id);
    set((state) => ({
      templates: state.templates.filter((template) => template.id !== id),
      currentId: state.currentId === id ? null : state.currentId,
    }));
  },

  detach: () => set({ currentId: null, currentName: "", dirty: false }),
}));

export default useTemplateStore;

```

