# Repository Context Group: server_actions
# Source Repository: no-peace/Hoho_manager

### File: `server/src/actions/addRole.ts`
```ts
import type { ActionType } from "@dmb/shared";
import { actionFailed, ephemeral } from "./responses.js";
import { configString, type ActionContext, type ActionResponse } from "./types.js";

export const type: ActionType = "add_role";
export const description = "Give the member who clicked a role";

export const run = async ({
  interaction,
  config,
  botToken,
  discord,
  logger,
}: ActionContext): Promise<ActionResponse | undefined> => {
  const roleId = configString(config, "roleId", "role_id");
  const guildId = interaction.guild_id;
  const userId = interaction.member?.user?.id ?? interaction.user?.id;

  if (!roleId) return actionFailed("This button has no role configured.");
  if (!guildId) return actionFailed("This action only works inside a server.");
  if (!userId) return actionFailed("I couldn't work out who clicked.");
  if (!botToken) return actionFailed("The bot isn't configured on the server.");

  try {
    await discord.addGuildMemberRole(guildId, userId, roleId, botToken);
    return ephemeral(`\u2705 Gave you <@&${roleId}>.`);
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    logger.warn(`add_role failed for ${userId}: ${reason}`);
    return actionFailed(
      "I couldn't add that role — check my permissions and that my role sits above it.",
    );
  }
};

export default run;

```

### File: `server/src/actions/check.ts`
```ts
import type { ActionType, CheckCondition, CheckFunction } from "@dmb/shared";
import { actionFailed } from "./responses.js";
import { configString, type ActionContext, type ActionResponse } from "./types.js";

export const type: ActionType = "check";
export const description = "Branch or stop the flow based on a condition";

/**
 * Evaluates a condition, optionally branching the flow.
 *
 * Two shapes are supported, deliberately:
 *
 * **1. Branching (preferred, Discohook-compatible).** The step carries
 * `then` and `else` arrays of steps. `evaluateCheck` decides which one runs, and
 * the executor recurses into it — this handler is never called. Because the
 * branches live in the step's own config they survive the flat
 * `action_definitions` table, which can only express one ordered list.
 *
 *     { function: "equals", conditions: [{ a, b, loose? }],
 *       then: [ FlowStep, ... ], else: [ FlowStep, ... ] }
 *
 * **2. Legacy single-shot.** No branches: the condition is checked and, when it
 * fails, an error response ends the chain ("this interaction isn't available for
 * you"). Kept so flows saved before branching still work.
 *
 * Values may reference a flow variable with `{{name}}` or a dotted path
 * (`{{result.channel_id}}`).
 */

const VARIABLE_PATTERN = /^\{\{\s*([\w.$]+)\s*\}\}$/;

/** Read a (possibly nested) value out of the variable bag. */
const lookup = (path: string, variables: Record<string, unknown>): unknown => {
  if (!path.includes(".")) return variables[path];

  let current: unknown = variables;
  for (const segment of path.split(".")) {
    if (current === null || typeof current !== "object") return undefined;
    current = (current as Record<string, unknown>)[segment];
  }
  return current;
};

const resolve = (value: unknown, variables: Record<string, unknown>): unknown => {
  if (typeof value !== "string") return value;
  const key = value.match(VARIABLE_PATTERN)?.[1];
  return key === undefined ? value : lookup(key, variables);
};

/** Config arrives from JSON, so `conditions` is `unknown` until checked. */
const toConditions = (value: unknown): CheckCondition[] => {
  if (!Array.isArray(value)) return [];

  return value.flatMap((entry) => {
    if (entry === null || typeof entry !== "object") return [];
    const record = entry as Record<string, unknown>;
    return [{ a: record.a, b: record.b, loose: record.loose === true }];
  });
};

/** Comparable primitives, so a loose `==` is well-defined. */
type Comparable = string | number | boolean | null | undefined;

const equals = (a: unknown, b: unknown, loose: boolean): boolean => {
  if (!loose) return a === b;
  // Loose equality is opt-in, which is why the cast and the lint escape exist.
  // eslint-disable-next-line eqeqeq
  return (a as Comparable) == (b as Comparable);
};

/**
 * Is `element` contained in `container`?
 *
 * `container` is usually a comma-separated string (what a `set_variable` step
 * produces) or an array (what an adaptive variable can be). Both forms are
 * accepted so users do not have to know which one they have.
 */
const contains = (element: unknown, container: unknown): boolean => {
  const target = element === undefined || element === null ? "" : String(element);

  if (Array.isArray(container)) {
    return container.some((entry) => String(entry) === target);
  }
  if (typeof container === "string") {
    const list = container.split(",").map((entry) => entry.trim());
    return list.includes(target);
  }
  return false;
};

/** Evaluate a `check` step's condition against the current variables. */
export const evaluateCheck = (
  config: Record<string, unknown>,
  variables: Record<string, unknown>,
): boolean => {
  const conditions = toConditions(config.conditions);
  const test = (condition: CheckCondition): boolean =>
    equals(resolve(condition.a, variables), resolve(condition.b, variables), condition.loose === true);

  const fn = (configString(config, "function") ?? "equals") as CheckFunction;

  switch (fn) {
    case "and":
      // An empty condition list is vacuously true, which keeps a half-built step
      // from silently halting the whole flow.
      return conditions.every(test);
    case "or":
      return conditions.some(test);
    case "not":
      return conditions.every((condition) => !test(condition));
    case "in": {
      const [first] = conditions;
      return first ? contains(resolve(first.a, variables), resolve(first.b, variables)) : true;
    }
    case "equals":
    default: {
      const [first] = conditions;
      return first ? test(first) : true;
    }
  }
};

/** Legacy path: no branches configured — a failed check ends the chain. */
export const run = async ({
  config,
  variables,
}: ActionContext): Promise<ActionResponse | undefined> => {
  if (evaluateCheck(config, variables)) return undefined; // continue

  const failureMessage = configString(config, "failureMessage");
  return actionFailed(failureMessage ?? "This interaction isn't available for you.");
};

export default run;

```

### File: `server/src/actions/createThread.ts`
```ts
import type { ActionType } from "@dmb/shared";
import { actionFailed, ephemeral } from "./responses.js";
import { configString, type ActionContext, type ActionResponse } from "./types.js";

export const type: ActionType = "create_thread";
export const description = "Start a thread from the message";

/**
 * Opens a thread on the message that carried the clicked component.
 *
 * The thread name comes from `config.name`; `{{user}}` and `{{user.tag}}` are
 * substituted with the clicker's name, which is the common use ("ticket – alice").
 * Requires the bot to have **Create Public Threads** in the channel.
 */
export const run = async ({
  interaction,
  config,
  botToken,
  discord,
  logger,
}: ActionContext): Promise<ActionResponse | undefined> => {
  const rawName = configString(config, "name") ?? "Thread";
  const channelId = interaction.channel_id;
  const messageId = interaction.message?.id;
  const user = interaction.member?.user ?? interaction.user;

  if (!channelId || !messageId) {
    return actionFailed("I couldn't find the message to thread from.");
  }
  if (!botToken) return actionFailed("The bot isn't configured on the server.");

  const name = rawName
    .replace(/\{\{\s*user\.tag\s*\}\}/g, user?.username ?? "user")
    .replace(/\{\{\s*user(?:\.name)?\s*\}\}/g, user?.global_name ?? user?.username ?? "user")
    .slice(0, 100);

  try {
    const thread = await discord.createThreadFromMessage(channelId, messageId, name, botToken);
    return ephemeral(
      thread?.id ? `\ud83e\uddf5 Started <#${thread.id}>.` : "\ud83e\uddf5 Thread started.",
    );
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    logger.warn(`create_thread failed in ${channelId}: ${reason}`);
    return actionFailed("I couldn't start a thread — check my permissions here.");
  }
};

export default run;

```

### File: `server/src/actions/deleteMessage.ts`
```ts
import type { ActionType } from "@dmb/shared";
import { acknowledge, actionFailed } from "./responses.js";
import { configString, type ActionContext, type ActionResponse } from "./types.js";

export const type: ActionType = "delete_message";
export const description = "Delete the message carrying the component";

export const run = async ({
  interaction,
  config,
  botToken,
  discord,
  logger,
}: ActionContext): Promise<ActionResponse | undefined> => {
  const channelId = interaction.channel_id;
  const messageId = configString(config, "messageId") ?? interaction.message?.id;

  if (!messageId || !channelId) return actionFailed("Nothing to delete.");
  if (!botToken) return actionFailed("The bot isn't configured on the server.");

  try {
    await discord.deleteChannelMessage(channelId, messageId, botToken);
    // The message is gone, so a normal reply would reference nothing.
    return acknowledge();
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    logger.warn(`delete_message failed for ${messageId}: ${reason}`);
    return actionFailed("I couldn't delete that message.");
  }
};

export default run;

```

### File: `server/src/actions/dud.ts`
```ts
import type { ActionType } from "@dmb/shared";
import type { ActionContext, ActionResponse } from "./types.js";

export const type: ActionType = "dud";
export const description = "Do nothing";

/**
 * The explicit no-op.
 *
 * Every new button starts life as `action:dud`, so this handler exists mostly to
 * make that default honest: clicking an unconfigured button does nothing visible
 * rather than tripping the "no handler registered" warning in the executor.
 */
export const run = async (_context: ActionContext): Promise<ActionResponse | undefined> => {
  // `undefined` tells the executor to acknowledge quietly.
  return undefined;
};

export default run;

```

### File: `server/src/actions/flow.test.ts`
```ts
import { describe, expect, it } from "vitest";
import { InteractionResponseType, MessageFlags } from "@dmb/shared";
import type { ActionConfig, DiscordInteraction } from "@dmb/shared";
import type { ActionContext } from "./types.js";
import { evaluateCheck } from "./check.js";
import * as setVariable from "./setVariable.js";
import * as stop from "./stop.js";

/**
 * Flow parity with Discohook: `check` branching, `stop`, and the three
 * `set_variable` modes.
 *
 * These are the parts of a flow a user builds in the editor, so their behaviour
 * is pinned here rather than only exercised through a live Discord click. The
 * condition evaluator and the variable writer are pure enough to test directly.
 */

const interaction = (overrides: Partial<DiscordInteraction> = {}): DiscordInteraction => ({
  id: "1",
  application_id: "app",
  type: 3,
  token: "tok",
  channel_id: "chan",
  guild_id: "guild",
  data: { custom_id: "action:dud", values: [] },
  member: { user: { id: "user-1", username: "ada", global_name: "Ada" } },
  ...overrides,
});

/** A context with only the fields these pure handlers actually read. */
const context = (
  config: ActionConfig,
  vars: Record<string, unknown> = {},
  overrides: Partial<DiscordInteraction> = {},
): ActionContext =>
  ({
    interaction: interaction(overrides),
    config,
    variables: vars,
  }) as unknown as ActionContext;

const eq = (a: unknown, b: unknown, loose = false) => ({
  function: "equals",
  conditions: [{ a, b, loose }],
});

describe("evaluateCheck — equals", () => {
  it("compares literals strictly by default", () => {
    expect(evaluateCheck(eq("a", "a"), {})).toBe(true);
    expect(evaluateCheck(eq("a", "b"), {})).toBe(false);
    // 1 !== "1", which is the point of strict-by-default.
    expect(evaluateCheck(eq(1, "1"), {})).toBe(false);
  });

  it("uses loose equality only when asked", () => {
    expect(evaluateCheck(eq(1, "1", true), {})).toBe(true);
    expect(evaluateCheck(eq(0, false, true), {})).toBe(true);
    expect(evaluateCheck(eq(0, false), {})).toBe(false);
  });

  it("treats a half-built step as passing so it cannot silently halt a flow", () => {
    expect(evaluateCheck({ function: "equals", conditions: [] }, {})).toBe(true);
    expect(evaluateCheck({}, {})).toBe(true);
  });

  it("defaults to equals when no function is set", () => {
    expect(evaluateCheck({ conditions: [{ a: "x", b: "x" }] }, {})).toBe(true);
  });
});

describe("evaluateCheck — variable resolution", () => {
  it("resolves {{name}} from the variable bag", () => {
    expect(evaluateCheck(eq("{{role}}", "member"), { role: "member" })).toBe(true);
  });

  it("tolerates whitespace inside the braces", () => {
    expect(evaluateCheck(eq("{{  role  }}", "member"), { role: "member" })).toBe(true);
  });

  it("resolves dotted paths", () => {
    expect(evaluateCheck(eq("{{result.channel_id}}", "99"), { result: { channel_id: "99" } })).toBe(
      true,
    );
  });

  it("yields undefined (not a throw) for a missing path", () => {
    expect(evaluateCheck(eq("{{result.channel_id}}", "99"), {})).toBe(false);
    expect(evaluateCheck(eq("{{a.b.c.d}}", "x"), { a: "scalar" })).toBe(false);
  });

  it("leaves a plain string alone when it is not a whole-value placeholder", () => {
    expect(evaluateCheck(eq("hello {{name}}", "hello {{name}}"), {})).toBe(true);
  });
});

describe("evaluateCheck — and / or / not / in", () => {
  it("`and` requires every condition", () => {
    const config = { function: "and", conditions: [{ a: "{{a}}", b: "1" }, { a: "{{b}}", b: "2" }] };
    expect(evaluateCheck(config, { a: "1", b: "2" })).toBe(true);
    expect(evaluateCheck(config, { a: "1", b: "9" })).toBe(false);
  });

  it("`or` requires any condition", () => {
    const config = { function: "or", conditions: [{ a: "{{a}}", b: "1" }, { a: "{{b}}", b: "2" }] };
    expect(evaluateCheck(config, { a: "no", b: "2" })).toBe(true);
    expect(evaluateCheck(config, { a: "no", b: "no" })).toBe(false);
  });

  it("`not` passes only when nothing matches", () => {
    const config = { function: "not", conditions: [{ a: "{{a}}", b: "1" }] };
    expect(evaluateCheck(config, { a: "no" })).toBe(true);
    expect(evaluateCheck(config, { a: "1" })).toBe(false);
  });

  it("`in` matches an array container", () => {
    const config = { function: "in", conditions: [{ a: "{{pick}}", b: "{{list}}" }] };
    expect(evaluateCheck(config, { pick: "b", list: ["a", "b", "c"] })).toBe(true);
    expect(evaluateCheck(config, { pick: "z", list: ["a", "b", "c"] })).toBe(false);
  });

  it("`in` matches a comma-separated string container", () => {
    // This is the shape a `set_variable` step produces for select menus.
    const config = { function: "in", conditions: [{ a: "b", b: "{{picks}}" }] };
    expect(evaluateCheck(config, { picks: "a, b , c" })).toBe(true);
    expect(evaluateCheck(config, { picks: "a,c" })).toBe(false);
  });
});

describe("stop", () => {
  it("replies ephemerally when content is set", async () => {
    const response = await stop.run(context({ content: "All done" }));
    expect(response).toEqual({
      type: InteractionResponseType.ChannelMessageWithSource,
      data: { content: "All done", flags: MessageFlags.Ephemeral },
    });
  });

  it("accepts `message` as an alias for `content`", async () => {
    const response = await stop.run(context({ message: "Done" }));
    expect(response?.data?.content).toBe("Done");
  });

  it("acknowledges silently when nothing is set", async () => {
    const response = await stop.run(context({}));
    expect(response).toEqual({ type: InteractionResponseType.DeferredUpdateMessage });
  });
});

describe("set_variable", () => {
  it("stores a static literal and never responds", async () => {
    const vars: Record<string, unknown> = {};
    const response = await setVariable.run(context({ name: "plan", value: "pro", varType: "static" }, vars));
    expect(response).toBeUndefined();
    expect(vars.plan).toBe("pro");
  });

  it("defaults to static when varType is absent", async () => {
    const vars: Record<string, unknown> = {};
    await setVariable.run(context({ name: "a", value: "1" }, vars));
    expect(vars.a).toBe("1");
  });

  it("reads an adaptive field off the interaction", async () => {
    const vars: Record<string, unknown> = {};
    await setVariable.run(context({ name: "who", value: "user.id", varType: "adaptive" }, vars));
    expect(vars.who).toBe("user-1");
  });

  it("joins select-menu values for adaptive `selected`", async () => {
    const vars: Record<string, unknown> = {};
    await setVariable.run(
      context({ name: "picked", value: "selected", varType: "adaptive" }, vars, {
        data: { custom_id: "action:dud", values: ["red", "blue"] },
      }),
    );
    expect(vars.picked).toBe("red,blue");
  });

  it("resolves an unknown adaptive field to null rather than throwing", async () => {
    const vars: Record<string, unknown> = {};
    await setVariable.run(context({ name: "x", value: "nope", varType: "adaptive" }, vars));
    expect(vars.x).toBeNull();
  });

  it("`get` mirrors another variable by name", async () => {
    const vars: Record<string, unknown> = { source: "kept" };
    await setVariable.run(context({ name: "copy", value: "source", varType: "get" }, vars));
    expect(vars.copy).toBe("kept");
  });

  it("`get` of a missing variable resolves to null", async () => {
    const vars: Record<string, unknown> = {};
    await setVariable.run(context({ name: "copy", value: "ghost", varType: "get" }, vars));
    expect(vars.copy).toBeNull();
  });

  it("does nothing without a name", async () => {
    const vars: Record<string, unknown> = {};
    const response = await setVariable.run(context({ value: "x" }, vars));
    expect(response).toBeUndefined();
    expect(vars).toEqual({});
  });

  it("exposes the adaptive field list the editor reads", () => {
    expect(setVariable.ADAPTIVE_FIELDS).toContain("user.id");
    expect(setVariable.ADAPTIVE_FIELDS).toContain("selected");
  });
});

```

### File: `server/src/actions/index.ts`
```ts
import type { ActionHandlerMeta } from "@dmb/shared";
import * as addRole from "./addRole.js";
import * as check from "./check.js";
import * as createThread from "./createThread.js";
import * as deleteMessage from "./deleteMessage.js";
import * as dud from "./dud.js";
import * as openModal from "./openModal.js";
import * as removeRole from "./removeRole.js";
import * as sendDm from "./sendDm.js";
import * as sendEphemeralReply from "./sendEphemeralReply.js";
import * as sendMessage from "./sendMessage.js";
import * as sendWebhookMessage from "./sendWebhookMessage.js";
import * as setVariable from "./setVariable.js";
import * as stop from "./stop.js";
import * as toggleRole from "./toggleRole.js";
import * as wait from "./wait.js";
import type { ActionHandlerModule } from "./types.js";

/**
 * The action registry.
 *
 * `custom_id` -> handler. Adding a capability means writing a module exporting
 * `type`, `description` and `run(ctx)` and listing it here — nothing else in the
 * codebase needs to change.
 *
 * `GET /api/config` exposes {@link listActionTypes} so the editor's action
 * picker is driven by this registry rather than a hardcoded copy that can drift.
 */
const modules: readonly ActionHandlerModule[] = [
  dud,
  addRole,
  removeRole,
  toggleRole,
  sendEphemeralReply,
  sendDm,
  openModal,
  sendMessage,
  sendWebhookMessage,
  deleteMessage,
  createThread,
  wait,
  setVariable,
  check,
  stop,
];

const registry = new Map<string, ActionHandlerModule>(modules.map((module) => [module.type, module]));

/** Look up a handler by its action type, or `null` when unregistered. */
export const getActionHandler = (actionType: string): ActionHandlerModule | null =>
  registry.get(actionType) ?? null;

export const hasActionHandler = (actionType: string): boolean => registry.has(actionType);

/** Metadata for the UI's action picker. */
export const listActionTypes = (): ActionHandlerMeta[] =>
  modules.map((module) => ({
    type: module.type,
    description: module.description,
  }));

export default { getActionHandler, hasActionHandler, listActionTypes };

```

### File: `server/src/actions/openModal.ts`
```ts
import crypto from "node:crypto";
import type { ActionType } from "@dmb/shared";
import { modal } from "./responses.js";
import { configString, type ActionContext, type ActionResponse } from "./types.js";

export const type: ActionType = "open_modal";
export const description = "Open a form the user can fill in";

/**
 * Modals must be acknowledged within 3 seconds, so we return the modal payload
 * directly and let the `MODAL_SUBMIT` interaction (handled in the interaction
 * route) do the actual work.
 */
export const run = async ({
  config,
}: ActionContext): Promise<ActionResponse | undefined> => {
  const components = Array.isArray(config.components) ? config.components : [];

  // A modal with no inputs is rejected by Discord.
  if (components.length === 0) return undefined;

  return modal({
    customId: configString(config, "customId") ?? `modal:${crypto.randomUUID()}`,
    title: configString(config, "title") ?? "Input",
    components,
  });
};

export default run;

```

### File: `server/src/actions/removeRole.ts`
```ts
import type { ActionType } from "@dmb/shared";
import { actionFailed, ephemeral } from "./responses.js";
import { configString, type ActionContext, type ActionResponse } from "./types.js";

export const type: ActionType = "remove_role";
export const description = "Take a role away from the member who clicked";

export const run = async ({
  interaction,
  config,
  botToken,
  discord,
  logger,
}: ActionContext): Promise<ActionResponse | undefined> => {
  const roleId = configString(config, "roleId", "role_id");
  const guildId = interaction.guild_id;
  const userId = interaction.member?.user?.id ?? interaction.user?.id;

  if (!roleId) return actionFailed("This button has no role configured.");
  if (!guildId) return actionFailed("This action only works inside a server.");
  if (!userId) return actionFailed("I couldn't work out who clicked.");
  if (!botToken) return actionFailed("The bot isn't configured on the server.");

  try {
    await discord.removeGuildMemberRole(guildId, userId, roleId, botToken);
    return ephemeral(`\u2705 Removed <@&${roleId}>.`);
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    logger.warn(`remove_role failed for ${userId}: ${reason}`);
    return actionFailed("I couldn't remove that role — check my permissions.");
  }
};

export default run;

```

### File: `server/src/actions/responses.ts`
```ts
import { InteractionResponseType, MessageFlags } from "@dmb/shared";
import type { ActionResponse } from "./types.js";

/**
 * Small builders for interaction callback payloads.
 *
 * Handlers return one of these instead of hand-rolling the numeric type codes,
 * which keeps the action modules readable.
 */

/** A message only the invoking user can see. */
export const ephemeral = (
  content: string,
  extra: Record<string, unknown> = {},
): ActionResponse => ({
  type: InteractionResponseType.ChannelMessageWithSource,
  data: {
    content,
    flags: MessageFlags.Ephemeral,
    ...extra,
  },
});

/** A public reply in the channel. */
export const reply = (content: string, extra: Record<string, unknown> = {}): ActionResponse => ({
  type: InteractionResponseType.ChannelMessageWithSource,
  data: { content, ...extra },
});

/** Replace the message that carried the clicked component. */
export const updateMessage = (data: Record<string, unknown>): ActionResponse => ({
  type: InteractionResponseType.UpdateMessage,
  data,
});

/** Acknowledge the click without a visible reply. */
export const acknowledge = (): ActionResponse => ({
  type: InteractionResponseType.DeferredUpdateMessage,
});

/** Present a modal form. */
export const modal = ({
  customId,
  title,
  components,
}: {
  customId: string;
  title: string;
  components: unknown[];
}): ActionResponse => ({
  type: InteractionResponseType.Modal,
  data: { custom_id: customId, title, components },
});

/** Standard "this action failed" message used by handlers and the executor. */
export const actionFailed = (
  message = "That action could not be completed.",
): ActionResponse => ephemeral(`\u26a0\ufe0f ${message}`);

```

### File: `server/src/actions/sendDm.ts`
```ts
import type { ActionType, DiscordMessagePayload, EmbedData } from "@dmb/shared";
import { actionFailed, ephemeral } from "./responses.js";
import { configString, type ActionContext, type ActionResponse } from "./types.js";

export const type: ActionType = "send_dm";
export const description = "DM the member who clicked";

export const run = async ({
  interaction,
  config,
  botToken,
  discord,
  logger,
}: ActionContext): Promise<ActionResponse | undefined> => {
  const userId =
    configString(config, "userId") ??
    interaction.member?.user?.id ??
    interaction.user?.id;
  const content = configString(config, "content") ?? "Thanks for clicking!";
  const embeds = Array.isArray(config.embeds) ? config.embeds : [];

  if (!userId) return actionFailed("I couldn't work out who to message.");
  if (!botToken) return actionFailed("The bot isn't configured on the server.");

  const payload: DiscordMessagePayload = { content };
  if (embeds.length > 0) payload.embeds = embeds as EmbedData[];

  try {
    await discord.sendDirectMessage(userId, payload, botToken);
    return ephemeral("\ud83d\udcec Sent you a direct message.");
  } catch (error) {
    // The most common cause is the user's privacy settings blocking DMs.
    const reason = error instanceof Error ? error.message : String(error);
    logger.warn(`send_dm failed for ${userId}: ${reason}`);
    return actionFailed(
      "I couldn't DM you — your privacy settings may block direct messages.",
    );
  }
};

export default run;

```

### File: `server/src/actions/sendEphemeralReply.ts`
```ts
import type { ActionType } from "@dmb/shared";
import { ephemeral } from "./responses.js";
import { configString, type ActionContext, type ActionResponse } from "./types.js";

export const type: ActionType = "send_ephemeral_reply";
export const description = "Show the clicker a private message";

export const run = async ({
  config,
}: ActionContext): Promise<ActionResponse | undefined> => {
  const content = configString(config, "content") ?? "\ud83d\udc4b";
  const embeds = Array.isArray(config.embeds) ? config.embeds : [];

  return ephemeral(content, embeds.length > 0 ? { embeds } : {});
};

export default run;

```

### File: `server/src/actions/sendMessage.ts`
```ts
import type { ActionType } from "@dmb/shared";
import { actionFailed, ephemeral } from "./responses.js";
import {
  configString,
  toMessagePayload,
  type ActionContext,
  type ActionResponse,
} from "./types.js";

export const type: ActionType = "send_message";
export const description = "Send a message as the bot";

/**
 * Sends a stored message payload to a channel.
 *
 * `config.message` is a raw Discord message object (content/embeds/components).
 * This runs as a follow-up rather than an interaction reply so the click can be
 * acknowledged instantly — interaction tokens stay valid for 15 minutes, which
 * is plenty for this.
 */
export const run = async ({
  interaction,
  config,
  discord,
  logger,
}: ActionContext): Promise<ActionResponse | undefined> => {
  const channelId = configString(config, "channelId") ?? interaction.channel_id;
  const payload =
    toMessagePayload(config.message) ??
    (configString(config, "content") ? { content: configString(config, "content") } : null);

  if (!channelId) return actionFailed("No target channel configured.");
  if (!payload) return actionFailed("No message content configured.");

  try {
    await discord.sendChannelMessage(channelId, payload, {});
    return ephemeral("\ud83d\udce8 Message sent.");
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    logger.warn(`send_message failed in ${channelId}: ${reason}`);
    return actionFailed("I couldn't send that message — check my permissions there.");
  }
};

export default run;

```

### File: `server/src/actions/sendWebhookMessage.ts`
```ts
import type { ActionType } from "@dmb/shared";
import { actionFailed, ephemeral } from "./responses.js";
import {
  configNumber,
  configString,
  toMessagePayload,
  type ActionContext,
  type ActionResponse,
} from "./types.js";

export const type: ActionType = "send_webhook_message";
export const description = "Send a message through a saved webhook";

/**
 * Posts through a stored webhook profile, or a raw URL when supplied.
 *
 * Prefer a profile id: webhook URLs are credentials, so keeping them in the
 * database avoids embedding one in a `custom_id`.
 */
export const run = async ({
  config,
  discord,
  repositories,
  logger,
}: ActionContext): Promise<ActionResponse | undefined> => {
  const payload =
    toMessagePayload(config.message) ??
    (configString(config, "content") ? { content: configString(config, "content") } : null);

  if (!payload) return actionFailed("No message content configured.");

  let url = configString(config, "webhookUrl");
  const profileId = configNumber(config, "webhookProfileId");

  if (!url && profileId != null) {
    const profile = await repositories.webhookProfiles.findById(profileId);
    url = profile?.url;
  }

  if (!url) return actionFailed("No webhook configured for this action.");

  try {
    await discord.sendWebhook(url, payload, { wait: false });
    return ephemeral("\ud83d\udce8 Sent.");
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    logger.warn(`send_webhook_message failed: ${reason}`);
    return actionFailed("I couldn't send through that webhook.");
  }
};

export default run;

```

### File: `server/src/actions/setVariable.ts`
```ts
import { AdaptiveFields } from "@dmb/shared";
import type { ActionType, SetVariableMode } from "@dmb/shared";
import { configString, type ActionContext, type ActionResponse } from "./types.js";

export const type: ActionType = "set_variable";
export const description = "Store a value for later steps";

/**
 * Writes a value into the flow's variable bag.
 *
 * Variables are the plumbing for multi-step flows: a later step can reference
 * `{{name}}` in its content, and `check` branches on it.
 *
 * Three modes, matching Discohook's names — though `adaptive` is scoped to what
 * this bot can actually observe, because our handlers return a *response* rather
 * than a result object, so there is no "previous sent message" to read from:
 *
 * | Mode       | `value` means                | Example                          |
 * | ---------- | ---------------------------- | -------------------------------- |
 * | `static`   | a literal                    | `member`                         |
 * | `adaptive` | a field of the interaction   | `user.id`, `channel.id`, `selected` |
 * | `get`      | the name of another variable | `userId`                         |
 *
 * Always returns `undefined`: this step never responds, so the chain continues.
 */

/**
 * Fields an `adaptive` variable can read off the interaction.
 *
 * Re-exported from `@dmb/shared` so the editor offers exactly the fields this
 * handler knows how to read.
 */
export const ADAPTIVE_FIELDS = AdaptiveFields;

const readAdaptive = (field: string, { interaction }: ActionContext): unknown => {
  const user = interaction.member?.user ?? interaction.user;

  switch (field) {
    case "user.id":
      return user?.id ?? null;
    case "user.name":
      return user?.global_name ?? user?.username ?? null;
    case "user.tag":
      return user?.username ?? null;
    case "channel.id":
      return interaction.channel_id ?? null;
    case "guild.id":
      return interaction.guild_id ?? null;
    case "message.id":
      return interaction.message?.id ?? null;
    case "selected":
      // Select menus deliver their values as an array; join so `{{name}}` and
      // the `in` check can both treat it as a plain comma-separated list.
      return interaction.data?.values?.join(",") ?? "";
    default:
      return null;
  }
};

export const run = async (
  context: ActionContext,
): Promise<ActionResponse | undefined> => {
  const { config, variables } = context;
  const name = configString(config, "name");
  if (!name) return undefined;

  const mode = (configString(config, "varType") ?? "static") as SetVariableMode;

  switch (mode) {
    case "adaptive":
      variables[name] = readAdaptive(String(config.value ?? ""), context);
      break;
    case "get":
      variables[name] = variables[String(config.value ?? "")] ?? null;
      break;
    case "static":
    default:
      variables[name] = config.value ?? null;
      break;
  }

  return undefined; // continue
};

export default run;

```

### File: `server/src/actions/stop.ts`
```ts
import type { ActionType } from "@dmb/shared";
import { acknowledge, ephemeral } from "./responses.js";
import { configString, type ActionContext, type ActionResponse } from "./types.js";

export const type: ActionType = "stop";
export const description = "End the flow here";

/**
 * Ends the chain and replies.
 *
 * The executor stops at the first step that returns a response, so "stopping" is
 * just returning one:
 *
 *   - with `content` set, the clicker gets an ephemeral message;
 *   - with nothing set, the interaction is acknowledged silently (no visible
 *     change), which is what you want at the end of a branch that did its work
 *     through role edits or DMs.
 *
 * This is how a `check` branch says "done" without falling through into the
 * steps that follow the check.
 */
export const run = async ({
  config,
}: ActionContext): Promise<ActionResponse | undefined> => {
  const content = configString(config, "content", "message");
  return content ? ephemeral(content) : acknowledge();
};

export default run;

```

### File: `server/src/actions/toggleRole.ts`
```ts
import type { ActionType } from "@dmb/shared";
import { actionFailed, ephemeral } from "./responses.js";
import { configString, type ActionContext, type ActionResponse } from "./types.js";

export const type: ActionType = "toggle_role";
export const description = "Add the role if absent, remove it if present";

export const run = async ({
  interaction,
  config,
  botToken,
  discord,
  logger,
}: ActionContext): Promise<ActionResponse | undefined> => {
  const roleId = configString(config, "roleId", "role_id");
  const guildId = interaction.guild_id;
  const userId = interaction.member?.user?.id ?? interaction.user?.id;

  if (!roleId) return actionFailed("This button has no role configured.");
  if (!guildId) return actionFailed("This action only works inside a server.");
  if (!userId) return actionFailed("I couldn't work out who clicked.");
  if (!botToken) return actionFailed("The bot isn't configured on the server.");

  try {
    const alreadyHas = await discord.hasRole(guildId, userId, roleId, botToken);

    if (alreadyHas) {
      await discord.removeGuildMemberRole(guildId, userId, roleId, botToken);
      return ephemeral(`\u2705 Removed <@&${roleId}>.`);
    }

    await discord.addGuildMemberRole(guildId, userId, roleId, botToken);
    return ephemeral(`\u2705 Gave you <@&${roleId}>.`);
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    logger.warn(`toggle_role failed for ${userId}: ${reason}`);
    return actionFailed("I couldn't update that role — check my permissions.");
  }
};

export default run;

```

### File: `server/src/actions/types.ts`
```ts
import type {
  ActionConfig,
  ActionType,
  ComponentNode,
  DiscordInteraction,
  DiscordMessagePayload,
  EmbedData,
} from "@dmb/shared";
import type { Repositories } from "../repositories/index.js";
import type { DiscordMessage, GuildMember } from "../services/discordService.js";
import type { Logger } from "../utils/logger.js";

/**
 * The contracts every action handler is written against.
 *
 * Handlers receive an explicit {@link ActionContext} rather than importing
 * services themselves. That keeps the dependency direction one-way and means a
 * handler can be unit-tested by hand-rolling a context object.
 */

/** An interaction callback body. Only the first response in a chain is sent. */
export interface ActionResponse {
  type: number;
  data?: Record<string, unknown>;
}

/**
 * The slice of the Discord API that handlers may use.
 *
 * Deliberately narrow: adding a capability here is a conscious decision, and
 * `discordService` satisfies this structurally so no adapter is needed.
 */
export interface DiscordApi {
  addGuildMemberRole(
    guildId: string,
    userId: string,
    roleId: string,
    token: string,
  ): Promise<boolean>;
  removeGuildMemberRole(
    guildId: string,
    userId: string,
    roleId: string,
    token: string,
  ): Promise<boolean>;
  hasRole(
    guildId: string,
    userId: string,
    roleId: string,
    token: string,
  ): Promise<boolean>;
  sendDirectMessage(
    userId: string,
    payload: DiscordMessagePayload,
    token: string,
  ): Promise<DiscordMessage | null>;
  sendChannelMessage(
    channelId: string,
    payload: DiscordMessagePayload,
    options?: { profileId?: number | null },
  ): Promise<DiscordMessage | null>;
  sendWebhook(
    webhookUrl: string,
    payload: DiscordMessagePayload,
    options?: { wait?: boolean; threadId?: string | null },
  ): Promise<DiscordMessage | null>;
  deleteChannelMessage(
    channelId: string,
    messageId: string,
    token: string,
  ): Promise<boolean>;
  createThreadFromMessage(
    channelId: string,
    messageId: string,
    name: string,
    token: string,
  ): Promise<{ id: string } | null>;
}

export interface ActionContext {
  /** The raw interaction payload from Discord. */
  interaction: DiscordInteraction;
  /** Action-specific parameters, either inline or from `action_definitions`. */
  config: ActionConfig;
  /**
   * Mutable variable bag for multi-step flows. Handlers may write to it (see
   * `set_variable`) and later steps read from it.
   */
  variables: Record<string, unknown>;
  /** Null when no bot token is configured — handlers must cope. */
  botToken: string | null;
  discord: DiscordApi;
  /** Only the persistence a handler genuinely needs, so it stays testable. */
  repositories: Pick<Repositories, "webhookProfiles">;
  logger: Logger;
}

export interface ActionHandlerModule {
  type: ActionType;
  description: string;
  /**
   * Run the action.
   *
   * Returning a response ends the chain and sends that response. Returning
   * `undefined` means "continue to the next step".
   */
  run(context: ActionContext): Promise<ActionResponse | undefined>;
}

/** Narrow a config value to a string, or `undefined`. */
export const configString = (config: ActionConfig, ...keys: string[]): string | undefined => {
  for (const key of keys) {
    const value = config[key];
    if (typeof value === "string" && value.trim() !== "") return value;
  }
  return undefined;
};

/** Narrow a config value to a number, or `undefined`. */
export const configNumber = (config: ActionConfig, key: string): number | undefined => {
  const value = config[key];
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return undefined;
};

/**
 * Coerce an untrusted config value into a message payload.
 *
 * Action configs arrive from JSON, so every field is `unknown` until checked.
 * The `embeds`/`components` arrays are cast rather than deep-validated: they were
 * authored by the same editor that produced the message, and Discord rejects
 * anything malformed with a specific error we surface to the user. Returns
 * `null` when there is nothing sendable.
 */
export const toMessagePayload = (value: unknown): DiscordMessagePayload | null => {
  if (value === null || typeof value !== "object") return null;

  const record = value as Record<string, unknown>;
  const payload: DiscordMessagePayload = {};

  if (typeof record.content === "string") payload.content = record.content;
  if (Array.isArray(record.embeds)) payload.embeds = record.embeds as EmbedData[];
  if (Array.isArray(record.components)) {
    payload.components = record.components as ComponentNode[];
  }
  if (typeof record.flags === "number") payload.flags = record.flags;

  return Object.keys(payload).length > 0 ? payload : null;
};

export type { DiscordMessage, GuildMember };

```

### File: `server/src/actions/wait.ts`
```ts
import type { ActionType } from "@dmb/shared";
import { configNumber, type ActionContext, type ActionResponse } from "./types.js";

export const type: ActionType = "wait";
export const description = "Pause before the next step";

const MAX_WAIT_SECONDS = 10;
const ACK_BUDGET_SECONDS = 3;

/**
 * Sleeps before continuing the chain.
 *
 * Discord expects an acknowledgement within 3 seconds, so anything longer must
 * be preceded by a deferral. The cap keeps a mis-set value from hanging the
 * request indefinitely.
 */
export const run = async ({
  config,
  logger,
}: ActionContext): Promise<ActionResponse | undefined> => {
  const requested = configNumber(config, "seconds") ?? 1;
  const seconds = Math.min(Math.max(requested, 0), MAX_WAIT_SECONDS);

  if (seconds > ACK_BUDGET_SECONDS) {
    logger.warn(
      `wait: ${seconds}s exceeds Discord's ${ACK_BUDGET_SECONDS}s ack window — make sure the flow defers first.`,
    );
  }

  await new Promise((resolve) => setTimeout(resolve, seconds * 1000));
  return undefined; // continue to the next step
};

export default run;

```

