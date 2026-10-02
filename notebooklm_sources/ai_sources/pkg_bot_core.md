# Repository Context Group: pkg_bot_core
# Source Repository: discohook/discohook

### File: `packages/bot/.yarn/install-state.gz`
```gz
// ERROR FETCHING FILE: 'utf-8' codec can't decode byte 0x8b in position 1: invalid start byte
```

### File: `packages/bot/LICENSE`
```text
The MIT License (MIT)

Copyright (c) 2022-present shay (shayypy), Justin Beckwith

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```

### File: `packages/bot/README.md`
```md
# Discohook Bot (formerly Discohook Utils)

## Setup

Due to the complexity of this project, I recommend that you do not do this, *especially* if you have not done something similar before! Instead, invite the instance of the bot that I host. [It's quick and easy!](https://discohook.app/bot)

### Attribution

This repository is based on a fork of [Discord's Cloudflare Workers sample app](https://github.com/discord/cloudflare-sample-app), thank you to the contributors!

### Configuring project

Create a [Discord app](https://discord.com/developers/applications). You will need the application ID, public key, and bot token.

### Creating your Cloudflare worker

Next, you'll need to create a Cloudflare Worker.

- Visit the [Cloudflare dashboard](https://dash.cloudflare.com/)
- Click on the `Workers` tab, and create a new service using the same name as your Discord bot

### Running locally

First clone the project:

```
git clone https://github.com/discohook/discohook.git
```

Then navigate to the bot directory and install all dependencies:

```
cd discohook/packages/bot
yarn install
```

> ⚙️ The dependencies in this project require at least v18 of [Node.js](https://nodejs.org/en/).

#### Local configuration

> 💡 More information about generating and fetching credentials can be found [in the tutorial](https://discord.com/developers/docs/tutorials/hosting-on-cloudflare-workers#storing-secrets)

Rename `example.dev.vars` to `.dev.vars`, and make sure to set each variable.

#### Register commands

The following command only needs to be run once:

```
$ yarn register
```

#### Run app

Now you should be ready to start your server:

```
$ yarn dev
```

### Deploying app

This repository is set up to automatically deploy to Cloudflare Workers when new changes land on the `main` branch. To deploy manually, run `npm run publish`, which uses the `wrangler publish` command under the hood. Publishing via a GitHub Action requires obtaining an [API Token and your Account ID from Cloudflare](https://developers.cloudflare.com/workers/wrangler/cli-wrangler/authentication/#generate-tokens). These are stored [as secrets in the GitHub repository](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository), making them available to GitHub Actions. The following configuration in `.github/workflows/ci.yaml` demonstrates how to tie it all together:

```yaml
release:
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  needs: [test, lint]
  steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: 18
    - run: npm install
    - run: npm run publish
      env:
        CF_API_TOKEN: ${{ secrets.CF_API_TOKEN }}
        CF_ACCOUNT_ID: ${{ secrets.CF_ACCOUNT_ID }}
```

#### Storing secrets

The credentials in `.dev.vars` are only applied locally. The production service needs access to credentials from your app:

```
$ wrangler secret put DISCORD_TOKEN
$ wrangler secret put DISCORD_PUBLIC_KEY
$ wrangler secret put DISCORD_APPLICATION_ID
```

##### Tokens for other bots

If you want the bot to be able to access webhook tokens created by other applications, supply a mapping of application ID to bot token as the `APPLICATIONS_RAW` environment variable. This will be parsed on fetch as `APPLICATIONS`.

```

### File: `packages/bot/package.json`
```json
{
  "name": "discohook-bot",
  "version": "2.0.0",
  "description": "",
  "type": "module",
  "private": true,
  "main": "src/server.ts",
  "scripts": {
    "start": "tsx src/server.ts",
    "dev": "wrangler dev src/server.ts --persist-to=../../persistence",
    "tunnel": "cloudflared tunnel --url http://localhost:8787",
    "register": "tsx src/register.ts",
    "deploy": "wrangler deploy --env=production",
    "deploy-preview": "wrangler deploy --env=preview"
  },
  "keywords": [],
  "license": "MIT",
  "dependencies": {
    "@discordjs/builders": "^1.14.1",
    "@discordjs/formatters": "^0.6.1",
    "@discordjs/rest": "^2.6.0",
    "dedent-js": "^1.0.1",
    "discord-api-types": "^0.38.55",
    "discord-bitflag": "^1.0.3",
    "discord-verify": "^1.2.0",
    "i18next": "^23.11.5",
    "itty-router": "^4.0.13",
    "jose": "^5.4.0",
    "store": "../store",
    "zod": "^4.0.5"
  },
  "devDependencies": {
    "@cloudflare/workers-types": "^4.20240405.0",
    "@tsconfig/node18": "^18.2.2",
    "c8": "^8.0.0",
    "chai": "^4.3.7",
    "dotenv": "^16.0.3",
    "mocha": "^10.2.0",
    "sinon": "^17.0.0",
    "tsx": "^4.7.0",
    "typescript": "^5.3.3",
    "wrangler": "^3.107.3"
  }
}

```

### File: `packages/bot/tsconfig.json`
```json
{
  "extends": "@tsconfig/node18/tsconfig.json",
  "compilerOptions": {
    "lib": ["es2021", "dom"],
    "types": ["@cloudflare/workers-types/2023-03-01"]
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules"]
}

```

### File: `packages/bot/wrangler.toml`
```toml
name = "discohook-bot"
main = "./src/server.ts"
compatibility_date = "2023-05-18"
node_compat = true
# DOES NOT 100% OVERLAP w/ node_compat! TODO switch
# compatibility_flags = ["nodejs_compat"]
services = [{ binding = "SITE", service = "discohook-site" }]

[vars]
ENVIRONMENT = "dev"
PREMIUM_SKUS = ["1249810125418397867"]
LIFETIME_SKU = "1266826214807572542"

[durable_objects]
bindings = [
  { name = "DRAFT_CLEANER", class_name = "DurableDraftComponentCleaner", script_name = "discohook-site" },
  { name = "SHARE_LINKS", class_name = "ShareLinks", script_name = "discohook-site" },
  { name = "EMOJIS", class_name = "EmojiManager" },
  { name = "SESSIONS", class_name = "SessionManager", script_name = "discohook-site" },
]

[[migrations]]
tag = "v1"
new_classes = ["DurableComponentState"]

[[migrations]]
tag = "v2"
new_classes = ["EmojiManager"]

[[migrations]]
tag = "v3"
deleted_classes = ["DurableComponentState"]

[env.preview]
route = { pattern = "bots.preview.discohook.app", custom_domain = true }
hyperdrive = [
  { binding = "HYPERDRIVE", id = "f8f714cc2701467cacf61b203ccd933a" },
]
services = [{ binding = "SITE", service = "discohook-site-preview" }]

[env.preview.durable_objects]
bindings = [
  { name = "DRAFT_CLEANER", class_name = "DurableDraftComponentCleaner", script_name = "discohook-site-preview" },
  { name = "SHARE_LINKS", class_name = "ShareLinks", script_name = "discohook-site-preview" },
  { name = "EMOJIS", class_name = "EmojiManager" },
  { name = "SESSIONS", class_name = "SessionManager", script_name = "discohook-site-preview" },
]

[[env.preview.migrations]]
tag = "v1"
new_classes = ["DurableComponentState"]

[[env.preview.migrations]]
tag = "v2"
new_classes = ["EmojiManager"]

[[env.preview.migrations]]
tag = "v3"
deleted_classes = ["DurableComponentState"]

[env.preview.vars]
ENVIRONMENT = "preview"
DISCORD_APPLICATION_ID = "1259876010627694662"
PREMIUM_SKUS = []
LIFETIME_SKU = ""
DISCOHOOK_ORIGIN = "https://preview.discohook.app"

[env.production]
route = { pattern = "bots.discohook.app", custom_domain = true }
hyperdrive = [
  { binding = "HYPERDRIVE", id = "9568cd870bee47f3801c862de747ca94" },
]
services = [{ binding = "SITE", service = "discohook-site-production" }]

[env.production.placement]
mode = "smart"

[env.production.observability]
enabled = true
head_sampling_rate = 1
logs.invocation_logs = false

[env.production.durable_objects]
bindings = [
  { name = "DRAFT_CLEANER", class_name = "DurableDraftComponentCleaner", script_name = "discohook-site-production" },
  { name = "SHARE_LINKS", class_name = "ShareLinks", script_name = "discohook-site-production" },
  { name = "EMOJIS", class_name = "EmojiManager" },
  { name = "SESSIONS", class_name = "SessionManager", script_name = "discohook-site-production" },
]

[[env.production.migrations]]
tag = "v1"
new_classes = ["DurableComponentState"]

[[env.production.migrations]]
tag = "v2"
new_classes = ["EmojiManager"]

[[env.production.migrations]]
tag = "v3"
deleted_classes = ["DurableComponentState"]

[env.production.vars]
ENVIRONMENT = "production"
DISCORD_APPLICATION_ID = "792842038332358656"
PREMIUM_SKUS = ["1249810125418397867"]
LIFETIME_SKU = "1266826214807572542"
DISCOHOOK_ORIGIN = "https://discohook.app"
GUILD_ID = "668218342779256857"
DONATOR_ROLE_ID = "747100568539103242"
SUBSCRIBER_ROLE_ID = "1251181202518315210"

```

