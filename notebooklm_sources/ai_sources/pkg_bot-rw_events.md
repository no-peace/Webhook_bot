# Repository Context Group: pkg_bot-rw_events
# Source Repository: discohook/discohook

### File: `packages/bot-rw/src/events/channelDelete.ts`
```ts
import { GatewayDispatchEvents } from "discord-api-types/v10";
import { eq } from "drizzle-orm";
import { webhooks } from "store";
import { createHandler } from "./handler";

export default createHandler(
  GatewayDispatchEvents.ChannelDelete,
  async ({ data, client }) => {
    const db = client.getDb();
    await db.delete(webhooks).where(eq(webhooks.channelId, data.id));
  },
);

```

### File: `packages/bot-rw/src/events/entitlementCreate.ts`
```ts
import { GatewayDispatchEvents } from "discord-api-types/v10";
import { createHandler } from "./handler";

export default createHandler(
  GatewayDispatchEvents.EntitlementCreate,
  async ({ data, api }) => {},
);

```

### File: `packages/bot-rw/src/events/entitlementDelete.ts`
```ts
import { GatewayDispatchEvents } from "discord-api-types/v10";
import { createHandler } from "./handler";

export default createHandler(
  GatewayDispatchEvents.EntitlementDelete,
  async ({ data, api }) => {},
);

```

### File: `packages/bot-rw/src/events/entitlementUpdate.ts`
```ts
import { GatewayDispatchEvents } from "discord-api-types/v10";
import { createHandler } from "./handler";

export default createHandler(
  GatewayDispatchEvents.EntitlementUpdate,
  async ({ data, api }) => {},
);

```

### File: `packages/bot-rw/src/events/guildCreate.ts`
```ts
import { GatewayDispatchEvents } from "discord-api-types/v10";
import { createHandler } from "./handler";

export default createHandler(
  GatewayDispatchEvents.GuildCreate,
  async ({ client, data: guild }) => {
    if (!client.ready) return;

    // For some reason in dev I was receiving these events only after the
    // client was ready, in which scenario I don't think it would be possible
    // to determine if this is a new authorization or just an event to fill
    // cache. Maybe we could implement a timeout per shard before we start
    // accepting these as new guilds?
    console.log("GUILD_CREATE", guild.id, { ready: client.ready });

    // const db = client.getDb();
    // const moderated = await client.KV.get<{ state: "banned"; reason?: string }>(
    //   `moderation-guild-${guild.id}`,
    //   "json",
    // );
    // if (moderated?.state === "banned") {
    //   await client.api.users.leaveGuild(guild.id);
    //   return;
    // }

    // const now = sql`NOW()`;
    // await db
    //   .insert(discordGuilds)
    //   .values({
    //     id: makeSnowflake(guild.id),
    //     name: guild.name,
    //     icon: guild.icon,
    //     ownerDiscordId: makeSnowflake(guild.owner_id),
    //     botJoinedAt: now,
    //   })
    //   .onConflictDoUpdate({
    //     target: discordGuilds.id,
    //     set: {
    //       name: guild.name,
    //       icon: guild.icon,
    //       ownerDiscordId: makeSnowflake(guild.owner_id),
    //       botJoinedAt: sql`CASE WHEN ${discordGuilds.botJoinedAt} IS NULL THEN ${now} ELSE excluded."botJoinedAt" END`,
    //     },
    //   });

    // await db
    //   .delete(discordRoles)
    //   .where(eq(discordRoles.guildId, makeSnowflake(guild.id)));
    // await db
    //   .insert(discordRoles)
    //   .values(
    //     guild.roles.map((role) => ({
    //       id: makeSnowflake(role.id),
    //       guildId: makeSnowflake(guild.id),
    //       name: role.name,
    //       position: role.position,
    //       color: role.color,
    //       hoist: role.hoist,
    //       icon: role.icon,
    //       unicodeEmoji: role.unicode_emoji,
    //       managed: role.managed,
    //       mentionable: role.mentionable,
    //       permissions: role.permissions,
    //     })),
    //   )
    //   .onConflictDoUpdate({
    //     target: discordRoles.id,
    //     set: {
    //       name: sql`excluded.name`,
    //       position: sql`excluded.position`,
    //       color: sql`excluded.color`,
    //       hoist: sql`excluded.hoist`,
    //       icon: sql`excluded.icon`,
    //       unicodeEmoji: sql`excluded."unicodeEmoji"`,
    //       managed: sql`excluded.managed`,
    //       mentionable: sql`excluded.mentionable`,
    //       permissions: sql`excluded.permissions`,
    //     },
    //   });
  },
);

```

### File: `packages/bot-rw/src/events/guildDelete.ts`
```ts
import { GatewayDispatchEvents } from "discord-api-types/v10";
import { eq } from "drizzle-orm";
import { discordGuilds, makeSnowflake } from "store";
import { createHandler } from "./handler";

export default createHandler(
  GatewayDispatchEvents.GuildDelete,
  async ({ client, data }) => {
    // > If the unavailable field is not set, the user was removed from the guild.
    // https://discord.dev/topics/gateway-events#guild-delete
    // We only care about this event if the bot has been removed.
    if (data.unavailable !== undefined) return;

    const db = client.getDb();
    await db
      .delete(discordGuilds)
      .where(eq(discordGuilds.id, makeSnowflake(data.id)));

    // No reason to keep these in memory
    await client.KV.delete(`cache-triggerGuild-${data.id}`);
    await client.KV.delete(`cache-guild-${data.id}`);
  },
);

```

### File: `packages/bot-rw/src/events/guildEmojisUpdate.ts`
```ts
import { GatewayDispatchEvents } from "discord-api-types/v10";
import { createHandler } from "./handler";

// Automatically manage emoji cache so we don't need to deal with stale data.
// Ideally small enough that this isn't an issue
export default createHandler(
  GatewayDispatchEvents.GuildEmojisUpdate,
  async ({ client, data }) => {
    const manager = client.emojiManagers.get(data.guild_id);
    if (manager) {
      manager.updateEmojis(
        data.emojis.map(({ id, name, animated }) => ({ id, name, animated })),
      );
    }
    // Wait until we need it so we don't just cache every server's
    // emojis for no reason
    // else {
    //   const manager = new EmojiManagerCache(data.emojis);
    //   client.emojiManagers.set(data.guild_id, manager);
    // }
  },
);

```

### File: `packages/bot-rw/src/events/guildMemberAdd.ts`
```ts
import { GatewayDispatchEvents } from "discord-api-types/v10";
import { and, eq } from "drizzle-orm";
import {
  backups,
  ensureTriggerFlow,
  type FlowAction,
  type FlowActionCheck,
  FlowActionCheckFunctionType,
  type FlowActionDeleteMessage,
  type FlowActionSendMessage,
  type FlowActionSendWebhookMessage,
  type FlowActionSetVariable,
  FlowActionSetVariableType,
  FlowActionType,
  type FlowActionWait,
  flowActions,
  flows,
  makeSnowflake,
  TriggerEvent,
  type TriggerKVGuild,
  triggers,
  upsertDiscordUser,
  upsertGuild,
  webhooks,
  welcomer_goodbye,
  welcomer_hello,
} from "store";
import type { Client } from "../client.js";
import { executeFlow, type FlowResult } from "../flows/flows.js";
import { createHandler } from "./handler";

export const getWelcomerConfigurations = async (
  client: Client,
  type: "add" | "remove",
  guild: TriggerKVGuild,
) => {
  const db = client.getDb();

  let configs = await db.query.triggers.findMany({
    columns: {
      id: true,
      disabled: true,
      flow: true,
      flowId: true,
    },
    where: and(
      eq(triggers.platform, "discord"),
      eq(triggers.discordGuildId, makeSnowflake(guild.id)),
      eq(
        triggers.event,
        type === "add" ? TriggerEvent.MemberAdd : TriggerEvent.MemberRemove,
      ),
    ),
  });
  if (configs.length === 0) {
    const oldTable = type === "add" ? welcomer_hello : welcomer_goodbye;
    const oldConfiguration = await db
      .select({
        id: oldTable.id,
        channelId: oldTable.channelId,
        deleteMessagesAfter: oldTable.deleteMessagesAfter,
        lastModifiedAt: oldTable.lastModifiedAt,
        lastModifiedById: oldTable.lastModifiedById,
        webhookId: oldTable.webhookId,
        webhookToken: oldTable.webhookToken,
        messageData: oldTable.messageData,
        overrideDisabled: oldTable.overrideDisabled,
        ignoreBots: oldTable.ignoreBots,
      })
      .from(oldTable)
      .where(eq(oldTable.guildId, BigInt(guild.id)));

    if (oldConfiguration.length !== 0) {
      let backupId: bigint | undefined;
      const dUserId = oldConfiguration[0].lastModifiedById
        ? String(oldConfiguration[0].lastModifiedById)
        : guild.owner_id;

      let userId = 0n;

      if (
        oldConfiguration[0].messageData ||
        oldConfiguration[0].lastModifiedById
      ) {
        const user = await client.api.users.get(dUserId);
        userId = (await upsertDiscordUser(db, user)).id;
      }

      if (oldConfiguration[0].messageData) {
        const backup = await db
          .insert(backups)
          .values({
            name: `Welcomer (${type})`,
            data: {
              version: "d2",
              messages: [
                {
                  data: JSON.parse(oldConfiguration[0].messageData),
                },
              ],
            },
            dataVersion: "d2",
            ownerId: userId,
          })
          .returning({ id: backups.id });
        backupId = backup[0].id;
      }
      let webhookInvalid = false;
      if (oldConfiguration[0].webhookId && oldConfiguration[0].webhookToken) {
        try {
          const webhook = await client.api.webhooks.get(
            String(oldConfiguration[0].webhookId),
            String(oldConfiguration[0].webhookToken),
          );
          await db
            .insert(webhooks)
            .values({
              platform: "discord",
              id: String(oldConfiguration[0].webhookId),
              token: String(oldConfiguration[0].webhookToken),
              name: webhook.name ?? "Unknown Welcomer Webhook",
              channelId: webhook.channel_id,
              discordGuildId: makeSnowflake(webhook.guild_id ?? guild.id),
              applicationId: webhook.application_id,
              avatar: webhook.avatar,
            })
            .onConflictDoUpdate({
              target: [webhooks.platform, webhooks.id],
              set: {
                name: webhook.name ?? undefined,
                channelId: webhook.channel_id,
                avatar: webhook.avatar,
              },
            });
        } catch {
          webhookInvalid = true;
        }
      }
      await upsertGuild(db, guild);

      const flow = (
        await db
          .insert(flows)
          .values({
            name: `Welcomer (${type})`,
          })
          .returning()
      )[0];
      const actions: FlowAction[] = backupId
        ? [
            ...(oldConfiguration[0].ignoreBots
              ? [
                  {
                    type: FlowActionType.Check,
                    function: {
                      type: FlowActionCheckFunctionType.Equals,
                      a: {
                        varType: FlowActionSetVariableType.Get,
                        value: "member.bot",
                      },
                      b: {
                        varType: FlowActionSetVariableType.Static,
                        value: true,
                      },
                    },
                    // biome-ignore lint/suspicious/noThenProperty: see note in quick.ts about this
                    then: [{ type: FlowActionType.Stop }],
                    else: [],
                  } satisfies FlowActionCheck,
                ]
              : []),
            ...(oldConfiguration[0].webhookId && !webhookInvalid
              ? [
                  {
                    type: FlowActionType.SendWebhookMessage,
                    webhookId: String(oldConfiguration[0].webhookId),
                    backupId: backupId.toString(),
                  } satisfies FlowActionSendWebhookMessage,
                  {
                    type: FlowActionType.SetVariable,
                    varType: FlowActionSetVariableType.Adaptive,
                    name: "channelId",
                    value: "channel_id",
                  } satisfies FlowActionSetVariable,
                ]
              : [
                  {
                    type: FlowActionType.SetVariable,
                    name: "channelId",
                    value: String(oldConfiguration[0].channelId),
                  } satisfies FlowActionSetVariable,
                  {
                    type: FlowActionType.SendMessage,
                    backupId: backupId.toString(),
                  } satisfies FlowActionSendMessage,
                ]),
            ...(oldConfiguration[0].deleteMessagesAfter
              ? [
                  {
                    type: FlowActionType.SetVariable,
                    varType: FlowActionSetVariableType.Adaptive,
                    name: "messageId",
                    value: "id",
                  } satisfies FlowActionSetVariable,
                  {
                    type: FlowActionType.Wait,
                    seconds: oldConfiguration[0].deleteMessagesAfter,
                  } satisfies FlowActionWait,
                  {
                    type: FlowActionType.DeleteMessage,
                  } satisfies FlowActionDeleteMessage,
                ]
              : []),
          ]
        : [];
      if (actions.length !== 0) {
        await db.insert(flowActions).values(
          actions.map((action) => ({
            flowId: flow.id,
            type: action.type,
            data: action,
          })),
        );
      }

      const protoConfigs = await db
        .insert(triggers)
        .values({
          platform: "discord",
          event:
            type === "add" ? TriggerEvent.MemberAdd : TriggerEvent.MemberRemove,
          discordGuildId: makeSnowflake(guild.id),
          updatedById: userId || undefined,
          updatedAt: oldConfiguration[0].lastModifiedAt
            ? new Date(oldConfiguration[0].lastModifiedAt)
            : undefined,
          disabled: oldConfiguration[0].overrideDisabled ?? undefined,
          flowId: flow.id,
        })
        .onConflictDoNothing()
        .returning({
          id: triggers.id,
          // flowId: triggers.flowId,
          disabled: triggers.disabled,
        });
      configs = [
        {
          ...protoConfigs[0],
          flow: {
            ...flow,
            actions: actions.map((data) => ({
              id: 0n, // this might need to be real in the future for diagnostics
              flowId: flow.id,
              type: data.type,
              data,
            })),
          },
        },
      ];
      await db.delete(oldTable).where(eq(oldTable.id, oldConfiguration[0].id));
    }
  } else {
    for (const trigger of configs) {
      await ensureTriggerFlow(trigger, db);
    }
  }
  return configs;
};

export type Trigger = Awaited<
  ReturnType<typeof getWelcomerConfigurations>
>[number];

export default createHandler(
  GatewayDispatchEvents.GuildMemberAdd,
  async ({ data, client }) => {
    // Don't like this. We really should store all triggers per guild id,
    // but I did this to fit with the way getWelcomerConfiguration works
    const key = `cache:triggers-${TriggerEvent.MemberAdd}-${data.guild_id}`;
    let triggers = await client.KV.get<Trigger[]>(key, "json");
    if (triggers && triggers.length === 0) {
      return;
    }

    const guild = await client.getchTriggerGuild(data.guild_id);
    const db = client.getDb();
    if (!triggers) {
      triggers = await getWelcomerConfigurations(client, "add", guild);
      await client.KV.put(key, JSON.stringify(triggers), {
        expirationTtl: 1200,
      });
    }

    const applicable = triggers.filter((t) => !!t.flow && !t.disabled);
    const results: FlowResult[] = [];
    for (const trigger of applicable) {
      results.push(
        await executeFlow({
          env,
          flow: trigger.flow,
          rest: client.rest,
          db,
          liveVars: { member: payload, user: payload.user, guild },
          deferred,
        }),
      );
    }
    return results;
  },
);

```

### File: `packages/bot-rw/src/events/guildMemberRemove.ts`
```ts
import {
  GatewayDispatchEvents,
  RESTJSONErrorCodes,
} from "discord-api-types/v10";
import { and, eq } from "drizzle-orm";
import {
  discordMembers,
  makeSnowflake,
  TriggerEvent,
  type TriggerKVGuild,
} from "store";
import { executeFlow, type FlowResult } from "../flows/flows.js";
import { isDiscordError } from "../util/error.js";
import { getWelcomerConfigurations, type Trigger } from "./guildMemberAdd.js";
import { createHandler } from "./handler";

export default createHandler(
  GatewayDispatchEvents.GuildMemberRemove,
  async ({ data, client }) => {
    if (data.user.id === Bun.env.DISCORD_APPLICATION_ID) return [];

    const key = `cache:triggers-${TriggerEvent.MemberRemove}-${data.guild_id}`;
    let triggers = await client.KV.get<Trigger[]>(key, "json");
    if (triggers && triggers.length === 0) {
      return;
    }

    const db = client.getDb();
    // Remove member relation data. This is slightly more important than storing
    // the data initially but it's still skippable
    try {
      await db.delete(discordMembers).where(
        and(
          // biome-ignore lint/style/noNonNullAssertion: Only absent for message_create and message_update
          eq(discordMembers.userId, makeSnowflake(payload.user!.id)),
          eq(discordMembers.guildId, makeSnowflake(payload.guild_id)),
        ),
      );
    } catch {}

    let guild: TriggerKVGuild;
    try {
      guild = await client.getchTriggerGuild(data.guild_id);
    } catch (e) {
      if (isDiscordError(e)) {
        return [
          {
            status: "failure",
            discordError: e.rawError,
            message:
              e.code === RESTJSONErrorCodes.UnknownGuild
                ? "Discohook cannot access the server"
                : e.rawError.message,
          } satisfies FlowResult,
        ];
      }
      throw e;
    }
    if (!triggers) {
      triggers = await getWelcomerConfigurations(client, "remove", guild);
      await client.KV.put(key, JSON.stringify(triggers), {
        expirationTtl: 600,
      });
    }

    const applicable = triggers.filter((t) => !!t.flow && !t.disabled);
    const results: FlowResult[] = [];
    for (const trigger of applicable) {
      results.push(
        await executeFlow({
          env,
          flow: trigger.flow,
          rest,
          db,
          liveVars: { user: payload.user, guild },
          deferred,
        }),
      );
    }
    return results;
  },
);

```

### File: `packages/bot-rw/src/events/handler.ts`
```ts
import type { Client, MappedEvents } from "@discordjs/core";
import type {
  AsyncEventEmitter,
  AsyncEventEmitterListenerForEvent,
} from "@vladfrangu/async_event_emitter";
import type { GatewayDispatchEvents } from "discord-api-types/v10";

export const createHandler = <E extends GatewayDispatchEvents>(
  event: E,
  callback: AsyncEventEmitterListenerForEvent<
    AsyncEventEmitter<MappedEvents>,
    E
  >,
) => {
  // TODO: see if necessary
  // const wrapped = async (payload: any) => {
  //   try {
  //     return await callback(payload);
  //   } catch (e) {
  //     console.error(e);
  //   }
  // };

  return (client: Client) => {
    // @ts-expect-error
    client.addListener(event, (payload) => {
      payload.client = client;
      return callback(payload);
    });
  };
};

```

### File: `packages/bot-rw/src/events/interactionCreate.ts`
```ts
import { GatewayDispatchEvents } from "discord-api-types/v10";
import { interactionCreateHandler } from "../commands/handler";
import { createHandler } from "./handler";

export default createHandler(
  GatewayDispatchEvents.InteractionCreate,
  interactionCreateHandler,
);

```

### File: `packages/bot-rw/src/events/messageReactionAdd.ts`
```ts
import { GatewayDispatchEvents } from "discord-api-types/v10";
import { and, eq } from "drizzle-orm";
import { discordReactionRoles, makeSnowflake } from "store";
import { createHandler } from "./handler";

export interface DiscordReactionRoleData {
  roleId: string | null;
}

export default createHandler(
  GatewayDispatchEvents.MessageReactionAdd,
  async ({ data, client }) => {
    if (!data.guild_id || data.member?.user?.bot) return;

    // biome-ignore lint/style/noNonNullAssertion: One is required
    const reaction = (data.emoji.id ?? data.emoji.name)!;
    const key = `discord-reaction-role-${data.message_id}-${reaction}`;
    let rrData = await client.KV.get<DiscordReactionRoleData>(key, "json");
    if (!rrData) {
      const db = client.getDb();
      const stored = await db.query.discordReactionRoles.findFirst({
        where: and(
          eq(discordReactionRoles.messageId, makeSnowflake(data.message_id)),
          eq(discordReactionRoles.reaction, reaction),
        ),
      });
      if (!stored) {
        await client.KV.put(key, JSON.stringify({ roleId: null }), {
          expirationTtl: 86400 / 2,
        });
        return;
      }
      rrData = { roleId: String(stored.roleId) };
      await client.KV.put(key, JSON.stringify(rrData), {
        expirationTtl: 86400,
      });
    }
    if (!rrData.roleId) return;

    try {
      await client.api.guilds.addRoleToMember(
        data.guild_id,
        data.user_id,
        rrData.roleId,
        { reason: `Reaction role in channel ID ${data.channel_id}` },
      );
    } catch (e) {
      console.error(e);
    }
  },
);

```

### File: `packages/bot-rw/src/events/messageReactionRemove.ts`
```ts
import { GatewayDispatchEvents } from "discord-api-types/v10";
import { and, eq } from "drizzle-orm";
import { discordReactionRoles, makeSnowflake } from "store";
import { createHandler } from "./handler";
import type { DiscordReactionRoleData } from "./messageReactionAdd";

export default createHandler(
  GatewayDispatchEvents.MessageReactionRemove,
  async ({ data, client }) => {
    if (!data.guild_id) return;

    // biome-ignore lint/style/noNonNullAssertion: One is required
    const reaction = (data.emoji.id ?? data.emoji.name)!;
    const key = `discord-reaction-role-${data.message_id}-${reaction}`;
    let rrData = await client.KV.get<DiscordReactionRoleData>(key, "json");
    if (!rrData) {
      const db = client.getDb();
      const stored = await db.query.discordReactionRoles.findFirst({
        where: and(
          eq(discordReactionRoles.messageId, makeSnowflake(data.message_id)),
          eq(discordReactionRoles.reaction, reaction),
        ),
      });
      if (!stored) {
        await client.KV.put(key, JSON.stringify({ roleId: null }), {
          expirationTtl: 86400 / 2,
        });
        return;
      }
      rrData = { roleId: String(stored.roleId) };
      await client.KV.put(key, JSON.stringify(rrData), {
        expirationTtl: 86400,
      });
    }
    if (!rrData.roleId) return;

    try {
      await client.api.guilds.removeRoleFromMember(
        data.guild_id,
        data.user_id,
        rrData.roleId,
        { reason: `Reaction role in channel ID ${data.channel_id}` },
      );
    } catch (e) {
      console.error(e);
    }
  },
);

```

### File: `packages/bot-rw/src/events/webhooksUpdate.ts`
```ts
import {
  type APIWebhook,
  GatewayDispatchEvents,
  WebhookType,
} from "@discordjs/core";
import { and, eq, inArray, notInArray, sql } from "drizzle-orm";
import { autoRollbackTx, makeSnowflake, webhooks } from "store";
import { createHandler } from "./handler";

export default createHandler(
  GatewayDispatchEvents.WebhooksUpdate,
  async ({ data, client }) => {
    let channelWebhooks: APIWebhook[];
    try {
      channelWebhooks = await client.api.channels.getWebhooks(data.channel_id);
    } catch (_e) {
      // if (isDiscordError(_e)) {
      //   console.error(e.rawError);
      // }
      return;
    }
    const incoming = channelWebhooks.filter(
      (w) => w.type === WebhookType.Incoming,
    );

    const db = client.getDb();
    if (incoming.length === 0) {
      await db
        .delete(webhooks)
        .where(
          and(
            eq(webhooks.platform, "discord"),
            eq(webhooks.channelId, data.channel_id),
          ),
        );
    } else {
      await db.transaction(
        autoRollbackTx(async (tx) => {
          // We retrieve tokens first in case we have tokens from a different bot;
          // we don't want to lose that data in the upsert event.
          const residual = await tx.query.webhooks.findMany({
            where: and(
              eq(webhooks.platform, "discord"),
              inArray(
                webhooks.id,
                incoming.map((w) => w.id),
              ),
            ),
            columns: { id: true, token: true },
          });

          await tx
            .insert(webhooks)
            .values(
              incoming.map((webhook) => {
                const extant = residual.find((w) => w.id === webhook.id);
                return {
                  platform: "discord" as const,
                  id: webhook.id,
                  name: webhook.name ?? "",
                  avatar: webhook.avatar,
                  channelId: webhook.channel_id,
                  discordGuildId: makeSnowflake(data.guild_id),
                  token: webhook.token ?? extant?.token ?? undefined,
                  applicationId: webhook.application_id,
                } satisfies typeof webhooks.$inferInsert;
              }),
            )
            .onConflictDoUpdate({
              target: [webhooks.platform, webhooks.id],
              set: {
                name: sql`excluded.name`,
                avatar: sql`excluded.avatar`,
                channelId: sql`excluded."channelId"`,
                token: sql`excluded.token`,
                applicationId: sql`excluded."applicationId"`,
              },
            });

          // Delete stale records
          await tx.delete(webhooks).where(
            and(
              eq(webhooks.platform, "discord"),
              eq(webhooks.channelId, data.channel_id),
              notInArray(
                webhooks.id,
                incoming.map((w) => w.id),
              ),
            ),
          );
        }),
      );
    }
  },
);

```

