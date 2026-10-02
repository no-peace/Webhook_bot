# Repository Context Group: pkg_bot-rw_core
# Source Repository: discohook/discohook

### File: `packages/bot-rw/.gitignore`
```gitignore
.env
config.json
node_modules/
status/
```

### File: `packages/bot-rw/README.md`
```md
# discohook/bot

This is the source code for the Discohook Utils application. This repository replaces the former `bot`, `bot-ws`, and `bouncer` sub-projects, which relied on Cloudflare Workers. Unfortunately, that platform's capabilities and pricing model are unfeasible for Discohook.

## Running

Before running any code, do the following, in no particular order:

- Install [Bun](https://bun.sh) (at least version 1.2.18).
- Set up your [.env](#env-example) and [config.json](#configjson) files.
- Create a `status` directory. This is where each cluster will automatically push information about its shards' statuses. These files are read by [bot-uptime](/packages/bot-uptime) (TODO) and relayed simplistically to our [statuspage](https://github.com/discohook/statuspage).

Run `bun deploy` to register commands. Then run `bun start --cluster=x` to start the bot, where `x` is the zero-indexed number of the cluster. For example, if you have 4 clusters configured, you will need to run `bun start` four concurrent times with `--cluster=0` through `--cluster=3`.

Swap out `bun start` for `bun dev` in the above commands to use an [auto-restarting](https://bun.sh/docs/runtime/hot#watch-mode) development server instead.

#### .env example

```
DISCORD_APPLICATION_ID = "12345"
DISCORD_TOKEN = "abc123"
DISCOHOOK_ORIGIN = "https://discohook.app"
TOKEN_SECRET = "ghi789"
DATABASE_URL = "postgresql://..."
APPLICATIONS_RAW = {"67890":"def456"}
REDIS_URL = "redis://..."
GUILD_ID = "123"
DEV_GUILD_ID = "123"
DEV_OWNER_ID = "456"
```

#### config.json

Most of this file is populated automatically by the `config` script (`bun config:shards`), which you must run before starting the bot. However, also take care to provide a `clusters` value according to your needs. You will need to start several processes in accordance with the number of clusters you set here; if you set 4 clusters, for example, each process will only handle 25% of the shards.

Since Discohook Utils is sufficiently large to require "large bot sharding", we leave shard calculation up to Discord, which will automatically return a `shards` value that is a multiple of 16. However, if this is not desirable for you, you can instead call `bun config:shardless` to only populate the `url` value of this file, and you can write in `shards` yourself.

```json
{
  "url": "wss://gateway.discord.gg",
  "shards": 304,
  "clusters": 4
}
```

```

### File: `packages/bot-rw/package.json`
```json
{
  "$schema": "https://json.schemastore.org/package.json",
  "name": "bot",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "send-help": "bun scripts/send-help.ts",
    "config:shards": "bun scripts/config.ts",
    "config:shardless": "bun scripts/config.ts --shardless",
    "getshard": "bun scripts/getshard.ts",
    "build": "tsc",
    "check": "biome check .",
    "format": "biome format . --write",
    "deploy": "bun src/deploy.ts",
    "dev": "ENVIRONMENT=development bun --watch src/bot.ts",
    "start": "bun src/bot.ts"
  },
  "dependencies": {
    "@discordjs/builders": "^1.13.0",
    "@discordjs/core": "^2.3.0",
    "@discordjs/rest": "^2.6.0",
    "@discordjs/ws": "^2.0.3",
    "@isaacs/ttlcache": "^1.4.1",
    "@sapphire/bitfield": "^1.2.4",
    "argparse": "^2.0.1",
    "discord-api-types": "^0.38.32",
    "dotenv": "^16.3.1",
    "drizzle-orm": "^0.45.1",
    "json-bigint": "^1.0.0",
    "keyv": "^5.0.1",
    "postgres": "^3.4.4",
    "zod": "^4.1.5"
  },
  "devDependencies": {
    "@biomejs/biome": "^1.8.3",
    "@sapphire/ts-config": "^5.0.0",
    "@types/argparse": "^2.0.17",
    "@types/bun": "^1.2.21",
    "@types/json-bigint": "^1.0.4",
    "@types/node": "^18.18.8",
    "tsx": "^4.20.3",
    "typescript": "^5.2.2"
  }
}

```

### File: `packages/bot-rw/scripts/config.ts`
```ts
import { REST } from "@discordjs/rest";
import {
  type RESTGetAPIGatewayBotResult,
  type RESTGetAPIGatewayResult,
  Routes,
} from "discord-api-types/v10";

const shardless = process.argv.includes("--shardless");
const config = Bun.file("./config.json");
const rest = new REST();

if (shardless) {
  const data = (await rest.get(Routes.gateway(), {
    auth: false,
  })) as RESTGetAPIGatewayResult;
  console.log({ shardless, url: data.url });

  await config.write({
    ...(await config.json()),
    ...data,
  });
} else {
  rest.setToken(Bun.env.DISCORD_TOKEN);
  const data = (await rest.get(
    Routes.gatewayBot(),
  )) as RESTGetAPIGatewayBotResult;
  console.log({ shardless, url: data.url, shards: data.shards });

  await config.write({
    ...(await config.json()),
    ...data,
  });
}

```

### File: `packages/bot-rw/scripts/getshard.ts`
```ts
const guildId = process.argv[2];
if (!guildId) {
  throw Error("guild ID is a positional argument that is missing.");
}

const config = (await Bun.file("./config.json").json()) as {
  shards: number;
  clusters: number;
};

const shardId = Number((BigInt(guildId) >> 22n) % BigInt(config.shards));

const SHARDS_PER_CLUSTER = Math.floor(config.shards / config.clusters);

let clusterId = -1;
for (let cluster = 0; cluster < config.clusters; cluster += 1) {
  const shardIds = Array(config.shards)
    .fill(
      0,
      cluster * SHARDS_PER_CLUSTER,
      // BUG: the very last shard is not accounted for. this doesn't matter
      // that much because this is just for display but it's good to keep in
      // mind in case we copy this code somewhere that it does matter.
      Math.min((cluster + 1) * SHARDS_PER_CLUSTER, config.shards),
    )
    .filter((val) => val === 0)
    .map((_, i) => i + cluster * SHARDS_PER_CLUSTER);

  // console.log({
  //   cluster,
  //   shardsFrom: shardIds[0],
  //   shardsTo: shardIds.slice(-1)[0],
  // });
  if (shardIds.includes(shardId)) {
    clusterId = cluster;
  }
}

// start: cluster * SHARDS_PER_CLUSTER,
// end: Math.min((cluster + 1) * SHARDS_PER_CLUSTER, SHARD_COUNT) - 1,

console.log(`\
Guild ID: ${guildId}
Shard ID: ${shardId} (${shardId + 1}/${config.shards})
Cluster ID: ${clusterId}
Shards per cluster: ${SHARDS_PER_CLUSTER}`);

```

### File: `packages/bot-rw/scripts/register.ts`
```ts
import {
  ContextMenuCommandBuilder,
  SlashCommandBuilder,
  SlashCommandChannelOption,
  type SlashCommandOptionsOnlyBuilder,
  SlashCommandStringOption,
  SlashCommandSubcommandBuilder,
  type SlashCommandSubcommandsOnlyBuilder,
  type ToAPIApplicationCommandOptions,
} from "@discordjs/builders";
import {
  type APIApplicationCommandOptionChoice,
  ApplicationCommandOptionType,
  ApplicationCommandType,
  ChannelType,
  InteractionContextType,
  type Locale,
  type LocalizationMap,
  type RESTPutAPIApplicationGuildCommandsJSONBody,
  RouteBases,
  Routes,
} from "discord-api-types/v10";
import { PermissionFlags } from "discord-bitflag";
import { TriggerEvent } from "store";

const webhookChannelTypes = [
  ChannelType.GuildAnnouncement,
  ChannelType.GuildText,
  ChannelType.GuildVoice,
  ChannelType.GuildForum,
  ChannelType.GuildMedia,
  ChannelType.PublicThread,
  ChannelType.PrivateThread,
  ChannelType.AnnouncementThread,
] as const;

const messageChannelTypes = [
  ChannelType.GuildAnnouncement,
  ChannelType.GuildText,
  ChannelType.GuildVoice,
  ChannelType.PublicThread,
  ChannelType.PrivateThread,
  ChannelType.AnnouncementThread,
] as const;

const token = Bun.env.DISCORD_TOKEN;
const applicationId = Bun.env.DISCORD_APPLICATION_ID;

if (!token) {
  throw new Error("The DISCORD_TOKEN environment variable is required.");
}
if (!applicationId) {
  throw new Error(
    "The DISCORD_APPLICATION_ID environment variable is required.",
  );
}

const url = RouteBases.api + Routes.applicationCommands(applicationId);

const loadLocalization = async (lang: string) =>
  JSON.parse(await Bun.file(`./src/i18n/${lang}.json`).json()).commands ?? {};

const localizeProp = (
  languages: Partial<Record<Locale, any>>,
  key: string,
  maxLength?: number,
) => {
  const drill = key.split(".");
  return Object.fromEntries(
    Object.keys(languages)
      .map((lang) => {
        let final: string | Record<string, any> | undefined;
        for (const drillKey of drill) {
          if (final) {
            if (typeof final !== "string") {
              final = final[drillKey];
            }
            if (typeof final === "string") {
              return [lang, final.slice(0, maxLength)];
            }
          } else {
            final = languages[lang as Locale]?.[drillKey];
            if (!final) {
              return [lang, undefined];
            }
          }
        }

        return [lang, undefined];
      })
      .filter((pair) => Boolean(pair[1])),
  ) as LocalizationMap;
};

const main = async () => {
  const languages = {
    nl: await loadLocalization("nl"),
    fr: await loadLocalization("fr"),
    it: await loadLocalization("it"),
    // "zh-CN": await loadLocalization("zh-CN"),
  };
  const english = { "en-US": await loadLocalization("en") };

  const localize = (key: string) => {
    const ized = localizeProp(languages, key);
    if (Object.keys(ized).length === 0) return null;
    return ized;
  };
  const getEnglish = (key: string) =>
    localizeProp(english, key)["en-US"] ?? "...";

  const addLocalizations = (
    command:
      | SlashCommandBuilder
      | SlashCommandSubcommandsOnlyBuilder
      | SlashCommandOptionsOnlyBuilder
      | Omit<SlashCommandBuilder, "addSubcommandGroup" | "addSubcommand">,
  ) => {
    const n = command.name;
    command.setDescription(getEnglish(`${n}.description`));
    command.setNameLocalizations(localize(`${n}.name`));
    command.setDescriptionLocalizations(localize(`${n}.description`));
    const doOpts = <
      T extends ReturnType<ToAPIApplicationCommandOptions["toJSON"]>[],
    >(
      opts: T,
      path: string,
      splice: (index: number, newOpt: T[number]) => void,
    ) => {
      let i = -1;
      for (const option of opts) {
        i += 1;
        option.description = getEnglish(
          `${path}.options.${option.name}.description`,
        );
        option.name_localizations = {
          ...localize(`${path}.options.${option.name}.name`),
          ...option.name_localizations,
        };
        option.description_localizations = {
          ...localize(`${path}.options.${option.name}.description`),
          ...option.description_localizations,
        };
        if ("options" in option && option.options) {
          doOpts(
            option.options,
            `${path}.options.${option.name}`,
            (ind, opt) => {
              // @ts-expect-error
              option.options?.splice(ind, 1, opt);
            },
          );
        }

        splice(i, option);
      }
    };
    // They don't give you the full builders /shrug
    doOpts(
      command.options.map((o) => o.toJSON()),
      n,
      (index, option) => {
        command.options.splice(index, 1, {
          toJSON: () => option,
        });
      },
    );
    return command;
  };

  const webhookAutocompleteOption = new SlashCommandStringOption()
    .setName("webhook")
    .setDescription(getEnglish("_options.webhook.description"))
    .setNameLocalizations(localize("_options.webhook.name"))
    .setDescriptionLocalizations(localize("_options.webhook.description"))
    .setRequired(true)
    .setAutocomplete(true);

  const webhookFilterAutocompleteOption = new SlashCommandChannelOption()
    .setName("filter-channel")
    .setDescription(getEnglish("_options.filter-channel.description"))
    .setNameLocalizations(localize("_options.filter-channel.name"))
    .setDescriptionLocalizations(
      localize("_options.filter-channel.description"),
    )
    .setRequired(false)
    .addChannelTypes(...webhookChannelTypes);

  const welcomerEventChoices: APIApplicationCommandOptionChoice<number>[] = [
    {
      name: getEnglish("welcomer.options.set.options.event.choices.0"),
      name_localizations: localize(
        "welcomer.options.set.options.event.choices.0",
      ),
      value: TriggerEvent.MemberAdd,
    },
    {
      name: getEnglish("welcomer.options.set.options.event.choices.1"),
      name_localizations: localize(
        "welcomer.options.set.options.event.choices.1",
      ),
      value: TriggerEvent.MemberRemove,
    },
  ];

  const allAppCommands = [
    addLocalizations(
      new SlashCommandBuilder()
        .setName("buttons")
        .setDescription("...")
        .setContexts(InteractionContextType.Guild)
        .setDefaultMemberPermissions(
          PermissionFlags.ManageMessages | PermissionFlags.ManageWebhooks,
        )
        .addSubcommand((opt) =>
          opt
            .setName("add")
            .setDescription("...")
            .addStringOption((opt) =>
              opt
                .setName("message")
                .setDescription("...")
                .setRequired(true)
                .setAutocomplete(true),
            )
            .addChannelOption((opt) =>
              opt
                .setName("channel")
                .setDescription("...")
                .setRequired(false)
                .addChannelTypes(...webhookChannelTypes),
            ),
        )
        .addSubcommand((opt) =>
          opt
            .setName("edit")
            .setDescription("...")
            .addStringOption((opt) =>
              opt
                .setName("message")
                .setDescription("...")
                .setRequired(true)
                .setAutocomplete(true),
            )
            .addChannelOption((opt) =>
              opt
                .setName("channel")
                .setDescription("...")
                .setRequired(false)
                .addChannelTypes(...webhookChannelTypes),
            ),
        )
        .addSubcommand((opt) =>
          opt
            .setName("delete")
            .setDescription("...")
            .addStringOption((opt) =>
              opt
                .setName("message")
                .setDescription("...")
                .setRequired(true)
                .setAutocomplete(true),
            )
            .addChannelOption((opt) =>
              opt
                .setName("channel")
                .setDescription("...")
                .setRequired(false)
                .addChannelTypes(...webhookChannelTypes),
            ),
        )
        .addSubcommand((opt) =>
          opt
            .setName("migrate")
            .setDescription("...")
            .addStringOption((opt) =>
              opt
                .setName("message")
                .setDescription("...")
                .setRequired(true)
                .setAutocomplete(true),
            )
            .addChannelOption((opt) =>
              opt
                .setName("channel")
                .setDescription("...")
                .setRequired(false)
                .addChannelTypes(...webhookChannelTypes),
            ),
        ),
    ),
    addLocalizations(
      new SlashCommandBuilder()
        .setName("deluxe")
        .setDescription("...")
        .setContexts(
          InteractionContextType.Guild,
          InteractionContextType.BotDM,
          InteractionContextType.PrivateChannel,
        )
        .addSubcommand((c) => c.setName("info").setDescription("..."))
        .addSubcommand((c) => c.setName("sync").setDescription("...")),
    ),
    addLocalizations(
      new SlashCommandBuilder()
        .setName("format")
        .setDescription("...")
        .setContexts(
          InteractionContextType.Guild,
          InteractionContextType.BotDM,
          InteractionContextType.PrivateChannel,
        )
        .addSubcommand((opt) =>
          opt
            .setName("mention")
            .setDescription("...")
            .addMentionableOption((opt) =>
              opt.setName("target").setDescription("...").setRequired(true),
            ),
        )
        .addSubcommand((opt) =>
          opt
            .setName("channel")
            .setDescription("...")
            .addChannelOption((opt) =>
              opt
                .setName("target")
                .setDescription("...")
                .setRequired(true)
                .addChannelTypes(
                  ChannelType.AnnouncementThread,
                  ChannelType.GuildAnnouncement,
                  ChannelType.GuildForum,
                  ChannelType.GuildMedia,
                  ChannelType.GuildStageVoice,
                  ChannelType.GuildText,
                  ChannelType.GuildVoice,
                  ChannelType.PrivateThread,
                  ChannelType.PublicThread,
                ),
            ),
        )
        .addSubcommand((opt) =>
          opt
            .setName("emoji")
            .setDescription("...")
            .addStringOption((opt) =>
              opt.setName("target").setDescription("...").setRequired(true),
            ),
        ),
    ),
    addLocalizations(
      new SlashCommandBuilder()
        .setName("id")
        .setDescription("...")
        .setContexts(
          InteractionContextType.Guild,
          InteractionContextType.BotDM,
          InteractionContextType.PrivateChannel,
        )
        .addSubcommand((opt) =>
          opt
            .setName("mention")
            .setDescription("...")
            .addMentionableOption((opt) =>
              opt.setName("target").setDescription("...").setRequired(true),
            ),
        )
        .addSubcommand((opt) =>
          opt
            .setName("channel")
            .setDescription("...")
            .addChannelOption((opt) =>
              opt.setName("target").setDescription("...").setRequired(true),
            ),
        )
        .addSubcommand((opt) =>
          opt
            .setName("emoji")
            .setDescription("...")
            .addStringOption((opt) =>
              opt.setName("target").setDescription("...").setRequired(true),
            ),
        ),
    ),
    addLocalizations(
      new SlashCommandBuilder()
        .setName("invite")
        .setDescription("...")
        .setContexts(
          InteractionContextType.Guild,
          InteractionContextType.BotDM,
          InteractionContextType.PrivateChannel,
        ),
    ),
    addLocalizations(
      new SlashCommandBuilder()
        .setName("triggers")
        .setDescription("...")
        .setContexts(InteractionContextType.Guild)
        .setDefaultMemberPermissions(PermissionFlags.ManageGuild)
        .addSubcommand((opt) =>
          opt
            .setName("add")
            .setDescription("...")
            .addStringOption((opt) =>
              opt
                .setName("name")
                .setDescription("...")
                .setMaxLength(100)
                .setRequired(true),
            )
            .addIntegerOption((opt) =>
              opt
                .setName("event")
                .setDescription("...")
                .setChoices(
                  {
                    name: getEnglish(
                      "triggers.options.add.options.event.choices.0",
                    ),
                    name_localizations: localize(
                      "triggers.options.add.options.event.choices.0",
                    ),
                    value: TriggerEvent.MemberAdd,
                  },
                  {
                    name: getEnglish(
                      "triggers.options.add.options.event.choices.1",
                    ),
                    name_localizations: localize(
                      "triggers.options.add.options.event.choices.1",
                    ),
                    value: TriggerEvent.MemberRemove,
                  },
                )
                .setRequired(true),
            ),
        )
        .addSubcommand(
          new SlashCommandSubcommandBuilder()
            .setName("view")
            .setDescription("...")
            .addStringOption((opt) =>
              opt
                .setName("name")
                .setDescription("...")
                .setMaxLength(100)
                .setRequired(true)
                .setAutocomplete(true),
            ),
        ),
    ),
    addLocalizations(
      new SlashCommandBuilder()
        .setName("webhook")
        .setDescription("...")
        .setContexts(InteractionContextType.Guild)
        .setDefaultMemberPermissions(PermissionFlags.ManageWebhooks)
        .addSubcommand((opt) =>
          opt
            .setName("create")
            .setDescription("...")
            .addStringOption((opt) =>
              opt
                .setName("name")
                .setDescription("...")
                .setRequired(true)
                .setMaxLength(80),
            )
            .addAttachmentOption((opt) =>
              opt.setName("avatar").setDescription("..."),
            )
            .addChannelOption((opt) =>
              opt
                .setName("channel")
                .setDescription("...")
                .addChannelTypes(...webhookChannelTypes),
            )
            .addBooleanOption((opt) =>
              opt.setName("show-url").setDescription("..."),
            ),
        )
        .addSubcommand((opt) =>
          opt
            .setName("delete")
            .setDescription("...")
            .addStringOption(webhookAutocompleteOption)
            .addChannelOption(webhookFilterAutocompleteOption),
        )
        .addSubcommand((opt) =>
          opt
            .setName("info")
            .setDescription("...")
            .addStringOption(webhookAutocompleteOption)
            .addChannelOption(webhookFilterAutocompleteOption)
            .addBooleanOption((opt) =>
              opt.setName("show-url").setDescription("..."),
            ),
        ),
    ),
    addLocalizations(
      new SlashCommandBuilder()
        .setName("welcomer")
        .setContexts(InteractionContextType.Guild)
        .setDefaultMemberPermissions(PermissionFlags.ManageGuild)
        .setDescription("...")
        .addSubcommand((o) =>
          o
            .setName("set")
            .setDescription("...")
            .addIntegerOption((o) =>
              o
                .setName("event")
                .setDescription("...")
                .addChoices(welcomerEventChoices)
                .setRequired(true),
            )
            .addChannelOption((o) =>
              o
                .setName("channel")
                .setDescription("...")
                .addChannelTypes(...messageChannelTypes),
            )
            .addStringOption((o) =>
              o.setName("webhook").setDescription("...").setAutocomplete(true),
            )
            .addStringOption((o) =>
              o
                .setName("share-link")
                .setDescription("...")
                .setMinLength(30)
                .setMaxLength(40),
            )
            .addIntegerOption((o) =>
              o
                .setName("delete-after")
                .setDescription("...")
                .setMinValue(0)
                .setMaxValue(60),
            ),
        )
        .addSubcommand((o) =>
          o
            .setName("view")
            .setDescription("...")
            .addIntegerOption((o) =>
              o
                .setName("event")
                .setDescription("...")
                .addChoices(welcomerEventChoices)
                .setRequired(true),
            ),
        )
        .addSubcommand((o) =>
          o
            .setName("delete")
            .setDescription("...")
            .addIntegerOption((o) =>
              o
                .setName("event")
                .setDescription("...")
                .addChoices(welcomerEventChoices)
                .setRequired(true),
            ),
        ),
    ),
    addLocalizations(
      new SlashCommandBuilder()
        .setName("profile")
        .setContexts(InteractionContextType.Guild)
        .setDefaultMemberPermissions(PermissionFlags.ManageNicknames)
        .setDescription("...")
        .addSubcommand(
          (o) =>
            o
              .setName("set")
              .setDescription("...")
              .addStringOption((o) =>
                o.setName("name").setDescription("...").setMaxLength(32),
              )
              .addAttachmentOption((o) =>
                o.setName("avatar").setDescription("..."),
              )
              .addAttachmentOption((o) =>
                o.setName("banner").setDescription("..."),
              ),
          // Not sure about an interface for this yet
          // .addStringOption((o) => o.setName("bio").setDescription("...")),
        )
        .addSubcommand((o) =>
          o
            .setName("clear")
            .setDescription("...")
            .addStringOption((o) =>
              o
                .setName("value")
                .setDescription("...")
                .addChoices([
                  {
                    name: getEnglish("profile.options.set.options.name.name"),
                    name_localizations: localize(
                      "profile.options.set.options.name.name",
                    ),
                    value: "name",
                  },
                  {
                    name: getEnglish("profile.options.set.options.avatar.name"),
                    name_localizations: localize(
                      "profile.options.set.options.avatar.name",
                    ),
                    value: "avatar",
                  },
                  {
                    name: getEnglish("profile.options.set.options.banner.name"),
                    name_localizations: localize(
                      "profile.options.set.options.banner.name",
                    ),
                    value: "banner",
                  },
                ]),
            ),
        ),
    ),
    addLocalizations(
      new SlashCommandBuilder()
        .setName("help")
        .setContexts(
          InteractionContextType.Guild,
          InteractionContextType.BotDM,
          InteractionContextType.PrivateChannel,
        )
        .setDescription("...")
        .addStringOption((opt) =>
          opt
            .setName("tag")
            .setDescription("...")
            .setAutocomplete(true)
            .setRequired(true),
        )
        .addUserOption((opt) =>
          opt.setName("mention").setDescription("...").setRequired(false),
        ),
    ),
    addLocalizations(
      new SlashCommandBuilder()
        .setName("reaction-role")
        .setDescription("...")
        .setDefaultMemberPermissions(
          PermissionFlags.ManageRoles | PermissionFlags.AddReactions,
        )
        .setContexts(InteractionContextType.Guild)
        .addSubcommand((opt) =>
          opt
            .setName("create")
            .setDescription("...")
            .addStringOption((opt) =>
              opt
                .setName("message")
                .setDescription("...")
                .setRequired(true)
                .setAutocomplete(true),
            )
            .addStringOption((opt) =>
              opt
                .setName("emoji")
                .setDescription("...")
                .setRequired(true)
                .setAutocomplete(true),
            )
            .addRoleOption((opt) =>
              opt.setName("role").setRequired(true).setDescription("..."),
            )
            .addChannelOption((opt) =>
              opt
                .setName("channel")
                .setDescription("...")
                .addChannelTypes(...messageChannelTypes),
            ),
        )
        .addSubcommand((opt) =>
          opt
            .setName("delete")
            .setDescription("...")
            .addStringOption((opt) =>
              opt
                .setName("message")
                .setDescription("...")
                .setRequired(true)
                .setAutocomplete(true),
            )
            .addStringOption((opt) =>
              opt.setName("emoji").setDescription("...").setAutocomplete(true),
            )
            .addChannelOption((opt) =>
              opt
                .setName("channel")
                .setDescription("...")
                .addChannelTypes(...messageChannelTypes),
            ),
        )
        .addSubcommand((opt) =>
          opt
            .setName("list")
            .setDescription("...")
            .addStringOption((opt) =>
              opt
                .setName("message")
                .setDescription("...")
                .setRequired(true)
                .setAutocomplete(true),
            )
            .addChannelOption((opt) =>
              opt
                .setName("channel")
                .setDescription("...")
                .addChannelTypes(...messageChannelTypes),
            ),
        ),
    ),
    addLocalizations(
      new SlashCommandBuilder()
        .setName("restore")
        .setDescription("...")
        .setDefaultMemberPermissions(PermissionFlags.ViewChannel)
        .setContexts(InteractionContextType.Guild)
        .addStringOption((opt) =>
          opt
            .setName("message")
            .setDescription("...")
            .setRequired(true)
            .setAutocomplete(true),
        )
        .addStringOption((opt) =>
          opt
            .setName("mode")
            .setDescription("...")
            .setRequired(false)
            .setChoices(
              {
                name: getEnglish("restore.options.mode.choices.edit"),
                name_localizations: localize(
                  "restore.options.mode.choices.edit",
                ),
                value: "edit",
              },
              // {
              //   name: getEnglish("restore.options.mode.choices.link"),
              //   name_localizations: localize(
              //     "restore.options.mode.choices.link",
              //   ),
              //   value: "link",
              // },
            ),
        ),
    ),
    new ContextMenuCommandBuilder()
      .setType(ApplicationCommandType.Message)
      .setName(getEnglish("_ctx.components.name"))
      .setNameLocalizations(localize("_ctx.components.name"))
      .setContexts(InteractionContextType.Guild)
      .setDefaultMemberPermissions(
        PermissionFlags.ManageMessages | PermissionFlags.ManageWebhooks,
      ),
    // new ContextMenuCommandBuilder()
    //   .setType(ApplicationCommandType.Message)
    //   .setName(getEnglish("_ctx.edit.name"))
    //   .setNameLocalizations(localize("_ctx.edit.name"))
    //   .setContexts(InteractionContextType.Guild)
    //   .setDefaultMemberPermissions(
    //     PermissionFlags.ManageMessages | PermissionFlags.ManageWebhooks,
    //   ),
    new ContextMenuCommandBuilder()
      .setType(ApplicationCommandType.Message)
      .setName(getEnglish("_ctx.restore.name"))
      .setNameLocalizations(localize("_ctx.restore.name"))
      .setContexts(InteractionContextType.Guild)
      .setDefaultMemberPermissions(PermissionFlags.ViewChannel),
    new ContextMenuCommandBuilder()
      .setType(ApplicationCommandType.Message)
      .setName(getEnglish("_ctx.webhook.name"))
      .setNameLocalizations(localize("_ctx.webhook.name"))
      .setContexts(InteractionContextType.Guild)
      .setDefaultMemberPermissions(PermissionFlags.ViewChannel),
    new ContextMenuCommandBuilder()
      .setType(ApplicationCommandType.Message)
      .setName(getEnglish("_ctx.quickedit.name"))
      .setNameLocalizations(localize("_ctx.quickedit.name"))
      .setContexts(InteractionContextType.Guild)
      .setDefaultMemberPermissions(
        PermissionFlags.ManageMessages | PermissionFlags.ManageWebhooks,
      ),
    // new ContextMenuCommandBuilder()
    //   .setType(ApplicationCommandType.Message)
    //   .setName(getEnglish("_ctx.debug.name"))
    //   .setNameLocalizations(localize("_ctx.debug.name"))
    //   .setContexts(InteractionContextType.Guild)
    //   .setDefaultMemberPermissions(PermissionFlags.ManageMessages),
  ];

  const payload = allAppCommands.map((c) => c.toJSON());
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bot ${token}`,
    },
    method: "PUT",
    body: JSON.stringify(payload),
  });

  if (response.ok) {
    console.log("Registered all commands");
    const data = await response.json();
    console.log(JSON.stringify(data, null, 2));
  } else {
    console.error("Error registering commands");
    let errorText = `Error registering commands \n ${response.url}: ${response.status} ${response.statusText}`;
    try {
      const error = await response.text();
      if (error) {
        errorText = `${errorText} \n\n ${error}`;
      }
    } catch (err) {
      console.error("Error reading body from request:", err);
    }
    console.error(errorText);
  }

  if (process.env.DEV_GUILD_ID) {
    await fetch(
      RouteBases.api +
        Routes.applicationGuildCommands(
          applicationId,
          process.env.DEV_GUILD_ID,
        ),
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bot ${token}`,
        },
        method: "PUT",
        body: JSON.stringify([
          {
            type: ApplicationCommandType.ChatInput,
            name: "leave",
            description: "Leave a guild (dangerous!)",
            options: [
              {
                type: ApplicationCommandOptionType.String,
                name: "guild-id",
                description: "The guild ID to leave",
                required: true,
              },
              {
                type: ApplicationCommandOptionType.String,
                name: "reason",
                description: "The reason for leaving",
                required: true,
              },
              {
                type: ApplicationCommandOptionType.Boolean,
                name: "send-reason-message",
                description: "Whether to send a message to the owner",
              },
              {
                type: ApplicationCommandOptionType.Boolean,
                name: "ban",
                description:
                  "Whether to ban the server so the bot cannot be re-added",
              },
            ],
          },
          {
            type: ApplicationCommandType.ChatInput,
            name: "grant-deluxe",
            description: "Grant a Deluxe subscription to a user",
            options: [
              {
                type: ApplicationCommandOptionType.String,
                name: "user-id",
                description: "The user ID",
                required: true,
              },
              {
                type: ApplicationCommandOptionType.String,
                name: "duration",
                description:
                  "A donation amount ($100) or time (3d, 2w, 3m, 1y)",
                required: true,
              },
            ],
          },
          {
            type: ApplicationCommandType.ChatInput,
            name: "revoke-deluxe",
            description:
              "Revoke a Deluxe subscription, including lifetime status",
            options: [
              {
                type: ApplicationCommandOptionType.String,
                name: "user-id",
                description: "The user ID",
                required: true,
              },
            ],
          },
        ] satisfies RESTPutAPIApplicationGuildCommandsJSONBody),
      },
    );
  }
};

await main();

```

### File: `packages/bot-rw/scripts/send-help.ts`
```ts
import { EmbedBuilder, messageLink } from "@discordjs/builders";
import {
  type APIEmbed,
  type APIMessage,
  type APIPublicThreadChannel,
  type APIWebhook,
  ChannelsAPI,
  RESTJSONErrorCodes,
  WebhooksAPI,
  WebhookType,
} from "@discordjs/core";
import { REST } from "@discordjs/rest";
import { ArgumentParser } from "argparse";
import { fetchTags } from "../src/commands/help";
import { isDiscordError } from "../src/util/error";
import { color } from "../src/util/meta";

const titleOverride: Record<string, string> = {
  buttons: "Add buttons to messages/embeds",
  blocked: "My request to Discord was blocked",
  schedule: "Schedule a message",
};

const argparser = new ArgumentParser();
argparser.add_argument("--thread", {
  help: "help channel forum thread ID",
  required: true,
});

const threadId = argparser.parse_args().thread as string;

const tags = await fetchTags();

const rest = new REST().setToken(Bun.env.DISCORD_TOKEN);

const channels = new ChannelsAPI(rest);
const allMessages = await channels.getMessages(threadId, {
  after: threadId,
  limit: 100,
});
console.log(allMessages.length);
const webhooks = new WebhooksAPI(rest);

const firstWebhookId = allMessages[0]?.webhook_id;
let webhook: APIWebhook | undefined;
if (!firstWebhookId || allMessages.length === 0) {
  const channel = (await channels.get(threadId)) as APIPublicThreadChannel;
  if (!channel.parent_id) {
    throw Error(`Missing parent ID for thread ID ${threadId}`);
  }
  const channelWebhooks = await channels.getWebhooks(channel.parent_id);
  webhook = channelWebhooks.find(
    (w) =>
      w.application_id === Bun.env.DISCORD_APPLICATION_ID ||
      (!w.application_id && w.type === WebhookType.Incoming),
  );
} else {
  webhook = await webhooks.get(firstWebhookId);
}
if (!webhook) {
  throw Error("Could not resolve webhook. Maybe you need to create a new one.");
}
const { token } = webhook;
if (!token) {
  throw Error("Could not resolve webhook token.");
}

// compile extant
const overlap: Record<string, APIMessage> = {};
for (const message of allMessages) {
  if (
    !message.webhook_id ||
    (message.application_id &&
      message.application_id !== Bun.env.DISCORD_APPLICATION_ID) ||
    message.embeds.length === 0
  ) {
    continue;
  }

  const embed = message.embeds[0];
  if (!embed?.footer?.text) continue;

  const id = embed.footer.text.split(",")[0]?.replace(/^#/, "");
  if (id && tags[id]) {
    overlap[id] = message;
  }
}
console.log(overlap);

// send or edit the tag messages
const tagsToId: Record<string, string> = {};
for (const [tag, embed] of Object.entries(tags)) {
  if (typeof embed === "string") continue;

  embed.color = embed.color ?? color;
  const newEmbed = new EmbedBuilder(embed);
  const aliases = Object.entries(tags)
    .filter((t) => t[1] === tag)
    .map((t) => t[0]);
  newEmbed.setFooter({
    text: [tag, ...aliases].map((t) => `#${t}`).join(", "),
  });

  const overlapping = overlap[tag];
  if (overlapping) {
    try {
      const message = await webhooks.editMessage(
        webhook.id,
        token,
        overlapping.id,
        {
          embeds: [newEmbed.toJSON()],
          thread_id: threadId,
        },
      );
      tagsToId[tag] = message.id;
    } catch (e) {
      // this shouldn't happen
      if (isDiscordError(e) && e.code === RESTJSONErrorCodes.UnknownMessage) {
        const message = await webhooks.execute(webhook.id, token, {
          embeds: [newEmbed.toJSON()],
          thread_id: threadId,
          wait: true,
        });
        tagsToId[tag] = message.id;
      } else {
        throw e;
      }
    }
  } else {
    const message = await webhooks.execute(webhook.id, token, {
      embeds: [newEmbed.toJSON()],
      thread_id: threadId,
      wait: true,
    });
    tagsToId[tag] = message.id;
  }
}

// update starter message
const embed = new EmbedBuilder().setColor(color);

const getKeyLinkItem = (key: string) => {
  let title: string;
  if (titleOverride[key]) {
    title = titleOverride[key];
  } else {
    title = (tags[key] as APIEmbed)?.title ?? key;
    if (title.toLowerCase().startsWith("how do i")) {
      title = title
        .replace(/^how do i/i, "")
        .replace(/\?$/, "")
        .trim();
      title = title.slice(0, 1).toUpperCase() + title.slice(1);
    }
    title = title.replace(/\.$/, "");
  }

  const messageId = tagsToId[key];
  if (messageId) {
    return `- [${title}](${messageLink(
      threadId,
      messageId,
      // biome-ignore lint/style/noNonNullAssertion: we're in a guild
      webhook.guild_id!,
    )})\n`;
  }
  return "";
};

embed.setDescription(
  // This one is too long to fit in a field
  `**How-to basics**\n${[
    "send",
    "edit",
    "sidebar",
    "mention",
    "link",
    "buttons",
    "reaction role",
    "schedule",
    "welcomer",
    "profile",
  ]
    .map(getKeyLinkItem)
    .join("")
    .trim()}`,
);

const otherCategories = {
  Troubleshooting: ["blocked", "ise", "nothing", "image"],
};
for (const [category, keys] of Object.entries(otherCategories)) {
  embed.addFields({
    name: category,
    value: keys.map(getKeyLinkItem).join("").trim(),
    inline: false,
  });
}

embed.addFields({
  name: "Something else",
  value:
    "If you can't find your answer here, try using the search feature or creating a new post in <#1234648356307996712>. Keep in mind you may not get your answer immediately, please be patient as we aren't available all day.",
});

await webhooks.editMessage(webhook.id, token, threadId, {
  content:
    "Welcome to Discohook's help channel! This channel contains the answers to many common questions and is able to solve some frequently occurring issues.",
  embeds: [embed.toJSON()],
  thread_id: threadId,
});

```

### File: `packages/bot-rw/tsconfig.json`
```json
{
  "compilerOptions": {
    // Environment setup & latest features
    "lib": ["ESNext"],
    "target": "ESNext",
    "module": "Preserve",
    "moduleDetection": "force",
    "allowJs": true,

    // Bundler mode
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "noEmit": true,

    // Best practices
    "strict": true,
    "skipLibCheck": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,

    // Some stricter flags (disabled by default)
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noPropertyAccessFromIndexSignature": false
  }
}

```

