# Repository Context Group: client_utils
# Source Repository: no-peace/Hoho_manager

### File: `client/src/utils/componentsV2.ts`
```ts
import { ButtonStyle, ComponentType } from "@dmb/shared";
import type {
  ComponentNode,
  ComponentTypeValue,
  GalleryItem,
  SelectOption,
} from "@dmb/shared";
import { DEFAULT_EMBED_COLOR, uid } from "./constants";

/**
 * Components V2 model.
 *
 * Every component carries an `_id` so the editor can key React lists and target
 * updates by identity instead of array position — reordering then costs nothing
 * and never desynchronises the preview. `stripInternal()` removes these before
 * the payload is sent.
 *
 * Factories return objects shaped exactly like Discord's API types, so the live
 * preview and the final payload render from the same data.
 *
 * Note: these use extensionless imports rather than `.js`, because the client is
 * bundled by Vite (`moduleResolution: bundler`). The server uses `.js` because it
 * is compiled to native ESM.
 */

/* ── Factories ────────────────────────────────────────────────────────────── */

export const newTextDisplay = (content = ""): ComponentNode => ({
  _id: uid(),
  type: ComponentType.TextDisplay,
  content,
});

export const newSeparator = ({
  divider = true,
  spacing = 1,
}: { divider?: boolean; spacing?: number } = {}): ComponentNode => ({
  _id: uid(),
  type: ComponentType.Separator,
  divider,
  spacing,
});

export const newContainer = (children: ComponentNode[] = []): ComponentNode => ({
  _id: uid(),
  type: ComponentType.Container,
  accent_color: DEFAULT_EMBED_COLOR,
  components: children,
});

export const newThumbnail = (url = ""): ComponentNode => ({
  _id: uid(),
  type: ComponentType.Thumbnail,
  media: { url },
});

export const newSection = (children: ComponentNode[] = []): ComponentNode => ({
  _id: uid(),
  type: ComponentType.Section,
  components: children.length > 0 ? children : [newTextDisplay("Section text")],
  accessory: newThumbnail(),
});

export const newGalleryItem = (url = ""): GalleryItem => ({ _id: uid(), media: { url } });

export const newMediaGallery = (items: GalleryItem[] = []): ComponentNode => ({
  _id: uid(),
  type: ComponentType.MediaGallery,
  items,
});

export const newFile = (url = ""): ComponentNode => ({
  _id: uid(),
  type: ComponentType.File,
  file: { url },
});

export const newButton = (style: number = ButtonStyle.Primary): ComponentNode => ({
  _id: uid(),
  type: ComponentType.Button,
  style,
  label: style === ButtonStyle.Link ? "Link" : "Button",
  ...(style === ButtonStyle.Link
    ? { url: "https://discord.com" }
    : { custom_id: "action:dud" }),
});

export const newSelectOption = (index: number): SelectOption => ({
  _id: uid(),
  label: `Option ${index}`,
  value: `option_${index}`,
});

export const newStringSelect = (): ComponentNode => ({
  _id: uid(),
  type: ComponentType.StringSelect,
  custom_id: "action:dud",
  placeholder: "Select an option",
  options: [newSelectOption(1)],
});

export const newActionRow = (children: ComponentNode[] = [newButton()]): ComponentNode => ({
  _id: uid(),
  type: ComponentType.ActionRow,
  components: children,
});

/* ── Metadata driving the palette UI ──────────────────────────────────────── */

export type ComponentGroup = "Content" | "Layout" | "Interactive";

export interface ComponentDef {
  type: ComponentTypeValue;
  label: string;
  description: string;
  group: ComponentGroup;
  /** May sit directly in a message (rather than inside a container). */
  topLevel: boolean;
  create: () => ComponentNode;
}

export const COMPONENT_DEFS: readonly ComponentDef[] = [
  {
    type: ComponentType.TextDisplay,
    label: "Text Display",
    description: "Markdown text — headings, lists, code blocks.",
    group: "Content",
    topLevel: true,
    create: () => newTextDisplay("Hello **world**"),
  },
  {
    type: ComponentType.Section,
    label: "Section",
    description: "Text with a thumbnail accessory.",
    group: "Content",
    topLevel: true,
    create: () => newSection(),
  },
  {
    type: ComponentType.MediaGallery,
    label: "Media Gallery",
    description: "One or more images or videos.",
    group: "Content",
    topLevel: true,
    create: () => newMediaGallery(),
  },
  {
    type: ComponentType.File,
    label: "File",
    description: "A single attachment reference.",
    group: "Content",
    topLevel: true,
    create: () => newFile(),
  },
  {
    type: ComponentType.Separator,
    label: "Separator",
    description: "Spacing or a divider line between components.",
    group: "Layout",
    topLevel: true,
    create: () => newSeparator(),
  },
  {
    type: ComponentType.Container,
    label: "Container",
    description: "A grouped card with an optional accent colour.",
    group: "Layout",
    topLevel: true,
    create: () => newContainer([newTextDisplay("Container text")]),
  },
  {
    type: ComponentType.ActionRow,
    label: "Action Row",
    description: "Holds buttons or a select menu.",
    group: "Interactive",
    topLevel: true,
    create: () => newActionRow(),
  },
];

/** Types that may be nested inside a Container. */
export const CONTAINER_CHILD_TYPES: readonly number[] = [
  ComponentType.ActionRow,
  ComponentType.TextDisplay,
  ComponentType.Section,
  ComponentType.MediaGallery,
  ComponentType.Separator,
  ComponentType.File,
];

/** Types that may be nested inside a Section. */
export const SECTION_CHILD_TYPES: readonly number[] = [ComponentType.TextDisplay];

const DEF_BY_TYPE = new Map<number, ComponentDef>(
  COMPONENT_DEFS.map((def) => [def.type, def]),
);

/** Instantiate a component from its palette definition. */
export const createComponent = (type: number): ComponentNode => {
  const def = DEF_BY_TYPE.get(type);
  if (!def) throw new Error(`Unknown component type: ${type}`);
  return def.create();
};

export const getComponentDef = (type: number): ComponentDef | null =>
  DEF_BY_TYPE.get(type) ?? null;

/** Short label for the layer tree / property panel header. */
export const componentLabel = (component: ComponentNode | undefined): string => {
  const def = component ? getComponentDef(component.type) : null;
  if (def) return def.label;

  const names: Record<number, string> = {
    [ComponentType.Button]: "Button",
    [ComponentType.StringSelect]: "String Select",
    [ComponentType.Thumbnail]: "Thumbnail",
  };
  return component ? (names[component.type] ?? "Component") : "Component";
};

/** Components that hold interactive controls (and therefore carry actions). */
export const isInteractiveComponent = (component: ComponentNode | undefined): boolean =>
  component?.type === ComponentType.Button ||
  component?.type === ComponentType.StringSelect ||
  component?.type === ComponentType.UserSelect ||
  component?.type === ComponentType.RoleSelect ||
  component?.type === ComponentType.MentionableSelect ||
  component?.type === ComponentType.ChannelSelect;

/** Can `childType` be nested inside `parentType`? Used to filter the palette. */
export const canNestIn = (parentType: number, childType: number): boolean => {
  if (parentType === ComponentType.Container) return CONTAINER_CHILD_TYPES.includes(childType);
  if (parentType === ComponentType.Section) return SECTION_CHILD_TYPES.includes(childType);
  if (parentType === ComponentType.ActionRow) {
    return childType === ComponentType.Button || childType === ComponentType.StringSelect;
  }
  return false;
};

```

### File: `client/src/utils/constants.ts`
```ts
/**
 * Client-side constants.
 *
 * Everything structural (component ids, limits, flags) comes from the shared
 * package so the frontend and backend can never disagree about the wire format.
 * Only presentation concerns are declared here.
 */
export * from "@dmb/shared";

/** Circular, sortable, collision-resistant enough for editor keys. */
export const uid = (): string => Math.random().toString(36).slice(2, 10);

export interface ColorPreset {
  name: string;
  value: number;
}

/** Embed accent presets shown in the colour picker. */
export const EMBED_COLOR_PRESETS: readonly ColorPreset[] = [
  { name: "Blurple", value: 0x5865f2 },
  { name: "Green", value: 0x57f287 },
  { name: "Yellow", value: 0xfee75c },
  { name: "Red", value: 0xed4245 },
  { name: "Fuchsia", value: 0xeb459e },
  { name: "Aqua", value: 0x1abc9c },
  { name: "Orange", value: 0xe67e22 },
  { name: "Dark", value: 0x2b2d31 },
];

export const DEFAULT_EMBED_COLOR = 0x5865f2;

/**
 * How a message is delivered.
 * - `webhook` may be sent straight from the browser.
 * - `bot` must go through `/api/send` so the token stays server-side.
 */
export const SEND_MODES = {
  WEBHOOK: "webhook",
  BOT: "bot",
} as const;

export type SendModeValue = (typeof SEND_MODES)[keyof typeof SEND_MODES];

/** Editor surface modes. V2 is the modern default; classic is the legacy path. */
export const EDITOR_MODES = {
  CLASSIC: "classic",
  V2: "v2",
} as const;

export type EditorMode = (typeof EDITOR_MODES)[keyof typeof EDITOR_MODES];

/** Human labels for button styles, used by the property panel. */
export const BUTTON_STYLE_LABELS: Record<number, string> = {
  1: "Primary (blurple)",
  2: "Secondary (grey)",
  3: "Success (green)",
  4: "Danger (red)",
  5: "Link",
  6: "Premium",
};

```

### File: `client/src/utils/discord.ts`
```ts
import { ComponentType, Limits, MessageFlags } from "@dmb/shared";
import type {
  ComponentNode,
  DiscordMessagePayload,
  EmbedData,
  MessageData,
} from "@dmb/shared";
import type { EditorMode } from "./constants";

/**
 * Payload construction and validation.
 *
 * Editors keep two things the Discord API knows nothing about:
 *   - `_id` on every embed/component, so React keys survive reordering
 *   - UI-only fields (e.g. a component's action config)
 *
 * {@link toDiscordPayload} is the single boundary where those are stripped, so
 * "what the user sees" and "what Discord receives" can never drift.
 */

/* ── Colour helpers ───────────────────────────────────────────────────────── */

/** `0x5865f2` -> `#5865f2` */
export const decimalToHex = (decimal: number | null | undefined): string => {
  if (decimal === null || decimal === undefined) return "#000000";
  return `#${Number(decimal).toString(16).padStart(6, "0").slice(-6)}`;
};

/** `#5865f2` -> `5865f2` (as an integer). */
export const hexToDecimal = (hex: string): number =>
  Number.parseInt(String(hex).replace("#", ""), 16) || 0;

/** Parse user-typed hex, returning `null` when it is not a valid colour. */
export const parseHexColor = (hex: string): number | null => {
  const cleaned = String(hex).replace("#", "").trim();
  if (!/^[0-9a-fA-F]{6}$/.test(cleaned)) return null;
  return Number.parseInt(cleaned, 16);
};

/* ── Sanitising ───────────────────────────────────────────────────────────── */

/** Recursively drop editor-only keys (`_id`, and anything starting with `_`). */
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

/* ── Payload building ─────────────────────────────────────────────────────── */

/**
 * Turn the editor's message document into a Discord message payload.
 *
 * @param data the store's `data` object
 */
export const toDiscordPayload = (
  data: MessageData,
  mode: EditorMode,
): DiscordMessagePayload => {
  const payload: DiscordMessagePayload = {};

  if (data.username) payload.username = data.username;
  if (data.avatar_url) payload.avatar_url = data.avatar_url;
  if (data.thread_name) payload.thread_name = data.thread_name;

  if (mode === "v2") {
    // Components V2 carries its own text; classic content/embeds are invalid
    // alongside it, so only `components` and the flag are sent.
    payload.components = stripInternal(data.components ?? []) as ComponentNode[];
    payload.flags = MessageFlags.IsComponentsV2;
  } else {
    if (data.content) payload.content = data.content;
    if (data.embeds.length > 0) {
      payload.embeds = stripInternal(data.embeds) as EmbedData[];
    }
    const classicComponents = data.components.filter(
      (component) => component.type === ComponentType.ActionRow,
    );
    if (classicComponents.length > 0) {
      payload.components = stripInternal(classicComponents) as ComponentNode[];
    }
  }

  return payload;
};

/**
 * A message must carry something. Discord rejects an entirely empty payload,
 * and an empty V2 message is almost always a mistake rather than intent.
 */
export const isPayloadEmpty = (payload: DiscordMessagePayload): boolean =>
  !payload.content &&
  !(payload.embeds && payload.embeds.length > 0) &&
  !(payload.components && payload.components.length > 0);

/* ── Validation ───────────────────────────────────────────────────────────── */

/** Total character usage of one embed, for the live counter in the editor. */
export const embedCharCount = (embed: EmbedData): number =>
  (embed.title?.length ?? 0) +
  (embed.description?.length ?? 0) +
  (embed.footer?.text?.length ?? 0) +
  (embed.author?.name?.length ?? 0) +
  (embed.fields ?? []).reduce(
    (sum, field) => sum + (field.name?.length ?? 0) + (field.value?.length ?? 0),
    0,
  );

/**
 * Validate the message document against Discord's documented limits.
 * Returns an array of human-readable problems; empty means valid.
 */
export const validateMessage = (data: MessageData, mode: EditorMode): string[] => {
  const errors: string[] = [];

  if (mode === "classic" && data.content.length > Limits.content) {
    errors.push(`Message content is ${data.content.length}/${Limits.content} characters`);
  }

  if (data.embeds.length > Limits.embed.embedsPerMessage) {
    errors.push(`Discord allows at most ${Limits.embed.embedsPerMessage} embeds per message`);
  }

  let totalEmbedChars = 0;
  data.embeds.forEach((embed, index) => {
    const label = `Embed ${index + 1}`;
    const chars = embedCharCount(embed);
    totalEmbedChars += chars;

    if (chars > Limits.embed.total) {
      errors.push(`${label} has ${chars} characters (limit ${Limits.embed.total})`);
    }
    if ((embed.fields?.length ?? 0) > Limits.embed.fields) {
      errors.push(`${label} has too many fields (limit ${Limits.embed.fields})`);
    }
  });

  if (totalEmbedChars > Limits.embed.total) {
    errors.push(`Embeds total ${totalEmbedChars} characters (limit ${Limits.embed.total})`);
  }

  if (data.components.length > Limits.components.total) {
    errors.push(
      `This message has ${data.components.length} components (limit ${Limits.components.total})`,
    );
  }

  return errors;
};

```

### File: `client/src/utils/exportImport.ts`
```ts
import type { MessageData, ComponentNode, EmbedData, EmbedField } from "@dmb/shared";

export interface QueryData {
  messages: { data: MessageData }[];
}

const genId = () => Math.random().toString(36).substring(2, 9);

export const fromQueryData = (parsed: any): MessageData => {
  let rawData = parsed;

  // 1. Detect official Discohook full workspace backups (like backups-2026-09-30.json)
  if (parsed.backups && Array.isArray(parsed.backups) && parsed.backups.length > 0) {
    const backup = parsed.backups[0];
    if (backup.messages && Array.isArray(backup.messages) && backup.messages.length > 0) {
      rawData = backup.messages[0].data;
    }
  }
  // 2. Detect standard QueryData single-message exports
  else if (parsed.messages && Array.isArray(parsed.messages) && parsed.messages.length > 0) {
    rawData = parsed.messages[0].data;
  }

  // Fallback to empty object to prevent UI crashes if data is malformed
  if (!rawData || typeof rawData !== 'object') rawData = {};

  return {
    content: rawData.content || "",
    username: rawData.username || "",
    avatar_url: rawData.avatar_url || "",
    thread_name: rawData.thread_name || "",
    embeds: (rawData.embeds || []).map((e: any): EmbedData => ({
      ...e,
      _id: e._id || genId(),
      fields: (e.fields || []).map((f: any): EmbedField => ({ ...f, _id: f._id || genId() }))
    })),
    components: (rawData.components || []).map((c: any): ComponentNode => ({
      ...c,
      _id: c._id || genId(),
      components: (c.components || []).map((child: any) => ({
        ...child,
        _id: child._id || genId(),
        options: (child.options || []).map((o: any) => ({ ...o, _id: o._id || genId() }))
      }))
    }))
  };
};

export const toQueryData = (payload: any): QueryData => {
  return {
    messages: [{ data: payload }]
  };
};

export const parseImportedJson = (text: string): MessageData => {
  const parsed = JSON.parse(text);
  return fromQueryData(parsed);
};

export const downloadJson = (payload: any, filename: string): void => {
  const queryData = toQueryData(payload);
  const blob = new Blob([JSON.stringify(queryData, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  
  a.href = url;
  a.download = filename.endsWith(".json") ? filename : `${filename}.json`;
  
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
```

### File: `client/src/utils/tree.test.ts`
```ts
import { describe, expect, it } from "vitest";
import {
  newActionRow,
  newButton,
  newContainer,
  newMediaGallery,
  newSection,
  newSeparator,
  newStringSelect,
  newTextDisplay,
} from "./componentsV2";
import { insertComponent, moveComponent, removeComponent, updateComponent } from "./tree";
import { stripInternal } from "./discord";

/**
 * The tree helpers are the backbone of every editor interaction — reordering,
 * nesting and deleting must all stay immutable and hit the right node.
 */

describe("updateComponent", () => {
  it("updates a deeply nested child by _id without mutating the input", () => {
    const child = newTextDisplay("before");
    const container = newContainer([child]);
    const tree = [container];

    const result = updateComponent(tree, child._id ?? "", (c) => ({
      content: `${c.content}!`,
    }));

    expect(result.found).toBe(true);
    expect(result.components[0]?.components?.[0]?.content).toBe("before!");
    // Original untouched (immutability).
    expect(tree[0]?.components?.[0]?.content).toBe("before");
  });

  it("reports found=false and returns the original array for unknown ids", () => {
    const tree = [newContainer([newTextDisplay("hi")])];
    const result = updateComponent(tree, "missing-id", () => ({ content: "nope" }));
    expect(result.found).toBe(false);
    expect(result.components).toEqual(tree);
  });
});

describe("removeComponent", () => {
  it("removes a nested child", () => {
    const a = newTextDisplay("a");
    const b = newTextDisplay("b");
    const tree = [newContainer([a, b])];

    const result = removeComponent(tree, a._id ?? "");
    expect(result.found).toBe(true);
    expect(result.components[0]?.components?.map((c) => c.content)).toEqual(["b"]);
  });

  it("removes a whole subtree when given a parent id", () => {
    const container = newContainer([newTextDisplay("inner")]);
    const sibling = newTextDisplay("sibling");
    const tree = [container, sibling];

    const result = removeComponent(tree, container._id ?? "");
    expect(result.found).toBe(true);
    expect(result.components).toEqual([sibling]);
  });
});

describe("insertComponent", () => {
  it("appends to a parent's children", () => {
    const container = newContainer([newTextDisplay("one")]);
    const item = newTextDisplay("two");

    const result = insertComponent([container], container._id ?? "", item);
    expect(result.found).toBe(true);
    expect(result.components[0]?.components?.length).toBe(2);
  });

  it("falls back to top level when the parent is unknown", () => {
    const item = newTextDisplay("orphan");
    const tree = [newContainer()];
    const result = insertComponent(tree, "no-such-parent", item);
    expect(result.found).toBe(true);
    expect(result.components.length).toBe(2);
  });

  it("appends to the top level when parentId is null", () => {
    const item = newTextDisplay("top");
    const result = insertComponent([], null, item);
    expect(result.components).toEqual([item]);
  });
});

describe("moveComponent", () => {
  it("swaps a component with its sibling inside a parent", () => {
    const a = newTextDisplay("a");
    const b = newTextDisplay("b");
    const c = newTextDisplay("c");
    const container = newContainer([a, b, c]);
    const containerId = container._id ?? "";

    const moved = moveComponent([container], a._id ?? "", 1, containerId);
    expect(moved.found).toBe(true);
    expect(moved.components[0]?.components?.map((x) => x.content)).toEqual(["b", "a", "c"]);
  });

  it("refuses to move past the edges", () => {
    const a = newTextDisplay("a");
    const b = newTextDisplay("b");
    const container = newContainer([a, b]);
    const containerId = container._id ?? "";

    expect(moveComponent([container], a._id ?? "", -1, containerId).found).toBe(false);
    expect(moveComponent([container], b._id ?? "", 1, containerId).found).toBe(false);
  });

  it("reports not-found for an unknown parent id instead of throwing", () => {
    const a = newTextDisplay("a");
    expect(moveComponent([a], a._id ?? "", 1, "no-such-parent").found).toBe(false);
  });

  it("moves at the top level when parentId is null", () => {
    const a = newTextDisplay("a");
    const b = newTextDisplay("b");
    const moved = moveComponent([a, b], a._id ?? "", 1);
    expect(moved.components.map((x) => x.content)).toEqual(["b", "a"]);
  });
});

describe("stripInternal", () => {
  it("removes _id from nested trees", () => {
    const section = newSection([newTextDisplay("hello")]);
    const json = JSON.stringify(stripInternal([section]));
    expect(json).not.toContain("_id");
    expect(json).toContain("hello");
  });

  it("leaves plain values alone", () => {
    expect(stripInternal("text")).toBe("text");
    expect(stripInternal(42)).toBe(42);
    expect(stripInternal(null)).toBeNull();
  });

  it("strips underscore-prefixed keys but keeps user content intact", () => {
    const payload = stripInternal({ _id: "x", content: "_not a key_" }) as Record<string, unknown>;
    expect(payload._id).toBeUndefined();
    expect(payload.content).toBe("_not a key_");
  });
});

describe("component factories", () => {
  it("give every node a unique _id", () => {
    const nodes = [
      newTextDisplay(),
      newSeparator(),
      newContainer(),
      newMediaGallery(),
      newButton(),
      newSection(),
      newStringSelect(),
      newActionRow(),
    ];
    const ids = new Set(nodes.map((n) => n._id));
    expect(ids.size).toBe(nodes.length);
  });

  it("type each factory to the right Discord component type", () => {
    expect(newTextDisplay().type).toBe(10);
    expect(newSeparator().type).toBe(14);
    expect(newContainer().type).toBe(17);
    expect(newMediaGallery().type).toBe(12);
    expect(newButton().type).toBe(2);
    expect(newSection().type).toBe(9);
    expect(newStringSelect().type).toBe(3);
    expect(newActionRow().type).toBe(1);
  });

  it("give buttons a custom_id, and link buttons a url instead", () => {
    expect(newButton().custom_id).toBe("action:dud");
    const link = newButton(5); // ButtonStyle.Link
    expect(link.url).toBe("https://discord.com");
    expect(link.custom_id).toBeUndefined();
  });
});

```

### File: `client/src/utils/tree.ts`
```ts
import type { ComponentNode } from "@dmb/shared";

/**
 * Immutable tree operations over an array of components.
 *
 * Components nest (a Container holds children, an ActionRow holds buttons), so
 * every edit needs a recursive walk. These helpers always return **new** arrays
 * and report whether anything matched, which lets the store skip state writes
 * (and therefore re-renders) for no-op updates.
 *
 * Only `components` arrays are traversed; `items`/`options` are leaves.
 */

export interface TreeResult {
  components: ComponentNode[];
  found: boolean;
}

/** Depth-first search for a component by `_id`. */
export const findComponent = (
  components: ComponentNode[] | undefined,
  id: string,
): ComponentNode | null => {
  for (const component of components ?? []) {
    if (component._id === id) return component;
    if (Array.isArray(component.components)) {
      const nested = findComponent(component.components, id);
      if (nested) return nested;
    }
  }
  return null;
};

/** Replace a component in place via `updater`. */
export const updateComponent = (
  components: ComponentNode[] | undefined,
  id: string,
  updater: (component: ComponentNode) => Partial<ComponentNode>,
): TreeResult => {
  let found = false;

  const next = (components ?? []).map((component) => {
    if (component._id === id) {
      found = true;
      return { ...component, ...updater(component) };
    }
    if (Array.isArray(component.components)) {
      const result = updateComponent(component.components, id, updater);
      if (result.found) {
        found = true;
        return { ...component, components: result.components };
      }
    }
    return component;
  });

  return { components: found ? next : (components ?? []), found };
};

/** Remove a component by id, wherever it sits. */
export const removeComponent = (
  components: ComponentNode[] | undefined,
  id: string,
): TreeResult => {
  let found = false;
  const next: ComponentNode[] = [];

  for (const component of components ?? []) {
    if (component._id === id) {
      found = true;
      continue;
    }
    if (Array.isArray(component.components)) {
      const result = removeComponent(component.components, id);
      if (result.found) {
        found = true;
        next.push({ ...component, components: result.components });
        continue;
      }
    }
    next.push(component);
  }

  return { components: found ? next : (components ?? []), found };
};

/**
 * Append `item` to a parent's children, or to the top level when `parentId` is
 * null/unknown.
 */
export const insertComponent = (
  components: ComponentNode[] | undefined,
  parentId: string | null,
  item: ComponentNode,
): TreeResult => {
  if (!parentId) return { components: [...(components ?? []), item], found: true };

  const result = updateComponent(components, parentId, (parent) => ({
    components: [...(parent.components ?? []), item],
  }));

  // Unknown parent: fall back to the top level rather than silently dropping it.
  if (!result.found) return { components: [...(components ?? []), item], found: true };
  return result;
};

/** Move a component one slot earlier/later among its own siblings. */
export const moveComponent = (
  components: ComponentNode[] | undefined,
  id: string,
  direction: number,
  parentId: string | null = null,
): TreeResult => {
  const list = parentId ? findComponent(components, parentId)?.components : components;
  if (!list) return { components: components ?? [], found: false };

  const index = list.findIndex((component) => component._id === id);
  if (index === -1) return { components: components ?? [], found: false };

  const target = index + direction;
  if (target < 0 || target >= list.length) return { components: components ?? [], found: false };

  const reordered = [...list];
  const current = reordered[index];
  const swap = reordered[target];
  if (!current || !swap) return { components: components ?? [], found: false };
  reordered[index] = swap;
  reordered[target] = current;

  if (!parentId) return { components: reordered, found: true };
  return updateComponent(components, parentId, () => ({ components: reordered }));
};

```

