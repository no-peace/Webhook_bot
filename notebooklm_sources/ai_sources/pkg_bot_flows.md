# Repository Context Group: pkg_bot_flows
# Source Repository: discohook/discohook

### File: `packages/bot/src/flows/backup.ts`
```ts
import { channelLink, time } from "@discordjs/formatters";
import {
  type APIButtonComponentWithCustomId,
  type APIComponentInMessageActionRow,
  type APIEmbed,
  type APIGuildMember,
  type APIInteractionDataResolvedChannel,
  type APIInteractionDataResolvedGuildMember,
  type APIMessageTopLevelComponent,
  type APIRole,
  type APISelectMenuComponent,
  type APIUser,
  ButtonStyle,
  ComponentType,
  MessageFlags,
} from "discord-api-types/v10";
import { MessageFlagsBitField } from "discord-bitflag";
import { getDate } from "discord-snowflake";
import type { QueryData, TriggerKVGuild } from "store";
import { isSnowflakeSafe } from "../commands/reactionRoles.js";
import { cdn } from "../util/cdn.js";
import { isActionRow } from "../util/components.js";
import { FlowFailure, type LiveVariables } from "./flows.js";

export const assertGetSnowflake = (id: string): `${bigint}` => {
  if (isSnowflakeSafe(id)) return id;
  throw Error(`${id} is not a snowflake.`);
};

const flattenMember = (
  vars: {
    member?: APIGuildMember | APIInteractionDataResolvedGuildMember;
    user?: APIUser;
    guild?: TriggerKVGuild;
  },
  prefix = "member",
): Record<string, string | number | undefined> => {
  const key = (attr: string) => `${prefix}.${attr}`;

  const mention = vars.user ? `<@${vars.user.id}>` : undefined;
  return {
    [key("role_ids")]: JSON.stringify(vars.member ? vars.member.roles : []),
    // Legacy-compatible (v1) format options
    [key("id")]: vars.user?.id,
    [key("name")]: vars.user?.username,
    [key("discriminator")]: vars.user?.discriminator,
    [key("display_name")]:
      vars.member?.nick ?? vars.user?.global_name ?? vars.user?.username,
    [key("tag")]:
      vars.user?.discriminator === "0"
        ? vars.user.username
        : `${vars.user?.username}#${vars.user?.discriminator}`,
    [key("mention")]: mention,
    [key("avatar_url")]:
      vars.member?.avatar && vars.guild && vars.user
        ? cdn.guildMemberAvatar(
            vars.guild.id,
            vars.user.id,
            vars.member.avatar,
            {
              size: 2048,
              extension: vars.member.avatar.startsWith("a_") ? "gif" : "webp",
            },
          )
        : vars.user?.avatar
          ? cdn.avatar(vars.user.id, vars.user.avatar, {
              size: 2048,
              extension: vars.user.avatar.startsWith("a_") ? "gif" : "webp",
            })
          : cdn.defaultAvatar(
              vars.user
                ? vars.user.discriminator === "0"
                  ? Number((BigInt(vars.user.id) >> 22n) % 6n)
                  : Number(vars.user.discriminator) % 5
                : 5,
            ),
    [key("default_avatar_url")]: cdn.defaultAvatar(
      vars.user
        ? vars.user.discriminator === "0"
          ? Number((BigInt(vars.user.id) >> 22n) % 6n)
          : Number(vars.user.discriminator) % 5
        : 5,
    ),
    [key("bot")]: vars.user?.bot ? "True" : "False",
    [key("created")]: vars.user
      ? time(getDate(assertGetSnowflake(vars.user.id)), "d")
      : undefined,
    [key("created_relative")]: vars.user
      ? time(getDate(assertGetSnowflake(vars.user.id)), "R")
      : undefined,
    [key("created_long")]: vars.user
      ? time(getDate(assertGetSnowflake(vars.user.id)), "F")
      : undefined,
    // User assumptions (other bots may use these?)
    mention,
    user: mention,
  };
};

const flattenChannel = (
  vars: { channel?: APIInteractionDataResolvedChannel },
  prefix = "channel",
): Record<string, string | undefined> => {
  const key = (attr: string) => `${prefix}.${attr}`;
  return {
    [key("id")]: vars.channel?.id,
    [key("name")]: vars.channel?.name ?? undefined,
    [key("mention")]: vars.channel ? `<#${vars.channel.id}>` : undefined,
    [key("link")]: vars.channel ? channelLink(vars.channel.id) : undefined,
  };
};

const flattenRole = (
  vars: { role?: APIRole },
  prefix = "role",
): Record<string, string | number | undefined> => {
  const key = (attr: string) => `${prefix}.${attr}`;
  return {
    [key("id")]: vars.role?.id,
    [key("name")]: vars.role?.name ?? undefined,
    [key("mention")]: vars.role ? `<@&${vars.role.id}>` : undefined,
    [key("color")]: vars.role ? `#${vars.role.color.toString(16)}` : undefined,
    [key("color_decimal")]: vars.role?.color,
  };
};

const ordinal = (num: number): string => {
  const str = String(num);
  return str.endsWith("11") || str.endsWith("12") || str.endsWith("13")
    ? `${num}th`
    : str.endsWith("1")
      ? `${num}st`
      : str.endsWith("2")
        ? `${num}nd`
        : str.endsWith("3")
          ? `${num}rd`
          : `${num}th`;
};

export const getReplacements = (
  vars: LiveVariables,
  setVars: Record<string, string | boolean>,
) => {
  const now = new Date();
  const values: Record<string, string | number | undefined> = {
    ...flattenMember(vars),
    // Server
    "server.id": vars.guild?.id,
    "server.name": vars.guild?.name,
    "server.icon_url": vars.guild?.icon
      ? cdn.icon(vars.guild.id, vars.guild.icon, { size: 2048 })
      : "",
    "server.members": vars.guild?.members,
    // "server.online_members": vars.guild?.online_members,
    "server.channels": 0,
    "server.roles": vars.guild?.roles,
    "server.boosts": vars.guild?.boosts,
    // "server.emojis": vars.guild?.emojis,
    "server.emoji_limit": vars.guild?.emoji_limit,
    "server.sticker_limit": vars.guild?.sticker_limit,
    "server.created": vars.guild
      ? time(getDate(assertGetSnowflake(vars.guild.id)), "d")
      : undefined,
    "server.created_relative": vars.guild
      ? time(getDate(assertGetSnowflake(vars.guild.id)), "R")
      : undefined,
    "server.created_long": vars.guild
      ? time(getDate(assertGetSnowflake(vars.guild.id)), "F")
      : undefined,
    // More
    now: time(now, "d"),
    now_relative: time(now, "R"),
    now_long: time(now, "F"),
  };

  // Select menu values
  if (vars.selected_values && vars.selected_values.length !== 0) {
    let i = 0;
    for (const value of vars.selected_values) {
      // Intentionally 1-indexed
      i += 1;
      values[`selected_values.${i}`] = value;
    }
    const first = vars.selected_values[0];
    values.selected_value = first;
    if (vars.selected_resolved && "members" in vars.selected_resolved) {
      const memberVars = flattenMember(
        {
          member: vars.selected_resolved.members?.[first],
          user: vars.selected_resolved.users?.[first],
          guild: vars.guild,
        },
        "selected_member",
      );
      Object.assign(values, memberVars);
    }
    if (vars.selected_resolved && "channels" in vars.selected_resolved) {
      const channelVars = flattenChannel(
        { channel: vars.selected_resolved.channels?.[first] },
        "selected_channel",
      );
      Object.assign(values, channelVars);
    }
    if (vars.selected_resolved && "roles" in vars.selected_resolved) {
      const roleVars = flattenRole(
        { role: vars.selected_resolved.roles?.[first] },
        "selected_role",
      );
      Object.assign(values, roleVars);
    }
  }

  // Allow shadowing per https://discohook.app/guide/recipes/checks
  for (const [key, val] of Object.entries(setVars)) {
    values[key] = String(val);
  }

  // Ordinal for any number value
  for (const [key, val] of Object.entries(values)) {
    if (typeof val === "number") {
      values[`${key}_ordinal`] = ordinal(val);
    }
  }

  return values;
};

type Replacements = ReturnType<typeof getReplacements>;

export const insertReplacements = <T extends {}>(
  target: T,
  fromData:
    | { replacements: Replacements }
    | {
        liveVars: LiveVariables;
        setVars: Record<string, string | boolean>;
      },
) => {
  let stringified = JSON.stringify(target);
  const replacements =
    "replacements" in fromData
      ? fromData.replacements
      : getReplacements(fromData.liveVars, fromData.setVars);

  for (const [key, value] of Object.entries(replacements)) {
    if (
      value == null ||
      key.includes(" ") ||
      Object.keys(target).includes(key)
    ) {
      continue;
    }
    // Remains to be seen if this is a good solution. I think it's reasonably
    // "sandboxed," but I haven't yet explored purposely trying to break out
    // of it. If you can do that or know how, please contact me privately!
    // https://discohook.app/discord
    stringified = stringified.replaceAll(`{${key}}`, String(value));
  }
  const parsed = JSON.parse(stringified) as T;
  return parsed;
};

export const processQueryData = async (
  queryData: QueryData,
  liveVars: LiveVariables,
  setVars: Record<string, string | boolean>,
  messageIndex?: number | null,
) => {
  const message =
    messageIndex === null
      ? queryData.messages[
          Math.floor(Math.random() * queryData.messages.length)
        ]
      : queryData.messages[messageIndex ?? 0];
  if (!message) {
    throw new FlowFailure("No message at the specified position.");
  }

  const query = new URLSearchParams();
  if (message.thread_id) {
    // This is "templatable" in that it will be replaced by the `threadId`
    // variable if one exists
    query.set("thread_id", message.thread_id);
  }
  const flags = new MessageFlagsBitField(message.data.flags ?? 0);
  // Required for non-app webhooks to use CV2
  if (flags.has(MessageFlags.IsComponentsV2)) {
    query.set("with_components", "true");
  }

  const data = {
    content: message.data.content || undefined,
    embeds:
      message.data.embeds?.map((e) => {
        if (e.color === null) e.color = undefined;
        return e as APIEmbed;
      }) || undefined,
    components: message.data.components
      ? structuredClone(message.data.components).map((row) => {
          const removeCustomIds = (
            children: APIComponentInMessageActionRow[],
          ) => {
            for (const child of children) {
              if (
                child.type === ComponentType.Button &&
                (child.style === ButtonStyle.Link ||
                  child.style === ButtonStyle.Premium)
              ) {
                // @ts-expect-error Prevent doublekeying due to site state
                child.custom_id = undefined;
              }
            }
          };
          if (row.type === ComponentType.Container) {
            for (const component of row.components) {
              if (isActionRow(component)) removeCustomIds(component.components);
              else if (
                component.type === ComponentType.Section &&
                component.accessory.type === ComponentType.Button
              ) {
                removeCustomIds([component.accessory]);
              }
            }
          }
          if (isActionRow(row)) removeCustomIds(row.components);
          else if (
            row.type === ComponentType.Section &&
            row.accessory.type === ComponentType.Button
          ) {
            removeCustomIds([row.accessory]);
          }

          return row;
        })
      : [],
    username: message.data.username ?? message.data.author?.name,
    avatar_url: message.data.avatar_url ?? message.data.author?.icon_url,
    thread_name: message.data.thread_name,
    flags: message.data.flags,
  };
  const parsed = insertReplacements(data, { liveVars, setVars });
  return { body: parsed, query };
};

export const prefixCustomIds = async (
  components: APIMessageTopLevelComponent[],
  prefix: string,
  filter?: (
    component: APIButtonComponentWithCustomId | APISelectMenuComponent,
  ) => boolean,
) => {
  for (const topLevel of components) {
    switch (topLevel.type) {
      case ComponentType.ActionRow:
        for (const child of topLevel.components) {
          if ("custom_id" in child && (filter ? filter(child) : true)) {
            const customId = `${prefix}${child.custom_id}`;
            if (customId.length <= 100) {
              child.custom_id = customId;
            }
          }
        }
        break;
      case ComponentType.Section: {
        const accessory = topLevel.accessory;
        if ("custom_id" in accessory && (filter ? filter(accessory) : true)) {
          const customId = `${prefix}${accessory.custom_id}`;
          if (customId.length <= 100) {
            accessory.custom_id = customId;
          }
        }
        break;
      }
      case ComponentType.Container:
        prefixCustomIds(topLevel.components, prefix);
        break;
      default:
        break;
    }
  }
  return components;
};

```

### File: `packages/bot/src/flows/flows.ts`
```ts
import type { REST, RouteLike } from "@discordjs/rest";
import {
  type APIGuildMember,
  type APIMessage,
  type APIMessageChannelSelectInteractionData,
  type APIMessageComponentInteraction,
  type APIMessageMentionableSelectInteractionData,
  type APIMessageRoleSelectInteractionData,
  type APIMessageUserSelectInteractionData,
  type APIUser,
  ChannelType,
  GuildPremiumTier,
  InteractionType,
  PermissionFlagsBits,
  type RESTError,
  type RESTGetAPIChannelResult,
  RESTJSONErrorCodes,
  type RESTPostAPIChannelThreadsJSONBody,
  type RESTPostAPIChannelThreadsResult,
  type RESTPostAPIGuildForumThreadsJSONBody,
  Routes,
} from "discord-api-types/v10";
import { MessageFlagsBitField, PermissionsBitField } from "discord-bitflag";
import { SignJWT } from "jose";
import {
  type AnonymousVariable,
  type DBWithSchema,
  type DraftFlow,
  type FlowAction,
  type FlowActionAddRole,
  type FlowActionCheckFunction,
  FlowActionCheckFunctionType,
  type FlowActionCreateThread,
  type FlowActionRemoveRole,
  type FlowActionSendMessage,
  type FlowActionSendWebhookMessage,
  type FlowActionSetVariable,
  FlowActionSetVariableType,
  type FlowActionToggleRole,
  FlowActionType,
  getchTriggerGuild,
  getDb,
  makeSnowflake,
  messageLogEntries,
  ResponsibleUser,
  type TriggerKVGuild,
  webhooks,
} from "store";
import z from "zod";
import { getWebhook } from "../commands/webhooks/webhookInfo.js";
import { InteractionContext } from "../interactions.js";
import type { Env } from "../types/env.js";
import { isDiscordError } from "../util/error.js";
import { isThreadMessage } from "../util/messages.js";
import { createREST } from "../util/rest.js";
import { sleep } from "../util/sleep.js";
import { sortRoles } from "../util/user.js";
import {
  getReplacements,
  insertReplacements,
  prefixCustomIds,
  processQueryData,
} from "./backup.js";
import { FlowLogger, FlowLoggerMessageStatus } from "./logger.js";

// TODO: use KV `cache-guildChannels-{id}` here somehow
export interface LiveVariables {
  member?: APIGuildMember;
  user?: APIUser;
  guild?: TriggerKVGuild;
  selected_values?: string[];
  selected_resolved?: (
    | APIMessageChannelSelectInteractionData
    | APIMessageMentionableSelectInteractionData
    | APIMessageRoleSelectInteractionData
    | APIMessageUserSelectInteractionData
  )["resolved"];
}

export class FlowFailure extends Error {
  constructor(
    public message: string,
    public discordError?: RESTError,
  ) {
    super();
  }
}

export class FlowStop extends Error {
  constructor() {
    super("Halt due to stop-type action");
  }
}

// export class FlowPause extends Error {
//   constructor(until: Date) {
//     const sec = Math.floor((until.valueOf() - new Date().valueOf()) / 1000);
//     super(
//       `Paused due to wait-type action, thus ended in this process. Flow will resume in ${sec} seconds`,
//     );
//   }
// }

export interface FlowResult {
  status: "success" | "failure";
  stopped?: boolean;
  paused?: boolean;
  message: string;
  discordError?: RESTError;
}

type SetVariables = Record<string, string | boolean>;

type SentMessages = Record<string, { route: RouteLike }>;

const TriggerKVGuildScheme: z.ZodType<TriggerKVGuild> = z.object({
  id: z.string(),
  name: z.string(),
  icon: z.string().nullable(),
  owner_id: z.string(),
  members: z.number(),
  online_members: z.number(),
  roles: z.number(),
  boosts: z.number(),
  boost_level: z.enum(GuildPremiumTier),
  vanity_code: z.string().nullable(),
  emoji_limit: z.number().optional(),
  sticker_limit: z.number().optional(),
  _roles: z
    .object({
      id: z.string(),
      position: z.number(),
      permissions: z.string(),
    })
    .array()
    .optional(),
});

const BouncerPayloadScheme = z.object({
  liveVars: z.object({
    member: z
      .object({ user: z.object({ id: z.string() }).loose() })
      .loose()
      .optional(),
    user: z.object({ id: z.string() }).loose().loose().optional(),
    guild: TriggerKVGuildScheme.optional(),
    selected_values: z.string().array().optional(),
    selected_resolved: z.record(z.string(), z.object({}).loose()).optional(),
  }) as z.ZodType<LiveVariables>,
  setVars: (
    z.record(
      z.string(),
      z.union([z.string(), z.boolean()]),
    ) satisfies z.ZodType<SetVariables>
  ).optional(),
  sentMessages: (
    z.record(
      z.string(),
      z.object({ route: z.string().regex(/^\//) as z.ZodType<RouteLike> }),
    ) satisfies z.ZodType<SentMessages>
  ).optional(),
  lastReturnValue: z.any().optional(),
  recursion: z.number().int().min(0).optional(),
  interaction: (
    (
      z.object({
        type: z.literal(InteractionType.MessageComponent),
        id: z.string(),
        token: z.string(),
        guild_id: z.string().optional(),
      }) satisfies z.ZodType<
        Pick<
          APIMessageComponentInteraction,
          "id" | "token" | "guild_id" | "type"
        >
      >
    ).loose() as unknown as z.ZodType<APIMessageComponentInteraction>
  ).optional(),
  flow: z.looseObject({
    actions: z
      .looseObject({
        type: z.enum(FlowActionType),
      })
      .array(),
  }) as z.ZodType<Pick<DraftFlow, "actions">>,
  responsibleUser: ResponsibleUser.optional(),
});

export const bounceFlow = async (
  env: Env,
  payload: z.infer<typeof BouncerPayloadScheme>,
  until?: Date,
) => {
  if (!env.BOUNCER_ORIGIN || !env.BOUNCER_JWT_KEY) {
    throw Error("Worker is not configured with bouncer details");
  }

  const key = new TextEncoder().encode(env.BOUNCER_JWT_KEY);
  const jwt = await new SignJWT()
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setIssuer("discohook:bot")
    .setAudience("discohook:bouncer")
    .setExpirationTime("1 minute")
    .sign(key);
  await fetch(`${env.BOUNCER_ORIGIN}/flow/pause`, {
    method: "POST",
    body: JSON.stringify({
      until: until ? until.valueOf() : undefined,
      payload,
    }),
    headers: {
      "Content-Type": "application/json",
      Authorization: jwt,
    },
  });
};

export const resumeFlowFromBouncer = async (
  env: Env,
  raw: unknown,
): Promise<FlowResult> => {
  const parsed = await z.object({ payload: BouncerPayloadScheme }).spa(raw);
  if (!parsed.success) {
    return {
      status: "failure",
      message: `Invalid payload to resume: ${JSON.stringify(z.treeifyError(parsed.error))}`,
    };
  }
  const { payload } = parsed.data;

  const db = getDb(env.HYPERDRIVE);
  const rest = createREST(env);
  const ctx = payload.interaction
    ? new InteractionContext(rest, payload.interaction, env)
    : undefined;

  // console.log("running from bounce", payload.flow);
  return await executeFlow({
    env,
    flow: payload.flow,
    rest,
    db,
    liveVars: payload.liveVars,
    setVars: payload.setVars,
    ctx,
    recursion: payload.recursion,
    lastReturnValue: payload.lastReturnValue,
    sentMessages: payload.sentMessages,
    responsibleUser: payload.responsibleUser,
  });
};

export const getResponsibleUser = async (
  rest: REST,
  guild: Pick<TriggerKVGuild, "id" | "_roles">,
  userId: string,
  reason?: string,
  log?: FlowLogger,
): Promise<ResponsibleUser | undefined> => {
  let member: APIGuildMember;
  try {
    member = (await rest.get(
      Routes.guildMember(guild.id, userId),
    )) as APIGuildMember;
  } catch (e) {
    if (log) {
      if (isDiscordError(e)) {
        log.add(
          `[${e.code}] ${e.rawError.message}`,
          FlowLoggerMessageStatus.Error,
        );
      } else {
        log.add(
          `Failed to get responsible user ${userId}`,
          FlowLoggerMessageStatus.Error,
        );
      }
    }
    return undefined;
  }
  const guildPermissions = new PermissionsBitField();
  if (guild._roles) {
    for (const roleId of member.roles) {
      const role = guild._roles.find((r) => r.id === roleId);
      if (!role) continue;
      guildPermissions.add(BigInt(role.permissions));
    }
  }

  return {
    id: member.user.id,
    username: member.user.username,
    roles: member.roles.sort((a, b) => {
      const aRole = guild._roles?.find((r) => r.id === a);
      const bRole = guild._roles?.find((r) => r.id === b);
      return (bRole?.position ?? 0) - (aRole?.position ?? 0);
    }),
    guild_permissions: String(guildPermissions.value),
    reason,
  };
};

interface MinimalAPIGuildChannel {
  id: string;
  type: ChannelType;
  guild_id: string;
}

export const executeFlow = async (options: {
  env: Env;
  flow: Pick<DraftFlow, "actions">;
  rest: REST;
  db: DBWithSchema;
  liveVars: LiveVariables;
  setVars?: SetVariables;
  ctx?: InteractionContext<APIMessageComponentInteraction>;
  recursion?: number;
  lastReturnValue?: any;
  sentMessages?: SentMessages;
  deferred?: boolean;
  responsibleUser?: ResponsibleUser;
  /** WARNING: do not pass to recursive executions. only level 0 should handle this. */
  responsibleUserId?: string;
  /** WARNING: do not pass to recursive executions. only level 0 should handle this. */
  responsibilityReason?: string;
  log?: FlowLogger;
  debug?: boolean;
  channels?: MinimalAPIGuildChannel[];
}): Promise<FlowResult> => {
  const {
    env,
    flow,
    rest,
    db,
    liveVars,
    setVars,
    ctx,
    recursion = 0,
    lastReturnValue: lastReturnValue_,
    sentMessages: sentMessages_,
    deferred = false,
    responsibleUser: responsibleUser_,
    responsibleUserId,
    responsibilityReason,
    log: log_,
    debug: DEBUG = false,
    channels = [],
  } = options;
  const log = log_ ?? new FlowLogger(recursion);

  if (recursion > 50) {
    return {
      status: "failure",
      message: `Too much recursion (${recursion} layers)`,
    };
  }
  let responsibleUser = responsibleUser_;
  if (
    !responsibleUser &&
    responsibleUserId &&
    liveVars.guild &&
    recursion === 0
  ) {
    log.add(`Resolving responsible user (${responsibleUserId})`);
    if (env.ENVIRONMENT === "dev") {
      console.log(
        "Resolving responsible user",
        liveVars.guild.id,
        responsibleUserId,
      );
    }
    responsibleUser = await getResponsibleUser(
      rest,
      liveVars.guild,
      responsibleUserId,
      responsibilityReason,
      log,
    );
  }
  if (recursion === 0) {
    if (env.ENVIRONMENT === "dev") console.log("Responsible:", responsibleUser);
    if (responsibleUser) {
      log.add(
        `Responsible user: <@${responsibleUser.id}> ${responsibleUser.reason ? `(${responsibleUser.reason})` : ""}`.trim(),
        FlowLoggerMessageStatus.Ok,
      );
    } else {
      log.add(
        "No responsible user. Permissions limited.",
        FlowLoggerMessageStatus.Error,
      );
    }
  }

  const responsibleOwner =
    !!responsibleUser && liveVars.guild?.owner_id === responsibleUser?.id;
  const responsibleGuildPermissions = new PermissionsBitField(
    BigInt(responsibleUser?.guild_permissions ?? 0),
  );
  let refreshedGuild = false;
  const checkRoleIdManageable = async (roleId: string, quiet = false) => {
    if (!responsibleUser) {
      if (quiet) return false;
      throw new FlowFailure(
        "A responsible user could not be determined for this flow, so out of safety the role cannot be managed.",
      );
    }
    if (liveVars.guild?.owner_id === responsibleUser.id) return true;
    if (!responsibleGuildPermissions.has(PermissionFlagsBits.ManageRoles)) {
      if (quiet) return false;
      throw new FlowFailure(
        "The responsible user for this flow does not have the Manage Roles permission.",
      );
    }
    let incoming = liveVars.guild?._roles?.find((r) => r.id === roleId);
    if (!incoming && liveVars.guild && !refreshedGuild) {
      // Refresh cache in case it's a new role or there is no roles cache
      try {
        liveVars.guild = await getchTriggerGuild(rest, env, liveVars.guild.id);
        incoming = liveVars.guild._roles?.find((r) => r.id === roleId);
        refreshedGuild = true;
      } catch {}
    }
    if (!incoming) {
      if (quiet) return false;
      throw new FlowFailure(
        "The role to be managed could not be found in the server.",
      );
    }
    if (liveVars.guild?._roles) {
      const responsibleRoles = sortRoles(
        responsibleUser.roles
          .map((r) => liveVars.guild?._roles?.find((guildR) => r === guildR.id))
          .filter((v) => !!v),
      );
      if (responsibleRoles.length === 0) return false;

      const responsibleHighestRole = responsibleRoles[0];
      const canManage = incoming.position < responsibleHighestRole.position;
      if (!canManage) {
        if (quiet) return false;
        throw new FlowFailure(
          "The responsible user for this flow has a highest role that is lower or equal to the role to be added or removed. Out of safety, the role cannot be managed.",
        );
      }
      return true;
    }
    // At minimum, disallow management of roles the user does not already have
    const hasRole = responsibleUser.roles.includes(roleId);
    if (!hasRole) {
      if (quiet) return false;
      throw new FlowFailure(
        "The responsible user for this flow may not be able to add or remove this role. Out of safety, it cannot be managed.",
      );
    }
    return true;
  };

  const botHasManageRoles = ctx
    ? ctx.appPermissons.has(PermissionFlagsBits.ManageRoles)
    : null;

  async function getChannel(
    id: string,
    quiet?: false,
  ): Promise<MinimalAPIGuildChannel>;
  async function getChannel(
    id: string,
    quiet: true,
  ): Promise<MinimalAPIGuildChannel | null>;
  async function getChannel(
    id: string,
    quiet = false,
  ): Promise<MinimalAPIGuildChannel | null> {
    if (id === ctx?.interaction.channel.id) {
      return {
        id: ctx.interaction.channel.id,
        type: ctx.interaction.channel.type,
        // we don't actually check this in any flow logic and we don't need it to know that it's ok to send to
        guild_id: ctx.interaction.guild_id ?? "",
      };
    } else if (
      liveVars.selected_resolved &&
      "channels" in liveVars.selected_resolved
    ) {
      if (liveVars.selected_resolved.channels?.[id]) {
        return {
          id,
          type: liveVars.selected_resolved.channels[id].type,
          // as above, we don't actually need this. it's necessarily the same as the current guild
          guild_id: ctx?.interaction.guild_id ?? "",
        };
      }
    }

    const channel = channels.find((c) => c.id === id);
    if (channel) {
      if (channel.guild_id !== liveVars.guild?.id) {
        if (quiet) return null;
        throw new FlowFailure(
          `<#${channel.id}> is not part of the current server`,
        );
      }
      return channel;
    }

    try {
      // i would fetch all channels, but that would not return all threads.
      // i would need to separately list all active threads, but that would exclude
      // inactive threads. therefore, it's likely faster for most flows to fetch
      // channels one by one. this is another thing that's going to be better when
      // we eventually migrate to a persistent gateway based application
      const channel = (await rest.get(
        Routes.channel(id),
      )) as RESTGetAPIChannelResult;
      if ("guild_id" in channel && channel.guild_id) {
        const minChannel: MinimalAPIGuildChannel = {
          id: channel.id,
          type: channel.type,
          guild_id: channel.guild_id,
        };
        channels.push(minChannel);
        if (minChannel.guild_id === liveVars.guild?.id) {
          return minChannel;
        } else if (!quiet) {
          throw new FlowFailure(`<#${id}> is not part of the current server`);
        }
      } else if (!quiet) {
        throw new FlowFailure(`<#${id}> is not a server channel`);
      }
    } catch (e) {
      if (e instanceof FlowFailure) throw e;
      if (isDiscordError(e)) {
        if (
          e.code === RESTJSONErrorCodes.MissingAccess ||
          e.code === RESTJSONErrorCodes.MissingPermissions
        ) {
          if (quiet) return null;
          throw new FlowFailure(`Bot cannot access <#${id}>`, e.rawError);
        }
        if (quiet) return null;
        throw new FlowFailure(`Failed to resolve <#${id}>`, e.rawError);
      }
    }
    if (quiet) return null;
    throw new FlowFailure(`Could not find <#${id}>`);
  }

  try {
    if (
      recursion === 0 &&
      deferred &&
      env.BOUNCER_ORIGIN &&
      env.BOUNCER_JWT_KEY
    ) {
      // console.log("Calculating if bounce is required");
      const processWait = (action: FlowAction): number => {
        switch (action.type) {
          case FlowActionType.Wait:
            return action.seconds;
          case FlowActionType.Check: {
            // only one branch can happen, but we don't know which yet,
            // so we take the maximum
            const thenWait = action.then
              .map(processWait)
              .reduce((a, b) => a + b, 0);
            const elseWait = action.else
              .map(processWait)
              .reduce((a, b) => a + b, 0);
            return Math.max(thenWait, elseWait);
          }
          default:
            return 0;
        }
      };

      let cumulativeWait = 0;
      for (const action of flow.actions) {
        cumulativeWait += processWait(action);
      }
      // console.log({ message: "Calculated possible wait", cumulativeWait });
      if (cumulativeWait !== 0) {
        log.add(`Potential sleep duration: ${cumulativeWait}s`);
      }

      // May need to lower or raise this
      if (cumulativeWait >= 25) {
        // console.log("Bouncing to", env.BOUNCER_ORIGIN);
        await bounceFlow(env, {
          liveVars,
          setVars,
          recursion: recursion + 1,
          interaction: ctx?.interaction,
          flow,
          responsibleUser,
        });
        return {
          status: "success",
          message: `Flow bounced to another process due to ≥${cumulativeWait}s of waiting time. Unfortunately Discohook is currently unable to give detailed feedback on this flow.`,
          paused: true,
          // TODO: some sort of job ID/a way to, at least, send a message in a channel to give feedback
        };
      }
    }
  } catch (e) {
    console.error(e);
    // try to continue without bouncing
  }

  // For now, this exists for more efficient operation of the delete message
  // action. This lets us use the webhook routes when appropriate, without
  // storing the whole context.
  const sentMessages: SentMessages = sentMessages_ ?? {};

  const vars = setVars ?? {};
  let lastReturnValue: any = lastReturnValue_;
  const resolveSetVariable = (
    v: FlowActionSetVariable | AnonymousVariable,
  ): string | boolean => {
    if (v.varType === FlowActionSetVariableType.Adaptive) {
      if (!lastReturnValue) {
        throw new FlowFailure(
          `Adaptive variable \`${
            "name" in v ? v.name : "[anonymous]"
          }\` was attempted to be assigned with attribute \`${
            v.value
          }\`, but there was no previous return value.`,
        );
      }
      return lastReturnValue[String(v.value)];
    } else if (v.varType === FlowActionSetVariableType.Get) {
      const replacements = getReplacements(liveVars, vars);
      return (
        Object.fromEntries(
          Object.entries(replacements).map((entry) => [entry[0], entry[1]]),
        )[v.value.toString()] ?? ""
      ).toString();
    }
    return v.value;
  };

  const reason = getReason(responsibleUser);
  let subActionsCompleted = 0;
  try {
    for (const action of flow.actions) {
      let actionName: string;
      try {
        actionName = FlowActionType[action.type]
          .replace(/([a-z])([A-Z])/g, "$1 $2")
          .trim();
      } catch {
        actionName = `${action.type}`;
      }
      log.add(`Action: ${actionName}`);
      switch (action.type) {
        case FlowActionType.Dud:
          break;
        case FlowActionType.Wait:
          await sleep(action.seconds * 1000);
          break;
        case FlowActionType.SetVariable:
          vars[action.name] = resolveSetVariable(action);
          break;
        case FlowActionType.Check: {
          /** Get the boolean results of all functions provided */
          const recurseFunctions = (
            functions: FlowActionCheckFunction[],
          ): boolean[] => {
            const results: boolean[] = [];
            for (const func of functions) {
              switch (func.type) {
                case FlowActionCheckFunctionType.And: {
                  results.push(
                    recurseFunctions(func.conditions).filter((r) => r !== true)
                      .length === 0,
                  );
                  break;
                }
                case FlowActionCheckFunctionType.Or: {
                  results.push(
                    recurseFunctions(func.conditions).filter((r) => r === true)
                      .length >= 1,
                  );
                  break;
                }
                case FlowActionCheckFunctionType.Not: {
                  results.push(
                    recurseFunctions(func.conditions).filter((r) => r === true)
                      .length === 0,
                  );
                  break;
                }
                case FlowActionCheckFunctionType.In: {
                  let arr: unknown[];
                  try {
                    const raw =
                      func.array.varType === FlowActionSetVariableType.Static
                        ? func.array.value
                        : resolveSetVariable(func.array);
                    arr = JSON.parse(raw.toString());
                    if (!Array.isArray(arr)) {
                      throw Error("Not an array");
                    }
                  } catch {
                    throw new FlowFailure(
                      "Provided `array` value could not be parsed as an array.",
                    );
                  }
                  const resolved = resolveSetVariable(func.element);
                  results.push(arr.includes(resolved));
                  break;
                }
                case FlowActionCheckFunctionType.Equals: {
                  const a = resolveSetVariable(func.a);
                  const b = resolveSetVariable(func.b);
                  // I thought the `loose` option might be useful in the future.
                  // It defaults to false since non-strict equality can be confusing.
                  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Equality
                  // biome-ignore lint/suspicious/noDoubleEquals: ^
                  results.push(func.loose ? a == b : a === b);
                  break;
                }
                default:
                  // This shouldn't happen, but we want to keep the return array length the same
                  results.push(false);
                  break;
              }
            }
            return results;
          };

          const checkResult = recurseFunctions([action.function])[0];
          if (checkResult) {
            const result = await executeFlow({
              env,
              flow: { actions: action.then ?? [] },
              rest,
              db,
              liveVars,
              setVars: vars,
              ctx,
              recursion: recursion + 1,
              lastReturnValue,
              sentMessages,
              responsibleUser,
              log: log.level(recursion + 1),
              debug: DEBUG,
              channels,
            });
            if (result.status === "success") {
              subActionsCompleted += action.then?.length ?? 0;
              if (result.stopped) throw new FlowStop();
            } else if (result.status === "failure") {
              throw new FlowFailure(result.message, result.discordError);
            }
          } else {
            const result = await executeFlow({
              env,
              flow: { actions: action.else ?? [] },
              rest,
              db,
              liveVars,
              setVars: vars,
              ctx,
              recursion: recursion + 1,
              lastReturnValue,
              sentMessages,
              responsibleUser,
              log: log.level(recursion + 1),
              debug: DEBUG,
              channels,
            });
            if (result.status === "success") {
              subActionsCompleted += action.else?.length ?? 0;
              if (result.stopped) throw new FlowStop();
            } else if (result.status === "failure") {
              throw new FlowFailure(result.message, result.discordError);
            }
          }
          break;
        }
        case FlowActionType.SendMessage: {
          if (!vars.channelId) {
            throw new FlowFailure(
              "No `channelId` variable was set, so the message could not be sent.",
            );
          }
          const channel = await getChannel(vars.channelId as string);
          lastReturnValue = await executeSendMessage(
            action,
            rest,
            db,
            vars,
            liveVars,
            channel,
            ctx,
            DEBUG,
          );
          log.add(
            `Message sent: ${lastReturnValue.id}`,
            FlowLoggerMessageStatus.Ok,
          );
          sentMessages[lastReturnValue.id] = {
            // prefer deleting with the interaction credentials
            route:
              ctx?.interaction.channel.id === channel.id
                ? Routes.webhookMessage(
                    ctx.interaction.application_id,
                    ctx.interaction.token,
                    lastReturnValue.id,
                  )
                : Routes.channelMessage(channel.id, lastReturnValue.id),
          };
          break;
        }
        case FlowActionType.SendWebhookMessage: {
          const returned = await executeSendWebhookMessage(
            action,
            rest,
            db,
            vars,
            liveVars,
            env,
            DEBUG,
          );
          lastReturnValue = returned.message;
          log.add(
            `Message sent: ${lastReturnValue.id}`,
            FlowLoggerMessageStatus.Ok,
          );
          sentMessages[lastReturnValue.id] = {
            // delete with the webhook credentials
            route: Routes.webhookMessage(
              returned.webhook.id,
              returned.webhook.token,
              lastReturnValue.id,
            ),
          };
          break;
        }
        case FlowActionType.DeleteMessage: {
          if (!vars.messageId) {
            throw new FlowFailure(
              "No `messageId` variable was set, so no message could be deleted.",
            );
          }
          const msg = sentMessages[vars.messageId as string];
          if (msg) {
            await executeDeleteMessage(rest, msg.route, reason);
          } else {
            if (!vars.channelId) {
              throw new FlowFailure(
                "No `channelId` variable was set, so no message could be deleted.",
              );
            }
            await executeDeleteMessage(
              rest,
              Routes.channelMessage(
                vars.channelId as string,
                vars.messageId as string,
              ),
              reason,
            );
          }
          break;
        }
        case FlowActionType.AddRole:
          if (!liveVars.guild) {
            throw new FlowFailure(
              "No server was provided to the flow executor.",
            );
          }
          await checkRoleIdManageable(action.roleId);
          log.add(
            `<@&${action.roleId}> is manageable`,
            FlowLoggerMessageStatus.Ok,
          );
          if (botHasManageRoles) {
            log.add("Bot has **Manage Roles**", FlowLoggerMessageStatus.Ok);
          } else if (botHasManageRoles === false) {
            log.add(
              "Bot does not have **Manage Roles**",
              FlowLoggerMessageStatus.Error,
            );
          }
          await executeAddRole(
            rest,
            action,
            liveVars.guild.id,
            vars as { userId: string },
            reason,
          );
          log.add(
            `Added role on <@${vars.userId}>`,
            FlowLoggerMessageStatus.Ok,
          );
          break;
        case FlowActionType.RemoveRole:
          if (!liveVars.guild) {
            throw new FlowFailure(
              "No server was provided to the flow executor.",
            );
          }
          await checkRoleIdManageable(action.roleId);
          log.add(
            `<@&${action.roleId}> is manageable`,
            FlowLoggerMessageStatus.Ok,
          );
          if (botHasManageRoles) {
            log.add("Bot has **Manage Roles**", FlowLoggerMessageStatus.Ok);
          } else if (botHasManageRoles === false) {
            log.add(
              "Bot does not have **Manage Roles**",
              FlowLoggerMessageStatus.Error,
            );
          }
          await executeRemoveRole(
            rest,
            action,
            liveVars.guild.id,
            vars as { userId: string },
            reason,
          );
          log.add(
            `Removed role on <@${vars.userId}>`,
            FlowLoggerMessageStatus.Ok,
          );
          break;
        case FlowActionType.ToggleRole:
          if (!liveVars.guild) {
            throw new FlowFailure(
              "No server was provided to the flow executor.",
            );
          }
          await checkRoleIdManageable(action.roleId);
          log.add(
            `<@&${action.roleId}> is manageable`,
            FlowLoggerMessageStatus.Ok,
          );
          if (botHasManageRoles) {
            log.add("Bot has **Manage Roles**", FlowLoggerMessageStatus.Ok);
          } else if (botHasManageRoles === false) {
            log.add(
              "Bot does not have **Manage Roles**",
              FlowLoggerMessageStatus.Error,
            );
          }
          await executeToggleRole(
            rest,
            action,
            liveVars.guild.id,
            vars as { userId: string },
            reason,
          );
          log.add(
            `Toggled role on <@${vars.userId}>`,
            FlowLoggerMessageStatus.Ok,
          );
          break;
        case FlowActionType.CreateThread: {
          if (!responsibleOwner) {
            if (
              action.threadType === ChannelType.PrivateThread &&
              !responsibleGuildPermissions.has(
                PermissionFlagsBits.CreatePrivateThreads,
              )
            ) {
              throw new FlowFailure(
                "The responsible user for this flow does not have the Create Private Threads permission.",
              );
            }
            if (
              !responsibleGuildPermissions.has(
                PermissionFlagsBits.CreatePublicThreads,
              )
            ) {
              throw new FlowFailure(
                "The responsible user for this flow does not have the Create Public Threads permission.",
              );
            }
          }

          const channelId =
            resolveSetVariable(action.channel)?.toString() ?? vars.channelId;
          lastReturnValue = await executeCreateThread(
            rest,
            action,
            { channelId },
            liveVars,
            reason,
            undefined,
          );
          break;
        }
        case FlowActionType.Stop:
          if (action.message && !!action.message.content?.trim()) {
            try {
              const { body } = await processQueryData(
                { messages: [{ data: action.message }] },
                liveVars,
                vars,
              );
              if (DEBUG && body.components) {
                prefixCustomIds(body.components, "DBG_", (c) =>
                  c.custom_id.startsWith("p_"),
                );
              }
              if (ctx) {
                await ctx.followup.send(body);
              } else {
                const { channelId } = vars;
                if (channelId && typeof channelId === "string") {
                  await rest.post(Routes.channelMessages(channelId), {
                    body,
                  });
                }
              }
              log.add("Message sent", FlowLoggerMessageStatus.Ok);
            } catch (e) {
              console.error(e);
              throw httpFlowFailure(e, "Failed to send the message.");
            }
          }
          throw new FlowStop();
        default:
          break;
      }
    }
  } catch (e) {
    if (e instanceof FlowStop) {
      return {
        status: "success",
        stopped: true,
        message: `${
          flow.actions.length + subActionsCompleted
        } actions completed successfully`,
      };
      // } else if (e instanceof FlowPause) {
      //   return {
      //     status: "success",
      //     paused: true,
      //     message: `${
      //       flow.actions.length + subActionsCompleted
      //     } actions completed prior to pause due to wait action - flow will resume automatically`,
      //   };
    } else {
      if (e instanceof FlowFailure) {
        return {
          status: "failure",
          message: e.message,
          discordError: e.discordError,
        };
      }
      console.error(e);
      return {
        status: "failure",
        message: String(e),
      };
    }
  }
  return {
    status: "success",
    message: `${
      flow.actions.length + subActionsCompleted
    } actions completed successfully`,
  };
};

const httpFlowFailure = (e: unknown, message: string) => {
  if (isDiscordError(e)) {
    return new FlowFailure(message, e.rawError);
  }
  return new FlowFailure(message);
};

const getReason = (user: ResponsibleUser | undefined) => {
  if (user === undefined) return "Action in a flow";
  const base = `Responsibility of ${user.username} (${user.id})`;
  return user.reason ? `${base}: ${user.reason}` : base;
};

const executeSendMessage = async (
  action: FlowActionSendMessage,
  rest: REST,
  db: DBWithSchema,
  setVars: SetVariables,
  liveVars: LiveVariables,
  channel: MinimalAPIGuildChannel,
  ctx?: InteractionContext<APIMessageComponentInteraction>,
  debug?: boolean,
): Promise<APIMessage> => {
  const backup = await db.query.backups.findFirst({
    where: (backups, { eq }) => eq(backups.id, makeSnowflake(action.backupId)),
    columns: {
      data: true,
    },
  });
  if (!backup) {
    throw new FlowFailure(
      "No backup was found with the stored ID, so there was no data to send the message.",
    );
  }
  if (backup.data.messages.length === 0) {
    throw new FlowFailure("The backup contains no messages.");
  }

  let message: APIMessage;
  try {
    const { body } = await processQueryData(
      backup.data,
      liveVars,
      setVars,
      action.backupMessageIndex,
    );
    const flags = Number(
      new MessageFlagsBitField(body.flags ?? 0, action.flags ?? 0).value,
    );
    if (debug && body.components) {
      prefixCustomIds(body.components, "DBG_", (c) =>
        c.custom_id.startsWith("p_"),
      );
    }

    if (ctx && channel.id === ctx.interaction.channel.id && !ctx.isExpired()) {
      message = await ctx.followup.send({ ...body, flags });
    } else {
      message = (await rest.post(Routes.channelMessages(channel.id), {
        body: { ...body, flags },
      })) as APIMessage;
    }
  } catch (e) {
    console.error(e);
    throw httpFlowFailure(e, "Failed to send the message.");
  }
  return message;
};

const executeSendWebhookMessage = async (
  action: FlowActionSendWebhookMessage,
  rest: REST,
  db: DBWithSchema,
  setVars: SetVariables,
  liveVars: LiveVariables,
  env: Env,
  debug?: boolean,
): Promise<{ webhook: { id: string; token: string }; message: APIMessage }> => {
  let webhook = await db.query.webhooks.findFirst({
    where: (webhooks, { eq, and }) =>
      and(eq(webhooks.platform, "discord"), eq(webhooks.id, action.webhookId)),
    columns: {
      id: true,
      token: true,
      discordGuildId: true,
      channelId: true,
      applicationId: true,
    },
  });
  if (!webhook || !webhook.token) {
    try {
      const retryWebhook = await getWebhook(
        action.webhookId,
        env,
        webhook?.applicationId ?? undefined,
      );
      webhook = {
        id: retryWebhook.id,
        token: retryWebhook.token ?? null,
        discordGuildId: retryWebhook.guild_id
          ? BigInt(retryWebhook.guild_id)
          : null,
        channelId: retryWebhook.channel_id,
        applicationId: retryWebhook.application_id,
      };
      if (webhook?.token) {
        await db
          .insert(webhooks)
          .values({
            ...webhook,
            name: retryWebhook.name ?? "Webhook",
            platform: "discord",
          })
          .onConflictDoUpdate({
            target: [webhooks.platform, webhooks.id],
            set: webhook,
          });
      }
    } catch {}
  }
  if (!webhook || !webhook.token) {
    throw new FlowFailure(
      "No webhook was found with the stored ID or it did not have a token associated with it.",
    );
  }

  const backup = await db.query.backups.findFirst({
    where: (backups, { eq }) => eq(backups.id, makeSnowflake(action.backupId)),
    columns: {
      data: true,
    },
  });
  if (!backup) {
    throw new FlowFailure(
      "No backup was found with the stored ID, so there was no data to send the message.",
    );
  }
  if (backup.data.messages.length === 0) {
    throw new FlowFailure("The backup contains no messages.");
  }

  let message: APIMessage;
  try {
    const { query, body } = await processQueryData(
      backup.data,
      liveVars,
      setVars,
      action.backupMessageIndex,
    );
    query.set("wait", "true");
    if (typeof setVars.threadId === "string" && setVars.threadId) {
      query.set("thread_id", setVars.threadId);
    }
    const flags = Number(
      new MessageFlagsBitField(body.flags ?? 0, action.flags ?? 0).value,
    );
    if (debug && body.components) {
      prefixCustomIds(body.components, "DBG_", (c) =>
        c.custom_id.startsWith("p_"),
      );
    }

    message = (await rest.post(Routes.webhook(webhook.id, webhook.token), {
      query,
      body: { ...body, flags },
    })) as APIMessage;
  } catch (e) {
    console.error(e);
    throw httpFlowFailure(e, "Failed to send the message.");
  }
  try {
    const msg = backup.data.messages[action.backupMessageIndex ?? 0].data;
    await db.insert(messageLogEntries).values({
      type: "send",
      webhookId: webhook.id,
      channelId: webhook.channelId,
      messageId: message.id,
      threadId: isThreadMessage(message) ? message.channel_id : undefined,
      discordGuildId: webhook.discordGuildId,
      hasContent: !!msg.content,
      embedCount: msg.embeds?.length,
      notifiedEveryoneHere: message.mention_everyone,
      notifiedUsers: message.mentions?.map((u) => u.id),
      notifiedRoles: message.mention_roles,
    });
  } catch {}
  return {
    // not expanding causes TS to think token is nullable
    webhook: { id: webhook.id, token: webhook.token },
    message,
  };
};

const executeDeleteMessage = async (
  rest: REST,
  route: RouteLike,
  reason: string,
): Promise<void> => {
  try {
    await rest.delete(route, { reason });
  } catch (e) {
    throw httpFlowFailure(e, "Failed to delete the message.");
  }
};

const executeAddRole = async (
  rest: REST,
  action: FlowActionAddRole,
  guildId: string,
  setVars: { userId: string },
  reason: string,
) => {
  if (!setVars.userId) {
    throw new FlowFailure("No user ID was set.");
  }
  try {
    await rest.put(
      Routes.guildMemberRole(guildId, setVars.userId, action.roleId),
      { reason },
    );
  } catch (e) {
    throw httpFlowFailure(e, "Failed to add the role.");
  }
};

const executeRemoveRole = async (
  rest: REST,
  action: FlowActionRemoveRole,
  guildId: string,
  setVars: { userId: string },
  reason: string,
) => {
  if (!setVars.userId) {
    throw new FlowFailure("No user ID was set.");
  }
  try {
    await rest.delete(
      Routes.guildMemberRole(guildId, setVars.userId, action.roleId),
      { reason },
    );
  } catch (e) {
    throw httpFlowFailure(e, "Failed to remove the role.");
  }
};

const executeToggleRole = async (
  rest: REST,
  action: FlowActionToggleRole,
  guildId: string,
  setVars: { userId: string },
  reason: string,
) => {
  if (!setVars.userId) {
    throw new FlowFailure("No user ID was set.");
  }
  try {
    const member = (await rest.get(
      Routes.guildMember(guildId, setVars.userId),
    )) as APIGuildMember;
    if (member.roles.includes(action.roleId)) {
      await rest.delete(
        Routes.guildMemberRole(guildId, setVars.userId, action.roleId),
        { reason },
      );
    } else {
      await rest.put(
        Routes.guildMemberRole(guildId, setVars.userId, action.roleId),
        { reason },
      );
    }
  } catch (e) {
    throw httpFlowFailure(e, "Failed to toggle the role.");
  }
};

const executeCreateThread = async (
  rest: REST,
  action: FlowActionCreateThread,
  setVars: { channelId: string },
  liveVars: LiveVariables,
  reason: string,
  ctx?: InteractionContext,
) => {
  const channelId = setVars.channelId;
  if (!channelId) {
    throw new FlowFailure("No channel ID was set.");
  }
  let channelType: ChannelType | undefined;
  if (ctx && ctx.interaction.channel?.id === channelId) {
    channelType = ctx.interaction.channel.type;
  }

  if (!channelType) {
    try {
      ({ type: channelType } = (await rest.get(
        Routes.channel(channelId),
      )) as RESTGetAPIChannelResult);
    } catch (e) {
      throw httpFlowFailure(
        e,
        "Failed to fetch the parent channel for the thread.",
      );
    }
  }

  let messageId: string | undefined;
  if (channelType !== ChannelType.GuildForum && action.message) {
    try {
      ({ id: messageId } = (await rest.post(Routes.channelMessages(channelId), {
        body: action.message,
      })) as APIMessage);
    } catch (e) {
      throw httpFlowFailure(e, "Failed to create a message for the thread.");
    }
  }

  const replacements = getReplacements(liveVars, setVars);
  const name = insertReplacements({ _: action.name }, { replacements })._.slice(
    0,
    100,
  );
  try {
    const thread = (await rest.post(Routes.threads(channelId, messageId), {
      body:
        channelType === ChannelType.GuildForum
          ? ({
              name,
              message: action.message
                ? insertReplacements(action.message, { replacements })
                : { content: "No message" },
              applied_tags: action.appliedTags,
              auto_archive_duration: action.autoArchiveDuration,
              rate_limit_per_user: action.rateLimitPerUser,
            } satisfies RESTPostAPIGuildForumThreadsJSONBody)
          : ({
              name,
              auto_archive_duration: action.autoArchiveDuration,
              rate_limit_per_user: action.rateLimitPerUser,
              type: action.threadType,
              invitable: action.invitable,
            } satisfies RESTPostAPIChannelThreadsJSONBody),
      reason,
    })) as RESTPostAPIChannelThreadsResult;
    return thread;
  } catch (e) {
    throw httpFlowFailure(e, "Failed to create the thread.");
  }
};

```

### File: `packages/bot/src/flows/logger.ts`
```ts
export enum FlowLoggerMessageStatus {
  Info = 0,
  Ok = 1,
  Error = 2,
}

const statusEmoji: Record<FlowLoggerMessageStatus, string> = {
  // dev
  // [FlowLoggerMessageStatus.Ok]: "834927244500533258",
  // [FlowLoggerMessageStatus.Error]: "834927293633527839",
  // [FlowLoggerMessageStatus.Info]: "1253688417275871302",
  // prod
  [FlowLoggerMessageStatus.Ok]: "1263857933209571329",
  [FlowLoggerMessageStatus.Error]: "1263857948086505482",
  [FlowLoggerMessageStatus.Info]: "1263857962892660786",
};

export class FlowLogger {
  public messages: FlowLoggerMessage[] = [];

  constructor(
    public recursion = 0,
    public parent?: FlowLogger,
  ) {
    this.messages = [];
  }

  add(message: string, status?: FlowLoggerMessageStatus): void;
  add(message: FlowLoggerMessage): void;
  add(
    message: string | FlowLoggerMessage,
    status = FlowLoggerMessageStatus.Info,
  ): void {
    const msg =
      typeof message === "string"
        ? new FlowLoggerMessage(status, message, this.recursion)
        : message;

    if (this.parent) this.parent.add(msg);
    else this.messages.push(msg);
  }

  level(recursion: number) {
    return new FlowLogger(recursion, this);
  }
}

export class FlowLoggerMessage {
  constructor(
    public status: FlowLoggerMessageStatus,
    public message: string,
    public recursionLevel: number,
  ) {}

  toString() {
    const emojiId = statusEmoji[this.status];
    const emoji = `<:_:${emojiId}>`;
    if (this.recursionLevel === 0) {
      return `${emoji} ${this.message}`;
    }
    return `${emoji} [${this.recursionLevel}] ${this.message}`;
  }
}

```

