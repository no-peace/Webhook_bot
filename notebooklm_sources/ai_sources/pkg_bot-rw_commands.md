# Repository Context Group: pkg_bot-rw_commands
# Source Repository: discohook/discohook

### File: `packages/bot-rw/src/commands/admin.ts`
```ts
import dedent from "dedent-js";
import { eq } from "drizzle-orm";
import { upsertDiscordUser, users } from "store";
import type { InteractionContext } from "../interactions.js";
import type { ChatInputAppCommandCallback } from "./handler.js";

const canRunDevCommand = (ctx: InteractionContext) =>
  Bun.env.DEV_OWNER_ID !== undefined &&
  Bun.env.DEV_GUILD_ID !== undefined &&
  ctx.user.id === Bun.env.DEV_OWNER_ID &&
  ctx.interaction.guild_id === Bun.env.DEV_GUILD_ID;

export const leaveCommandHandler: ChatInputAppCommandCallback<true> = async (
  ctx,
) => {
  if (!canRunDevCommand(ctx)) {
    await ctx.reply({ content: "Not available", ephemeral: true });
    return;
  }

  const guildId = ctx.getStringOption("guild-id").value;
  const reason = ctx.getStringOption("reason").value;
  const sendMsg = ctx.getBooleanOption("send-reason-message").value;
  const ban = ctx.getBooleanOption("ban").value;

  await ctx.defer({ ephemeral: true });

  if (ban) {
    await ctx.client.KV.put(
      `moderation-guild-${guildId}`,
      JSON.stringify({ state: "banned", reason }),
    );
  }

  if (sendMsg) {
    const guild = await ctx.client.api.guilds.get(guildId);
    const dm = await ctx.client.api.users.createDM(guild.owner_id);
    await ctx.client.api.channels.createMessage(dm.id, {
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
          Bun.env.DISCOHOOK_ORIGIN
        }/legal).
        ${
          ban
            ? "\nIf you attempt to re-add the bot, it will leave automatically.\n"
            : ""
        }
        If you believe this was done in error, contact us on the [Discohook support server](${
          Bun.env.DISCOHOOK_ORIGIN
        }/discord).
      `.trim(),
    });
  }

  await ctx.client.api.users.leaveGuild(guildId);
  await ctx.followup.editOriginalMessage({ content: `Left server ${guildId}` });
};

const USD_REGEX = /^\$(\d+)$/;

const TIME_REGEX = /^(\d+)(d|w|m|y)$/i;

// $6 / 30 days = 20c per day
const USD_PER_DAY = 6 / 30;

export const grantDeluxeCommandHandler: ChatInputAppCommandCallback<
  true
> = async (ctx) => {
  if (!canRunDevCommand(ctx)) {
    await ctx.reply({ content: "Not available", ephemeral: true });
    return;
  }

  const userId = ctx.getStringOption("user-id").value;
  const duration = ctx.getStringOption("duration").value;

  let days: number;
  let lifetime: boolean | undefined;
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
      const unit = (match[2] ?? "null").toLowerCase() as "d" | "w" | "m" | "y";
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
          await ctx.reply({
            content: `Could not resolve value of unit "${unit}"`,
            ephemeral: true,
          });
          return;
      }
      break;
    }
    case duration === "lifetime": {
      days = 0;
      lifetime = true;
      break;
    }
    default:
      await ctx.reply({
        content: "Invalid duration format",
        ephemeral: true,
      });
      return;
  }
  days = Math.ceil(days);

  const discordUser = await ctx.client.api.users.get(userId);

  const db = ctx.client.getDb();
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
      subscriptionExpiresAt: lifetime ? null : expiresAt,
      lifetime,
    })
    .where(eq(users.id, dbUser.id));

  await ctx.reply({
    content: `Granted ${lifetime ? "♾️" : days} days of Deluxe membership to ${discordUser.username} (${discordUser.id})`,
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
  const discordUser = await ctx.client.api.users.get(userId);

  const db = ctx.client.getDb();
  await db
    .update(users)
    .set({
      lifetime: false,
      subscribedSince: null,
      subscriptionExpiresAt: null,
    })
    .where(eq(users.discordId, BigInt(userId)));

  await ctx.reply({
    content: `Revoked Deluxe membership from ${discordUser.username} (${discordUser.id})`,
    ephemeral: true,
  });
};

```

### File: `packages/bot-rw/src/commands/components/add.ts`
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
  type APIInteraction,
  type APIMessage,
  type APIModalInteractionResponseCallbackData,
  type APIModalSubmitStringSelectComponent,
  type APISelectMenuComponent,
  type APIStringSelectComponent,
  ButtonStyle,
  ComponentType,
  TextInputStyle,
} from "discord-api-types/v10";
import { SignJWT } from "jose";
import {
  autoRollbackTx,
  discordMessageComponents,
  type DraftComponent,
  generateId,
  makeSnowflake,
  type StorableComponent,
  upsertDiscordUser,
  upsertGuild,
} from "store";
import type {
  ButtonCallback,
  MinimumKVComponentState,
  ModalCallback,
  SelectMenuCallback,
} from "../../components.js";
import type { InteractionContext } from "../../interactions.js";
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
  component: StorableComponent,
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
  component?: StorableComponent;
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
    throw new Error(`Failed to build the component (type ${data.type}).`);
  }
  const requiredWidth = getComponentWidth(built);

  let message: APIMessage | undefined;
  try {
    message = await ctx.client.api.webhooks.getMessage(
      state.message.webhookId,
      state.webhookToken,
      state.message.id,
      {
        thread_id: state.message.isInThread
          ? state.message.channelId
          : undefined,
      },
    );
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

  const db = ctx.client.getDb();
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

      const editedMsg = await ctx.client.api.webhooks.editMessage(
        state.message.webhookId,
        state.webhookToken,
        state.message.id,
        {
          components,
          thread_id: state.message.isInThread
            ? state.message.channelId
            : undefined,
        },
      );

      if (customId !== undefined) {
        await launchComponentKV(ctx.client.KV, {
          messageId: editedMsg.id,
          componentId: id,
          customId,
        });
      }
      return editedMsg;
    }),
  );
};

export const startComponentFlow = async (
  ctx: InteractionContext<APIInteraction>,
  message: APIMessage,
  components?: ActionRowBuilder<MessageActionRowComponentBuilder>[],
): Promise<InteractionInstantOrDeferredResponse> => {
  const db = ctx.client.getDb();
  const user = await upsertDiscordUser(db, ctx.user);

  if (!message.webhook_id) {
    await ctx.reply({
      content: "This is not a webhook message.",
      ephemeral: true,
    });
    return;
  }
  if (
    !message.application_id ||
    message.application_id !== Bun.env.DISCORD_APPLICATION_ID
  ) {
    await ctx.reply({
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
    return;
  }
  const webhook = await getWebhook(
    ctx.client,
    message.webhook_id,
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

  return [
    ctx.reply({
      components: [
        getComponentFlowContainer(componentFlow),
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
                  description:
                    "Select from a custom list of options (up to 25)",
                  value: "string-select",
                  emoji: { name: "🔽" },
                },
                {
                  label: "User Select",
                  description: "Select from a list of all server members",
                  value: "user-select",
                  emoji: { name: "👤" },
                },
                {
                  label: "Role Select",
                  description: "Select from a list of all server roles",
                  value: "role-select",
                  emoji: { name: "🏷️" },
                },
                {
                  label: "User/Role Select",
                  description: "Select from a list of all members and roles",
                  value: "mentionable-select",
                  emoji: { name: "*️⃣" },
                },
                {
                  label: "Channel Select",
                  description: "Select from a list of all server channels",
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
        ...(components ?? []),
      ],
      ephemeral: true,
      componentsV2: true,
    }),
    async () => {
      // biome-ignore lint/style/noNonNullAssertion: we are in a guild
      const guild = await ctx.client.getchGuild(ctx.interaction.guild_id!);
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
const createEditorToken = async (data: KVComponentEditorState) => {
  const secretKey = Uint8Array.from(
    Bun.env.TOKEN_SECRET.split("").map((x) => x.charCodeAt(0)),
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
    .setIssuer(Bun.env.DISCOHOOK_ORIGIN)
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
  componentId: bigint,
  data: Omit<KVComponentEditorState, "componentId">,
) => {
  const editorToken = await createEditorToken({
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
): string =>
  `${Bun.env.DISCOHOOK_ORIGIN}/edit/component/${
    token.componentId
  }?${new URLSearchParams({
    token: token.value,
  })}`;

export const continueComponentFlow: SelectMenuCallback = async (ctx) => {
  // biome-ignore lint/style/noNonNullAssertion: must provide exactly one value
  const value = ctx.interaction.data.values[0]!;

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

      await ctx.updateMessage({
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
      return;
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
        .addLabelComponents((l) =>
          l
            .setLabel("Label")
            .setTextInputComponent((b) =>
              b
                .setCustomId("label")
                .setStyle(TextInputStyle.Short)
                .setRequired(false)
                .setMaxLength(80)
                .setPlaceholder("The text displayed on this button."),
            ),
        )
        .addLabelComponents((l) =>
          l
            .setLabel("Emoji")
            .setTextInputComponent((b) =>
              b
                .setCustomId("emoji")
                .setStyle(TextInputStyle.Short)
                .setRequired(false)
                .setPlaceholder(
                  "Like :smile: or a custom emoji in the server.",
                ),
            ),
        )
        .addLabelComponents((l) =>
          l
            .setLabel("Button URL")
            .setTextInputComponent((b) =>
              b
                .setCustomId("url")
                .setStyle(TextInputStyle.Paragraph)
                .setRequired(true)
                .setPlaceholder(
                  "The full URL this button will lead to when it is clicked.",
                ),
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

      await storeComponents(ctx.client.KV, [
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
                await storeComponents(ctx.client.KV, [
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
      const db = ctx.client.getDb();
      let componentData: DraftComponent;
      if (value === "string-select") {
        componentData = {
          type: ComponentType.StringSelect,
          options: [],
          flows: {},
        };
      } else {
        componentData = {
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
      }

      const [component] = await db
        .insert(discordMessageComponents)
        .values({
          guildId: makeSnowflake(state.message.guildId),
          channelId: makeSnowflake(state.message.channelId),
          messageId: makeSnowflake(state.message.id),
          type: componentData.type,
          data: componentData,
          createdById: makeSnowflake(state.user.id),
          updatedById: makeSnowflake(state.user.id),
          draft: true,
        })
        .returning({
          id: discordMessageComponents.id,
        });
      const doId = ctx.env.DRAFT_CLEANER.idFromName(String(component.id));
      const stub = ctx.env.DRAFT_CLEANER.get(doId);
      await stub.fetch(`http://do/?id=${component.id}`);

      const editorToken = await generateEditorTokenForComponent(component.id, {
        user: {
          id: ctx.user.id,
          name: ctx.user.username,
          avatar: ctx.user.avatar,
        },
      });

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
      await ctx.updateMessage({
        components: [
          container,
          new ActionRowBuilder<ButtonBuilder>().addComponents(
            new ButtonBuilder()
              .setStyle(ButtonStyle.Link)
              .setLabel(ctx.t("customize"))
              .setURL(getEditorTokenComponentUrl(editorToken)),
          ),
        ],
      });
      return;
    }
    default:
      break;
  }

  await ctx.updateMessage({
    components: [getComponentFlowContainer(state)],
  });
};

export const reopenCustomizeModal: ButtonCallback = async (ctx) => {
  const state = ctx.state as MinimumKVComponentState & {
    modal: APIModalInteractionResponseCallbackData;
  };
  await ctx.modal(state.modal);
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
          ctx.client,
          emojiRaw,
          undefined,
          state.message.guildId,
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

    await ctx.defer();

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
    return;
  }

  await ctx.reply({
    content: "This shouldn't happen",
    ephemeral: true,
  });
};

```

### File: `packages/bot-rw/src/commands/components/delete.ts`
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
  const customId = `p_${id}`;

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

### File: `packages/bot-rw/src/commands/components/edit.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  ContainerBuilder,
  messageLink,
  ModalBuilder,
  SelectMenuBuilder,
  SelectMenuOptionBuilder,
  StringSelectMenuBuilder,
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
import { t } from "i18next";
import {
  autoRollbackTx,
  discordMessageComponents,
  getDb,
  launchComponentKV,
  makeSnowflake,
  type StorableButtonWithUrl,
  type StorableComponent,
  upsertDiscordUser,
  webhooks,
} from "store";
import { parseApplicationsValue } from "../../client.js";
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
import type { ChatInputAppCommandCallback } from "../handler.js";
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
    ctx.client,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    await ctx.reply({
      components: [textDisplay(message)],
      ephemeral: true,
      componentsV2: true,
    });
    return;
  }
  if (
    !message.webhook_id ||
    !message.application_id ||
    !parseApplicationsValue()[message.application_id]
  ) {
    await ctx.reply({
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
    return;
  }

  const webhook = await ctx.client.getchWebhook(message.webhook_id, {
    applicationId: message.application_id,
  });

  const response = await pickWebhookMessageComponentToEdit(ctx, message);
  await ctx.reply(response);

  const db = ctx.client.getDb();
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
      discordGuildId: webhook.guild_id ? BigInt(webhook.guild_id) : undefined,
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
};

export const editComponentButtonEntry: ButtonCallback = async (ctx) => {
  const guildId = ctx.interaction.guild_id;
  if (!guildId) {
    await ctx.reply("Guild-only");
    return;
  }

  const { webhookId, messageId, threadId } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "webhookId",
    "messageId",
    "threadId",
  );
  const { message } = await getWebhookMessage(
    ctx.client,
    webhookId,
    messageId,
    threadId,
  );

  const responseData = await pickWebhookMessageComponentToEdit(ctx, message);
  await ctx.updateMessage(responseData);
};

function ensureValidEmoji<T extends APIMessageComponentEmoji | APIPartialEmoji>(
  emoji: T | undefined,
  emojis: APIEmoji[],
  fallback: T,
): T;
function ensureValidEmoji<T extends APIMessageComponentEmoji | APIPartialEmoji>(
  emoji: T | undefined,
  emojis: APIEmoji[],
  fallback?: T | undefined,
): T | undefined;
function ensureValidEmoji<T extends APIMessageComponentEmoji | APIPartialEmoji>(
  emoji: T | undefined,
  emojis: APIEmoji[],
  fallback?: T,
): T | undefined {
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
  dbComponents?: { id: bigint; data: StorableComponent }[],
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
    dbComponents?: { id: bigint; data: StorableComponent }[];
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
    return {
      components: [textDisplay("Guild only")],
      ephemeral: true,
      componentsV2: true,
    };
  }

  // not sure if we need to bother using cache with this
  const emojiManager = await ctx.client.fetchEmojiManager(guildId);

  const threadId = message.position === undefined ? "" : message.channel_id;
  const menu = getComponentsAsV2Menu(
    message.components ?? [],
    emojiManager.emojis,
    {
      getSelectCustomId: (index: number) =>
        `a_edit-component-flow-pick_${message.webhook_id}:${message.id}:${threadId}:${index}` satisfies AutoComponentCustomId,
    },
  );
  if (menu.length === 0) {
    return {
      components: [
        textDisplay("That message has no components that can be picked from."),
      ],
      ephemeral: true,
      componentsV2: true,
    };
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
  return { components: menu, ephemeral: true, componentsV2: true };
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
        ctx.client,
        webhookId,
        messageId,
        threadId,
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
                  .setLabel(t("customize")),
              ),
            ],
          });
        },
      ];
    }
    default:
      // As far as we know, this component doesn't exist in the database or
      // it's a type that we can't handle. What do you do here?
      // Answer for a prize: https://github.com/discohook/discohook/issues
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
    data: StorableComponent;
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
        modal.addComponents(
          new ActionRowBuilder<TextInputBuilder>().addComponents(
            new TextInputBuilder()
              .setCustomId("sku_id")
              .setLabel("SKU ID")
              .setStyle(TextInputStyle.Short)
              .setRequired(true)
              .setValue(component.data.sku_id)
              .setPlaceholder("Identifier for a purchasable SKU"),
          ),
        );
      } else {
        modal.addComponents(
          new ActionRowBuilder<TextInputBuilder>().addComponents(
            new TextInputBuilder()
              .setCustomId("label")
              .setLabel("Label")
              .setStyle(TextInputStyle.Short)
              .setRequired(false)
              .setMaxLength(80)
              .setValue(component.data.label ?? "")
              .setPlaceholder("The text displayed on this button."),
          ),
          new ActionRowBuilder<TextInputBuilder>().addComponents(
            new TextInputBuilder()
              .setCustomId("emoji")
              .setLabel("Emoji")
              .setStyle(TextInputStyle.Short)
              .setRequired(false)
              .setValue(
                component.data.emoji?.id ?? component.data.emoji?.name ?? "",
              )
              .setPlaceholder("Like :smile: or a custom emoji in the server."),
          ),
        );
        if (component.data.style === ButtonStyle.Link) {
          modal.addComponents(
            new ActionRowBuilder<TextInputBuilder>().addComponents(
              new TextInputBuilder()
                .setCustomId("url")
                .setLabel("Button URL")
                .setStyle(TextInputStyle.Paragraph)
                .setRequired(true)
                .setValue(component.data.url)
                .setPlaceholder(
                  "The full URL this button will lead to when it is clicked.",
                ),
            ),
          );
        }
      }
      modal.addComponents(
        new ActionRowBuilder<TextInputBuilder>().addComponents(
          new TextInputBuilder()
            .setCustomId("disabled")
            .setLabel("Disabled?")
            .setStyle(TextInputStyle.Short)
            .setRequired(false)
            .setMinLength(4)
            .setMaxLength(5)
            .setValue(String(component.data.disabled ?? false))
            .setPlaceholder(
              'Type "true" or "false" for whether the button should be unclickable.',
            ),
        ),
      );
      break;
    case ComponentType.StringSelect:
    case ComponentType.ChannelSelect:
    case ComponentType.MentionableSelect:
    case ComponentType.RoleSelect:
    case ComponentType.UserSelect:
      modal.addComponents(
        new ActionRowBuilder<TextInputBuilder>().addComponents(
          new TextInputBuilder()
            .setCustomId("placeholder")
            .setLabel("Placeholder")
            .setStyle(TextInputStyle.Paragraph)
            .setMaxLength(150)
            .setRequired(false)
            .setValue(component.data.placeholder ?? "")
            .setPlaceholder(
              "The text to show in the select menu when it is collapsed.",
            ),
        ),
        new ActionRowBuilder<TextInputBuilder>().addComponents(
          new TextInputBuilder()
            .setCustomId("disabled")
            .setLabel("Disabled?")
            .setStyle(TextInputStyle.Short)
            .setRequired(false)
            .setMinLength(4)
            .setMaxLength(5)
            .setValue(String(component.data.disabled ?? false))
            .setPlaceholder(
              'Type "true" or "false" for whether the select should be unclickable.',
            ),
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
                .setLabel(t("customize")),
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
          .setLabel(t("customize"))
          .setURL(getEditorTokenComponentUrl(editorToken, ctx.env)),
      ),
    ],
  });
};

const registerComponentUpdate = async (
  ctx: InteractionContext<APIInteraction>,
  id: bigint,
  data: StorableComponent,
  webhook: { id: string; token: string; guild_id?: string },
  message: APIMessage,
  path: number[],
) => {
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
    await launchComponentKV(env, {
      componentId: id,
      data,
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

  const data: StorableComponent = component.data;
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
    data.disabled = disabledRaw.toLowerCase() === "true";
  }

  const edited = await registerComponentUpdate(
    ctx,
    component.id,
    data,
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

### File: `packages/bot-rw/src/commands/components/entry.ts`
```ts
import { ActionRowBuilder, ButtonBuilder } from "@discordjs/builders";
import { messageLink } from "@discordjs/formatters";
import dedent from "dedent-js";
import {
  type APIApplicationCommandAutocompleteInteraction,
  type APIGuildChannel,
  type APIMessage,
  type APIWebhook,
  ApplicationCommandOptionType,
  ButtonStyle,
  type ChannelType,
} from "discord-api-types/v10";
import { getDate, type Snowflake } from "discord-snowflake";
import type { Client } from "../../client.js";
import type { AutoComponentCustomId } from "../../components.js";
import type { InteractionContext } from "../../interactions.js";
import type {
  AppCommandAutocompleteCallback,
  ChatInputAppCommandCallback,
  MessageAppCommandCallback,
} from "../handler.js";
import { startComponentFlow } from "./add.js";

const MESSAGE_LINK_RE =
  /^https:\/\/(?:www\.|ptb\.|canary\.)?discord(?:app)?\.com\/channels\/(\d+)\/(\d+)\/(\d+)$/;

export const resolveMessageLink = async (
  client: Client,
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

  // biome-ignore lint/style/noNonNullAssertion: required for match array
  const channelId = match[2]!;

  if (checkGuildId) {
    const channel = (await client.api.channels.get(
      channelId,
    )) as APIGuildChannel<ChannelType>;
    if (!channel.guild_id || channel.guild_id !== checkGuildId) {
      return "That message is not from this server.";
    }
  }

  let message: APIMessage;
  try {
    // biome-ignore lint/style/noNonNullAssertion: same as above
    message = await client.api.channels.getMessage(channelId, match[3]!);
  } catch {
    return "Unable to resolve that message. Make sure you are pasting a valid message link in a channel that I can access.";
  }

  return message;
};

type APIWebhookWithToken = APIWebhook & Required<Pick<APIWebhook, "token">>;

export const getWebhookMessage = async (
  client: Client,
  webhookId: string,
  messageId: string,
  threadId?: string,
): Promise<{ webhook: APIWebhookWithToken; message: APIMessage }> => {
  const webhook = await client.getchWebhook(webhookId);
  if (!webhook.token) {
    throw Error("Webhook token is inaccessible.");
  }

  const message = await client.api.webhooks.getMessage(
    webhook.id,
    webhook.token,
    messageId,
    { thread_id: threadId },
  );
  return { webhook: webhook as APIWebhookWithToken, message };
};

export const addComponentChatEntry: ChatInputAppCommandCallback<true> = async (
  ctx,
) => {
  const message = await resolveMessageLink(
    ctx.client,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    await ctx.reply({
      content: message,
      ephemeral: true,
    });
    return;
  }
  await startComponentFlow(ctx, message);
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
  const cached = await ctx.client.KV.get<CompactCompatibleMessage[]>(
    kvKey,
    "json",
  );
  let messages = cached;
  if (!messages) {
    const channelMessages = (await ctx.client.api.channels.getMessages(
      channelId,
      { limit: 20 },
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
      await ctx.client.KV.put(kvKey, JSON.stringify(messages), {
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
    new ButtonBuilder()
      .setLabel("View all")
      .setStyle(ButtonStyle.Link)
      .setURL(
        `${Bun.env.DISCOHOOK_ORIGIN}/s/${ctx.interaction.guild_id}?t=components`,
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

### File: `packages/bot-rw/src/commands/components/migrate.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  messageLink,
} from "@discordjs/builders";
import type { REST } from "@discordjs/rest";
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
import { t } from "i18next";
import {
  autoRollbackTx,
  backups,
  buttons,
  type DBWithSchema,
  discordMessageComponents,
  discordMessageComponentsToFlows,
  type FlowActionCheck,
  FlowActionCheckFunctionType,
  type FlowActionDud,
  type FlowActionSendMessage,
  FlowActionSetVariableType,
  type FlowActionStop,
  type FlowActionToggleRole,
  FlowActionType,
  flowActions,
  flows,
  generateId,
  getchTriggerGuild,
  getDb,
  launchComponentKV,
  makeSnowflake,
  type QueryData,
  type StorableButtonWithCustomId,
  type StorableButtonWithUrl,
  upsertDiscordUser,
} from "store";
import type { ChatInputAppCommandCallback } from "../../commands.js";
import type {
  AutoComponentCustomId,
  ButtonCallback,
} from "../../components.js";
import type { Env } from "../../types/env.js";
import {
  hasCustomId,
  isActionRow,
  parseAutoComponentId,
} from "../../util/components.js";
import { getWebhookThreadQuery } from "../../util/messages.js";
import { getWebhook } from "../webhooks/webhookInfo.js";
import { resolveMessageLink } from "./entry.js";

export const migrateLegacyButtons = async (
  env: Env,
  rest: REST,
  db: DBWithSchema,
  guildId: string,
  message: APIMessage,
) => {
  const guild = await getchTriggerGuild(rest, env, guildId);
  // Not sure if it's better for RL reasons to use guildMember instead?
  const owner = (await rest.get(Routes.user(guild.owner_id))) as APIUser;
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
    throw Error(t("noMigratableComponents"));
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
        const newCustomId = `p_${newId}`;
        if (old) {
          oldIdMap[old] = newId;
        }

        let flowId: string | undefined;
        if (!button.url) {
          const backupId = insertedBackups.find(
            old && oldIdToBackupName[old]
              ? (backup) => backup.name === oldIdToBackupName[old]
              : () => false,
          )?.id;

          flowId = generateId();
          await tx.insert(flows).values({ id: BigInt(flowId) });

          const actions = [
            ...(button.roleId
              ? [
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
                  } satisfies FlowActionCheck,
                  {
                    type: FlowActionType.ToggleRole,
                    roleId: String(button.roleId),
                  } satisfies FlowActionToggleRole,
                  {
                    type: FlowActionType.Stop,
                    message: {
                      content: "{response}",
                      flags: MessageFlags.Ephemeral,
                    },
                  } satisfies FlowActionStop,
                ]
              : backupId
                ? [
                    {
                      type: FlowActionType.SendMessage,
                      backupId: backupId.toString(),
                      backupMessageIndex: 0,
                      response: true,
                      flags:
                        button.customEphemeralMessageData ||
                        button.customDmMessageData
                          ? MessageFlags.Ephemeral
                          : undefined,
                    } satisfies FlowActionSendMessage,
                  ]
                : button.type === "do_nothings"
                  ? [{ type: FlowActionType.Dud } satisfies FlowActionDud]
                  : []),
          ];
          if (actions.length !== 0) {
            await tx.insert(flowActions).values(
              actions.map((action) => ({
                // biome-ignore lint/style/noNonNullAssertion: non-null by this point
                flowId: BigInt(flowId!),
                type: action.type,
                data: action,
              })),
            );
          }
        }

        const data = {
          type: ComponentType.Button,
          label: button.customLabel ?? undefined,
          emoji: button.emoji
            ? button.emoji.startsWith("<")
              ? {
                  id: button.emoji.split(":")[2].replace(/>$/, ""),
                  name: button.emoji.split(":")[1],
                  animated: button.emoji.split(":")[0] === "<a",
                }
              : {
                  name: button.emoji,
                }
            : undefined,
          ...(button.url
            ? {
                url: button.url,
                style: ButtonStyle.Link,
              }
            : {
                customId: newCustomId,
                // biome-ignore lint/style/noNonNullAssertion: non-null by this point
                flowId: flowId!,
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
              }),
        } satisfies StorableButtonWithCustomId | StorableButtonWithUrl;

        values.push({
          id: BigInt(newId),
          channelId: makeSnowflake(message.channel_id),
          guildId: makeSnowflake(guildId),
          messageId: makeSnowflake(message.id),
          draft: false,
          type: ComponentType.Button,
          data,
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
      const withFlowId = inserted.filter(
        (i): i is { id: bigint; data: StorableButtonWithCustomId } =>
          "flowId" in i.data && !!i.data.flowId,
      );
      if (withFlowId.length !== 0) {
        await tx
          .insert(discordMessageComponentsToFlows)
          .values(
            withFlowId.map((component) => ({
              discordMessageComponentId: component.id,
              flowId: BigInt(component.data.flowId),
            })),
          )
          .onConflictDoNothing();
      }

      return inserted;
    }),
  );

  const emojis = (await rest.get(
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
        ctx.env,
        ctx.rest,
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
            await launchComponentKV(ctx.client.KV, {
              componentId: component.id,
              data: component.data,
            });
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

### File: `packages/bot-rw/src/commands/components/quick.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  ModalBuilder,
  RoleSelectMenuBuilder,
  StringSelectMenuBuilder,
  StringSelectMenuOptionBuilder,
  TextInputBuilder,
} from "@discordjs/builders";
import dedent from "dedent-js";
import {
  type APIButtonComponentWithCustomId,
  type APIMessageComponentEmoji,
  ButtonStyle,
  ComponentType,
  MessageFlags,
  TextInputStyle,
} from "discord-api-types/v10";
import { MessageFlagsBitField, PermissionFlags } from "discord-bitflag";
import { eq } from "drizzle-orm";
import {
  autoRollbackTx,
  backups,
  discordMessageComponents,
  discordMessageComponentsToFlows,
  type FlowAction,
  FlowActionCheckFunctionType,
  FlowActionSetVariableType,
  FlowActionType,
  flowActions,
  flows,
  generateId,
  makeSnowflake,
} from "store";
import type { Client } from "../../client.js";
import type { ModalCallback, SelectMenuCallback } from "../../components.js";
import type { InteractionContext } from "../../interactions.js";
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

  const db = ctx.client.getDb();
  const flowId = BigInt(generateId());
  await db.insert(flows).values({ id: flowId }).returning({ id: flows.id });

  state.component = state.component ?? {
    type: ComponentType.Button,
    style: ButtonStyle.Primary,
    flowId: String(flowId),
    label: "Button",
  };

  // biome-ignore lint/style/noNonNullAssertion: insert always returns or throws. what's up with this type?
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
  )[0]!;
  await db
    .insert(discordMessageComponentsToFlows)
    .values({
      discordMessageComponentId: component.id,
      flowId,
    })
    .onConflictDoNothing();
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
      const editorToken = await generateEditorTokenForComponent(component.id, {
        user: {
          id: ctx.user.id,
          name: ctx.user.username,
          avatar: ctx.user.avatar,
        },
      });

      const container = getComponentFlowContainer(state);
      container.addTextDisplayComponents((c) =>
        c.setContent(`-# ${ctx.t("componentWillExpire")}`),
      );
      await ctx.updateMessage({
        components: [
          container,
          new ActionRowBuilder<ButtonBuilder>().addComponents(
            new ButtonBuilder()
              .setLabel(ctx.t("customize"))
              .setStyle(ButtonStyle.Link)
              .setURL(getEditorTokenComponentUrl(editorToken)),
          ),
        ],
      });
      return;
    }
    case "toggle-role": {
      state.totalSteps = 5;
      if (!ctx.userPermissons.has(PermissionFlags.ManageRoles)) {
        return ctx.reply({
          content: "You need the **Manage Roles** permission",
          ephemeral: true,
        });
      }
      await ctx.updateMessage({
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
      return;
    }
    case "send-message": {
      state.totalSteps = 6;
      state.stepTitle = "Set share link";
      state.step = 3;
      const modal = new ModalBuilder()
        .setTitle("Button message")
        .addComponents(
          new ActionRowBuilder<TextInputBuilder>().addComponents(
            new TextInputBuilder()
              .setCustomId("share-link")
              .setLabel("Share Link")
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

      await ctx.modal(modal);
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
                componentRoutingId: "add-component-flow-customize-modal-resend",
                componentOnce: false,
              },
            ]),
          ),
        ],
      });
      return;
    }
    default:
      break;
  }

  await ctx.reply({
    content: "Unknown setup path",
    ephemeral: true,
  });
};

const getCustomButtonValuesModal = () =>
  new ModalBuilder().setTitle("Custom button values").addLabelComponents(
    (l) =>
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
    (l) =>
      l
        .setLabel("Emoji")
        .setDescription("Like :smile: or a custom emoji in the server.")
        .setTextInputComponent((b) =>
          b
            .setCustomId("emoji")
            .setStyle(TextInputStyle.Short)
            .setRequired(false),
        ),
    (l) =>
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

const addComponentSetStylePrompt = async (ctx: InteractionContext) => {
  const state = ctx.state as ComponentFlow;
  state.stepTitle = "Choose a button style";
  state.step += 1;

  return await ctx.followup.editOriginalMessage({
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

  await ctx.modal(modal);
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
};

export const addComponentQuickToggleRoleCallback: SelectMenuCallback = async (
  ctx,
) => {
  const value = ctx.interaction.data.values[0];
  // biome-ignore lint/style/noNonNullAssertion: Options generated from this array
  const config = quickButtonConfigs.find((c) => c.id === "toggle-role")!;

  const guildId = ctx.interaction.guild_id;
  if (!guildId) throw Error("Guild-only");

  const { roles, owner_id } = await ctx.client.api.guilds.get(guildId);
  const role = roles.find((r) => r.id === value);
  if (!role) {
    await ctx.reply({
      content:
        "The role could not be found. Please choose a different one or try restarting Discord.",
      ephemeral: true,
    });
    return;
  }
  if (role.managed) {
    await ctx.reply({
      content: `<@&${role.id}> can't be assigned to members.`,
      ephemeral: true,
    });
    return;
  }

  const me = await ctx.client.api.guilds.getMember(
    guildId,
    Bun.env.DISCORD_APPLICATION_ID,
  );
  const botHighestRole = getHighestRole(roles, me.roles);
  if (owner_id !== Bun.env.DISCORD_APPLICATION_ID) {
    // You could be running an instance of this bot where
    // the bot is the owner of the guild
    if (!botHighestRole) {
      await ctx.reply({
        content: `I can't assign <@&${role.id}> to members because I don't have any roles.`,
        ephemeral: true,
      });
      return;
    } else if (botHighestRole && role.position >= botHighestRole.position) {
      await ctx.reply({
        content: `<@&${role.id}> is higher than my highest role (<@&${botHighestRole.id}>), so I can't assign it to members. <@&${role.id}> needs to be lower in the role list, or my highest role needs to be higher.`,
        ephemeral: true,
      });
      return;
    }
  }
  // biome-ignore lint/style/noNonNullAssertion: guild-only
  const member = ctx.interaction.member!;
  const memberHighestRole = getHighestRole(roles, member.roles);
  if (owner_id !== ctx.user.id) {
    // Guild owner can always do everything
    if (!memberHighestRole) {
      // This message should never be seen unless someone messes with permissions
      await ctx.reply({
        content: `You can't assign <@&${role.id}> to members because you don't have any roles.`,
        ephemeral: true,
      });
      return;
    } else if (
      memberHighestRole &&
      role.position >= memberHighestRole.position
    ) {
      await ctx.reply({
        content: `<@&${role.id}> is higher than your highest role (<@&${memberHighestRole.id}>), so you can't select it to be assigned to members. <@&${role.id}> needs to be lower in the role list, or your highest role needs to be higher.`,
        ephemeral: true,
      });
      return;
    }
  }

  const state = ctx.state as ComponentFlow;
  state.step = 4;
  state.steps = state.steps ?? [];
  state.steps.push({ label: `Select role (<@&${role.id}>)` });

  // Assume button
  const { flowId } = state.component as StorableButtonWithCustomId;
  const actions = config.build({ roleId: role.id });

  await ctx.defer();
  const db = ctx.client.getDb();
  await db.transaction(
    autoRollbackTx(async (tx) => {
      await tx
        .delete(flowActions)
        .where(eq(flowActions.flowId, BigInt(flowId)));
      await tx.insert(flowActions).values(
        actions.map((action) => ({
          flowId: BigInt(flowId),
          type: action.type,
          data: action,
        })),
      );
    }),
  );

  await addComponentSetStylePrompt(ctx);
};

export const parseShareLink = async (client: Client, raw: string) => {
  const invalidShareLinkMessage = `Invalid share link. They look like this: \`${Bun.env.DISCOHOOK_ORIGIN}/?share=...\``;
  let shareUrl: URL;
  try {
    shareUrl = new URL(raw);
  } catch {
    throw Error(invalidShareLinkMessage);
  }
  const shareId = shareUrl.searchParams.get("share");
  if (shareUrl.origin !== Bun.env.DISCOHOOK_ORIGIN || !shareId) {
    if (shareUrl.host === "share.discohook.app") {
      throw Error(dedent`
        This is an old-style share link. You must use a share link created on <${Bun.env.DISCOHOOK_ORIGIN}>. They look like this: \`${Bun.env.DISCOHOOK_ORIGIN}/?share=...\`

        -# TIP: Just [open the share link](${shareUrl.href}), change the address from \`discohook.org\` to \`discohook.app\`, then press "Share" again to generate a new link.
      `);
    }
    throw Error(invalidShareLinkMessage);
  }

  if (!(await getShareLinkExists(client, shareId))) {
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
      ctx.client,
      ctx.getModalComponent("share-link").value,
    );
  } catch (e) {
    await ctx.reply({ content: String(e), flags: MessageFlags.Ephemeral });
    return;
  }

  const state = ctx.state as ComponentFlow;
  state.steps?.push({
    label: `Set share link ([${shareId}](${Bun.env.DISCOHOOK_ORIGIN}/?share=${shareId}))`,
  });
  state.stepTitle = "Set visibility";
  state.step += 1;

  await ctx.updateMessage({
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

    await ctx.defer();
    const { data } = await getShareLink(ctx.client, shareId);

    // Assume button
    const { flowId } = state.component as StorableButtonWithCustomId;

    // biome-ignore lint/style/noNonNullAssertion: Options generated from this array
    const config = quickButtonConfigs.find((c) => c.id === "send-message")!;
    const backupId = generateId();
    const backupName = `Button in #${
      ctx.interaction.channel.name ?? "unknown"
    } (share ${shareId})`.slice(0, 100);
    const actions = config.build({ flags, backupId });

    const db = ctx.client.getDb();
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
          .delete(flowActions)
          .where(eq(flowActions.flowId, BigInt(flowId)));
        await tx.insert(flowActions).values(
          actions.map((action) => ({
            flowId: BigInt(flowId),
            type: action.type,
            data: action,
          })),
        );
      }),
    );

    state.steps?.splice(
      // Remove share link step and replace it with editable backup link now
      // that we have fetched the data and created the backup
      state.steps.length - 1,
      1,
      {
        label: `Set [message data](${Bun.env.DISCOHOOK_ORIGIN}/?backup=${backupId} "${backupName}") (${shareId})`,
      },
      {
        label: `Set message visibility (${
          flags.has(MessageFlags.Ephemeral) ? "hidden" : "public"
        })`,
      },
    );
    state.stepTitle = "Set visibility";
    state.step += 1;

    await addComponentSetStylePrompt(ctx);
  };

```

### File: `packages/bot-rw/src/commands/debug.ts`
```ts
import { EmbedBuilder, messageLink, time } from "@discordjs/builders";
import dedent from "dedent-js";
import {
  type APIGuildTextChannel,
  type APIMessage,
  type APIMessageApplicationCommandGuildInteraction,
  type APIWebhook,
  type ChannelType,
  OverwriteType,
  type RESTGetAPIGuildRolesResult,
} from "discord-api-types/v10";
import { PermissionFlags, PermissionsBitField } from "discord-bitflag";
import { desc, eq } from "drizzle-orm";
import { getId, messageLogEntries } from "store";
import type { InteractionContext } from "../interactions.js";
import { userAvatarUrl, webhookAvatarUrl } from "../util/cdn.js";
import { boolEmoji, color } from "../util/meta.js";
import type { MessageAppCommandCallback } from "./handler.js";

interface LogEntry {
  id: bigint;
  type: string | null;
  user: { discordId: bigint | null } | null;
}

const getMessageDebugEmbed = async (
  ctx: InteractionContext<APIMessageApplicationCommandGuildInteraction>,
  message: APIMessage,
) => {
  const db = ctx.client.getDb();
  let webhook: APIWebhook | undefined;
  let logEntries: LogEntry[] | undefined;
  if (message.webhook_id) {
    try {
      webhook = await ctx.client.api.webhooks.get(message.webhook_id);
    } catch {}
    logEntries = await db.query.messageLogEntries.findMany({
      where: eq(messageLogEntries.messageId, message.id),
      columns: {
        id: true,
        type: true,
      },
      with: {
        user: { columns: { discordId: true } },
      },
      orderBy: desc(messageLogEntries.id),
    });
  }

  const guildId = ctx.interaction.guild_id;
  const embed = new EmbedBuilder()
    .setColor(color)
    .setAuthor({
      name: message.author.global_name ?? message.author.username,
      iconURL: message.webhook_id
        ? webhookAvatarUrl(message.author, { size: 64 })
        : userAvatarUrl(message.author, { size: 64 }),
    })
    .setTitle(
      `Message Debug for ${messageLink(
        message.channel_id,
        message.id,
        guildId,
      )}`,
    )
    .setFooter({
      text: dedent`
        ID: ${message.id}
        Flags: ${message.flags?.toString() ?? 0}
      `,
    });

  let roles: RESTGetAPIGuildRolesResult | undefined;
  try {
    roles = await ctx.client.api.guilds.getRoles(guildId);
  } catch {}
  const channel = ctx.interaction.channel as APIGuildTextChannel<
    | ChannelType.GuildText
    | ChannelType.GuildVoice
    | ChannelType.GuildAnnouncement
    | ChannelType.GuildForum
    | ChannelType.GuildMedia
  >;
  const overwrites =
    ((await ctx.client.api.channels.get(channel.id)) as typeof channel)
      .permission_overwrites ?? [];

  const permissions = {
    everyone: {
      guild: new PermissionsBitField(
        BigInt(roles?.find((r) => r.id === guildId)?.permissions ?? "0"),
      ),
      channel: (() => {
        const ow = channel.permission_overwrites?.find(
          (ow) => ow.id === guildId && ow.type === OverwriteType.Role,
        );
        if (ow) {
          return {
            allow: new PermissionsBitField(BigInt(ow.allow)),
            deny: new PermissionsBitField(BigInt(ow.deny)),
          };
        }
        return {
          allow: new PermissionsBitField(),
          deny: new PermissionsBitField(),
        };
      })(),
    },
    // reg. message author or app webhook owner
    user: {
      guild: new PermissionsBitField(),
      channel: {
        allow: new PermissionsBitField(),
        deny: new PermissionsBitField(),
      },
    },
  };

  if (message.webhook_id) {
    if (webhook?.user?.bot && roles) {
      try {
        // May no longer be a member
        const member = await ctx.client.api.guilds.getMember(
          guildId,
          webhook.user.id,
        );
        permissions.user.guild.add(
          member.roles.map((rid) =>
            BigInt(roles.find((role) => role.id === rid)?.permissions ?? "0"),
          ),
        );
        const ows = overwrites.filter(
          (ow) =>
            (ow.id === webhook.user?.id && ow.type === OverwriteType.Member) ||
            (ow.type === OverwriteType.Role && member.roles.includes(ow.id)),
        );
        for (const ow of ows) {
          permissions.user.channel.deny.add(BigInt(ow.deny));
          permissions.user.channel.allow.add(BigInt(ow.allow));
        }
      } catch {}
    }
    embed.addFields({
      name: "Webhook",
      value: webhook
        ? dedent`
            Created by <@${webhook.user?.id}>
            ID: \`${webhook.id}\`
          `
        : `Failed to fetch. The webhook may no longer exist (ID \`${message.webhook_id}\`)`,
    });
  } else {
    try {
      // May no longer be a member
      const member =
        message.author.id === ctx.user.id
          ? ctx.interaction.member
          : await ctx.client.api.guilds.getMember(guildId, message.author.id);
      permissions.user.guild.add(
        ...(roles
          ?.filter((role) => member.roles.includes(role.id))
          .map((role) => BigInt(role.permissions)) ?? []),
      );

      const ows = overwrites.filter(
        (ow) =>
          (ow.id === message.author.id && ow.type === OverwriteType.Member) ||
          (ow.type === OverwriteType.Role && member.roles.includes(ow.id)),
      );
      for (const ow of ows) {
        permissions.user.channel.deny.add(BigInt(ow.deny));
        permissions.user.channel.allow.add(BigInt(ow.allow));
      }
    } catch {}
    embed.addFields({
      name: "Author",
      value: `${message.author.bot ? "Bot" : "User"} with ID \`${
        message.author.id
      }\` (<@${message.author.id}>)`,
    });
  }

  const permissionScope = webhook?.user?.bot
    ? "user"
    : message.webhook_id
      ? "everyone"
      : "user";
  const guildPerm =
    permissionScope === "user"
      ? new PermissionsBitField(
          permissions.everyone.guild.mask(permissions.user.guild),
        )
      : permissions.everyone.guild;
  const channelPerm =
    permissionScope === "user"
      ? // ?  {
        //       allow: new PermissionsBitField(
        //         permissions.everyone.channel.allow.mask(
        //           permissions.user.channel.allow,
        //         ),
        //       ),
        //       deny: new PermissionsBitField(
        //         permissions.everyone.channel.deny.mask(
        //           permissions.user.channel.deny,
        //         ),
        //       ),
        //     }
        permissions.user.channel
      : permissions.everyone.channel;

  embed.addFields({
    name: "Emojis",
    value: dedent`
      Permissions for this message apply to ${
        webhook?.user?.bot
          ? `<@${webhook.user.id}> (the application that owns the webhook)`
          : message.webhook_id
            ? `@everyone ${
                webhook
                  ? ""
                  : "or the application that may have owned the webhook"
              }`
            : `<@${message.author.id}>`
      }

      **Server**
      ${boolEmoji(true)} Use Discord emojis
      ${boolEmoji(true)} Use this server's emojis
      ${boolEmoji(guildPerm.has(PermissionFlags.UseExternalEmojis))} Use external emojis

      **Channel**
      ${boolEmoji(true)} Use Discord emojis
      ${boolEmoji(true)} Use this server's emojis
      ${boolEmoji(
        channelPerm.deny.has(PermissionFlags.UseExternalEmojis)
          ? false
          : channelPerm.allow.has(PermissionFlags.UseExternalEmojis)
            ? true
            : null,
      )} Use external emojis
    `,
  });

  if (message.webhook_id) {
    embed.addFields({
      name: "Discohook Logs",
      value:
        !logEntries || logEntries.length === 0
          ? "This message may not have been sent with Discohook."
          : logEntries
              .map(
                (entry) =>
                  `${time(new Date(getId(entry).timestamp), "d")} ${
                    entry.type
                  } - ${
                    entry.user?.discordId
                      ? `<@${entry.user.discordId}>`
                      : "anonymous"
                  }`,
              )
              .join("\n")
              .slice(0, 1024),
    });
  }

  return embed;
};

export const debugMessageCallback: MessageAppCommandCallback<
  APIMessageApplicationCommandGuildInteraction
> = async (ctx) => {
  const message = ctx.getMessage();
  await ctx.reply({
    embeds: [await getMessageDebugEmbed(ctx, message)],
    ephemeral: true,
  });
};

```

### File: `packages/bot-rw/src/commands/deluxe.ts`
```ts
import { ActionRowBuilder, ButtonBuilder } from "@discordjs/builders";
import { TimestampStyles, time } from "@discordjs/formatters";
import { ButtonStyle } from "discord-api-types/v10";
import { eq } from "drizzle-orm";
import { upsertDiscordUser, users } from "store";
import type { ChatInputAppCommandCallback } from "./handler.js";

export const deluxeInfoCallback: ChatInputAppCommandCallback = async (ctx) => {
  const premiumSkus: string[] = JSON.parse(Bun.env.PREMIUM_SKUS ?? "[]");
  const components = [
    new ActionRowBuilder<ButtonBuilder>().addComponents(
      premiumSkus.map((skuId) =>
        new ButtonBuilder().setStyle(ButtonStyle.Premium).setSKUId(skuId),
      ),
    ),
  ];
  await ctx.reply({
    content: `Learn about Discohook Deluxe here: <${Bun.env.DISCOHOOK_ORIGIN}/donate>`,
    components,
    ephemeral: true,
  });
};

export const deluxeSyncCallback: ChatInputAppCommandCallback = async (ctx) => {
  const db = ctx.client.getDb();
  const user = await upsertDiscordUser(db, ctx.user);

  // Make sure we don't accidentally do this for users if we ever introduce a
  // guild-level subscription
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

  await ctx.reply({
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

### File: `packages/bot-rw/src/commands/emojis.ts`
```ts
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

export const fetchEmojiData = async () => {
  const response = await fetch(`${Bun.env.DISCOHOOK_ORIGIN}/emoji.json`, {
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
    if (!emoji) continue; // type guard

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

export type ResolvedEmojiData = ReturnType<typeof resolveEmojiData>;

```

### File: `packages/bot-rw/src/commands/format.ts`
```ts
import { EmbedBuilder } from "@discordjs/builders";
import dedent from "dedent-js";
import {
  type APIChatInputApplicationCommandInteraction,
  type APIPartialEmoji,
  type APIRole,
  FormattingPatterns,
} from "discord-api-types/v10";
import type { InteractionContext } from "../interactions.js";
import { color } from "../util/meta.js";
import type { ChatInputAppCommandCallback } from "./handler.js";

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
  await ctx.reply({
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
  await ctx.reply({
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

  const { nameToEmoji, emojiToName } = await ctx.client.fetchEmojis();
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
    await ctx.reply({
      content: "No emoji was found.",
      ephemeral: true,
    });
    return;
  }

  const formatting =
    typeof emoji === "object"
      ? `<${emoji.animated ? "a" : ""}:${emoji.name}:${emoji.id}>`
      : emoji;

  await ctx.reply({
    embeds: [getMentionEmbed(formatting, "Emoji")],
    ephemeral: true,
  });
};

```

### File: `packages/bot-rw/src/commands/handler.ts`
```ts
import type {
  APIApplicationCommandInteractionDataOption,
  ToEventProps,
} from "@discordjs/core";
import {
  type APIApplicationCommandAutocompleteInteraction,
  type APIApplicationCommandAutocompleteResponse,
  type APIChatInputApplicationCommandDMInteraction,
  type APIChatInputApplicationCommandGuildInteraction,
  type APIChatInputApplicationCommandInteraction,
  type APIInteraction,
  type APIMessageApplicationCommandDMInteraction,
  type APIMessageApplicationCommandGuildInteraction,
  type APIUserApplicationCommandInteraction,
  ApplicationCommandOptionType,
  ApplicationCommandType,
  InteractionType,
  MessageFlags,
} from "discord-api-types/v10";
import { sendErrorMessage } from "../errors.js";
import { InteractionContext } from "../interactions.js";
import { isDiscordError } from "../util/error.js";
import {
  grantDeluxeCommandHandler,
  leaveCommandHandler,
  revokeDeluxeCommandHandler,
} from "./admin.js";
import { deluxeInfoCallback, deluxeSyncCallback } from "./deluxe.js";
import {
  formatChannelCallback,
  formatEmojiCallback,
  formatMentionCallback,
} from "./format.js";
import { helpAutocomplete, helpEntry } from "./help.js";
import { idChannelCallback, idEmojiCallback, idMentionCallback } from "./id.js";
import { inviteCallback } from "./invite.js";
import { profileClearCallback, profileSetCallback } from "./profile.js";

export type AppCommandCallbackT<T extends APIInteraction> = (
  ctx: InteractionContext<T>,
) => Promise<void>;
export type ChatInputAppCommandCallback<
  GuildOnly extends boolean = false,
  DMOnly extends boolean = false,
> = AppCommandCallbackT<
  GuildOnly extends true
    ? APIChatInputApplicationCommandGuildInteraction
    : DMOnly extends true
      ? APIChatInputApplicationCommandDMInteraction
      : APIChatInputApplicationCommandInteraction
>;
export type MessageAppCommandCallback<
  T extends
    | APIMessageApplicationCommandDMInteraction
    | APIMessageApplicationCommandGuildInteraction = APIMessageApplicationCommandGuildInteraction,
> = AppCommandCallbackT<T>;
export type UserAppCommandCallback =
  AppCommandCallbackT<APIUserApplicationCommandInteraction>;

type AutocompleteChoices = NonNullable<
  APIApplicationCommandAutocompleteResponse["data"]["choices"]
>;
export type AppCommandAutocompleteCallback = (
  ctx: InteractionContext<APIApplicationCommandAutocompleteInteraction>,
) => Promise<AutocompleteChoices>;

export type AppCommandCallback =
  | ChatInputAppCommandCallback<boolean>
  | MessageAppCommandCallback
  | UserAppCommandCallback;

export type AppCommandHandlers = {
  handlers: Record<string, AppCommandCallback>;
  autocompleteHandlers?: Record<string, AppCommandAutocompleteCallback>;
};

export const appCommands: Record<
  ApplicationCommandType,
  Record<string, AppCommandHandlers>
> = {
  [ApplicationCommandType.ChatInput]: {
    // buttons: {
    //   handlers: {
    //     add: addComponentChatEntry,
    //     edit: editComponentChatEntry,
    //     delete: deleteComponentChatEntry,
    //     migrate: migrateComponentsChatEntry,
    //   },
    //   autocompleteHandlers: {
    //     add: addComponentMessageAutocomplete,
    //     edit: addComponentMessageAutocomplete,
    //     delete: addComponentMessageAutocomplete,
    //     migrate: addComponentMessageAutocomplete,
    //   },
    // },
    format: {
      handlers: {
        mention: formatMentionCallback,
        channel: formatChannelCallback,
        emoji: formatEmojiCallback,
      },
    },
    id: {
      handlers: {
        mention: idMentionCallback,
        channel: idChannelCallback,
        emoji: idEmojiCallback,
      },
    },
    invite: { handlers: { BASE: inviteCallback } },
    // triggers: {
    //   handlers: {
    //     add: addTriggerCallback,
    //     view: viewTriggerCallback,
    //   },
    //   autocompleteHandlers: {
    //     view: triggerAutocompleteCallback,
    //   },
    // },
    // webhook: {
    //   handlers: {
    //     create: webhookCreateEntry,
    //     info: webhookInfoCallback,
    //     delete: webhookDeleteEntryCallback,
    //   },
    //   autocompleteHandlers: {
    //     delete: webhookAutocomplete,
    //     info: webhookAutocomplete,
    //   },
    // },
    // welcomer: {
    //   handlers: {
    //     set: welcomerSetupEntry,
    //     view: welcomerViewEntry,
    //     delete: welcomerDeleteEntry,
    //   },
    //   autocompleteHandlers: {
    //     set: webhookAutocomplete,
    //   },
    // },
    help: {
      handlers: { BASE: helpEntry },
      autocompleteHandlers: { BASE: helpAutocomplete },
    },
    // "reaction-role": {
    //   handlers: {
    //     create: createReactionRoleHandler,
    //     delete: deleteReactionRoleHandler,
    //     list: listReactionRolesHandler,
    //   },
    //   autocompleteHandlers: {
    //     create: messageAndEmojiAutocomplete,
    //     // I think it would be cool to have the delete `message` results
    //     // filtered by messages that have registered reaction roles, but I
    //     // can't think of a particularly efficient way to do that right now
    //     delete: messageAndEmojiAutocomplete,
    //     list: autocompleteMessageCallback,
    //   },
    // },
    // restore: {
    //   handlers: {
    //     BASE: restoreMessageChatInputCallback,
    //   },
    //   autocompleteHandlers: {
    //     BASE: autocompleteMessageCallback,
    //   },
    // },
    deluxe: {
      handlers: {
        info: deluxeInfoCallback,
        sync: deluxeSyncCallback,
      },
    },
    // // dev server
    leave: { handlers: { BASE: leaveCommandHandler } },
    "grant-deluxe": {
      handlers: { BASE: grantDeluxeCommandHandler },
    },
    "revoke-deluxe": {
      handlers: { BASE: revokeDeluxeCommandHandler },
    },
    profile: {
      handlers: {
        set: profileSetCallback,
        clear: profileClearCallback,
      },
    },
  },
  [ApplicationCommandType.Message]: {
    // "Buttons & Components": {
    //   handlers: {
    //     BASE: addComponentMessageEntry,
    //   },
    // },
    // "Quick Edit": {
    //   handlers: { BASE: quickEditMessageEntry },
    // },
    // Restore: {
    //   handlers: {
    //     BASE: restoreMessageEntry,
    //   },
    // },
    // "Webhook Info": {
    //   handlers: {
    //     BASE: webhookInfoMsgCallback,
    //   },
    // },
    // Debug: {
    //   handlers: {
    //     BASE: debugMessageCallback,
    //   },
    // },
  },
  [ApplicationCommandType.User]: {},
  [ApplicationCommandType.PrimaryEntryPoint]: {},
};

const bannedUserIds = ["1201838301674479672"];

export const interactionCreateHandler = async ({
  client,
  data: interaction,
}: ToEventProps<APIInteraction>) => {
  if (
    (interaction.user && bannedUserIds.includes(interaction.user.id)) ||
    (interaction.member && bannedUserIds.includes(interaction.member.user.id))
  ) {
    console.log(
      "Forbidden usage",
      interaction.member?.user?.id ?? interaction.user?.id,
    );
    await client.api.interactions.reply(interaction.id, interaction.token, {
      content:
        "Sorry, you are forbidden from using this bot. If this seems like a mistake, contact support.",
      flags: MessageFlags.Ephemeral,
    });
    return;
  }

  if (
    interaction.type === InteractionType.ApplicationCommand ||
    interaction.type === InteractionType.ApplicationCommandAutocomplete
  ) {
    let qualifiedOptions = "";
    if (interaction.data.type === ApplicationCommandType.ChatInput) {
      const appendOption = (
        option: APIApplicationCommandInteractionDataOption,
      ) => {
        if (option.type === ApplicationCommandOptionType.SubcommandGroup) {
          qualifiedOptions += ` ${option.name}`;
          for (const opt of option.options) {
            appendOption(opt);
          }
        } else if (option.type === ApplicationCommandOptionType.Subcommand) {
          qualifiedOptions += ` ${option.name}`;
        }
      };
      for (const option of interaction.data.options ?? []) {
        appendOption(option);
      }
    }

    const commandData =
      appCommands[interaction.data.type][interaction.data.name];
    if (!commandData) {
      console.warn("Received unknown command", interaction.data.name);
      return; // Unknown command;
    }

    if (interaction.type === InteractionType.ApplicationCommand) {
      const handler = commandData.handlers[qualifiedOptions.trim() || "BASE"];
      if (!handler) {
        return; // Cannot handle this command
      }

      const ctx = new InteractionContext(client, interaction);
      try {
        await (handler as AppCommandCallbackT<APIInteraction>)(ctx);
        return;
      } catch (e) {
        if (isDiscordError(e)) {
          await sendErrorMessage(ctx, e.rawError);
        } else {
          console.error(e);
        }
        return; // 500
      }
    } else {
      const ctx = new InteractionContext(client, interaction);
      if (!commandData.autocompleteHandlers) {
        await ctx.createAutocompleteResponse([]);
        return;
      }
      const handler =
        commandData.autocompleteHandlers[qualifiedOptions.trim() || "BASE"];
      if (!handler) {
        await ctx.createAutocompleteResponse([]);
        return;
      }

      try {
        const response = await handler(ctx);
        // Normally I wouldn't truncate data at this level but this just
        // makes it a lot easier if the limit is changed in the future,
        // and there's hardly a reason I would *want* to go over the limit
        // in a callback
        await ctx.createAutocompleteResponse(response.slice(0, 25));
        return;
      } catch (e) {
        console.error(e);
      }
      await ctx.createAutocompleteResponse([]);
      return;
    }
    // } else if (interaction.type === InteractionType.MessageComponent) {
    //   const { custom_id: customId, component_type: type } = interaction.data;
    //   if (customId.startsWith("t_")) {
    //     const state = await env.KV.get<MinimumKVComponentState>(
    //       `component-${type}-${customId}`,
    //       "json",
    //     );
    //     if (!state) {
    //       return respond({ error: "Unknown component" });
    //     }

    //     const handler = componentStore[
    //       state.componentRoutingId as ComponentRoutingId
    //     ] as ComponentCallbackT<APIMessageComponentInteraction>;
    //     if (!handler) {
    //       return respond({ error: "Unknown routing ID" });
    //     }

    //     const ctx = new InteractionContext(rest, interaction, env, state);
    //     try {
    //       const response = await handler(ctx);
    //       if (state.componentOnce) {
    //         try {
    //           await env.KV.delete(`component-${type}-${customId}`);
    //         } catch {}
    //       }
    //       if (Array.isArray(response)) {
    //         eCtx.waitUntil(response[1]());
    //         return respond(response[0]);
    //       } else {
    //         return respond(response);
    //       }
    //     } catch (e) {
    //       if (isDiscordError(e)) {
    //         const errorResponse = getErrorMessage(ctx, e.rawError);
    //         if (errorResponse) {
    //           return respond(errorResponse);
    //         }
    //       } else {
    //         console.error(e);
    //       }
    //       return respond({
    //         error: "You've found a super unlucky error. Try again later!",
    //         status: 500,
    //       });
    //     }
    //   } else if (customId.startsWith("p_")) {
    //     const ctx = new InteractionContext(rest, interaction, env);
    //     const guildId = interaction.guild_id;
    //     if (!guildId) {
    //       return respond({ error: "Must be in a guild context", status: 400 });
    //     }

    //     const db = getDb(env.HYPERDRIVE);
    //     const doId = env.COMPONENTS.idFromName(
    //       `${interaction.message.id}-${customId}`,
    //     );
    //     const stub = env.COMPONENTS.get(doId, { locationHint: "enam" });
    //     const response = await stub.fetch("http://do/", { method: "GET" });
    //     let component: DurableStoredComponent;
    //     if (response.status === 404) {
    //       // In case a durable object does not exist for this component for
    //       // whatever reason. Usually because of migrated components that have
    //       // not yet actually been activated.
    //       const componentId = getComponentId(
    //         type === ComponentType.Button
    //           ? { type, style: ButtonStyle.Primary, custom_id: customId }
    //           : { type, custom_id: customId },
    //       );

    //       if (componentId === undefined) {
    //         return respond({ error: "Bad Request", status: 400 });
    //       }

    //       // Don't allow component data to leak into other servers
    //       const dryComponent = await db.query.discordMessageComponents.findFirst({
    //         where: (table, { eq }) => eq(table.id, componentId),
    //         columns: { guildId: true, channelId: true },
    //         with: {
    //           createdBy: {
    //             columns: { discordId: true },
    //           },
    //         },
    //       });
    //       if (!dryComponent) {
    //         return respond(
    //           ctx.reply({
    //             content:
    //               "No data could be found for this component. It may have been deleted by a moderator but not removed from the message.",
    //             ephemeral: true,
    //           }),
    //         );
    //       }
    //       if (!dryComponent.guildId) {
    //         if (
    //           // Allow the component creator to set this data since it's obvious
    //           // they can access the component's contents
    //           dryComponent.createdBy?.discordId &&
    //           dryComponent.createdBy.discordId === BigInt(ctx.user.id)
    //         ) {
    //           await db
    //             .update(discordMessageComponents)
    //             .set({
    //               guildId: BigInt(guildId),
    //               channelId: BigInt(interaction.channel.id),
    //             })
    //             .where(eq(discordMessageComponents.id, componentId));

    //           dryComponent.guildId = BigInt(guildId);
    //           dryComponent.channelId = BigInt(interaction.channel.id);
    //         } else {
    //           return respond(
    //             ctx.reply({
    //               content: [
    //                 "This component hasn't been linked with a server. Please tell",
    //                 "the component owner (the person who created the component on",
    //                 "the Discohook site) to use the component at least once. This",
    //                 "will link the component with the current server. After you do",
    //                 "this, the component should work as expected.",
    //               ].join(" "),
    //               ephemeral: true,
    //             }),
    //           );
    //         }
    //       } else if (dryComponent.guildId.toString() !== interaction.guild_id) {
    //         return respond({
    //           error: response.statusText,
    //           status: response.status,
    //         });
    //         // ctx.reply({
    //         //   content: [
    //         //     "The server associated with this component does not match the current server.",
    //         //     "If this component should be able to be used in this server,",
    //         //     "contact support to have its server association changed.",
    //         //   ].join(" "),
    //         //   ephemeral: true,
    //         // }),
    //       }

    //       const params = new URLSearchParams({ id: componentId.toString() });
    //       if (
    //         new MessageFlagsBitField(interaction.message.flags ?? 0).has(
    //           MessageFlags.Ephemeral,
    //         )
    //       ) {
    //         // Ephemeral buttons last one hour to avoid durable object clutter.
    //         // To be honest, this is not necessary at all, but if someone spams
    //         // any button then we would rather the requests go to Cloudflare and
    //         // not the database.
    //         params.set(
    //           "expireAt",
    //           new Date(new Date().getTime() + 3_600_000).toISOString(),
    //         );
    //       }
    //       const doResponse = await stub.fetch(`http://do/?${params}`, {
    //         method: "PUT",
    //       });
    //       if (!doResponse.ok) {
    //         return respond({
    //           error: doResponse.statusText,
    //           status: doResponse.status,
    //         });
    //       }
    //       component = await doResponse.json();
    //     } else if (!response.ok) {
    //       return respond({
    //         error: response.statusText,
    //         status: response.status,
    //       });
    //     } else {
    //       component = (await response.json()) as DurableStoredComponent;
    //     }
    //     // if (component.draft) {
    //     //   return respond({ error: "Component is marked as draft" });
    //     // }

    //     let guild: TriggerKVGuild;
    //     try {
    //       guild = await getchTriggerGuild(rest, env, guildId);
    //     } catch (e) {
    //       if (isDiscordError(e) && e.code === RESTJSONErrorCodes.UnknownGuild) {
    //         return respond(
    //           ctx.reply({
    //             content:
    //               "Discohook Utils needs to be a member of this server in order to use components.",
    //             ephemeral: true,
    //             components: [
    //               {
    //                 type: ComponentType.ActionRow,
    //                 components: [
    //                   {
    //                     type: ComponentType.Button,
    //                     style: ButtonStyle.Link,
    //                     label: "Add Bot",
    //                     url: `https://discord.com/oauth2/authorize?${new URLSearchParams(
    //                       {
    //                         client_id: interaction.application_id,
    //                         scope: "bot",
    //                         guild_id: guildId,
    //                         disable_guild_select: "true",
    //                         integration_type: String(
    //                           ApplicationIntegrationType.GuildInstall,
    //                         ),
    //                       },
    //                     )}`,
    //                   },
    //                 ],
    //               },
    //             ],
    //           }),
    //         );
    //       }
    //       throw e;
    //     }

    //     const liveVars: LiveVariables = {
    //       guild,
    //       member: interaction.member,
    //       user: interaction.member?.user,
    //     };
    //     switch (interaction.data.component_type) {
    //       case ComponentType.ChannelSelect:
    //       case ComponentType.MentionableSelect:
    //       case ComponentType.UserSelect:
    //       case ComponentType.RoleSelect:
    //         liveVars.selected_values = interaction.data.values;
    //         liveVars.selected_resolved = interaction.data.resolved;
    //         break;
    //       case ComponentType.StringSelect:
    //         liveVars.selected_values = interaction.data.values;
    //         break;
    //       default:
    //         break;
    //     }

    //     const allFlows = component.componentsToFlows.map((ctf) => ctf.flow);
    //     let flows: Flow[] = [];
    //     switch (component.data.type) {
    //       case ComponentType.Button: {
    //         if (component.data.type !== interaction.data.component_type) break;

    //         if (component.data.style === ButtonStyle.Link) break;
    //         flows = allFlows;
    //         break;
    //       }
    //       case ComponentType.StringSelect: {
    //         if (component.data.type !== interaction.data.component_type) break;

    //         // While we do have the logic to handle multiple selected values,
    //         // it's currently unsupported behavior and is overwritten when
    //         // saving components. Nonetheless, if a user manually saved a select
    //         // menu allowing multiple values, we are able to deal with it
    //         // gracefully. Should we truncate here too?
    //         flows = Object.entries(component.data.flowIds)
    //           .filter(([key]) =>
    //             (
    //               interaction.data as APIMessageStringSelectInteractionData
    //             ).values.includes(key),
    //           )
    //           .map(([_, flowId]) =>
    //             allFlows.find((flow) => String(flow.id) === flowId),
    //           )
    //           .filter((v): v is NonNullable<typeof v> => Boolean(v));
    //         break;
    //       }
    //       case ComponentType.ChannelSelect:
    //       case ComponentType.MentionableSelect:
    //       case ComponentType.RoleSelect:
    //       case ComponentType.UserSelect: {
    //         if (component.data.type !== interaction.data.component_type) break;

    //         flows = allFlows;
    //         break;
    //       }
    //       default:
    //         break;
    //     }
    //     if (env.ENVIRONMENT === "dev") console.log(flows.map((f) => f.actions));
    //     if (flows.length === 0) {
    //       const messageCreatedAt = Snowflake.parse(
    //         interaction.message.id,
    //         new Date(2015, 0),
    //       ).timestamp;
    //       const maybeMigrate =
    //         messageCreatedAt < new Date("2024-09-06").valueOf();

    //       return respond(
    //         liveVars.guild?.owner_id === ctx.user.id ||
    //           ctx.userPermissons.has(
    //             PermissionFlags.ManageMessages,
    //             PermissionFlags.ManageWebhooks,
    //           )
    //           ? ctx.reply({
    //               content: `${t("noComponentFlow")} ${
    //                 maybeMigrate ? t("noComponentFlowMigratePrompt") : ""
    //               }`,
    //               components: [
    //                 new ActionRowBuilder<ButtonBuilder>().addComponents(
    //                   new ButtonBuilder()
    //                     .setStyle(ButtonStyle.Link)
    //                     .setURL(
    //                       `${env.DISCOHOOK_ORIGIN}/edit/component/${component.id}`,
    //                     )
    //                     .setLabel(t("customize")),
    //                 ),
    //               ],
    //               ephemeral: true,
    //             })
    //           : ctx.updateMessage({}),
    //       );
    //     }

    //     // Don't like this. We should be returning a response
    //     // from one of the flows instead, especially for modals.
    //     eCtx.waitUntil(
    //       (async () => {
    //         for (const flow of flows) {
    //           const result = await executeFlow({
    //             env,
    //             flow,
    //             rest,
    //             db,
    //             liveVars,
    //             setVars: {
    //               guildId,
    //               channelId: interaction.channel.id,
    //               // Possible confusing conflict with Delete Message action
    //               messageId: interaction.message.id,
    //               userId: ctx.user.id,
    //             },
    //             ctx,
    //             recursion: 0,
    //             deferred: true,
    //           });
    //           if (env.ENVIRONMENT === "dev") console.log(result);
    //         }
    //       })(),
    //     );
    //     return respond(ctx.updateMessage({}));
    //   } else if (customId.startsWith("a_")) {
    //     // "Auto" components require only the state defined in their custom ID,
    //     // allowing them to have an unlimited timeout.
    //     // Example: `a_delete-reaction-role_123456789012345679:✨`
    //     //           auto  routing id       message id         reaction
    //     const { routingId } = parseAutoComponentId(customId);
    //     const handler = componentStore[
    //       routingId as ComponentRoutingId
    //     ] as ComponentCallbackT<APIMessageComponentInteraction>;
    //     if (!handler) {
    //       return respond({ error: "Unknown routing ID" });
    //     }

    //     const ctx = new InteractionContext(rest, interaction, env);
    //     try {
    //       const response = await handler(ctx);
    //       if (Array.isArray(response)) {
    //         eCtx.waitUntil(response[1]());
    //         return respond(response[0]);
    //       } else {
    //         return respond(response);
    //       }
    //     } catch (e) {
    //       if (isDiscordError(e)) {
    //         const errorResponse = getErrorMessage(ctx, e.rawError);
    //         if (errorResponse) {
    //           return respond(errorResponse);
    //         }
    //       } else {
    //         console.error(e);
    //       }
    //       return respond({
    //         error: "You've found a super unlucky error. Try again later!",
    //         status: 500,
    //       });
    //     }
    //   } else if (interaction.data.component_type === ComponentType.Button) {
    //     // Check for unmigrated buttons and migrate them
    //     const db = getDb(env.HYPERDRIVE);
    //     const ctx = new InteractionContext(rest, interaction, env);
    //     const guildId = interaction.guild_id;
    //     if (!guildId) {
    //       return respond({ error: "No guild ID" });
    //     }

    //     eCtx.waitUntil(
    //       (async () => {
    //         let inserted: Pick<
    //           typeof discordMessageComponents.$inferSelect,
    //           "id" | "data"
    //         >[];
    //         let rows: APIActionRowComponent<APIComponentInMessageActionRow>[];
    //         let guild: TriggerKVGuild;
    //         let oldIdMap: Record<string, string>;
    //         try {
    //           ({ inserted, rows, guild, oldIdMap } = await migrateLegacyButtons(
    //             env,
    //             rest,
    //             db,
    //             guildId,
    //             interaction.message,
    //           ));
    //         } catch (e) {
    //           return respond(
    //             ctx.reply({
    //               content: String(e),
    //               flags: MessageFlags.Ephemeral,
    //             }),
    //           );
    //         }
    //         await ctx.followup.editOriginalMessage({ components: rows });

    //         const thisButton = inserted.find(
    //           (b) => String(b.id) === oldIdMap[customId],
    //         );
    //         if (
    //           thisButton &&
    //           thisButton.data.type === ComponentType.Button &&
    //           thisButton.data.style !== ButtonStyle.Link &&
    //           thisButton.data.style !== ButtonStyle.Premium
    //         ) {
    //           const liveVars: LiveVariables = {
    //             guild,
    //             member: interaction.member,
    //             user: interaction.member?.user,
    //           };
    //           const result = await executeFlow({
    //             env,
    //             flow: thisButtonData.componentsToFlows[0].flow,
    //             rest,
    //             db,
    //             liveVars,
    //             setVars: {
    //               channelId: interaction.channel.id,
    //               messageId: interaction.message.id,
    //               userId: ctx.user.id,
    //             },
    //             ctx,
    //             recursion: 0,
    //             deferred: true,
    //           });
    //           if (env.ENVIRONMENT === "dev") console.log(result);
    //         }
    //       })(),
    //     );

    //     // Discord needs to know whether our eventual response will be ephemeral
    //     // const thisOldButton = oldMessageButtons.find((b) => getOldCustomId(b));
    //     // const ephemeral = !!(
    //     //   thisOldButton &&
    //     //   (thisOldButton.roleId || thisOldButton.customEphemeralMessageData)
    //     // );

    //     // We might have an ephemeral followup but our first followup is always
    //     // editOriginalMessage. Luckily this doesn't matter anymore.
    //     return respond(ctx.defer({ thinking: false, ephemeral: false }));
    //   }
    //   return respond({
    //     error: "Component custom ID does not contain a valid prefix",
    //   });
    // } else if (interaction.type === InteractionType.ModalSubmit) {
    //   const { custom_id: customId } = interaction.data;
    //   if (customId.startsWith("t_")) {
    //     const state = await env.KV.get<MinimumKVComponentState>(
    //       `modal-${customId}`,
    //       "json",
    //     );
    //     if (!state) {
    //       return respond({ error: "Unknown modal" });
    //     }

    //     const handler = modalStore[state.componentRoutingId as ModalRoutingId];
    //     if (!handler) {
    //       return respond({ error: "Unknown routing ID" });
    //     }

    //     const ctx = new InteractionContext(rest, interaction, env, state);
    //     try {
    //       const response = await handler(ctx);
    //       if (state.componentOnce) {
    //         try {
    //           await env.KV.delete(`modal-${customId}`);
    //         } catch {}
    //       }
    //       if (Array.isArray(response)) {
    //         eCtx.waitUntil(response[1]());
    //         return respond(response[0]);
    //       } else {
    //         return respond(response);
    //       }
    //     } catch (e) {
    //       if (isDiscordError(e)) {
    //         const errorResponse = getErrorMessage(ctx, e.rawError);
    //         if (errorResponse) {
    //           return respond(errorResponse);
    //         }
    //       } else {
    //         console.error(e);
    //       }
    //       return respond({
    //         error: "You've found a super unlucky error. Try again later!",
    //         status: 500,
    //       });
    //     }
    //   } else if (customId.startsWith("a_")) {
    //     const { routingId } = parseAutoComponentId(customId);
    //     const handler = modalStore[routingId as ModalRoutingId];
    //     if (!handler) {
    //       return respond({ error: "Unknown routing ID" });
    //     }

    //     const ctx = new InteractionContext(rest, interaction, env);
    //     try {
    //       const response = await handler(ctx);
    //       if (Array.isArray(response)) {
    //         eCtx.waitUntil(response[1]());
    //         return respond(response[0]);
    //       } else {
    //         return respond(response);
    //       }
    //     } catch (e) {
    //       if (isDiscordError(e)) {
    //         const errorResponse = getErrorMessage(ctx, e.rawError);
    //         if (errorResponse) {
    //           return respond(errorResponse);
    //         }
    //       } else {
    //         console.error(e);
    //       }
    //       return respond({
    //         error: "You've found a super unlucky error. Try again later!",
    //         status: 500,
    //       });
    //     }
    //   }
    // }
  }

  console.error("Unknown interaction type");
  return;
};

```

### File: `packages/bot-rw/src/commands/help.ts`
```ts
import type { APIEmbed } from "discord-api-types/v10";
import { color } from "../util/meta.js";
import type {
  AppCommandAutocompleteCallback,
  ChatInputAppCommandCallback,
} from "./handler.js";

type HelpTags = Record<string, APIEmbed | string>;

export const fetchTags = async () => {
  const response = await fetch(`${Bun.env.DISCOHOOK_ORIGIN}/help/en.json`, {
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

  const tags = await fetchTags();
  const [, embed] = findEmbed(tags, query.value);

  if (embed) {
    embed.color = embed.color ?? color;
    await ctx.reply({
      content: mentionUser ? `<@${mentionUser.id}>` : undefined,
      allowedMentions: mentionUser ? { users: [mentionUser.id] } : undefined,
      // These messages are ephemeral by default to reduce spam
      ephemeral: !mentionUser || mentionUser.bot,
      embeds: [embed],
    });
    return;
  }

  const entries = Object.entries(tags)
    .filter((v) => typeof v[1] !== "string")
    .map((v) => [v[0], v[1]] as [string, APIEmbed])
    .filter((v) => v[1].title === query.value.trim());

  if (entries.length !== 0) {
    const e = entries[0]?.[1];
    if (e) {
      e.color = e.color ?? color;
      await ctx.reply({
        embeds: [e],
        ephemeral: true,
      });
      return;
    }
  }

  await ctx.reply({
    content:
      "No tag found. Select an item from the autocomplete menu or use the exact title of a valid item.",
    ephemeral: true,
  });
};

export const helpAutocomplete: AppCommandAutocompleteCallback = async (ctx) => {
  const query = ctx.getStringOption("tag");

  const tags = await fetchTags();
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

### File: `packages/bot-rw/src/commands/id.ts`
```ts
import { parseEmojiOption } from "./format.js";
import type { ChatInputAppCommandCallback } from "./handler.js";

export const idMentionCallback: ChatInputAppCommandCallback = async (ctx) => {
  // biome-ignore lint/style/noNonNullAssertion: Required option
  const target = ctx.getMentionableOption("target")!;
  await ctx.reply({
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
  await ctx.reply({
    content: target.id,
    ephemeral: true,
  });
};

export const idEmojiCallback: ChatInputAppCommandCallback = async (ctx) => {
  const emoji = await parseEmojiOption(ctx, "target");
  if (!emoji) {
    await ctx.reply({
      content: "No emoji was found.",
      ephemeral: true,
    });
    return;
  }

  await ctx.reply({
    content:
      typeof emoji === "object" ? (emoji.id ?? ctx.t("idUnavailable")) : emoji,
    ephemeral: true,
  });
};

```

### File: `packages/bot-rw/src/commands/invite.ts`
```ts
import { ButtonBuilder, ContainerBuilder } from "@discordjs/builders";
import { ButtonStyle } from "@discordjs/core";
import { PermissionFlags, PermissionsBitField } from "discord-bitflag";
import { cdn } from "../util/cdn.js";
import type { ChatInputAppCommandCallback } from "./handler.js";

const permissions = new PermissionsBitField(0);
// permissions.set(PermissionFlags.ManageGuild, true);
// Create & manage webhooks & their messages
permissions.set(PermissionFlags.ManageWebhooks, true);
permissions.set(PermissionFlags.ManageChannels, true);
permissions.set(PermissionFlags.ManageMessages, true);
// Flows (add/remove roles from members)
permissions.set(PermissionFlags.ManageRoles, true);
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
// permissions.set(PermissionFlags.ModerateMembers, true);
// Profile (nickname)
permissions.set(PermissionFlags.ChangeNickname, true);

const url = new URL(
  `https://discord.com/oauth2/authorize?${new URLSearchParams({
    client_id: Bun.env.DISCORD_APPLICATION_ID,
    permissions: permissions.toString(),
    scope: "bot",
  })}`,
);

export const inviteCallback: ChatInputAppCommandCallback = async (ctx) => {
  const emojiId = ctx.isPremium()
    ? "1356993126513901599" // pink
    : "793970422504751114"; // blue

  const container = new ContainerBuilder()
    .addSectionComponents((s) =>
      s
        .addTextDisplayComponents((t) =>
          t.setContent(
            "## Add Discohook to your server\nAfter inviting, you can use Discohook to create buttons, selects, and custom flows.",
          ),
        )
        .setThumbnailAccessory((t) => t.setURL(cdn.emoji(emojiId))),
    )
    .addActionRowComponents((r) =>
      r.addComponents(
        new ButtonBuilder()
          .setStyle(ButtonStyle.Link)
          .setURL(url.href)
          .setLabel("Invite"),
        new ButtonBuilder()
          .setStyle(ButtonStyle.Link)
          .setURL(`${Bun.env.DISCOHOOK_ORIGIN}/guide`)
          .setLabel("Guides"),
      ),
    );

  await ctx.reply({
    components: [container],
    ephemeral: true,
    componentsV2: true,
  });
};

```

### File: `packages/bot-rw/src/commands/profile.ts`
```ts
import { ContainerBuilder } from "@discordjs/builders";
import {
  type APIGuildMember,
  PermissionFlagsBits,
  RESTJSONErrorCodes,
  Routes,
} from "discord-api-types/v10";
import { cdn, readAttachment, userAvatarUrl } from "../util/cdn.js";
import { textDisplay } from "../util/components.js";
import { isDiscordError } from "../util/error.js";
import { color } from "../util/meta.js";
import { getUserTag } from "../util/user.js";
import type { ChatInputAppCommandCallback } from "./handler.js";

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
          bio === null || bio === ""
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
  const nickField = ctx.getStringOption("name")?.value?.trim() || undefined;
  const bannerField = ctx.getAttachmentOption("banner");
  const avatarField = ctx.getAttachmentOption("avatar");

  // as far as i know the other fields are not permission-restricted right now
  if (nickField && !ctx.appPermissons.has(PermissionFlagsBits.ChangeNickname)) {
    return ctx.reply({
      content:
        "I need the **Change Nickname** permission to change my own nickname.",
      ephemeral: true,
    });
  }

  if (!nickField && !bannerField && !avatarField) {
    let member: APIGuildMember;
    try {
      // empty PATCH to get own bio
      member = (await ctx.client.rest.patch(
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
        member = (await ctx.client.rest.get(
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

  await ctx.defer({ componentsV2: true, ephemeral: true });

  const body: ModifyCurrentMemberBody = { nick: nickField };
  if (avatarField) {
    const avatar = await readAttachment(avatarField.url);
    body.avatar = avatar;
  }
  if (bannerField) {
    const banner = await readAttachment(bannerField.url);
    body.banner = banner;
  }

  const member = (await ctx.client.rest.patch(
    Routes.guildMember(ctx.interaction.guild_id, "@me"),
    {
      body,
      reason: `${getUserTag(ctx.user)} (${ctx.user.id}) via /profile set`,
    },
  )) as APIGuildMember;
  await ctx.followup.editOriginalMessage({
    // I don't really like how plain this is
    components: [
      textDisplay("Profile updated."),
      getMemberProfileContainer(member, ctx.interaction.guild_id, body.bio),
    ],
    componentsV2: true,
  });
};

export const profileClearCallback: ChatInputAppCommandCallback<true> = async (
  ctx,
) => {
  const value = (ctx.getStringOption("value")?.value || undefined) as
    | "name"
    | "avatar"
    | "banner"
    | undefined;

  await ctx.defer({ ephemeral: true });

  const body: ModifyCurrentMemberBody = {};
  if (value) {
    body[value === "name" ? "nick" : value] = null;
  } else {
    body.nick = null;
    body.avatar = null;
    body.banner = null;
    body.bio = null;
  }

  await ctx.client.rest.patch(
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
};

```

### File: `packages/bot-rw/src/commands/reactionRoles.ts`
```ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  EmbedBuilder,
  messageLink,
} from "@discordjs/builders";
import dedent from "dedent-js";
import {
  type APIMessage,
  type APIPartialEmoji,
  type APIRole,
  ButtonStyle,
  CDNRoutes,
  ImageFormat,
  RouteBases,
} from "discord-api-types/v10";
import { isSnowflake } from "discord-snowflake";
import { and, eq } from "drizzle-orm";
import { discordReactionRoles, makeSnowflake, upsertGuild } from "store";
import type { Client } from "../client.js";
import type { AutoComponentCustomId, ButtonCallback } from "../components.js";
import { isActionRow, parseAutoComponentId } from "../util/components.js";
import { color } from "../util/meta.js";
import {
  autocompleteMessageCallback,
  resolveMessageLink,
} from "./components/entry.js";
import type {
  AppCommandAutocompleteCallback,
  ChatInputAppCommandCallback,
} from "./handler.js";

export const isSnowflakeSafe = (id: string): id is `${bigint}` => {
  try {
    return isSnowflake(id);
  } catch {
    return false;
  }
};

export const CUSTOM_EMOJI_RE = /^<(a)?:(\w+):(\d+)>/;

export const resolveEmoji = async (
  client: Client,
  value: string,
  message: APIMessage | undefined,
  guildId: string,
): Promise<APIPartialEmoji | undefined> => {
  const match = value.match(CUSTOM_EMOJI_RE);
  if (match?.[3]) {
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
        name: match[2] ?? null,
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
    const manager = await client.fetchEmojiManager(guildId);
    emoji = manager.emojis.find((e) =>
      isSnowflakeSafe(value)
        ? e.id === value || e.name === val
        : e.name === val,
    );
  }
  // Try unicode emojis
  if (!emoji) {
    try {
      const { nameToEmoji, emojiToName } = await client.fetchEmojis();

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
    const cached = await ctx.client.KV.get<APIPartialEmoji[]>(kvKey, "json");
    let emojis = cached;
    if (!emojis) {
      const guildEmojis = await ctx.client.api.guilds.getEmojis(guildId);
      emojis = guildEmojis.map(
        (e) => ({ id: e.id, name: e.name }) satisfies APIPartialEmoji,
      );

      await ctx.client.KV.put(kvKey, JSON.stringify(emojis), {
        expirationTtl: 3600,
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

// MAYBE BUG: I've seen reports of incorrect position calculation but I have
// not confirmed them
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
  const guild = await ctx.client.api.guilds.get(guildId);

  // biome-ignore lint/style/noNonNullAssertion: Required option
  const role = ctx.getRoleOption("role")!;
  if (role.managed) {
    await ctx.reply({
      content: `<@&${role.id}> can't be assigned to members.`,
      ephemeral: true,
    });
    return;
  }

  const me = await ctx.client.api.guilds.getMember(
    guildId,
    Bun.env.DISCORD_APPLICATION_ID,
  );
  const botHighestRole = getHighestRole(guild.roles, me.roles);
  if (!botHighestRole && guild.owner_id !== Bun.env.DISCORD_APPLICATION_ID) {
    // You could be running an instance of this bot where
    // the bot is the owner of the guild
    await ctx.reply({
      content: `I can't assign <@&${role.id}> to members because I don't have any roles.`,
      ephemeral: true,
    });
    return;
  } else if (botHighestRole && role.position >= botHighestRole.position) {
    await ctx.reply({
      content: `<@&${role.id}> is higher than my highest role (<@&${botHighestRole.id}>), so I can't assign it to members. <@&${role.id}> needs to be lower in the role list, or my highest role needs to be higher.`,
      ephemeral: true,
    });
    return;
  }
  // biome-ignore lint/style/noNonNullAssertion: guild-only
  const member = ctx.interaction.member!;
  const memberHighestRole = getHighestRole(guild.roles, member.roles);
  if (guild.owner_id !== ctx.user.id) {
    // Guild owner can always do everything
    if (!memberHighestRole) {
      // This message should never be seen unless someone messes with permissions
      await ctx.reply({
        content: `You can't assign <@&${role.id}> to members because you don't have any roles.`,
        ephemeral: true,
      });
      return;
    } else if (
      memberHighestRole &&
      role.position >= memberHighestRole.position
    ) {
      await ctx.reply({
        content: `<@&${role.id}> is higher than your highest role (<@&${memberHighestRole.id}>), so you can't select it to be assigned to members. <@&${role.id}> needs to be lower in the role list, or your highest role needs to be higher.`,
        ephemeral: true,
      });
      return;
    }
  }

  const message = await resolveMessageLink(
    ctx.client,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    await ctx.reply({
      content: message,
      ephemeral: true,
    });
    return;
  }

  const emoji = await resolveEmoji(
    ctx.client,
    ctx.getStringOption("emoji").value,
    message,
    guildId,
  );
  if (!emoji) {
    await ctx.reply({
      content:
        "The emoji you specified couldn't be found. For best results, react to the message with the desired emoji before running this command.",
      ephemeral: true,
    });
    return;
  }

  // biome-ignore lint/style/noNonNullAssertion: Must have at least one
  const reaction = (emoji.id ?? emoji.name)!;
  const reactionMention = emoji.id
    ? `<${emoji.animated ? "a" : ""}:${emoji.name}:${emoji.id}>`
    : reaction;

  try {
    await ctx.client.api.channels.addMessageReaction(
      message.channel_id,
      message.id,
      emoji.id
        ? `${emoji.animated ? "a:" : ""}${emoji.name}:${emoji.id}`
        : // biome-ignore lint/style/noNonNullAssertion: Required in this case
          emoji.name!,
    );
  } catch {
    await ctx.reply({
      content: `Failed to add the reaction (${reactionMention}) to the message.`,
      ephemeral: true,
    });
    return;
  }

  await ctx.client.KV.put(
    `discord-reaction-role-${message.id}-${reaction}`,
    JSON.stringify({ roleId: role.id }),
    { expirationTtl: 86400 }, // prev 7x as much
  );
  const db = ctx.client.getDb();
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
      set: { roleId: makeSnowflake(role.id) },
    });
  await ctx.reply({
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
    ctx.client,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    await ctx.reply({
      content: message,
      ephemeral: true,
    });
    return;
  }

  const emojiValue: string | undefined = ctx.getStringOption("emoji")?.value;
  if (emojiValue) {
    // We should only care about reactions that are actually on the message,
    // but all reactions may have been removed by accident.
    const emoji = await resolveEmoji(ctx.client, emojiValue, message, guildId);
    if (!emoji) {
      await ctx.reply({
        content:
          "The emoji you specified couldn't be found. For best results, react to the message with the desired emoji before running this command.",
        ephemeral: true,
      });
      return;
    }
    // biome-ignore lint/style/noNonNullAssertion: Must have at least one
    const reaction = (emoji.id ?? emoji.name)!;

    const db = ctx.client.getDb();
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
    ctx.client.KV.delete(
      `discord-reaction-role-${message.id}-${reaction}`,
    ).catch(() => {});

    await ctx.reply({
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
    return;
  }

  const db = ctx.client.getDb();
  const entries = await db.query.discordReactionRoles.findMany({
    where: eq(discordReactionRoles.messageId, makeSnowflake(message.id)),
  });

  if (entries.length === 0) {
    await ctx.reply({
      content: "This message has no reaction roles registered.",
      ephemeral: true,
    });
    return;
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

  const { roles, emojis } = await ctx.client.api.guilds.get(guildId);

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

  const db = ctx.client.getDb();
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

  ctx.client.KV.delete(`discord-reaction-role-${messageId}-${reaction}`).catch(
    () => {},
  );
  if (deleted) {
    ctx.client.api.channels
      .deleteOwnMessageReaction(
        String(deleted.channelId),
        messageId,
        isSnowflakeSafe(reaction) ? `_:${reaction}` : reaction,
      )
      .catch(() => {});
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

  await ctx.updateMessage({ components });
};

export const listReactionRolesHandler: ChatInputAppCommandCallback = async (
  ctx,
) => {
  const guildId = ctx.interaction.guild_id;
  if (!guildId) throw Error("Guild-only command");

  const message = await resolveMessageLink(
    ctx.client,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    await ctx.reply({
      content: message,
      ephemeral: true,
    });
    return;
  }

  const db = ctx.client.getDb();
  const entries = await db.query.discordReactionRoles.findMany({
    where: eq(discordReactionRoles.messageId, makeSnowflake(message.id)),
  });

  if (entries.length === 0) {
    await ctx.reply({
      content: "This message has no reaction roles registered.",
      ephemeral: true,
    });
    return;
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

### File: `packages/bot-rw/src/commands/restore.ts`
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
import { type QueryData, shareLinks, upsertDiscordUser } from "store";
import { type Client, parseApplicationsValue } from "../client.js";
import type {
  AutoComponentCustomId,
  SelectMenuCallback,
} from "../components.js";
import { isComponentsV2, parseAutoComponentId } from "../util/components.js";
import { isDiscordError } from "../util/error.js";
import { isThread } from "../util/guards.js";
import { boolEmoji, color } from "../util/meta.js";
import { base64UrlEncode, randomString } from "../util/text.js";
import { getUserTag } from "../util/user.js";
import { resolveMessageLink } from "./components/entry.js";
import type {
  ChatInputAppCommandCallback,
  MessageAppCommandCallback,
} from "./handler.js";
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

const generateUniqueShortenKey = async (
  client: Client,
  length: number,
  tries = 10,
): Promise<string> => {
  for (const _ of Array(tries)) {
    const shareId = randomString(length);
    const exists = await client.getShareLinkExists(shareId);
    if (!exists) {
      return shareId;
    }
  }
  return await generateUniqueShortenKey(client, length + 1);
};

export const createLongDiscohookUrl = (data: QueryData, origin?: string) =>
  `${origin ?? Bun.env.DISCOHOOK_ORIGIN}/?${new URLSearchParams({
    data: base64UrlEncode(JSON.stringify(data)),
  })}`;

const createShareLink = async (
  client: Client,
  data: QueryData,
  options?: {
    /** Expiration from now in milliseconds */
    ttl?: number;
    userId?: bigint;
    origin?: string;
  },
) => {
  const { userId } = options ?? {};
  const origin = options?.origin ?? Bun.env.DISCOHOOK_ORIGIN;
  const ttl = options?.ttl ?? 604800000;
  const expires = new Date(new Date().getTime() + ttl);

  delete data.backup_id;
  const shareId = await generateUniqueShortenKey(client, 8);
  await client.putShareLink(
    shareId,
    { data, origin: options?.origin },
    expires,
  );
  if (userId) {
    const db = client.getDb();
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
      Object.keys(parseApplicationsValue()).includes(message.application_id))
  ) {
    return true;
  }
  return false;
};

export const restoreMessageEntry: MessageAppCommandCallback = async (ctx) => {
  const user = await upsertDiscordUser(ctx.client.getDb(), ctx.user);
  const message = ctx.getMessage();

  if (!isMessageWebhookEditable(message)) {
    const data = messageToQueryData(message);
    const share = await createShareLink(ctx.client, data, { userId: user.id });
    await ctx.reply({
      embeds: [getShareEmbed(share, true)],
      components: [],
      ephemeral: true,
    });
    return;
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

  await ctx.reply({
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
      webhook = await getWebhook(ctx.client, webhookId);
    } catch (e) {
      if (isDiscordError(e)) webhookErrorMsg = e.rawError.message;
      webhook = null;
    }
    if (webhook?.token) {
      message = await ctx.client.api.webhooks.getMessage(
        webhook.id,
        webhook.token,
        messageId,
        { thread_id: threadId },
      );
    }
  }
  if (!message) {
    message = await ctx.client.api.channels.getMessage(
      ctx.interaction.channel.id,
      messageId,
    );
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
      const share = await createShareLink(ctx.client, data, {
        userId: BigInt(userId),
      });
      await ctx.updateMessage({
        embeds: [getShareEmbed(share, true)],
        components: [],
      });
      return;
    }
    case "edit": {
      if (webhook === null) {
        await ctx.updateMessage({
          content: `It looks like this webhook was deleted (ID ${webhookId}), so the message cannot be edited${
            webhookErrorMsg ? ` (${webhookErrorMsg})` : ""
          }.`,
          components: [],
        });
        return;
      }
      if (!webhook) {
        await ctx.updateMessage({
          content: "This is not a webhook message.",
          components: [],
        });
        return;
      }
      if (!webhook.token) {
        await ctx.updateMessage({
          content: [
            `Webhook token (ID ${webhookId}) was not available. `,
            "It may be an incompatible type of webhook, or it may have been ",
            "created by a different bot user.",
          ].join(""),
          components: [],
        });
        return;
      }

      let channel: APIGuildChannel<GuildChannelType> | undefined;
      if (message.channel_id !== webhook.channel_id) {
        if (message.channel_id !== ctx.interaction.channel.id) {
          try {
            channel = (await ctx.client.api.channels.get(
              message.channel_id,
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
            await ctx.client.api.webhooks.edit(
              webhook.id,
              { channel_id: channel.id },
              {
                reason: `User ${getUserTag(ctx.user)} (${
                  ctx.user.id
                }) restored ${messageId} to edit it, but the webhook had to be moved.`.slice(
                  0,
                  512,
                ),
              },
            );
          } catch {}
        }
      }

      const data = messageToQueryData(message);
      data.messages[0]!.thread_id = threadId;
      data.messages[0]!.reference = ctx.interaction.guild_id
        ? messageLink(message.channel_id, message.id, ctx.interaction.guild_id)
        : messageLink(message.channel_id, message.id);

      data.targets = [
        {
          url: `${RouteBases.api}${Routes.webhook(webhook.id, webhook.token)}`,
        },
      ];
      const share = await createShareLink(ctx.client, data, {
        userId: BigInt(userId),
      });
      await ctx.updateMessage({
        embeds: [getShareEmbed(share, false)],
        components: [],
      });
      return;
    }
    case "link": {
      // const url = new URL(ctx.env.DISCOHOOK_ORIGIN);
      break;
    }
    default:
      break;
  }
  await ctx.reply({
    content: "This shouldn't happen!",
    ephemeral: true,
  });
  return;
};

export const restoreMessageChatInputCallback: ChatInputAppCommandCallback<
  true
> = async (ctx) => {
  const message = await resolveMessageLink(
    ctx.client,
    ctx.getStringOption("message").value,
    ctx.interaction.guild_id,
  );
  if (typeof message === "string") {
    await ctx.reply({ content: message, flags: MessageFlags.Ephemeral });
    return;
  }
  const mode = (ctx.getStringOption("mode").value || "none") as
    | "none"
    | "edit"
    | "link";

  const user = await upsertDiscordUser(ctx.client.getDb(), ctx.user);
  // if (!userIsPremium(user) && mode === "link") {}
  if (
    mode === "edit" &&
    !ctx.userPermissons.has(PermissionFlags.ManageWebhooks)
  ) {
    await ctx.reply({
      content:
        "You must have the manage webhooks permission to restore a message in edit mode.",
      ephemeral: true,
    });
    return;
  }

  const data = messageToQueryData(message);

  if (!message.webhook_id || message.interaction_metadata) {
    const share = await createShareLink(ctx.client, data, { userId: user.id });
    await ctx.reply({
      embeds: [getShareEmbed(share, true)],
      ephemeral: true,
    });
    return;
  }

  switch (mode) {
    case "none": {
      const data = messageToQueryData(message);
      // url.searchParams.set("data", base64UrlEncode(JSON.stringify(data)))
      const share = await createShareLink(ctx.client, data, {
        userId: BigInt(user.id),
      });
      await ctx.reply({
        embeds: [getShareEmbed(share, true)],
        ephemeral: true,
      });
      return;
    }
    case "edit": {
      if (!message.webhook_id) {
        await ctx.reply({
          content: "This is not a webhook message.",
          ephemeral: true,
        });
        return;
      }

      const webhook = await getWebhook(
        ctx.client,
        message.webhook_id,
        message.application_id,
      );
      if (!webhook.token) {
        await ctx.reply({
          content: dedent`
            Webhook token (ID ${message.webhook_id}) was not available.
            It may be an incompatible type of webhook, or it may have been
            created by a different bot user.
          `,
          ephemeral: true,
        });
        return;
      }

      let channel: APIGuildChannel<GuildChannelType> | undefined;
      let threadId: string | undefined;
      if (message.channel_id !== webhook.channel_id) {
        if (message.channel_id !== ctx.interaction.channel.id) {
          try {
            channel = (await ctx.client.api.channels.get(
              message.channel_id,
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
            await ctx.client.api.webhooks.edit(
              webhook.id,
              { channel_id: channel.id },
              {
                reason:
                  `User ${getUserTag(ctx.user)} (${ctx.user.id}) restored ${
                    message.id
                  } to edit it, but the webhook had to be moved.`.slice(0, 512),
              },
            );
          } catch {}
        }
      }

      data.messages[0]!.thread_id = threadId;
      data.messages[0]!.reference = ctx.interaction.guild_id
        ? messageLink(message.channel_id, message.id, ctx.interaction.guild_id)
        : messageLink(message.channel_id, message.id);
      data.targets = [
        {
          url: `${RouteBases.api}${Routes.webhook(webhook.id, webhook.token)}`,
        },
      ];
      const share = await createShareLink(ctx.client, data, {
        userId: user.id,
      });
      await ctx.reply({
        embeds: [getShareEmbed(share, false)],
        ephemeral: true,
      });
      return;
    }
    case "link": {
      // const url = new URL(ctx.env.DISCOHOOK_ORIGIN);
      break;
    }
    default:
      break;
  }

  await ctx.reply({
    content: "This shouldn't happen",
    ephemeral: true,
  });
};

```

### File: `packages/bot-rw/src/commands/triggers.ts`
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
  type DraftFlow,
  FlowActionType,
  makeSnowflake,
  TriggerEvent,
  triggers,
  upsertDiscordUser,
} from "store";
import type { Client } from "../client.js";
import type { ButtonCallback } from "../components.js";
import { emojiToString } from "../emojis.js";
import { gatewayEventNameToCallback } from "../events.js";
import { getWelcomerConfigurations } from "../events/guildMemberAdd.js";
import type { FlowResult } from "../flows/flows.js";
import type { InteractionContext } from "../interactions.js";
import { parseAutoComponentId } from "../util/components.js";
import { color } from "../util/meta.js";
import { spaceEnum } from "../util/regex.js";
import type {
  AppCommandAutocompleteCallback,
  ChatInputAppCommandCallback,
} from "./handler.js";

export const addTriggerCallback: ChatInputAppCommandCallback = async (ctx) => {
  const name = ctx.getStringOption("name").value;
  const event = ctx.getIntegerOption("event").value as TriggerEvent;

  await ctx.defer({ ephemeral: true });

  // biome-ignore lint/style/noNonNullAssertion: Guild only command
  const guild = await ctx.client.getchTriggerGuild(ctx.interaction.guild_id!);

  if ([TriggerEvent.MemberAdd, TriggerEvent.MemberRemove].includes(event)) {
    const configs = await getWelcomerConfigurations(
      ctx.client,
      event === TriggerEvent.MemberAdd ? "add" : "remove",
      guild,
    );
    if (configs.length !== 0) {
      await ctx.followup.editOriginalMessage({
        content: ctx.t("triggerDuplicate"),
      });
      return;
    }
  }

  const db = ctx.client.getDb();
  const user = await upsertDiscordUser(db, ctx.user);
  await db.insert(triggers).values({
    platform: "discord",
    event,
    discordGuildId: makeSnowflake(guild.id),
    disabled: true,
    flow: { actions: [] },
    flowId: null,
    updatedById: user.id,
  });

  await ctx.followup.editOriginalMessage({
    content: ctx.t("triggerCreated", { replace: { name } }),
    components: [
      new ActionRowBuilder<ButtonBuilder>().addComponents(
        new ButtonBuilder()
          .setStyle(ButtonStyle.Link)
          .setLabel(ctx.t("addActions"))
          .setURL(`${Bun.env.DISCOHOOK_ORIGIN}/s/${guild.id}?t=triggers`),
      ),
    ],
  });
};

export const getFlowEmbed = (
  ctx: InteractionContext,
  flow: DraftFlow | null,
): EmbedBuilder =>
  new EmbedBuilder()
    .setTitle(flow?.name ?? ctx.t("unnamedTrigger"))
    .setColor(color)
    .setDescription(
      !flow?.actions?.length
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

  // biome-ignore lint/style/noNonNullAssertion: Guild only command
  const guild = await ctx.client.getchTriggerGuild(ctx.interaction.guild_id!);

  // I don't like this because it causes several DB calls
  // but we need to migrate them anyway to make them into
  // triggers
  const welcomerTriggers = [
    ...(await getWelcomerConfigurations(ctx.client, "add", guild)),
    ...(await getWelcomerConfigurations(ctx.client, "remove", guild)),
  ];

  const trigger = welcomerTriggers.find((t) =>
    name.startsWith("_id:")
      ? t.id === BigInt(name.replace(/^_id:/, ""))
      : t.flow?.name === name,
  );
  if (!trigger) {
    await ctx.reply({
      content: ctx.t("noTrigger"),
      ephemeral: true,
    });
    return;
  }

  return ctx.reply({
    embeds: [getFlowEmbed(ctx, trigger.flow)],
    components: [
      new ActionRowBuilder<ButtonBuilder>().addComponents(
        new ButtonBuilder()
          .setStyle(ButtonStyle.Link)
          .setLabel(ctx.t("manageActions"))
          .setURL(
            `${Bun.env.DISCOHOOK_ORIGIN}/s/${ctx.interaction.guild_id}?t=triggers`,
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
    const db = ctx.client.getDb();
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
    await ctx.updateMessage({
      content: "You don't have the Manage Guild permission.",
      embeds: [],
      components: [],
    });
    return;
  }
  const parsed = parseAutoComponentId(ctx.interaction.data.custom_id, "event");
  const event = Number(parsed.event) as TriggerEvent;

  const guildId = ctx.interaction.guild_id;
  if (!guildId) throw Error("Guild-only");

  const db = ctx.client.getDb();
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
    await ctx.updateMessage({
      content: `There are no triggers in this server with the event ${TriggerEvent[event]}.`,
      embeds: [],
      components: [],
    });
    return;
  }

  await db.delete(triggers).where(inArray(triggers.id, triggerIds));

  await ctx.updateMessage({
    content: `Deleted ${triggerIds.length} trigger${
      triggerIds.length === 1 ? "" : "s"
    } successfully.`,
    embeds: [],
    components: [],
  });
};

export const triggersDeleteCancel: ButtonCallback = async (ctx) => {
  await ctx.updateMessage({
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

interface EventExecutionResult {
  event: GatewayDispatchEvents;
  name?: string;
  status: "success" | "failure" | "timeout";
  message?: string;
}

export const triggerTestButtonCallback: ButtonCallback = async (ctx) => {
  const guildId = ctx.interaction.guild_id;
  if (!guildId) throw Error("Guild-only");

  const parsed = parseAutoComponentId(ctx.interaction.data.custom_id, "event");
  const event = Number(parsed.event) as TriggerEvent;
  const eventName = triggerEventToDispatchEvent[event];

  if (!ctx.userPermissons.has(PermissionFlags.ManageGuild)) {
    await ctx.reply({
      content:
        "You must have the Manage Server permission to send test events.",
      ephemeral: true,
    });
    return;
  }

  let payload: any = {};
  const func = gatewayEventNameToCallback[eventName] as (
    client: Client,
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
      await ctx.reply({
        content: "No dispatch data could be formed for the event",
        ephemeral: true,
      });
      return;
  }
  if (!func) {
    await ctx.reply({
      content: `There was no function for the event \`${eventName}\``,
      ephemeral: true,
    });
    return;
  }

  // TODO: application emojis
  const emojis = await getEmojis(ctx.env);
  const trueEmoji = emojiToString(emojis.get("true", true));
  const falseEmoji = emojiToString(emojis.get("false", true));

  await ctx.defer({ thinking: true, ephemeral: true });

  const started = new Date().getTime();
  const results = await Promise.race([
    (async (): Promise<EventExecutionResult[]> => {
      try {
        const flowResults = <FlowResult[] | undefined>(
          await func(ctx.client, payload, true)
        );
        if (flowResults) {
          return flowResults.map((result) => ({
            event: eventName,
            status: result.status,
            message:
              result.message +
              (result.discordError
                ? `\nDiscord error: ${result.discordError.message}${
                    result.discordError.errors
                      ? ` | ${result.discordError.errors}`
                      : ""
                  }`
                : ""),
          }));
        }
        return [];
      } catch (e) {
        return [
          {
            event: eventName,
            status: "failure",
            message: `Function failed to complete: ${e}`,
          },
        ];
      }
    })(),
    promiseTimeout<EventExecutionResult[]>(840_000, [
      {
        event: eventName,
        status: "timeout",
        message: "Timeout after 14m",
      },
    ]),
  ]);
  const ended = new Date().getTime();
  await ctx.followup.editOriginalMessage({
    embeds: [
      new EmbedBuilder()
        .setTitle("Results")
        .setColor(color)
        .setDescription(
          results
            .map(
              (r) =>
                `${results.length === 1 ? "" : "- "}${
                  r.status === "success" ? trueEmoji : falseEmoji
                } ${r.message ?? "no message"}`,
            )
            .join("\n")
            .slice(0, 4096),
        )
        .setFields(
          {
            name: "Diagnostic",
            value: `${results.length} result${
              results.length === 1 ? "" : "s"
            } in ${Math.ceil(ended - started)}ms`,
            inline: true,
          },
          {
            name: "Management",
            value:
              "View all actions in this trigger with </triggers view:1281305550340096033>",
            inline: true,
          },
        ),
    ],
  });
};

// https://stackoverflow.com/a/48578424
const promiseTimeout = <T = any>(ms: number, val: T) =>
  new Promise<T>((resolve) => {
    setTimeout(resolve.bind(null, val), ms);
  });

```

### File: `packages/bot-rw/src/commands/webhooks/autocomplete.ts`
```ts
import { WebhookType } from "discord-api-types/v10";
import type { AppCommandAutocompleteCallback } from "../handler.js";

export const webhookAutocomplete: AppCommandAutocompleteCallback = async (
  ctx,
) => {
  // biome-ignore lint/style/noNonNullAssertion: only guild-only commands use this function
  const guildId = ctx.interaction.guild_id!;
  const query = ctx.getStringOption("webhook").value.trim();
  const channel = ctx.getAutocompleteChannelOption("filter-channel");

  const cached = ctx.client.guildWebhooks.get(guildId);
  if (cached) {
    const matches = cached
      .filter(
        (w) =>
          (channel ? w.channel.id === channel.id : true) &&
          w.name &&
          w.name.toLowerCase().includes(query.toLowerCase()),
      )
      .sort((a, b) => {
        const alphabeticalScore = (a.name ?? "") > (b.name ?? "") ? -1 : 1;
        const posScore = a.channel.position - b.channel.position;
        return (
          posScore + (a.channel.id === b.channel.id ? alphabeticalScore : 0)
        );
      });
    return matches.map((w) => {
      const channelHead = channel ? "" : `#${w.channel.name ?? "unknown"}: `;
      const userTail = w.user
        ? ` | ${w.user.global_name ?? w.user.username}`
        : "";
      return {
        name: `${channelHead}${w.name}${userTail}`.slice(0, 100),
        value: w.id,
      };
    });
  }

  const [guildWebhooks, channels] = await Promise.all([
    ctx.client.api.guilds.getWebhooks(guildId),
    (async () => {
      if (channel) return [];
      try {
        return await ctx.client.api.guilds.getChannels(guildId);
      } catch {
        return [];
      }
    })(),
  ]);
  ctx.client.guildWebhooks.set(
    guildId,
    guildWebhooks
      .filter((w) => w.type === WebhookType.Incoming)
      .map((webhook) => {
        const channel = channels.find((c) => c.id === webhook.channel_id);
        return {
          id: webhook.id,
          name: webhook.name,
          user: webhook.user
            ? {
                username: webhook.user.username,
                global_name: webhook.user.global_name,
              }
            : undefined,
          channel: channel
            ? {
                id: channel.id,
                name: channel.name ?? "unknown",
                position: "position" in channel ? channel.position : 0,
              }
            : {
                id: webhook.channel_id,
                name: "unknown",
                position: 0,
              },
        };
      }),
  );

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
        const aPos = "position" in channelA ? channelA.position : 0;
        const bPos = "position" in channelB ? channelB.position : 0;
        return (
          aPos - bPos + (a.channel_id === b.channel_id ? alphabeticalScore : 0)
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

### File: `packages/bot-rw/src/commands/webhooks/webhookCreate.ts`
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
} from "discord-api-types/v10";
import { and, eq } from "drizzle-orm";
import { makeSnowflake, upsertDiscordUser, upsertGuild, webhooks } from "store";
import { getErrorEmbed } from "../../errors.js";
import type { APIPartialResolvedChannel } from "../../types/api.js";
import { readAttachment } from "../../util/cdn.js";
import { isDiscordError } from "../../util/error.js";
import { color } from "../../util/meta.js";
import type { ChatInputAppCommandCallback } from "../handler.js";
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
    await ctx.reply({
      content: `Invalid channel type.${
        !channel ? " To specify a channel, use the `channel` argument." : ""
      }`,
      ephemeral: true,
    });
    return;
  }

  // Attachment handling takes a long time
  await ctx.defer({ ephemeral: true });

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
          "Invalid attachment type. Must be a PNG, JPG, GIF, or WebP image.",
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
    webhook = await ctx.client.api.channels.createWebhook(channelId, {
      name,
      avatar: avatarData,
    });
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
        embeds: [getErrorEmbed(e.rawError)],
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
    channelType ?? ctx.interaction.channel.type,
    showUrl,
  );

  const row = new ActionRowBuilder<ButtonBuilder>().addComponents(
    new ButtonBuilder()
      .setStyle(ButtonStyle.Link)
      .setLabel("Use in Discohook")
      .setURL(
        `${Bun.env.DISCOHOOK_ORIGIN}/?data=${Buffer.from(
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

  const db = ctx.client.getDb();
  const guild = await ctx.client.getchGuild(ctx.interaction.guild_id);
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

  // Check if the webhook is deleted by a bot
  await Bun.sleep(2000);

  try {
    await ctx.client.api.webhooks.get(webhook.id, { token: webhook.token });
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
          and(eq(webhooks.id, webhook.id), eq(webhooks.platform, "discord")),
        );
    }
  }
};

```

### File: `packages/bot-rw/src/commands/webhooks/webhookDelete.ts`
```ts
import { ActionRowBuilder, ButtonBuilder } from "@discordjs/builders";
import { ButtonStyle } from "discord-api-types/v10";
import { PermissionFlags } from "discord-bitflag";
import { and, count, eq } from "drizzle-orm";
import { messageLogEntries, webhooks } from "store";
import type {
  AutoComponentCustomId,
  ButtonCallback,
} from "../../components.js";
import { parseAutoComponentId } from "../../util/components.js";
import { getUserTag } from "../../util/user.js";
import type { ChatInputAppCommandCallback } from "../handler.js";
import { getWebhookInfoEmbed } from "./webhookInfo.js";

export const webhookDeleteEntryCallback: ChatInputAppCommandCallback = async (
  ctx,
) => {
  const webhookId = ctx.getStringOption("webhook").value;
  const webhook = await ctx.client.api.webhooks.get(webhookId);
  const embed = getWebhookInfoEmbed(webhook);

  // Originally delegated this to a followup but it sometimes happened so
  // quickly that it completed before Discord had downloaded the initial
  // response. This will definitely change in production, but I think it
  // should be fine to keep in the response.
  const db = ctx.client.getDb();
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

  await ctx.reply({
    content:
      "Are you sure you want to delete this webhook? This will make it impossible to edit any messages it has sent.",
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
    await ctx.updateMessage({
      content: "You don't have permissions to manage webhooks.",
      embeds: [],
      components: [],
    });
    return;
  }
  const { webhookId } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "webhookId",
  );
  const webhook = await ctx.client.api.webhooks.get(webhookId);
  if (!webhook.guild_id || webhook.guild_id !== ctx.interaction.guild_id) {
    await ctx.updateMessage({
      content: "Webhook does not exist or it is not in this server.",
      embeds: [],
      components: [],
    });
    return;
  }

  // Not sure if it's faster to use the webhook token but we would rather
  // have the bot attribution and audit log reason
  await ctx.client.api.webhooks.delete(webhookId, {
    reason:
      `User ${getUserTag(ctx.user)} (${ctx.user.id}) used /webhook delete`.slice(
        0,
        512,
      ),
  });

  const db = ctx.client.getDb();
  await db
    .delete(webhooks)
    .where(and(eq(webhooks.platform, "discord"), eq(webhooks.id, webhookId)));

  await ctx.updateMessage({
    content: "Deleted the webhook successfully.",
    embeds: [],
    components: [],
  });
};

export const webhookDeleteCancel: ButtonCallback = async (ctx) => {
  await ctx.updateMessage({
    content: "The webhook is safe and sound.",
    embeds: [],
    components: [],
  });
};

```

### File: `packages/bot-rw/src/commands/webhooks/webhookInfo.ts`
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
import { webhooks } from "store";
import { type Client, parseApplicationsValue } from "../../client.js";
import type { ButtonCallback } from "../../components.js";
import type { InteractionContext } from "../../interactions.js";
import { webhookAvatarUrl } from "../../util/cdn.js";
import { parseAutoComponentId } from "../../util/components.js";
import { color } from "../../util/meta.js";
import type { ChatInputAppCommandCallback } from "../handler.js";
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
    webhook.application_id &&
      Bun.env.DISCORD_APPLICATION_ID === webhook.application_id
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
  client: Client,
  webhookId: string,
  webhookApplicationId?: string,
  // This is for when we are trying to resolve a full webhook from partial
  // server webhooks cache and already have the token; we can save some time
  // this way
  token?: string,
): Promise<APIWebhook> => {
  const APPLICATIONS = parseApplicationsValue();

  let tryAppId = webhookApplicationId;
  let botToken = webhookApplicationId
    ? APPLICATIONS[webhookApplicationId]
    : Bun.env.DISCORD_TOKEN;
  if (!botToken) {
    tryAppId = Bun.env.DISCORD_APPLICATION_ID;
    botToken = Bun.env.DISCORD_TOKEN;
  }
  const cached = client.webhooks.get(webhookId);
  // Only return cached result if we already have the token
  // or wouldn't be able to retrieve it
  if (
    cached &&
    (token ||
      cached.token ||
      cached.type !== WebhookType.Incoming ||
      (cached.application_id && !APPLICATIONS[cached.application_id]))
  ) {
    if (token && !cached.token) {
      // not likely to happen
      cached.token = token;
    }
    return cached;
  }

  const rest =
    botToken === Bun.env.DISCORD_TOKEN
      ? client.rest
      : new REST().setToken(botToken);
  const webhook = (await rest.get(
    Routes.webhook(webhookId, token),
  )) as APIWebhook;
  if (webhook.token || webhook.type !== WebhookType.Incoming) {
    // Non-incoming webhooks don't have tokens
    client.webhooks.set(webhookId, webhook);
    return webhook;
  }

  if (webhook.application_id && tryAppId !== webhook.application_id) {
    // env check ensures we don't enter infinite recursion
    if (APPLICATIONS[webhook.application_id]) {
      // we know `token` doesn't need to be passed again because if it was
      // valid then we would already have the webhook, and if it was invalid
      // then we would have errored out.
      return await getWebhook(client, webhook.id, webhook.application_id);
    }
    client.webhooks.set(webhookId, webhook);
    return webhook;
  }

  throw Error("Could not retrieve the webhook.");
};

export const webhookInfoCallback: ChatInputAppCommandCallback = async (ctx) => {
  const webhookId = ctx.getStringOption("webhook").value;
  const showUrl = ctx.getBooleanOption("show-url")?.value ?? false;
  const webhook = showUrl
    ? // if we're going to need the URL right away, bother with the possible extra fetch
      await getWebhook(ctx.client, webhookId)
    : await ctx.client.api.webhooks.get(webhookId);

  const tokenAccessible = webhook.application_id
    ? !!parseApplicationsValue()[webhook.application_id]
    : webhook.type === WebhookType.Incoming;

  const embeds = [getWebhookInfoEmbed(webhook)];
  if (showUrl) {
    embeds.push(
      getWebhookUrlEmbed(
        webhook,
        undefined,
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
    embeds[0]?.setFooter({
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

  await ctx.reply({
    embeds,
    components,
    ephemeral: showUrl,
  });
};

const processUseWebhookButtonBoilerplate = async (
  ctx: InteractionContext<APIMessageComponentButtonInteraction>,
) => {
  if (!ctx.userPermissons.has(PermissionFlags.ManageWebhooks)) {
    await ctx.reply({
      content: "You need the manage webhooks permission.",
      ephemeral: true,
    });
    return;
  }
  const guildId = ctx.interaction.guild_id;
  if (!guildId) {
    await ctx.reply({
      content: "This is a guild-only operation.",
      ephemeral: true,
    });
    return;
  }

  const { webhookId } = parseAutoComponentId(
    ctx.interaction.data.custom_id,
    "webhookId",
  );

  const db = ctx.client.getDb();
  const dbWebhook = await db.query.webhooks.findFirst({
    where: and(eq(webhooks.platform, "discord"), eq(webhooks.id, webhookId)),
    columns: { token: true },
  });

  const webhook = await getWebhook(ctx.client, webhookId);
  if (!webhook.guild_id || webhook.guild_id !== guildId) {
    await ctx.reply({
      content: "This webhook belongs to a different server.",
      ephemeral: true,
    });
    return;
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
      await ctx.reply({
        content: "The webhook's token is not available.",
        ephemeral: true,
      });
      return;
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
  if (!webhook) return;

  const url = createLongDiscohookUrl({
    version: "d2",
    messages: [{ data: {} }],
    targets: [{ url: getWebhookUrl(webhook) }],
  });

  await ctx.reply({
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
  if (!webhook) return;

  const embed = getWebhookUrlEmbed(
    webhook,
    undefined,
    // TODO: always provide channel type
    ctx.interaction.channel.id === webhook.channel_id
      ? ctx.interaction.channel.type
      : undefined,
    true,
  );
  await ctx.reply({
    embeds: [embed],
    ephemeral: true,
  });
};

```

### File: `packages/bot-rw/src/commands/webhooks/webhookInfoMsg.ts`
```ts
import { ActionRowBuilder, ButtonBuilder } from "@discordjs/builders";
import { ButtonStyle, WebhookType } from "discord-api-types/v10";
import { PermissionFlags } from "discord-bitflag";
import { parseApplicationsValue } from "../../client.js";
import type { MessageAppCommandCallback } from "../handler.js";
import { createLongDiscohookUrl } from "../restore.js";
import { getWebhookInfoEmbed, getWebhookUrl } from "./webhookInfo.js";

export const webhookInfoMsgCallback: MessageAppCommandCallback = async (
  ctx,
) => {
  const msg = ctx.getMessage();
  if (!msg.webhook_id) {
    await ctx.reply({
      content: "This is not a webhook message.",
      ephemeral: true,
    });
    return;
  }

  const webhook = await ctx.client.api.webhooks.get(msg.webhook_id);
  const tokenAccessible = webhook.application_id
    ? !!parseApplicationsValue()[webhook.application_id]
    : webhook.type === WebhookType.Incoming;

  const url = webhook.token
    ? createLongDiscohookUrl({
        version: "d2",
        messages: [{ data: {} }],
        targets: [{ url: getWebhookUrl(webhook) }],
      })
    : Bun.env.DISCOHOOK_ORIGIN;

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

  await ctx.reply({
    embeds: [getWebhookInfoEmbed(webhook)],
    components,
    ephemeral: true,
  });
};

```

