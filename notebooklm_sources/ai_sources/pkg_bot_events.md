# Repository Context Group: pkg_bot_events
# Source Repository: discohook/discohook

### File: `packages/bot/src/events/applicationAuthorized.ts`
```ts
import { ApplicationIntegrationType, Routes } from "discord-api-types/v10";
import { eq, sql } from "drizzle-orm";
import { discordGuilds, discordRoles, getDb, makeSnowflake } from "store";
import type { GatewayEventCallback } from "../events.js";
import type {
  APIWebhookEventBodyApplicationAuthorizedBase,
  APIWebhookEventBodyApplicationAuthorizedGuild,
} from "../types/webhook-events.js";
import { createREST } from "../util/rest.js";

export const applicationAuthorizedCallback: GatewayEventCallback = async (
  env,
  authorization: APIWebhookEventBodyApplicationAuthorizedBase,
) => {
  if (
    !authorization ||
    authorization.integration_type === undefined ||
    authorization.integration_type !== ApplicationIntegrationType.GuildInstall
  ) {
    return;
  }
  const { guild } =
    authorization as APIWebhookEventBodyApplicationAuthorizedGuild;

  const db = getDb(env.HYPERDRIVE);
  const moderated = await env.KV.get<{ state: "banned"; reason?: string }>(
    `moderation-guild-${guild.id}`,
    "json",
  );
  if (moderated?.state === "banned") {
    const rest = createREST(env);
    await rest.delete(Routes.userGuild(guild.id));
    return;
  }

  const now = sql`NOW()`;
  await db
    .insert(discordGuilds)
    .values({
      id: makeSnowflake(guild.id),
      name: guild.name,
      icon: guild.icon,
      ownerDiscordId: makeSnowflake(guild.owner_id),
      botJoinedAt: now,
    })
    .onConflictDoUpdate({
      target: discordGuilds.id,
      set: {
        name: guild.name,
        icon: guild.icon,
        ownerDiscordId: makeSnowflake(guild.owner_id),
        botJoinedAt: sql`CASE WHEN ${discordGuilds.botJoinedAt} IS NULL THEN ${now} ELSE excluded."botJoinedAt" END`,
      },
    });

  await db
    .delete(discordRoles)
    .where(eq(discordRoles.guildId, makeSnowflake(guild.id)));
  await db
    .insert(discordRoles)
    .values(
      guild.roles.map((role) => ({
        id: makeSnowflake(role.id),
        guildId: makeSnowflake(guild.id),
        name: role.name,
        position: role.position,
        color: role.color,
        hoist: role.hoist,
        icon: role.icon,
        unicodeEmoji: role.unicode_emoji,
        managed: role.managed,
        mentionable: role.mentionable,
        permissions: role.permissions,
      })),
    )
    .onConflictDoUpdate({
      target: discordRoles.id,
      set: {
        name: sql`excluded.name`,
        position: sql`excluded.position`,
        color: sql`excluded.color`,
        hoist: sql`excluded.hoist`,
        icon: sql`excluded.icon`,
        unicodeEmoji: sql`excluded."unicodeEmoji"`,
        managed: sql`excluded.managed`,
        mentionable: sql`excluded.mentionable`,
        permissions: sql`excluded.permissions`,
      },
    });
};

```

### File: `packages/bot/src/events/channelDelete.ts`
```ts
import type { APIGuildChannel, ChannelType } from "discord-api-types/v10";
import { and, eq } from "drizzle-orm";
import { getDb, webhooks } from "store";
import type { GatewayEventCallback } from "../events.js";

export const channelDeleteCallback: GatewayEventCallback = async (
  env,
  // Type checked by bot-ws before bulk sending
  channel: APIGuildChannel<
    | ChannelType.GuildAnnouncement
    | ChannelType.GuildForum
    | ChannelType.GuildMedia
    | ChannelType.GuildText
    | ChannelType.GuildVoice
  >,
) => {
  const db = getDb(env.HYPERDRIVE);
  await db
    .delete(webhooks)
    .where(
      and(eq(webhooks.platform, "discord"), eq(webhooks.channelId, channel.id)),
    );
};

```

### File: `packages/bot/src/events/entitlementCreate.ts`
```ts
import {
  type APIEntitlement,
  type APIUser,
  Routes,
} from "discord-api-types/v10";
import { eq } from "drizzle-orm";
import { discordUsers, getDb, makeSnowflake, users } from "store";
import type { GatewayEventCallback } from "../events.js";
import { createREST } from "../util/rest.js";

export const entitlementCreateCallback: GatewayEventCallback = async (
  env,
  entitlement: APIEntitlement,
) => {
  const db = getDb(env.HYPERDRIVE);
  if (entitlement.application_id !== env.DISCORD_APPLICATION_ID) return;
  if (!entitlement.user_id) return;

  const rest = createREST(env);
  const user = (await rest.get(Routes.user(entitlement.user_id))) as APIUser;

  if (env.GUILD_ID) {
    try {
      if (env.DONATOR_ROLE_ID) {
        await rest.put(
          Routes.guildMemberRole(env.GUILD_ID, user.id, env.DONATOR_ROLE_ID),
          { reason: `Entitlement created: ${entitlement.id}` },
        );
      }
      if (env.SUBSCRIBER_ROLE_ID) {
        await rest.put(
          Routes.guildMemberRole(env.GUILD_ID, user.id, env.SUBSCRIBER_ROLE_ID),
          { reason: `Entitlement created: ${entitlement.id}` },
        );
      }
    } catch {}
  }

  await db
    .insert(discordUsers)
    .values({
      id: makeSnowflake(user.id),
      name: user.username,
      globalName: user.global_name,
      avatar: user.avatar,
      discriminator: user.discriminator,
    })
    .onConflictDoUpdate({
      target: discordUsers.id,
      set: {
        name: user.username,
        globalName: user.global_name,
        avatar: user.avatar,
        discriminator: user.discriminator,
      },
    });

  const isLifetimeSKU =
    !!env.LIFETIME_SKU && entitlement.sku_id === env.LIFETIME_SKU;

  const dbUser = await db.query.users.findFirst({
    where: (users, { eq }) => eq(users.discordId, makeSnowflake(user.id)),
    columns: { lifetime: true, firstSubscribed: true },
  });
  await db
    .insert(users)
    .values({
      discordId: makeSnowflake(user.id),
      name: user.global_name ?? user.username,
      lifetime: isLifetimeSKU,
      subscribedSince: entitlement.starts_at
        ? new Date(entitlement.starts_at)
        : undefined,
      firstSubscribed: entitlement.starts_at
        ? new Date(entitlement.starts_at)
        : undefined,
    })
    .onConflictDoUpdate({
      target: users.discordId,
      set: {
        name: user.global_name ?? user.username,
        // Keep lifetime if it's already true
        lifetime: env.LIFETIME_SKU
          ? dbUser?.lifetime
            ? true
            : isLifetimeSKU
          : undefined,
        subscribedSince: entitlement.starts_at
          ? new Date(entitlement.starts_at)
          : undefined,
        // Only override `firstSubscribed` if it isn't already defined
        firstSubscribed:
          entitlement.starts_at && !dbUser?.firstSubscribed
            ? new Date(entitlement.starts_at)
            : undefined,
        subscriptionExpiresAt: null,
      },
    });
};

// https://discord.dev/monetization/implementing-app-subscriptions#working-with-entitlements
// This is sent when a subscription ends
export const entitlementUpdateCallback: GatewayEventCallback = async (
  env,
  entitlement: APIEntitlement,
) => {
  const db = getDb(env.HYPERDRIVE);
  if (entitlement.application_id !== env.DISCORD_APPLICATION_ID) return;
  if (!entitlement.user_id) return;
  // This shouldn't happen
  if (!entitlement.ends_at) return;

  const endsAt = new Date(entitlement.ends_at);
  const rest = createREST(env);

  if (env.GUILD_ID) {
    try {
      if (env.SUBSCRIBER_ROLE_ID) {
        await rest.delete(
          Routes.guildMemberRole(
            env.GUILD_ID,
            entitlement.user_id,
            env.SUBSCRIBER_ROLE_ID,
          ),
          { reason: `Subscription ended for SKU ${entitlement.sku_id}` },
        );
      }
    } catch {}
  }

  await db
    .update(users)
    .set({ subscriptionExpiresAt: endsAt })
    .where(eq(users.discordId, makeSnowflake(entitlement.user_id)));
};

```

### File: `packages/bot/src/events/entitlementDelete.ts`
```ts
import { type APIEntitlement, Routes } from "discord-api-types/v10";
import { eq } from "drizzle-orm";
import { getDb, makeSnowflake, users } from "store";
import type { GatewayEventCallback } from "../events.js";
import { createREST } from "../util/rest.js";

// Discord removed the entitlement. I think in any case this means the user is
// no longer subscribed (through discord, at least), so it's safe to carefully
// remove subscription information
export const entitlementDeleteCallback: GatewayEventCallback = async (
  env,
  entitlement: APIEntitlement,
) => {
  if (entitlement.application_id !== env.DISCORD_APPLICATION_ID) return;
  if (!entitlement.user_id) return;

  if (env.GUILD_ID && env.SUBSCRIBER_ROLE_ID) {
    const rest = createREST(env);
    try {
      await rest.delete(
        Routes.guildMemberRole(
          env.GUILD_ID,
          entitlement.user_id,
          env.SUBSCRIBER_ROLE_ID,
        ),
        { reason: `Entitlement deleted: ${entitlement.id}` },
      );
    } catch {}
  }

  const db = getDb(env.HYPERDRIVE);
  const isLifetimeSKU =
    !!env.LIFETIME_SKU && entitlement.sku_id === env.LIFETIME_SKU;
  await db
    .update(users)
    .set({
      lifetime: isLifetimeSKU ? false : undefined,
      subscribedSince: isLifetimeSKU ? undefined : null,
      subscriptionExpiresAt: isLifetimeSKU ? undefined : null,
    })
    .where(eq(users.discordId, makeSnowflake(entitlement.user_id)));
};

```

### File: `packages/bot/src/events/guildDelete.ts`
```ts
import type {
  APIUnavailableGuild,
  GatewayGuildDeleteDispatchData,
} from "discord-api-types/v10";
import { eq } from "drizzle-orm";
import { discordGuilds, getDb, makeSnowflake } from "store";
import type { GatewayEventCallback } from "../events.js";

export const guildDeleteCallback: GatewayEventCallback = async (
  env,
  guild: GatewayGuildDeleteDispatchData,
) => {
  // > If the unavailable field is not set, the user was removed from the guild.
  // https://discord.dev/topics/gateway-events#guild-delete
  // We only care about this event if the bot has been removed.
  if ("unavailable" in guild) return;

  const db = getDb(env.HYPERDRIVE);
  await db
    .delete(discordGuilds)
    .where(
      eq(discordGuilds.id, makeSnowflake((guild as APIUnavailableGuild).id)),
    );
};

```

### File: `packages/bot/src/events/guildMemberAdd.ts`
```ts
import type { REST } from "@discordjs/rest";
import {
  type APIUser,
  type APIWebhook,
  type GatewayGuildMemberAddDispatchData,
  Routes,
} from "discord-api-types/v10";
import { and, eq } from "drizzle-orm";
import {
  backups,
  type DBWithSchema,
  type DraftFlow,
  ensureTriggerFlow,
  FlowActionCheckFunctionType,
  FlowActionSetVariableType,
  FlowActionType,
  getchTriggerGuild,
  getDb,
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
import type { GatewayEventCallback } from "../events.js";
import { executeFlow, type FlowResult } from "../flows/flows.js";
import { createREST } from "../util/rest.js";

export const getWelcomerConfigurations = async (
  db: DBWithSchema,
  type: "add" | "remove",
  rest: REST,
  guild: TriggerKVGuild,
) => {
  let configs = await db.query.triggers.findMany({
    columns: {
      id: true,
      disabled: true,
      flow: true,
      flowId: true,
    },
    with: { updatedBy: { columns: { discordId: true } } },
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
        const user = (await rest.get(Routes.user(dUserId))) as APIUser;
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
          const webhook = (await rest.get(
            Routes.webhook(
              String(oldConfiguration[0].webhookId),
              String(oldConfiguration[0].webhookToken),
            ),
          )) as APIWebhook;
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

      const flow: DraftFlow = { actions: [] };
      if (backupId !== undefined) {
        if (oldConfiguration[0].ignoreBots) {
          flow.actions.push({
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
          });
        }
        if (oldConfiguration[0].webhookId && !webhookInvalid) {
          flow.actions.push(
            {
              type: FlowActionType.SendWebhookMessage,
              webhookId: String(oldConfiguration[0].webhookId),
              backupId: backupId.toString(),
            },
            {
              type: FlowActionType.SetVariable,
              varType: FlowActionSetVariableType.Adaptive,
              name: "channelId",
              value: "channel_id",
            },
          );
        } else {
          flow.actions.push(
            {
              type: FlowActionType.SetVariable,
              name: "channelId",
              value: String(oldConfiguration[0].channelId),
            },
            {
              type: FlowActionType.SendMessage,
              backupId: backupId.toString(),
            },
          );
        }
        if (oldConfiguration[0].deleteMessagesAfter) {
          flow.actions.push(
            {
              type: FlowActionType.SetVariable,
              varType: FlowActionSetVariableType.Adaptive,
              name: "messageId",
              value: "id",
            },
            {
              type: FlowActionType.Wait,
              seconds: oldConfiguration[0].deleteMessagesAfter,
            },
            { type: FlowActionType.DeleteMessage },
          );
        }
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
          flow,
        })
        .onConflictDoNothing()
        .returning({
          id: triggers.id,
          disabled: triggers.disabled,
        });
      configs = [
        {
          ...protoConfigs[0],
          flow,
          flowId: null,
          updatedBy: { discordId: BigInt(dUserId) },
        },
      ];
      await db.delete(oldTable).where(eq(oldTable.id, oldConfiguration[0].id));
    }
  } else {
    for (const trigger of configs) {
      await ensureTriggerFlow(trigger, db);
    }
  }

  return configs.map(({ flowId: _, ...c }) => ({
    ...c,
    flow: c.flow ?? { actions: [] },
  }));
};

export type Trigger = Awaited<
  ReturnType<typeof getWelcomerConfigurations>
>[number];

export const guildMemberAddCallback: GatewayEventCallback = async (
  env,
  payload: GatewayGuildMemberAddDispatchData,
  deferred = false,
) => {
  const rest = createREST(env);

  // Don't like this. We really should store all triggers per guild id,
  // but I did this to fit with the way getWelcomerConfiguration works
  const key = `cache:triggers-${TriggerEvent.MemberAdd}-${payload.guild_id}`;
  let triggers = await env.KV.get<Trigger[]>(key, "json");
  if (triggers && triggers.length === 0) {
    return;
  }

  const guild = await getchTriggerGuild(rest, env, payload.guild_id);
  const db = getDb(env.HYPERDRIVE);
  if (!triggers) {
    triggers = await getWelcomerConfigurations(db, "add", rest, guild);
    await env.KV.put(key, JSON.stringify(triggers), { expirationTtl: 1200 });
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
        liveVars: { member: payload, user: payload.user, guild },
        deferred,
        responsibleUserId: trigger.updatedBy
          ? String(trigger.updatedBy.discordId)
          : undefined,
        responsibilityReason: "most recently edited the Member Join trigger",
      }),
    );
  }
  return results;
};

```

### File: `packages/bot/src/events/guildMemberRemove.ts`
```ts
import {
  type GatewayGuildMemberRemoveDispatchData,
  RESTJSONErrorCodes,
} from "discord-api-types/v10";
import { and, eq } from "drizzle-orm";
import {
  discordMembers,
  getchTriggerGuild,
  getDb,
  makeSnowflake,
  TriggerEvent,
  type TriggerKVGuild,
} from "store";
import type { GatewayEventCallback } from "../events.js";
import { executeFlow, type FlowResult } from "../flows/flows.js";
import { isDiscordError } from "../util/error.js";
import { createREST } from "../util/rest.js";
import { getWelcomerConfigurations, type Trigger } from "./guildMemberAdd.js";

export const guildMemberRemoveCallback: GatewayEventCallback = async (
  env,
  payload: GatewayGuildMemberRemoveDispatchData,
  deferred = false,
) => {
  if (payload.user.id === env.DISCORD_APPLICATION_ID) return [];

  const rest = createREST(env);

  const key = `cache:triggers-${TriggerEvent.MemberRemove}-${payload.guild_id}`;
  let triggers = await env.KV.get<Trigger[]>(key, "json");
  if (triggers && triggers.length === 0) {
    return;
  }

  const db = getDb(env.HYPERDRIVE);
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
    guild = await getchTriggerGuild(rest, env, payload.guild_id);
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
    triggers = await getWelcomerConfigurations(db, "remove", rest, guild);
    await env.KV.put(key, JSON.stringify(triggers), { expirationTtl: 600 });
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
        responsibleUserId: trigger.updatedBy
          ? String(trigger.updatedBy.discordId)
          : undefined,
        responsibilityReason: "most recently edited the Member Remove trigger",
      }),
    );
  }
  return results;
};

```

### File: `packages/bot/src/events/messageReactionAdd.ts`
```ts
import {
  type GatewayMessageReactionAddDispatchData,
  Routes,
} from "discord-api-types/v10";
import { and, eq } from "drizzle-orm";
import { discordReactionRoles, getDb, makeSnowflake } from "store";
import type { GatewayEventCallback } from "../events.js";
import { createREST } from "../util/rest.js";

export interface DiscordReactionRoleData {
  roleId: string | null;
}

export const messageReactionAddCallback: GatewayEventCallback = async (
  env,
  event: GatewayMessageReactionAddDispatchData,
) => {
  if (!event.guild_id || event.member?.user?.bot) return;

  // biome-ignore lint/style/noNonNullAssertion: One is required
  const reaction = (event.emoji.id ?? event.emoji.name)!;
  const key = `discord-reaction-role-${event.message_id}-${reaction}`;
  let data = await env.KV.get<DiscordReactionRoleData>(key, "json");
  if (!data) {
    const db = getDb(env.HYPERDRIVE);
    const stored = await db.query.discordReactionRoles.findFirst({
      where: and(
        eq(discordReactionRoles.messageId, makeSnowflake(event.message_id)),
        eq(discordReactionRoles.reaction, reaction),
      ),
    });
    if (!stored) {
      await env.KV.put(key, JSON.stringify({ roleId: null }), {
        expirationTtl: 86400 / 2,
      });
      return;
    }
    data = { roleId: String(stored.roleId) };
    await env.KV.put(key, JSON.stringify(data), { expirationTtl: 86400 });
  }
  if (!data.roleId) return;

  const rest = createREST(env);
  try {
    await rest.put(
      Routes.guildMemberRole(event.guild_id, event.user_id, data.roleId),
      { reason: `Reaction role in channel ID ${event.channel_id}` },
    );
  } catch (e) {
    console.error(e);
  }
};

```

### File: `packages/bot/src/events/messageReactionRemove.ts`
```ts
import {
  type GatewayMessageReactionRemoveDispatchData,
  Routes,
} from "discord-api-types/v10";
import { and, eq } from "drizzle-orm";
import { discordReactionRoles, getDb, makeSnowflake } from "store";
import type { GatewayEventCallback } from "../events.js";
import { createREST } from "../util/rest.js";
import type { DiscordReactionRoleData } from "./messageReactionAdd.js";

export const messageReactionRemoveCallback: GatewayEventCallback = async (
  env,
  event: GatewayMessageReactionRemoveDispatchData,
) => {
  if (!event.guild_id) return;

  // biome-ignore lint/style/noNonNullAssertion: One is required
  const reaction = (event.emoji.id ?? event.emoji.name)!;
  const key = `discord-reaction-role-${event.message_id}-${reaction}`;
  let data = await env.KV.get<DiscordReactionRoleData>(key, "json");
  if (!data) {
    const db = getDb(env.HYPERDRIVE);
    const stored = await db.query.discordReactionRoles.findFirst({
      where: and(
        eq(discordReactionRoles.messageId, makeSnowflake(event.message_id)),
        eq(discordReactionRoles.reaction, reaction),
      ),
    });
    if (!stored) {
      await env.KV.put(key, JSON.stringify({ roleId: null }), {
        expirationTtl: 86400 / 2,
      });
      return;
    }
    data = { roleId: String(stored.roleId) };
    await env.KV.put(key, JSON.stringify(data), { expirationTtl: 86400 });
  }
  if (!data.roleId) return;

  const rest = createREST(env);
  try {
    await rest.delete(
      Routes.guildMemberRole(event.guild_id, event.user_id, data.roleId),
      { reason: `Reaction role in channel ID ${event.channel_id}` },
    );
  } catch (e) {
    console.error(e);
  }
};

```

### File: `packages/bot/src/events/webhooksUpdate.ts`
```ts
import {
  type APIWebhook,
  type GatewayWebhooksUpdateDispatchData,
  Routes,
  WebhookType,
} from "discord-api-types/v10";
import { and, eq, inArray, notInArray, sql } from "drizzle-orm";
import { autoRollbackTx, getDb, makeSnowflake, webhooks } from "store";
import type { GatewayEventCallback } from "../events.js";
import { createREST } from "../util/rest.js";

export const webhooksUpdateCallback: GatewayEventCallback = async (
  env,
  event: GatewayWebhooksUpdateDispatchData,
) => {
  const rest = createREST(env);
  let channelWebhooks: APIWebhook[];
  try {
    channelWebhooks = (await rest.get(
      Routes.channelWebhooks(event.channel_id),
    )) as APIWebhook[];
  } catch (_e) {
    // if (isDiscordError(_e)) {
    //   console.error(e.rawError);
    // }
    return;
  }
  const incoming = channelWebhooks.filter(
    (w) => w.type === WebhookType.Incoming,
  );

  const db = getDb(env.HYPERDRIVE);
  if (incoming.length === 0) {
    await db
      .delete(webhooks)
      .where(
        and(
          eq(webhooks.platform, "discord"),
          eq(webhooks.channelId, event.channel_id),
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
                discordGuildId: makeSnowflake(event.guild_id),
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
            eq(webhooks.channelId, event.channel_id),
            notInArray(
              webhooks.id,
              incoming.map((w) => w.id),
            ),
          ),
        );
      }),
    );
  }
};

```

