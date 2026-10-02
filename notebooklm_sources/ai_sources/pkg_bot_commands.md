# Repository Context Group: pkg_bot_commands
# Source Repository: discohook/discohook

### File: `packages/bot/src/commands/account.ts`
```ts
import { getDb, upsertDiscordUser } from "store";
import type { ChatInputAppCommandCallback } from "../commands.js";

const CODE_RE = /^\d{8}$/;

interface LinkCodeData {
  expires: number;
}

// I'm not sure about this since it opens the possibility for users to give
// login codes to people who aren't themselves. I think I'll leave it unused
// for now. Site part of this functionality doesn't exist yet.

export const accountLinkHandler: ChatInputAppCommandCallback = async (ctx) => {
  const code = ctx.getStringOption("code").value;
  if (!CODE_RE.test(code)) {
    return ctx.reply({ content: "Not a valid login code.", ephemeral: true });
  }

  const extant = await ctx.env.KV.get<LinkCodeData>(
    `link-code-${code}`,
    "json",
  );
  if (!extant || Date.now() > extant.expires) {
    return ctx.reply({
      content: "This code does not exist or it has expired.",
      ephemeral: true,
    });
  }

  return [
    ctx.defer({ ephemeral: true }),
    async () => {
      const db = getDb(ctx.env.HYPERDRIVE);
      const user = await upsertDiscordUser(db, ctx.user);

      extant.expires += 60_000;
      await ctx.env.KV.put(
        `link-code-${code}`,
        JSON.stringify({
          ...extant,
          user,
        }),
        { expiration: extant.expires / 1000 },
      );
    },
  ];
};

```

### File: `packages/bot/src/commands/admin.ts`
```ts
import dedent from "dedent-js";
import {
  type APIDMChannel,
  type APIGuild,
  type APIUser,
  type RESTPostAPIChannelMessageJSONBody,
  type RESTPostAPICurrentUserCreateDMChannelJSONBody,
  Routes,
} from "discord-api-types/v10";
import { eq } from "drizzle-orm";
import { getDb, upsertDiscordUser, users } from "store";
import type { ChatInputAppCommandCallback } from "../commands.js";
import type { InteractionContext } from "../interactions.js";

const canRunDevCommand = (ctx: InteractionContext) =>
  ctx.env.DEV_OWNER_ID !== undefined &&
  ctx.env.DEV_GUILD_ID !== undefined &&
  ctx.user.id === ctx.env.DEV_OWNER_ID &&
  ctx.interaction.guild_id === ctx.env.DEV_GUILD_ID;

export const leaveCommandHandler: ChatInputAppCommandCallback<true> = async (
  ctx,
) => {
  if (!canRunDevCommand(ctx)) {
    return ctx.reply({ content: "Not available", ephemeral: true });
  }

  const guildId = ctx.getStringOption("guild-id").value;
  const reason = ctx.getStringOption("reason").value;
  const sendMsg = ctx.getBooleanOption("send-reason-message").value;
  const ban = ctx.getBooleanOption("ban").value;

  if (ban) {
    await ctx.env.KV.put(
      `moderation-guild-${guildId}`,
      JSON.stringify({ state: "banned", reason }),
    );
  }

  if (sendMsg) {
    const guild = (await ctx.rest.get(Routes.guild(guildId))) as APIGuild;
    const dm = (await ctx.rest.post(Routes.userChannels(), {
      body: {
        recipient_id: guild.owner_id,
      } satisfies RESTPostAPICurrentUserCreateDMChannelJSONBody,
    })) as APIDMChannel;
    await ctx.rest.post(Routes.channelMessages(dm.id), {
      body: {
        content: dedent`
          Hello,

          ${[
            `Discohook Utils has just left your server **${guild.name}** (${guild.id}).`,
            "Message components will be unresponsive (except for link buttons),",
            "and you will not be able to send or edit messages using webhooks owned by Discohook.",
          ].join(" ")}

          The reason given is below:
          > ${reason.replace(/\n/g, "\n> ")}

          You may wish to review Discohook's [terms of service](${
            ctx.env.DISCOHOOK_ORIGIN
          }/legal).
          ${
            ban
              ? "\nIf you attempt to re-add the bot, it will leave automatically.\n"
              : ""
          }
          If you believe this was done in error, contact us on the [Discohook support server](${
            ctx.env.DISCOHOOK_ORIGIN
          }/discord).
        `.trim(),
      } satisfies RESTPostAPIChannelMessageJSONBody,
    });
  }

  await ctx.rest.delete(Routes.userGuild(guildId));
  return ctx.reply({ content: `Left server ${guildId}`, ephemeral: true });
};

const USD_REGEX = /^\$(\d+)$/;

const TIME_REGEX = /^(\d+)(d|w|m|y)$/i;

// $6 / 30 days = 20c per day
const USD_PER_DAY = 6 / 30;

export const grantDeluxeCommandHandler: ChatInputAppCommandCallback<
  true
> = async (ctx) => {
  if (!canRunDevCommand(ctx)) {
    return ctx.reply({ content: "Not available", ephemeral: true });
  }

  const userId = ctx.getStringOption("user-id").value;
  const duration = ctx.getStringOption("duration").value;

  let days: number;
  switch (true) {
    case USD_REGEX.test(duration): {
      // biome-ignore lint/style/noNonNullAssertion: above
      const match = USD_REGEX.exec(duration)!;
      const dollars = Number(match[1]);
      days = dollars / USD_PER_DAY;
      break;
    }
    case TIME_REGEX.test(duration): {
      // biome-ignore lint/style/noNonNullAssertion: above
      const match = TIME_REGEX.exec(duration)!;
      const amount = Number(match[1]);
      const unit = match[2].toLowerCase() as "d" | "w" | "m" | "y";
      switch (unit) {
        case "d":
          days = amount;
          break;
        case "w":
          days = amount * 7;
          break;
        case "m":
          days = amount * 31;
          break;
        case "y":
          days = amount * 366;
          break;
        default:
          return ctx.reply({
            content: `Could not resolve value of unit "${unit}"`,
            ephemeral: true,
          });
      }
      break;
    }
    default:
      return ctx.reply({
        content: "Invalid duration format",
        ephemeral: true,
      });
  }
  days = Math.ceil(days);

  const discordUser = (await ctx.rest.get(Routes.user(userId))) as APIUser;

  const db = getDb(ctx.env.HYPERDRIVE);
  const dbUser = await upsertDiscordUser(db, discordUser);

  const now = new Date();
  const expiresAt = new Date(
    // Stack renewals as much as possible
    (dbUser.subscriptionExpiresAt &&
    dbUser.subscriptionExpiresAt.getTime() > now.getTime()
      ? dbUser.subscriptionExpiresAt
      : now
    ).getTime() +
      days * 86_400_000,
  );

  // TODO: create entitlement and expire it after time allotted
  await db
    .update(users)
    .set({
      firstSubscribed: dbUser.firstSubscribed ?? now,
      subscribedSince: dbUser.subscribedSince ?? now,
      subscriptionExpiresAt: expiresAt,
    })
    .where(eq(users.id, dbUser.id));

  return ctx.reply({
    content: `Granted ${days} days of Deluxe membership to ${discordUser.username} (${discordUser.id})`,
    ephemeral: true,
  });
};

export const revokeDeluxeCommandHandler: ChatInputAppCommandCallback<
  true
> = async (ctx) => {
  if (!canRunDevCommand(ctx)) {
    return ctx.reply({ content: "Not available", ephemeral: true });
  }

  const userId = ctx.getStringOption("user-id").value;
  const discordUser = (await ctx.rest.get(Routes.user(userId))) as APIUser;

  const db = getDb(ctx.env.HYPERDRIVE);
  await db
    .update(users)
    .set({
      lifetime: false,
      subscribedSince: null,
      subscriptionExpiresAt: null,
    })
    .where(eq(users.discordId, BigInt(userId)));

  return ctx.reply({
    content: `Revoked Deluxe membership from ${discordUser.username} (${discordUser.id})`,
    ephemeral: true,
  });
};

```

### File: `packages/bot/src/commands/components/add.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  ContainerBuilder,
  escapeMarkdown,
  formatEmoji,
  type MessageActionRowComponentBuilder,
  messageLink,
  ModalBuilder,
  StringSelectMenuBuilder,
  StringSelectMenuOptionBuilder,
  TextDisplayBuilder,
} from "@discordjs/builders";
import dedent from "dedent-js";
import {
  type APIButtonComponent,
  type APIGuildInteraction,
  type APIInteraction,
  type APIMessage,
  type APIModalInteractionResponseCallbackData,
  type APIModalSubmitStringSelectComponent,
  type APISelectMenuComponent,
  type APIStringSelectComponent,
  ButtonStyle,
  ComponentType,
  Routes,
  TextInputStyle,
} from "discord-api-types/v10";
import { SignJWT } from "jose";
import {
  autoRollbackTx,
  discordMessageComponents,
  type DraftComponent,
  generateId,
  getchGuild,
  getDb,
  launchComponentKV,
  makeSnowflake,
  upsertDiscordUser,
  upsertGuild,
} from "store";
import type { InteractionInstantOrDeferredResponse } from "../../commands.js";
import type {
  ButtonCallback,
  InteractionResponseWithFollowup,
  MinimumKVComponentState,
  ModalCallback,
  SelectMenuCallback,
} from "../../components.js";
import type { InteractionContext } from "../../interactions.js";
import type { Env } from "../../types/env.js";
import { webhookAvatarUrl } from "../../util/cdn.js";
import {
  getComponentWidth,
  getRemainingComponentsCount,
  getRowWidth,
  isComponentsV2,
  onlyActionRows,
  storeComponents,
} from "../../util/components.js";
import { MAX_ACTION_ROW_WIDTH } from "../../util/constants.js";
import { isDiscordError } from "../../util/error.js";
import { isThreadMessage } from "../../util/messages.js";
import { color } from "../../util/meta.js";
import { BUTTON_URL_RE } from "../../util/regex.js";
import { getUserPremiumDetails } from "../../util/user.js";
import { resolveEmoji } from "../reactionRoles.js";
import { getWebhook } from "../webhooks/webhookInfo.js";
import { partialEmojiToComponentEmoji } from "./edit.js";
import { quickButtonConfigs } from "./quick.js";

export const buildStorableComponent = (
  component: DraftComponent,
  customId?: string,
): APIButtonComponent | APISelectMenuComponent | undefined => {
  switch (component.type) {
    case ComponentType.Button:
      return component.style === ButtonStyle.Premium
        ? component
        : ({
            type: component.type,
            custom_id:
              component.style === ButtonStyle.Link ? undefined : customId,
            url:
              component.style === ButtonStyle.Link ? component.url : undefined,
            style: component.style,
            label: component.label,
            emoji: component.emoji,
            disabled: component.disabled,
          } as APIButtonComponent);
    case ComponentType.StringSelect:
      return {
        type: component.type,
        custom_id: customId,
        placeholder: component.placeholder,
        disabled: component.disabled,
        min_values: component.minValues,
        max_values: component.maxValues,
        options: component.options,
      } as APIStringSelectComponent;
    case ComponentType.UserSelect:
    case ComponentType.RoleSelect:
    case ComponentType.MentionableSelect:
    case ComponentType.ChannelSelect:
      return {
        type: component.type,
        custom_id: customId,
        placeholder: component.placeholder,
        disabled: component.disabled,
        min_values: component.minValues,
        max_values: component.maxValues,
        default_values: component.defaultValues,
      } as APISelectMenuComponent;
    default:
      break;
  }
};

export interface ComponentFlow extends MinimumKVComponentState {
  step: number;
  stepTitle: string;
  totalSteps?: number;
  steps?: {
    label: string;
  }[];
  webhookToken: string;
  message: {
    id: string;
    channelId: string;
    isInThread?: boolean;
    guildId: string;
    webhookId: string;
    webhookName: string;
    webhookAvatar: string | null;
  };
  user: {
    id: string;
    premium: ReturnType<typeof getUserPremiumDetails>;
  };
  componentId?: string;
  component?: DraftComponent;
}

export const getComponentFlowContainer = (
  flow: ComponentFlow,
): ContainerBuilder => {
  const container = new ContainerBuilder().setAccentColor(color);
  const bodyText = new TextDisplayBuilder().setContent(
    [
      `### ${
        flow.stepTitle +
        (flow.totalSteps
          ? ` - Step ${flow.step}/${flow.totalSteps} (${Math.floor(
              (flow.step / flow.totalSteps) * 100,
            )}%)`
          : "")
      }`,
      flow.steps
        ? flow.steps.map((step, i) => `${i + 1}. ${step.label}`).join("\n")
        : "",
      "**Message**",
      messageLink(
        flow.message.channelId,
        flow.message.id,
        flow.message.guildId,
      ),
    ]
      .filter(Boolean)
      .join("\n"),
  );

  if (flow.step === 0) {
    container.addSectionComponents((s) =>
      s.addTextDisplayComponents(bodyText).setThumbnailAccessory((a) =>
        a
          .setURL(
            webhookAvatarUrl({
              id: flow.message.webhookId,
              avatar: flow.message.webhookAvatar,
            }),
          )
          .setDescription(
            flow.message.webhookName.slice(0, 1024) || "Webhook Avatar",
          ),
      ),
    );
  } else {
    // Unfortunately we have no alternative for an author w/ icon :(
    container.addTextDisplayComponents(bodyText);
  }

  return container;
};

const registerComponent = async (
  ctx: InteractionContext<APIInteraction>,
  state: ComponentFlow,
  componentId?: bigint,
): Promise<APIMessage> => {
  // biome-ignore lint/style/noNonNullAssertion: It's not null
  const data = state.component!;

  const id = componentId ?? BigInt(generateId());
  const customId =
    data.type === ComponentType.Button &&
    (data.style === ButtonStyle.Link || data.style === ButtonStyle.Premium)
      ? undefined
      : `p_${id}`;
  const built = buildStorableComponent(data, customId);
  if (!built) {
    throw new Error(`Failed to built the component (type ${data.type}).`);
  }
  const requiredWidth = getComponentWidth(built);

  let message: APIMessage | undefined;
  try {
    message = (await ctx.rest.get(
      Routes.webhookMessage(
        state.message.webhookId,
        state.webhookToken,
        state.message.id,
      ),
      {
        query: state.message.isInThread
          ? new URLSearchParams({ thread_id: state.message.channelId })
          : undefined,
      },
    )) as APIMessage;
  } catch (e) {
    if (isDiscordError(e)) {
      throw new Error(
        [
          `Failed to fetch the message (${state.message.id}).`,
          `Make sure the webhook (${state.message.webhookId})`,
          `exists and is in the same channel. (${e.code})`,
        ].join(" "),
      );
    }
    console.error(state.message.id, e);
    throw new Error(`Failed to fetch the message (${state.message.id}).`);
  }
  const isCV2 = isComponentsV2(message);

  const components = message.components ?? [
    { type: ComponentType.ActionRow, components: [] },
  ];
  let nextAvailableRow = onlyActionRows(components, true).find((c) => {
    return MAX_ACTION_ROW_WIDTH - getRowWidth(c) >= requiredWidth;
  });

  if (!nextAvailableRow && getRemainingComponentsCount(components, isCV2) > 0) {
    nextAvailableRow = { type: ComponentType.ActionRow, components: [] };
    components.push(nextAvailableRow);
  } else if (!nextAvailableRow) {
    throw new Error(
      `No available slots for this component (need at least ${requiredWidth}).`,
    );
  }
  nextAvailableRow.components.push(built);

  const db = getDb(ctx.env.HYPERDRIVE);
  return await db.transaction(
    autoRollbackTx(async (tx) => {
      await tx
        .insert(discordMessageComponents)
        .values({
          id,
          guildId: makeSnowflake(state.message.guildId),
          channelId: makeSnowflake(state.message.channelId),
          messageId: makeSnowflake(state.message.id),
          createdById: makeSnowflake(state.user.id),
          type: data.type,
          data,
        })
        .onConflictDoUpdate({
          target: discordMessageComponents.id,
          set: {
            data,
            draft: false,
            updatedById: makeSnowflake(state.user.id),
          },
        })
        .returning({
          id: discordMessageComponents.id,
        });

      const editedMsg = (await ctx.rest.patch(
        Routes.webhookMessage(
          state.message.webhookId,
          state.webhookToken,
          state.message.id,
        ),
        {
          body: { components },
          query: state.message.isInThread
            ? new URLSearchParams({ thread_id: state.message.channelId })
            : undefined,
        },
      )) as APIMessage;

      if (customId !== undefined) {
        await launchComponentKV(ctx.env, {
          componentId: id,
          data,
          createdById: ctx.user.id,
        });
      }
      return editedMsg;
    }),
  );
};

export const startComponentFlow = async (
  ctx: InteractionContext<APIGuildInteraction>,
  message: APIMessage,
  components?: ActionRowBuilder<MessageActionRowComponentBuilder>[],
): Promise<InteractionInstantOrDeferredResponse> => {
  const db = getDb(ctx.env.HYPERDRIVE);
  const user = await upsertDiscordUser(db, ctx.user);

  if (!message.webhook_id) {
    return ctx.reply({
      content: "This is not a webhook message.",
      ephemeral: true,
    });
  }
  if (
    !message.application_id ||
    message.application_id !== ctx.env.DISCORD_APPLICATION_ID
  ) {
    return ctx.reply({
      // content:
      //   "This message's webhook is not owned by Discohook Utils. You can create a bot-owned webhook with </webhook create:908884724087410732>. Would you like to automatically clone the message using a new webhook?",
      content: `This message's webhook is ${
        message.application_id
          ? `owned by <@${message.application_id}>, not Discohook Utils`
          : "not owned by Discohook Utils"
      }. You can create a bot-owned webhook with </webhook create:908884724087410732>, then re-send the message from Discohook (use </restore:979811266073878560> to load the message).`,
      ephemeral: true,
      // components: [
      //   new ActionRowBuilder<ButtonBuilder>()
      //     .addComponents(
      //       new ButtonBuilder()
      //         .setCustomId(
      //           `a_clone-webhook-message_${message.id}:${message.webhook_id}` satisfies AutoComponentCustomId,
      //         )
      //         .setLabel("Create webhook & re-send message"),
      //     ),
      // ],
    });
  }
  const webhook = await getWebhook(
    message.webhook_id,
    ctx.env,
    message.application_id,
  );
  const webhookToken = webhook.token;
  if (!webhookToken) {
    return ctx.reply({
      content: dedent`
        Webhook token (ID ${message.webhook_id}) was not available.
        It may be an incompatible type of webhook, or it may have been
        created by a different bot user.
      `,
      ephemeral: true,
    });
  }

  const componentFlow: ComponentFlow = {
    componentTimeout: 300,
    componentRoutingId: "add-component-flow",
    step: 0,
    stepTitle: "Message Components",
    webhookToken,
    message: {
      id: message.id,
      channelId: message.channel_id,
      isInThread: isThreadMessage(message),
      // biome-ignore lint/style/noNonNullAssertion: Guild-only command
      guildId: ctx.interaction.guild_id!,
      webhookId: message.webhook_id,
      webhookName: message.author.username,
      webhookAvatar: message.author.avatar,
    },
    user: {
      id: String(user.id),
      premium: getUserPremiumDetails(user),
    },
  };

  const container = getComponentFlowContainer(componentFlow);
  container.addActionRowComponents(
    new ActionRowBuilder<StringSelectMenuBuilder>().addComponents(
      await storeComponents(ctx.env.KV, [
        new StringSelectMenuBuilder({
          placeholder: "Add a component",
          options: [
            {
              label: "Button",
              description:
                "A simple button that runs a flow (add roles/send messages/etc)",
              value: "button",
              emoji: { name: "🟦" },
            },
            {
              label: "Link Button",
              description: "Direct a user to a webpage",
              value: "link-button",
              emoji: { name: "🌐" },
            },
            {
              label: "String Select",
              description: "Define a custom list of options (up to 25)",
              value: "string-select",
              emoji: { name: "🔽" },
            },
            {
              label: "User Select",
              description: "Show a list of all server members",
              value: "user-select",
              emoji: { name: "👤" },
            },
            {
              label: "Role Select",
              description: "Show a list of all server roles",
              value: "role-select",
              emoji: { name: "🏷️" },
            },
            {
              label: "User/Role Select",
              description: "Show a list of all members and roles",
              value: "mentionable-select",
              emoji: { name: "*️⃣" },
            },
            {
              label: "Channel Select",
              description: "Show a list of all server channels",
              value: "channel-select",
              emoji: { name: "#️⃣" },
            },
          ],
        }),
        {
          ...componentFlow,
          componentOnce: true,
        },
      ]),
    ),
  );

  return [
    ctx.reply({
      components: [container, ...(components ?? [])],
      ephemeral: true,
      componentsV2: true,
    }),
    async () => {
      const guild = await getchGuild(
        ctx.rest,
        ctx.env,
        ctx.interaction.guild_id,
      );
      await upsertGuild(db, guild);
    },
  ];
};

/**
 * An editor token is a special subset of our JWTs that is scoped for editing
 * one or more components, and does not authorize a request as a user.
 * This flow makes them fairly safe; Even if the token is hijacked, the
 * attacker cannot edit the message itself or send any new messages to the server.
 *
 * The drawback is that if the user wants to add a custom message action, they
 * will need to log in the long way through OAuth to access their backups.
 */
const createEditorToken = async (env: Env, data: KVComponentEditorState) => {
  const secretKey = Uint8Array.from(
    env.TOKEN_SECRET.split("").map((x) => x.charCodeAt(0)),
  );

  const now = new Date();
  // 2 hours
  const expiresAt = new Date(now.getTime() + 7_200_000);
  const id = generateId(now);
  const token = await new SignJWT({
    scp: "editor",
    // We expand the object instead of passing it directly just to make sure
    // there are no superfluous values
    sub: JSON.stringify({
      componentId: data.componentId,
      user: data.user,
      path: data.path,
    }),
  })
    .setProtectedHeader({ alg: "HS256" })
    .setJti(id)
    .setIssuedAt(now)
    .setIssuer(env.DISCOHOOK_ORIGIN)
    .setExpirationTime(expiresAt)
    .sign(secretKey);

  return { id, value: token, expiresAt };
};

interface KVComponentEditorState {
  componentId: string;
  user: {
    id: string;
    name: string;
    avatar: string | null;
  };
  path?: number[];
}

export const generateEditorTokenForComponent = async (
  env: Env,
  componentId: bigint,
  data: Omit<KVComponentEditorState, "componentId">,
) => {
  const editorToken = await createEditorToken(env, {
    ...data,
    componentId: String(componentId),
  });
  return { ...editorToken, componentId };
};

export type EditorTokenWithComponent = Awaited<
  ReturnType<typeof generateEditorTokenForComponent>
>;

export const getEditorTokenComponentUrl = (
  token: EditorTokenWithComponent,
  env: Env,
): string =>
  `${env.DISCOHOOK_ORIGIN}/edit/component/${
    token.componentId
  }?${new URLSearchParams({
    token: token.value,
  })}`;

export const continueComponentFlow: SelectMenuCallback = async (ctx) => {
  const value = ctx.interaction.data.values[0];

  const state = ctx.state as ComponentFlow;
  state.steps = [];
  state.steps.push({
    label: `Select component type (${value.replace("-", " ")})`,
  });
  state.step += 1;

  switch (value) {
    case "button": {
      state.stepTitle = "Choose a quick setup or finish on Discohook";
      state.steps.push({
        label:
          'Choose from the select menu. For more in-depth configuration, choose the final "Custom Flow" option.',
      });

      return ctx.updateMessage({
        components: [
          getComponentFlowContainer(state),
          new ActionRowBuilder<StringSelectMenuBuilder>().addComponents(
            await storeComponents(ctx.env.KV, [
              new StringSelectMenuBuilder()
                .setPlaceholder("Choose your path")
                .addOptions(
                  ...quickButtonConfigs.map((config) =>
                    new StringSelectMenuOptionBuilder()
                      .setValue(config.id)
                      .setLabel(config.name)
                      .setEmoji(config.emoji),
                  ),
                  new StringSelectMenuOptionBuilder()
                    .setValue("_")
                    .setLabel("Custom Flow")
                    .setEmoji({ name: "⛓️" }),
                ),
              {
                ...state,
                componentTimeout: 600,
                componentRoutingId: "add-component-quick-entry",
                componentOnce: true,
              },
            ]),
          ),
        ],
      });
    }
    case "link-button": {
      state.stepTitle = "Customize the button's link, label, & emoji";
      state.totalSteps = 3;
      state.component = {
        type: ComponentType.Button,
        style: ButtonStyle.Link,
        url: "",
      };

      const modal = new ModalBuilder()
        .setTitle("Custom button values")
        .addLabelComponents((s) =>
          s
            .setLabel("Label")
            .setDescription("The text displayed on this button.")
            .setTextInputComponent((b) =>
              b
                .setCustomId("label")
                .setStyle(TextInputStyle.Short)
                .setRequired(false)
                .setMaxLength(80),
            ),
        )
        .addLabelComponents((s) =>
          s
            .setLabel("Emoji")
            .setDescription("Like :smile: or a custom emoji in the server.")
            .setTextInputComponent((b) =>
              b
                .setCustomId("emoji")
                .setStyle(TextInputStyle.Short)
                .setRequired(false),
            ),
        )
        .addLabelComponents((s) =>
          s
            .setLabel("Button URL")
            .setDescription(
              "The full URL this button will lead to when it is clicked.",
            )
            .setTextInputComponent((b) =>
              b
                .setCustomId("url")
                .setStyle(TextInputStyle.Paragraph)
                .setRequired(true),
            ),
        )
        .addLabelComponents((l) =>
          l
            .setLabel("Disabled?")
            .setStringSelectMenuComponent((s) =>
              s
                .setCustomId("disabled")
                .addOptions(
                  new StringSelectMenuOptionBuilder()
                    .setLabel("True")
                    .setValue("true")
                    .setDescription("The button will not be clickable."),
                  new StringSelectMenuOptionBuilder()
                    .setLabel("False")
                    .setValue("false")
                    .setDescription("The button will be clickable (default)")
                    .setDefault(true),
                ),
            ),
        );

      await storeComponents(ctx.env.KV, [
        modal,
        {
          ...state,
          componentTimeout: 600,
          componentRoutingId: "add-component-flow-customize-modal",
          componentOnce: false,
        },
      ]);

      return [
        ctx.modal(modal),
        async () => {
          await ctx.followup.editOriginalMessage({
            components: [
              getComponentFlowContainer(state),
              new ActionRowBuilder<ButtonBuilder>().addComponents(
                await storeComponents(ctx.env.KV, [
                  new ButtonBuilder()
                    .setStyle(ButtonStyle.Primary)
                    .setLabel("Open modal"),
                  {
                    componentRoutingId:
                      "add-component-flow-customize-modal-resend",
                    componentTimeout: 600,
                    modal: modal.toJSON(),
                  },
                ]),
              ),
            ],
          });
        },
      ];
    }
    case "string-select":
    case "user-select":
    case "role-select":
    case "mentionable-select":
    case "channel-select": {
      const db = getDb(ctx.env.HYPERDRIVE);

      state.component =
        (state.component ?? value === "string-select")
          ? {
              type: ComponentType.StringSelect,
              options: [],
              flows: {},
            }
          : {
              type:
                value === "user-select"
                  ? ComponentType.UserSelect
                  : value === "role-select"
                    ? ComponentType.RoleSelect
                    : value === "mentionable-select"
                      ? ComponentType.MentionableSelect
                      : ComponentType.ChannelSelect,
              flow: { actions: [] },
            };

      const component = (
        await db
          .insert(discordMessageComponents)
          .values({
            guildId: makeSnowflake(state.message.guildId),
            channelId: makeSnowflake(state.message.channelId),
            messageId: makeSnowflake(state.message.id),
            type: state.component.type,
            data: state.component,
            createdById: makeSnowflake(state.user.id),
            updatedById: makeSnowflake(state.user.id),
            draft: true,
          })
          .returning({
            id: discordMessageComponents.id,
          })
      )[0];
      const doId = ctx.env.DRAFT_CLEANER.idFromName(String(component.id));
      const stub = ctx.env.DRAFT_CLEANER.get(doId);
      await stub.fetch(`http://do/?id=${component.id}`);

      const editorToken = await generateEditorTokenForComponent(
        ctx.env,
        component.id,
        {
          user: {
            id: ctx.user.id,
            name: ctx.user.username,
            avatar: ctx.user.avatar,
          },
        },
      );

      state.stepTitle = "Finish in the editor";
      // state.totalSteps = 3;
      state.steps.push(
        {
          label:
            'Click "Customize" to set details and flows **<--- you are here**',
        },
        {
          label: 'Finish editing and click "Add Select" in the tab',
        },
      );

      const container = getComponentFlowContainer(state);
      container.addTextDisplayComponents((c) =>
        c.setContent(`-# ${ctx.t("componentWillExpire")}`),
      );
      return ctx.updateMessage({
        components: [
          container,
          new ActionRowBuilder<ButtonBuilder>().addComponents(
            new ButtonBuilder()
              .setStyle(ButtonStyle.Link)
              .setLabel(ctx.t("customize"))
              .setURL(getEditorTokenComponentUrl(editorToken, ctx.env)),
          ),
        ],
      });
    }
    default:
      break;
  }

  return ctx.updateMessage({
    components: [getComponentFlowContainer(state)],
  });
};

export const reopenCustomizeModal: ButtonCallback = async (ctx) => {
  const state = ctx.state as MinimumKVComponentState & {
    modal: APIModalInteractionResponseCallbackData;
  };
  return ctx.modal(state.modal);
};

export const submitCustomizeModal: ModalCallback = async (ctx) => {
  const state = ctx.state as ComponentFlow;
  const id = state.componentId ?? generateId();

  if (state.component?.type === ComponentType.Button) {
    const label = ctx.getModalComponent("label").value;
    const emojiRaw = ctx.getModalComponent("emoji").value;

    if (!label && !emojiRaw) {
      return ctx.reply({
        content: "Must provide either a label or emoji.",
        ephemeral: true,
      });
    }

    if (state.component.style !== ButtonStyle.Premium) {
      state.component.label = label;
      if (emojiRaw) {
        if (emojiRaw.includes(" ")) {
          return ctx.reply({
            content: "Invalid emoji: Contains invalid characters.",
            ephemeral: true,
          });
        }

        const emoji = await resolveEmoji(
          ctx.rest,
          emojiRaw,
          undefined,
          state.message.guildId,
          ctx.env,
        );
        if (!emoji) {
          return ctx.reply({
            content:
              "Could not find an emoji that matches the input. For a custom emoji, try using the numeric ID, and make sure Discohook has access to it.",
            ephemeral: true,
          });
        }
        state.component.emoji = partialEmojiToComponentEmoji(emoji);
      }
      state.step += 1;
      state.steps?.push({
        label: `Set label (${
          label ? escapeMarkdown(label) : "none"
        }) and emoji (${
          state.component.emoji?.id
            ? formatEmoji(
                state.component.emoji.id,
                state.component.emoji.animated,
              )
            : (state.component.emoji?.name ?? "none")
        })`,
      });
    }

    const disabledRaw =
      ctx.getModalComponent<APIModalSubmitStringSelectComponent>("disabled")
        ?.values[0];
    if (disabledRaw) {
      state.component.disabled = disabledRaw === "true";
    }

    if (state.component.style === ButtonStyle.Link) {
      let url: URL;
      try {
        url = new URL(ctx.getModalComponent("url").value);
      } catch {
        return ctx.reply({
          content: "Invalid URL.",
          ephemeral: true,
        });
      }
      if (!BUTTON_URL_RE.test(url.href)) {
        return ctx.reply({
          content:
            "Invalid URL. Must be a `http://`, `https://`, or `discord://` address.",
          ephemeral: true,
        });
      }

      state.component.url = url.href;
      state.step += 1;
      state.steps?.push({ label: "Set URL" });
    }

    return [
      ctx.defer(),
      async () => {
        try {
          await registerComponent(ctx, state, BigInt(id));
        } catch (e) {
          console.error(e);
          await ctx.followup.send({ content: String(e), ephemeral: true });
          return;
        }

        state.stepTitle = "Finished!";
        state.step = state.steps?.length ?? 0;
        state.totalSteps = state.steps?.length;
        await ctx.followup.editOriginalMessage({
          components: [getComponentFlowContainer(state)],
        });
      },
    ] as InteractionResponseWithFollowup;
  }

  return ctx.reply({
    content: "This shouldn't happen",
    ephemeral: true,
  });
};

```

### File: `packages/bot/src/commands/components/delete.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  ContainerBuilder,
  messageLink,
  TextDisplayBuilder,
} from "@discordjs/builders";
import {
  type APIComponentInContainer,
  type APIComponentInMessageActionRow,
  type APIContainerComponent,
  type APIEmoji,
  type APIInteraction,
  type APIMessage,
  type APIMessageTopLevelComponent,
  type APISectionComponent,
  ButtonStyle,
  ComponentType,
  type RESTPatchAPIWebhookWithTokenMessageJSONBody,
  Routes,
} from "discord-api-types/v10";
import { eq } from "drizzle-orm";
import {
  autoRollbackTx,
  destroyComponentKV,
  discordMessageComponents,
  getDb,
} from "store";
import type { ChatInputAppCommandCallback } from "../../commands.js";
import type {
  AutoComponentCustomId,
  ButtonCallback,
  SelectMenuCallback,
} from "../../components.js";
import type { InteractionContext } from "../../interactions.js";
import { webhookAvatarUrl } from "../../util/cdn.js";
import {
  getComponentId,
  getRemainingComponentsCount,
  isComponentsV2,
  isStorableComponent,
  parseAutoComponentId,
  storeComponents,
  textDisplay,
} from "../../util/components.js";
import { getWebhookThreadQuery } from "../../util/messages.js";
import { getComponentsAsV2Menu } from "./edit.js";
import { getWebhookMessage, resolveMessageLink } from "./entry.js";

export const deleteComponentChatEntry: ChatInputAppCommandCallback<
  true
> = async (ctx) => {
  const message = await resolveMessageLink(
    ctx.rest,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    return ctx.reply({
      content: message,
      ephemeral: true,
    });
  }

  return await pickWebhookMessageComponentToDelete(ctx, message);
};

const pickWebhookMessageComponentToDelete = async (
  ctx: InteractionContext,
  message: APIMessage,
) => {
  const guildId = ctx.interaction.guild_id;
  if (!guildId) {
    return ctx.reply("Guild only");
  }

  const emojis = (await ctx.rest.get(
    Routes.guildEmojis(guildId),
  )) as APIEmoji[];

  const threadId = message.position === undefined ? "" : message.channel_id;
  const menu = getComponentsAsV2Menu(message.components ?? [], emojis, {
    getSelectCustomId: (index) =>
      `a_delete-component-pick_${message.webhook_id}:${message.id}:${threadId}:${index}` satisfies AutoComponentCustomId,
  });
  if (menu.length === 0) {
    return ctx.reply({
      components: [
        textDisplay("That message has no components that can be picked from."),
      ],
      ephemeral: true,
      componentsV2: true,
    });
  }

  const menuContainer = new ContainerBuilder()
    .setAccentColor(0xed4245)
    .addSectionComponents((s) =>
      s
        .addTextDisplayComponents((td) =>
          td.setContent(
            [
              "### Delete Component",
              "**Message**",
              messageLink(message.channel_id, message.id, guildId),
            ].join("\n"),
          ),
        )
        .setThumbnailAccessory((t) =>
          t
            .setURL(
              webhookAvatarUrl({
                id: message.author.id,
                avatar: message.author.avatar,
              }),
            )
            .setDescription(message.author.username),
        ),
    )
    .toJSON();
  // Due to the reduction taking place to form a menu, at least one of these
  // should almost always be displayed
  const free = getRemainingComponentsCount(menu, true);
  if (free >= 3) {
    menu.splice(0, 0, menuContainer);
  } else if (free >= 2) {
    menu.splice(0, 0, menuContainer.components[0]);
  } else if (free >= 1) {
    menu.splice(
      0,
      0,
      (menuContainer.components[0] as APISectionComponent).components[0],
    );
  }

  return ctx.reply({ components: menu, ephemeral: true, componentsV2: true });
};

export const deleteComponentButtonEntry: ButtonCallback = async (ctx) => {
  const guildId = ctx.interaction.guild_id;
  if (!guildId) {
    return ctx.reply("Guild-only");
  }

  const {
    webhookId,
    messageId,
    threadId: threadId_,
  } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "webhookId",
    "messageId",
    "threadId",
  );
  const threadId = threadId_ || undefined;
  const { message } = await getWebhookMessage(
    ctx.env,
    webhookId,
    messageId,
    threadId,
    ctx.rest,
  );

  const response = await pickWebhookMessageComponentToDelete(ctx, message);
  return ctx.updateMessage(response.data);
};

export const extractComponentByPath = (
  message: APIMessage,
  path: number[],
  options?: {
    operation: "remove" | "replace";
    replacement?:
      | APIComponentInMessageActionRow
      | (() => APIComponentInMessageActionRow);
  },
): APIComponentInMessageActionRow | null => {
  let parent: APIContainerComponent | undefined;
  let siblings: (
    | APIMessageTopLevelComponent
    | APIComponentInMessageActionRow
    | APIComponentInContainer
  )[] = message.components ?? [];
  let indexIndex = -1; // where we are in the path; the index of indexes
  for (const index of path) {
    indexIndex += 1;
    const atIndex = siblings[index];
    if (!atIndex) break;

    if (
      atIndex.type === ComponentType.Section &&
      // Sections cannot be navigated into further so we have to get it
      // in the second-to-last path position (the last value for section
      // accessories is always 0)
      indexIndex === path.length - 2
    ) {
      if (atIndex.accessory.type !== ComponentType.Button) return null;
      if (options?.operation === "remove") {
        siblings.splice(
          index,
          1,
          new TextDisplayBuilder({ id: atIndex.id })
            .setContent(
              atIndex.components
                .map((td) => td.content)
                .join("\n")
                .slice(0, 4000),
            )
            .toJSON(),
        );
      } else if (options?.operation === "replace" && options.replacement) {
        const replacement =
          typeof options.replacement === "function"
            ? options.replacement()
            : options.replacement;
        if (replacement.type !== atIndex.accessory.type) {
          throw Error(
            `Conflicting type for accessory component replacement (${atIndex.accessory.type} to ${replacement.type})`,
          );
        }
        atIndex.accessory = replacement;
      }
      return atIndex.accessory;
    }
    if (atIndex.type === ComponentType.Container) {
      siblings = atIndex.components;
      parent = atIndex;
      continue;
    }
    if (atIndex.type === ComponentType.ActionRow) {
      siblings = atIndex.components;
      continue;
    }
    if (isStorableComponent(atIndex)) {
      if (options?.operation === "remove") {
        siblings.splice(index, 1);
        if (siblings.length === 0) {
          // Remove the empty action row, which should be the second-to-last path index
          ((parent ?? message).components ?? []).splice(path.slice(-2)[0], 1);
        }
      } else if (options?.operation === "replace" && options.replacement) {
        const replacement =
          typeof options.replacement === "function"
            ? options.replacement()
            : options.replacement;
        if (replacement.type !== atIndex.type) {
          throw Error(
            `Conflicting type for component replacement (${atIndex.type} to ${replacement.type})`,
          );
        }
        siblings.splice(index, 1, replacement);
      }
      return atIndex;
    }
  }
  return null;
};

const componentsOrEmptyBody = (
  message: Pick<APIMessage, "components" | "flags">,
): RESTPatchAPIWebhookWithTokenMessageJSONBody => {
  return message.components?.length !== 0
    ? { components: message.components }
    : isComponentsV2(message)
      ? {
          components: [textDisplay("Empty message").toJSON()],
        }
      : {
          content: "Empty message",
        };
};

export const deleteComponentFlowPickCallback: SelectMenuCallback = async (
  ctx,
) => {
  const {
    webhookId,
    messageId,
    threadId: threadId_,
  } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "webhookId",
    "messageId",
    "threadId",
  );
  const threadId = threadId_ || undefined;

  const db = getDb(ctx.env.HYPERDRIVE);
  const [scope, key] = ctx.interaction.data.values[0].split(":");
  switch (scope as "id" | "link" | "unknown") {
    case "id": {
      const id = BigInt(key);
      const path = ctx.interaction.data.values[0]
        .split(":")[2]
        .split(".")
        .map(Number);

      const component = await db.query.discordMessageComponents.findFirst({
        where: (table, { eq }) => eq(table.id, id),
        columns: {
          id: true,
          guildId: true,
          messageId: true,
        },
      });
      if (
        component?.guildId &&
        component.messageId &&
        (component.guildId?.toString() !== ctx.interaction.guild_id ||
          component.messageId?.toString() !== messageId)
      ) {
        return ctx.updateMessage({
          components: [textDisplay("Unknown component")],
        });
      }
      if (!component) {
        const { webhook, message } = await getWebhookMessage(
          ctx.env,
          webhookId,
          messageId,
          threadId,
          ctx.rest,
        );
        const removed = extractComponentByPath(message, path, {
          operation: "remove",
        });
        if (removed === null) {
          return ctx.updateMessage({
            components: [
              textDisplay("Unable to locate the component in the message."),
            ],
          });
        }

        await ctx.rest.patch(
          Routes.webhookMessage(webhook.id, webhook.token, message.id),
          {
            body: componentsOrEmptyBody(message),
            auth: false,
            query: threadId
              ? new URLSearchParams({ thread_id: threadId })
              : undefined,
          },
        );
        return ctx.updateMessage({
          components: [
            textDisplay(
              "The component was already missing from the database, so it has been removed from the message.",
            ),
          ],
        });
      }

      return ctx.updateMessage({
        components: [
          textDisplay(
            "Are you sure you want to delete this component? This cannot be undone.",
          ),
          new ActionRowBuilder<ButtonBuilder>().addComponents(
            ...(await storeComponents(ctx.env.KV, [
              new ButtonBuilder()
                .setStyle(ButtonStyle.Danger)
                .setLabel("Delete"),
              {
                componentRoutingId: "delete-component-confirm",
                componentTimeout: 600,
                componentOnce: true,
                webhookId,
                messageId,
                threadId,
                componentId: component.id,
                path,
              },
            ])),
            new ButtonBuilder()
              .setCustomId(
                "a_delete-component-cancel_" satisfies AutoComponentCustomId,
              )
              .setStyle(ButtonStyle.Secondary)
              .setLabel("Cancel"),
          ),
        ],
      });
    }
    case "link": {
      const path = key.split(".").map(Number);
      const { webhook, message } = await getWebhookMessage(
        ctx.env,
        webhookId,
        messageId,
        threadId,
        ctx.rest,
      );
      const removed = extractComponentByPath(message, path, {
        operation: "remove",
      });
      if (removed === null) {
        return ctx.updateMessage({
          components: [
            textDisplay(
              `The button could not be located in the message (${key}).`,
            ),
          ],
        });
      }

      const dbComponents = await db.query.discordMessageComponents.findMany({
        where: (table, { eq, and }) =>
          and(
            eq(table.messageId, BigInt(messageId)),
            eq(table.type, ComponentType.Button),
          ),
        columns: {
          id: true,
          data: true,
        },
      });
      const matchId = getComponentId(removed, dbComponents);
      if (matchId === undefined) {
        await ctx.rest.patch(
          Routes.webhookMessage(webhook.id, webhook.token, message.id),
          {
            body: componentsOrEmptyBody(message),
            auth: false,
            query: threadId
              ? new URLSearchParams({ thread_id: threadId })
              : undefined,
          },
        );
        return ctx.updateMessage({
          components: [
            textDisplay(
              "The button was already missing from the database, so it has been removed from the message.",
            ),
          ],
        });
      }

      return ctx.updateMessage({
        components: [
          textDisplay(
            "Are you sure you want to delete this component? This cannot be undone.",
          ),
          new ActionRowBuilder<ButtonBuilder>().addComponents(
            ...(await storeComponents(ctx.env.KV, [
              new ButtonBuilder()
                .setStyle(ButtonStyle.Danger)
                .setLabel("Delete"),
              {
                componentRoutingId: "delete-component-confirm",
                componentTimeout: 600,
                componentOnce: true,
                webhookId,
                messageId,
                threadId,
                componentId: matchId,
                path,
              },
            ])),
            new ButtonBuilder()
              .setCustomId(
                "a_delete-component-cancel_" satisfies AutoComponentCustomId,
              )
              .setStyle(ButtonStyle.Secondary)
              .setLabel("Cancel"),
          ),
        ],
      });
    }
    default:
      return ctx.reply({
        components: [
          textDisplay(
            "Cannot resolve that component from the database. Try editing another component to remove it.",
          ),
        ],
        ephemeral: true,
        componentsV2: true,
      });
  }
};

const registerComponentDelete = async (
  ctx: InteractionContext<APIInteraction>,
  id: bigint,
  // type: ComponentType,
  webhook: { id: string; token: string; guild_id?: string },
  message: APIMessage,
  path: number[],
  shouldKeepRecord?: boolean,
) => {
  const db = getDb(ctx.env.HYPERDRIVE);

  const removed = extractComponentByPath(message, path, {
    operation: "remove",
  });
  if (removed === null) {
    throw new Error(
      `Couldn't find the row that this component is on. Try editing via the site instead (choose "Everything")`,
    );
  }

  const editedMsg = await db.transaction(
    autoRollbackTx(async (tx) => {
      if (!shouldKeepRecord) {
        await tx
          .delete(discordMessageComponents)
          .where(eq(discordMessageComponents.id, id));
      }

      // An error thrown here triggers a rollback
      return (await ctx.rest.patch(
        Routes.webhookMessage(webhook.id, webhook.token, message.id),
        {
          body: componentsOrEmptyBody(message),
          query: getWebhookThreadQuery(message),
        },
      )) as APIMessage;
    }),
  );

  if (!shouldKeepRecord) {
    await destroyComponentKV(ctx.env, id);
  }

  return editedMsg;
};

export const deleteComponentConfirm: ButtonCallback = async (ctx) => {
  const { webhookId, messageId, threadId, componentId, path } = ctx.state as {
    webhookId: string;
    messageId: string;
    threadId?: string;
    componentId: string;
    path: number[];
  };

  const { webhook, message } = await getWebhookMessage(
    ctx.env,
    webhookId,
    messageId,
    threadId,
    ctx.rest,
  );

  const db = getDb(ctx.env.HYPERDRIVE);
  const component = await db.query.discordMessageComponents.findFirst({
    where: (table, { eq }) => eq(table.id, BigInt(componentId)),
    columns: {
      id: true,
      type: true,
      guildId: true,
      messageId: true,
    },
  });
  // Allow removal from the message, but not record deletion, if the
  // component's messageId/guildId hasn't been stored for whatever
  // reason
  const shouldKeepRecord = !component?.guildId || !component?.messageId;
  if (
    component &&
    ((component.guildId &&
      component.guildId.toString() !== ctx.interaction.guild_id) ||
      (component.messageId && component.messageId.toString() !== messageId))
  ) {
    return ctx.updateMessage({
      components: [
        textDisplay("That component does not belong to this server."),
      ],
    });
  }

  if (!component) {
    const removed = extractComponentByPath(message, path, {
      operation: "remove",
    });
    if (removed === null) {
      return ctx.updateMessage({
        components: [
          textDisplay("The component could not be located in the message."),
        ],
      });
    }
    await ctx.rest.patch(
      Routes.webhookMessage(webhook.id, webhook.token, message.id),
      {
        body: componentsOrEmptyBody(message),
        query: getWebhookThreadQuery(message),
      },
    );
  } else {
    await registerComponentDelete(
      ctx,
      component.id,
      // component.type,
      webhook,
      message,
      path,
      shouldKeepRecord,
    );
  }
  return ctx.updateMessage({
    components: [
      textDisplay(
        `Component deleted successfully: ${messageLink(
          message.channel_id,
          message.id,
          // biome-ignore lint/style/noNonNullAssertion: we are in a guild
          (webhook.guild_id ?? ctx.interaction.guild_id)!,
        )}`,
      ),
    ],
  });
};

export const deleteComponentCancel: ButtonCallback = async (ctx) => {
  return ctx.updateMessage({
    components: [textDisplay("The component is safe and sound.")],
  });
};

```

### File: `packages/bot/src/commands/components/edit.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  ContainerBuilder,
  LabelBuilder,
  messageLink,
  ModalBuilder,
  SelectMenuBuilder,
  SelectMenuOptionBuilder,
  StringSelectMenuBuilder,
  StringSelectMenuOptionBuilder,
  TextInputBuilder,
} from "@discordjs/builders";
import { isLinkButton } from "discord-api-types/utils";
import {
  type APIComponentInMessageActionRow,
  type APIEmoji,
  type APIInteraction,
  type APIMessage,
  type APIMessageComponentEmoji,
  type APIMessageTopLevelComponent,
  type APIModalSubmitStringSelectComponent,
  type APIPartialEmoji,
  type APISectionComponent,
  type APISelectMenuOption,
  ButtonStyle,
  ComponentType,
  Routes,
  TextInputStyle,
} from "discord-api-types/v10";
import { sql } from "drizzle-orm";
import {
  autoRollbackTx,
  discordMessageComponents,
  type DraftComponent,
  getDb,
  launchComponentKV,
  makeSnowflake,
  type StorableButtonWithUrl,
  upsertDiscordUser,
  webhooks,
} from "store";
import type { ChatInputAppCommandCallback } from "../../commands.js";
import type {
  AutoComponentCustomId,
  AutoModalCustomId,
  ButtonCallback,
  ModalCallback,
  SelectMenuCallback,
} from "../../components.js";
import type {
  InteractionContext,
  MessageConstructorData,
} from "../../interactions.js";
import { webhookAvatarUrl } from "../../util/cdn.js";
import {
  chunkArray,
  getComponentId,
  getRemainingComponentsCount,
  isActionRow,
  parseAutoComponentId,
  textDisplay,
} from "../../util/components.js";
import { MAX_SELECT_OPTIONS } from "../../util/constants.js";
import { getWebhookThreadQuery } from "../../util/messages.js";
import { color } from "../../util/meta.js";
import { resolveEmoji } from "../reactionRoles.js";
import { getWebhook } from "../webhooks/webhookInfo.js";
import {
  buildStorableComponent,
  generateEditorTokenForComponent,
  getEditorTokenComponentUrl,
} from "./add.js";
import { extractComponentByPath } from "./delete.js";
import { getWebhookMessage, resolveMessageLink } from "./entry.js";

export const editComponentChatEntry: ChatInputAppCommandCallback<true> = async (
  ctx,
) => {
  const message = await resolveMessageLink(
    ctx.rest,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    return ctx.reply({
      components: [textDisplay(message)],
      ephemeral: true,
      componentsV2: true,
    });
  }
  if (
    !message.webhook_id ||
    !message.application_id ||
    !ctx.env.APPLICATIONS[message.application_id]
  ) {
    return ctx.reply({
      components: [
        textDisplay(
          !message.webhook_id
            ? "This is not a webhook message."
            : !message.application_id
              ? `This message's webhook is owned by a user, so it cannot have components.`
              : `This message's webhook is owned by <@${message.application_id}>, so I cannot edit it.`,
        ),
      ],
      ephemeral: true,
      componentsV2: true,
    });
  }

  const webhook = await getWebhook(
    message.webhook_id,
    ctx.env,
    message.application_id,
  );

  const response = await pickWebhookMessageComponentToEdit(ctx, message);
  return [
    response,
    async () => {
      const db = getDb(ctx.env.HYPERDRIVE);
      await db
        .insert(webhooks)
        .values({
          platform: "discord",
          id: webhook.id,
          token: webhook.token,
          applicationId: webhook.application_id,
          name: webhook.name ?? "Webhook",
          avatar: webhook.avatar,
          channelId: webhook.channel_id,
          discordGuildId: webhook.guild_id
            ? BigInt(webhook.guild_id)
            : undefined,
        })
        .onConflictDoUpdate({
          target: [webhooks.platform, webhooks.id],
          set: {
            token: sql`excluded.token`,
            applicationId: sql`excluded."applicationId"`,
            name: sql`excluded.name`,
            avatar: sql`excluded.avatar`,
            channelId: sql`excluded."channelId"`,
            discordGuildId: sql`excluded."discordGuildId"`,
          },
        });
    },
  ];
};

export const editComponentButtonEntry: ButtonCallback = async (ctx) => {
  const guildId = ctx.interaction.guild_id;
  if (!guildId) {
    return ctx.reply("Guild-only");
  }

  const { webhookId, messageId, threadId } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "webhookId",
    "messageId",
    "threadId",
  );
  const { message } = await getWebhookMessage(
    ctx.env,
    webhookId,
    messageId,
    threadId,
    ctx.rest,
  );

  const response = await pickWebhookMessageComponentToEdit(ctx, message);
  return ctx.updateMessage(response.data);
};

export function ensureValidEmoji<
  T extends APIMessageComponentEmoji | APIPartialEmoji,
>(emoji: T | undefined, emojis: APIEmoji[], fallback: T): T;
export function ensureValidEmoji<
  T extends APIMessageComponentEmoji | APIPartialEmoji,
>(
  emoji: T | undefined,
  emojis: APIEmoji[],
  fallback?: T | undefined,
): T | undefined;
export function ensureValidEmoji<
  T extends APIMessageComponentEmoji | APIPartialEmoji,
>(emoji: T | undefined, emojis: APIEmoji[], fallback?: T): T | undefined {
  return emoji?.id
    ? emojis.find((e) => e.id === emoji?.id)
      ? emoji
      : fallback
    : emoji?.name
      ? emoji
      : fallback;
}

/** Don't use this for all message components unless it's CV1 */
const getComponentsAsOptions = (
  components: APIMessageTopLevelComponent[],
  emojis: APIEmoji[],
  dbComponents?: { id: bigint; data: DraftComponent }[],
  /**
   * If we're processing data individually (not as part of the whole message),
   * we can elect to modify the paths with otherwise unknown parent data.
   * This ensures components aren't given incorrect top-level paths.
   */
  arrayConfig?: {
    padStart?: number;
    topLevelIndex?: number;
  },
): APISelectMenuOption[] => {
  const childToOption = (
    child: APIComponentInMessageActionRow,
    /** Array of indexes */
    parents: number[],
  ): APISelectMenuOption | undefined => {
    const id = getComponentId(child, dbComponents);

    // try to naturally describe where the component is
    let location = "";
    let column = -1;
    if (parents.length === 3) {
      location = `container ${parents[0] + 1}, row ${parents[1] + 1}`;
      column = parents[2] + 1;
    } else if (parents.length === 2) {
      location = `stack row ${parents[0] + 1}`;
      column = parents[1] + 1;
    }
    const path = parents.join(".");
    const value = id
      ? `id:${id}:${path}`
      : child.type === ComponentType.Button && isLinkButton(child)
        ? `link:${path}`
        : `unknown:${path}`;

    switch (child.type) {
      case ComponentType.Button: {
        if (child.style === ButtonStyle.Premium) {
          return undefined;
        }
        const styleEmoji: Record<typeof child.style, string> = {
          [ButtonStyle.Danger]: "🟥",
          [ButtonStyle.Link]: "🌐",
          [ButtonStyle.Primary]: "🟦",
          [ButtonStyle.Secondary]: "⬜",
          [ButtonStyle.Success]: "🟩",
        };
        const emoji = ensureValidEmoji(child.emoji, emojis, {
          name: styleEmoji[child.style],
        });

        return {
          label: child.label ?? "Emoji-only",
          value,
          description: `${
            child.style === ButtonStyle.Link ? "Link" : "Button"
          }, ${location}, column ${column}`,
          emoji,
        };
      }
      case ComponentType.StringSelect:
        return {
          label: (child.placeholder ?? `${child.options.length} options`).slice(
            0,
            100,
          ),
          value,
          description: `Select, ${location}`,
          emoji: { name: "🔽" },
        };
      case ComponentType.ChannelSelect:
      case ComponentType.MentionableSelect:
      case ComponentType.RoleSelect:
      case ComponentType.UserSelect:
        return {
          label: (
            child.placeholder ?? `${child.default_values?.length ?? 0} defaults`
          ).slice(0, 100),
          value,
          description: `Select, ${location}`,
          emoji: {
            name:
              child.type === ComponentType.ChannelSelect
                ? "#️⃣"
                : child.type === ComponentType.MentionableSelect
                  ? "*️⃣"
                  : child.type === ComponentType.RoleSelect
                    ? "🏷️"
                    : "👤",
          },
        };
      default:
        break;
    }
  };

  const pad = (array: number[]): number[] => {
    if (arrayConfig?.topLevelIndex !== undefined) {
      array.splice(0, 1, arrayConfig.topLevelIndex + array[0]);
    }
    if (arrayConfig?.padStart !== undefined)
      return [arrayConfig.padStart, ...array];
    return array;
  };

  return components
    .flatMap((component, ri) => {
      if (component.type === ComponentType.Container) {
        return component.components.flatMap((containerChild, cci) => {
          if (isActionRow(containerChild)) {
            return containerChild.components.map((child, ci) =>
              childToOption(child, pad([ri, cci, ci])),
            );
          } else if (
            containerChild.type === ComponentType.Section &&
            containerChild.accessory.type === ComponentType.Button &&
            containerChild.accessory.style !== ButtonStyle.Premium
          ) {
            return [childToOption(containerChild.accessory, pad([ri, cci, 0]))];
          }
          return [];
        });
      } else if (isActionRow(component)) {
        return component.components.map((child, ci) =>
          childToOption(child, pad([ri, ci])),
        );
      } else if (
        component.type === ComponentType.Section &&
        component.accessory.type === ComponentType.Button &&
        component.accessory.style !== ButtonStyle.Premium
      ) {
        return [childToOption(component.accessory, pad([ri, 0]))];
      }
      return [];
    })
    .filter((c): c is APISelectMenuOption => !!c);
};

// Create a menu simulating the real positions in the message
export const getComponentsAsV2Menu = (
  components: APIMessageTopLevelComponent[],
  emojis: APIEmoji[],
  options?: {
    dbComponents?: { id: bigint; data: DraftComponent }[];
    getSelectCustomId?: (index: number) => string;
  },
): APIMessageTopLevelComponent[] => {
  const { dbComponents, getSelectCustomId = () => "" } = options ?? {};

  const recreated: typeof components = [];
  let selectId = 0;
  let totalI = -1;
  for (const component of components) {
    totalI += 1;
    switch (component.type) {
      case ComponentType.Container: {
        const container: typeof component = {
          type: component.type,
          accent_color: component.accent_color,
          components: [],
        };
        const allChildren = getComponentsAsOptions(
          component.components,
          emojis,
          dbComponents,
          { padStart: totalI },
        );
        const chunkedOptions = chunkArray(allChildren, MAX_SELECT_OPTIONS);
        let i = 0;
        for (const options of chunkedOptions) {
          if (options.length === 0) continue;
          const previousCount = i * MAX_SELECT_OPTIONS + 1;
          const select = new StringSelectMenuBuilder()
            .setCustomId(getSelectCustomId(selectId))
            .setPlaceholder(
              `${previousCount}-${
                previousCount + options.length - 1
              } container components`,
            )
            .addOptions(options);
          container.components.push({
            type: ComponentType.ActionRow,
            components: [select.toJSON()],
          });
          i += 1;
          selectId += 1;
        }
        if (container.components.length > 0) recreated.push(container);
        break;
      }
      // 1:1 for top-level component count
      case ComponentType.Section:
      case ComponentType.ActionRow: {
        const options = getComponentsAsOptions(
          [component],
          emojis,
          dbComponents,
          { topLevelIndex: totalI },
        );
        if (options.length === 0) break;

        const typeName =
          component.type === ComponentType.Section ? "Section" : "Row";
        const select = new StringSelectMenuBuilder()
          .setCustomId(getSelectCustomId(selectId))
          .setPlaceholder(
            `${typeName} ${totalI + 1} - ${options.length} component${
              options.length === 1 ? "" : "s"
            }`,
          )
          .addOptions(options);
        recreated.push({
          type: ComponentType.ActionRow,
          components: [select.toJSON()],
        });
        selectId += 1;
        break;
      }
    }
  }

  return recreated;
};

const pickWebhookMessageComponentToEdit = async (
  ctx: InteractionContext,
  message: APIMessage,
) => {
  const guildId = ctx.interaction.guild_id;
  if (!guildId) {
    return ctx.reply("Guild only");
  }

  const emojis = (await ctx.rest.get(
    Routes.guildEmojis(guildId),
  )) as APIEmoji[];

  const threadId = message.position === undefined ? "" : message.channel_id;
  const menu = getComponentsAsV2Menu(message.components ?? [], emojis, {
    getSelectCustomId: (index: number) =>
      `a_edit-component-flow-pick_${message.webhook_id}:${message.id}:${threadId}:${index}` satisfies AutoComponentCustomId,
  });
  if (menu.length === 0) {
    return ctx.reply({
      components: [
        textDisplay("That message has no components that can be picked from."),
      ],
      ephemeral: true,
      componentsV2: true,
    });
  }

  const menuContainer = new ContainerBuilder()
    .setAccentColor(color)
    .addSectionComponents((s) =>
      s
        .addTextDisplayComponents((td) =>
          td.setContent(
            [
              "### Edit Component",
              "**Message**",
              messageLink(message.channel_id, message.id, guildId),
            ].join("\n"),
          ),
        )
        .setThumbnailAccessory((t) =>
          t
            .setURL(
              webhookAvatarUrl({
                id: message.author.id,
                avatar: message.author.avatar,
              }),
            )
            .setDescription(message.author.username),
        ),
    )
    .toJSON();
  // Due to the reduction taking place to form a menu, at least one of these
  // should almost always be displayed
  const free = getRemainingComponentsCount(menu, true);
  if (free >= 3) {
    menu.splice(0, 0, menuContainer);
  } else if (free >= 2) {
    menu.splice(0, 0, menuContainer.components[0]);
  } else if (free >= 1) {
    menu.splice(
      0,
      0,
      (menuContainer.components[0] as APISectionComponent).components[0],
    );
  }
  return ctx.reply({ components: menu, ephemeral: true, componentsV2: true });
};

const getComponentPickCallbackData = (
  messageId: string,
  componentId: bigint,
  path: number[],
): MessageConstructorData => ({
  componentsV2: true,
  components: [
    textDisplay(
      "What aspect of this component would you like to edit? Surface details are what users can see before clicking on the component.",
    ),
    new ActionRowBuilder<SelectMenuBuilder>().addComponents(
      new SelectMenuBuilder()
        .setCustomId(
          `a_edit-component-flow-mode_${messageId}:${componentId}:${path.join(
            ".",
          )}` satisfies AutoComponentCustomId,
        )
        .addOptions(
          new SelectMenuOptionBuilder()
            .setLabel("Details")
            .setValue("internal")
            .setDescription(
              "Just change the surface details without leaving Discord",
            ),
          new SelectMenuOptionBuilder()
            .setLabel("Everything")
            .setValue("external")
            .setDescription("Change what happens when this component is used"),
        ),
    ),
  ],
});

export const editComponentFlowPickCallback: SelectMenuCallback = async (
  ctx,
) => {
  const {
    webhookId,
    messageId,
    threadId: threadId_,
  } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "webhookId",
    "messageId",
    "threadId",
  );
  const threadId = threadId_ || undefined;

  const db = getDb(ctx.env.HYPERDRIVE);

  const [scope, key] = ctx.interaction.data.values[0].split(":");
  switch (scope as "id" | "link" | "unknown") {
    case "id": {
      const path = ctx.interaction.data.values[0]
        .split(":")[2]
        .split(".")
        .map(Number);
      const id = BigInt(key);
      const component = await db.query.discordMessageComponents.findFirst({
        where: (table, { eq }) => eq(table.id, id),
        columns: {
          id: true,
          guildId: true,
          messageId: true,
        },
      });
      if (
        !component ||
        component.guildId?.toString() !== ctx.interaction.guild_id ||
        (component.messageId !== null &&
          component.messageId?.toString() !== messageId)
      ) {
        return ctx.updateMessage({
          components: [textDisplay("Unknown component")],
        });
      }

      return ctx.updateMessage(
        getComponentPickCallbackData(messageId, component.id, path),
      );
    }
    case "link": {
      const path = key.split(".").map(Number);
      const { message } = await getWebhookMessage(
        ctx.env,
        webhookId,
        messageId,
        threadId,
        ctx.rest,
      );
      const foundComponent = extractComponentByPath(message, path);
      if (
        !foundComponent ||
        foundComponent.type !== ComponentType.Button ||
        foundComponent.style !== ButtonStyle.Link
      ) {
        return ctx.updateMessage({
          components: [
            textDisplay("The button could not be located in the message."),
          ],
        });
      }

      const dbComponents = await db.query.discordMessageComponents.findMany({
        where: (table, { eq, and }) =>
          and(
            eq(table.messageId, BigInt(messageId)),
            eq(table.type, ComponentType.Button),
          ),
        columns: {
          id: true,
          data: true,
        },
      });
      let dbComponent = dbComponents.find(
        (c) =>
          c.data.type === ComponentType.Button &&
          c.data.style === ButtonStyle.Link &&
          c.data.url === foundComponent.url,
      );
      if (!dbComponent) {
        const user = await upsertDiscordUser(db, ctx.user);
        dbComponent = (
          await db
            .insert(discordMessageComponents)
            .values({
              channelId: makeSnowflake(message.channel_id),
              messageId: makeSnowflake(message.id),
              // biome-ignore lint/style/noNonNullAssertion: Guild only
              guildId: makeSnowflake(ctx.interaction.guild_id!),
              type: ComponentType.Button,
              data: foundComponent satisfies StorableButtonWithUrl,
              createdById: user.id,
            })
            .returning({
              id: discordMessageComponents.id,
              data: discordMessageComponents.data,
            })
        )[0];
      }

      const modal = getComponentEditModal(dbComponent, messageId, path);
      return [
        ctx.modal(modal.toJSON()),
        async () => {
          await ctx.followup.editOriginalMessage({
            components: [
              textDisplay("Click the button to resume editing."),
              new ActionRowBuilder<ButtonBuilder>().addComponents(
                new ButtonBuilder()
                  .setCustomId(
                    `a_edit-component-flow-modal-resend_${messageId}:${
                      dbComponent.id
                    }:${path.join(".")}` satisfies AutoComponentCustomId,
                  )
                  .setStyle(ButtonStyle.Secondary)
                  .setLabel(ctx.t("customize")),
              ),
            ],
          });
        },
      ];
    }
    default:
      // As far as we know, this component doesn't actually exist anymore
      return ctx.reply({
        components: [
          textDisplay("Cannot resolve that component from the database."),
        ],
        ephemeral: true,
        componentsV2: true,
      });
  }
};

const getComponentEditModal = (
  component: {
    id: bigint;
    data: DraftComponent;
  },
  messageId: string,
  path: number[],
) => {
  const modal = new ModalBuilder()
    .setCustomId(
      `a_edit-component-flow-modal_${messageId}:${component.id}:${path.join(
        ".",
      )}` satisfies AutoModalCustomId,
    )
    .setTitle("Edit Component");

  switch (component.data.type) {
    case ComponentType.Button:
      if (component.data.style === ButtonStyle.Premium) {
        modal.addLabelComponents(
          // we don't use function chaining here because it breaks the type guard
          new LabelBuilder()
            .setLabel("SKU ID")
            .setDescription("Identifier for a purchasable SKU")
            .setTextInputComponent(
              new TextInputBuilder()
                .setCustomId("sku_id")
                .setStyle(TextInputStyle.Short)
                .setRequired(true)
                .setValue(component.data.sku_id),
            ),
        );
      } else {
        modal.addLabelComponents(
          new LabelBuilder()
            .setLabel("Label")
            .setDescription("The text displayed on this button.")
            .setTextInputComponent(
              new TextInputBuilder()
                .setCustomId("label")
                .setStyle(TextInputStyle.Short)
                .setRequired(false)
                .setMaxLength(80)
                .setValue(component.data.label ?? ""),
            ),
          new LabelBuilder()
            .setLabel("Emoji")
            .setDescription("Like :smile: or a custom emoji in the server.")
            .setTextInputComponent(
              new TextInputBuilder()
                .setCustomId("emoji")
                .setStyle(TextInputStyle.Short)
                .setRequired(false)
                .setValue(
                  component.data.emoji?.id ?? component.data.emoji?.name ?? "",
                ),
            ),
        );
        if (component.data.style === ButtonStyle.Link) {
          modal.addLabelComponents(
            new LabelBuilder()
              .setLabel("Button URL")
              .setDescription(
                "The full URL this button will lead to when it is clicked.",
              )
              .setTextInputComponent(
                new TextInputBuilder()
                  .setCustomId("url")
                  .setStyle(TextInputStyle.Paragraph)
                  .setRequired(true)
                  .setValue(component.data.url),
              ),
          );
        }
      }
      modal.addLabelComponents((l) =>
        l
          .setLabel("Disabled?")
          .setStringSelectMenuComponent((s) =>
            s
              .setCustomId("disabled")
              .addOptions([
                new StringSelectMenuOptionBuilder()
                  .setLabel("True")
                  .setValue("true")
                  .setDescription("The button will not be clickable.")
                  .setDefault(!!component.data.disabled),
                new StringSelectMenuOptionBuilder()
                  .setLabel("False")
                  .setValue("false")
                  .setDescription("The button will be clickable")
                  .setDefault(!component.data.disabled),
              ]),
          ),
      );
      break;
    case ComponentType.StringSelect:
    case ComponentType.ChannelSelect:
    case ComponentType.MentionableSelect:
    case ComponentType.RoleSelect:
    case ComponentType.UserSelect:
      modal.addLabelComponents(
        new LabelBuilder()
          .setLabel("Placeholder")
          .setDescription(
            "The text to show in the select menu when it is collapsed.",
          )
          .setTextInputComponent(
            new TextInputBuilder()
              .setCustomId("placeholder")
              .setStyle(TextInputStyle.Paragraph)
              .setMaxLength(150)
              .setRequired(false)
              .setValue(component.data.placeholder ?? ""),
          ),
        new LabelBuilder()
          .setLabel("Disabled?")
          .setStringSelectMenuComponent((s) =>
            s
              .setCustomId("disabled")
              .addOptions([
                new StringSelectMenuOptionBuilder()
                  .setLabel("True")
                  .setValue("true")
                  .setDescription("The select will not be usable.")
                  .setDefault(!!component.data.disabled),
                new StringSelectMenuOptionBuilder()
                  .setLabel("False")
                  .setValue("false")
                  .setDescription("The select will be usable")
                  .setDefault(!component.data.disabled),
              ]),
          ),
      );
      break;
    default:
      break;
  }
  return modal;
};

export const editComponentFlowModeCallback: SelectMenuCallback = async (
  ctx,
) => {
  const {
    messageId,
    componentId,
    path: path_,
  } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "messageId",
    "componentId",
    "path",
  );
  const path = path_.split(".").map(Number);
  const mode = ctx.interaction.data.values[0] as "internal" | "external";

  const db = getDb(ctx.env.HYPERDRIVE);
  const component = await db.query.discordMessageComponents.findFirst({
    where: (table, { eq }) => eq(table.id, BigInt(componentId)),
    columns: {
      id: true,
      data: true,
      guildId: true,
      messageId: true,
    },
  });
  if (
    !component ||
    component.guildId?.toString() !== ctx.interaction.guild_id ||
    (component.messageId !== null &&
      component.messageId?.toString() !== messageId)
  ) {
    // This shouldn't happen unless the component was deleted in between
    // running the command and selecting the option
    return ctx.updateMessage({
      components: [textDisplay("Unknown component")],
    });
  }

  if (mode === "internal") {
    const modal = getComponentEditModal(component, messageId, path);
    // TODO: also allow changing button style in this mode
    return [
      ctx.modal(modal.toJSON()),
      async () => {
        await ctx.followup.editOriginalMessage({
          components: [
            textDisplay("Click the button to continue editing the component."),
            new ActionRowBuilder<ButtonBuilder>().addComponents(
              new ButtonBuilder()
                .setCustomId(
                  `a_edit-component-flow-modal-resend_${messageId}:${componentId}:${path_}` satisfies AutoComponentCustomId,
                )
                .setStyle(ButtonStyle.Secondary)
                .setLabel(ctx.t("customize")),
            ),
          ],
        });
      },
    ];
  }

  const editorToken = await generateEditorTokenForComponent(
    ctx.env,
    component.id,
    {
      user: {
        id: ctx.user.id,
        name: ctx.user.username,
        avatar: ctx.user.avatar,
      },
    },
  );

  return ctx.updateMessage({
    components: [
      textDisplay(
        "Click the button to open your browser and edit the component.",
      ),
      new ActionRowBuilder<ButtonBuilder>().addComponents(
        new ButtonBuilder()
          .setStyle(ButtonStyle.Link)
          .setLabel(ctx.t("customize"))
          .setURL(getEditorTokenComponentUrl(editorToken, ctx.env)),
      ),
    ],
  });
};

const registerComponentUpdate = async (
  ctx: InteractionContext<APIInteraction>,
  component: {
    id: bigint;
    data: DraftComponent;
    createdBy: { discordId: bigint | null } | null;
  },
  webhook: { id: string; token: string; guild_id?: string },
  message: APIMessage,
  path: number[],
) => {
  const { id, data, createdBy } = component;
  const db = getDb(ctx.env.HYPERDRIVE);
  const user = await upsertDiscordUser(db, ctx.user);

  const customId =
    data.type === ComponentType.Button &&
    (data.style === ButtonStyle.Link || data.style === ButtonStyle.Premium)
      ? undefined
      : `p_${id}`;

  const built = buildStorableComponent(data, customId);
  if (!built) {
    throw new Error(`Failed to built the component (type ${data.type}).`);
  }

  const foundComponent = extractComponentByPath(message, path, {
    operation: "replace",
    replacement: built,
  });
  if (!foundComponent) {
    throw new Error(
      `Couldn't find the row that this component is on. Try editing via the site instead (choose "Everything")`,
    );
  }

  const editedMsg = await db.transaction(
    autoRollbackTx(async (tx) => {
      await tx
        .insert(discordMessageComponents)
        .values({
          id,
          guildId: webhook.guild_id
            ? makeSnowflake(webhook.guild_id)
            : undefined,
          channelId: makeSnowflake(message.channel_id),
          messageId: makeSnowflake(message.id),
          createdById: user.id,
          type: data.type,
          data,
        })
        .onConflictDoUpdate({
          target: discordMessageComponents.id,
          set: {
            data,
            draft: false,
            updatedById: user.id,
          },
        });

      // An error thrown here triggers a rollback
      return (await ctx.rest.patch(
        Routes.webhookMessage(webhook.id, webhook.token, message.id),
        {
          body: { components: message.components },
          query: getWebhookThreadQuery(message),
        },
      )) as APIMessage;
    }),
  );

  if (customId !== undefined) {
    await launchComponentKV(ctx.env, {
      componentId: id,
      data,
      createdById: createdBy?.discordId?.toString() ?? ctx.user.id,
      updatedById: ctx.user.id,
      // Wish we could do this but we need guild_permissions and so it
      // requires an extra request to resolve the roles
      // responsibleUser: {
      //   id: ctx.user.id,
      //   username: ctx.user.username,
      //   roles: ctx.interaction.member?.roles ?? [],
      //   reason: "last edited the component",
      // },
    });
  }
  return editedMsg;
};

export const partialEmojiToComponentEmoji = (
  emoji: APIPartialEmoji,
): APIMessageComponentEmoji => ({
  id: emoji.id ?? undefined,
  name: emoji.name ?? undefined,
  animated: emoji.animated,
});

export const editComponentFlowModalCallback: ModalCallback = async (ctx) => {
  const {
    messageId,
    componentId,
    path: path_,
  } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "messageId",
    "componentId",
    "path",
  );
  const path = path_.split(".").map(Number);

  const db = getDb(ctx.env.HYPERDRIVE);
  const component = await db.query.discordMessageComponents.findFirst({
    where: (table, { eq }) => eq(table.id, BigInt(componentId)),
    columns: {
      id: true,
      data: true,
      guildId: true,
      channelId: true,
      messageId: true,
    },
    with: { createdBy: { columns: { discordId: true } } },
  });
  if (
    !component ||
    component.guildId?.toString() !== ctx.interaction.guild_id ||
    (component.messageId !== null &&
      component.messageId?.toString() !== messageId)
  ) {
    // This shouldn't happen unless the component was deleted in between
    // running the command and selecting the option
    return ctx.updateMessage({
      components: [textDisplay("Unknown component")],
    });
  }
  // biome-ignore lint/style/noNonNullAssertion: Only a guild-only command should get us here
  const guildId = (component.guildId?.toString() ?? ctx.interaction.guild_id)!;

  const channelId =
    component.channelId?.toString() ?? ctx.interaction.channel?.id;
  if (!channelId) {
    return ctx.updateMessage({
      components: [textDisplay("Channel context was unavailable")],
    });
  }

  let message: APIMessage | undefined;
  try {
    message = (await ctx.rest.get(
      Routes.channelMessage(channelId, messageId),
    )) as APIMessage;
  } catch {
    return ctx.updateMessage({
      components: [
        textDisplay(
          `Failed to fetch the message (${messageId}). Make sure I am able to view <#${channelId}>.`,
        ),
      ],
    });
  }
  const webhookId = message.webhook_id;
  if (!webhookId) {
    return ctx.updateMessage({
      components: [
        textDisplay(
          `Apparently, the message (${messageId}) was not sent by a webhook. This shouldn't happen.`,
        ),
      ],
    });
  }
  const webhook = await getWebhook(webhookId, ctx.env, message.application_id);
  if (!webhook.token) {
    return ctx.updateMessage({
      components: [
        textDisplay(
          `The webhook's token (ID ${webhookId}) is not accessible, so I cannot edit the message.`,
        ),
      ],
    });
  }

  const { data } = component;
  switch (data.type) {
    case ComponentType.Button:
      if (data.style === ButtonStyle.Premium) {
        data.sku_id = ctx.getModalComponent("sku_id").value;
      } else {
        data.label = ctx.getModalComponent("label")?.value || undefined;
        const emojiRaw = ctx.getModalComponent("emoji")?.value || undefined;
        if (!emojiRaw) {
          data.emoji = undefined;
        } else {
          if (emojiRaw.includes(" ")) {
            return ctx.reply({
              components: [
                textDisplay("Invalid emoji: Contains invalid characters."),
              ],
              ephemeral: true,
              componentsV2: true,
            });
          }

          const emoji = await resolveEmoji(
            ctx.rest,
            emojiRaw,
            undefined,
            guildId,
            ctx.env,
          );
          if (!emoji) {
            return ctx.reply({
              components: [
                textDisplay(
                  "Could not find an emoji that matches the input. For a custom emoji, try using the numeric ID, and make sure Discohook has access to it.",
                ),
              ],
              ephemeral: true,
              componentsV2: true,
            });
          }
          data.emoji = partialEmojiToComponentEmoji(emoji);
        }
      }
      if (data.style === ButtonStyle.Link) {
        let url: URL;
        try {
          url = new URL(ctx.getModalComponent("url").value);
          if (!["http:", "https:", "discord:"].includes(url.protocol)) {
            throw Error("Protocol must be `http`, `https`, or `discord`.");
          }
        } catch {
          return ctx.reply({
            components: [textDisplay("Invalid URL")],
            ephemeral: true,
            componentsV2: true,
          });
        }
        if (url.searchParams.get("dhc-id")) {
          url.searchParams.delete("dhc-id");
        }
        data.url = url.href;
      }
      break;
    default:
      break;
  }
  const disabledRaw =
    ctx.getModalComponent<APIModalSubmitStringSelectComponent>("disabled")
      ?.values[0];
  if (disabledRaw) {
    data.disabled = disabledRaw === "true";
  }

  const edited = await registerComponentUpdate(
    ctx,
    component,
    {
      id: webhookId,
      token: webhook.token,
      guild_id: guildId,
    },
    message,
    path,
  );

  return ctx.updateMessage({
    components: [
      textDisplay(
        `Message edited successfully: ${messageLink(
          edited.channel_id,
          edited.id,
          guildId,
        )}`,
      ),
    ],
  });
};

export const editComponentFlowModalResendCallback: ButtonCallback = async (
  ctx,
) => {
  const {
    messageId,
    componentId,
    path: path_,
  } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "messageId",
    "componentId",
    "path",
  );
  const path = path_.split(".").map(Number);

  const db = getDb(ctx.env.HYPERDRIVE);
  const component = await db.query.discordMessageComponents.findFirst({
    where: (table, { eq }) => eq(table.id, BigInt(componentId)),
    columns: {
      id: true,
      data: true,
      guildId: true,
      messageId: true,
    },
  });
  if (
    !component ||
    component.guildId?.toString() !== ctx.interaction.guild_id ||
    (component.messageId !== null &&
      component.messageId?.toString() !== messageId)
  ) {
    // This shouldn't happen unless the component was deleted in between
    // running the command and selecting the option
    return ctx.updateMessage({
      components: [textDisplay("Unknown component")],
    });
  }

  return ctx.modal(getComponentEditModal(component, messageId, path).toJSON());
};

```

### File: `packages/bot/src/commands/components/entry.ts`
```ts
import { ActionRowBuilder, ButtonBuilder } from "@discordjs/builders";
import { messageLink } from "@discordjs/formatters";
import { REST } from "@discordjs/rest";
import dedent from "dedent-js";
import {
  type APIApplicationCommandAutocompleteInteraction,
  type APIGuildChannel,
  type APIMessage,
  type APIWebhook,
  ApplicationCommandOptionType,
  ButtonStyle,
  Routes,
} from "discord-api-types/v10";
import { getDate, type Snowflake } from "discord-snowflake";
import type {
  AppCommandAutocompleteCallback,
  ChatInputAppCommandCallback,
  MessageAppCommandCallback,
} from "../../commands.js";
import type { AutoComponentCustomId } from "../../components.js";
import type { InteractionContext } from "../../interactions.js";
import type { Env } from "../../types/env.js";
import { getWebhook } from "../webhooks/webhookInfo.js";
import { startComponentFlow } from "./add.js";

const MESSAGE_LINK_RE =
  /^https:\/\/(?:www\.|ptb\.|canary\.)?discord(?:app)?\.com\/channels\/(\d+)\/(\d+)\/(\d+)$/;

export const resolveMessageLink = async (
  rest: REST,
  messageLink: string,
  checkGuildId: string | undefined,
): Promise<APIMessage | string> => {
  const match = messageLink.match(MESSAGE_LINK_RE);
  if (!match) {
    return dedent`
      Invalid message link. Select an option from the autocomplete menu, or
      right click or long-press a message, then use "Copy Message Link".
    `;
  }
  if (checkGuildId && checkGuildId !== match[1]) {
    return "That message is not from this server.";
  }

  if (checkGuildId) {
    const channel = (await rest.get(
      Routes.channel(match[2]),
    )) as APIGuildChannel;
    if (!channel.guild_id || channel.guild_id !== checkGuildId) {
      return "That message is not from this server.";
    }
  }

  let message: APIMessage;
  try {
    message = (await rest.get(
      Routes.channelMessage(match[2], match[3]),
    )) as APIMessage;
  } catch {
    return "Unable to resolve that message. Make sure you are pasting a valid message link in a channel that I can access.";
  }

  return message;
};

type APIWebhookWithToken = APIWebhook & Required<Pick<APIWebhook, "token">>;

export const getWebhookMessage = async (
  env: Env,
  webhookId: string,
  messageId: string,
  threadId?: string,
  rest_?: REST,
): Promise<{ webhook: APIWebhookWithToken; message: APIMessage }> => {
  const webhook = await getWebhook(webhookId, env);
  if (!webhook.token) {
    throw Error("Webhook token is inaccessible.");
  }

  const rest = rest_ ?? new REST();
  const message = (await rest.get(
    Routes.webhookMessage(webhook.id, webhook.token, messageId),
    {
      auth: false,
      query: threadId
        ? new URLSearchParams({ thread_id: threadId })
        : undefined,
    },
  )) as APIMessage;
  return { webhook: webhook as APIWebhookWithToken, message };
};

export const addComponentChatEntry: ChatInputAppCommandCallback<true> = async (
  ctx,
) => {
  const message = await resolveMessageLink(
    ctx.rest,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    return ctx.reply({
      content: message,
      ephemeral: true,
    });
  }
  return await startComponentFlow(ctx, message);
};

/** Always use `filterKey` when specifying `filter`, or results will not be cached! */
export const autocompleteMessageCallback = async (
  ctx: InteractionContext<APIApplicationCommandAutocompleteInteraction>,
  filter?: (message: APIMessage) => boolean,
  filterKey?: string,
) => {
  const channelOption = ctx._getOption("channel");
  const query = ctx.getStringOption("message").value;

  const channelId =
    channelOption?.type === ApplicationCommandOptionType.Channel
      ? channelOption.value
      : ctx.interaction.channel?.id;
  if (!channelId) return [];

  interface CompactCompatibleMessage {
    id: string;
    authorName: string;
    label: string;
  }

  const kvKey = `cache-${
    filterKey ?? "autocompleteChannelMessages"
  }-${channelId}`;
  const cached = await ctx.env.KV.get<CompactCompatibleMessage[]>(
    kvKey,
    "json",
  );
  let messages = cached;
  if (!messages) {
    const channelMessages = (await ctx.rest.get(
      Routes.channelMessages(channelId),
      { query: new URLSearchParams({ limit: "20" }) },
    )) as APIMessage[];

    messages = channelMessages.filter(filter ?? (() => true)).map((m) => {
      const createdAt = getDate(m.id as Snowflake);
      const sentToday = new Date().toDateString() === createdAt.toDateString();

      return {
        id: m.id,
        authorName: m.author.username,
        label: `${
          sentToday
            ? `Today at ${createdAt.toLocaleTimeString(ctx.interaction.locale, {
                hour: "numeric",
                minute: "2-digit",
                timeZoneName: "short",
              })}`
            : createdAt.toDateString()
        } | ${m.author.username} | ${m.embeds.length} embed${
          m.embeds.length === 1 ? "" : "s"
        }`,
      } as CompactCompatibleMessage;
    });

    // We don't want all message autocompletions to accidentally receive
    // filtered results. There are surely better ways to do this, but
    // hopefully I never forget to simply provide both parameters.
    if (!filter || (!!filter && !filterKey)) {
      await ctx.env.KV.put(kvKey, JSON.stringify(messages), {
        expirationTtl: 60,
      });
    }
  }

  return messages
    .filter((m) => m.authorName.toLowerCase().includes(query.toLowerCase()))
    .map((message) => {
      return {
        name: message.label.slice(0, 100),
        // biome-ignore lint/style/noNonNullAssertion: we are in a guild
        value: messageLink(channelId, message.id, ctx.interaction.guild_id!),
      };
    });
};

export const addComponentMessageAutocomplete: AppCommandAutocompleteCallback = (
  ctx,
) =>
  autocompleteMessageCallback(
    ctx,
    (m) =>
      !!m.webhook_id &&
      !m.interaction_metadata &&
      // dapi-types says application_id is only for interaction responses,
      // but it appears for application-owned webhooks as well:
      // https://discord.dev/resources/channel#message-object
      m.application_id === ctx.followup.applicationId &&
      m.application_id !== m.webhook_id,
    "autocompleteChannelWebhookMessages",
  );

export const addComponentMessageEntry: MessageAppCommandCallback = (ctx) => {
  const message = ctx.getMessage();
  const threadId = message.position === undefined ? "" : message.channel_id;
  const row = new ActionRowBuilder<ButtonBuilder>().addComponents(
    new ButtonBuilder()
      .setCustomId(
        `a_edit-component-flow-ctx_${message.webhook_id}:${message.id}:${threadId}` satisfies AutoComponentCustomId,
      )
      .setLabel("Edit mode")
      .setStyle(ButtonStyle.Secondary),
    // new ButtonBuilder()
    //   .setCustomId(
    //     `a_debug-component-flow-ctx_${message.webhook_id}:${message.id}:${threadId}` satisfies AutoComponentCustomId,
    //   )
    //   .setLabel("Debug")
    //   .setStyle(ButtonStyle.Secondary),
    new ButtonBuilder()
      .setLabel("View all")
      .setStyle(ButtonStyle.Link)
      .setURL(
        `${ctx.env.DISCOHOOK_ORIGIN}/s/${ctx.interaction.guild_id}?t=components`,
      ),
    new ButtonBuilder()
      .setCustomId(
        `a_delete-component-pick-ctx_${message.webhook_id}:${message.id}:${threadId}` satisfies AutoComponentCustomId,
      )
      .setLabel("Delete mode")
      .setStyle(ButtonStyle.Danger),
  );
  return startComponentFlow(ctx, message, [
    row,
  ]) as ReturnType<MessageAppCommandCallback>;
};

```

### File: `packages/bot/src/commands/components/migrate.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  messageLink,
} from "@discordjs/builders";
import {
  type APIActionRowComponent,
  type APIComponentInMessageActionRow,
  type APIMessage,
  type APIUser,
  ButtonStyle,
  ComponentType,
  MessageFlags,
  type RESTGetAPIGuildEmojisResult,
  type RESTPatchAPIWebhookWithTokenMessageJSONBody,
  Routes,
} from "discord-api-types/v10";
import { and, count, eq, notInArray } from "drizzle-orm";
import {
  autoRollbackTx,
  backups,
  buttons,
  type DBWithSchema,
  discordMessageComponents,
  type DraftComponent,
  type DraftFlow,
  FlowActionCheckFunctionType,
  FlowActionSetVariableType,
  FlowActionType,
  generateId,
  getchTriggerGuild,
  getDb,
  makeSnowflake,
  type QueryData,
  upsertDiscordUser,
} from "store";
import type { ChatInputAppCommandCallback } from "../../commands.js";
import type {
  AutoComponentCustomId,
  ButtonCallback,
} from "../../components.js";
import type { InteractionContext } from "../../interactions.js";
import {
  hasCustomId,
  isActionRow,
  parseAutoComponentId,
} from "../../util/components.js";
import { getWebhookThreadQuery } from "../../util/messages.js";
import { getWebhook } from "../webhooks/webhookInfo.js";
import { resolveMessageLink } from "./entry.js";

export const migrateLegacyButtons = async (
  ctx: InteractionContext,
  db: DBWithSchema,
  guildId: string,
  message: APIMessage,
) => {
  const guild = await getchTriggerGuild(ctx.rest, ctx.env, guildId);
  // Not sure if it's better for RL reasons to use guildMember instead?
  const owner = (await ctx.rest.get(Routes.user(guild.owner_id))) as APIUser;
  const ownerUser = await upsertDiscordUser(db, owner);

  const oldMessageButtons = await db.query.buttons.findMany({
    where: (buttons, { eq }) =>
      eq(buttons.messageId, makeSnowflake(message.id)),
    columns: {
      id: true,
      roleId: true,
      customId: true,
      customLabel: true,
      emoji: true,
      style: true,
      customDmMessageData: true,
      customEphemeralMessageData: true,
      customPublicMessageData: true,
      type: true,
      url: true,
    },
  });
  if (oldMessageButtons.length === 0) {
    throw Error(ctx.t("noMigratableComponents"));
  }

  const getOldCustomId = (button: {
    roleId: bigint | null;
    customId: string | null;
  }): string | undefined => {
    if (button.roleId) {
      return `button_role:${message.id}-${button.roleId}`;
    } else if (button.customId) {
      return button.customId;
    }
  };

  const oldIdMap: Record<string, string> = {};
  const inserted = await db.transaction(
    autoRollbackTx(async (tx) => {
      const oldIdToBackupName: Record<string, string> = {};
      const backupInsertValues: (typeof backups.$inferInsert)[] =
        oldMessageButtons
          .filter(
            (button) =>
              !!getOldCustomId(button) &&
              !!(
                button.customPublicMessageData ||
                button.customEphemeralMessageData ||
                button.customDmMessageData
              ),
          )
          .map((button) => {
            const name = `Button (${
              button.customPublicMessageData ? "public" : "hidden"
            } message) ${Math.floor(Math.random() * 1000000)}`;
            // biome-ignore lint/style/noNonNullAssertion: Filter
            oldIdToBackupName[getOldCustomId(button)!] = name;
            // biome-ignore lint/style/noNonNullAssertion: At least one must be non-null according to filter
            const dataStr = (button.customPublicMessageData ??
              button.customEphemeralMessageData ??
              button.customDmMessageData)!;
            return {
              name,
              ownerId: ownerUser.id,
              data: {
                messages: [{ data: JSON.parse(dataStr) }],
              } satisfies QueryData,
              dataVersion: "d2",
            };
          });
      const insertedBackups =
        backupInsertValues.length === 0
          ? []
          : await tx
              .insert(backups)
              .values(backupInsertValues)
              .returning({ id: backups.id, name: backups.name });

      const values: (typeof discordMessageComponents.$inferInsert)[] = [];
      for (const button of oldMessageButtons) {
        const old = getOldCustomId(button);
        const newId = generateId();
        if (old) {
          oldIdMap[old] = newId;
        }

        const flow: DraftFlow = { actions: [] };
        if (!button.url) {
          const backupId = insertedBackups.find(
            old && oldIdToBackupName[old]
              ? (backup) => backup.name === oldIdToBackupName[old]
              : () => false,
          )?.id;

          if (button.roleId) {
            flow.actions.push(
              {
                type: FlowActionType.Check,
                function: {
                  type: FlowActionCheckFunctionType.In,
                  array: {
                    varType: FlowActionSetVariableType.Get,
                    value: "member.role_ids",
                  },
                  element: {
                    varType: FlowActionSetVariableType.Static,
                    value: String(button.roleId),
                  },
                },
                // biome-ignore lint/suspicious/noThenProperty: see note in quick.ts
                then: [
                  {
                    type: FlowActionType.SetVariable,
                    name: "response",
                    value: `Removed the <@&${button.roleId}> role from you.`,
                  },
                ],
                else: [
                  {
                    type: FlowActionType.SetVariable,
                    name: "response",
                    value: `Gave you the <@&${button.roleId}> role.`,
                  },
                ],
              },
              {
                type: FlowActionType.ToggleRole,
                roleId: String(button.roleId),
              },
              {
                type: FlowActionType.Stop,
                message: {
                  content: "{response}",
                  flags: MessageFlags.Ephemeral,
                },
              },
            );
          } else if (backupId) {
            flow.actions.push({
              type: FlowActionType.SendMessage,
              backupId: backupId.toString(),
              backupMessageIndex: 0,
              response: true,
              flags:
                button.customEphemeralMessageData || button.customDmMessageData
                  ? MessageFlags.Ephemeral
                  : undefined,
            });
          } else if (button.type === "do_nothings") {
            flow.actions.push({ type: FlowActionType.Dud });
          }
        }

        const buttonEmoji = button.emoji
          ? button.emoji.startsWith("<")
            ? {
                id: button.emoji.split(":")[2].replace(/>$/, ""),
                name: button.emoji.split(":")[1],
                animated: button.emoji.split(":")[0] === "<a",
              }
            : {
                name: button.emoji,
              }
          : undefined;

        let data: DraftComponent;
        if (button.url) {
          data = {
            type: ComponentType.Button,
            style: ButtonStyle.Link,
            label: button.customLabel ?? undefined,
            emoji: buttonEmoji,
            url: button.url,
          };
        } else {
          data = {
            type: ComponentType.Button,
            style:
              (
                {
                  // ??? what was I on?
                  primary: ButtonStyle.Primary,
                  blurple: ButtonStyle.Primary,
                  secondary: ButtonStyle.Secondary,
                  gray: ButtonStyle.Secondary,
                  link: ButtonStyle.Secondary,
                  success: ButtonStyle.Success,
                  green: ButtonStyle.Success,
                  danger: ButtonStyle.Danger,
                  red: ButtonStyle.Danger,
                } as const
              )[button.style ?? "primary"] ?? ButtonStyle.Primary,
            label: button.customLabel ?? undefined,
            emoji: buttonEmoji,
            flow,
          };
        }
        values.push({
          id: BigInt(newId),
          channelId: makeSnowflake(message.channel_id),
          guildId: makeSnowflake(guildId),
          messageId: makeSnowflake(message.id),
          draft: false,
          type: ComponentType.Button,
          data,
          createdById: ownerUser.id,
        });
      }

      if (values.length === 0) return [];
      const inserted = await tx
        .insert(discordMessageComponents)
        .values(values)
        .onConflictDoNothing()
        .returning({
          id: discordMessageComponents.id,
          data: discordMessageComponents.data,
        });
      return inserted.map((val) => ({ ...val, createdBy: ownerUser }));
    }),
  );

  const emojis = (await ctx.rest.get(
    Routes.guildEmojis(guildId),
  )) as RESTGetAPIGuildEmojisResult;

  // In the very specific context of this command, the message should always
  // be CV1, so we're just lazily type guarding for new components here.
  const rows = message.components?.map((row) => {
    if (!isActionRow(row)) return row;
    return {
      ...row,
      components: row.components.map((component) => {
        if (
          component.type !== ComponentType.Button ||
          component.style === ButtonStyle.Premium
        ) {
          return component;
        }

        // Remove likely-inaccessible emojis
        const subdata = { ...component };
        if (
          subdata.emoji?.id &&
          !emojis.find((e) => e.id === subdata.emoji?.id)
        ) {
          subdata.emoji = subdata.label ? undefined : { name: "🌫️" };
        }
        if (!hasCustomId(subdata)) return subdata;

        const button = inserted.find(
          (b) => String(b.id) === oldIdMap[subdata.custom_id],
        );
        return {
          ...subdata,
          disabled: !button,
          // This shouldn't happen, but fall back anyway to avoid failure
          custom_id: button ? `p_${button.id}` : subdata.custom_id,
        };
      }),
    };
  }) as APIActionRowComponent<APIComponentInMessageActionRow>[];
  // await ctx.followup.editOriginalMessage({ components: rows });
  return { inserted, rows, guild, emojis, oldIdMap };
};

export const migrateComponentsChatEntry: ChatInputAppCommandCallback<
  true
> = async (ctx) => {
  const message = await resolveMessageLink(
    ctx.rest,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    return ctx.reply({
      content: message,
      ephemeral: true,
    });
  }
  if (!message.webhook_id) {
    return ctx.reply({
      content: "This is not a webhook message.",
      ephemeral: true,
    });
  }

  const db = getDb(ctx.env.HYPERDRIVE);
  const result = (
    await db
      .select({
        count: count(),
      })
      .from(buttons)
      .where(eq(buttons.messageId, makeSnowflake(message.id)))
  )[0];
  if (result.count === 0) {
    return ctx.reply({
      content: "There are no buttons on this message to migrate.",
      ephemeral: true,
    });
  }
  return ctx.reply({
    content: `This will replace ALL components on ${messageLink(
      message.channel_id,
      message.id,
      ctx.interaction.guild_id,
    )} with ${
      result.count
    } migrated legacy buttons. Positions may be altered, but can be changed later. Are you sure you want to do this?`,
    components: [
      new ActionRowBuilder<ButtonBuilder>().addComponents(
        new ButtonBuilder()
          .setCustomId(
            `a_migrate-buttons-confirm_${message.channel_id}:${message.id}` satisfies AutoComponentCustomId,
          )
          .setLabel("Migrate")
          .setStyle(ButtonStyle.Danger),
        new ButtonBuilder()
          .setCustomId(
            "a_migrate-buttons-cancel_" satisfies AutoComponentCustomId,
          )
          .setLabel("Cancel")
          .setStyle(ButtonStyle.Secondary),
      ),
    ],
    ephemeral: true,
  });
};

export const migrateComponentsConfirm: ButtonCallback = async (ctx) => {
  const { channelId, messageId } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "channelId",
    "messageId",
  );
  const guildId = ctx.interaction.guild_id;
  if (!guildId) throw Error();

  const message = (await ctx.rest.get(
    Routes.channelMessage(channelId, messageId),
  )) as APIMessage;

  // biome-ignore lint/style/noNonNullAssertion: Checked before this callback
  const webhook = await getWebhook(message.webhook_id!, ctx.env);
  if (!webhook.token) {
    return ctx.updateMessage({
      content: "The webhook's token was inaccessible.",
      components: [],
    });
  }

  const db = getDb(ctx.env.HYPERDRIVE);
  return [
    ctx.updateMessage({ content: "Migrating...", components: [] }),
    async () => {
      console.log("[migrating] Start followup");
      const { inserted, emojis } = await migrateLegacyButtons(
        ctx,
        db,
        guildId,
        message,
      );

      const rows: ActionRowBuilder<ButtonBuilder>[] = [];
      for (const component of inserted) {
        if (rows.length >= 5) break;
        if (component.data.type === ComponentType.Button) {
          let row = rows[rows.length - 1];
          if (!row || row.components.length >= 5) {
            row = new ActionRowBuilder();
            rows.push(row);
          }
          const button = new ButtonBuilder().setStyle(component.data.style);
          const { data } = component;
          if ("emoji" in data && data.emoji) {
            if (
              data.emoji.id &&
              !emojis.find((e) => e.id === data.emoji?.id) &&
              !data.label
            ) {
              button.setEmoji({ name: "🌫️" });
            } else {
              button.setEmoji(data.emoji);
            }
          }
          if (data.style !== ButtonStyle.Premium && data.label) {
            button.setLabel(data.label);
          }
          if (
            component.data.style !== ButtonStyle.Link &&
            component.data.style !== ButtonStyle.Premium
          ) {
            const customId = `p_${component.id}`;
            button.setCustomId(customId);
          }
          row.addComponents(button);
        }
      }
      console.log("[migrating] Compiled rows");
      await ctx.rest.patch(
        // biome-ignore lint/style/noNonNullAssertion: Stopped if null
        Routes.webhookMessage(webhook.id, webhook.token!, message.id),
        {
          query: getWebhookThreadQuery(message),
          body: {
            components: rows.map((r) => r.toJSON()),
          } satisfies RESTPatchAPIWebhookWithTokenMessageJSONBody,
        },
      );
      console.log("[migrating] Updated message");

      // Clean up
      const insertedIds = inserted.map((i) => i.id);
      if (insertedIds.length !== 0) {
        await db
          .delete(discordMessageComponents)
          .where(
            and(
              eq(discordMessageComponents.messageId, BigInt(message.id)),
              notInArray(discordMessageComponents.id, insertedIds),
            ),
          );
      }
      console.log("[migrating] Cleaned up residue");

      await ctx.followup.editOriginalMessage({
        content: "Migrated successfully - enjoy!",
      });
      console.log("[migrating] End followup");
    },
  ];
};

export const migrateComponentsCancel: ButtonCallback = async (ctx) => {
  return ctx.updateMessage({
    content: "No changes have been made.",
    components: [],
  });
};

```

### File: `packages/bot/src/commands/components/quick.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  ModalBuilder,
  RoleSelectMenuBuilder,
  StringSelectMenuBuilder,
  StringSelectMenuOptionBuilder,
} from "@discordjs/builders";
import dedent from "dedent-js";
import {
  type APIButtonComponentWithCustomId,
  type APIGuild,
  type APIGuildMember,
  type APIMessageComponentEmoji,
  ButtonStyle,
  ComponentType,
  MessageFlags,
  Routes,
  TextInputStyle,
} from "discord-api-types/v10";
import { MessageFlagsBitField, PermissionFlags } from "discord-bitflag";
import { eq } from "drizzle-orm";
import {
  autoRollbackTx,
  backups,
  discordMessageComponents,
  type FlowAction,
  FlowActionCheckFunctionType,
  FlowActionSetVariableType,
  FlowActionType,
  generateId,
  getDb,
  makeSnowflake,
  type StorableButtonWithCustomIdResolved,
} from "store";
import type { ModalCallback, SelectMenuCallback } from "../../components.js";
import { getShareLink, getShareLinkExists } from "../../durable/share-links.js";
import type { InteractionContext } from "../../interactions.js";
import type { Env } from "../../types/env.js";
import { storeComponents } from "../../util/components.js";
import { getHighestRole } from "../reactionRoles.js";
import {
  type ComponentFlow,
  generateEditorTokenForComponent,
  getComponentFlowContainer,
  getEditorTokenComponentUrl,
} from "./add.js";

interface QuickButtonConfig {
  id: string;
  name: string;
  emoji: APIMessageComponentEmoji;
  build: (props: any) => FlowAction[];
}

export const quickButtonConfigs: QuickButtonConfig[] = [
  {
    id: "toggle-role",
    name: "Toggle Role",
    emoji: { name: "🏷️" },
    build(props: { roleId: string }) {
      const { roleId } = props;
      return [
        {
          type: FlowActionType.SetVariable,
          name: "roleId",
          value: roleId,
        },
        {
          type: FlowActionType.Check,
          function: {
            type: FlowActionCheckFunctionType.In,
            element: {
              varType: FlowActionSetVariableType.Get,
              value: "roleId",
            },
            array: {
              varType: FlowActionSetVariableType.Get,
              value: "member.role_ids",
            },
          },
          // biome-ignore lint/suspicious/noThenProperty: sorry! maybe we will rename this in a future version
          then: [
            {
              type: FlowActionType.RemoveRole,
              roleId,
            },
            {
              type: FlowActionType.Stop,
              message: {
                content: "Removed the <@&{roleId}> role from you.",
                flags: MessageFlags.Ephemeral,
              },
            },
          ],
          else: [
            {
              type: FlowActionType.AddRole,
              roleId,
            },
            {
              type: FlowActionType.Stop,
              message: {
                content: "Gave you the <@&{roleId}> role.",
                flags: MessageFlags.Ephemeral,
              },
            },
          ],
        },
      ];
    },
  },
  {
    id: "send-message",
    name: "Send Message",
    emoji: { name: "✉️" },
    build(props: { backupId: string; flags: MessageFlagsBitField }) {
      return [
        {
          type: FlowActionType.SendMessage,
          backupId: props.backupId,
          flags: Number(props.flags.value),
          response: true,
        },
      ];
    },
  },
];

export const addComponentQuickEntry: SelectMenuCallback = async (ctx) => {
  const value = ctx.interaction.data.values[0];
  // biome-ignore lint/style/noNonNullAssertion: Options generated from this array (except `_`)
  const config = quickButtonConfigs.find((c) => c.id === value)!;

  const state = ctx.state as ComponentFlow;
  state.steps = state.steps ?? [];

  if (value === "_") {
    state.stepTitle = "Finish on Discohook";
    state.steps.splice(
      1,
      1,
      { label: "Choose path (custom flow)" },
      {
        label:
          'Click "Customize" to set details and flows **<--- you are here**',
      },
      { label: 'Finish editing and click "Add Button" in the tab' },
    );
  } else {
    state.stepTitle = `Configure ${config.name}`;
    state.steps.splice(1, 1, {
      label: `Choose a quick setup (${config.name})`,
    });
  }

  const db = getDb(ctx.env.HYPERDRIVE);

  state.component = state.component ?? {
    type: ComponentType.Button,
    style: ButtonStyle.Primary,
    flow: { actions: [] },
    label: "Button",
  };

  const [component] = await db
    .insert(discordMessageComponents)
    .values({
      guildId: makeSnowflake(state.message.guildId),
      channelId: makeSnowflake(state.message.channelId),
      messageId: makeSnowflake(state.message.id),
      type: state.component.type,
      data: state.component,
      createdById: makeSnowflake(state.user.id),
      updatedById: makeSnowflake(state.user.id),
      draft: true,
    })
    .returning({
      id: discordMessageComponents.id,
    });
  state.componentId = String(component.id);

  const doId = ctx.env.DRAFT_CLEANER.idFromName(String(component.id));
  const stub = ctx.env.DRAFT_CLEANER.get(doId);
  const cleanerParams = new URLSearchParams({ id: String(component.id) });
  if (value !== "_") {
    // If we're not going to use the web flow, we don't need 2 weeks
    // for expiry in case the user backs out
    cleanerParams.set(
      "expires",
      new Date(new Date().getTime() + 86_400_000).toISOString(),
    );
  }
  await stub.fetch(`http://do/?${cleanerParams}`, { method: "GET" });

  switch (value) {
    case "_": {
      const editorToken = await generateEditorTokenForComponent(
        ctx.env,
        component.id,
        {
          user: {
            id: ctx.user.id,
            name: ctx.user.username,
            avatar: ctx.user.avatar,
          },
        },
      );

      const container = getComponentFlowContainer(state);
      container.addTextDisplayComponents((c) =>
        c.setContent(`-# ${ctx.t("componentWillExpire")}`),
      );
      return ctx.updateMessage({
        components: [
          container,
          new ActionRowBuilder<ButtonBuilder>().addComponents(
            new ButtonBuilder()
              .setLabel(ctx.t("customize"))
              .setStyle(ButtonStyle.Link)
              .setURL(getEditorTokenComponentUrl(editorToken, ctx.env)),
          ),
        ],
      });
    }
    case "toggle-role": {
      state.totalSteps = 5;
      if (!ctx.userPermissons.has(PermissionFlags.ManageRoles)) {
        return ctx.reply({
          content: "You need the **Manage Roles** permission",
          ephemeral: true,
        });
      }
      return ctx.updateMessage({
        components: [
          getComponentFlowContainer(state),
          new ActionRowBuilder<RoleSelectMenuBuilder>().addComponents(
            await storeComponents(ctx.env.KV, [
              new RoleSelectMenuBuilder().setPlaceholder(
                "Select or search for a role",
              ),
              {
                ...state,
                componentTimeout: 600,
                componentRoutingId: `add-component-quick-${value}`,
                componentOnce: false,
              },
            ]),
          ),
        ],
      });
    }
    case "send-message": {
      state.totalSteps = 6;
      state.stepTitle = "Set share link";
      state.step = 3;
      const modal = new ModalBuilder()
        .setTitle("Button message")
        .addLabelComponents((l) =>
          l
            .setLabel("Share Link")
            .setDescription(
              // Wish this could be more detailed but max length is 100
              // 'You can generate a share link at https://discohook.app. Compose or open the message data you would like to use in the Discohook editor, then press "Share" at the top left.',
              'Generate share links at discohook.app. Open the message you would like to use, then press "Share"',
            )
            .setTextInputComponent((b) =>
              b
                .setCustomId("share-link")
                .setStyle(TextInputStyle.Short)
                .setPlaceholder("https://discohook.app/?share=...")
                .setMaxLength(40)
                .setMinLength(30),
            ),
        );
      await storeComponents(ctx.env.KV, [
        modal,
        {
          ...state,
          componentTimeout: 600,
          componentRoutingId: `add-component-quick-${value}-modal`,
          componentOnce: false,
        },
      ]);

      return [
        ctx.modal(modal),
        async () => {
          await ctx.followup.editOriginalMessage({
            components: [
              getComponentFlowContainer(state),
              new ActionRowBuilder<ButtonBuilder>().addComponents(
                await storeComponents(ctx.env.KV, [
                  new ButtonBuilder()
                    .setStyle(ButtonStyle.Primary)
                    .setLabel("Open modal"),
                  {
                    ...state,
                    modal,
                    componentTimeout: 600,
                    componentRoutingId:
                      "add-component-flow-customize-modal-resend",
                    componentOnce: false,
                  },
                ]),
              ),
            ],
          });
        },
      ];
    }
    default:
      break;
  }

  return ctx.reply({
    content: "Unknown setup path",
    ephemeral: true,
  });
};

const getCustomButtonValuesModal = () =>
  new ModalBuilder()
    .setTitle("Custom button values")
    .addLabelComponents((l) =>
      l
        .setLabel("Label")
        .setDescription("The text displayed on this button.")
        .setTextInputComponent((b) =>
          b
            .setCustomId("label")
            .setStyle(TextInputStyle.Short)
            .setRequired(false)
            .setMaxLength(80),
        ),
    )
    .addLabelComponents((l) =>
      l
        .setLabel("Emoji")
        .setDescription("Like :smile: or a custom emoji in the server.")
        .setTextInputComponent((b) =>
          b
            .setCustomId("emoji")
            .setStyle(TextInputStyle.Short)
            .setRequired(false),
        ),
    )
    .addLabelComponents((l) =>
      l
        .setLabel("Disabled?")
        .setStringSelectMenuComponent((s) =>
          s
            .setCustomId("disabled")
            .addOptions(
              new StringSelectMenuOptionBuilder()
                .setLabel("True")
                .setValue("true")
                .setDescription("The button will not be clickable."),
              new StringSelectMenuOptionBuilder()
                .setLabel("False")
                .setValue("false")
                .setDescription("The button will be clickable (default)")
                .setDefault(true),
            ),
        ),
    );

export const addComponentSetStylePrompt = async (ctx: InteractionContext) => {
  const state = ctx.state as ComponentFlow;
  state.stepTitle = "Choose a button style";
  state.step += 1;

  return ctx.updateMessage({
    components: [
      getComponentFlowContainer(state),
      new ActionRowBuilder<StringSelectMenuBuilder>().addComponents(
        await storeComponents(ctx.env.KV, [
          new StringSelectMenuBuilder().addOptions(
            (
              [
                ButtonStyle.Primary,
                ButtonStyle.Secondary,
                ButtonStyle.Success,
                ButtonStyle.Danger,
              ] as const
            ).map((style) =>
              new StringSelectMenuOptionBuilder()
                .setLabel(
                  {
                    [ButtonStyle.Primary]: "Blurple",
                    [ButtonStyle.Secondary]: "Gray",
                    [ButtonStyle.Success]: "Green",
                    [ButtonStyle.Danger]: "Red",
                  }[style],
                )
                .setDescription(ButtonStyle[style])
                .setValue(String(style))
                .setEmoji({
                  name: {
                    [ButtonStyle.Primary]: "🟦",
                    [ButtonStyle.Secondary]: "⬜",
                    [ButtonStyle.Success]: "🟩",
                    [ButtonStyle.Danger]: "🟥",
                  }[style],
                }),
            ),
          ),
          {
            ...state,
            componentOnce: true,
            componentTimeout: 300,
            componentRoutingId: "add-component-quick-style",
          },
        ]),
      ),
    ],
  });
};

export const submitButtonQuickStyle: SelectMenuCallback = async (ctx) => {
  // const style = ctx.interaction.message.components?.[0].components.find(
  //   (c): c is APIButtonComponentWithCustomId =>
  //     c.type === ctx.interaction.data.component_type &&
  //     "custom_id" in c &&
  //     c.custom_id === ctx.interaction.data.custom_id,
  // )?.style;
  // if (style === undefined) {
  //   throw Error(
  //     "This should not happen unless this callback was assigned to the wrong component",
  //   );
  // }
  const state = ctx.state as ComponentFlow;
  if (!state.component) throw Error("state.component is missing");

  const style = Number(
    ctx.interaction.data.values[0],
  ) as APIButtonComponentWithCustomId["style"];
  (state.component as unknown as APIButtonComponentWithCustomId).style = style;

  state.stepTitle = "Customize button details";
  state.steps = state.steps ?? [];
  state.steps.push({
    label: `Select style (${ButtonStyle[style].toLowerCase()})`,
  });

  const modal = getCustomButtonValuesModal();
  await storeComponents(ctx.env.KV, [
    modal,
    {
      ...state,
      componentTimeout: 600,
      componentRoutingId: "add-component-flow-customize-modal",
      componentOnce: false,
    },
  ]);

  return [
    ctx.modal(modal),
    async () => {
      await ctx.followup.editOriginalMessage({
        components: [
          getComponentFlowContainer(state),
          new ActionRowBuilder<ButtonBuilder>().addComponents(
            await storeComponents(ctx.env.KV, [
              new ButtonBuilder()
                .setStyle(ButtonStyle.Primary)
                .setLabel("Open modal"),
              {
                componentRoutingId: "add-component-flow-customize-modal-resend",
                componentTimeout: 600,
                modal: modal.toJSON(),
              },
            ]),
          ),
        ],
      });
    },
  ];
};

export const addComponentQuickToggleRoleCallback: SelectMenuCallback = async (
  ctx,
) => {
  const value = ctx.interaction.data.values[0];
  // biome-ignore lint/style/noNonNullAssertion: Options generated from this array
  const config = quickButtonConfigs.find((c) => c.id === "toggle-role")!;

  const guildId = ctx.interaction.guild_id;
  if (!guildId) throw Error("Guild-only");

  const { roles, owner_id } = (await ctx.rest.get(
    Routes.guild(guildId),
  )) as APIGuild;
  const role = roles.find((r) => r.id === value);
  if (!role) {
    return ctx.reply({
      content:
        "The role could not be found. Please choose a different one or try restarting Discord.",
      ephemeral: true,
    });
  }
  if (role.managed) {
    return ctx.reply({
      content: `<@&${role.id}> can't be assigned to members.`,
      ephemeral: true,
    });
  }

  const me = (await ctx.rest.get(
    Routes.guildMember(guildId, ctx.env.DISCORD_APPLICATION_ID),
  )) as APIGuildMember;
  const botHighestRole = getHighestRole(roles, me.roles);
  if (owner_id !== ctx.env.DISCORD_APPLICATION_ID) {
    // You could be running an instance of this bot where
    // the bot is the owner of the guild
    if (!botHighestRole) {
      return ctx.reply({
        content: `I can't assign <@&${role.id}> to members because I don't have any roles.`,
        ephemeral: true,
      });
    } else if (botHighestRole && role.position >= botHighestRole.position) {
      return ctx.reply({
        content: `<@&${role.id}> is higher than my highest role (<@&${botHighestRole.id}>), so I can't assign it to members. <@&${role.id}> needs to be lower in the role list, or my highest role needs to be higher.`,
        ephemeral: true,
      });
    }
  }
  // biome-ignore lint/style/noNonNullAssertion: guild-only
  const member = ctx.interaction.member!;
  const memberHighestRole = getHighestRole(roles, member.roles);
  if (owner_id !== ctx.user.id) {
    // Guild owner can always do everything
    if (!memberHighestRole) {
      // This message should never be seen unless someone messes with permissions
      return ctx.reply({
        content: `You can't assign <@&${role.id}> to members because you don't have any roles.`,
        ephemeral: true,
      });
    } else if (
      memberHighestRole &&
      role.position >= memberHighestRole.position
    ) {
      return ctx.reply({
        content: `<@&${role.id}> is higher than your highest role (<@&${memberHighestRole.id}>), so you can't select it to be assigned to members. <@&${role.id}> needs to be lower in the role list, or your highest role needs to be higher.`,
        ephemeral: true,
      });
    }
  }

  const state = ctx.state as ComponentFlow;
  state.step = 4;
  state.steps = state.steps ?? [];
  state.steps.push({ label: `Select role (<@&${role.id}>)` });

  const component = state.component;
  const componentId = state.componentId;
  if (componentId === undefined || !component) {
    return ctx.reply({
      content:
        "Sorry, we're missing some required state and cannot continue. Try restarting this action.",
      ephemeral: true,
    });
  }

  return [
    ctx.defer(),
    async () => {
      const actions = config.build({ roleId: role.id });
      if (
        // Shouldn't actually be necessary
        component.type === ComponentType.Button &&
        component.style !== ButtonStyle.Link &&
        component.style !== ButtonStyle.Premium
      ) {
        component.flow.actions = actions;

        const db = getDb(ctx.env.HYPERDRIVE);
        await db
          .update(discordMessageComponents)
          .set({ data: component })
          .where(eq(discordMessageComponents.id, BigInt(componentId)));
      }

      const response = await addComponentSetStylePrompt(ctx);
      // biome-ignore lint/style/noNonNullAssertion: returns an updateMessage()
      await ctx.followup.editOriginalMessage(response.data!);
    },
  ];
};

export const parseShareLink = async (env: Env, raw: string) => {
  const invalidShareLinkMessage = `Invalid share link. They look like this: \`${env.DISCOHOOK_ORIGIN}/?share=...\``;
  let shareUrl: URL;
  try {
    shareUrl = new URL(raw);
  } catch {
    throw Error(invalidShareLinkMessage);
  }
  const shareId = shareUrl.searchParams.get("share");
  if (shareUrl.origin !== env.DISCOHOOK_ORIGIN || !shareId) {
    if (shareUrl.host === "share.discohook.app") {
      throw Error(dedent`
        This is an old-style share link. You must use a share link created on <${env.DISCOHOOK_ORIGIN}>. They look like this: \`${env.DISCOHOOK_ORIGIN}/?share=...\`

        -# TIP: Just [open the share link](${shareUrl.href}), change the address from \`discohook.org\` to \`discohook.app\`, then press "Share" again to generate a new link.
      `);
    }
    throw Error(invalidShareLinkMessage);
  }

  if (!(await getShareLinkExists(env, shareId))) {
    throw Error(
      "Share link does not exist. Keep in mind that they expire after a week by default.",
    );
  }
  return shareId;
};

export const addComponentQuickSendMessageCallback: ModalCallback = async (
  ctx,
) => {
  const guildId = ctx.interaction.guild_id;
  if (!guildId) throw Error("Guild-only");

  let shareId: string;
  try {
    shareId = await parseShareLink(
      ctx.env,
      ctx.getModalComponent("share-link").value,
    );
  } catch (e) {
    return ctx.reply({ content: String(e), flags: MessageFlags.Ephemeral });
  }

  const state = ctx.state as ComponentFlow;
  state.steps?.push({
    label: `Set share link ([${shareId}](${ctx.env.DISCOHOOK_ORIGIN}/?share=${shareId}))`,
  });
  state.stepTitle = "Set visibility";
  state.step += 1;

  return ctx.updateMessage({
    components: [
      getComponentFlowContainer(state),
      new ActionRowBuilder<StringSelectMenuBuilder>().addComponents(
        await storeComponents(ctx.env.KV, [
          new StringSelectMenuBuilder()
            .setPlaceholder("Select whether the message should be hidden")
            .addOptions(
              new StringSelectMenuOptionBuilder()
                .setValue("0")
                .setLabel("Public")
                .setEmoji({ name: "🦺" })
                .setDescription(
                  "The message is visible to everyone in the channel",
                ),
              new StringSelectMenuOptionBuilder()
                .setValue(String(MessageFlags.Ephemeral))
                .setLabel("Hidden")
                .setEmoji({ name: "😶‍🌫️" })
                .setDescription(
                  "Only the person who pressed the button can see the message",
                ),
            ),
          {
            ...state,
            shareId,
            componentRoutingId: "add-component-quick-send-message-visibility",
            componentTimeout: 600,
            componentOnce: true,
          },
        ]),
      ),
    ],
  });
};

export const addComponentQuickSendMessageVisibilityCallback: SelectMenuCallback =
  async (ctx) => {
    const guildId = ctx.interaction.guild_id;
    if (!guildId) throw Error("Guild-only");

    const flags = new MessageFlagsBitField(
      Number(ctx.interaction.data.values[0]),
    );

    const { shareId, ...state } = ctx.state as ComponentFlow & {
      shareId: string;
    };

    const componentId = state.componentId;
    const component = state.component as StorableButtonWithCustomIdResolved;
    if (componentId === undefined || !component) {
      return ctx.reply({
        content:
          "Sorry, we're missing some required state and cannot continue. Try restarting this action.",
        ephemeral: true,
      });
    }

    return [
      ctx.defer(),
      async () => {
        const { data } = await getShareLink(ctx.env, shareId);

        // biome-ignore lint/style/noNonNullAssertion: Options generated from this array
        const config = quickButtonConfigs.find((c) => c.id === "send-message")!;
        const backupId = generateId();
        const backupName = `Button in #${
          ctx.interaction.channel.name ?? "unknown"
        } (share ${shareId})`.slice(0, 100);

        const actions = config.build({ flags, backupId });
        component.flow.actions = actions;

        const db = getDb(ctx.env.HYPERDRIVE);
        await db.transaction(
          autoRollbackTx(async (tx) => {
            await tx.insert(backups).values({
              id: BigInt(backupId),
              ownerId: BigInt(state.user.id),
              name: backupName,
              dataVersion: "d2",
              data,
            });
            await tx
              .update(discordMessageComponents)
              .set({ data: component })
              .where(eq(discordMessageComponents.id, BigInt(componentId)));
          }),
        );

        state.steps?.splice(
          // Remove share link step and replace it with editable backup link now
          // that we have fetched the data and created the backup
          state.steps.length - 1,
          1,
          {
            label: `Set [message data](${ctx.env.DISCOHOOK_ORIGIN}/?backup=${backupId} "${backupName}") (${shareId})`,
          },
          {
            label: `Set message visibility (${
              flags.has(MessageFlags.Ephemeral) ? "hidden" : "public"
            })`,
          },
        );
        state.stepTitle = "Set visibility";
        state.step += 1;

        const response = await addComponentSetStylePrompt(ctx);
        // biome-ignore lint/style/noNonNullAssertion: returns an updateMessage()
        await ctx.followup.editOriginalMessage(response.data!);
      },
    ];
  };

```

### File: `packages/bot/src/commands/debug.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  ContainerBuilder,
  messageLink,
  StringSelectMenuBuilder,
  StringSelectMenuOptionBuilder,
} from "@discordjs/builders";
import dedent from "dedent-js";
import {
  type APIEmoji,
  type APIGuildMember,
  type APIGuildTextChannel,
  type APIMessage,
  type APIMessageApplicationCommandGuildInteraction,
  type APIWebhook,
  ButtonStyle,
  type ChannelType,
  ComponentType,
  OverwriteType,
  type RESTGetAPIGuildMemberResult,
  type RESTGetAPIGuildRolesResult,
  Routes,
} from "discord-api-types/v10";
import { PermissionFlags, PermissionsBitField } from "discord-bitflag";
import { eq } from "drizzle-orm";
import {
  autoRollbackTx,
  discordMessageComponents,
  type DraftComponent,
  getchTriggerGuild,
  getDb,
  launchComponentKV,
  makeSnowflake,
  type StorableButtonWithUrl,
  type TriggerKVGuild,
  upsertDiscordUser,
} from "store";
import type { MessageAppCommandCallback } from "../commands.js";
import type {
  AutoComponentCustomId,
  ButtonCallback,
  SelectMenuCallback,
} from "../components.js";
import type { InteractionContext } from "../interactions.js";
import {
  onlyActionRows,
  parseAutoComponentId,
  textDisplay,
} from "../util/components.js";
import { MAX_SELECT_OPTIONS } from "../util/constants.js";
import { boolEmoji, color } from "../util/meta.js";
import { extractComponentByPath } from "./components/delete.js";
import { ensureValidEmoji, getComponentsAsV2Menu } from "./components/edit.js";
import { getWebhookMessage } from "./components/entry.js";
import { isSnowflakeSafe } from "./reactionRoles.js";

const getMessageDebugContainers = async (
  ctx: InteractionContext<APIMessageApplicationCommandGuildInteraction>,
  message: APIMessage,
) => {
  let webhook: APIWebhook | undefined;
  if (message.webhook_id) {
    try {
      webhook = (await ctx.rest.get(
        Routes.webhook(message.webhook_id),
      )) as APIWebhook;
    } catch {}
  }

  const guildId = ctx.interaction.guild_id;
  const container = new ContainerBuilder()
    .setAccentColor(color)
    .addTextDisplayComponents(
      textDisplay(
        `### Message Debug for ${messageLink(
          message.channel_id,
          message.id,
          guildId,
        )}`,
      ),
    );

  const [roles, channel] = await Promise.all([
    (async () => {
      try {
        return (await ctx.rest.get(
          Routes.guildRoles(guildId),
        )) as RESTGetAPIGuildRolesResult;
      } catch {}
    })(),
    ctx.rest.get(
      Routes.channel(webhook?.channel_id ?? ctx.interaction.channel.id),
    ) as Promise<
      APIGuildTextChannel<
        | ChannelType.GuildText
        | ChannelType.GuildVoice
        | ChannelType.GuildAnnouncement
        | ChannelType.GuildForum
        | ChannelType.GuildMedia
      >
    >,
  ]);

  let guildPerm = new PermissionsBitField();
  let channelAllow = new PermissionsBitField();
  const channelDeny = new PermissionsBitField();

  // calculate for user (webhook owner if bot, else direct author)
  if (webhook?.user?.bot || !message.webhook_id) {
    const userId = webhook?.user?.bot ? webhook.user.id : message.author.id;

    let member: APIGuildMember | undefined;
    if (
      webhook?.user?.bot &&
      webhook.application_id === ctx.interaction.application_id
    ) {
      member = ctx.interaction.member;
      channelAllow = ctx.appPermissons;
    } else if (userId === ctx.user.id) {
      member = ctx.interaction.member;
      channelAllow = ctx.userPermissons;
    }
    if (!member) {
      // must exist because webhooks are removed if the bot is removed, and
      // oauth webhooks have the `user` of the user who authorized.
      // TODO: what permissions do oauth webhooks inherit?
      member = (await ctx.rest.get(
        Routes.guildMember(guildId, userId),
      )) as RESTGetAPIGuildMemberResult;
    }
    if (roles) {
      for (const roleId of member.roles) {
        const role = roles.find((r) => r.id === roleId);
        if (!role) continue;

        guildPerm.add(BigInt(role.permissions));
      }
    }
    if (channelAllow.value !== 0n) {
      for (const override of channel.permission_overwrites ?? []) {
        switch (override.type) {
          case OverwriteType.Member:
            if (override.id === userId) {
              channelAllow.add(BigInt(override.allow));
              channelDeny.add(BigInt(override.deny));
            }
            break;
          case OverwriteType.Role:
            if (member.roles.includes(override.id)) {
              channelAllow.add(BigInt(override.allow));
              channelDeny.add(BigInt(override.deny));
            }
            break;
          default:
            break;
        }
      }
    }
  }
  // calculate for @everyone (if webhook)
  if (message.webhook_id) {
    // Disregard the webhook owner in favor of @everyone if they are a human,
    // but not if they are a bot
    const everyoneRole = roles?.find((r) => r.id === guildId);
    if (everyoneRole) {
      if (webhook?.user?.bot) {
        guildPerm.add(BigInt(everyoneRole.permissions));
      } else {
        guildPerm = new PermissionsBitField(BigInt(everyoneRole.permissions));
      }
    }
    for (const override of channel.permission_overwrites ?? []) {
      if (override.type === OverwriteType.Role && override.id === guildId) {
        channelAllow.add(BigInt(override.allow));
        channelDeny.add(BigInt(override.deny));
      }
    }
  }
  const hasGuildExtEmoji = guildPerm.has(PermissionFlags.UseExternalEmojis);
  const hasChannelExtEmoji = channelDeny.has(PermissionFlags.UseExternalEmojis)
    ? false
    : channelAllow.has(PermissionFlags.UseExternalEmojis)
      ? true
      : null;

  container
    .addTextDisplayComponents(
      textDisplay(dedent`
        **Emojis**
        Permissions for this message inherit from ${
          webhook?.user?.bot
            ? `<@${webhook.user.id}> and @everyone`
            : message.webhook_id
              ? "@everyone"
              : `<@${message.author.id}>`
        }`),
    )
    .addSeparatorComponents((s) => s.setDivider())
    .addTextDisplayComponents(
      textDisplay(dedent`
        ${boolEmoji(true)} Use this server's emojis
        ${boolEmoji(hasGuildExtEmoji)} Use external emojis (server)
        ${boolEmoji(hasChannelExtEmoji)} Use external emojis (channel)
        ${(hasChannelExtEmoji === null ? hasGuildExtEmoji : hasChannelExtEmoji) ? "Looks good! If you just updated permissions, try sending the message again." : ""}
      `),
    )
    .addSeparatorComponents((s) => s.setDivider());

  const threadId = message.position === undefined ? "" : message.channel_id;
  if (
    message.components &&
    webhook?.application_id === ctx.interaction.application_id
  ) {
    const interactive = onlyActionRows(message.components, true, true)
      .flatMap((r) => r.components)
      .filter(
        (c) =>
          c.type !== ComponentType.Button ||
          (c.style !== ButtonStyle.Link && c.style !== ButtonStyle.Premium),
      );
    if (interactive.length !== 0) {
      container
        .addSectionComponents((s) =>
          s
            .addTextDisplayComponents(
              textDisplay(dedent`
                **Components**
                ${interactive.length} on this message ${interactive.length === 1 ? "is" : "are"} interactive
              `),
            )
            .setButtonAccessory(
              new ButtonBuilder()
                .setCustomId(
                  `a_debug-component-flow_${message.webhook_id}:${message.id}:${threadId}` satisfies AutoComponentCustomId,
                )
                .setLabel("Debug Components")
                .setStyle(ButtonStyle.Primary),
            ),
        )
        .addSeparatorComponents((s) => s.setDivider());
    }
  }

  container.addTextDisplayComponents(
    textDisplay(
      `-# ID: ${message.id}\n-# Flags: ${message.flags?.toString() ?? 0}`,
    ),
  );
  return [container];
};

export const debugMessageCallback: MessageAppCommandCallback<
  APIMessageApplicationCommandGuildInteraction
> = async (ctx) => {
  const message = ctx.getMessage();
  return ctx.reply({
    components: await getMessageDebugContainers(ctx, message),
    ephemeral: true,
    componentsV2: true,
    allowedMentions: { parse: [] },
  });
};

// This is a separate callback instead of being affixed to debugMessageCallback
// because of the components per message limit.
export const debugComponentFlowPickerCallback: ButtonCallback<true> = async (
  ctx,
) => {
  const {
    webhookId,
    messageId,
    threadId: threadId_,
  } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "webhookId",
    "messageId",
    "threadId",
  );
  const threadId = threadId_ || undefined;

  if (
    !ctx.userPermissons.has(
      PermissionFlags.ManageWebhooks,
      PermissionFlags.ManageMessages,
    )
  ) {
    return ctx.reply({
      content:
        "You need the Manage Webhooks and Manage Messages permissions to modify components.",
      ephemeral: true,
    });
  }

  const { message, webhook } = await getWebhookMessage(
    ctx.env,
    webhookId,
    messageId,
    threadId,
    ctx.rest,
  );

  const guildId = ctx.interaction.guild_id;
  if (webhook.guild_id !== guildId) {
    return ctx.reply({ content: "Server ID mismatch", ephemeral: true });
  }
  if (webhook.application_id !== ctx.interaction.application_id) {
    return ctx.reply({
      content: "This webhook is not owned by Discohook",
      ephemeral: true,
    });
  }

  const menu = getComponentsAsV2Menu(message.components ?? [], [], {
    getSelectCustomId: (index: number) =>
      `a_debug-component-flow-pick_${message.webhook_id}:${message.id}:${threadId}:${index}` satisfies AutoComponentCustomId,
  });
  menu.splice(
    0,
    0,
    textDisplay(dedent`
      **Components**
      Select one to debug.
    `).toJSON(),
  );

  return ctx.updateMessage({
    components: menu,
    allowedMentions: { parse: [] },
  });
};

export const debugComponentFlowPickCallback: SelectMenuCallback<true> = async (
  ctx,
) => {
  const {
    webhookId,
    messageId,
    threadId: threadId_,
  } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "webhookId",
    "messageId",
    "threadId",
  );
  const threadId = threadId_ || undefined;

  const db = getDb(ctx.env.HYPERDRIVE);
  let component:
    | {
        id: bigint;
        data: DraftComponent;
        createdBy: { discordId: bigint | null } | null;
        updatedBy: { discordId: bigint | null } | null;
      }
    | undefined;

  const [scope, key] = ctx.interaction.data.values[0].split(":");
  switch (scope as "id" | "link" | "unknown") {
    case "id": {
      const id = BigInt(key);
      const dbComponent = await db.query.discordMessageComponents.findFirst({
        where: (table, { eq }) => eq(table.id, id),
        columns: {
          id: true,
          data: true,
          guildId: true,
          messageId: true,
        },
        with: {
          createdBy: { columns: { discordId: true } },
          updatedBy: { columns: { discordId: true } },
        },
      });
      if (
        !dbComponent ||
        dbComponent.guildId?.toString() !== ctx.interaction.guild_id ||
        (dbComponent.messageId !== null &&
          dbComponent.messageId?.toString() !== messageId)
      ) {
        return ctx.updateMessage({
          components: [textDisplay("Unknown component")],
        });
      }
      component = dbComponent;
      break;
    }
    case "link": {
      const path = key.split(".").map(Number);
      const { message } = await getWebhookMessage(
        ctx.env,
        webhookId,
        messageId,
        threadId,
        ctx.rest,
      );
      const foundComponent = extractComponentByPath(message, path);
      if (
        !foundComponent ||
        foundComponent.type !== ComponentType.Button ||
        foundComponent.style !== ButtonStyle.Link
      ) {
        return ctx.updateMessage({
          components: [
            textDisplay("The button could not be located in the message."),
          ],
        });
      }

      const dbComponents = await db.query.discordMessageComponents.findMany({
        where: (table, { eq, and }) =>
          and(
            eq(table.messageId, BigInt(messageId)),
            eq(table.type, ComponentType.Button),
          ),
        columns: { id: true, data: true },
        with: {
          createdBy: { columns: { discordId: true } },
          updatedBy: { columns: { discordId: true } },
        },
      });
      component = dbComponents.find(
        (c) =>
          c.data.type === ComponentType.Button &&
          c.data.style === ButtonStyle.Link &&
          c.data.url === foundComponent.url,
      );
      if (!component) {
        const user = await upsertDiscordUser(db, ctx.user);
        const [dbComponent] = await db
          .insert(discordMessageComponents)
          .values({
            channelId: makeSnowflake(message.channel_id),
            messageId: makeSnowflake(message.id),
            guildId: makeSnowflake(ctx.interaction.guild_id),
            type: ComponentType.Button,
            data: foundComponent satisfies StorableButtonWithUrl,
            createdById: user.id,
          })
          .returning({ id: discordMessageComponents.id });
        component = {
          ...dbComponent,
          data: foundComponent,
          createdBy: user,
          updatedBy: user,
        };
      }

      break;
    }
    default:
      break;
  }

  if (!component) {
    // As far as we know, this component doesn't actually exist anymore
    return ctx.reply({
      components: [
        textDisplay("Cannot resolve that component from the database."),
      ],
      ephemeral: true,
      componentsV2: true,
    });
  }

  const responsibleId = (
    component.updatedBy?.discordId ?? component.createdBy?.discordId
  )?.toString();

  const [guild, emojis, responsible] = await Promise.all([
    // currently we only really need this for owner_id, but unfortunately
    // interaction.guild doesn't provide that
    getchTriggerGuild(ctx.rest, ctx.env, ctx.interaction.guild_id),
    (async (): Promise<APIEmoji[]> => {
      if ("flows" in component.data) {
        try {
          return (await ctx.rest.get(
            Routes.guildEmojis(ctx.interaction.guild_id),
          )) as APIEmoji[];
        } catch {}
      }
      return [];
    })(),
    (async () => {
      if (responsibleId) {
        try {
          return (await ctx.rest.get(
            Routes.guildMember(ctx.interaction.guild_id, responsibleId),
          )) as APIGuildMember;
        } catch {
          return null;
        }
      }
      return undefined;
    })(),
  ]);

  const container = new ContainerBuilder()
    .setAccentColor(color)
    .addTextDisplayComponents(
      textDisplay(dedent`
        ### ${ComponentType[component.data.type]
          .replace(/([a-z])([A-Z])/g, "$1 $2")
          .trim()} on ${messageLink(
          ctx.interaction.channel.id,
          messageId,
          ctx.interaction.guild_id,
        )}
        Responsible user: ${
          responsible
            ? `<@${responsible.user.id}> (${responsible.user.username})`
            : responsible === null
              ? "not found in the server"
              : "indeterminable (nothing stored for this component)"
        }

      `),
    );
  // .addSeparatorComponents((s) => s.setDivider());

  const row = new ActionRowBuilder<ButtonBuilder>().addComponents(
    new ButtonBuilder()
      .setCustomId(
        `a_debug-component-take_${component.id}` satisfies AutoComponentCustomId,
      )
      .setLabel("Take Responsibility")
      .setStyle(ButtonStyle.Secondary),
  );
  container.addActionRowComponents(row);
  if (ctx.user.id !== guild.owner_id) {
    const btn = row.components[0] as ButtonBuilder;
    btn.setDisabled(true);
    btn.setLabel("Take Responsibility (owner only)");
  }

  if ("flows" in component.data) {
    const options = component.data.options
      .map((option) => {
        return new StringSelectMenuOptionBuilder({
          ...option,
          emoji: ensureValidEmoji(option.emoji, emojis),
          default: false,
        });
      })
      .slice(0, MAX_SELECT_OPTIONS);

    container
      // .addTextDisplayComponents(textDisplay("Test Flow"))
      .addActionRowComponents((r) =>
        r.addComponents(
          new StringSelectMenuBuilder()
            .setCustomId(`DBG_p_${component.id}`)
            .setPlaceholder("Test Option Flow")
            .addOptions(options)
            .setMaxValues(1),
        ),
      );
  } else {
    row.addComponents(
      new ButtonBuilder()
        .setCustomId(`DBG_p_${component.id}`)
        .setLabel("Test Flow")
        .setStyle(ButtonStyle.Secondary),
    );
  }

  return ctx.updateMessage({
    components: [container],
    allowedMentions: { parse: [] },
  });
};

export const debugComponentFlowTakeResponsibilityCallback: ButtonCallback<
  true
> = async (ctx) => {
  const { componentId } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "componentId",
  );
  if (!isSnowflakeSafe(componentId)) {
    return ctx.reply({ content: "Invalid ID", ephemeral: true });
  }
  if (
    !ctx.userPermissons.has(
      PermissionFlags.ManageWebhooks,
      PermissionFlags.ManageMessages,
    )
  ) {
    return ctx.reply({
      content:
        "You need the Manage Webhooks and Manage Messages permissions to modify this component.",
      ephemeral: true,
    });
  }

  const db = getDb(ctx.env.HYPERDRIVE);
  const component = await db.query.discordMessageComponents.findFirst({
    where: (table, { eq }) => eq(table.id, BigInt(componentId)),
    columns: {
      id: true,
      data: true,
      guildId: true,
      channelId: true,
      createdById: true,
    },
  });
  if (
    !component ||
    component.channelId?.toString() !== ctx.interaction.channel.id
  ) {
    return ctx.updateMessage({
      components: [textDisplay("Unknown component or channel mismatch")],
    });
  }

  return [
    ctx.defer({ ephemeral: true, thinking: true, componentsV2: true }),
    async () => {
      await db.transaction(
        autoRollbackTx(async (tx) => {
          let dbUser = await tx.query.users.findFirst({
            where: (users, { eq }) => eq(users.discordId, BigInt(ctx.user.id)),
            columns: { id: true },
          });
          if (!dbUser) dbUser = await upsertDiscordUser(tx, ctx.user);

          await tx
            .update(discordMessageComponents)
            .set({ updatedById: dbUser.id })
            .where(eq(discordMessageComponents.id, BigInt(componentId)));
        }),
      );

      let guild: Pick<TriggerKVGuild, "_roles">;
      try {
        guild = await getchTriggerGuild(
          ctx.rest,
          ctx.env,
          ctx.interaction.guild_id,
        );
      } catch {
        guild = { _roles: [] };
      }
      // Doing this instead of using ctx.userPermissions because that is for
      // the current channel, not the guild
      const permissions = new PermissionsBitField();
      for (const roleId of ctx.interaction.member.roles) {
        const role = guild._roles?.find((r) => r.id === roleId);
        if (!role) continue;
        permissions.add(BigInt(role.permissions));
      }
      await launchComponentKV(ctx.env, {
        componentId,
        db,
        data: component.data,
        guildId: component.guildId?.toString(),
        channelId: component.channelId?.toString(),
        createdById: component.createdById?.toString(),
        responsibleUser: {
          id: ctx.user.id,
          username: ctx.user.username,
          roles: ctx.interaction.member.roles,
          guild_permissions: permissions.value.toString(),
          reason: "took responsibility with debug command",
        },
      });

      await ctx.followup.send({
        components: [
          textDisplay(
            "Updated the component. You are now the responsible user until someone else edits it.",
          ),
        ],
        componentsV2: true,
      });
    },
  ];
};

```

### File: `packages/bot/src/commands/deluxe.ts`
```ts
import { ActionRowBuilder, ButtonBuilder } from "@discordjs/builders";
import { TimestampStyles, time } from "@discordjs/formatters";
import { ButtonStyle } from "discord-api-types/v10";
import { eq } from "drizzle-orm";
import { getDb, upsertDiscordUser, users } from "store";
import type { ChatInputAppCommandCallback } from "../commands.js";

export const deluxeInfoCallback: ChatInputAppCommandCallback = async (ctx) => {
  const components = [
    new ActionRowBuilder<ButtonBuilder>().addComponents(
      ctx.env.PREMIUM_SKUS.map((sku_id) =>
        new ButtonBuilder().setStyle(ButtonStyle.Premium).setSKUId(sku_id),
      ),
    ),
  ];
  return ctx.reply({
    content: `Learn about Discohook Deluxe here: <${ctx.env.DISCOHOOK_ORIGIN}/donate>`,
    components,
    ephemeral: true,
  });
};

export const deluxeSyncCallback: ChatInputAppCommandCallback = async (ctx) => {
  const db = getDb(ctx.env.HYPERDRIVE);
  const user = await upsertDiscordUser(db, ctx.user);

  // Make sure we don't accidentally do this for users if we ever introduce a guild-level subscription
  const { premium } = ctx;
  await db
    .update(users)
    .set({
      subscribedSince: premium.subscribedAt ?? null,
      firstSubscribed: user.firstSubscribed ? undefined : premium.subscribedAt,
      subscriptionExpiresAt: user.subscriptionExpiresAt ?? null,
      lifetime: user.lifetime ?? premium.lifetime,
    })
    .where(eq(users.id, user.id));

  return ctx.reply({
    content: `Synced successfully: ${
      (user.lifetime ?? premium.lifetime)
        ? "You have a lifetime subscription."
        : premium.grace && premium.graceEndsAt
          ? `You can access your Deluxe subscription until ${time(
              premium.graceEndsAt,
              TimestampStyles.LongDate,
            )} (expired ${
              premium.endsAt
                ? time(premium.endsAt, TimestampStyles.RelativeTime)
                : ""
            }).`
          : premium.active
            ? `You have an active Deluxe subscription until ${
                premium.endsAt
                  ? time(premium.endsAt, TimestampStyles.LongDate)
                  : "unknown"
              }${
                premium.purchased
                  ? ", with an eligible grace period of 3 days."
                  : ""
              }.`
            : "You do not have an active Deluxe subscription."
    }`,
    ephemeral: true,
  });
};

```

### File: `packages/bot/src/commands/emojis.ts`
```ts
import type { Env } from "../types/env.js";

type EmojiDataEntry = [
  string | [string, string] | [string, string, string],
  ...([string, number] | string)[],
];

type EmojiData = EmojiDataEntry[];

const diversities = [
  {
    value: "\u{1f3fb}",
    classic: "skin-tone-1",
    numbered: "_tone1",
    named: "_light_skin_tone",
  },
  {
    value: "\u{1f3fc}",
    classic: "skin-tone-2",
    numbered: "_tone2",
    named: "_medium_light_skin_tone",
  },
  {
    value: "\u{1f3fd}",
    classic: "skin-tone-3",
    numbered: "_tone3",
    named: "_medium_skin_tone",
  },
  {
    value: "\u{1f3fe}",
    classic: "skin-tone-4",
    numbered: "_tone4",
    named: "_medium_dark_skin_tone",
  },
  {
    value: "\u{1f3ff}",
    classic: "skin-tone-5",
    numbered: "_tone5",
    named: "_dark_skin_tone",
  },
];

const bitflag = {
  classic: 1 << 0,
  numbered: 1 << 1,
  named: 1 << 2,
  multiNumbered: 1 << 3,
  multiNamed: 1 << 4,
  diverseOnly: 1 << 5,
};

export const fetchEmojiData = async (env: Env) => {
  const response = await env.SITE.fetch("http://localhost/emoji.json", {
    method: "GET",
  });
  return (await response.json()) as EmojiData;
};

export const resolveEmojiData = (rawEmojiData: EmojiData) => {
  const nameToEmojiMap = new Map<string, string>();
  const emojiToNameMap = new Map<string, string>();

  function insertEmoji(emoji: string, name: string) {
    nameToEmojiMap.set(name, emoji);
    if (!emojiToNameMap.has(emoji)) {
      emojiToNameMap.set(emoji, name);
    }
    if (!emoji.includes("\u200d")) {
      const cleaned = emoji.replace("\ufe0f", "");
      if (!emojiToNameMap.has(cleaned)) {
        emojiToNameMap.set(cleaned, name);
      }
    }
  }

  for (const [emojiDescriptor, ...names] of rawEmojiData) {
    const [emoji, diverseTemplate, multiDiverseTemplate] = [emojiDescriptor]
      .flat()
      .map((it) => it.replaceAll("!", "\u200d"));

    for (const nameDescriptor of names) {
      const [nameTemplate, flags] =
        typeof nameDescriptor === "string"
          ? [nameDescriptor, 0]
          : nameDescriptor;

      const name = nameTemplate.replace("@", "");
      insertEmoji(emoji, name);

      if (diverseTemplate) {
        for (const diversity of diversities) {
          const emoji = diverseTemplate.replaceAll("?", diversity.value);

          if (flags & bitflag.classic) {
            nameToEmojiMap.set(`${name}::${diversity.classic}`, emoji);
          }
          if (flags & bitflag.numbered) {
            insertEmoji(emoji, nameTemplate.replace(/@|$/, diversity.numbered));
          }
          if (flags & bitflag.named) {
            insertEmoji(emoji, nameTemplate.replace(/@|$/, diversity.named));
          }
        }
      }

      if (multiDiverseTemplate) {
        for (const first of diversities) {
          for (const second of diversities) {
            if (first.value === second.value) {
              continue;
            }

            const emoji = multiDiverseTemplate
              .replace("?", first.value)
              .replace("?", second.value);

            if (flags & bitflag.numbered) {
              insertEmoji(
                emoji,
                nameTemplate.replace(/@|$/, first.numbered + second.numbered),
              );
            }
            if (flags & bitflag.named) {
              insertEmoji(
                emoji,
                nameTemplate.replace(/@|$/, first.named + second.named),
              );
            }
          }
        }
      }
    }
  }

  for (const diversity of diversities) {
    insertEmoji(diversity.value, diversity.classic);
  }

  return {
    nameToEmoji: nameToEmojiMap,
    emojiToName: emojiToNameMap,
  };
};

```

### File: `packages/bot/src/commands/format.ts`
```ts
import { EmbedBuilder } from "@discordjs/builders";
import dedent from "dedent-js";
import {
  type APIChatInputApplicationCommandInteraction,
  type APIPartialEmoji,
  type APIRole,
  FormattingPatterns,
} from "discord-api-types/v10";
import type { ChatInputAppCommandCallback } from "../commands.js";
import type { InteractionContext } from "../interactions.js";
import { color } from "../util/meta.js";
import { fetchEmojiData, resolveEmojiData } from "./emojis.js";

const getMentionEmbed = (result: string, title: string, warning?: string) => {
  const embed = new EmbedBuilder()
    .setColor(color)
    .setTitle(title)
    .setDescription(
      dedent`
      Copy the markdown into Discohook and it will show up on the right panel.
      If it appears as plain text, chances are you pasted it in a section that
      doesn't support rich markdown.
    `.replace(/\n/g, " "),
    )
    .addFields(
      {
        name: "Markdown",
        value: `\`${result}\``.slice(0, 4096),
        inline: true,
      },
      {
        name: "Output",
        value: result,
        inline: true,
      },
    );
  if (warning) {
    embed.addFields({ name: "Warning", value: warning, inline: true });
  }

  return embed;
};

export const formatMentionCallback: ChatInputAppCommandCallback = async (
  ctx,
) => {
  // biome-ignore lint/style/noNonNullAssertion: Required option
  const target = ctx.getMentionableOption("target")!;
  const isRole = (r: typeof target): r is APIRole => "color" in target;
  const result =
    "user" in target
      ? `<@${target.user.id}>`
      : isRole(target)
        ? `<@&${target.id}>`
        : `<@${target.id}>`;
  return ctx.reply({
    embeds: [
      getMentionEmbed(
        result,
        "Mention",
        isRole(target) && !target.mentionable
          ? "This role is not mentionable by @everyone, so a mention may not deliver as intended."
          : "Mentions will only deliver to users when they are in the **Content** section, not an embed.",
      ),
    ],
    ephemeral: true,
  });
};

export const formatChannelCallback: ChatInputAppCommandCallback = async (
  ctx,
) => {
  // biome-ignore lint/style/noNonNullAssertion: Required option
  const target = ctx.getChannelOption("target")!;
  return ctx.reply({
    embeds: [getMentionEmbed(`<#${target.id}>`, "Channel")],
    ephemeral: true,
  });
};

// Borrowed and modified from the legacy bot:
// https://github.com/discohook/bot/blob/7c5a03ed25ad6d699eef322048b2791e025ec416/src/lib/emojis/parseEmojiOption.ts
export const parseEmojiOption = async (
  ctx: InteractionContext<APIChatInputApplicationCommandInteraction>,
  emojiOptionName: string,
): Promise<string | APIPartialEmoji | undefined> => {
  const query = ctx.getStringOption(emojiOptionName).value;
  const safeQuery = query.replace(/[\W-+]*/g, "");

  const match = FormattingPatterns.Emoji.exec(query);
  if (match?.groups) {
    return {
      id: match.groups.id,
      name: match.groups.name,
      animated: Boolean(match.groups.animated),
    } as APIPartialEmoji;
  }

  const emojiData = await fetchEmojiData(ctx.env);
  const { nameToEmoji, emojiToName } = resolveEmojiData(emojiData);

  if (emojiToName.has(query)) {
    return query;
  }

  if (nameToEmoji.has(safeQuery)) {
    return nameToEmoji.get(safeQuery);
  }
};

export const formatEmojiCallback: ChatInputAppCommandCallback = async (ctx) => {
  const emoji = await parseEmojiOption(ctx, "target");
  if (!emoji) {
    return ctx.reply({
      content: "No emoji was found.",
      ephemeral: true,
    });
  }

  const formatting =
    typeof emoji === "object"
      ? `<${emoji.animated ? "a" : ""}:${emoji.name}:${emoji.id}>`
      : emoji;

  return ctx.reply({
    embeds: [getMentionEmbed(formatting, "Emoji")],
    ephemeral: true,
  });
};

```

### File: `packages/bot/src/commands/help.ts`
```ts
import type { APIEmbed } from "discord-api-types/v10";
import type {
  AppCommandAutocompleteCallback,
  ChatInputAppCommandCallback,
} from "../commands.js";
import type { Env } from "../types/env.js";
import { color } from "../util/meta.js";

type HelpTags = Record<string, APIEmbed | string>;

const fetchTags = async (env: Env) => {
  const response = await env.SITE.fetch("http://localhost/help/en.json", {
    method: "GET",
  });
  return (await response.json()) as HelpTags;
};

const findEmbed = (
  tags: HelpTags,
  tag: string,
): [string, APIEmbed | undefined] => {
  const cur = tags[tag];
  if (typeof cur === "string") {
    return findEmbed(tags, cur);
  } else {
    return [tag, cur];
  }
};

export const helpEntry: ChatInputAppCommandCallback = async (ctx) => {
  const query = ctx.getStringOption("tag");
  const mentionUser = ctx.getUserOption("mention");

  const tags = await fetchTags(ctx.env);
  const [, embed] = findEmbed(tags, query.value);

  if (embed) {
    embed.color = embed.color ?? color;
    return ctx.reply({
      content: mentionUser ? `<@${mentionUser.id}>` : undefined,
      allowedMentions: mentionUser ? { users: [mentionUser.id] } : undefined,
      // These messages are ephemeral by default to reduce spam
      ephemeral: !mentionUser || mentionUser.bot,
      embeds: [embed],
    });
  }

  const entries = Object.entries(tags)
    .filter((v) => typeof v[1] !== "string")
    .map((v) => [v[0], v[1]] as [string, APIEmbed])
    .filter((v) => v[1].title === query.value.trim());

  if (entries.length !== 0) {
    const e = entries[0][1];
    e.color = e.color ?? color;
    return ctx.reply({
      embeds: [e],
      ephemeral: true,
    });
  }

  return ctx.reply({
    content:
      "No tag found. Select an item from the autocomplete menu or use the exact title of a valid item.",
    ephemeral: true,
  });
};

export const helpAutocomplete: AppCommandAutocompleteCallback = async (ctx) => {
  const query = ctx.getStringOption("tag");

  const tags = await fetchTags(ctx.env);
  const [tag, embed] = findEmbed(tags, query.value);

  if (!embed) {
    const entries = Object.entries(tags)
      .filter((v) => typeof v[1] !== "string")
      .map((v) => [v[0], v[1]] as [string, APIEmbed])
      // Make this 'search' function better in the future
      .filter(
        (v) =>
          !!v[1].title &&
          v[1].title.toLowerCase().includes(query.value.toLowerCase().trim()),
      );

    return entries.map((entry) => ({
      // biome-ignore lint/style/noNonNullAssertion: Undefined titles filtered above
      name: entry[1].title!,
      value: entry[0],
    }));
  } else {
    return [
      {
        // biome-ignore lint/style/noNonNullAssertion: Undefined titles filtered above
        name: embed.title!,
        value: tag,
      },
    ];
  }
};

```

### File: `packages/bot/src/commands/id.ts`
```ts
import type { ChatInputAppCommandCallback } from "../commands.js";
import { parseEmojiOption } from "./format.js";

export const idMentionCallback: ChatInputAppCommandCallback = async (ctx) => {
  // biome-ignore lint/style/noNonNullAssertion: Required option
  const target = ctx.getMentionableOption("target")!;
  return ctx.reply({
    content:
      "color" in target
        ? target.id
        : "user" in target
          ? target.user.id
          : target.id,
    ephemeral: true,
  });
};

export const idChannelCallback: ChatInputAppCommandCallback = async (ctx) => {
  // biome-ignore lint/style/noNonNullAssertion: Required option
  const target = ctx.getChannelOption("target")!;
  return ctx.reply({
    content: target.id,
    ephemeral: true,
  });
};

export const idEmojiCallback: ChatInputAppCommandCallback = async (ctx) => {
  const emoji = await parseEmojiOption(ctx, "target");
  if (!emoji) {
    return ctx.reply({
      content: "No emoji was found.",
      ephemeral: true,
    });
  }

  return ctx.reply({
    content:
      typeof emoji === "object" ? (emoji.id ?? ctx.t("idUnavailable")) : emoji,
    ephemeral: true,
  });
};

```

### File: `packages/bot/src/commands/invite.ts`
```ts
import { MessageFlags } from "discord-api-types/v10";
import { PermissionFlags, PermissionsBitField } from "discord-bitflag";
import type { ChatInputAppCommandCallback } from "../commands.js";

export const inviteCallback: ChatInputAppCommandCallback = async (ctx) => {
  const permissions = new PermissionsBitField(0);
  // permissions.set(PermissionFlags.ManageGuild, true);
  // Create & manage webhooks
  permissions.set(PermissionFlags.ManageWebhooks, true);
  permissions.set(PermissionFlags.ManageChannels, true);
  // Flows (add/remove roles from members)
  permissions.set(PermissionFlags.ManageRoles, true);
  // Create buttons?
  permissions.set(PermissionFlags.ManageMessages, true);
  // Welcomer, flows (custom message, create thread)
  permissions.set(PermissionFlags.ReadMessageHistory, true);
  permissions.set(PermissionFlags.ViewChannel, true);
  permissions.set(PermissionFlags.SendMessages, true);
  permissions.set(PermissionFlags.EmbedLinks, true);
  permissions.set(PermissionFlags.UseExternalEmojis, true);
  permissions.set(PermissionFlags.AttachFiles, true);
  permissions.set(PermissionFlags.CreatePublicThreads, true);
  permissions.set(PermissionFlags.CreatePrivateThreads, true);
  permissions.set(PermissionFlags.SendMessagesInThreads, true);
  // Flows
  permissions.set(PermissionFlags.ModerateMembers, true);
  // Profile (nickname)
  permissions.set(PermissionFlags.ChangeNickname, true);

  const url = new URL(
    `https://discord.com/oauth2/authorize?${new URLSearchParams({
      client_id: ctx.followup.applicationId,
      permissions: permissions.toString(),
      scope: "bot",
    })}`,
  );

  return ctx.reply({ content: url.href, flags: MessageFlags.Ephemeral });
};

```

### File: `packages/bot/src/commands/profile.ts`
```ts
import { ContainerBuilder } from "@discordjs/builders";
import {
  type APIGuildMember,
  PermissionFlagsBits,
  RESTJSONErrorCodes,
  Routes,
} from "discord-api-types/v10";
import type { ChatInputAppCommandCallback } from "../commands.js";
import { cdn, readAttachment, userAvatarUrl } from "../util/cdn.js";
import { textDisplay } from "../util/components.js";
import { isDiscordError } from "../util/error.js";
import { color } from "../util/meta.js";
import { getUserTag } from "../util/user.js";

interface ModifyCurrentMemberBody {
  nick?: string | null;
  avatar?: string | null;
  banner?: string | null;
  bio?: string | null;
}

const getMemberProfileContainer = (
  member: APIGuildMember,
  guildId: string,
  // discord doesn't return user bios in the member object, even for yourself
  newBio?: string | null,
): ContainerBuilder => {
  // but they *do* return the bio in a PATCH response
  const bio = "bio" in member ? (member.bio as string) : newBio;

  const container = new ContainerBuilder().setAccentColor(color);
  if (member.banner) {
    container.addMediaGalleryComponents((g) =>
      g.addItems((i) =>
        i.setURL(
          // biome-ignore lint/style/noNonNullAssertion: above
          cdn.guildMemberBanner(guildId, member.user.id, member.banner!, {
            size: 2048,
          }),
        ),
      ),
    );
  }
  container.addSectionComponents((s) =>
    s
      .addTextDisplayComponents([
        textDisplay(
          `### ${member.nick ?? member.user.global_name ?? member.user.username}\n${getUserTag(member.user)}`,
        ),
        textDisplay(
          bio === null
            ? "-# *Discohook's default bio will be used.*"
            : bio
              ? bio // max 190 chars; should be fine
              : "-# *Bio cannot be shown due to Discord limitations.*",
        ),
      ])
      .setThumbnailAccessory((t) =>
        t.setURL(
          member.avatar
            ? cdn.guildMemberAvatar(guildId, member.user.id, member.avatar, {
                size: 2048,
              })
            : userAvatarUrl(member.user, { size: 2048 }),
        ),
      ),
  );

  return container;
};

export const profileSetCallback: ChatInputAppCommandCallback<true> = async (
  ctx,
) => {
  // Well, this is handled by the command permissions right?
  // if (!ctx.userPermissons.has(PermissionFlagsBits.ManageNicknames)) {
  //   return ctx.reply({
  //     content:
  //       "You need the **manage nicknames** permission to use this command.",
  //     ephemeral: true,
  //   });
  // }

  const nickField = ctx.getStringOption("name")?.value?.trim() || undefined;
  const bannerField = ctx.getAttachmentOption("banner");
  const avatarField = ctx.getAttachmentOption("avatar");
  const bioField = ctx.getStringOption("bio")?.value?.trim() || undefined;

  // as far as i know the other fields are not permission-restricted right now
  if (nickField && !ctx.appPermissons.has(PermissionFlagsBits.ChangeNickname)) {
    return ctx.reply({
      content:
        "I need the **Change Nickname** permission to change my own nickname.",
      ephemeral: true,
    });
  }

  if (!nickField && !bannerField && !avatarField && !bioField) {
    let member: APIGuildMember;
    try {
      // empty PATCH to get own bio
      member = (await ctx.rest.patch(
        Routes.guildMember(ctx.interaction.guild_id, "@me"),
        // This won't show up in audit log since it's blank so
        // the reason shouldn't matter
        { body: {} },
      )) as APIGuildMember;
    } catch (e) {
      if (
        // perhaps rate limit or empty body was forbidden
        isDiscordError(e) &&
        e.code !== RESTJSONErrorCodes.UnknownMember &&
        e.code !== RESTJSONErrorCodes.UnknownGuild
      ) {
        console.error(
          "Failed to submit empty PATCH current member, falling back to GET",
          e.rawError,
        );
        member = (await ctx.rest.get(
          Routes.guildMember(
            ctx.interaction.guild_id,
            ctx.interaction.application_id,
          ),
        )) as APIGuildMember;
      } else {
        throw e;
      }
    }

    return ctx.reply({
      components: [getMemberProfileContainer(member, ctx.interaction.guild_id)],
      componentsV2: true,
      ephemeral: true,
    });
  }

  return [
    ctx.defer({ componentsV2: false, ephemeral: true }),
    async () => {
      const body: ModifyCurrentMemberBody = { nick: nickField, bio: bioField };

      if (avatarField) {
        const avatar = await readAttachment(avatarField.url);
        body.avatar = avatar;
      }
      if (bannerField) {
        const banner = await readAttachment(bannerField.url);
        body.banner = banner;
      }

      const member = (await ctx.rest.patch(
        Routes.guildMember(ctx.interaction.guild_id, "@me"),
        {
          body,
          reason: `${getUserTag(ctx.user)} (${ctx.user.id}) via /profile set`,
        },
      )) as APIGuildMember;
      await ctx.followup.editOriginalMessage({
        // content: "Profile updated.",
        // I don't really like how plain this is
        components: [
          getMemberProfileContainer(member, ctx.interaction.guild_id, body.bio),
        ],
        componentsV2: true,
      });
    },
  ];
};

export const profileClearCallback: ChatInputAppCommandCallback<true> = async (
  ctx,
) => {
  const value = (ctx.getStringOption("value")?.value || undefined) as
    | "name"
    | "avatar"
    | "banner"
    | "bio"
    | undefined;

  return [
    ctx.defer({ ephemeral: true }),
    async () => {
      const body: ModifyCurrentMemberBody = {};

      if (value) {
        body[value === "name" ? "nick" : value] = null;
      } else {
        body.nick = null;
        body.avatar = null;
        body.banner = null;
        body.bio = null;
      }

      await ctx.rest.patch(
        Routes.guildMember(ctx.interaction.guild_id, "@me"),
        {
          body,
          reason: `${getUserTag(ctx.user)} (${ctx.user.id}) via /profile clear`,
        },
      );
      await ctx.followup.editOriginalMessage({
        content: value
          ? `Cleared my ${value} for this server.`
          : "Reset all profile values to their defaults.",
      });
    },
  ];
};

```

### File: `packages/bot/src/commands/quick-edit/entry.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  ContainerBuilder,
  ModalBuilder,
  StringSelectMenuBuilder,
  StringSelectMenuOptionBuilder,
  ThumbnailBuilder,
} from "@discordjs/builders";
import dedent from "dedent-js";
import {
  type APIChatInputApplicationCommandGuildInteraction,
  type APIComponentInContainer,
  type APIContainerComponent,
  type APIEmbed,
  type APIMediaGalleryItem,
  type APIMessage,
  type APIMessageApplicationCommandGuildInteraction,
  type APIMessageTopLevelComponent,
  type APISectionComponent,
  type APISeparatorComponent,
  type APITextDisplayComponent,
  ButtonStyle,
  ComponentType,
  EmbedType,
  SeparatorSpacingSize,
  TextInputStyle,
} from "discord-api-types/v10";
import {
  type APIMessageReducedWithId,
  cacheMessage,
  getchMessage,
} from "store";
import type {
  ChatInputAppCommandCallback,
  InteractionInstantOrDeferredResponse,
  MessageAppCommandCallback,
} from "../../commands.js";
import type {
  AutoComponentCustomId,
  AutoModalCustomId,
  SelectMenuCallback,
} from "../../components.js";
import type { InteractionContext } from "../../interactions.js";
import {
  isComponentsV2,
  parseAutoComponentId,
  textDisplay,
} from "../../util/components.js";
import { boolEmoji } from "../../util/meta.js";
import { resolveMessageLink } from "../components/entry.js";
import { isMessageWebhookEditable } from "../restore.js";
import { getQuickEditComponentByPath } from "./open.js";

const getCV2TopLevelOptions = (
  components: (APIMessageTopLevelComponent | APIComponentInContainer)[],
) => {
  const options: StringSelectMenuOptionBuilder[] = [];
  let hasActionRows = false;
  let i = -1;
  for (const component of components) {
    i += 1;
    switch (component.type) {
      case ComponentType.Container:
      // case ComponentType.File:
      case ComponentType.MediaGallery:
      case ComponentType.Section:
      case ComponentType.Separator:
      case ComponentType.TextDisplay:
        options.push(
          new StringSelectMenuOptionBuilder()
            .setLabel(
              `[${i + 1}] ${ComponentType[component.type].replace(
                // Add space before capital
                /([a-z])([A-Z])/g,
                "$1 $2",
              )}`,
            )
            .setValue(`components.${i}`),
        );
        break;
      case ComponentType.ActionRow:
        hasActionRows = true;
        break;
      default:
        break;
    }
  }
  return { options, hasActionRows };
};

export const quickEditChatEntry: ChatInputAppCommandCallback<true> = async (
  ctx,
) => {
  const message = await resolveMessageLink(
    ctx.rest,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    return ctx.reply({ content: message, ephemeral: true });
  }
  return await quickEditPart1(ctx, message);
};

export const quickEditMessageEntry: MessageAppCommandCallback<
  APIMessageApplicationCommandGuildInteraction
> = async (ctx) => {
  const message = ctx.getMessage();
  return await quickEditPart1(ctx, message);
};

const quickEditPart1 = async (
  ctx: InteractionContext<
    | APIChatInputApplicationCommandGuildInteraction
    | APIMessageApplicationCommandGuildInteraction
  >,
  message: APIMessage,
): Promise<InteractionInstantOrDeferredResponse> => {
  if (!isMessageWebhookEditable(ctx.env, message)) {
    return ctx.reply({
      content:
        "Discohook Utils can only edit webhook messages owned by itself or a user.",
      ephemeral: true,
    });
  }

  const options: StringSelectMenuOptionBuilder[] = [];
  let hasActionRows = false;
  if (isComponentsV2(message)) {
    const result = getCV2TopLevelOptions(message.components ?? []);
    options.push(...result.options);
    hasActionRows = result.hasActionRows;
  } else {
    // Should be max 21 items
    options.push(
      new StringSelectMenuOptionBuilder()
        .setLabel(
          message.content
            ? `Content (${message.content.length} chars)`
            : "Add Content",
        )
        .setValue("content"),
    );
    if (message.embeds) {
      let i = -1;
      for (const embed of message.embeds) {
        i += 1;
        // Ignore link embeds in options since we can't edit those (but still
        // pass correct index). Not sure what to do about Mastodon link embeds,
        // which have a type of `rich` despite being unfurls.
        if (embed.type && embed.type !== EmbedType.Rich) continue;
        options.push(
          new StringSelectMenuOptionBuilder()
            .setLabel(`Embed ${i + 1}`)
            .setValue(`embeds.${i}`),
        );
      }
    }
  }

  const actionRowWarning = hasActionRows
    ? "To edit interactive components, use the **Buttons & Components** message command."
    : "";
  if (options.length === 0) {
    return ctx.reply({
      content: `There's nothing in this message that Discohook Utils can edit. ${actionRowWarning}`,
      ephemeral: true,
    });
  }

  // TODO: this should be futureproofed.
  // We're doing this the lazy way instead of the robust way. Currently there
  // should be a maximum of 40 options (40 total components in a CV2 message)
  // but it's totally possible there could be more in the future.
  const options1 = options.slice(0, 25);
  const options2 = options.slice(25, 50);

  const components = [
    textDisplay(
      `There ${
        options.length === 1 ? "is 1 element" : `are ${options.length} elements`
      } in this message that Discohook Utils can edit. Pick one below and follow the instructions to edit it.`,
    ),
    new ActionRowBuilder<StringSelectMenuBuilder>().addComponents(
      new StringSelectMenuBuilder()
        .setCustomId(
          `a_qe-select-element_${message.channel_id}:${message.id}:0` satisfies AutoComponentCustomId,
        )
        .addOptions(options1)
        .setPlaceholder(
          options2.length === 0
            ? "Select what to edit"
            : "Select what to edit (1/2)",
        ),
    ),
  ];
  if (options2.length !== 0) {
    components.push(
      new ActionRowBuilder<StringSelectMenuBuilder>().addComponents(
        new StringSelectMenuBuilder()
          .setCustomId(
            `a_qe-select-element_${message.channel_id}:${message.id}:1` satisfies AutoComponentCustomId,
          )
          .addOptions(options2)
          .setPlaceholder("Select what to edit (2/2)"),
      ),
    );
  }

  await cacheMessage(ctx.env, message, ctx.interaction.guild_id);
  return ctx.reply({ components, componentsV2: true, ephemeral: true });
};

export const missingElement =
  "There is nothing at that index. Has the message already been updated?";

// Part 2
export const quickEditSelectElement: SelectMenuCallback = async (ctx) => {
  const { channelId, messageId } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "channelId",
    "messageId",
    "i", // index of which overflow select was used, not useful here
  );
  const message = await getchMessage(ctx.rest, ctx.env, channelId, messageId, {
    guildId: ctx.interaction.guild_id,
  });

  const value = ctx.interaction.data.values[0];
  const [group, index] = value.split(".");
  switch (group) {
    case "content": {
      const modal = getQuickEditContentModal(message);
      // TODO: Reset select state
      return ctx.modal(modal);
    }
    case "embeds": {
      const embed = message.embeds?.[Number(index)];
      if (!embed) {
        return ctx.reply({
          content: missingElement,
          ephemeral: true,
        });
      }
      const container = getQuickEditEmbedContainer(
        message,
        embed,
        Number(index),
      );
      return ctx.updateMessage({
        components: [
          // new ContainerBuilder()
          //   .setAccentColor(color)
          //   .addTextDisplayComponents((td) =>
          //     td.setContent("Select a part of the embed to edit."),
          //   ),
          container,
        ],
      });
    }
    case "components": {
      const component = message.components?.[Number(index)];
      if (!component) {
        return ctx.reply({
          content: missingElement,
          ephemeral: true,
        });
      }
      return await getQuickEditComponentUpdateResponse(
        ctx,
        message,
        component,
        Number(index),
      );
    }
    default:
      break;
  }

  return ctx.updateMessage({
    components: [
      textDisplay(`Couldn't determine what data to edit. Value: ${value}`),
    ],
  });
};

// Part 3 if editing a container
export const quickEditSelectContainerElement: SelectMenuCallback = async (
  ctx,
) => {
  const { channelId, messageId, componentIndex } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "channelId",
    "messageId",
    "componentIndex",
    "i", // index of which overflow select was used, not useful here
  );
  const message = await getchMessage(ctx.rest, ctx.env, channelId, messageId, {
    guildId: ctx.interaction.guild_id,
  });

  const container = message.components?.[Number(componentIndex)];
  if (!container || container.type !== ComponentType.Container) {
    return ctx.reply({
      content: missingElement,
      ephemeral: true,
    });
  }

  const value = ctx.interaction.data.values[0];
  const [, index] = value.split(".");
  const component = container.components[Number(index)];
  if (!component) {
    return ctx.reply({
      content: missingElement,
      ephemeral: true,
    });
  }

  return await getQuickEditComponentUpdateResponse(
    ctx,
    message,
    component,
    Number(index),
    Number(componentIndex),
  );
};

const getQuickEditContentModal = (message: APIMessageReducedWithId) => {
  const modal = new ModalBuilder()
    .setCustomId(
      `a_qe-submit-content_${message.channel_id}:${message.id}` satisfies AutoModalCustomId,
    )
    .setTitle("Set Content")
    .addLabelComponents((l) =>
      l.setLabel("Content").setTextInputComponent((b) =>
        b
          .setCustomId("content")
          .setStyle(TextInputStyle.Paragraph)
          .setValue((message.content ?? "").slice(0, 2000))
          .setMaxLength(2000)
          .setRequired(false),
      ),
    );
  return modal;
};

export const getQuickEditEmbedContainer = (
  message: APIMessageReducedWithId,
  embed: APIEmbed,
  embedIndex: number,
) => {
  const customId =
    `a_qe-embed-part_${message.channel_id}:${message.id}:${embedIndex}` satisfies AutoComponentCustomId;
  const container = new ContainerBuilder({ accent_color: embed.color });
  // We don't preview the text because it could easily become too large (6000 embed chars vs 4000 cv2 chars)
  const missingParts: string[] = [];
  if (embed.author) {
    container.addSectionComponents((s) =>
      s
        .addTextDisplayComponents((td) => td.setContent("**Author**"))
        .addTextDisplayComponents((td) =>
          td.setContent(dedent`
            Name: ${boolEmoji(!!embed.author?.name)} ${
              embed.author?.name.length ?? 0
            }/256
            Icon: ${boolEmoji(!!embed.author?.icon_url)}
            URL: ${boolEmoji(!!embed.author?.url)}
          `),
        )
        .setButtonAccessory(
          new ButtonBuilder()
            .setCustomId(`${customId}:author`)
            .setStyle(ButtonStyle.Secondary)
            .setLabel("Set Author"),
        ),
    );
  } else {
    missingParts.push("author");
  }

  if (embed.title || embed.url || embed.description) {
    container.addSectionComponents((s) =>
      s
        .addTextDisplayComponents((td) => td.setContent("**Body**"))
        .addTextDisplayComponents((td) =>
          td.setContent(dedent`
            Title: ${boolEmoji(!!embed.title)} ${embed.title?.length ?? 0}/256
            Title URL: ${boolEmoji(!!embed.url)}
            Description: ${boolEmoji(!!embed.description)} ${
              embed.description?.length ?? 0
            }/4096
          `),
        )
        .setButtonAccessory(
          new ButtonBuilder()
            .setCustomId(`${customId}:title`)
            .setStyle(ButtonStyle.Secondary)
            .setLabel("Set Body"),
        ),
    );
  } else {
    if (!embed.title) missingParts.push("title");
    if (!embed.description) missingParts.push("description");
    if (!embed.url) missingParts.push("url");
  }

  if (embed.thumbnail) {
    container.addSectionComponents((s) =>
      s
        .addTextDisplayComponents((td) => td.setContent("**Thumbnail**"))
        .addTextDisplayComponents((td) =>
          td.setContent(dedent`
            URL: ${boolEmoji(!!embed.thumbnail?.url)}
            Size: ${embed.thumbnail?.width ?? "?"}x${
              embed.thumbnail?.height ?? "?"
            }
          `),
        )
        .setButtonAccessory(
          new ButtonBuilder()
            .setCustomId(`${customId}:thumbnail`)
            .setStyle(ButtonStyle.Secondary)
            .setLabel("Set Thumbnail"),
        ),
    );
  } else {
    missingParts.push("thumbnail");
  }

  container.addTextDisplayComponents((td) =>
    td.setContent(`**Fields - ${embed.fields?.length ?? 0}/25**`),
  );
  if (embed.fields && embed.fields.length !== 0) {
    container.addActionRowComponents((row) =>
      row.addComponents(
        new StringSelectMenuBuilder()
          .setCustomId(`${customId}:fields`)
          .setPlaceholder("Select a field")
          .addOptions(
            embed.fields?.map((field, i) =>
              new StringSelectMenuOptionBuilder()
                // non-content components don't count toward char limit
                .setLabel(`[${i + 1}] ${field.name}`.slice(0, 100))
                .setDescription(field.value.slice(0, 100))
                .setValue(String(i)),
            ) ?? [],
          ),
      ),
    );
  }
  if (!embed.fields || embed.fields.length < 25) {
    container.addActionRowComponents((row) =>
      row.addComponents(
        new ButtonBuilder()
          .setCustomId(`${customId}:fields.new`)
          .setStyle(ButtonStyle.Secondary)
          .setLabel("Add Field"),
      ),
    );
  }

  if (embed.image) {
    container.addSectionComponents((s) =>
      s
        .addTextDisplayComponents((td) => td.setContent("**Image**"))
        .addTextDisplayComponents((td) =>
          td.setContent(dedent`
            URL: ${boolEmoji(!!embed.image?.url)}
            Size: ${embed.image?.width ?? "?"}x${embed.image?.height ?? "?"}
          `),
        )
        .setButtonAccessory(
          new ButtonBuilder()
            .setCustomId(`${customId}:image`)
            .setStyle(ButtonStyle.Secondary)
            .setLabel("Set Image"),
        ),
    );
  } else {
    missingParts.push("image");
  }

  if (embed.footer) {
    container.addSectionComponents((s) =>
      s
        .addTextDisplayComponents((td) => td.setContent("**Footer**"))
        .addTextDisplayComponents((td) =>
          td.setContent(dedent`
            Text: ${boolEmoji(!!embed.footer?.text)}
            Icon: ${boolEmoji(!!embed.footer?.icon_url)}
          `),
        )
        .setButtonAccessory(
          new ButtonBuilder()
            .setCustomId(`${customId}:footer`)
            .setStyle(ButtonStyle.Secondary)
            .setLabel("Set Footer"),
        ),
    );
  } else {
    missingParts.push("footer");
  }

  if (missingParts.length > 0) {
    container
      .addSeparatorComponents((s) =>
        s.setDivider().setSpacing(SeparatorSpacingSize.Large),
      )
      .addTextDisplayComponents((td) => td.setContent("**New Parts**"))
      .addActionRowComponents((row) =>
        row.addComponents(
          new StringSelectMenuBuilder()
            .setCustomId(`${customId}:new`)
            // .setPlaceholder("Add missing parts")
            .addOptions(
              missingParts.map((part) =>
                new StringSelectMenuOptionBuilder()
                  .setLabel(
                    part === "url"
                      ? "Title URL"
                      : part[0].toUpperCase() + part.slice(1),
                  )
                  .setValue(part),
              ),
            ),
        ),
      );
  }

  return container;
};

export const getQuickEditMediaGalleryItemModal = (
  message: APIMessageReducedWithId,
  item: APIMediaGalleryItem,
  path: number[],
) => {
  const modal = new ModalBuilder()
    .setCustomId(
      `a_qe-submit-gallery-item_${message.channel_id}:${message.id}:${path.join(
        ".",
      )}` satisfies AutoModalCustomId,
    )
    .setTitle("Edit Media")
    .addLabelComponents((l) =>
      l
        .setLabel("URL")
        .setDescription("A full, direct URL to the media")
        .setTextInputComponent((b) =>
          b
            .setCustomId("url")
            .setStyle(TextInputStyle.Short)
            .setValue(item.media.url)
            .setRequired(),
        ),
    );

  if (item.media.content_type?.startsWith("image/")) {
    modal
      .addLabelComponents((l) =>
        l.setLabel("Description (alt text)").setTextInputComponent((b) =>
          b
            .setStyle(TextInputStyle.Short)
            .setCustomId("description")
            .setValue(item.description ?? "")
            .setMaxLength(1024)
            .setRequired(false),
        ),
      )
      .addLabelComponents((l) =>
        l
          .setLabel("Spoiler?")
          .setStringSelectMenuComponent((s) =>
            s
              .setCustomId("spoiler")
              .addOptions(
                new StringSelectMenuOptionBuilder()
                  .setLabel("True")
                  .setValue("true")
                  .setDescription("The image will be blurred.")
                  .setDefault(!!item.spoiler),
                new StringSelectMenuOptionBuilder()
                  .setLabel("False")
                  .setValue("false")
                  .setDescription("The image will not be blurred (default)")
                  .setDefault(!item.spoiler),
              ),
          ),
      );
  }

  return modal;
};

export const getQuickEditMediaGalleryItemContainer = (
  message: APIMessageReducedWithId,
  item: APIMediaGalleryItem,
  path: number[],
) => {
  const container = new ContainerBuilder();

  let filename: string;
  let validThumbnailUrl = true;
  try {
    const { pathname } = new URL(item.media.url);
    filename = pathname.split("/")[pathname.split("/").length - 1];
    // discord.js validation
    new ThumbnailBuilder().setURL(item.media.url).toJSON();
  } catch {
    // Can be a user-provided value not checked by discord
    filename = item.media.url;
    validThumbnailUrl = false;
  }
  if (item.media.content_type?.startsWith("image/") && validThumbnailUrl) {
    container.addSectionComponents((s) =>
      s
        .addTextDisplayComponents((td) => td.setContent(`### ${filename}`))
        .addTextDisplayComponents((td) =>
          td.setContent(dedent`
            Spoiler: ${boolEmoji(item.spoiler ?? null)}
            Description: ${boolEmoji(!!item.description)}
          `),
        )
        .setThumbnailAccessory(
          new ThumbnailBuilder({
            description: item.description,
            media: { url: item.media.url },
          }),
        ),
    );
  } else {
    container.addTextDisplayComponents((td) =>
      td.setContent(dedent`
        ### ${filename}
        Spoiler: ${boolEmoji(item.spoiler ?? null)}
        Description: ${boolEmoji(!!item.description)}
      `),
    );
  }

  container.addActionRowComponents((row) =>
    row.addComponents(
      new ButtonBuilder()
        .setCustomId(
          `a_qe-reopen-component-modal_${message.channel_id}:${
            message.id
          }:${path.join(".")}` satisfies AutoComponentCustomId,
        )
        .setStyle(ButtonStyle.Primary)
        .setLabel("Edit"),
    ),
  );

  return container;
};

export const getQuickEditSeparatorContainer = (
  message: APIMessageReducedWithId,
  component: APISeparatorComponent,
  path: number[],
) => {
  const container = new ContainerBuilder()
    .addTextDisplayComponents((td) =>
      td.setContent(
        `### ${
          SeparatorSpacingSize[component.spacing ?? SeparatorSpacingSize.Small]
        } ${(component.divider ?? true) ? "Divider" : "Separator"}`,
      ),
    )
    .addActionRowComponents((row) =>
      row.addComponents(
        new ButtonBuilder()
          .setCustomId(
            `a_qe-separator-size_${message.channel_id}:${
              message.id
            }:${path.join(".")}` satisfies AutoComponentCustomId,
          )
          .setLabel(
            component.spacing === SeparatorSpacingSize.Small
              ? "More spacing"
              : "Less spacing",
          )
          .setEmoji({
            name: component.spacing === SeparatorSpacingSize.Small ? "⬆️" : "⬇️",
          })
          .setStyle(ButtonStyle.Secondary),
        new ButtonBuilder()
          .setCustomId(
            `a_qe-separator-divider_${message.channel_id}:${
              message.id
            }:${path.join(".")}` satisfies AutoComponentCustomId,
          )
          .setLabel(
            component.divider === false ? "Show divider" : "Hide divider",
          )
          .setEmoji({
            name: component.divider === false ? "👓" : "🕶️",
          })
          .setStyle(ButtonStyle.Secondary),
      ),
    );
  return container;
};

export const getQuickEditContainerContainer = (
  message: APIMessageReducedWithId,
  component: APIContainerComponent,
  componentIndex: number,
) => {
  const container = new ContainerBuilder({
    accent_color: component.accent_color,
  });

  container
    .addActionRowComponents((row) =>
      row.addComponents(
        new ButtonBuilder()
          .setCustomId(
            `a_qe-container-spoiler_${message.channel_id}:${message.id}:${componentIndex}` satisfies AutoComponentCustomId,
          )
          .setStyle(ButtonStyle.Secondary)
          .setLabel(component.spoiler ? "Unmark as spoiler" : "Mark as spoiler")
          .setEmoji({ name: component.spoiler ? "👓" : "🕶️" }),
      ),
    )
    .addSeparatorComponents((s) => s.setDivider());

  const { options, hasActionRows } = getCV2TopLevelOptions(
    component.components,
  );
  if (options.length === 0) {
    const actionRowWarning = hasActionRows
      ? "To edit interactive components, use the **Buttons & Components** message command."
      : "";
    container.addTextDisplayComponents((td) =>
      td.setContent(
        `There's nothing else in this container that Discohook Utils can edit. ${actionRowWarning}`,
      ),
    );
  } else {
    // TODO: see comment in part 1
    const options1 = options.slice(0, 25);
    const options2 = options.slice(25, 50);

    container
      .addTextDisplayComponents((td) =>
        td.setContent(
          `There ${
            options.length === 1
              ? "is 1 element"
              : `are ${options.length} elements`
          } in this container that Discohook Utils can edit. Pick one below and follow the instructions to edit it.`,
        ),
      )
      .addActionRowComponents((row) =>
        row.addComponents(
          new StringSelectMenuBuilder()
            .setCustomId(
              `a_qe-select-c-element_${message.channel_id}:${message.id}:${componentIndex}:0` satisfies AutoComponentCustomId,
            )
            .addOptions(options1)
            .setPlaceholder(
              options2.length === 0
                ? "Select what to edit"
                : "Select what to edit (1/2)",
            ),
        ),
      );
    if (options2.length !== 0) {
      container.addActionRowComponents((row) =>
        row.addComponents(
          new StringSelectMenuBuilder()
            .setCustomId(
              `a_qe-select-c-element_${message.channel_id}:${message.id}:${componentIndex}:1` satisfies AutoComponentCustomId,
            )
            .addOptions(options2)
            .setPlaceholder("Select what to edit (2/2)"),
        ),
      );
    }
  }

  return container;
};

const getQuickEditTextDisplayModal = (
  message: APIMessageReducedWithId,
  component: APITextDisplayComponent,
  path: number[],
) => {
  const modal = new ModalBuilder()
    .setCustomId(
      `a_qe-submit-text-display_${message.channel_id}:${message.id}:${path.join(
        ".",
      )}` satisfies AutoModalCustomId,
    )
    .setTitle("Set Text Display Content")
    .addLabelComponents((l) =>
      l.setLabel("Content").setTextInputComponent((b) =>
        b
          .setCustomId("content")
          .setStyle(TextInputStyle.Paragraph)
          .setValue((component.content ?? "").slice(0, 2000))
          .setMaxLength(2000)
          .setRequired(),
      ),
    );
  return modal;
};

export const getQuickEditSectionModal = (
  message: APIMessageReducedWithId,
  component: APISectionComponent,
  path: number[],
) => {
  const modal = new ModalBuilder()
    .setCustomId(
      `a_qe-submit-section_${message.channel_id}:${message.id}:${path.join(
        ".",
      )}` satisfies AutoModalCustomId,
    )
    .setTitle("Set Section Text Content")
    .addLabelComponents(
      component.components
        .filter((c) => c.type === ComponentType.TextDisplay)
        .map(
          (text, i, a) => (l) =>
            l
              .setLabel(`Content ${a.length === 1 ? "" : i + 1}`)
              .setTextInputComponent((b) =>
                b
                  .setCustomId(`components.${i}.content`)
                  .setStyle(TextInputStyle.Paragraph)
                  .setValue((text.content ?? "").slice(0, 2000))
                  .setMaxLength(2000)
                  // bot will require at least one of these on submit
                  .setRequired(a.length === 1),
              ),
        ),
    );
  // we don't plan on supporting a button thumbnail here, except maybe link
  // buttons since we hardly care about those in the database
  if (component.accessory.type === ComponentType.Thumbnail) {
    const thumbnail = component.accessory;
    modal
      .addLabelComponents((l) =>
        l
          .setLabel("Thumbnail URL")
          .setDescription("A full, direct URL to the media")
          .setTextInputComponent((b) =>
            b
              .setCustomId("accessory.media.url")
              .setStyle(TextInputStyle.Short)
              .setValue(thumbnail.media.url)
              .setRequired(),
          ),
      )
      .addLabelComponents((l) =>
        l.setLabel("Description (alt text)").setTextInputComponent((b) =>
          b
            .setCustomId("accessory.description")
            .setStyle(TextInputStyle.Short)
            .setValue(thumbnail.description ?? "")
            .setMaxLength(1024)
            .setRequired(false),
        ),
      );
    // sacrifice spoiler if we are over the row limit due to text inputs
    if (modal.components.length < 5) {
      modal.addLabelComponents((l) =>
        l
          .setLabel("Spoiler?")
          .setStringSelectMenuComponent((s) =>
            s
              .setCustomId("accessory.spoiler")
              .addOptions(
                new StringSelectMenuOptionBuilder()
                  .setLabel("True")
                  .setValue("true")
                  .setDescription("The image will be blurred.")
                  .setDefault(!!thumbnail.spoiler),
                new StringSelectMenuOptionBuilder()
                  .setLabel("False")
                  .setValue("false")
                  .setDescription("The image will not be blurred (default)")
                  .setDefault(!thumbnail.spoiler),
              ),
          ),
      );
    }
  }

  return modal;
};

export const getQuickEditSectionContainer = (
  message: APIMessageReducedWithId,
  component: APISectionComponent,
  path: number[],
) => {
  const container = new ContainerBuilder();
  const description = dedent`
    ### Section
    Text: ${boolEmoji(true)} ${component.components.length} item${
      component.components.length === 1 ? "" : "s"
    }
  `;
  if (component.accessory.type === ComponentType.Thumbnail) {
    const thumbnail = component.accessory;
    let filename: string;
    let validThumbnailUrl = true;
    try {
      const { pathname } = new URL(thumbnail.media.url);
      filename = pathname.split("/")[pathname.split("/").length - 1];
      // discord.js validation
      new ThumbnailBuilder().setURL(thumbnail.media.url).toJSON();
    } catch {
      // Can be a user-provided value not checked by discord
      filename = thumbnail.media.url;
      validThumbnailUrl = false;
    }
    if (validThumbnailUrl) {
      container.addSectionComponents((s) =>
        s
          .addTextDisplayComponents((td) =>
            td.setContent(dedent`
              ${description}
              Thumbnail: ${boolEmoji(true)} ${filename}
              Spoiler: ${boolEmoji(thumbnail.spoiler ?? null)}
              Description: ${boolEmoji(!!thumbnail.description)}
            `),
          )
          .setThumbnailAccessory(
            new ThumbnailBuilder({
              description: thumbnail.description,
              media: { url: thumbnail.media.url },
            }),
          ),
      );
    } else {
      container.addTextDisplayComponents((td) =>
        td.setContent(dedent`
          ${description}
          Thumbnail: ${boolEmoji(false)} ${filename}
          Spoiler: ${boolEmoji(thumbnail.spoiler ?? null)}
          Description: ${boolEmoji(!!thumbnail.description)}
        `),
      );
    }
  } else {
    container.addTextDisplayComponents((td) =>
      td.setContent(
        `${description}\nAccessory: ${ComponentType[component.accessory.type]}`,
      ),
    );
  }

  container.addActionRowComponents((row) =>
    row.addComponents(
      new ButtonBuilder()
        .setCustomId(
          `a_qe-reopen-component-modal_${message.channel_id}:${
            message.id
          }:${path.join(".")}` satisfies AutoComponentCustomId,
        )
        .setStyle(ButtonStyle.Primary)
        .setLabel("Edit"),
    ),
  );

  return container;
};

const getQuickEditComponentUpdateResponse = async (
  ctx: InteractionContext,
  message: APIMessageReducedWithId,
  component: APIMessageTopLevelComponent | APIComponentInContainer,
  componentIndex: number,
  parentIndex?: number,
): Promise<InteractionInstantOrDeferredResponse> => {
  const path =
    parentIndex !== undefined
      ? [parentIndex, componentIndex]
      : [componentIndex];
  switch (component.type) {
    case ComponentType.Container:
      return ctx.updateMessage({
        components: [
          getQuickEditContainerContainer(message, component, componentIndex),
        ],
      });
    case ComponentType.MediaGallery: {
      // max 10 items per gallery
      const select = new StringSelectMenuBuilder()
        .setCustomId(
          `a_qe-select-component_${message.channel_id}:${
            message.id
          }:${path.join(".")}` satisfies AutoComponentCustomId,
        )
        .setPlaceholder("Select a gallery item to edit")
        .addOptions(
          component.items.map((item, i) => {
            const { pathname } = new URL(item.media.url);
            const filename =
              pathname.split("/")[pathname.split("/").length - 1];
            return new StringSelectMenuOptionBuilder({
              description: item.description ?? undefined,
            })
              .setLabel(`[${i + 1}] ${filename}`.slice(0, 100))
              .setValue(String(i))
              .setEmoji({
                name: item.media.content_type?.startsWith("image/")
                  ? "🖼️"
                  : item.media.content_type?.startsWith("video/")
                    ? "🎞️"
                    : "📄",
              });
          }),
        );
      return ctx.updateMessage({
        components: [
          new ActionRowBuilder<StringSelectMenuBuilder>().addComponents(select),
        ],
      });
    }
    case ComponentType.Separator:
      return ctx.updateMessage({
        components: [getQuickEditSeparatorContainer(message, component, path)],
      });
    case ComponentType.TextDisplay:
      return ctx.modal(getQuickEditTextDisplayModal(message, component, path));
    case ComponentType.Section:
      return [
        ctx.modal(getQuickEditSectionModal(message, component, path)),
        async () => {
          await ctx.followup.editOriginalMessage({
            components: [
              getQuickEditSectionContainer(message, component, path),
            ],
          });
        },
      ];
    default:
      return ctx.reply({
        content: `Couldn't determine what data to edit. Component: type ${component.type}, index ${componentIndex}`,
        ephemeral: true,
      });
  }
};

export const quickEditSelectComponent: SelectMenuCallback = async (ctx) => {
  const {
    channelId,
    messageId,
    path: path_,
  } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "channelId",
    "messageId",
    "path",
  );
  const message = await getchMessage(ctx.rest, ctx.env, channelId, messageId, {
    guildId: ctx.interaction.guild_id,
  });

  const path = path_.split(".").map(Number);
  const { component } = getQuickEditComponentByPath(
    message.components ?? [],
    path,
  );
  if (!component) {
    return ctx.reply({ content: missingElement, ephemeral: true });
  }

  const value = ctx.interaction.data.values[0];
  switch (component.type) {
    case ComponentType.MediaGallery: {
      // the value is the index of an item
      const item = component.items[Number(value)];
      if (!item) {
        return ctx.reply({ content: missingElement, ephemeral: true });
      }
      return [
        ctx.modal(
          getQuickEditMediaGalleryItemModal(message, item, [
            ...path,
            Number(value),
          ]),
        ),
        async () => {
          await ctx.followup.editOriginalMessage({
            components: [
              getQuickEditMediaGalleryItemContainer(message, item, [
                ...path,
                Number(value),
              ]),
            ],
          });
        },
      ];
    }
    default:
      break;
  }

  return ctx.updateMessage({
    components: [
      textDisplay(`Couldn't determine what data to edit. ${path_} > ${value}`),
    ],
  });
};

```

### File: `packages/bot/src/commands/quick-edit/open.ts`
```ts
import {
  ModalBuilder,
  StringSelectMenuOptionBuilder,
} from "@discordjs/builders";
import {
  type APIComponentInContainer,
  type APIContainerComponent,
  type APIMessageTopLevelComponent,
  ComponentType,
  TextInputStyle,
} from "discord-api-types/v10";
import { getchMessage } from "store";
import type {
  AutoModalCustomId,
  ButtonCallback,
  SelectMenuCallback,
} from "../../components.js";
import { parseAutoComponentId, textDisplay } from "../../util/components.js";
import {
  getQuickEditEmbedContainer,
  getQuickEditMediaGalleryItemModal,
  getQuickEditSectionModal,
  missingElement,
} from "./entry.js";

// Not designed to work with interactive components - nesting support
// is only for containers.
export const getQuickEditComponentByPath = (
  components: APIMessageTopLevelComponent[],
  path: number[],
) => {
  let parent: APIContainerComponent | undefined;
  let component:
    | APIMessageTopLevelComponent
    | APIComponentInContainer
    | undefined;
  if (path.length > 1) {
    const container = components[path[0]];
    if (container?.type === ComponentType.Container) {
      parent = container;
      component = container.components[path[1]];
    }
  } else {
    component = components[path[0]];
  }
  return { parent, component };
};

export const quickEditComponentModalReopen: ButtonCallback = async (ctx) => {
  const {
    channelId,
    messageId,
    path: path_,
  } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "channelId",
    "messageId",
    "path",
  );

  const message = await getchMessage(ctx.rest, ctx.env, channelId, messageId);
  const path = path_.split(".").map(Number);
  const { component } = getQuickEditComponentByPath(
    message.components ?? [],
    path,
  );
  if (!component) {
    return ctx.reply({ content: missingElement, ephemeral: true });
  }

  const index = path[path.length - 1];
  switch (component.type) {
    case ComponentType.MediaGallery: {
      // the value is the index of an item
      const item = component.items[index];
      if (!item) {
        return ctx.reply({ content: missingElement, ephemeral: true });
      }
      return ctx.modal(getQuickEditMediaGalleryItemModal(message, item, path));
    }
    case ComponentType.Section: {
      return ctx.modal(getQuickEditSectionModal(message, component, path));
    }
    default:
      break;
  }

  return ctx.updateMessage({
    components: [textDisplay(`Couldn't determine what data to edit. ${path_}`)],
  });
};

export const quickEditEmbedPartOpen: ButtonCallback & SelectMenuCallback =
  async (ctx) => {
    const { channelId, messageId, embedIndex, embedPart } =
      parseAutoComponentId(
        ctx.interaction.data.custom_id,
        "channelId",
        "messageId",
        "embedIndex",
        "embedPart",
      );

    const message = await getchMessage(ctx.rest, ctx.env, channelId, messageId);
    const embed = message.embeds?.[Number(embedIndex)];
    if (!embed) {
      return ctx.reply({ content: missingElement, ephemeral: true });
    }

    let [part, inner] = embedPart.split(".");
    // Normalize select data since the identifier structure is slightly different
    if (ctx.interaction.data.component_type === ComponentType.StringSelect) {
      if (part === "new") {
        part = ctx.interaction.data.values[0];
      } else if (part === "fields") {
        inner = ctx.interaction.data.values[0];
      }
    }

    const modal = new ModalBuilder().setCustomId(
      // `part` is ignored in the callback but must be provided or else
      // Discord assumes this is the same modal as was used for another part
      // and autofills content based on each component's index rather than
      // its custom ID.
      `a_qe-submit-embed_${channelId}:${messageId}:${embedIndex}:${part}` satisfies AutoModalCustomId,
    );

    switch (part) {
      case "author": {
        modal.setTitle("Set Author");
        modal.addLabelComponents(
          (l) =>
            l
              .setLabel("Name")
              .setDescription(
                "This must be provided to display the author section.",
              )
              .setTextInputComponent((b) =>
                b
                  .setCustomId("author.name")
                  .setMaxLength(128)
                  .setStyle(TextInputStyle.Paragraph)
                  .setValue(embed.author?.name ?? "")
                  .setRequired(false),
              ),
          (l) =>
            l
              .setLabel("URL")
              .setDescription(
                "Directs desktop users to this URL when they click the author name.",
              )
              .setTextInputComponent((b) =>
                b
                  .setCustomId("author.url")
                  .setStyle(TextInputStyle.Short)
                  .setValue(embed.author?.url ?? "")
                  .setRequired(false),
              ),
          (l) =>
            l
              .setLabel("Icon URL")
              .setDescription("An image shown to the left of the author name.")
              .setTextInputComponent((b) =>
                b
                  .setCustomId("author.icon_url")
                  .setStyle(TextInputStyle.Short)
                  .setValue(embed.author?.icon_url ?? "")
                  .setRequired(false),
              ),
        );
        break;
      }
      case "title":
      case "description": {
        modal.setTitle("Set Body");
        modal.addLabelComponents(
          (l) =>
            l
              .setLabel("Title")
              .setDescription(
                "Large text below the author and above the description.",
              )
              .setTextInputComponent((b) =>
                b
                  .setCustomId("title")
                  .setMaxLength(256)
                  .setStyle(TextInputStyle.Paragraph)
                  .setValue(embed.title ?? "")
                  .setRequired(false),
              ),
          (l) =>
            l
              .setLabel("Title URL")
              .setDescription("Open this URL when users click the title.")
              .setTextInputComponent((b) =>
                b
                  .setCustomId("url")
                  .setStyle(TextInputStyle.Short)
                  .setValue(embed.url ?? "")
                  .setRequired(false),
              ),
          (l) =>
            l
              .setLabel("Description")
              .setDescription(
                `Markdown-safe text below the title. ${
                  embed.description && embed.description?.length > 4000
                    ? "This value was truncated because Discord's limit for text inputs is 4000."
                    : ""
                }`,
              )
              .setTextInputComponent((b) =>
                b
                  .setCustomId("description")
                  .setMaxLength(4000) // actual limit is 4096, but TextInput is capped lower
                  .setStyle(TextInputStyle.Paragraph)
                  .setValue(embed.description?.slice(0, 4000) ?? "")
                  .setRequired(false),
              ),
        );
        break;
      }
      case "url": {
        modal.setTitle("Set URL");
        modal.addLabelComponents((l) =>
          l
            .setLabel("URL")
            .setDescription(
              "If there is no title, this can still be used alone for creating image galleries.",
            )
            .setTextInputComponent((b) =>
              b
                .setCustomId("url")
                .setStyle(TextInputStyle.Short)
                .setValue(embed.url ?? "")
                .setRequired(false),
            ),
        );
        break;
      }
      case "thumbnail": {
        modal.setTitle("Set Thumbnail");
        modal.addLabelComponents((l) =>
          l
            .setLabel("Thumbnail URL")
            .setDescription("Displayed to the right of all text in the embed.")
            .setTextInputComponent((b) =>
              b
                .setCustomId("thumbnail.url")
                .setStyle(TextInputStyle.Short)
                .setValue(embed.thumbnail?.url ?? "")
                .setRequired(false),
            ),
        );
        break;
      }
      case "fields": {
        const isNewField = inner === "new";
        const prefix = isNewField
          ? `fields.${embed.fields ? embed.fields.length : 0}`
          : `fields.${inner}`;
        const field = isNewField ? undefined : embed.fields?.[Number(inner)];

        modal.setTitle(isNewField ? "New Field" : "Set Field");
        modal.addLabelComponents(
          (l) =>
            l
              .setLabel("Name")
              .setDescription(
                "Short, semibold text that supports a markdown subset.",
              )
              .setTextInputComponent((b) =>
                b
                  .setCustomId(`${prefix}.name`)
                  .setMaxLength(256)
                  .setStyle(TextInputStyle.Paragraph)
                  .setValue(field?.name ?? "")
                  .setRequired(isNewField),
              ),
          (l) =>
            l
              .setLabel("Value")
              .setDescription("Markdown-safe text below the field name.")
              .setTextInputComponent((b) =>
                b
                  .setCustomId(`${prefix}.value`)
                  .setStyle(TextInputStyle.Paragraph)
                  .setMaxLength(1024)
                  .setValue(field?.value ?? "")
                  .setRequired(isNewField),
              ),
          (l) =>
            l
              .setLabel("Inline?")
              .setStringSelectMenuComponent((s) =>
                s
                  .setCustomId(`${prefix}.inline`)
                  .addOptions(
                    new StringSelectMenuOptionBuilder()
                      .setLabel("True")
                      .setValue("true")
                      .setDescription(
                        "The field will display inline with other fields (up to 3 per line).",
                      )
                      .setDefault(!!field?.inline),
                    new StringSelectMenuOptionBuilder()
                      .setLabel("False")
                      .setValue("false")
                      .setDescription(
                        "The field will take the width of the entire line (default)",
                      )
                      .setDefault(!field?.inline),
                  ),
              ),
        );
        break;
      }
      case "image": {
        modal.setTitle("Set Image");
        modal.addLabelComponents((l) =>
          l
            .setLabel("Image URL")
            .setDescription(
              "Displayed as a large image below all sections except the footer.",
            )
            .setTextInputComponent((b) =>
              b
                .setCustomId("image.url")
                .setStyle(TextInputStyle.Short)
                .setValue(embed.image?.url ?? "")
                .setRequired(false),
            ),
        );
        break;
      }
      case "footer": {
        modal.setTitle("Set Footer");
        modal.addLabelComponents(
          (l) =>
            l
              .setLabel("Text")
              .setDescription(
                "This must be provided to display the footer icon, but is optional for the timestamp.",
              )
              .setTextInputComponent((b) =>
                b
                  .setCustomId("footer.text")
                  .setMaxLength(2048)
                  .setStyle(TextInputStyle.Paragraph)
                  .setValue(embed.footer?.text ?? "")
                  .setRequired(false),
              ),
          (l) =>
            l
              .setLabel("Icon URL")
              .setDescription("An image shown to the left of the footer text.")
              .setTextInputComponent((b) =>
                b
                  .setCustomId("footer.icon_url")
                  .setStyle(TextInputStyle.Short)
                  .setValue(embed.footer?.icon_url ?? "")
                  .setRequired(false),
              ),
          (l) =>
            l
              .setLabel("Timestamp")
              .setDescription(
                'A timestamp like "2025-01-01 14:00:00" or "Jan 1 2025 14:00", parsed in UTC',
              )
              .setTextInputComponent((b) =>
                b
                  .setCustomId("timestamp")
                  .setStyle(TextInputStyle.Short)
                  .setValue(embed.timestamp ?? "")
                  .setRequired(false),
              ),
        );
        break;
      }
      default:
        break;
    }

    if (modal.components.length === 0) {
      return ctx.reply({
        content: "Unable to compile any data to edit.",
        ephemeral: true,
      });
    }
    return [
      ctx.modal(modal),
      async () => {
        // Reset select state
        await ctx.followup.editOriginalMessage({
          components: [
            getQuickEditEmbedContainer(message, embed, Number(embedIndex)),
          ],
        });
      },
    ];
  };

```

### File: `packages/bot/src/commands/quick-edit/submit.ts`
```ts
import {
  type APIEmbed,
  type APIEmbedField,
  type APIInteractionResponse,
  type APIMessage,
  type APIMessageComponentButtonInteraction,
  type APIMessageComponentSelectMenuInteraction,
  type APIModalSubmitInteraction,
  type APIModalSubmitStringSelectComponent,
  type APIWebhook,
  ComponentType,
  PermissionFlagsBits,
  RESTJSONErrorCodes,
  type RESTPatchAPIWebhookWithTokenMessageJSONBody,
  Routes,
  SeparatorSpacingSize,
} from "discord-api-types/v10";
import {
  type APIMessageReducedWithId,
  cacheMessage,
  getchMessage,
} from "store";
import type { ButtonCallback, ModalCallback } from "../../components.js";
import {
  type InteractionContext,
  isInteractionResponse,
} from "../../interactions.js";
import { parseAutoComponentId, textDisplay } from "../../util/components.js";
import { isDiscordError } from "../../util/error.js";
import { getWebhookThreadQuery } from "../../util/messages.js";
import { getWebhook } from "../webhooks/webhookInfo.js";
import {
  getQuickEditContainerContainer,
  getQuickEditEmbedContainer,
  getQuickEditMediaGalleryItemContainer,
  getQuickEditSectionContainer,
  getQuickEditSeparatorContainer,
  missingElement,
} from "./entry.js";
import { getQuickEditComponentByPath } from "./open.js";

const submitWebhookMessageEdit = async (
  ctx: InteractionContext,
  webhook: APIWebhook,
  message: Pick<APIMessage, "id" | "position" | "channel_id">,
  body: RESTPatchAPIWebhookWithTokenMessageJSONBody,
  after: (updated: APIMessage) => Promise<void>,
): Promise<[APIInteractionResponse, () => Promise<void>]> => {
  return [
    ctx.defer(),
    async () => {
      const query = getWebhookThreadQuery(message);
      let updated: APIMessage | undefined;
      try {
        updated = (await ctx.rest.patch(
          // biome-ignore lint/style/noNonNullAssertion: this should have been verified previously
          Routes.webhookMessage(webhook.id, webhook.token!, message.id),
          { body, query },
        )) as APIMessage;
      } catch (e) {
        if (
          isDiscordError(e) &&
          e.code === RESTJSONErrorCodes.UnknownMessage &&
          !query.has("thread_id")
        ) {
          // There is a bug where the second message in a forum thread is
          // missing `position`, so it cannot be determined that it is a
          // thread message. Therefore, in the event that we receive this
          // specific error and did not already try passing a thread ID, we
          // try again assuming that this is what's happening
          // https://github.com/discord/discord-api-docs/issues/7788
          try {
            updated = (await ctx.rest.patch(
              // biome-ignore lint/style/noNonNullAssertion: see above
              Routes.webhookMessage(webhook.id, webhook.token!, message.id),
              {
                body,
                query: new URLSearchParams({ thread_id: message.channel_id }),
              },
            )) as APIMessage;
          } catch {
            // well, that wasn't the problem
          }
        }
        if (!updated) {
          if (isDiscordError(e)) {
            await ctx.followup.send({
              content: `Discord rejected the edit: **${
                e.rawError.message
              }**\`\`\`json\n${JSON.stringify(e.rawError)}\`\`\``,
              ephemeral: true,
            });
          }
          throw e;
        }
      }

      // Re-cache the message so subsequent edits use the newest version of
      // the message. Cached with a shorter TTL than normal.
      await cacheMessage(ctx.env, updated, webhook.guild_id, 600);
      await after(updated);
    },
  ];
};

const verifyWebhookMessageEditPermissions = async (
  ctx: InteractionContext,
  channelId: string,
  messageId: string,
) => {
  const message = await getchMessage(ctx.rest, ctx.env, channelId, messageId, {
    guildId: ctx.interaction.guild_id,
  });
  if (!message.webhook_id) {
    throw ctx.reply({
      content: "Somehow, this isn't a webhook message.",
      ephemeral: true,
    });
  }

  const webhook = await getWebhook(
    message.webhook_id,
    ctx.env,
    message.application_id,
  );
  if (
    !webhook.guild_id ||
    webhook.guild_id !== ctx.interaction.guild_id ||
    !ctx.userPermissons.has(
      PermissionFlagsBits.ManageWebhooks,
      PermissionFlagsBits.ManageMessages,
      PermissionFlagsBits.ReadMessageHistory,
    )
  ) {
    throw ctx.reply({
      content:
        "You don't have the appropriate permissions to edit webhook messages.",
      ephemeral: true,
    });
  }
  if (!webhook.token) {
    throw ctx.reply({
      content: "The webhook's token was inaccessible.",
      ephemeral: true,
    });
  }
  return { message, webhook };
};

const modifyEmbedByPath = (embed: APIEmbed, path: string, value: string) => {
  const [part, subPart] = path.split(".");

  switch (part) {
    case "author":
      if (subPart === "name" && !value) {
        // Remove author
        embed.author = undefined;
      } else {
        embed.author = embed.author ?? { name: "" };
        embed.author[subPart as "name" | "icon_url" | "url"] = value;
      }
      break;
    case "title":
    case "url":
    case "description":
      embed[part] = value || undefined;
      break;
    case "thumbnail":
    case "image":
      if (subPart === "url") {
        embed[part] = embed[part] ?? { url: "" };
        embed[part].url = value;
      }
      break;
    case "fields": {
      embed.fields = embed.fields ?? [];
      const index = Number(subPart);
      const field = embed.fields[index];
      const [, , fieldProp] = path.split(".");
      if (field) {
        if (fieldProp === "inline") {
          field.inline = value === "true";
        } else {
          field[fieldProp as "name" | "value"] = value;
        }
      } else {
        const newField: APIEmbedField = { name: "", value: "" };
        if (fieldProp === "inline") {
          newField.inline = value === "true";
        } else {
          newField[fieldProp as "name" | "value"] = value;
        }
        embed.fields.splice(index, 0, newField);
      }
      break;
    }
    case "footer":
      if (subPart === "text" && !value) {
        // Remove footer
        embed.footer = undefined;
      } else {
        embed.footer = embed.footer ?? { text: "" };
        embed.footer[subPart as "text" | "icon_url"] = value;
      }
      break;
    case "timestamp": {
      if (!value) {
        embed.timestamp = undefined;
      } else {
        const date = new Date(value);
        if (!Number.isNaN(date)) {
          embed.timestamp = date.toISOString();
        }
      }
      break;
    }
    default:
      break;
  }

  return embed;
};

const trimEmptyEmbedParts = (embed: APIEmbed) => {
  if (embed.author && !embed.author.name) {
    embed.author = undefined;
  }
  if (embed.footer && !embed.footer.text) {
    embed.footer = undefined;
  }
  if (embed.thumbnail && !embed.thumbnail.url) {
    embed.thumbnail = undefined;
  }
  if (embed.image && !embed.image.url) {
    embed.image = undefined;
  }
  return embed;
};

// If an embed with an `attachment://` image is updated without re-including
// the attachment URI, the attachment will appear duplicated above the embeds.
// const maintainAttachmentReferences = (
//   channelId: string,
//   embed: APIEmbed,
//   attachments: APIAttachment[],
// ) => {
//   const replaceAttachmentUrl = (
//     value: string | undefined,
//     callback: (newValue: string) => void,
//   ) => {
//     if (!value) return;
//     let url: URL;
//     try {
//       url = new URL(value);
//     } catch {
//       return;
//     }

//     if (
//       url.host === "cdn.discordapp.com" &&
//       url.pathname.startsWith(`/attachments/${channelId}/`)
//     ) {
//       const attachmentId = url.pathname.split("/")[3];
//       const attachment = attachments.find((a) => a.id === attachmentId);
//       if (attachment) {
//         callback(`attachment://${attachment.filename}`);
//       }
//     }
//   };

//   replaceAttachmentUrl(embed.author?.icon_url, (url) => {
//     if (embed.author) embed.author.icon_url = url;
//   });
//   replaceAttachmentUrl(embed.footer?.icon_url, (url) => {
//     if (embed.footer) embed.footer.icon_url = url;
//   });
//   replaceAttachmentUrl(embed.image?.url, (url) => {
//     embed.image = { url };
//   });
//   replaceAttachmentUrl(embed.thumbnail?.url, (url) => {
//     embed.thumbnail = { url };
//   });

//   return embed;
// };

export const quickEditSubmitContent: ModalCallback = async (ctx) => {
  const { channelId, messageId } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "channelId",
    "messageId",
  );
  let webhook: APIWebhook;
  let message: APIMessageReducedWithId;
  try {
    ({ webhook, message } = await verifyWebhookMessageEditPermissions(
      ctx,
      channelId,
      messageId,
    ));
  } catch (e) {
    if (isInteractionResponse(e)) return e;
    throw e;
  }

  const { value } = ctx.getModalComponent("content");
  message.content = value.trim();

  return submitWebhookMessageEdit(
    ctx,
    webhook,
    message,
    { content: message.content },
    async () => {
      await ctx.followup.editOriginalMessage({
        components: [textDisplay("Updated content.")],
      });
    },
  );
};

export const quickEditSubmitEmbed: ModalCallback = async (ctx) => {
  const { channelId, messageId, embedIndex } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "channelId",
    "messageId",
    "embedIndex",
    "embedPart", // Ignored; see open.ts `quickEditEmbedPartOpen`
  );
  let webhook: APIWebhook;
  let message: APIMessageReducedWithId;
  try {
    ({ webhook, message } = await verifyWebhookMessageEditPermissions(
      ctx,
      channelId,
      messageId,
    ));
  } catch (e) {
    if (isInteractionResponse(e)) return e;
    throw e;
  }
  const embed = message.embeds?.[Number(embedIndex)];
  if (!embed) {
    return ctx.reply({ content: missingElement, ephemeral: true });
  }

  for (const row of ctx.interaction.data.components) {
    const input =
      row.type === ComponentType.ActionRow
        ? row.components[0]
        : row.type === ComponentType.Label
          ? row.component
          : undefined;
    if (!input) continue;

    // These should all be valid references for existing or new parts
    modifyEmbedByPath(
      embed,
      input.custom_id,
      input.type === ComponentType.TextInput ? input.value : input.values[0],
    );
  }

  trimEmptyEmbedParts(embed);
  return submitWebhookMessageEdit(
    ctx,
    webhook,
    message,
    { embeds: message.embeds },
    async (updated) => {
      await ctx.followup.editOriginalMessage({
        components: [
          getQuickEditEmbedContainer(updated, embed, Number(embedIndex)),
        ],
      });

      // This is not working quite like how I want it to, for now users will
      // just have to edit via the site to maintain attachment URIs.
      // if (
      //   updated.attachments &&
      //   ((message.attachments &&
      //     updated.attachments.length > message.attachments.length) ||
      //     !message.attachments)
      // ) {
      //   // Attachments already present in embeds are not also present in
      //   // `attachments`, so we have to let Discord show the duplicated
      //   // attachments before copying them back down into the embed.
      //   // Users will see a quick flash of double attachments while this
      //   // happens.
      //   for (const e of updated.embeds) {
      //     maintainAttachmentReferences(channelId, e, updated.attachments ?? []);
      //   }

      //   let uriUpdated: APIMessage | undefined;
      //   try {
      //     uriUpdated = (await ctx.rest.patch(
      //       // biome-ignore lint/style/noNonNullAssertion: this should have been verified previously
      //       Routes.webhookMessage(webhook.id, webhook.token!, updated.id),
      //       {
      //         body: { embeds: updated.embeds },
      //         query: getWebhookThreadQuery(updated),
      //       },
      //     )) as APIMessage;
      //   } catch {}
      //   if (uriUpdated) {
      //     // https://github.com/discord/discord-api-docs/issues/7570
      //     if (uriUpdated.position !== updated.position) {
      //       uriUpdated.position = updated.position;
      //     }

      //     // If we don't re-cache then the next time this message is edited,
      //     // the attachments won't get fixed
      //     await cacheMessage(ctx.env, uriUpdated, webhook.guild_id, 600);
      //   }
      // }
    },
  );
};

const parsePathCustomId = (
  ctx: InteractionContext<
    | APIMessageComponentButtonInteraction
    | APIMessageComponentSelectMenuInteraction
    | APIModalSubmitInteraction
  >,
) => {
  const {
    channelId,
    messageId,
    path: path_,
  } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "channelId",
    "messageId",
    "path",
  );
  return { channelId, messageId, path: path_.split(".").map(Number) };
};

export const quickEditToggleContainerSpoiler: ButtonCallback = async (ctx) => {
  const { channelId, messageId, path } = parsePathCustomId(ctx);
  let webhook: APIWebhook;
  let message: APIMessageReducedWithId;
  try {
    ({ webhook, message } = await verifyWebhookMessageEditPermissions(
      ctx,
      channelId,
      messageId,
    ));
  } catch (e) {
    if (isInteractionResponse(e)) return e;
    throw e;
  }
  const container = message.components?.[path[0]];
  if (!container || container.type !== ComponentType.Container) {
    return ctx.reply({ content: missingElement, ephemeral: true });
  }

  container.spoiler = !container.spoiler;
  return submitWebhookMessageEdit(
    ctx,
    webhook,
    message,
    { components: message.components },
    async (updated) => {
      await ctx.followup.editOriginalMessage({
        components: [
          getQuickEditContainerContainer(updated, container, path[0]),
        ],
      });
    },
  );
};

export const quickEditSubmitGalleryItem: ModalCallback = async (ctx) => {
  const { channelId, messageId, path } = parsePathCustomId(ctx);
  let webhook: APIWebhook;
  let message: APIMessageReducedWithId;
  try {
    ({ webhook, message } = await verifyWebhookMessageEditPermissions(
      ctx,
      channelId,
      messageId,
    ));
  } catch (e) {
    if (isInteractionResponse(e)) return e;
    throw e;
  }
  const { component } = getQuickEditComponentByPath(
    message.components ?? [],
    path,
  );
  if (!component || component.type !== ComponentType.MediaGallery) {
    return ctx.reply({ content: missingElement, ephemeral: true });
  }

  const index = path[path.length - 1];
  const item = component.items[index];

  const url = ctx.getModalComponent("url")?.value;
  const { content_type } = item.media;
  item.media = { url };
  item.description =
    ctx.getModalComponent("description")?.value.trim() || undefined;
  item.spoiler =
    ctx.getModalComponent<APIModalSubmitStringSelectComponent>("spoiler")
      ?.values[0] === "true";

  return submitWebhookMessageEdit(
    ctx,
    webhook,
    message,
    { components: message.components },
    async (updated) => {
      // We do this so that the container builder can assume the content type
      // of the previous URL (if any), since it's unlikely that it would have
      // changed e.g. from an image to a video. But if it does, it's fine,
      // they just have to bring up the menu again.
      // We could fetch the URL to determine the content type ourselves but
      // that does not seem worth the effort at the moment.
      const containerItem = { ...item, media: { url, content_type } };
      await ctx.followup.editOriginalMessage({
        components: [
          getQuickEditMediaGalleryItemContainer(updated, containerItem, path),
        ],
      });
    },
  );
};

export const quickEditToggleSeparatorDivider: ButtonCallback = async (ctx) => {
  const { channelId, messageId, path } = parsePathCustomId(ctx);
  let webhook: APIWebhook;
  let message: APIMessageReducedWithId;
  try {
    ({ webhook, message } = await verifyWebhookMessageEditPermissions(
      ctx,
      channelId,
      messageId,
    ));
  } catch (e) {
    if (isInteractionResponse(e)) return e;
    throw e;
  }
  const { component } = getQuickEditComponentByPath(
    message.components ?? [],
    path,
  );
  if (!component || component.type !== ComponentType.Separator) {
    return ctx.reply({ content: missingElement, ephemeral: true });
  }

  // Defaults to true if undefined so we can't just negate
  component.divider = component.divider === false;

  return submitWebhookMessageEdit(
    ctx,
    webhook,
    message,
    { components: message.components },
    async (updated) => {
      await ctx.followup.editOriginalMessage({
        components: [getQuickEditSeparatorContainer(updated, component, path)],
      });
    },
  );
};

export const quickEditToggleSeparatorSize: ButtonCallback = async (ctx) => {
  const { channelId, messageId, path } = parsePathCustomId(ctx);
  let webhook: APIWebhook;
  let message: APIMessageReducedWithId;
  try {
    ({ webhook, message } = await verifyWebhookMessageEditPermissions(
      ctx,
      channelId,
      messageId,
    ));
  } catch (e) {
    if (isInteractionResponse(e)) return e;
    throw e;
  }
  const { component } = getQuickEditComponentByPath(
    message.components ?? [],
    path,
  );
  if (!component || component.type !== ComponentType.Separator) {
    return ctx.reply({ content: missingElement, ephemeral: true });
  }

  component.spacing =
    component.spacing === SeparatorSpacingSize.Large
      ? SeparatorSpacingSize.Small
      : SeparatorSpacingSize.Large;

  return submitWebhookMessageEdit(
    ctx,
    webhook,
    message,
    { components: message.components },
    async (updated) => {
      await ctx.followup.editOriginalMessage({
        components: [getQuickEditSeparatorContainer(updated, component, path)],
      });
    },
  );
};

export const quickEditSubmitTextDisplay: ModalCallback = async (ctx) => {
  const { channelId, messageId, path } = parsePathCustomId(ctx);
  let webhook: APIWebhook;
  let message: APIMessageReducedWithId;
  try {
    ({ webhook, message } = await verifyWebhookMessageEditPermissions(
      ctx,
      channelId,
      messageId,
    ));
  } catch (e) {
    if (isInteractionResponse(e)) return e;
    throw e;
  }
  const { component } = getQuickEditComponentByPath(
    message.components ?? [],
    path,
  );
  if (!component || component.type !== ComponentType.TextDisplay) {
    return ctx.reply({ content: missingElement, ephemeral: true });
  }

  const content = ctx.getModalComponent("content").value;
  component.content = content;

  return submitWebhookMessageEdit(
    ctx,
    webhook,
    message,
    { components: message.components },
    async () => {
      await ctx.followup.editOriginalMessage({
        components: [textDisplay("Updated text display content.")],
      });
    },
  );
};

export const quickEditSubmitSection: ModalCallback = async (ctx) => {
  const { channelId, messageId, path } = parsePathCustomId(ctx);
  let webhook: APIWebhook;
  let message: APIMessageReducedWithId;
  try {
    ({ webhook, message } = await verifyWebhookMessageEditPermissions(
      ctx,
      channelId,
      messageId,
    ));
  } catch (e) {
    if (isInteractionResponse(e)) return e;
    throw e;
  }
  const { component } = getQuickEditComponentByPath(
    message.components ?? [],
    path,
  );
  if (!component || component.type !== ComponentType.Section) {
    return ctx.reply({ content: missingElement, ephemeral: true });
  }

  for (const row of ctx.interaction.data.components) {
    const input =
      row.type === ComponentType.ActionRow
        ? row.components[0]
        : row.type === ComponentType.Label
          ? row.component
          : undefined;
    if (!input) continue;

    switch (input.type) {
      case ComponentType.TextInput:
        switch (input.custom_id) {
          // ew
          case "components.0.content":
          case "components.1.content":
          case "components.2.content": {
            const index = Number(input.custom_id.split(".")[1]);
            const text = component.components[index];
            if (!text) {
              return ctx.reply({ content: missingElement, ephemeral: true });
            }
            text.content = input.value.trim();
            break;
          }
          case "accessory.media.url":
          case "accessory.description": {
            const thumbnail = component.accessory;
            if (thumbnail.type !== ComponentType.Thumbnail) {
              return ctx.reply({ content: missingElement, ephemeral: true });
            }
            switch (input.custom_id) {
              case "accessory.media.url":
                thumbnail.media.url = input.value;
                break;
              case "accessory.description":
                thumbnail.description = input.value.trim() || undefined;
                break;
              default:
                break;
            }
            break;
          }
          default:
            break;
        }
        break;
      case ComponentType.StringSelect:
        switch (input.custom_id) {
          case "accessory.spoiler": {
            const thumbnail = component.accessory;
            if (thumbnail.type !== ComponentType.Thumbnail) {
              return ctx.reply({ content: missingElement, ephemeral: true });
            }
            thumbnail.spoiler = input.values[0] === "true";
            break;
          }
          default:
            break;
        }
        break;
      default:
        break;
    }
  }

  component.components = component.components.filter((td) =>
    Boolean(td.content),
  );
  if (component.components.length === 0) {
    return ctx.reply({
      content: "Section content cannot be empty.",
      ephemeral: true,
    });
  }

  return submitWebhookMessageEdit(
    ctx,
    webhook,
    message,
    { components: message.components },
    async (updated) => {
      await ctx.followup.editOriginalMessage({
        components: [getQuickEditSectionContainer(updated, component, path)],
      });
    },
  );
};

```

### File: `packages/bot/src/commands/reactionRoles.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  EmbedBuilder,
  messageLink,
} from "@discordjs/builders";
import type { REST } from "@discordjs/rest";
import dedent from "dedent-js";
import {
  type APIEmoji,
  type APIGuild,
  type APIGuildMember,
  type APIMessage,
  type APIPartialEmoji,
  type APIRole,
  ButtonStyle,
  CDNRoutes,
  ImageFormat,
  type RESTGetAPIGuildEmojisResult,
  RouteBases,
  Routes,
} from "discord-api-types/v10";
import { isSnowflake } from "discord-snowflake";
import { and, eq } from "drizzle-orm";
import { discordReactionRoles, getDb, makeSnowflake, upsertGuild } from "store";
import type {
  AppCommandAutocompleteCallback,
  ChatInputAppCommandCallback,
} from "../commands.js";
import type { AutoComponentCustomId, ButtonCallback } from "../components.js";
import type { Env } from "../types/env.js";
import { isActionRow, parseAutoComponentId } from "../util/components.js";
import { color } from "../util/meta.js";
import {
  autocompleteMessageCallback,
  resolveMessageLink,
} from "./components/entry.js";
import { fetchEmojiData, resolveEmojiData } from "./emojis.js";

export const isSnowflakeSafe = (id: string): id is `${bigint}` => {
  try {
    return isSnowflake(id);
  } catch {
    return false;
  }
};

export const CUSTOM_EMOJI_RE = /^<(a)?:(\w+):(\d+)>/;

export const resolveEmoji = async (
  rest: REST,
  value: string,
  message: APIMessage | undefined,
  guildId: string,
  env: Env,
): Promise<APIPartialEmoji | undefined> => {
  const match = value.match(CUSTOM_EMOJI_RE);
  if (match) {
    // Possible worry: this does not check if the bot can access the emoji.
    const response = await fetch(
      RouteBases.cdn + CDNRoutes.emoji(match[3], ImageFormat.WebP),
    );
    if (response.ok) {
      // This does not check that the emoji still exists, only that the ID was
      // once valid. We are also assuming that the name and animated flag are
      // correct.
      return {
        id: match[3],
        name: match[2],
        animated: Boolean(match[1]),
      };
    }
    return undefined;
  }

  const val = value.replace(/^:|:$/g, "");
  const messageReaction = message?.reactions?.find((r) =>
    r.emoji.id
      ? r.emoji.id === value || r.emoji.name === val
      : r.emoji.name === val,
  );
  let emoji = messageReaction?.emoji;
  // Try guild emojis
  if (!emoji) {
    const emojis = (await rest.get(
      Routes.guildEmojis(guildId),
    )) as RESTGetAPIGuildEmojisResult;
    emoji = emojis.find((e) =>
      isSnowflakeSafe(value)
        ? e.id === value || e.name === val
        : e.name === val,
    );
  }
  // Try unicode emojis
  if (!emoji) {
    try {
      const rawEmojiData = await fetchEmojiData(env);
      const { nameToEmoji, emojiToName } = resolveEmojiData(rawEmojiData);

      const query = val.toLowerCase();
      if (emojiToName.has(query)) {
        emoji = {
          id: null,
          name: query,
        };
      } else if (nameToEmoji.has(query)) {
        emoji = {
          id: null,
          // biome-ignore lint/style/noNonNullAssertion: map.has() was true
          name: nameToEmoji.get(query)!,
        };
      }
    } catch (e) {
      // Worker is probably not reachable
      console.error(e);
    }
  }
  return emoji;
};

export const messageAndEmojiAutocomplete: AppCommandAutocompleteCallback =
  async (ctx) => {
    if (ctx.getStringOption("message").focused) {
      return await autocompleteMessageCallback(ctx);
    }
    const query = ctx.getStringOption("emoji").value;

    const guildId = ctx.interaction.guild_id;
    if (!guildId) return [];

    const kvKey = `cache-autocompleteGuildEmojis-${guildId}`;
    const cached = await ctx.env.KV.get<APIPartialEmoji[]>(kvKey, "json");
    let emojis = cached;
    if (!emojis) {
      const guildEmojis = (await ctx.rest.get(
        Routes.guildEmojis(guildId),
      )) as APIEmoji[];

      emojis = guildEmojis.map(
        (e) => ({ id: e.id, name: e.name }) satisfies APIPartialEmoji,
      );

      await ctx.env.KV.put(kvKey, JSON.stringify(emojis), {
        expirationTtl: 1800,
      });
    }

    return emojis
      .filter((emoji) =>
        emoji.name?.toLowerCase().includes(query.toLowerCase()),
      )
      .map((emoji) => {
        return {
          name: emoji.name ?? "Emoji",
          value: emoji.id ?? "",
        };
      });
  };

export const getHighestRole = (guildRoles: APIRole[], roleIds: string[]) =>
  guildRoles.find(
    (r) =>
      r.id ===
      [...roleIds].sort((aId, bId) => {
        const a = guildRoles.find((r) => r.id === aId);
        const b = guildRoles.find((r) => r.id === bId);
        return a && b ? b.position - a.position : a ? 1 : -1;
      })[0],
  );

export const createReactionRoleHandler: ChatInputAppCommandCallback = async (
  ctx,
) => {
  const guildId = ctx.interaction.guild_id;
  if (!guildId) throw Error("Guild-only command");
  const guild = (await ctx.rest.get(Routes.guild(guildId))) as APIGuild;

  // biome-ignore lint/style/noNonNullAssertion: Required option
  const role = ctx.getRoleOption("role")!;
  if (role.managed) {
    return ctx.reply({
      content: `<@&${role.id}> can't be assigned to members.`,
      ephemeral: true,
    });
  }

  const me = (await ctx.rest.get(
    Routes.guildMember(guildId, ctx.env.DISCORD_APPLICATION_ID),
  )) as APIGuildMember;
  const botHighestRole = getHighestRole(guild.roles, me.roles);
  if (!botHighestRole && guild.owner_id !== ctx.env.DISCORD_APPLICATION_ID) {
    // You could be running an instance of this bot where
    // the bot is the owner of the guild
    return ctx.reply({
      content: `I can't assign <@&${role.id}> to members because I don't have any roles.`,
      ephemeral: true,
    });
  } else if (botHighestRole && role.position >= botHighestRole.position) {
    return ctx.reply({
      content: `<@&${role.id}> is higher than my highest role (<@&${botHighestRole.id}>), so I can't assign it to members. <@&${role.id}> needs to be lower in the role list, or my highest role needs to be higher.`,
      ephemeral: true,
    });
  }
  // biome-ignore lint/style/noNonNullAssertion: guild-only
  const member = ctx.interaction.member!;
  const memberHighestRole = getHighestRole(guild.roles, member.roles);
  if (guild.owner_id !== ctx.user.id) {
    // Guild owner can always do everything
    if (!memberHighestRole) {
      // This message should never be seen unless someone messes with permissions
      return ctx.reply({
        content: `You can't assign <@&${role.id}> to members because you don't have any roles.`,
        ephemeral: true,
      });
    } else if (
      memberHighestRole &&
      role.position >= memberHighestRole.position
    ) {
      return ctx.reply({
        content: `<@&${role.id}> is higher than your highest role (<@&${memberHighestRole.id}>), so you can't select it to be assigned to members. <@&${role.id}> needs to be lower in the role list, or your highest role needs to be higher.`,
        ephemeral: true,
      });
    }
  }

  const message = await resolveMessageLink(
    ctx.rest,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    return ctx.reply({
      content: message,
      ephemeral: true,
    });
  }

  const emoji = await resolveEmoji(
    ctx.rest,
    ctx.getStringOption("emoji").value,
    message,
    guildId,
    ctx.env,
  );
  if (!emoji) {
    return ctx.reply({
      content:
        "The emoji you specified couldn't be found. For best results, react to the message with the desired emoji before running this command.",
      ephemeral: true,
    });
  }

  // biome-ignore lint/style/noNonNullAssertion: Must have at least one
  const reaction = (emoji.id ?? emoji.name)!;
  const reactionMention = emoji.id
    ? `<${emoji.animated ? "a" : ""}:${emoji.name}:${emoji.id}>`
    : reaction;

  try {
    await ctx.rest.put(
      Routes.channelMessageOwnReaction(
        message.channel_id,
        message.id,
        encodeURIComponent(
          emoji.id
            ? `${emoji.animated ? "a:" : ""}${emoji.name}:${emoji.id}`
            : // biome-ignore lint/style/noNonNullAssertion: Required in this case
              emoji.name!,
        ),
      ),
    );
  } catch {
    return ctx.reply({
      content: `Failed to add the reaction (${reactionMention}) to the message.`,
      ephemeral: true,
    });
  }

  await ctx.env.KV.put(
    `discord-reaction-role-${message.id}-${reaction}`,
    JSON.stringify({ roleId: role.id }),
    { expirationTtl: 86400 }, // prev. 7x as much
  );
  const db = getDb(ctx.env.HYPERDRIVE);
  await upsertGuild(db, guild);
  await db
    .insert(discordReactionRoles)
    .values({
      guildId: makeSnowflake(guildId),
      channelId: makeSnowflake(message.channel_id),
      messageId: makeSnowflake(message.id),
      roleId: makeSnowflake(role.id),
      reaction,
    })
    .onConflictDoUpdate({
      target: [discordReactionRoles.messageId, discordReactionRoles.reaction],
      set: {
        roleId: makeSnowflake(role.id),
      },
    });
  return ctx.reply({
    embeds: [
      new EmbedBuilder()
        .setTitle("Reaction role created")
        .setColor(color)
        .addFields(
          {
            name: "Message",
            value: messageLink(message.channel_id, message.id, guildId),
            inline: true,
          },
          {
            name: "Role",
            value: `<@&${role.id}>`,
            inline: true,
          },
          {
            name: "Emoji",
            value: reactionMention,
            inline: true,
          },
          {
            name: "Not working as expected?",
            value: dedent`
              Make sure:
              - <@${ctx.interaction.application_id}> has the View Channel permission in <#${message.channel_id}>
              - <@${ctx.interaction.application_id}> has the Manage Roles permission
              - <@${ctx.interaction.application_id}>'s highest role is higher than <@&${role.id}> in the role list
            `,
            inline: false,
          },
          {
            name: "Want more power?",
            value: dedent`
              Check out components! Try **/buttons add** for more info.
            `,
            inline: false,
          },
        ),
    ],
    ephemeral: true,
  });
};

export const deleteReactionRoleHandler: ChatInputAppCommandCallback = async (
  ctx,
) => {
  const guildId = ctx.interaction.guild_id;
  if (!guildId) throw Error("Guild-only command");

  const message = await resolveMessageLink(
    ctx.rest,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    return ctx.reply({
      content: message,
      ephemeral: true,
    });
  }

  const emojiValue: string | undefined = ctx.getStringOption("emoji")?.value;
  if (emojiValue) {
    // We should only care about reactions that are actually on the message,
    // but all reactions may have been removed by accident.
    const emoji = await resolveEmoji(
      ctx.rest,
      emojiValue,
      message,
      guildId,
      ctx.env,
    );
    if (!emoji) {
      return ctx.reply({
        content:
          "The emoji you specified couldn't be found. For best results, react to the message with the desired emoji before running this command.",
        ephemeral: true,
      });
    }
    // biome-ignore lint/style/noNonNullAssertion: Must have at least one
    const reaction = (emoji.id ?? emoji.name)!;

    const db = getDb(ctx.env.HYPERDRIVE);
    const deleted = (
      await db
        .delete(discordReactionRoles)
        .where(
          and(
            eq(discordReactionRoles.messageId, makeSnowflake(message.id)),
            eq(discordReactionRoles.reaction, reaction),
          ),
        )
        .returning()
    )[0];
    try {
      await ctx.env.KV.delete(
        `discord-reaction-role-${message.id}-${reaction}`,
      );
    } catch {}

    return ctx.reply({
      ...(deleted
        ? {
            embeds: [
              new EmbedBuilder()
                .setTitle("Reaction role deleted")
                .setColor(color)
                .setDescription(dedent`
                  Message: ${messageLink(
                    message.channel_id,
                    message.id,
                    guildId,
                  )}
                  Role: <@&${deleted.roleId}>
                  Emoji: ${
                    isSnowflakeSafe(reaction) ? `<:_:${reaction}>` : reaction
                  }
                `),
            ],
          }
        : {
            content:
              "There was not a registered reaction role on that message for that emoji.",
          }),
      ephemeral: true,
    });
  }

  const db = getDb(ctx.env.HYPERDRIVE);
  const entries = await db.query.discordReactionRoles.findMany({
    where: eq(discordReactionRoles.messageId, makeSnowflake(message.id)),
  });

  if (entries.length === 0) {
    return ctx.reply({
      content: "This message has no reaction roles registered.",
      ephemeral: true,
    });
  }

  const rows: (typeof entries)[] = [];
  for (const entry of entries) {
    const lastRow = rows[rows.length - 1];
    if (!lastRow) rows.push([entry]);
    else {
      if (lastRow.length >= 5) rows.push([entry]);
      else lastRow.push(entry);
    }
    if (rows.length >= 5) break;
  }

  const { roles, emojis } = (await ctx.rest.get(
    Routes.guild(guildId),
  )) as APIGuild;

  return ctx.reply({
    content:
      'Below are all the reaction roles registered to this message. Click a button to permanently delete the reaction role. Some external emojis may not be shown, but order should be roughly correct. If a button says "Unknown Role", you should delete it.',
    components: rows.slice(0, 5).map((row) =>
      new ActionRowBuilder<ButtonBuilder>().addComponents(
        row.map((cell) => {
          const role = roles.find((r) => r.id === String(cell.roleId));
          const emoji = isSnowflakeSafe(cell.reaction)
            ? emojis.find((e) => e.id === cell.reaction)
            : { id: null, name: cell.reaction };
          return new ButtonBuilder({
            emoji: emoji
              ? {
                  animated: emoji.animated,
                  id: emoji.id ?? undefined,
                  name: emoji.name ?? undefined,
                }
              : undefined,
          })
            .setCustomId(
              `a_delete-reaction-role_${cell.messageId}:${cell.reaction}` satisfies AutoComponentCustomId,
            )
            .setStyle(ButtonStyle.Secondary)
            .setLabel(role?.name ?? "Unknown Role");
        }),
      ),
    ),
    ephemeral: true,
  });
};

export const deleteReactionRoleButtonCallback: ButtonCallback = async (ctx) => {
  const { messageId, reaction } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "messageId",
    "reaction",
  );

  const db = getDb(ctx.env.HYPERDRIVE);
  const deleted = (
    await db
      .delete(discordReactionRoles)
      .where(
        and(
          eq(discordReactionRoles.messageId, makeSnowflake(messageId)),
          eq(discordReactionRoles.reaction, reaction),
        ),
      )
      .returning({
        channelId: discordReactionRoles.channelId,
      })
  )[0];
  try {
    await ctx.env.KV.delete(`discord-reaction-role-${messageId}-${reaction}`);
  } catch {}

  if (deleted) {
    try {
      await ctx.rest.delete(
        Routes.channelMessageOwnReaction(
          String(deleted.channelId),
          messageId,
          encodeURIComponent(
            isSnowflakeSafe(reaction) ? `_:${reaction}` : reaction,
          ),
        ),
      );
    } catch {}
  }

  // Remove the button that was just clicked
  // biome-ignore lint/style/noNonNullAssertion: We're in a component callback for this message
  const components = ctx.interaction.message
    .components!.map((row) =>
      isActionRow(row)
        ? {
            ...row,
            components: row.components.filter((c) =>
              "custom_id" in c
                ? c.custom_id !== ctx.interaction.data.custom_id
                : true,
            ),
          }
        : row,
    )
    .filter((row) => !isActionRow(row) || row.components.length !== 0);

  return ctx.updateMessage({ components });
};

export const listReactionRolesHandler: ChatInputAppCommandCallback = async (
  ctx,
) => {
  const guildId = ctx.interaction.guild_id;
  if (!guildId) throw Error("Guild-only command");

  const message = await resolveMessageLink(
    ctx.rest,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    return ctx.reply({
      content: message,
      ephemeral: true,
    });
  }

  const db = getDb(ctx.env.HYPERDRIVE);
  const entries = await db.query.discordReactionRoles.findMany({
    where: eq(discordReactionRoles.messageId, makeSnowflake(message.id)),
  });

  if (entries.length === 0) {
    return ctx.reply({
      content: "This message has no reaction roles registered.",
      ephemeral: true,
    });
  }

  return ctx.reply({
    embeds: [
      new EmbedBuilder()
        .setTitle(
          `Reaction roles on ${messageLink(
            message.channel_id,
            message.id,
            guildId,
          )}`,
        )
        .setColor(color)
        .setDescription(
          entries
            .slice(0, 25)
            .map((entry) => {
              const emoji = isSnowflakeSafe(entry.reaction)
                ? `<:_:${entry.reaction}>`
                : entry.reaction;
              return `- ${emoji} - <@&${entry.roleId}>`;
            })
            .join("\n"),
        ),
    ],
    ephemeral: true,
  });
};

```

### File: `packages/bot/src/commands/restore.ts`
```ts
import {
  ActionRowBuilder,
  EmbedBuilder,
  messageLink,
  SelectMenuOptionBuilder,
  StringSelectMenuBuilder,
  time,
} from "@discordjs/builders";
import dedent from "dedent-js";
import {
  AllowedMentionsTypes,
  type APIAllowedMentions,
  type APIGuildChannel,
  type APIMessage,
  type APIMessageTopLevelComponent,
  type APIWebhook,
  ChannelType,
  ComponentType,
  type GuildChannelType,
  MessageFlags,
  MessageReferenceType,
  PermissionFlagsBits,
  RouteBases,
  Routes,
} from "discord-api-types/v10";
import { MessageFlagsBitField, PermissionFlags } from "discord-bitflag";
import { getDb, type QueryData, shareLinks, upsertDiscordUser } from "store";
import type {
  ChatInputAppCommandCallback,
  MessageAppCommandCallback,
} from "../commands.js";
import type {
  AutoComponentCustomId,
  SelectMenuCallback,
} from "../components.js";
import { getShareLinkExists, putShareLink } from "../durable/share-links.js";
import type { Env } from "../types/env.js";
import { isComponentsV2, parseAutoComponentId } from "../util/components.js";
import { isDiscordError } from "../util/error.js";
import { isThread } from "../util/guards.js";
import { boolEmoji, color } from "../util/meta.js";
import { base64UrlEncode, randomString } from "../util/text.js";
import { getUserTag } from "../util/user.js";
import { resolveMessageLink } from "./components/entry.js";
import { getWebhook } from "./webhooks/webhookInfo.js";

// essentially flattens all content components
const getAllComponentContent = (
  components: APIMessageTopLevelComponent[],
): string[] => {
  const content: string[] = [];
  for (const component of components) {
    switch (component.type) {
      case ComponentType.Container:
      case ComponentType.Section:
        content.push(...getAllComponentContent(component.components));
        break;
      case ComponentType.TextDisplay:
        content.push(component.content);
        break;
      default:
        break;
    }
  }
  return content;
};

const allowedMentionsIsBlank = (am: APIAllowedMentions) =>
  !Object.entries(am)
    .map(([, val]) => !val || val.length === 0)
    .includes(false);

export const inferAllowedMentions = (
  message: Pick<
    APIMessage,
    | "author"
    | "content"
    | "components"
    | "flags"
    | "mentions"
    | "mention_everyone"
    | "mention_roles"
  >,
) => {
  if (!message.author.bot) {
    // only bots can specify allowed mentions
    return;
  }
  const allContent = isComponentsV2(message)
    ? getAllComponentContent(message.components ?? []).join("\n")
    : message.content;

  // our strategy here ignores code blocks
  const mentionEveryone =
    allContent.includes("@everyone") || allContent.includes("@here");
  const mentionedUserIds = [...allContent.matchAll(/<@!?(\d+)>/g)]
    .map((mention) => mention[1])
    .filter((id, i, a) => a.indexOf(id) === i);
  const mentionedRoleIds = [...allContent.matchAll(/<@&(\d+)>/g)]
    .map((mention) => mention[1])
    .filter((id, i, a) => a.indexOf(id) === i);

  if (
    mentionedUserIds.length === message.mentions.length &&
    mentionedRoleIds.length === message.mention_roles.length &&
    mentionEveryone === message.mention_everyone
  ) {
    // everything is identical (barring code blocks), so
    // allowed_mentions probably was not used
    return;
  }

  const data: APIAllowedMentions = {
    parse: [],
    users: [],
    roles: [],
  };
  if (mentionedUserIds.length === message.mentions.length) {
    data.parse?.push(AllowedMentionsTypes.User);
  } else {
    data.users = message.mentions.map((u) => u.id);
  }
  if (mentionedRoleIds.length === message.mention_roles.length) {
    data.parse?.push(AllowedMentionsTypes.Role);
  } else {
    data.roles = message.mention_roles;
  }
  if (message.mention_everyone && allowedMentionsIsBlank(data)) {
    return;
  } else if (message.mention_everyone) {
    data.parse?.push(AllowedMentionsTypes.Everyone);
  }

  if (allowedMentionsIsBlank(data)) return;
  return data;
};

export const messageToQueryData = (
  ...messages: Pick<
    APIMessage,
    | "author"
    | "content"
    | "embeds"
    | "components"
    | "webhook_id"
    | "attachments"
    | "flags"
    // restore from fwd
    | "message_reference"
    | "message_snapshots"
    // recreate allowed mentions
    | "mentions"
    | "mention_everyone"
    | "mention_roles"
  >[]
): QueryData => {
  return {
    version: "d2",
    messages: messages.map((msg) => {
      // Messages that forward other messages have no content outside of the
      // snapshot, so we can reasonably assume that the user wants to restore
      // the forwarded message.
      const isForward =
        msg.message_reference?.type === MessageReferenceType.Forward &&
        !!msg.message_snapshots?.length;
      const innerMsg = isForward
        ? (msg.message_snapshots?.[0]?.message ?? msg)
        : msg;

      return {
        data: {
          content: innerMsg.content || undefined,
          embeds: !innerMsg.embeds?.length ? undefined : innerMsg.embeds,
          components: innerMsg.components,
          webhook_id: isForward ? undefined : msg.webhook_id,
          attachments: innerMsg.attachments,
          allowed_mentions: isForward ? undefined : inferAllowedMentions(msg),
          flags:
            Number(
              new MessageFlagsBitField(innerMsg.flags ?? 0).mask(
                MessageFlags.IsComponentsV2,
                MessageFlags.SuppressEmbeds,
                MessageFlags.SuppressNotifications,
              ),
            ) || undefined,
        },
      };
    }),
  };
};

// export const messageToLinkQueryData = (embeds: APIEmbed[]): LinkQueryData => {

//   return {
//     version: 1
//     embed: {
//       data: {
//         author: embed.author,
//         color: embed.color,
//         description: embed.description,
//         images:
//       },
//       redirect_url: embed.url
//     },
//   };
// };

export const getShareEmbed = (
  data: Awaited<ReturnType<typeof createShareLink>>,
  safe?: boolean,
) => {
  const embed = new EmbedBuilder()
    .setColor(color)
    .setTitle("Restored message")
    .setDescription(data.url)
    .addFields({
      name: "Expires",
      value: `${time(data.expires, "d")} (${time(data.expires, "R")})`,
      inline: true,
    });
  if (safe !== undefined) {
    embed.addFields({
      name: "Safe",
      value: `${boolEmoji(safe)} ${
        safe
          ? "This link is safe to share - it does not include a webhook URL."
          : "This link **may not be** safe to share - it includes the webhook's URL."
      }`,
      inline: true,
    });
  }
  return embed;
};

export const generateUniqueShortenKey = async (
  env: Env,
  length: number,
  tries = 10,
): Promise<string> => {
  for (const _ of Array(tries)) {
    const shareId = randomString(length);
    const exists = await getShareLinkExists(env, shareId);
    if (!exists) {
      return shareId;
    }
  }
  return await generateUniqueShortenKey(env, length + 1);
};

export const createLongDiscohookUrl = (origin: string, data: QueryData) =>
  `${origin}/?${new URLSearchParams({
    data: base64UrlEncode(JSON.stringify(data)),
  })}`;

const createShareLink = async (
  env: Env,
  data: QueryData,
  options?: {
    /** Expiration from now in milliseconds */
    ttl?: number;
    userId?: bigint;
    origin?: string;
  },
) => {
  const { userId } = options ?? {};
  const origin = options?.origin ?? env.DISCOHOOK_ORIGIN;
  const ttl = options?.ttl ?? 604800000;
  const expires = new Date(new Date().getTime() + ttl);

  delete data.backup_id;
  const shareId = await generateUniqueShortenKey(env, 8);
  await putShareLink(env, shareId, data, expires, options?.origin);
  if (userId) {
    const db = getDb(env.HYPERDRIVE);
    await db.insert(shareLinks).values({
      userId,
      shareId,
      expiresAt: expires,
      origin: options?.origin,
    });
  }

  return {
    id: shareId,
    origin,
    url: `${origin}/?share=${shareId}`,
    expires,
  };
};

/**
 * Returns whether a message could be feasibly edited using webhook credentials
 * that the bot can obtain. This does not determine whether a message absolutely
 * _can_ be edited, because it doesn't take into account whether the webhook is
 * deleted.
 */
export const isMessageWebhookEditable = (
  env: Env,
  message: Pick<
    APIMessage,
    "webhook_id" | "application_id" | "interaction_metadata" | "flags"
  >,
) => {
  const flags = new MessageFlagsBitField(message.flags ?? 0);
  if (
    message.interaction_metadata ||
    // incoming webhooks have no credentials
    flags.has(MessageFlags.IsCrosspost)
  ) {
    return false;
  }
  if (
    message.webhook_id &&
    (!message.application_id ||
      Object.keys(env.APPLICATIONS).includes(message.application_id))
  ) {
    return true;
  }
  return false;
};

export const restoreMessageEntry: MessageAppCommandCallback = async (ctx) => {
  const user = await upsertDiscordUser(getDb(ctx.env.HYPERDRIVE), ctx.user);
  const message = ctx.getMessage();

  if (!isMessageWebhookEditable(ctx.env, message)) {
    const data = messageToQueryData(message);
    const share = await createShareLink(ctx.env, data, { userId: user.id });
    return ctx.reply({
      embeds: [getShareEmbed(share, true)],
      components: [],
      ephemeral: true,
    });
  }

  const select = new StringSelectMenuBuilder()
    .setCustomId(
      `a_select-restore-options_${user.id}:${message.id}:${
        message.webhook_id ?? ""
      }` satisfies AutoComponentCustomId,
    )
    .setMaxValues(1)
    .addOptions(
      new SelectMenuOptionBuilder()
        .setLabel("Don't include edit options")
        .setDescription("The share link won't show the message's webhook URL")
        .setValue("none")
        .setEmoji({ name: "💬" }),
    );

  if (
    message.webhook_id &&
    ctx.userPermissons.has(PermissionFlagsBits.ManageWebhooks)
  ) {
    select.addOptions(
      new SelectMenuOptionBuilder()
        .setLabel("Include edit options")
        .setDescription("The share link will show the message's webhook URL")
        .setValue("edit")
        .setEmoji({ name: "🔗" }),
    );
  }

  // if (message.embeds && message.embeds.length !== 0) {
  //   select.addOptions(
  //     new SelectMenuOptionBuilder()
  //       .setLabel("[Deluxe] Restore as a link embed")
  //       .setDescription("You will be taken to the link embed editor")
  //       .setValue("link")
  //       .setEmoji({ name: "✨" }),
  //   );
  // }

  return ctx.reply({
    components: [new ActionRowBuilder<typeof select>().addComponents(select)],
    ephemeral: true,
  });
};

export const selectRestoreOptionsCallback: SelectMenuCallback = async (ctx) => {
  const { userId, messageId, webhookId } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "userId",
    "messageId",
    "webhookId",
  );

  let threadId = [
    ChannelType.PublicThread,
    ChannelType.PrivateThread,
    ChannelType.AnnouncementThread,
  ].includes(ctx.interaction.channel.type)
    ? ctx.interaction.channel.id
    : undefined;

  let message: APIMessage | undefined;
  let webhook: APIWebhook | null | undefined;
  let webhookErrorMsg: string | undefined;
  if (webhookId) {
    try {
      webhook = await getWebhook(webhookId, ctx.env);
    } catch (e) {
      if (isDiscordError(e)) webhookErrorMsg = e.rawError.message;
      webhook = null;
    }
    if (webhook?.token) {
      message = (await ctx.rest.get(
        Routes.webhookMessage(webhook.id, webhook.token, messageId),
        {
          query: threadId
            ? new URLSearchParams({ thread_id: threadId })
            : undefined,
        },
      )) as APIMessage;
    }
  }
  if (!message) {
    message = (await ctx.rest.get(
      Routes.channelMessage(ctx.interaction.channel.id, messageId),
    )) as APIMessage;
  }

  const value = (
    ctx.interaction.data.values as ("none" | "edit" | "link")[]
  )[0];

  if (
    value === "edit" &&
    !ctx.userPermissons.has(PermissionFlags.ManageWebhooks)
  ) {
    return ctx.reply({
      content:
        "You must have the manage webhooks permission to restore a message in edit mode.",
      ephemeral: true,
    });
  }

  switch (value) {
    case "none": {
      const data = messageToQueryData(message);
      // url.searchParams.set("data", base64UrlEncode(JSON.stringify(data)))
      const share = await createShareLink(ctx.env, data, {
        userId: BigInt(userId),
      });
      return ctx.updateMessage({
        embeds: [getShareEmbed(share, true)],
        components: [],
      });
    }
    case "edit": {
      if (webhook === null) {
        return ctx.updateMessage({
          content: `It looks like this webhook was deleted (ID ${webhookId}), so the message cannot be edited${
            webhookErrorMsg ? ` (${webhookErrorMsg})` : ""
          }.`,
          components: [],
        });
      }
      if (!webhook) {
        return ctx.updateMessage({
          content: "This is not a webhook message.",
          components: [],
        });
      }
      if (!webhook.token) {
        return ctx.updateMessage({
          content: [
            `Webhook token (ID ${webhookId}) was not available. `,
            "It may be an incompatible type of webhook, or it may have been ",
            "created by a different bot user.",
          ].join(""),
          components: [],
        });
      }

      let channel: APIGuildChannel<GuildChannelType> | undefined;
      if (message.channel_id !== webhook.channel_id) {
        if (message.channel_id !== ctx.interaction.channel.id) {
          try {
            channel = (await ctx.rest.get(
              Routes.channel(message.channel_id),
            )) as APIGuildChannel<GuildChannelType>;
          } catch {}
        } else {
          channel = ctx.interaction
            .channel as APIGuildChannel<GuildChannelType>;
        }

        if (channel && isThread(channel)) {
          threadId = channel.id;
        } else if (channel) {
          // The message channel is not a thread, yet it differs from the
          // webhook channel. In this instance, we attempt to move the webhook
          // so that the user can edit the message. I'm afraid that this might
          // be confusing for users who use the same webhook across multiple
          // channels a lot, but if they only use the bot to restore, everything
          // should stay in sync.
          try {
            await ctx.rest.patch(Routes.webhook(webhook.id), {
              body: { channel_id: channel.id },
              reason: `User ${getUserTag(ctx.user)} (${
                ctx.user.id
              }) restored ${messageId} to edit it, but the webhook had to be moved.`.slice(
                0,
                512,
              ),
            });
          } catch {}
        }
      }

      const data = messageToQueryData(message);
      data.messages[0].thread_id = threadId;
      data.messages[0].reference = ctx.interaction.guild_id
        ? messageLink(message.channel_id, message.id, ctx.interaction.guild_id)
        : messageLink(message.channel_id, message.id);

      data.targets = [
        {
          url: `${RouteBases.api}${Routes.webhook(webhook.id, webhook.token)}`,
        },
      ];
      const share = await createShareLink(ctx.env, data, {
        userId: BigInt(userId),
      });
      return ctx.updateMessage({
        embeds: [getShareEmbed(share, false)],
        components: [],
      });
    }
    case "link": {
      // const url = new URL(ctx.env.DISCOHOOK_ORIGIN);
      break;
    }
    default:
      break;
  }
  return ctx.reply({
    content: "This shouldn't happen!",
    ephemeral: true,
  });
};

export const restoreMessageChatInputCallback: ChatInputAppCommandCallback<
  true
> = async (ctx) => {
  const message = await resolveMessageLink(
    ctx.rest,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    return ctx.reply({ content: message, flags: MessageFlags.Ephemeral });
  }
  const mode = (ctx.getStringOption("mode").value || "none") as
    | "none"
    | "edit"
    | "link";

  const user = await upsertDiscordUser(getDb(ctx.env.HYPERDRIVE), ctx.user);
  // if (!userIsPremium(user) && mode === "link") {}
  if (
    mode === "edit" &&
    !ctx.userPermissons.has(PermissionFlags.ManageWebhooks)
  ) {
    return ctx.reply({
      content:
        "You must have the manage webhooks permission to restore a message in edit mode.",
      ephemeral: true,
    });
  }

  const data = messageToQueryData(message);

  if (!message.webhook_id || message.interaction_metadata) {
    const share = await createShareLink(ctx.env, data, { userId: user.id });
    return ctx.reply({
      embeds: [getShareEmbed(share, true)],
      ephemeral: true,
    });
  }

  switch (mode) {
    case "none": {
      const data = messageToQueryData(message);
      // url.searchParams.set("data", base64UrlEncode(JSON.stringify(data)))
      const share = await createShareLink(ctx.env, data, {
        userId: BigInt(user.id),
      });
      return ctx.reply({
        embeds: [getShareEmbed(share, true)],
        ephemeral: true,
      });
    }
    case "edit": {
      if (!message.webhook_id) {
        return ctx.reply({
          content: "This is not a webhook message.",
          ephemeral: true,
        });
      }

      const webhook = await getWebhook(
        message.webhook_id,
        ctx.env,
        message.application_id,
      );
      if (!webhook.token) {
        return ctx.reply({
          content: dedent`
            Webhook token (ID ${message.webhook_id}) was not available.
            It may be an incompatible type of webhook, or it may have been
            created by a different bot user.
          `,
          ephemeral: true,
        });
      }

      let channel: APIGuildChannel<GuildChannelType> | undefined;
      let threadId: string | undefined;
      if (message.channel_id !== webhook.channel_id) {
        if (message.channel_id !== ctx.interaction.channel.id) {
          try {
            channel = (await ctx.rest.get(
              Routes.channel(message.channel_id),
            )) as APIGuildChannel<GuildChannelType>;
          } catch {}
        } else {
          channel = ctx.interaction
            .channel as APIGuildChannel<GuildChannelType>;
        }

        if (channel && isThread(channel)) {
          threadId = channel.id;
        } else if (channel) {
          // See comment in selectRestoreOptionsCallback
          try {
            await ctx.rest.patch(Routes.webhook(webhook.id), {
              body: { channel_id: channel.id },
              reason: `User ${getUserTag(ctx.user)} (${ctx.user.id}) restored ${
                message.id
              } to edit it, but the webhook had to be moved.`.slice(0, 512),
            });
          } catch {}
        }
      }

      data.messages[0].thread_id = threadId;
      data.messages[0].reference = ctx.interaction.guild_id
        ? messageLink(message.channel_id, message.id, ctx.interaction.guild_id)
        : messageLink(message.channel_id, message.id);
      data.targets = [
        {
          url: `${RouteBases.api}${Routes.webhook(webhook.id, webhook.token)}`,
        },
      ];
      const share = await createShareLink(ctx.env, data, {
        userId: user.id,
      });
      return ctx.reply({
        embeds: [getShareEmbed(share, false)],
        ephemeral: true,
      });
    }
    case "link": {
      // const url = new URL(ctx.env.DISCOHOOK_ORIGIN);
      break;
    }
    default:
      break;
  }

  return ctx.reply({
    content: "This shouldn't happen",
    ephemeral: true,
  });
};

```

### File: `packages/bot/src/commands/triggers.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  EmbedBuilder,
} from "@discordjs/builders";
import {
  type APIInteractionGuildMember,
  ButtonStyle,
  GatewayDispatchEvents,
  type GatewayGuildMemberAddDispatchData,
  type GatewayGuildMemberRemoveDispatchData,
  type GuildMemberFlags,
} from "discord-api-types/v10";
import { PermissionFlags } from "discord-bitflag";
import { inArray } from "drizzle-orm";
import {
  FlowActionType,
  getchTriggerGuild,
  getDb,
  makeSnowflake,
  TriggerEvent,
  triggers,
  upsertDiscordUser,
} from "store";
import type {
  AppCommandAutocompleteCallback,
  ChatInputAppCommandCallback,
} from "../commands.js";
import type { ButtonCallback } from "../components.js";
import { gatewayEventNameToCallback } from "../events.js";
import { getWelcomerConfigurations } from "../events/guildMemberAdd.js";
import type { FlowResult } from "../flows/flows.js";
import type { FlowLogger } from "../flows/logger.js";
import type { InteractionContext } from "../interactions.js";
import type { Env } from "../types/env.js";
import { parseAutoComponentId } from "../util/components.js";
import { color } from "../util/meta.js";
import { spaceEnum } from "../util/regex.js";

export const addTriggerCallback: ChatInputAppCommandCallback = async (ctx) => {
  const name = ctx.getStringOption("name").value;
  const event = ctx.getIntegerOption("event").value as TriggerEvent;

  return [
    ctx.defer({ ephemeral: true }),
    async () => {
      const db = getDb(ctx.env.HYPERDRIVE);
      const guild = await getchTriggerGuild(
        ctx.rest,
        ctx.env,
        // biome-ignore lint/style/noNonNullAssertion: Guild only command
        ctx.interaction.guild_id!,
      );
      if ([TriggerEvent.MemberAdd, TriggerEvent.MemberRemove].includes(event)) {
        const configs = await getWelcomerConfigurations(
          db,
          event === TriggerEvent.MemberAdd ? "add" : "remove",
          ctx.rest,
          guild,
        );
        if (configs.length !== 0) {
          await ctx.followup.editOriginalMessage({
            content: ctx.t("triggerDuplicate"),
          });
          return;
        }
      }
      const user = await upsertDiscordUser(db, ctx.user);
      await db.insert(triggers).values({
        platform: "discord",
        event,
        discordGuildId: makeSnowflake(guild.id),
        disabled: true,
        flow: { actions: [] },
        updatedById: user.id,
      });

      await ctx.followup.editOriginalMessage({
        content: ctx.t("triggerCreated", { replace: { name } }),
        components: [
          new ActionRowBuilder<ButtonBuilder>().addComponents(
            new ButtonBuilder()
              .setStyle(ButtonStyle.Link)
              .setLabel(ctx.t("addActions"))
              .setURL(`${ctx.env.DISCOHOOK_ORIGIN}/s/${guild.id}?t=triggers`),
          ),
        ],
      });
    },
  ];
};

export const getFlowEmbed = (
  ctx: InteractionContext,
  flow: Awaited<ReturnType<typeof getWelcomerConfigurations>>[number]["flow"],
): EmbedBuilder =>
  new EmbedBuilder()
    .setTitle(flow.name ?? ctx.t("unnamedTrigger"))
    .setColor(color)
    .setDescription(
      flow.actions?.length === 0
        ? ctx.t("noActions")
        : flow.actions
            .map(
              (action, i) =>
                `${i + 1}. ${spaceEnum(FlowActionType[action.type])}${
                  action.type === FlowActionType.Wait
                    ? ` ${action.seconds}s`
                    : action.type === FlowActionType.SetVariable
                      ? ` \`${action.name}\``
                      : ""
                }`,
            )
            .join("\n"),
    );

export const viewTriggerCallback: ChatInputAppCommandCallback = async (ctx) => {
  const name = ctx.getStringOption("name").value;

  const db = getDb(ctx.env.HYPERDRIVE);
  const guild = await getchTriggerGuild(
    ctx.rest,
    ctx.env,
    // biome-ignore lint/style/noNonNullAssertion: Guild only command
    ctx.interaction.guild_id!,
  );

  // I don't like this because it causes several DB calls
  // but we need to migrate them anyway to make them into
  // triggers
  const welcomerTriggers = [
    ...(await getWelcomerConfigurations(db, "add", ctx.rest, guild)),
    ...(await getWelcomerConfigurations(db, "remove", ctx.rest, guild)),
  ];

  const trigger = welcomerTriggers.find((t) =>
    name.startsWith("_id:")
      ? t.id === BigInt(name.split(":")[1])
      : t.flow?.name === name,
  );
  if (!trigger) {
    return ctx.reply({
      content: ctx.t("noTrigger"),
      ephemeral: true,
    });
  }

  return ctx.reply({
    embeds: [getFlowEmbed(ctx, trigger.flow)],
    components: [
      new ActionRowBuilder<ButtonBuilder>().addComponents(
        new ButtonBuilder()
          .setStyle(ButtonStyle.Link)
          .setLabel(ctx.t("manageActions"))
          .setURL(
            `${ctx.env.DISCOHOOK_ORIGIN}/s/${ctx.interaction.guild_id}?t=triggers`,
          ),
      ),
      // .addComponents(
      //   await storeComponents(ctx.env.KV, [
      //     new ButtonBuilder()
      //       .setStyle(ButtonStyle.Danger)
      //       .setLabel("Delete Trigger"),
      //     {
      //       componentRoutingId: "add-component-flow",
      //       componentTimeout: 600,
      //     },
      //   ]),
      // ),
    ],
    ephemeral: true,
  });
};

export const triggerAutocompleteCallback: AppCommandAutocompleteCallback =
  async (ctx) => {
    const db = getDb(ctx.env.HYPERDRIVE);
    // This doesn't reflect pre-migration triggers (from v1 utils)
    const triggers = await db.query.triggers.findMany({
      where: (triggers, { eq }) =>
        eq(
          triggers.discordGuildId,
          // biome-ignore lint/style/noNonNullAssertion: Guild only command
          makeSnowflake(ctx.interaction.guild_id!),
        ),
      columns: { id: true, event: true, flow: true },
    });
    return triggers.map((trigger) => ({
      name:
        trigger.flow?.name ??
        (trigger.event === TriggerEvent.MemberAdd
          ? "Member Join"
          : trigger.event === TriggerEvent.MemberRemove
            ? "Member Remove"
            : ctx.t("unnamedTrigger")),
      value: `_id:${trigger.id}`,
    }));
  };

export const triggersDeleteConfirm: ButtonCallback = async (ctx) => {
  if (!ctx.userPermissons.has(PermissionFlags.ManageGuild)) {
    return ctx.updateMessage({
      content: "You don't have the Manage Guild permission.",
      embeds: [],
      components: [],
    });
  }
  const parsed = parseAutoComponentId(ctx.interaction.data.custom_id, "event");
  const event = Number(parsed.event) as TriggerEvent;

  const guildId = ctx.interaction.guild_id;
  if (!guildId) throw Error("Guild-only");

  const db = getDb(ctx.env.HYPERDRIVE);
  const results = await db.query.triggers.findMany({
    where: (triggers, { and, eq }) =>
      and(
        eq(triggers.platform, "discord"),
        eq(triggers.discordGuildId, makeSnowflake(guildId)),
        eq(triggers.event, event),
      ),
    columns: { id: true },
  });
  const triggerIds = results.map((t) => t.id);
  if (triggerIds.length === 0) {
    return ctx.updateMessage({
      content: `There are no triggers in this server with the event ${TriggerEvent[event]}.`,
      embeds: [],
      components: [],
    });
  }

  await db.delete(triggers).where(inArray(triggers.id, triggerIds));

  return ctx.updateMessage({
    content: `Deleted ${triggerIds.length} trigger${
      triggerIds.length === 1 ? "" : "s"
    } successfully.`,
    embeds: [],
    components: [],
  });
};

export const triggersDeleteCancel: ButtonCallback = async (ctx) => {
  return ctx.updateMessage({
    content: "The triggers are safe and sound.",
    embeds: [],
    components: [],
  });
};

// Replicating `/api/v1/guilds/:id/trigger-events/:event` here
// We need a lower level function so this duplication isn't necessary (or
// rather we would have an async function in the bot and call it from the
// site)
const triggerEventToDispatchEvent: Record<TriggerEvent, GatewayDispatchEvents> =
  {
    [TriggerEvent.MemberAdd]: GatewayDispatchEvents.GuildMemberAdd,
    [TriggerEvent.MemberRemove]: GatewayDispatchEvents.GuildMemberRemove,
  };

export const triggerTestButtonCallback: ButtonCallback = async (ctx) => {
  const guildId = ctx.interaction.guild_id;
  if (!guildId) throw Error("Guild-only");

  const parsed = parseAutoComponentId(ctx.interaction.data.custom_id, "event");
  const event = Number(parsed.event) as TriggerEvent;
  const eventName = triggerEventToDispatchEvent[event];

  if (!ctx.userPermissons.has(PermissionFlags.ManageGuild)) {
    return ctx.reply({
      content:
        "You must have the Manage Server permission to send test events.",
      ephemeral: true,
    });
  }

  let payload: any = {};
  const func = gatewayEventNameToCallback[eventName] as (
    env: Env,
    payload: any,
    deferred?: boolean,
  ) => Promise<FlowResult[] | undefined> | undefined;
  switch (event) {
    case TriggerEvent.MemberAdd: {
      payload = {
        ...(ctx.interaction.member ??
          ({
            user: ctx.user,
            deaf: false,
            mute: false,
            joined_at: new Date().toISOString(),
            permissions: "0",
            roles: [],
            flags: 0 as GuildMemberFlags,
          } satisfies APIInteractionGuildMember)),
        guild_id: guildId,
      } satisfies GatewayGuildMemberAddDispatchData;
      break;
    }
    case TriggerEvent.MemberRemove: {
      payload = {
        user: ctx.user,
        guild_id: guildId,
      } satisfies GatewayGuildMemberRemoveDispatchData;
      break;
    }
    default:
      return ctx.reply({
        content: "No dispatch data could be formed for the event",
        ephemeral: true,
      });
  }
  if (!func) {
    return ctx.reply({
      content: `There was no function for the event \`${eventName}\``,
      ephemeral: true,
    });
  }

  return [
    ctx.defer({ thinking: true, ephemeral: true }),
    async () => {
      const started = Date.now();
      const results = await Promise.race([
        (async (): Promise<FlowResult[]> => {
          try {
            const flowResults = <FlowResult[] | undefined>(
              await func(ctx.env, payload, true)
            );
            return flowResults ?? [];
          } catch (e) {
            return [
              {
                status: "failure",
                message: `Function failed to complete: ${e}`,
              },
            ];
          }
        })(),
        promiseTimeout<FlowResult[]>(840_000, [
          {
            status: "failure",
            message: "Timeout after 14m",
          },
        ]),
      ]);
      const ended = Date.now();
      await ctx.followup.editOriginalMessage({
        embeds: [
          getFlowDiagnosticEmbed(results, started, ended).addFields({
            name: "Management",
            value:
              "View all actions in this trigger with </triggers view:1281305550340096033>",
            inline: true,
          }),
        ],
      });
    },
  ];
};

// https://stackoverflow.com/a/48578424
export const promiseTimeout = <T = any>(ms: number, val: T) =>
  new Promise<T>((resolve) => {
    setTimeout(resolve.bind(null, val), ms);
  });

export const getFlowDiagnosticEmbed = (
  results: FlowResult[],
  started: number,
  ended: number,
  logger?: FlowLogger,
) => {
  let description = "";
  const descFooter = results
    .map((r) => {
      const firstLine = `${results.length === 1 ? "" : "- "}<:_:${
        r.status === "success"
          ? "1263857933209571329" // true emoji
          : "1263857948086505482" // false emoji
      }> ${r.message ?? "no message"}`;
      if (r.discordError) {
        return `${firstLine}\n[${r.discordError.code}] ${r.discordError.message}`;
      }
      return firstLine;
    })
    .join("\n")
    .slice(0, 4096);
  for (const message of logger?.messages ?? []) {
    const full = `${description}\n${message.toString()}`;
    const part = `${description}\n…`;

    if (`${full}\n${descFooter}`.length > 4096) {
      if (`${part}\n${descFooter}`.length > 4096) {
        break;
      } else {
        description = part;
        break;
      }
    } else {
      description = full;
    }
  }
  description += `\n${descFooter}`;

  return new EmbedBuilder()
    .setTitle("Results")
    .setColor(color)
    .setDescription(description.trim())
    .setFields({
      name: "Diagnostic",
      value: `${results.length} result${
        results.length === 1 ? "" : "s"
      } in ${Math.ceil(ended - started)}ms`,
      inline: true,
    });
};

```

### File: `packages/bot/src/commands/webhooks/autocomplete.ts`
```ts
import {
  type APIGuildChannel,
  type APIWebhook,
  type GuildChannelType,
  Routes,
  WebhookType,
} from "discord-api-types/v10";
import type { AppCommandAutocompleteCallback } from "../../commands.js";

export const webhookAutocomplete: AppCommandAutocompleteCallback = async (
  ctx,
) => {
  // biome-ignore lint/style/noNonNullAssertion: only guild-only commands use this function
  const guildId = ctx.interaction.guild_id!;
  const query = ctx.getStringOption("webhook").value.trim();
  const channel = ctx.getAutocompleteChannelOption("filter-channel");

  // TODO: Use KV here, or query DB if we're confident enough in it

  const [guildWebhooks, channels] = await Promise.all([
    ctx.rest.get(Routes.guildWebhooks(guildId)) as Promise<APIWebhook[]>,
    (async () => {
      if (channel) return [];
      try {
        return await ctx.rest.get(Routes.guildChannels(guildId));
      } catch {
        return [];
      }
    })() as Promise<APIGuildChannel<GuildChannelType>[]>,
  ]);
  // TODO: Make this 'search' function better in the future
  const matches = guildWebhooks
    .filter(
      (w) =>
        w.type === WebhookType.Incoming &&
        w.name &&
        w.name.toLowerCase().includes(query.toLowerCase()) &&
        (channel ? w.channel_id === channel.id : true),
    )
    .sort((a, b) => {
      const alphabeticalScore = (a.name ?? "") > (b.name ?? "") ? -1 : 1;

      const channelA = channels.find((c) => c.id === a.channel_id);
      const channelB = channels.find((c) => c.id === b.channel_id);
      if (channelA && channelB) {
        return (
          channelA.position -
          channelB.position +
          (a.channel_id === b.channel_id ? alphabeticalScore : 0)
        );
      } else if (channelA) {
        return -1;
      }
      return alphabeticalScore;
    });

  return matches.map((w) => {
    const channelHead = channel
      ? ""
      : `#${channels.find((c) => c.id === w.channel_id)?.name ?? "unknown"}: `;
    const userTail = w.user
      ? ` | ${w.user.global_name ?? w.user.username}`
      : "";
    return {
      name: `${channelHead}${w.name}${userTail}`.slice(0, 100),
      value: w.id,
    };
  });
};

```

### File: `packages/bot/src/commands/webhooks/webhookCreate.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  EmbedBuilder,
} from "@discordjs/builders";
import dedent from "dedent-js";
import {
  type APIInteraction,
  type APIWebhook,
  ButtonStyle,
  ChannelType,
  RESTJSONErrorCodes,
  Routes,
} from "discord-api-types/v10";
import { and, eq } from "drizzle-orm";
import {
  getchGuild,
  getDb,
  makeSnowflake,
  upsertDiscordUser,
  upsertGuild,
  webhooks,
} from "store";
import type { ChatInputAppCommandCallback } from "../../commands.js";
import { getErrorEmbed } from "../../errors.js";
import type { APIPartialResolvedChannel } from "../../types/api.js";
import { readAttachment } from "../../util/cdn.js";
import { isDiscordError } from "../../util/error.js";
import { color } from "../../util/meta.js";
import { sleep } from "../../util/sleep.js";
import { getUserTag } from "../../util/user.js";
import { getWebhookUrlEmbed } from "./webhookInfo.js";

export const extractWebhookableChannel = (
  channel: APIPartialResolvedChannel | null,
  ctxChannel: APIInteraction["channel"],
): [string | undefined, ChannelType | undefined] => {
  let channelId: string | undefined;
  let channelType: ChannelType | undefined = ctxChannel?.type;
  if (channel) {
    channelType = channel.type;
    if (
      [
        ChannelType.PublicThread,
        ChannelType.PrivateThread,
        ChannelType.AnnouncementThread,
      ].includes(channel.type) &&
      "parent_id" in channel
    ) {
      // All threadable channels should also be webhook-compatible
      channelId = channel.parent_id ?? undefined;
    } else {
      channelId = channel.id;
    }
  } else if (ctxChannel) {
    if (
      [
        ChannelType.GuildAnnouncement,
        ChannelType.GuildText,
        ChannelType.GuildVoice,
        ChannelType.GuildForum,
        ChannelType.GuildMedia,
      ].includes(ctxChannel.type)
    ) {
      channelId = ctxChannel.id;
    } else if (
      [
        ChannelType.PublicThread,
        ChannelType.PrivateThread,
        ChannelType.AnnouncementThread,
      ].includes(ctxChannel.type) &&
      "parent_id" in ctxChannel
    ) {
      channelId = ctxChannel.parent_id ?? undefined;
    }
  }

  return [channelId, channelType];
};

export const webhookCreateEntry: ChatInputAppCommandCallback<true> = async (
  ctx,
) => {
  const name = ctx.getStringOption("name").value;
  const avatar = ctx.getAttachmentOption("avatar");
  const channel = ctx.getChannelOption("channel");
  const showUrl = ctx.getBooleanOption("show-url").value;

  const [channelId, channelType] = extractWebhookableChannel(
    channel,
    ctx.interaction.channel,
  );
  if (!channelId) {
    return ctx.reply({
      content: `Invalid channel type.${
        !channel ? " To specify a channel, use the `channel` argument." : ""
      }`,
      ephemeral: true,
    });
  }

  return [
    // Defer because attachment handling takes so long
    ctx.defer({ ephemeral: true }),
    async () => {
      let avatarData: string | undefined;
      if (avatar) {
        if (
          !avatar.content_type ||
          !["image/png", "image/jpeg", "image/gif", "image/webp"].includes(
            avatar.content_type,
          )
        ) {
          await ctx.followup.editOriginalMessage({
            content:
              "Invalid attachment type. Must be a PNG, JPEG/JPG, GIF, or WebP image.",
          });
          return;
        }

        try {
          avatarData = await readAttachment(avatar.url);
        } catch (e) {
          if (e instanceof RangeError) {
            console.error(e);
            await ctx.followup.editOriginalMessage({
              content:
                "Failed to handle the file, it may be too large or it may be malformed.",
            });
            return;
          } else {
            console.error(e);
            await ctx.followup.editOriginalMessage({
              content:
                "Failed to handle the file. Try creating a webhook without an avatar and uploading it later.",
            });
            return;
          }
        }
      }

      let webhook: APIWebhook;
      try {
        webhook = (await ctx.rest.post(Routes.channelWebhooks(channelId), {
          body: { name, avatar: avatarData },
          reason: `${getUserTag(ctx.user)} (${ctx.user.id}) via /webhook create`,
        })) as APIWebhook;
      } catch (e) {
        if (isDiscordError(e)) {
          if (
            [
              RESTJSONErrorCodes.MaximumNumberOfWebhooksReached,
              RESTJSONErrorCodes.MaximumNumberOfWebhooksPerGuildReached,
            ].includes(e.code)
          ) {
            await ctx.followup.editOriginalMessage({
              content: e.rawError.message,
            });
            return;
          }
          await ctx.followup.editOriginalMessage({
            content:
              "Failed to create the webhook. It is likely that some information was invalid or I am missing permissions. A description of the error is below:",
            embeds: [getErrorEmbed(e.rawError, ctx.isDeveloper)],
          });
          return;
        }
        await ctx.followup.editOriginalMessage({
          content: "Failed to create the webhook.",
        });
        return;
      }

      const embed = getWebhookUrlEmbed(
        webhook,
        "Webhook Created",
        ctx.followup.applicationId,
        channelType ?? ctx.interaction.channel.type,
        showUrl,
      );

      const row = new ActionRowBuilder<ButtonBuilder>().addComponents(
        new ButtonBuilder()
          .setStyle(ButtonStyle.Link)
          .setLabel("Use in Discohook")
          .setURL(
            `${ctx.env.DISCOHOOK_ORIGIN}/?data=${Buffer.from(
              JSON.stringify({
                messages: [{ data: {} }],
                targets: [{ url: webhook.url }],
              }),
              "utf8",
            ).toString("base64")}`,
          ),
        // new ButtonBuilder()
        //   .setCustomId(`a_webhook-info-show-url_${webhook.id}`)
        //   .setLabel("Show URL (advanced)")
        //   .setStyle(ButtonStyle.Secondary),
      );

      const db = getDb(ctx.env.HYPERDRIVE);
      const guild = await getchGuild(
        ctx.rest,
        ctx.env,
        ctx.interaction.guild_id,
      );
      await upsertGuild(db, guild);
      const dbUser = await upsertDiscordUser(db, ctx.user);
      await db
        .insert(webhooks)
        .values({
          platform: "discord",
          id: webhook.id,
          token: webhook.token,
          name: webhook.name ?? name,
          // biome-ignore lint/style/noNonNullAssertion: we are in a guild
          discordGuildId: makeSnowflake(webhook.guild_id!),
          channelId: webhook.channel_id,
          avatar: webhook.avatar,
          applicationId: webhook.application_id,
          userId: dbUser.id,
        })
        .onConflictDoNothing();

      await ctx.followup.editOriginalMessage({
        embeds: [embed],
        components: [row],
      });

      await sleep(2000);
      try {
        await ctx.rest.get(Routes.webhook(webhook.id, webhook.token));
      } catch (e) {
        if (isDiscordError(e) && e.code === RESTJSONErrorCodes.UnknownWebhook) {
          await ctx.followup.editOriginalMessage({
            embeds: [
              new EmbedBuilder()
                .setTitle("Webhook was deleted")
                .setColor(color)
                .setDescription(dedent`
                  Your webhook was created successfully, but it seems like a
                  moderation bot may have deleted it automatically. Some bots
                  detect new webhooks as spam activity. Check your server audit
                  log for more details.
                `),
            ],
            components: [],
          });
          await db
            .delete(webhooks)
            .where(
              and(
                eq(webhooks.id, webhook.id),
                eq(webhooks.platform, "discord"),
              ),
            );
        }
      }
    },
  ];
};

```

### File: `packages/bot/src/commands/webhooks/webhookDelete.ts`
```ts
import { ActionRowBuilder, ButtonBuilder } from "@discordjs/builders";
import { type APIWebhook, ButtonStyle, Routes } from "discord-api-types/v10";
import { PermissionFlags } from "discord-bitflag";
import { and, count, eq } from "drizzle-orm";
import { getDb, messageLogEntries, webhooks } from "store";
import type { ChatInputAppCommandCallback } from "../../commands.js";
import type {
  AutoComponentCustomId,
  ButtonCallback,
} from "../../components.js";
import { parseAutoComponentId } from "../../util/components.js";
import { getUserTag } from "../../util/user.js";
import { getWebhookInfoEmbed } from "./webhookInfo.js";

export const webhookDeleteEntryCallback: ChatInputAppCommandCallback<
  true
> = async (ctx) => {
  const webhookId = ctx.getStringOption("webhook").value;
  const webhook = (await ctx.rest.get(Routes.webhook(webhookId))) as APIWebhook;
  const embed = getWebhookInfoEmbed(webhook);

  // Originally delegated this to a followup but it sometimes happened so
  // quickly that it completed before Discord had downloaded the initial
  // response. This will definitely change in production, but I think it
  // should be fine to keep in the response.
  const db = getDb(ctx.env.HYPERDRIVE);
  const [{ logs }] = await db
    .select({ logs: count() })
    .from(messageLogEntries)
    .where(
      and(
        eq(messageLogEntries.type, "send"),
        eq(messageLogEntries.webhookId, webhookId),
      ),
    );
  if (logs !== 0) {
    embed.addFields({
      name: "Logs",
      value: ctx.t("gteNMessagesSent", { count: logs }),
      inline: true,
    });
  }

  // This currently doesn't work because no results are returned when querying
  // `author_id` with a webhook ID, despite `author_type` being an acceptable
  // way to search for webhook messages.
  // const data = (await ctx.rest.get(
  //   `/guilds/${ctx.interaction.guild_id}/messages/search`,
  //   {
  //     query: new URLSearchParams({
  //       // I think "latest message sent" would be a useful diagnostic
  //       sort_by: "timestamp",
  //       author_id: webhookId,
  //       author_type: "webhook",
  //       limit: "1",
  //     }),
  //   },
  // )) as { total_results: number };

  return ctx.reply({
    content: ctx.t("webhookDelete.confirm"),
    embeds: [embed],
    components: [
      new ActionRowBuilder<ButtonBuilder>().setComponents(
        new ButtonBuilder()
          .setCustomId(
            `a_webhook-delete-confirm_${webhookId}` satisfies AutoComponentCustomId,
          )
          .setLabel("Delete")
          .setStyle(ButtonStyle.Danger),
        new ButtonBuilder()
          .setCustomId(
            "a_webhook-delete-cancel_" satisfies AutoComponentCustomId,
          )
          .setLabel("Cancel")
          .setStyle(ButtonStyle.Secondary),
      ),
    ],
    ephemeral: true,
  });
};

export const webhookDeleteConfirm: ButtonCallback = async (ctx) => {
  if (!ctx.userPermissons.has(PermissionFlags.ManageWebhooks)) {
    return ctx.updateMessage({
      content: ctx.t("webhookDelete.forbidden"),
      embeds: [],
      components: [],
    });
  }
  const { webhookId } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "webhookId",
  );
  const webhook = (await ctx.rest.get(Routes.webhook(webhookId))) as APIWebhook;
  if (!webhook.guild_id || webhook.guild_id !== ctx.interaction.guild_id) {
    return ctx.updateMessage({
      content: ctx.t("webhookDelete.wrongServer"),
      embeds: [],
      components: [],
    });
  }

  await ctx.rest.delete(Routes.webhook(webhookId), {
    reason: `${getUserTag(ctx.user)} (${ctx.user.id}) via /webhook delete`,
  });

  const db = getDb(ctx.env.HYPERDRIVE);
  await db
    .delete(webhooks)
    .where(and(eq(webhooks.platform, "discord"), eq(webhooks.id, webhookId)));

  return ctx.updateMessage({
    content: ctx.t("webhookDelete.success"),
    embeds: [],
    components: [],
  });
};

export const webhookDeleteCancel: ButtonCallback = async (ctx) => {
  return ctx.updateMessage({
    content: ctx.t("webhookDelete.cancel"),
    embeds: [],
    components: [],
  });
};

```

### File: `packages/bot/src/commands/webhooks/webhookInfo.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  EmbedBuilder,
  inlineCode,
  spoiler,
  TimestampStyles,
  time,
} from "@discordjs/builders";
import { REST } from "@discordjs/rest";
import dedent from "dedent-js";
import {
  type APIMessageComponentButtonInteraction,
  type APIWebhook,
  ButtonStyle,
  ChannelType,
  RouteBases,
  Routes,
  WebhookType,
} from "discord-api-types/v10";
import { PermissionFlags } from "discord-bitflag";
import { getDate, type Snowflake } from "discord-snowflake";
import { and, eq, sql } from "drizzle-orm";
import { getDb, webhooks } from "store";
import type { ChatInputAppCommandCallback } from "../../commands.js";
import type { ButtonCallback } from "../../components.js";
import type { InteractionContext } from "../../interactions.js";
import type { Env } from "../../types/env.js";
import { webhookAvatarUrl } from "../../util/cdn.js";
import { parseAutoComponentId } from "../../util/components.js";
import { color } from "../../util/meta.js";
import { createREST } from "../../util/rest.js";
import { createLongDiscohookUrl } from "../restore.js";

export const getWebhookInfoEmbed = (webhook: APIWebhook) => {
  const createdAt = getDate(webhook.id as Snowflake);

  return new EmbedBuilder({
    title: "Webhook Info",
    color,
    thumbnail: {
      url: webhookAvatarUrl(webhook, { size: 1024 }),
    },
    fields: [
      {
        name: "Name",
        value: (webhook.name || "...").slice(0, 1024),
        inline: true,
      },
      {
        name: "Channel",
        value: `<#${webhook.channel_id}>`,
        inline: true,
      },
      {
        name: "ID",
        value: webhook.id,
        inline: true,
      },
      {
        name: "Created by",
        value: webhook.user ? `<@${webhook.user.id}>` : "Unknown",
        inline: true,
      },
      {
        name: "Created at",
        value: `${time(createdAt, TimestampStyles.ShortDate)} (${time(
          createdAt,
          TimestampStyles.RelativeTime,
        )})`,
        inline: true,
      },
    ],
  });
};

export const getWebhookUrlEmbed = (
  webhook: APIWebhook,
  header?: string,
  applicationId?: string,
  channelType?: ChannelType,
  showUrl?: boolean,
) => {
  const title = header ?? "Webhook URL";

  if (!webhook.token) {
    return new EmbedBuilder({
      title,
      description: dedent`
        This webhook\'s token is not available. It may have been created by a\
        different bot or it may be a news webhook (from a different server).
      `,
      color,
    });
  }

  const url = getWebhookUrl(webhook);
  const embed = new EmbedBuilder({
    title,
    description: showUrl
      ? spoiler(inlineCode(url))
      : `**${webhook.name}** in <#${webhook.channel_id}>`,
    color,
  });

  if (showUrl) {
    embed.setAuthor({
      name: webhook.name ?? "Webhook",
      iconURL: webhookAvatarUrl(webhook, { size: 128 }),
    });
  } else {
    embed.setThumbnail(webhookAvatarUrl(webhook, { size: 1024 }));
  }

  // Surely this is not necessary?
  // embed.addFields({
  //   name: ":information_source: Usage",
  //   value: dedent`
  //       Click "Open in Discohook". Compose your message and click send to create a new message.
  //       If you need the webhook URL for another application,
  //     `,
  //   inline: false,
  // });

  embed.addFields(
    webhook.application_id && applicationId === webhook.application_id
      ? {
          name: ":white_check_mark: Buttons & Selects",
          value:
            "This webhook is owned by Discohook, so its messages can have components.",
          inline: false,
        }
      : {
          name: ":x: Buttons & Selects",
          value: "This webhook is not owned by Discohook.",
          inline: false,
        },
  );

  if (
    channelType === ChannelType.GuildForum ||
    channelType === ChannelType.GuildMedia
  ) {
    embed.addFields({
      name: "<:forum:1074458133407211562> Forum/media channels",
      value: dedent`
          <#${webhook.channel_id}> is a thread-only channel. In order to create a new\
          post using Discohook, click "Thread" and fill in the "Forum Thread Name" box.\
          If you want to send to an existing thread, paste the ID of the thread in the\
          "Thread ID" box.\
          [Read how to get a thread ID](https://support.discord.com/hc/en-us/articles/206346498)\
          or use </id channel:1281305550340096032>.
        `,
      inline: false,
    });
  }

  if (showUrl) {
    embed.addFields({
      name: ":warning: Keep this secret!",
      value: dedent`
        Someone who can see this URL can send any message they want in\
        <#${webhook.channel_id}>, including scams and \`@everyone\` mentions.\
        We are not able to screen messages sent by users.
      `,
      inline: false,
    });
  }

  return embed;
};

export const getWebhook = async (
  webhookId: string,
  env: Env,
  webhookApplicationId?: string,
): Promise<APIWebhook> => {
  let tryAppId = webhookApplicationId;
  let token = webhookApplicationId
    ? env.APPLICATIONS[webhookApplicationId]
    : env.DISCORD_TOKEN;
  if (!token) {
    tryAppId = env.DISCORD_APPLICATION_ID;
    token = env.DISCORD_TOKEN;
  }
  const key = `cache-webhook-${webhookId}`;
  const cached = await env.KV.get<APIWebhook>(key, "json");
  // Only return cached result if we already have the token
  // or wouldn't be able to retrieve it
  if (
    cached &&
    (cached.token ||
      cached.type !== WebhookType.Incoming ||
      (cached.application_id && !env.APPLICATIONS[cached.application_id]))
  ) {
    return cached;
  }

  const rest =
    token === env.DISCORD_TOKEN ? createREST(env) : new REST().setToken(token);
  const webhook = (await rest.get(Routes.webhook(webhookId))) as APIWebhook;
  if (webhook.token || webhook.type !== WebhookType.Incoming) {
    // Non-incoming webhooks don't have tokens
    await env.KV.put(key, JSON.stringify(webhook), { expirationTtl: 600 });
    return webhook;
  }

  if (webhook.application_id && tryAppId !== webhook.application_id) {
    if (env.APPLICATIONS[webhook.application_id]) {
      // env check ensures we don't enter infinite recursion
      return await getWebhook(webhook.id, env, webhook.application_id);
    }
    // 10 minutes
    await env.KV.put(key, JSON.stringify(webhook), { expirationTtl: 600 });
    return webhook;
  }

  throw Error("Could not retrieve the webhook.");
};

export const webhookInfoCallback: ChatInputAppCommandCallback = async (ctx) => {
  const webhookId = ctx.getStringOption("webhook").value;
  const showUrl = ctx.getBooleanOption("show-url")?.value ?? false;
  const webhook = showUrl
    ? // if we're going to need the URL right away, bother with the possible extra fetch
      await getWebhook(webhookId, ctx.env)
    : ((await ctx.rest.get(Routes.webhook(webhookId))) as APIWebhook);

  const tokenAccessible = webhook.application_id
    ? !!ctx.env.APPLICATIONS[webhook.application_id]
    : webhook.type === WebhookType.Incoming;

  const embeds = [getWebhookInfoEmbed(webhook)];
  if (showUrl) {
    embeds.push(
      getWebhookUrlEmbed(
        webhook,
        undefined,
        ctx.interaction.application_id,
        webhook.channel_id === ctx.interaction.channel.id
          ? ctx.interaction.channel.type
          : undefined,
        showUrl,
      ),
    );
  }

  if (
    !showUrl &&
    ctx.userPermissons.has(PermissionFlags.ManageWebhooks) &&
    !webhook.token &&
    !tokenAccessible
  ) {
    embeds[0].setFooter({
      // This basically just means that if another bot created the webhook and
      // lets you see the token then you can provide it yourself on the website.
      // But that's a little wordy and I'm not sure how many cases there are
      // where that's useful information for people.
      text: "Discohook cannot see this webhook's token, so it cannot be used unless you provide the URL manually. Try creating a new webhook with Discohook.",
    });
  }

  const components =
    !showUrl && ctx.userPermissons.has(PermissionFlags.ManageWebhooks)
      ? [
          new ActionRowBuilder<ButtonBuilder>().addComponents(
            new ButtonBuilder()
              .setCustomId(`a_webhook-info-use_${webhook.id}`)
              .setLabel("Use Webhook")
              .setDisabled(!webhook.token && !tokenAccessible)
              .setStyle(ButtonStyle.Primary),
            new ButtonBuilder()
              .setCustomId(`a_webhook-info-show-url_${webhook.id}`)
              .setLabel("Show URL (advanced)")
              .setDisabled(!webhook.token && !tokenAccessible)
              .setStyle(ButtonStyle.Secondary),
          ),
        ]
      : undefined;

  return ctx.reply({
    embeds,
    components,
    ephemeral: showUrl,
  });
};

const processUseWebhookButtonBoilerplate = async (
  ctx: InteractionContext<APIMessageComponentButtonInteraction>,
) => {
  if (!ctx.userPermissons.has(PermissionFlags.ManageWebhooks)) {
    return ctx.reply({
      content: "You need the manage webhooks permission.",
      ephemeral: true,
    });
  }
  const guildId = ctx.interaction.guild_id;
  if (!guildId) {
    return ctx.reply({
      content: "This is a guild-only operation.",
      ephemeral: true,
    });
  }

  const { webhookId } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "webhookId",
  );

  const db = getDb(ctx.env.HYPERDRIVE);
  const dbWebhook = await db.query.webhooks.findFirst({
    where: and(eq(webhooks.platform, "discord"), eq(webhooks.id, webhookId)),
    columns: { token: true },
  });

  const webhook = await getWebhook(webhookId, ctx.env);
  if (!webhook.guild_id || webhook.guild_id !== guildId) {
    return ctx.reply({
      content: "This webhook belongs to a different server.",
      ephemeral: true,
    });
  }

  db.insert(webhooks)
    .values({
      platform: "discord",
      id: webhook.id,
      name: webhook.name ?? "",
      token: webhook.token ?? dbWebhook?.token,
      avatar: webhook.avatar,
      channelId: webhook.channel_id,
      applicationId: webhook.application_id,
      discordGuildId: BigInt(webhook.guild_id ?? guildId),
    })
    .onConflictDoUpdate({
      target: [webhooks.platform, webhooks.id],
      set: {
        name: sql`excluded.name`,
        token: sql`excluded.token`,
        avatar: sql`excluded.avatar`,
        channelId: sql`excluded."channelId"`,
        discordGuildId: sql`excluded."discordGuildId"`,
      },
    })
    .catch(console.error);

  if (!webhook.token) {
    if (dbWebhook?.token) {
      webhook.token = dbWebhook.token;
    } else {
      return ctx.reply({
        content: "The webhook's token is not available.",
        ephemeral: true,
      });
    }
  }

  return webhook;
};

export const getWebhookUrl = (
  webhook: Pick<APIWebhook, "id" | "token" | "url">,
): string =>
  webhook.url ?? RouteBases.api + Routes.webhook(webhook.id, webhook.token);

export const webhookInfoUseCallback: ButtonCallback = async (ctx) => {
  const webhook = await processUseWebhookButtonBoilerplate(ctx);
  if (!("id" in webhook)) return webhook;
  webhook.token;

  const url = createLongDiscohookUrl(ctx.env.DISCOHOOK_ORIGIN, {
    version: "d2",
    messages: [{ data: {} }],
    targets: [{ url: getWebhookUrl(webhook) }],
  });

  return ctx.reply({
    content:
      "Click the button to start a new Discohook message with this webhook preloaded.",
    components: [
      new ActionRowBuilder<ButtonBuilder>().addComponents(
        new ButtonBuilder()
          .setStyle(ButtonStyle.Link)
          .setLabel("Open Discohook")
          .setURL(url),
      ),
    ],
    ephemeral: true,
  });
};

export const webhookInfoShowUrlCallback: ButtonCallback = async (ctx) => {
  const webhook = await processUseWebhookButtonBoilerplate(ctx);
  if (!("id" in webhook)) return webhook;

  const embed = getWebhookUrlEmbed(
    webhook,
    undefined,
    ctx.env.DISCORD_APPLICATION_ID,
    // TODO: always provide channel type
    ctx.interaction.channel.id === webhook.channel_id
      ? ctx.interaction.channel.type
      : undefined,
    true,
  );
  return ctx.reply({
    embeds: [embed],
    ephemeral: true,
  });
};

```

### File: `packages/bot/src/commands/webhooks/webhookInfoMsg.ts`
```ts
import { ActionRowBuilder, ButtonBuilder } from "@discordjs/builders";
import {
  type APIWebhook,
  ButtonStyle,
  Routes,
  WebhookType,
} from "discord-api-types/v10";
import { PermissionFlags } from "discord-bitflag";
import type { MessageAppCommandCallback } from "../../commands.js";
import { createLongDiscohookUrl } from "../restore.js";
import { getWebhookInfoEmbed, getWebhookUrl } from "./webhookInfo.js";

export const webhookInfoMsgCallback: MessageAppCommandCallback = async (
  ctx,
) => {
  const msg = ctx.getMessage();
  if (!msg.webhook_id) {
    return ctx.reply({
      content: "This is not a webhook message.",
      ephemeral: true,
    });
  }

  const webhook = (await ctx.rest.get(
    Routes.webhook(msg.webhook_id),
  )) as APIWebhook;
  const tokenAccessible = webhook.application_id
    ? !!ctx.env.APPLICATIONS[webhook.application_id]
    : webhook.type === WebhookType.Incoming;

  const url = webhook.token
    ? createLongDiscohookUrl(ctx.env.DISCOHOOK_ORIGIN, {
        version: "d2",
        messages: [{ data: {} }],
        targets: [{ url: getWebhookUrl(webhook) }],
      })
    : ctx.env.DISCOHOOK_ORIGIN;

  const components = ctx.userPermissons.has(PermissionFlags.ManageWebhooks)
    ? [
        new ActionRowBuilder<ButtonBuilder>().addComponents(
          new ButtonBuilder()
            .setLabel("Use Webhook")
            .setDisabled(!webhook.token && !tokenAccessible)
            .setURL(url)
            .setStyle(ButtonStyle.Link),
          new ButtonBuilder()
            .setCustomId(`a_webhook-info-show-url_${webhook.id}`)
            .setLabel("Show URL (advanced)")
            .setDisabled(!webhook.token && !tokenAccessible)
            .setStyle(ButtonStyle.Secondary),
        ),
      ]
    : undefined;

  return ctx.reply({
    embeds: [getWebhookInfoEmbed(webhook)],
    components,
    ephemeral: true,
  });
};

```

### File: `packages/bot/src/commands/welcomer/delete.ts`
```ts
import { ActionRowBuilder, ButtonBuilder } from "@discordjs/builders";
import { ButtonStyle } from "discord-api-types/v10";
import { getchTriggerGuild, getDb, TriggerEvent } from "store";
import type { ChatInputAppCommandCallback } from "../../commands.js";
import type { AutoComponentCustomId } from "../../components.js";
import { getWelcomerConfigurations } from "../../events/guildMemberAdd.js";
import type { WelcomerTriggerEvent } from "./set.js";

export const welcomerDeleteEntry: ChatInputAppCommandCallback<true> = async (
  ctx,
) => {
  const event = ctx.getIntegerOption("event").value as WelcomerTriggerEvent;

  const guild = await getchTriggerGuild(
    ctx.rest,
    ctx.env,
    ctx.interaction.guild_id,
  );

  const db = getDb(ctx.env.HYPERDRIVE);
  const triggers = await getWelcomerConfigurations(
    db,
    event === TriggerEvent.MemberAdd ? "add" : "remove",
    ctx.rest,
    guild,
  );

  if (triggers.length === 0) {
    return ctx.reply({
      content: "This server has no triggers with that event.",
      ephemeral: true,
    });
  }

  return ctx.reply({
    content: `Are you sure you want to delete these triggers?\n${triggers
      .map((t) => `- ${t.flow.name ?? TriggerEvent[event]}`)
      .join("\n")}`,
    ephemeral: true,
    components: [
      new ActionRowBuilder<ButtonBuilder>().addComponents(
        new ButtonBuilder()
          .setLabel("Delete")
          .setStyle(ButtonStyle.Danger)
          .setCustomId(
            `a_delete-triggers-confirm_${event}` satisfies AutoComponentCustomId,
          ),
        new ButtonBuilder()
          .setLabel("Cancel")
          .setStyle(ButtonStyle.Secondary)
          .setCustomId(
            "a_delete-triggers-cancel_" satisfies AutoComponentCustomId,
          ),
      ),
    ],
  });
};

```

### File: `packages/bot/src/commands/welcomer/set.ts`
```ts
import {
  ActionRowBuilder,
  StringSelectMenuBuilder,
  StringSelectMenuOptionBuilder,
} from "@discordjs/builders";
import type { APIWebhook } from "discord-api-types/v10";
import { eq } from "drizzle-orm";
import {
  autoRollbackTx,
  backups,
  triggers as dTriggers,
  type FlowAction,
  FlowActionSetVariableType,
  FlowActionType,
  generateId,
  getchTriggerGuild,
  getDb,
  TriggerEvent,
  upsertDiscordUser,
} from "store";
import type { ChatInputAppCommandCallback } from "../../commands.js";
import type { AutoComponentCustomId } from "../../components.js";
import { getShareLink } from "../../durable/share-links.js";
import { getEmojis } from "../../emojis.js";
import { getErrorMessage } from "../../errors.js";
import { getWelcomerConfigurations } from "../../events/guildMemberAdd.js";
import { isDiscordError } from "../../util/error.js";
import { parseShareLink } from "../components/quick.js";
import { getWebhook } from "../webhooks/webhookInfo.js";
import {
  type AutoWelcomerConfig,
  getWelcomerConfigComponents,
  getWelcomerConfigEmbed,
  getWelcomerConfigFromActions,
} from "./view.js";

export type WelcomerTriggerEvent =
  | TriggerEvent.MemberAdd
  | TriggerEvent.MemberRemove;

const buildSimpleWelcomer = (
  props: AutoWelcomerConfig & { backupId: string },
) => {
  const {
    webhookId,
    channelId,
    backupId,
    backupMessageIndex,
    flags,
    deleteAfter,
  } = props;

  const actions: FlowAction[] = [];
  if (webhookId) {
    actions.push({
      type: FlowActionType.SendWebhookMessage,
      webhookId,
      backupId,
      backupMessageIndex,
      flags,
    });
    if (deleteAfter) {
      actions.push({
        type: FlowActionType.SetVariable,
        varType: FlowActionSetVariableType.Adaptive,
        name: "channelId",
        value: "channel_id",
      });
    }
  } else if (channelId) {
    actions.push(
      {
        type: FlowActionType.SetVariable,
        name: "channelId",
        value: channelId,
      },
      {
        type: FlowActionType.SendMessage,
        backupId,
        backupMessageIndex,
        flags,
      },
    );
  }
  if (deleteAfter) {
    actions.push(
      {
        type: FlowActionType.SetVariable,
        varType: FlowActionSetVariableType.Adaptive,
        name: "messageId",
        value: "id",
      },
      { type: FlowActionType.Wait, seconds: deleteAfter },
      { type: FlowActionType.DeleteMessage },
    );
  }

  return actions;
};

export const welcomerSetupEntry: ChatInputAppCommandCallback<true> = async (
  ctx,
) => {
  const event = ctx.getIntegerOption("event").value as WelcomerTriggerEvent;
  const channel = ctx.getChannelOption("channel") ?? undefined;
  const deleteAfter = ctx.getIntegerOption("delete-after").value as number;
  const shareLink = ctx.getStringOption("share-link").value || undefined;

  return [
    ctx.defer({ ephemeral: true }),
    async () => {
      let shareId: string | undefined;
      if (shareLink) {
        try {
          shareId = await parseShareLink(ctx.env, shareLink);
        } catch (e) {
          await ctx.followup.editOriginalMessage({
            content: String(e),
          });
          return;
        }
      }

      const webhookValue = ctx.getStringOption("webhook").value || undefined;
      let webhook: APIWebhook | undefined;
      if (webhookValue) {
        try {
          webhook = await getWebhook(webhookValue, ctx.env);
        } catch (e) {
          const def = { content: String(e) };
          await ctx.followup.editOriginalMessage(
            isDiscordError(e)
              ? (getErrorMessage(ctx, e.rawError)?.data ?? def)
              : def,
          );
          return;
        }
        if (!webhook.token) {
          await ctx.followup.editOriginalMessage({
            content:
              "I cannot access that webhook's token. Choose a different webhook or use a channel instead.",
          });
          return;
        }
      }

      const isModified =
        !!channel || !!webhook || deleteAfter !== -1 || !!shareId;
      const guild = await getchTriggerGuild(
        ctx.rest,
        ctx.env,
        ctx.interaction.guild_id,
      );

      const db = getDb(ctx.env.HYPERDRIVE);
      const addRemove = event === TriggerEvent.MemberAdd ? "add" : "remove";
      const triggers = await getWelcomerConfigurations(
        db,
        addRemove,
        ctx.rest,
        guild,
      );

      const emojis = await getEmojis(ctx.env);
      // This block is not actually used currently since we limit triggers to
      // one per event per server, but I want to open it in the future
      if (triggers.length > 1) {
        await ctx.followup.editOriginalMessage({
          content: `This server has ${triggers.length} triggers with this event. Please select one to modify, or [modify the trigger online](${ctx.env.DISCOHOOK_ORIGIN}/s/${ctx.interaction.guild_id}).`,
          components: [
            new ActionRowBuilder<StringSelectMenuBuilder>().setComponents(
              new StringSelectMenuBuilder()
                .setCustomId(
                  "a_edit-trigger-select_" satisfies AutoComponentCustomId,
                )
                .setOptions(
                  triggers.slice(0, 25).map((trigger, i) =>
                    i === 24 && triggers.length > 25
                      ? new StringSelectMenuOptionBuilder()
                          .setLabel("Too many options")
                          .setValue("overflow")
                          .setDescription(
                            "Please visit the link for more options",
                          )
                      : new StringSelectMenuOptionBuilder()
                          .setLabel(`${i + 1}. ${trigger.flow.name}`)
                          .setValue(`${trigger.id}`)
                          .setEmoji(
                            emojis.getC(
                              event === TriggerEvent.MemberAdd
                                ? "User_Add"
                                : "User_Remove",
                              true,
                            ),
                          ),
                  ),
                ),
            ),
          ],
        });
        return;
      }

      const title = `Welcomer (${addRemove})`;
      let currentFlow: (typeof triggers)[number]["flow"];
      if (triggers.length === 0) {
        currentFlow = { actions: [] };
      } else {
        currentFlow = triggers[0].flow;
      }

      const current = getWelcomerConfigFromActions(currentFlow.actions);
      if (deleteAfter === 0) {
        current.deleteAfter = undefined;
      } else if (deleteAfter && deleteAfter > 0) {
        current.deleteAfter = deleteAfter;
      }

      if (!current.backupId && !shareId) {
        await ctx.followup.editOriginalMessage({
          content:
            "Please provide message data with the **share-link** option.",
        });
        return;
      }

      if (webhook) {
        current.webhookId = webhook.id;
        current.channelId = undefined;
      } else if (channel) {
        current.channelId = channel.id;
        current.webhookId = undefined;
      }
      if (!current.webhookId && !current.channelId) {
        await ctx.followup.editOriginalMessage({
          content:
            "Please select a destination with either the **webhook** or **channel** option.",
        });
        return;
      }

      const user = await upsertDiscordUser(db, ctx.user);

      let backupName: string | undefined;
      if (shareId) {
        const { data } = await getShareLink(ctx.env, shareId);
        current.backupId = generateId();
        backupName = `Welcomer (${addRemove}) - ${guild.name}`.slice(0, 100);
        await db.insert(backups).values({
          id: BigInt(current.backupId),
          ownerId: user.id,
          name: backupName,
          dataVersion: "d2",
          data,
        });
      }

      if (isModified) {
        const actions = buildSimpleWelcomer({
          ...current,
          // biome-ignore lint/style/noNonNullAssertion: Checked above or re-assigned
          backupId: current.backupId!,
        });
        const flow = { ...currentFlow, actions };

        await db.transaction(
          autoRollbackTx(async (tx) => {
            if (triggers.length === 0) {
              await tx.insert(dTriggers).values({
                platform: "discord",
                discordGuildId: BigInt(ctx.interaction.guild_id),
                flow,
                event,
              });
            } else {
              await tx
                .update(dTriggers)
                .set({ flow, flowId: null, updatedById: user.id })
                .where(eq(dTriggers.id, triggers[0].id));
            }

            triggers.splice(0, 1, {
              ...(triggers[0] ?? { disabled: false }),
              flow,
            });
            await ctx.env.KV.put(
              `cache:triggers-${event}-${ctx.interaction.guild_id}`,
              JSON.stringify(triggers),
              { expirationTtl: 1200 },
            );
          }),
        );
      }

      await ctx.followup.editOriginalMessage({
        embeds: [
          getWelcomerConfigEmbed(ctx.env, current, {
            backup: backupName ? { name: backupName } : undefined,
            webhook,
            emojis,
          }).setTitle(title),
        ],
        components: [
          getWelcomerConfigComponents(
            ctx.env,
            current,
            event,
            ctx.interaction.guild_id,
          ),
        ],
      });
    },
  ];
};

```

### File: `packages/bot/src/commands/welcomer/view.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  bold,
  EmbedBuilder,
} from "@discordjs/builders";
import dedent from "dedent-js";
import {
  type APIWebhook,
  ButtonStyle,
  type MessageFlags,
} from "discord-api-types/v10";
import {
  type FlowAction,
  FlowActionType,
  type FlowActionWait,
  getchTriggerGuild,
  getDb,
  TriggerEvent,
} from "store";
import type { ChatInputAppCommandCallback } from "../../commands.js";
import { EmojiManagerCache, emojiToString, getEmojis } from "../../emojis.js";
import { getWelcomerConfigurations } from "../../events/guildMemberAdd.js";
import type { Env } from "../../types/env.js";
import { color } from "../../util/meta.js";
import { getWebhook } from "../webhooks/webhookInfo.js";
import type { WelcomerTriggerEvent } from "./set.js";

export interface AutoWelcomerConfig {
  webhookId?: string;
  channelId?: string;
  backupId?: string;
  backupMessageIndex?: number | null;
  flags?: MessageFlags;
  deleteAfter?: number;
}

export const getWelcomerConfigFromActions = (
  actions: FlowAction[],
): AutoWelcomerConfig => {
  const current: AutoWelcomerConfig = {};

  let i = -1;
  for (const action of actions) {
    i += 1;
    switch (action.type) {
      case FlowActionType.SendWebhookMessage: {
        current.webhookId = action.webhookId;
        current.backupId = action.backupId;
        current.backupMessageIndex = action.backupMessageIndex;
        current.flags = action.flags;
        break;
      }
      case FlowActionType.SendMessage: {
        current.backupId = action.backupId;
        current.backupMessageIndex = action.backupMessageIndex;
        current.flags = action.flags;
        break;
      }
      case FlowActionType.SetVariable: {
        if (
          action.name === "channelId" &&
          !action.varType &&
          typeof action.value === "string"
        ) {
          current.channelId = action.value;
        }
        break;
      }
      case FlowActionType.DeleteMessage: {
        // This action isn't our `deleteAfter` because the message hasn't been sent yet
        if (!current.backupId) break;

        const waitAction = actions.find(
          (a, ai): a is FlowActionWait =>
            a.type === FlowActionType.Wait && ai < i,
        );
        if (waitAction) {
          current.deleteAfter = waitAction.seconds;
        }
        break;
      }
      default:
        break;
    }
  }

  return current;
};

export const getWelcomerConfigEmbed = (
  env: Env,
  config: AutoWelcomerConfig,
  rich?: {
    backup?: { name: string };
    webhook?: Pick<APIWebhook, "name" | "channel_id">;
    emojis?: EmojiManagerCache;
  },
) => {
  const emojis = rich?.emojis ?? new EmojiManagerCache([]);
  const trueEmoji = emojiToString(emojis.get("true", true));
  const falseEmoji = emojiToString(emojis.get("false", true));
  const nullEmoji = emojiToString(emojis.get("null", true));

  return new EmbedBuilder()
    .setColor(color)
    .setTitle("Welcomer")
    .addFields(
      {
        name: "Destination",
        value: config.webhookId
          ? rich?.webhook
            ? `${trueEmoji} ${
                rich.webhook.name ? bold(rich.webhook.name) : "Webhook"
              } in <#${rich.webhook.channel_id}>`
            : `${trueEmoji} Webhook`
          : config.channelId
            ? `${trueEmoji} <#${config.channelId}>`
            : `${falseEmoji} Not set`,
        inline: true,
      },
      {
        name: "Message data",
        value: config.backupId
          ? `${trueEmoji} ${rich?.backup ? rich.backup.name : "Set"}`
          : `${falseEmoji} Not set`,
        inline: true,
      },
      {
        name: "Cleanup",
        value: config.deleteAfter
          ? `${trueEmoji} Messages are deleted after ${config.deleteAfter} seconds`
          : `${nullEmoji} Not set`,
        inline: true,
      },
      {
        name: "Troubleshooting",
        value: dedent`
          If your welcome messages aren't being sent, make sure <@${
            env.DISCORD_APPLICATION_ID
          }> has permission to ${
            config.webhookId
              ? `manage webhooks${
                  rich?.webhook ? ` in <#${rich.webhook.channel_id}>` : ""
                }`
              : `send messages and embed links${
                  config.channelId ? ` in <#${config.channelId}>` : ""
                }`
          } and that the backup still exists. ${
            config.deleteAfter && config.webhookId
              ? `If the message is not being deleted, make sure the bot has permission to manage messages${
                  rich?.webhook ? ` in <#${rich.webhook.channel_id}>` : ""
                }.`
              : ""
          }
        `,
        inline: false,
      },
    );
};

export const getWelcomerConfigComponents = (
  env: Env,
  config: AutoWelcomerConfig,
  event: WelcomerTriggerEvent,
  guildId: string,
) => {
  return new ActionRowBuilder<ButtonBuilder>().addComponents(
    new ButtonBuilder()
      .setCustomId(`a_trigger-test_${event}`)
      .setLabel("Send Test")
      .setStyle(ButtonStyle.Primary)
      .setDisabled(
        !config.backupId || (!config.channelId && !config.webhookId),
      ),
    new ButtonBuilder()
      .setLabel("Edit Message")
      .setStyle(ButtonStyle.Link)
      .setURL(
        env.DISCOHOOK_ORIGIN +
          (config.backupId ? `/?backup=${config.backupId}` : ""),
      )
      .setDisabled(!config.backupId),
    new ButtonBuilder()
      .setLabel("View Triggers")
      .setStyle(ButtonStyle.Link)
      .setURL(`${env.DISCOHOOK_ORIGIN}/s/${guildId}?t=triggers`),
  );
};

export const welcomerViewEntry: ChatInputAppCommandCallback<true> = async (
  ctx,
) => {
  const event = ctx.getIntegerOption("event").value as WelcomerTriggerEvent;

  const guild = await getchTriggerGuild(
    ctx.rest,
    ctx.env,
    ctx.interaction.guild_id,
  );

  const db = getDb(ctx.env.HYPERDRIVE);
  const addRemove = event === TriggerEvent.MemberAdd ? "add" : "remove";
  const triggers = await getWelcomerConfigurations(
    db,
    addRemove,
    ctx.rest,
    guild,
  );

  if (triggers.length === 0) {
    return ctx.reply({
      content: "This server has no triggers with that event.",
      ephemeral: true,
    });
  }

  const config = getWelcomerConfigFromActions(triggers[0].flow.actions);
  let webhook: APIWebhook | undefined;
  if (config.webhookId) {
    try {
      // We don't need the token here but this function uses cache
      webhook = await getWebhook(config.webhookId, ctx.env);
    } catch {}
  }

  const emojis = await getEmojis(ctx.env);
  return ctx.reply({
    embeds: [
      getWelcomerConfigEmbed(ctx.env, config, { webhook, emojis }).setTitle(
        `Welcomer (${addRemove})`,
      ),
    ],
    components: [
      getWelcomerConfigComponents(
        ctx.env,
        config,
        event,
        ctx.interaction.guild_id,
      ),
    ],
    ephemeral: true,
  });
};

```

