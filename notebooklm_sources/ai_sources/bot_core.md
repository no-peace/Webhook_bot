# Repository Context Group: bot_core
# Source Repository: no-peace/Hoho_manager

### File: `bot/.env.example`
```example
# ─── Gateway worker ────────────────────────────────────────────────────────
# Copy to bot/.env and fill in. See bot/README.md.
NODE_ENV=development

# Developer Portal → Bot → Token. Same token the API uses.
# NOTE: this token is used to open the gateway connection, so it *is* present in
# this process's environment — which is fine, because this process is the bot.
DISCORD_BOT_TOKEN=

# Origin of the Express API. The worker never touches the database directly.
API_BASE_URL=http://localhost:3001

# Must match ADMIN_API_KEY in server/.env — the worker sends it as x-admin-key
# when it relays an interaction to /api/interactions/relay, so a mismatch means
# the API refuses the forward and the click appears to do nothing.
ADMIN_API_KEY=dev-admin-key

# Optional. When set, slash commands are registered to this guild only, so
# changes appear instantly instead of waiting for global propagation.
# Remove it in production.
DEV_GUILD_ID=

# ─── Discord API compatibility ─────────────────────────────────────────────
# discord.js reads these for REST rate-limit metadata. Harmless to omit.
# DISCORD_APPLICATION_ID=

```

### File: `bot/README.md`
```md
# Gateway worker (Sapphire)

A [Sapphire](https://sapphirejs.dev) Discord bot that connects to the **gateway**, alongside the
web editor and the Express API.

## Why this exists

It has two jobs, and the second one is the reason it is not optional everywhere.

### 1. Slash commands

`/ping`, `/status`, `/server`, `/send` — things only a persistent gateway connection can do, plus
presence and (with the privileged intents enabled) member/reaction events.

### 2. The interaction relay — for hosts with no public address

Discord delivers interactions in exactly one of two ways, decided by the application's
*Interactions Endpoint URL*. **They are mutually exclusive per application:**

| | Endpoint URL set | Endpoint URL empty |
| --- | --- | --- |
| Delivery | Discord POSTs to your `/api/interactions` | `INTERACTION_CREATE` over the gateway |
| Needs a public HTTPS address | **yes** | **no** |
| Who receives it | the Express API | this worker |

A Cloudflare Tunnel gives you a public address — but it needs a `cloudflared` credential *on the
machine running the app*, and in this project's setup that credential exists **only on the laptop**.
On a server (e.g. a Pterodactyl container) there is no tunnel and no public URL, so Discord has
nowhere to POST. That is the case this worker covers: it receives the click over the gateway — an
**outbound** WebSocket, so no port is ever opened — and forwards it to the API on `localhost`.

The API then runs the flow and posts the reply back to Discord using the **interaction token**,
which is itself the credential for `POST /interactions/{id}/{token}/callback`. So the reply path
needs no inbound port either, and the API can answer an interaction it never received over HTTP.

```
Discord ──(INTERACTION_CREATE)──► dmb-gateway (Sapphire)
                                     │  POST /api/interactions/relay  (localhost, x-admin-key)
                                     ▼
                                 dmb-api (Express) ──► SQLite
                                     │  POST /interactions/{id}/{token}/callback
                                     ▼
                                  Discord

Slash commands are dispatched here instead and never relayed.
```

If the API is unreachable the worker answers the user itself, so they get a real error rather than
"This interaction failed".

It deliberately owns **no database credentials**. It calls the same API the web editor uses
(`server/src/routes/*`), which keeps exactly one bot token on disk, one payload validator, and one
SQLite writer.

## Setup

```bash
cp bot/.env.example bot/.env     # from the repo root
```

Fill in:

| Variable | Notes |
| -------- | ----- |
| `DISCORD_BOT_TOKEN` | Same token the API uses |
| `API_BASE_URL` | Origin of the Express API (default `http://localhost:3001`) |
| `ADMIN_API_KEY` | Must match `server/.env` — sent as `x-admin-key` |
| `DEV_GUILD_ID` | Optional. Scopes command registration to one guild so changes appear instantly |
| `NODE_ENV` | `production` in production (warns about the default admin key otherwise) |

Start the API first (`npm run dev` from the repo root), then:

```bash
npm run dev:bot        # tsx watch, from the repo root
# or, inside bot/:
npm run dev
```

## Layout

```
src/
├── index.ts               SapphireClient + login + graceful shutdown
├── lib/
│   ├── env.ts             validated env (mirrors server/src/config/env.ts)
│   ├── api.ts             HTTP client for the Express API
│   └── registration.ts    guild-scoped vs global command registration
├── commands/
│   ├── ping.ts            latency check
│   ├── status.ts          API + integration health
│   ├── server.ts          current guild status (members, channels, roles, boost, owner)
│   └── send.ts            post a message through the builder API
└── listeners/
    ├── ready.ts           logs login state
    └── interactionRelay.ts forwards component/modal interactions to the API
```

Sapphire discovers `commands/` and `listeners/` relative to the entry file. `src/index.ts` sets
`baseUserDirectory` from `import.meta.url`, so the **same code runs unbuilt (`src/`) and built
(`dist/`)** with no build-specific branching — `npm run build` preserves the directory structure.

## Adding a command

```ts
import { Command } from "@sapphire/framework";

export class HelloCommand extends Command {
  public constructor(context: Command.LoaderContext, options: Command.Options) {
    super(context, { ...options, description: "Say hello." });
  }

  public override registerApplicationCommands(registry: Command.Registry): void {
    registry.registerChatInputCommand((builder) =>
      builder.setName("hello").setDescription("Say hello."),
    );
  }

  public override async chatInputRun(interaction: Command.ChatInputCommandInteraction) {
    await interaction.reply("Hello!");
  }
}
```

## Intents

Only `GatewayIntentBits.Guilds` is requested, which is all slash commands need. `GuildMembers` and
`GuildMessageReactions` are **privileged**: enable them in the Developer Portal under *Privileged
Gateway Intents* **before** adding them to `src/index.ts`, or login fails with `Used disallowed
intents`.

## Relay mode checklist

Use this whenever the app has **no public HTTPS address**:

1. Developer Portal → your app → **General Information** → **clear the Interactions Endpoint URL**.
   While it is set, Discord keeps using HTTP and this worker sees no components at all — this is the
   single most common reason the relay looks broken.
2. `ADMIN_API_KEY` in `bot/.env` must match `server/.env`. It is the credential for the relay call.
3. `API_BASE_URL` must point at the API (`http://localhost:3001` when both run on the same host).
4. Start the API **before** the worker — the relay has nothing to talk to otherwise.
5. Invite the bot with the `bot` scope (plus *Manage Roles* if you use role actions).

Verify with `/ping` (handled in-process) and then a real button click; see
[`docs/PTERODACTYL_DEPLOYMENT.md`](../../docs/PTERODACTYL_DEPLOYMENT.md) §6.3 for what each log line
means.

## Deployment

See [`docs/PTERODACTYL_DEPLOYMENT.md`](../../docs/PTERODACTYL_DEPLOYMENT.md) §6 and §8 — including
how to run this under PM2 as `dmb-gateway`.

```

### File: `bot/package.json`
```json
{
  "name": "bot",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "description": "Sapphire gateway worker — slash commands and gateway events, driving the same API the web editor uses.",
  "main": "dist/index.js",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc -p tsconfig.build.json",
    "start": "node dist/index.js",
    "typecheck": "tsc -p tsconfig.json --noEmit"
  },
  "dependencies": {
    "@dmb/shared": "*",
    "@sapphire/framework": "^5.5.1",
    "discord.js": "^14.27.0",
    "dotenv": "^16.4.5"
  },
  "devDependencies": {
    "@types/node": "^24.10.1",
    "tsx": "^4.20.3",
    "typescript": "^5.9.3"
  },
  "engines": {
    "node": ">=20"
  }
}

```

### File: `bot/tsconfig.build.json`
```json
{
  "extends": "./tsconfig.json",
  "//": "Build-only config: identical to tsconfig.json but without test files, so vitest specs never land in dist/.",
  "exclude": ["dist", "node_modules", "src/**/*.test.ts"]
}

```

### File: `bot/tsconfig.json`
```json
{
  "extends": "../tsconfig.base.json",
  "compilerOptions": {
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2023"],
    "types": ["node"],
    "rootDir": "src",
    "outDir": "dist",
    "newLine": "lf"
  },
  "include": ["src/**/*.ts"],
  "exclude": ["dist", "node_modules"]
}

```

