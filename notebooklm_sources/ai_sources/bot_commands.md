# Repository Context Group: bot_commands
# Source Repository: no-peace/Hoho_manager

### File: `bot/src/commands/ping.ts`
```ts
import { Command } from "@sapphire/framework";
import { commandRegistration } from "../lib/registration.js";

/**
 * `/ping` — the smallest useful Sapphire command.
 *
 * Kept as a reference for the shape of every command in this worker:
 *   - the constructor supplies metadata,
 *   - `registerApplicationCommands` declares the Discord-side schema,
 *   - `chatInputRun` is the handler.
 */
export class PingCommand extends Command {
  public constructor(context: Command.LoaderContext, options: Command.Options) {
    super(context, { ...options, description: "Check that the bot is alive." });
  }

  public override registerApplicationCommands(registry: Command.Registry): void {
    registry.registerChatInputCommand(
      (builder) => builder.setName("ping").setDescription("Check that the bot is alive."),
      commandRegistration,
    );
  }

  public override async chatInputRun(
    interaction: Command.ChatInputCommandInteraction,
  ): Promise<void> {
    const started = Date.now();
    await interaction.reply("Pong!");
    const roundTrip = Date.now() - started;
    const gateway = Math.round(this.container.client.ws.ping);

    await interaction.editReply(`Pong! Round trip **${roundTrip}ms** · gateway **${gateway}ms**`);
  }
}

```

### File: `bot/src/commands/send.ts`
```ts
import { Command } from "@sapphire/framework";
import { ChannelType, MessageFlags } from "discord.js";
import api from "../lib/api.js";
import { commandRegistration } from "../lib/registration.js";

/**
 * `/send` — post a message as the bot, through the builder's own API.
 *
 * Why route through the API instead of calling Discord directly? The API owns the
 * bot token, the payload validation and the audit log. Sending from here would
 * duplicate all three and put a second copy of the token on disk.
 */
export class SendCommand extends Command {
  public constructor(context: Command.LoaderContext, options: Command.Options) {
    super(context, { ...options, description: "Send a message as the bot." });
  }

  public override registerApplicationCommands(registry: Command.Registry): void {
    registry.registerChatInputCommand(
      (builder) =>
        builder
          .setName("send")
          .setDescription("Send a message as the bot.")
          .addChannelOption((option) =>
            option
              .setName("channel")
              .setDescription("Where to post the message.")
              .addChannelTypes(ChannelType.GuildText, ChannelType.GuildAnnouncement)
              .setRequired(true),
          )
          .addStringOption((option) =>
            option
              .setName("message")
              .setDescription("Message content. Markdown is supported.")
              .setMaxLength(2000)
              .setRequired(true),
          ),
      commandRegistration,
    );
  }

  public override async chatInputRun(
    interaction: Command.ChatInputCommandInteraction,
  ): Promise<void> {
    const channel = interaction.options.getChannel("channel", true);
    const message = interaction.options.getString("message", true);

    // Defer first: the API round trip can exceed Discord's 3-second ack window.
    await interaction.deferReply({ flags: MessageFlags.Ephemeral });

    try {
      await api.sendMessage({ content: message, channelId: channel.id });
      await interaction.editReply(`\u2705 Sent to <#${channel.id}>.`);
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error);
      await interaction.editReply(`\u26a0\ufe0f Could not send:\n${reason}`);
    }
  }
}

```

### File: `bot/src/commands/server.ts`
```ts
import { Command } from "@sapphire/framework";
import { MessageFlags } from "discord.js";
import { commandRegistration } from "../lib/registration.js";

/**
 * `/server` — status of the server the command was run in.
 *
 * The gateway is the only place this information exists: it arrives over the
 * WebSocket as guild cache, so the API cannot answer it. Kept ephemeral so a
 * status check does not clutter the channel.
 *
 * `Guilds` is the only intent this needs — `memberCount` is the *approximate*
 * count Discord ships with the guild object, so the privileged `GuildMembers`
 * intent stays switched off.
 */

const BOOST_TIERS = ["None", "Tier 1", "Tier 2", "Tier 3"] as const;

export class ServerCommand extends Command {
  public constructor(context: Command.LoaderContext, options: Command.Options) {
    super(context, { ...options, description: "Show status information about this server." });
  }

  public override registerApplicationCommands(registry: Command.Registry): void {
    registry.registerChatInputCommand(
      (builder) =>
        builder
          .setName("server")
          .setDescription("Show status information about this server."),
      commandRegistration,
    );
  }

  public override async chatInputRun(
    interaction: Command.ChatInputCommandInteraction,
  ): Promise<void> {
    if (!interaction.inCachedGuild()) {
      await interaction.reply({
        content: "\u26a0\ufe0f This command only works inside a server.",
        flags: MessageFlags.Ephemeral,
      });
      return;
    }

    const { guild } = interaction;

    const body = [
      `**${guild.name}**`,
      `\u2022 ID: \`${guild.id}\``,
      `\u2022 Members: ${guild.memberCount}`,
      `\u2022 Channels: ${guild.channels.cache.size}`,
      `\u2022 Roles: ${guild.roles.cache.size}`,
      `\u2022 Boost: ${BOOST_TIERS[guild.premiumTier] ?? "Unknown"}`,
      `\u2022 Owner: <@${guild.ownerId}>`,
      `\u2022 Created: <t:${Math.floor(guild.createdTimestamp / 1000)}:R>`,
      `_Gateway latency: ${Math.round(this.container.client.ws.ping)}ms_`,
    ].join("\n");

    await interaction.reply({ content: body, flags: MessageFlags.Ephemeral });
  }
}

```

### File: `bot/src/commands/status.ts`
```ts
import { Command } from "@sapphire/framework";
import { MessageFlags } from "discord.js";
import api from "../lib/api.js";
import { env } from "../lib/env.js";
import { commandRegistration } from "../lib/registration.js";

/**
 * `/status` — shows whether the API and its Discord integrations are configured.
 *
 * This is the pattern for the worker's real purpose: the webhook/interaction
 * machinery lives in the Express API, and the gateway reads it over HTTP rather
 * than reaching into the database itself.
 */
export class StatusCommand extends Command {
  public constructor(context: Command.LoaderContext, options: Command.Options) {
    super(context, { ...options, description: "Report API and integration health." });
  }

  public override registerApplicationCommands(registry: Command.Registry): void {
    registry.registerChatInputCommand(
      (builder) =>
        builder.setName("status").setDescription("Report API and integration health."),
      commandRegistration,
    );
  }

  public override async chatInputRun(
    interaction: Command.ChatInputCommandInteraction,
  ): Promise<void> {
    await interaction.deferReply({ flags: MessageFlags.Ephemeral });

    try {
      const health = await api.health();

      const line = (label: string, ok: boolean): string =>
        `${ok ? "\u2705" : "\u274c"} ${label}`;

      const body = [
        `**API** \`${env.apiBaseUrl}\` — ${health.status} (${health.environment})`,
        line("Database connected", health.database.connected),
        line("Bot token configured", health.discord.botTokenConfigured),
        line("Public key configured", health.discord.publicKeyConfigured),
        line("Application id configured", health.discord.applicationIdConfigured),
        `_Uptime: ${Math.round(health.uptimeSeconds)}s_`,
      ].join("\n");

      await interaction.editReply(body);
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error);
      await interaction.editReply(`\u26a0\ufe0f ${reason}`);
    }
  }
}

```

