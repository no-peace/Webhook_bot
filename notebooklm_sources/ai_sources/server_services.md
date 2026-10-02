# Repository Context Group: server_services
# Source Repository: no-peace/Hoho_manager

### File: `server/src/services/actionExecutor.ts`
```ts
import { parseCustomId } from "@dmb/shared";
import type { DiscordInteraction } from "@dmb/shared";
import { getActionHandler } from "../actions/index.js";
import { actionFailed } from "../actions/responses.js";
import type { ActionContext, ActionResponse } from "../actions/types.js";
import { actionRepository, webhookProfileRepository } from "../repositories/index.js";
import { logger } from "../utils/logger.js";
import { hasBranches, selectBranch, type ExecutableStep } from "./branches.js";
import * as discord from "./discordService.js";

const log = logger.child("actions");
const MAX_BRANCH_DEPTH = 10;

export interface ExecuteResult {
  response: ActionResponse | undefined;
  handled: boolean;
  type: string | null;
}

const replaceVariables = (obj: any, vars: Record<string, any>): any => {
  if (typeof obj === 'string') {
    return obj.replace(/\{([^}]+)\}/g, (match, key) => {
      return vars[key] !== undefined ? String(vars[key]) : match;
    });
  }
  if (Array.isArray(obj)) return obj.map(v => replaceVariables(v, vars));
  if (obj !== null && typeof obj === 'object') {
    const newObj: any = {};
    for (const [k, v] of Object.entries(obj)) {
      newObj[k] = replaceVariables(v, vars);
    }
    return newObj;
  }
  return obj;
};

const snowflakeToUnix = (id: string) => {
  const epoch = 1420070400000;
  const binary = BigInt(id).toString(2).padStart(64, '0');
  const timestamp = parseInt(binary.substring(0, 42), 2) + epoch;
  return Math.floor(timestamp / 1000);
};

export const executeCustomId = async (
  customId: string,
  interaction: DiscordInteraction,
): Promise<ExecuteResult> => {
  const parsed = parseCustomId(customId);
  if (!parsed) return { response: undefined, handled: false, type: null };

  const stored = await actionRepository.findByCustomId(customId);
  const steps: ExecutableStep[] =
    stored.length > 0
      ? stored.map((definition) => ({
          id: definition.id,
          type: definition.action_type,
          config: definition.config ?? {},
        }))
      : [{ id: null, type: parsed.type, config: parsed.params }];

  const user = interaction.member?.user ?? interaction.user;
  const member = interaction.member as any;
  const userId = user?.id ?? "unknown";
  
  const username = user?.username ?? "User";
  const displayname = member?.nick ?? user?.global_name ?? username;

  const unixNow = Math.floor(Date.now() / 1000);
  const userCreated = user?.id ? snowflakeToUnix(user.id) : unixNow;
  const joinedAt = member?.joined_at ? Math.floor(new Date(member.joined_at).getTime() / 1000) : unixNow;

  const variables: Record<string, unknown> = {
    // User
    "user.mention": `<@${userId}>`,
    "user.name": username,
    "user.displayname": displayname,
    "user.id": userId,
    "user.avatar": user?.avatar ? `https://cdn.discordapp.com/avatars/${userId}/${user.avatar}.png` : "",
    "user.created": `<t:${userCreated}:d>`,
    "user.joined": `<t:${joinedAt}:R>`,
    
    // Server
    "server.id": interaction.guild_id ?? "unknown",
    "server.name": "Your Server",
    "server.icon": interaction.guild_id ? `https://cdn.discordapp.com/icons/${interaction.guild_id}/icon.png` : "",
    
    // Channel & Bot
    "channel.id": interaction.channel_id ?? "unknown",
    "channel.mention": interaction.channel_id ? `<#${interaction.channel_id}>` : "unknown",
    "bot.id": interaction.application_id ?? "unknown",
    "bot.mention": interaction.application_id ? `<@${interaction.application_id}>` : "unknown",
    
    // Time
    "now": `<t:${unixNow}:t>`,
    "now.relative": `<t:${unixNow}:R>`,
    "now.long": `<t:${unixNow}:F>`,
    "now.unix": unixNow
  };

  const botToken = await discord.resolveBotToken().catch(() => null);
  const context: Omit<ActionContext, "config"> = { interaction, variables, botToken, discord, repositories: { webhookProfiles: webhookProfileRepository }, logger: log };

  const logStep = async (step: ExecutableStep, response: ActionResponse | undefined, startedAt: number): Promise<void> => {
    await actionRepository.log({
      actionDefinitionId: step.id, interactionId: interaction.id, userId, guildId: interaction.guild_id ?? null, channelId: interaction.channel_id ?? null, status: response ? "success" : "pending", response: { type: step.type, ms: Date.now() - startedAt },
    });
  };

  const runSteps = async (list: ExecutableStep[], depth: number): Promise<ActionResponse | undefined> => {
    if (depth > MAX_BRANCH_DEPTH) return actionFailed("That flow nests too deeply to run.");

    for (const step of list) {
      const handler = getActionHandler(step.type);
      if (!handler) continue;

      const started = Date.now();

      if (step.type === "check" && hasBranches(step.config)) {
        const parsedConfig = replaceVariables(step.config, variables);
        const branch = selectBranch(parsedConfig, variables);
        const nested = await runSteps(branch, depth + 1);
        await logStep(step, nested, started);
        if (nested) return nested;
        continue;
      }

      let response: ActionResponse | undefined;
      try {
        const parsedConfig = replaceVariables(step.config, variables);
        response = await handler.run({ ...context, config: parsedConfig });
      } catch (error) {
        response = actionFailed("Something went wrong running that action.");
      }

      await logStep(step, response, started);
      if (response) return response;
    }
    return undefined;
  };

  const response = await runSteps(steps, 0);
  return { response, handled: true, type: parsed.type };
};

export default { executeCustomId };
```

### File: `server/src/services/branches.test.ts`
```ts
import { describe, expect, it } from "vitest";
import { hasBranches, readBranch, selectBranch } from "./branches.js";

/**
 * Branch parsing and selection.
 *
 * The `then` / `else` arrays are untrusted JSON on their way in from the editor,
 * and picking the wrong branch is the difference between a button working and a
 * flow silently doing the wrong thing — so both halves are pinned here, away from
 * the database the executor otherwise needs.
 */

const step = (type: string, config: Record<string, unknown> = {}) => ({ type, config });

describe("readBranch", () => {
  it("returns an empty list for non-arrays", () => {
    expect(readBranch(undefined)).toEqual([]);
    expect(readBranch(null)).toEqual([]);
    expect(readBranch("nope")).toEqual([]);
    expect(readBranch({ type: "dud" })).toEqual([]);
  });

  it("reads type and config, defaulting the id to null", () => {
    expect(readBranch([step("add_role", { roleId: "1" })])).toEqual([
      { id: null, type: "add_role", config: { roleId: "1" } },
    ]);
  });

  it("falls back to a dud for a non-string type and to {} for a non-object config", () => {
    expect(readBranch([{ type: 42, config: "bad" }])).toEqual([
      { id: null, type: "dud", config: {} },
    ]);
  });

  it("drops malformed entries instead of throwing", () => {
    const parsed = readBranch([null, "x", 7, [], step("stop")]);
    expect(parsed).toEqual([{ id: null, type: "stop", config: {} }]);
  });

  it("preserves a nested check's own branches", () => {
    const nested = step("check", {
      function: "equals",
      conditions: [{ a: "1", b: "1" }],
      then: [step("stop", { content: "yes" })],
      else: [],
    });
    const [parsed] = readBranch([nested]);
    expect(readBranch(parsed?.config.then)).toEqual([
      { id: null, type: "stop", config: { content: "yes" } },
    ]);
  });
});

describe("hasBranches", () => {
  it("is false when neither branch has steps", () => {
    expect(hasBranches({ function: "equals" })).toBe(false);
    expect(hasBranches({ then: [], else: [] })).toBe(false);
  });

  it("is true when either branch has a step", () => {
    expect(hasBranches({ else: [step("stop")] })).toBe(true);
    expect(hasBranches({ then: [step("stop")] })).toBe(true);
  });
});

describe("selectBranch", () => {
  const config = {
    function: "equals",
    conditions: [{ a: "{{flag}}", b: "on" }],
    then: [step("stop", { content: "on" })],
    else: [step("stop", { content: "off" })],
  };

  it("takes `then` when the condition passes", () => {
    const branch = selectBranch(config, { flag: "on" });
    expect(branch).toEqual([{ id: null, type: "stop", config: { content: "on" } }]);
  });

  it("takes `else` when the condition fails", () => {
    const branch = selectBranch(config, { flag: "off" });
    expect(branch).toEqual([{ id: null, type: "stop", config: { content: "off" } }]);
  });

  it("returns empty when the chosen branch is empty, so the flow falls through", () => {
    expect(selectBranch({ function: "equals", conditions: [], then: [] }, {})).toEqual([]);
  });
});

```

### File: `server/src/services/branches.ts`
```ts
export interface ExecutableStep {
  id: string | null;
  type: string;
  config: Record<string, any>;
}

export const hasBranches = (config: Record<string, any>): boolean => {
  // Detects if the action contains nested steps in Discohook's pass/fail format
  return Array.isArray(config.pass) || Array.isArray(config.fail);
};

const evaluateCondition = (left: any, op: string, right: any): boolean => {
  const l = String(left ?? "").trim();
  const r = String(right ?? "").trim();

  const numL = Number(l);
  const numR = Number(r);
  
  // Ensure both sides are valid numbers before doing mathematical comparisons
  const isNum = !isNaN(numL) && !isNaN(numR) && l !== "" && r !== "";

  switch (op) {
    case "==":
    case "equals":
    case "is equal to":
      return l === r;
    case "!=":
    case "not_equals":
      return l !== r;
    case ">":
      return isNum ? numL > numR : l > r;
    case ">=":
      return isNum ? numL >= numR : l >= r;
    case "<":
      return isNum ? numL < numR : l < r;
    case "<=":
      return isNum ? numL <= numR : l <= r;
    case "includes":
      return l.includes(r);
    case "not_includes":
      return !l.includes(r);
    case "starts_with":
      return l.startsWith(r);
    case "ends_with":
      return l.endsWith(r);
    case "is_empty":
      return l === "";
    case "is_not_empty":
      return l !== "";
    default:
      return l === r; // Fallback to strict equality
  }
};

export const selectBranch = (
  config: Record<string, any>,
  variables: Record<string, unknown>
): ExecutableStep[] => {
  // Fallback operator is "==" if none is provided by the UI
  const operator = config.op || config.operator || "==";
  const isTrue = evaluateCondition(config.left, operator, config.right);

  // Return the 'pass' array if true, or the 'fail' array if false
  if (isTrue) {
    return config.pass || [];
  } else {
    return config.fail || [];
  }
};
```

### File: `server/src/services/discordService.ts`
```ts
import { DISCORD_API_BASE, InteractionResponseType, MessageFlags } from "@dmb/shared";
import type { DiscordMessagePayload, DiscordUser, InteractionResponse } from "@dmb/shared";
import { env } from "../config/env.js";
import { botProfileRepository } from "../repositories/profileRepository.js";
import { ApiError } from "../utils/errors.js";
import { logger } from "../utils/logger.js";
import { parseWebhookUrl } from "../utils/validation.js";

const log = logger.child("discord");

/**
 * Everything that talks to Discord's REST API lives here.
 *
 * Two things are kept strictly separate:
 *   - **Webhook calls** need no bot token and may be made with a URL supplied by
 *     the browser (they can only ever post to that one webhook).
 *   - **Bot calls** need the token, which is resolved server-side only.
 *
 * The token is *never* accepted from a request body — callers pass a profile id
 * or fall back to the environment variable.
 */

/** A guild member, as far as this app cares. */
export interface GuildMember {
  roles?: string[];
  user?: DiscordUser;
}

/** A created message, as far as this app cares. */
export interface DiscordMessage {
  id: string;
  channel_id: string;
}

const sleep = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));

const asRecord = (value: unknown): Record<string, unknown> =>
  typeof value === "object" && value !== null ? (value as Record<string, unknown>) : {};

/** Pull Discord's own error message out of an error body, with a fallback. */
const readErrorMessage = (data: unknown, status: number): string => {
  const message = asRecord(data).message;
  return typeof message === "string" ? message : `Discord responded with ${status}`;
};

/**
 * Resolve the bot token to use for an outbound request.
 * Preference: explicit profile id -> the configured env token.
 */
export const resolveBotToken = async (profileId: number | null = null): Promise<string> => {
  if (profileId != null) {
    const token = await botProfileRepository.revealToken(profileId);
    if (!token) throw ApiError.notFound(`Bot profile ${profileId} not found`);
    return token;
  }

  if (!env.discord.botToken) {
    // Deliberately user-visible: "Internal server error" would send someone
    // hunting through logs for a one-line config fix.
    throw new ApiError(503, "No bot token is configured on the server", {
      code: "bot_token_missing",
      expose: true,
    });
  }
  return env.discord.botToken;
};

interface ApiRequestOptions {
  body?: unknown;
  /** Sent as `Authorization: <auth> <token>`. Omit for interaction callbacks. */
  token?: string;
  auth?: string;
  retries?: number;
  /** Skip the base-URL join (used for webhook endpoints). */
  absoluteUrl?: string;
}

/**
 * Low-level fetch against the Discord API with retry/backoff.
 *
 * Discord signals throttling with 429 and a `retry_after` (seconds); transient
 * 5xx responses are also retried. 4xx is never retried — that is our bug.
 */
const apiRequest = async <T>(
  method: string,
  path: string | null,
  {
    body,
    token,
    auth = "Bot",
    retries = 3,
    absoluteUrl,
  }: ApiRequestOptions = {},
): Promise<T | null> => {
  const url = absoluteUrl ?? `${DISCORD_API_BASE}${path ?? ""}`;
  let attempt = 0;

  for (;;) {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers.Authorization = `${auth} ${token}`;

    let response: Response;
    try {
      response = await fetch(url, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
      });
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error);
      if (attempt >= retries) {
        throw ApiError.upstream(`Could not reach Discord: ${reason}`);
      }
      await sleep(2 ** attempt * 500);
      attempt += 1;
      continue;
    }

    // 204 No Content (most webhook sends) has no body to parse.
    if (response.status === 204) return null;

    const isJson = (response.headers.get("content-type") ?? "").includes("application/json");
    const data: unknown = isJson
      ? await response.json().catch(() => null)
      : await response.text();

    if (response.ok) return data as T;

    // Throttled — honour Discord's own retry hint.
    if (response.status === 429 && attempt < retries) {
      const retryAfter = asRecord(data).retry_after;
      const retryAfterMs = Math.ceil((typeof retryAfter === "number" ? retryAfter : 1) * 1000);
      log.warn(`Rate limited by Discord; retrying in ${retryAfterMs}ms`);
      await sleep(Math.min(retryAfterMs, 10_000));
      attempt += 1;
      continue;
    }

    // Transient server errors are worth another shot.
    if (response.status >= 500 && attempt < retries) {
      await sleep(2 ** attempt * 500);
      attempt += 1;
      continue;
    }

    const message = readErrorMessage(data, response.status);

    if (response.status === 401) {
      throw new ApiError(401, `Discord rejected the credentials: ${message}`, {
        code: "discord_unauthorized",
        details: data,
      });
    }

    throw ApiError.upstream(`Discord error: ${message}`, {
      status: response.status,
      discord: data,
    });
  }
};

/* ── Webhooks (no bot token required) ─────────────────────────────────────── */

export interface WebhookSendOptions {
  wait?: boolean;
  threadId?: string | null;
}

/**
 * POST a message through a webhook URL.
 *
 * @param webhookUrl full Discord webhook URL
 * @param payload    message payload (content/embeds/components)
 */
export const sendWebhook = async (
  webhookUrl: string,
  payload: DiscordMessagePayload,
  { wait = true, threadId }: WebhookSendOptions = {},
): Promise<DiscordMessage | null> => {
  const parsed = parseWebhookUrl(webhookUrl);
  if (!parsed) throw ApiError.badRequest("Not a valid Discord webhook URL");

  const params = new URLSearchParams();
  if (wait) params.set("wait", "true");
  if (threadId) params.set("thread_id", threadId);

  const query = params.toString();
  const absoluteUrl = `${DISCORD_API_BASE}/webhooks/${parsed.id}/${parsed.token}${
    query ? `?${query}` : ""
  }`;

  const message = await apiRequest<DiscordMessage>("POST", null, {
    body: { ...payload, allowed_mentions: payload.allowed_mentions ?? { parse: [] } },
    absoluteUrl,
  });

  log.info(`Sent webhook message${message?.id ? ` ${message.id}` : ""}`);
  return message;
};

/** Inspect a webhook without sending (used to validate a URL before saving). */
export const getWebhookInfo = async (webhookUrl: string): Promise<unknown> => {
  const parsed = parseWebhookUrl(webhookUrl);
  if (!parsed) throw ApiError.badRequest("Not a valid Discord webhook URL");

  return apiRequest<unknown>("GET", null, {
    absoluteUrl: `${DISCORD_API_BASE}/webhooks/${parsed.id}/${parsed.token}`,
  });
};

/* ── Bot (token required, server-side only) ───────────────────────────────── */

export interface BotSendOptions {
  profileId?: number | null;
}

/** Send a message to a channel as the bot. */
export const sendChannelMessage = async (
  channelId: string,
  payload: DiscordMessagePayload,
  { profileId = null }: BotSendOptions = {},
): Promise<DiscordMessage | null> => {
  const token = await resolveBotToken(profileId);

  const message = await apiRequest<DiscordMessage>("POST", `/channels/${channelId}/messages`, {
    token,
    body: { ...payload, allowed_mentions: payload.allowed_mentions ?? { parse: [] } },
  });

  log.info(`Bot sent message ${message?.id} to channel ${channelId}`);
  return message;
};

/** Resolve who a token belongs to — doubles as a validity check. */
export const getBotIdentity = async (token: string): Promise<DiscordUser | null> =>
  apiRequest<DiscordUser>("GET", "/users/@me", { token });

export const addGuildMemberRole = async (
  guildId: string,
  userId: string,
  roleId: string,
  token: string,
): Promise<boolean> => {
  await apiRequest("PUT", `/guilds/${guildId}/members/${userId}/roles/${roleId}`, { token });
  return true;
};

export const removeGuildMemberRole = async (
  guildId: string,
  userId: string,
  roleId: string,
  token: string,
): Promise<boolean> => {
  await apiRequest("DELETE", `/guilds/${guildId}/members/${userId}/roles/${roleId}`, { token });
  return true;
};

export const getGuildMember = async (
  guildId: string,
  userId: string,
  token: string,
): Promise<GuildMember | null> =>
  apiRequest<GuildMember>("GET", `/guilds/${guildId}/members/${userId}`, { token });

export const hasRole = async (
  guildId: string,
  userId: string,
  roleId: string,
  token: string,
): Promise<boolean> => {
  const member = await getGuildMember(guildId, userId, token);
  return Array.isArray(member?.roles) && member.roles.includes(roleId);
};

/** Open (or reuse) a DM channel with a user, then send `payload` to it. */
export const sendDirectMessage = async (
  userId: string,
  payload: DiscordMessagePayload,
  token: string,
): Promise<DiscordMessage | null> => {
  const channel = await apiRequest<{ id: string }>("POST", "/users/@me/channels", {
    token,
    body: { recipient_id: userId },
  });
  if (!channel) throw ApiError.upstream("Discord did not return a DM channel");

  return apiRequest<DiscordMessage>("POST", `/channels/${channel.id}/messages`, {
    token,
    body: { ...payload, allowed_mentions: payload.allowed_mentions ?? { parse: [] } },
  });
};

export const deleteChannelMessage = async (
  channelId: string,
  messageId: string,
  token: string,
): Promise<boolean> => {
  await apiRequest("DELETE", `/channels/${channelId}/messages/${messageId}`, { token });
  return true;
};

/**
 * Start a thread on an existing message.
 *
 * Discord threads off the *message*, not the channel, which is why this needs
 * both ids. Used by the `create_thread` flow action.
 */
export const createThreadFromMessage = async (
  channelId: string,
  messageId: string,
  name: string,
  token: string,
): Promise<{ id: string } | null> =>
  apiRequest<{ id: string }>("POST", `/channels/${channelId}/messages/${messageId}/threads`, {
    token,
    body: { name },
  });

/* ── Interaction responses ────────────────────────────────────────────────── */

/**
 * Respond to an interaction using its `application_id` + `token`.
 *
 * These calls need no bot token — the interaction token *is* the credential, and
 * it expires 15 minutes after the interaction was created.
 */
export const createInteractionResponse = async (
  applicationId: string,
  interactionToken: string,
  response: InteractionResponse,
): Promise<unknown> =>
  apiRequest("POST", `/interactions/${applicationId}/${interactionToken}/callback`, {
    auth: "",
    body: response,
  });

export const createFollowupMessage = async (
  applicationId: string,
  interactionToken: string,
  payload: DiscordMessagePayload,
): Promise<unknown> =>
  apiRequest("POST", `/webhooks/${applicationId}/${interactionToken}`, { body: payload });

export const editOriginalResponse = async (
  applicationId: string,
  interactionToken: string,
  payload: DiscordMessagePayload,
): Promise<unknown> =>
  apiRequest("PATCH", `/webhooks/${applicationId}/${interactionToken}/messages/@original`, {
    body: payload,
  });

/** Defer a response so we still have time to do slow work before replying. */
export const deferResponse = async (
  applicationId: string,
  interactionToken: string,
  { ephemeral = false }: { ephemeral?: boolean } = {},
): Promise<unknown> =>
  createInteractionResponse(applicationId, interactionToken, {
    type: InteractionResponseType.DeferredChannelMessageWithSource,
    data: ephemeral ? { flags: MessageFlags.Ephemeral } : {},
  });

export default {
  resolveBotToken,
  sendWebhook,
  getWebhookInfo,
  sendChannelMessage,
  getBotIdentity,
  addGuildMemberRole,
  removeGuildMemberRole,
  getGuildMember,
  hasRole,
  sendDirectMessage,
  deleteChannelMessage,
  createThreadFromMessage,
  createInteractionResponse,
  createFollowupMessage,
  editOriginalResponse,
  deferResponse,
};

```

### File: `server/src/services/interactionHandler.ts`
```ts
import { InteractionResponseType, InteractionType } from "@dmb/shared";
import type { DiscordInteraction, InteractionResponse } from "@dmb/shared";
import { ephemeral } from "../actions/responses.js";
import { executeCustomId } from "./actionExecutor.js";
import { logger } from "../utils/logger.js";

const log = logger.child("interactions");

/**
 * Turn one interaction into the callback body Discord expects.
 *
 * This is the single decision point for *what* to reply, deliberately separated
 * from *how the reply is delivered*. There are two deliveries, and they must
 * behave identically:
 *
 *   1. **Webhook** — Discord POSTs to `POST /api/interactions`; the body we return
 *      here is the HTTP response, which Discord reads directly. Requires the app's
 *      Interactions Endpoint URL to be set (Cloudflare Tunnel, or any public
 *      HTTPS address).
 *   2. **Gateway relay** — the app has no public URL, so the gateway worker
 *      receives `INTERACTION_CREATE` and forwards the payload to
 *      `POST /api/interactions/relay`; we then POST this body to Discord's
 *      callback endpoint using the interaction token. See
 *      {@link file://./../routes/interactions.ts}.
 *
 * Discord gives the app **3 seconds** to reply or the user sees "This
 * interaction failed", so no path may return without an answer — including the
 * error path, which is why the catch lives here rather than in a route.
 */
export const handleInteraction = async (
  interaction: DiscordInteraction,
): Promise<InteractionResponse> => {
  // Discord's endpoint-validation handshake (webhook mode only).
  if (interaction.type === InteractionType.Ping) {
    return { type: InteractionResponseType.Pong };
  }

  const customId = interaction.data?.custom_id;

  try {
    if (customId) {
      const { response, handled } = await executeCustomId(customId, interaction);

      if (response) return response;

      if (handled) {
        // The chain ran but produced no visible output — acknowledge quietly.
        //
        // Which "quiet" is valid depends on the interaction: "update the message
        // with no changes" only exists for components on a message, and Discord
        // rejects it for a modal submit, which must answer with a channel
        // response instead.
        return {
          type:
            interaction.type === InteractionType.MessageComponent
              ? InteractionResponseType.DeferredUpdateMessage
              : InteractionResponseType.DeferredChannelMessageWithSource,
        };
      }

      log.warn(
        `Ignoring unrecognised custom_id from ${interaction.user?.id ?? "?"}: ${customId}`,
      );
      return ephemeral("This component isn't wired up to an action.");
    }

    // Interaction types we receive but don't act on yet (e.g. an application
    // command). Defer so Discord doesn't time us out.
    log.debug(`Unhandled interaction type ${interaction.type}`);
    return { type: InteractionResponseType.DeferredChannelMessageWithSource };
  } catch (error) {
    // Never let an exception surface as a timeout — Discord would retry and the
    // user would just see "interaction failed".
    const reason = error instanceof Error ? error.message : String(error);
    const stack = error instanceof Error ? error.stack : undefined;
    log.error(`Failed to handle interaction ${interaction.id}: ${reason}`, stack);
    return ephemeral("\u26a0\ufe0f Something went wrong handling that interaction.");
  }
};

export default handleInteraction;

```

### File: `server/src/services/profileService.ts`
```ts
import type { WebhookProfileRecord } from "@dmb/shared";
import {
  botProfileRepository,
  webhookProfileRepository,
  type PublicBotProfile,
} from "../repositories/profileRepository.js";
import * as discord from "./discordService.js";
import { ApiError } from "../utils/errors.js";
import { parseWebhookUrl } from "../utils/validation.js";

/**
 * Profile management for both send modes.
 *
 * A webhook profile stores a URL; a bot profile stores an encrypted token. Both
 * are validated against Discord before we persist them, so a typo surfaces
 * immediately rather than at send time.
 */

export interface CreateWebhookProfileInput {
  name: string;
  url: string;
  avatarUrl?: string | null;
  isDefault?: number;
}

export interface CreateBotProfileInput {
  name: string;
  token: string;
  applicationId: string;
  publicKey: string;
  defaultGuildId?: string | null;
}

/**
 * Pull the ids Discord knows about out of a webhook response.
 * The endpoint returns them untyped, so this narrows before we persist.
 */
const readWebhookIds = (
  info: unknown,
): { guildId: string | null; channelId: string | null } => {
  if (info === null || typeof info !== "object") return { guildId: null, channelId: null };
  const record = info as Record<string, unknown>;
  return {
    guildId: typeof record.guild_id === "string" ? record.guild_id : null,
    channelId:
      typeof record.channel_id === "string"
        ? record.channel_id
        : typeof record.channel_id === "number"
          ? String(record.channel_id)
          : null,
  };
};

export const webhookProfileService = {
  async list(userId: number): Promise<WebhookProfileRecord[]> {
    return webhookProfileRepository.listByUser(userId);
  },

  /**
   * Validate a webhook URL and create a profile from it.
   * We call Discord so the user finds out about a dead webhook right away.
   */
  async create(
    userId: number,
    { name, url, avatarUrl = null, isDefault = 0 }: CreateWebhookProfileInput,
  ): Promise<WebhookProfileRecord> {
    if (!parseWebhookUrl(url)) {
      throw ApiError.badRequest("That isn't a valid Discord webhook URL");
    }

    const info = await discord.getWebhookInfo(url).catch(() => null);
    if (!info) {
      throw ApiError.badRequest("Discord rejected that webhook URL — check it is active");
    }

    const { guildId, channelId } = readWebhookIds(info);

    const profile = await webhookProfileRepository.create({
      userId,
      name,
      url,
      guildId,
      channelId,
      avatarUrl,
      isDefault,
    });
    if (!profile) throw ApiError.upstream("Webhook profile could not be created");

    if (isDefault) {
      const promoted = await webhookProfileRepository.setDefault(profile.id, userId);
      if (promoted) return promoted;
    }
    return profile;
  },

  async update(
    id: number,
    userId: number,
    patch: Parameters<typeof webhookProfileRepository.update>[1],
  ): Promise<WebhookProfileRecord> {
    const existing = await webhookProfileRepository.findById(id);
    if (!existing) throw ApiError.notFound("Webhook profile not found");
    if (existing.user_id !== userId) {
      throw ApiError.forbidden("That profile belongs to someone else");
    }

    if (patch.url && !parseWebhookUrl(patch.url)) {
      throw ApiError.badRequest("That isn't a valid Discord webhook URL");
    }

    const updated = await webhookProfileRepository.update(id, patch);
    if (!updated) throw ApiError.notFound("Webhook profile not found");

    if (patch.is_default === 1) {
      const promoted = await webhookProfileRepository.setDefault(id, userId);
      if (promoted) return promoted;
    }
    return updated;
  },

  async setDefault(id: number, userId: number): Promise<WebhookProfileRecord> {
    const existing = await webhookProfileRepository.findById(id);
    if (!existing || existing.user_id !== userId) {
      throw ApiError.notFound("Webhook profile not found");
    }

    const promoted = await webhookProfileRepository.setDefault(id, userId);
    if (!promoted) throw ApiError.notFound("Webhook profile not found");
    return promoted;
  },

  async remove(id: number, userId: number): Promise<boolean> {
    const existing = await webhookProfileRepository.findById(id);
    if (!existing) throw ApiError.notFound("Webhook profile not found");
    if (existing.user_id !== userId) {
      throw ApiError.forbidden("That profile belongs to someone else");
    }
    return webhookProfileRepository.delete(id);
  },
};

export const botProfileService = {
  /** Never returns the token — only metadata plus `has_token`. */
  async list(userId: number): Promise<PublicBotProfile[]> {
    return botProfileRepository.listByUser(userId);
  },

  /**
   * Validate the token by asking Discord who it belongs to, then store it
   * encrypted. `applicationId` and `publicKey` are required so interactions can
   * be verified against the same bot.
   */
  async create(
    userId: number,
    { name, token, applicationId, publicKey, defaultGuildId = null }: CreateBotProfileInput,
  ): Promise<PublicBotProfile> {
    const identity = await discord.getBotIdentity(token).catch(() => null);
    if (!identity) throw ApiError.badRequest("Discord rejected that bot token");

    const profile = await botProfileRepository.create({
      userId,
      name,
      token,
      applicationId,
      publicKey,
      defaultGuildId,
    });
    if (!profile) throw ApiError.upstream("Bot profile could not be created");
    return profile;
  },

  async update(
    id: number,
    userId: number,
    patch: Parameters<typeof botProfileRepository.update>[1],
  ): Promise<PublicBotProfile> {
    const existing = await botProfileRepository.findById(id);
    if (!existing) throw ApiError.notFound("Bot profile not found");
    if (existing.user_id !== userId) {
      throw ApiError.forbidden("That profile belongs to someone else");
    }

    // Re-validate whenever the token changes.
    if (patch.token) {
      const identity = await discord.getBotIdentity(patch.token).catch(() => null);
      if (!identity) throw ApiError.badRequest("Discord rejected that bot token");
    }

    const updated = await botProfileRepository.update(id, patch);
    if (!updated) throw ApiError.notFound("Bot profile not found");
    return updated;
  },

  async remove(id: number, userId: number): Promise<boolean> {
    const existing = await botProfileRepository.findById(id);
    if (!existing) throw ApiError.notFound("Bot profile not found");
    if (existing.user_id !== userId) {
      throw ApiError.forbidden("That profile belongs to someone else");
    }
    return botProfileRepository.delete(id);
  },
};

export default { webhookProfileService, botProfileService };

```

### File: `server/src/services/templateService.ts`
```ts
import type {
  ActionDefinitionRecord,
  ActionType,
  QueryData,
  StoredActionDefinition,
  TemplateRecord,
} from "@dmb/shared";
import { actionRepository } from "../repositories/actionRepository.js";
import {
  templateRepository,
  type TemplateSummary,
} from "../repositories/templateRepository.js";
import { ApiError } from "../utils/errors.js";

/**
 * Template use-cases.
 *
 * Routes stay thin: they parse the request and delegate here. The service owns
 * the rule that saving a template also replaces its action definitions, so the
 * two tables can never drift apart.
 */

const MAX_TEMPLATES_PER_USER = 500;

export interface TemplateWithActions extends TemplateRecord {
  /**
   * Always the editor wire shape (`customId`/`actionType`), never raw DB rows.
   * Returning `action_type` here used to make loaded flows come back with
   * `undefined` step types.
   */
  actions: StoredActionDefinition[];
}

/** DB rows -> the editor's wire shape. */
const toStoredActions = (records: ActionDefinitionRecord[]): StoredActionDefinition[] =>
  records.map((record) => ({
    customId: record.custom_id,
    actionType: record.action_type as ActionType,
    config: record.config ?? {},
    executionOrder: record.execution_order,
  }));

export interface CreateTemplateServiceInput {
  name: string;
  description?: string | null;
  data: QueryData | Record<string, unknown>;
  actions?: StoredActionDefinition[];
  isPublic?: number;
}

export interface UpdateTemplateServiceInput {
  name?: string;
  description?: string | null;
  data?: QueryData | Record<string, unknown>;
  actions?: StoredActionDefinition[];
  isPublic?: number;
}

export const templateService = {
  async list(userId: number, { q }: { q?: string } = {}): Promise<TemplateSummary[]> {
    return templateRepository.search({ userId, q: q?.trim() || null });
  },

  async get(id: number, userId: number): Promise<TemplateWithActions> {
    const template = await templateRepository.findById(id);
    if (!template) throw ApiError.notFound("Template not found");
    if (template.user_id !== userId) {
      throw ApiError.forbidden("That template belongs to someone else");
    }

    return { ...template, actions: toStoredActions(await actionRepository.listByTemplate(id)) };
  },

  async create(
    userId: number,
    { name, description = null, data, actions = [], isPublic = 0 }: CreateTemplateServiceInput,
  ): Promise<TemplateWithActions> {
    const existing = await templateRepository.findByUser(userId);
    if (existing.length >= MAX_TEMPLATES_PER_USER) {
      throw ApiError.badRequest(`You've reached the ${MAX_TEMPLATES_PER_USER} template limit`);
    }

    const template = await templateRepository.create({
      userId,
      name,
      description,
      data,
      isPublic,
    });
    if (!template) throw ApiError.upstream("Template could not be created");

    if (actions.length > 0) {
      await actionRepository.replaceForTemplate(template.id, actions);
    }

    return this.get(template.id, userId);
  },

  async update(
    id: number,
    userId: number,
    { name, description, data, actions, isPublic }: UpdateTemplateServiceInput,
  ): Promise<TemplateWithActions> {
    // Ownership check happens inside get().
    await this.get(id, userId);

    if (data !== undefined) {
      // `data` is the whole message document, so an update always replaces it.
      await templateRepository.updateData(id, data);
    }

    const updated = await templateRepository.update(id, { name, description, is_public: isPublic });
    if (!updated) throw ApiError.notFound("Template not found");

    if (actions !== undefined) {
      await actionRepository.replaceForTemplate(id, actions);
    }

    return { ...updated, actions: toStoredActions(await actionRepository.listByTemplate(id)) };
  },

  async remove(id: number, userId: number): Promise<boolean> {
    await this.get(id, userId);
    return templateRepository.delete(id);
  },
};

export default templateService;

```

