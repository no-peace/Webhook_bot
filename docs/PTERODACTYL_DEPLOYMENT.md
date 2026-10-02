# Deploying on Pterodactyl (no public ports, PM2, Sapphire gateway)

This guide is for the case where the app runs **inside a Pterodactyl container** that gives you one
(or two) network allocations and no way to bind extra public ports.

The trick is to stop thinking in terms of public ports entirely:

- Run the API and the web server on **localhost ports** inside the container.
- Let **PM2** supervise them (auto-restart, logs, boot behaviour).
- Carry button clicks in through the **Discord gateway**, not through HTTP.

> **Why not a Cloudflare Tunnel?** A tunnel is the obvious answer to "no public ports" — but it
> needs a `cloudflared` credential *on the host that serves the app*, and that is not always
> available. In this project's setup the tunnel exists **only on the laptop** used for local
> development. The server has no tunnel, so the app there has **no public HTTPS address at all**.
> §6 covers the way out: the gateway worker relays interactions to the API over localhost, and
> nothing needs to be reachable from the internet. §7 documents the tunnel as the *alternative*,
> for a host that does have one.

Verified against:

- PM2 — [Quick Start](https://pm2.keymetrics.io/docs/usage/quick-start/) and
  [Ecosystem File / application declaration](https://pm2.keymetrics.io/docs/usage/application-declaration/)
- Cloudflare — [Cloudflare Tunnel overview](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/)
  and [Configuration file reference](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/configuration-file/)
- Discord — [Receiving and Responding to Interactions](https://docs.discord.com/developers/interactions/receiving-and-responding)
  and [Interactions Overview](https://docs.discord.com/developers/interactions/overview)
- Sapphire — [Getting started](https://sapphirejs.dev/docs/Guide/getting-started/getting-started-with-sapphire/)

---

## 1. Why the panel's port allocation is not the bottleneck

Pterodactyl allocates ports, then tells your container which ones it may bind. That is a
**container-level** constraint — it does not apply to loopback. `localhost:3001` and
`localhost:5173` inside the container are always available, whether or not the panel allocated
them.

So the app itself runs fine. The only real question is **how a Discord button click gets in**,
which §2 answers.

---

## 2. Two ways in — pick one

Discord delivers interactions in exactly one of two ways, and which one you get is decided by the
application's *Interactions Endpoint URL* in the Developer Portal. **They are mutually exclusive
per application:** the moment an endpoint URL is set, every interaction goes there and the gateway
receives none.

| | **A. HTTP webhook** | **B. Gateway relay** |
| --- | --- | --- |
| Needs a public HTTPS address | **Yes** | **No** |
| Discord posts to | your `/api/interactions` | — |
| Delivery | inbound HTTP request | `INTERACTION_CREATE` over the gateway WebSocket (outbound) |
| Endpoint URL | must be set | must be **cleared** |
| Slash commands (`/ping`) | gateway worker, if run | gateway worker (**required**) |
| Works on this project's server | only with a tunnel | **yes** |
| Config | `DISCORD_PUBLIC_KEY` required | not required for delivery |

**This project's split:**

| Where it runs | Mode | Why |
| --- | --- | --- |
| **Laptop** (`npm run dev`) | A — HTTP webhook | You have the Cloudflare Tunnel here, so Discord can reach `localhost:3001` through it |
| **Pterodactyl server** | B — Gateway relay | No tunnel, so nothing inbound is possible |

Both modes run the **same** flow: `handleInteraction()` in
`server/src/services/interactionHandler.ts` decides *what* to reply, and only the transport
differs. A flow therefore behaves identically in both places.

The 3-second reply budget applies to both: Discord shows "This interaction failed" if the app does
not answer in time, however the interaction arrived.

---

## 3. Layout inside the container

| Piece | Binds to | Needs a public port? |
| ----- | -------- | -------------------- |
| `dmb-api` (Express + flows) | `localhost:3001` | no |
| `dmb-web` (built SPA) | `localhost:5173` | no (see below) |
| `dmb-gateway` (Sapphire bot — **the relay**) | no port; outbound gateway WebSocket | no |

The API and the SPA talk to each other over loopback, so **you can run the whole thing with zero
public ports.** That does mean the web editor is only reachable from inside the container, unless
you also expose `dmb-web` (the portal lets you publish an allocated port, or you can attach a
tunnel as in §7).

If you only care about the bot and its button flows — which is the case when there is no tunnel —
you can run `dmb-api` + `dmb-gateway` alone and skip `dmb-web`:

```bash
pm2 start ecosystem.config.cjs --only dmb-api,dmb-gateway --env production
```

---

## 4. Build and supervise with PM2

```bash
# from the repo root inside the container
npm install
npm run build          # shared -> client -> server -> bot
npm run migrate        # create/upgrade the SQLite database

npm install -g pm2
pm2 start ecosystem.config.cjs --env production
pm2 save               # freeze the process list
pm2 startup            # print the command to re-run PM2 at boot
```

`ecosystem.config.cjs` (already in the repo) defines `dmb-api` and `dmb-web`, with `dmb-gateway`
and `dmb-tunnel` left as commented entries to uncomment once configured. For the tunnel-less
server you uncomment **`dmb-gateway`** and leave `dmb-tunnel` alone.

### The one thing to get right: fork mode, not cluster

PM2's `exec_mode: "cluster"` and `-i max` load-balance a Node app across CPU cores by starting
**several OS processes**. This app stores data in a single SQLite file through `better-sqlite3`,
which is a synchronous, single-process embedded database. Multiple writers on one file is how you
get `SQLITE_BUSY` and eventually a corrupt database.

That is why `dmb-api` is pinned to `instances: 1` / `exec_mode: "fork"`. Move to Postgres
(`docs/DEPLOYMENT.md` §9) before you raise that number.

> Consequence: a restart of `dmb-api` is a (brief) outage. `pm2 reload` gives zero-downtime
> reloading for networked apps, but it works by overlapping *new* workers with old ones — which is
> exactly the multi-writer case above. Use `pm2 restart dmb-api` and accept the few seconds.

`dmb-web` is stateless static files and `dmb-gateway` holds no data, so both are safe to restart
freely.

### Everyday PM2 commands

| Command | What it does |
| ------- | ------------ |
| `pm2 list` | Status of every managed process |
| `pm2 logs dmb-api --lines 200` | Tail logs |
| `pm2 logs dmb-gateway --lines 200` | Tail the bot's logs |
| `pm2 restart dmb-api` | Restart one app |
| `pm2 reload ecosystem.config.cjs` | Reload everything |
| `pm2 monit` | Live terminal dashboard |
| `pm2 save` / `pm2 resurrect` | Persist / restore the process list |

If the panel manages your container's entrypoint, you cannot rely on `pm2 startup` (it installs a
systemd unit, which containers usually do not have). Instead make the panel's **startup command**
launch PM2 in the foreground:

```bash
cd /home/container && npm install -g pm2 >/dev/null 2>&1; pm2 start ecosystem.config.cjs --env production && pm2 logs
```

---

## 5. Configure the app for the container

In the panel's environment variables:

```ini
NODE_ENV=production
PORT=3001

# Only matters if you publish the SPA. Must be scheme + host, no trailing slash.
CLIENT_ORIGIN=http://localhost:5173

# On the volume, so flows and templates survive redeploys.
DATABASE_URL=/home/container/data/prod.sqlite

# The bot token is required for BOTH modes — it is how the API replies to Discord.
DISCORD_BOT_TOKEN=<your bot token>
DISCORD_APPLICATION_ID=<your app's application id>

# Only needed for HTTP webhook mode (§7). Harmless to leave it set.
DISCORD_PUBLIC_KEY=<your app's public key>

ADMIN_API_KEY=<64 random hex chars>
ENCRYPTION_KEY=<64 random hex chars>
```

And in `bot/.env` (copy from `bot/.env.example`):

```ini
NODE_ENV=production
DISCORD_BOT_TOKEN=<same token as above>
API_BASE_URL=http://localhost:3001
ADMIN_API_KEY=<same value as server/.env>
DEV_GUILD_ID=<a server you own, optional but recommended>
```

`ADMIN_API_KEY` **must match** on both sides — it is the credential the worker uses to reach the
relay endpoint.

> **Bind the API to loopback.** In gateway mode nothing outside the container ever calls the API,
> so `localhost:3001` is the correct and safest address. Do not publish that port; if you do, the
> admin key is the only thing standing between the internet and `/api/send`.

---

## 6. Gateway relay mode (the server path)

This is the mode for a host with **no tunnel and no public address**.

### 6.1 How it works

```
Discord ──(INTERACTION_CREATE)──► dmb-gateway (Sapphire)
                                      │
                                      │ POST /api/interactions/relay   (localhost, x-admin-key)
                                      ▼
                                  dmb-api  ── runs the flow ──► SQLite
                                      │
                                      │ POST /interactions/{id}/{token}/callback
                                      ▼
                                   Discord
```

The gateway connection is an **outbound WebSocket** (`wss://gateway.discord.gg`), so it works from
behind any firewall and needs no allocation. When a component is clicked:

1. Discord pushes the interaction down that socket.
2. `bot/src/listeners/interactionRelay.ts` forwards the raw payload to the API over loopback.
3. The API executes the flow (`handleInteraction`) and posts the reply back to Discord using the
   **interaction token**.

Step 3 is the part worth being precise about: the interaction token is itself the credential for
`POST /interactions/{id}/{token}/callback`, so **the API can answer an interaction it never
received over HTTP** — this is the same call `discord.js` makes internally for `interaction.reply()`.
No gateway connection is needed on the API side, and no port needs to be open.

If the API is unreachable, the worker notices (`delivered: false`) and answers the user itself with
a readable error instead of leaving them with "This interaction failed".

### 6.2 Set it up

1. **Clear the Interactions Endpoint URL** in the Developer Portal (app → *General Information*).
   If it is set, Discord keeps delivering over HTTP and the gateway sees nothing — this is the
   single most common reason the relay appears not to work.
2. Make sure the bot is **invited to your server** (OAuth2 → `bot` scope → *Send Messages*, plus
   *Manage Roles* if you use role actions).
3. Fill in `bot/.env` (§5) and start everything under PM2:

   ```bash
   npm run build
   pm2 start ecosystem.config.cjs --only dmb-api,dmb-gateway --env production
   pm2 save
   ```

4. Watch it come up:

   ```bash
   pm2 logs dmb-gateway --lines 50
   # [bot] logged in as YourBot#1234
   # [bot] ready as YourBot#1234 — 1 guild(s)
   ```

5. In Discord, run `/ping` — that command is handled by the worker directly and proves the gateway
   connection is live.

### 6.3 Verify a button actually works

1. Open the editor (locally, over the tunnel, or however you reach `dmb-web`).
2. Build a button, give it a flow on the **Flow** tab, and send it in **bot token** mode. Sending
   in bot mode is what registers the multi-step flow with the API — a webhook-only send cannot
   carry a chain longer than the 100-character `custom_id`.
3. Click the button in Discord.
4. Check the logs:

   ```bash
   pm2 logs dmb-api --lines 30       # the flow ran
   pm2 logs dmb-gateway --lines 30   # the forward succeeded
   ```

| Symptom in the logs | Meaning |
| --- | --- |
| nothing at all in either log | Endpoint URL is still set, so Discord sent the interaction over HTTP instead |
| `interaction relay failed: Can't reach the API…` | `dmb-api` is down, or `API_BASE_URL`/`ADMIN_API_KEY` is wrong |
| `Relay could not deliver a reply for …` | The flow ran but Discord rejected the callback — usually the 3-second window expired (long `wait` steps) |
| `Ignoring unrecognised custom_id from …` | The button's `custom_id` is not `action:…` — re-pick an action on the Flow tab |

### 6.4 What the relay does *not* do

- **Slash commands** (`/ping`, `/status`, `/server`, `/send`) are handled by the worker itself, not
  relayed. They arrive on the same gateway event but are dispatched by Sapphire first.
- **Modals** are relayed only if their `custom_id` uses the `action:` prefix, because that is what
  the API's parser recognises. A modal opened with `customId: "modal:about"` needs to be
  `action:…` to have a flow run on submit.
- **Autocomplete** is not handled.

---

## 7. Alternative: Cloudflare Tunnel mode

Use this **only if the host that runs the app actually has a `cloudflared` credential** — for
example a VPS you control with a Cloudflare account, or a machine where you are happy to
`cloudflared tunnel login`. On the laptop this is already available; on a shared Pterodactyl
container it usually is not.

With a tunnel, switch back to mode A from §2 and follow the steps below instead of §6.

### 7.1 Why it works without a public port

```
Internet ──► Cloudflare edge ──► (outbound tunnel) ──► cloudflared ──► localhost:5173  (SPA)
                                                                   └─► localhost:3001  (/api)
```

`cloudflared` establishes outbound connections from the container to Cloudflare and then carries
traffic back down that same connection in both directions. Because there is no inbound listener on
your origin, you can leave every port closed — and you get HTTPS and DDoS protection for free.

The API and the SPA can share **one hostname** because Cloudflare forwards the full request path
unmodified and every API route already lives under `/api`.

### 7.2 Create the tunnel and its ingress rules

```bash
cloudflared tunnel login
cloudflared tunnel create dmb
cloudflared tunnel route dns dmb builder.example.com

mkdir -p ~/.cloudflared
cp tunnel/config.yml.example ~/.cloudflared/config.yml
```

`tunnel/config.yml.example` in this repo is ready to use — the important part:

```yaml
tunnel: <TUNNEL-UUID>
credentials-file: /home/container/.cloudflared/<TUNNEL-UUID>.json

ingress:
  # API first. A rule without `path` matches every path, so it must come last.
  - hostname: builder.example.com
    path: ^/api
    service: http://localhost:3001
  - hostname: builder.example.com
    service: http://localhost:5173
  # Required catch-all — cloudflared refuses to start without it.
  - service: http_status:404
```

Validate before running — this catches typos and a missing catch-all:

```bash
cloudflared tunnel ingress validate
cloudflared tunnel ingress rule https://builder.example.com/api/health
```

Run it in the foreground, or let PM2 supervise it (uncomment `dmb-tunnel` in
`ecosystem.config.cjs`; note `interpreter: "none"`, because `cloudflared` is a Go binary and PM2
would otherwise try to wrap it in Node):

```bash
cloudflared tunnel run dmb
```

> **Quick tunnels need no config.** For a throwaway `trycloudflare.com` URL, just run
> `cloudflared tunnel --url http://localhost:3001`. Handy for testing, but the URL changes every
> restart — re-save it in the Developer Portal each time.

### 7.3 Point Discord at the tunnel

1. Developer Portal → your application → **General Information** → **Interactions Endpoint URL**:
   ```
   https://builder.example.com/api/interactions
   ```
2. Save. Discord immediately sends a signed `PING`; the server verifies the Ed25519 signature with
   `DISCORD_PUBLIC_KEY` and answers `PONG`. A red banner means the tunnel is down, the public key is
   wrong, or the path is missing `/api/interactions`.
3. Button clicks now arrive over the tunnel. The gateway worker is then **optional** — leave
   `dmb-gateway` stopped unless you also want slash commands.

The SPA is built with `VITE_API_BASE_URL` baked in at **build time**. With path routing on one
hostname, leave it empty so the browser calls `/api` on the same origin:

```bash
VITE_API_BASE_URL= npm run build:client
```

---

## 8. The Sapphire gateway worker

`bot/` is a [Sapphire](https://sapphirejs.dev) worker that connects to the Discord **gateway**. Its
role depends on the mode you chose:

| Mode | What the worker is for |
| --- | --- |
| **B — gateway relay** (server, no tunnel) | **Required.** It is the only way interactions reach the API, and it also serves slash commands |
| **A — HTTP webhook** (laptop, tunnel) | Optional. Slash commands, presence and member/reaction events only |

It deliberately owns **no database credentials**. It calls the API over loopback, which keeps
exactly one bot token on disk, one payload validator and one SQLite writer.

```bash
cp bot/.env.example bot/.env     # DISCORD_BOT_TOKEN, API_BASE_URL, ADMIN_API_KEY, DEV_GUILD_ID
npm run dev:bot                  # tsx watch
npm run start:bot                # node bot/dist/index.js
```

Commands register automatically on login; setting `DEV_GUILD_ID` scopes them to one guild so
changes appear immediately instead of waiting up to an hour for global propagation.

Under PM2, uncomment the `dmb-gateway` entry in `ecosystem.config.cjs` and:

```bash
npm run build:bot
pm2 start ecosystem.config.cjs --only dmb-gateway
```

### Built-in commands

| Command | What it does |
| ------- | ------------ |
| `/ping` | Round-trip and gateway latency — proves the connection is alive |
| `/status` | API health: database, bot token, public key, application id, uptime |
| `/server` | The current server: name, id, member/channel/role counts, boost tier, owner, age |
| `/send` | Post a message through the builder API (exercises the same `/api/send` path the editor uses) |

---

## 9. Operational notes

- **Logs** end up in `~/.pm2/logs/`; `merge_logs` and `time` are already set in the ecosystem file.
  Set `log_file` if you would rather have one file.
- **Memory**: `max_memory_restart: "400M"` restarts a process before the host OOM-kills it. Raise it
  if the panel gives you more RAM.
- **Backups**: the SQLite file lives at `DATABASE_URL`. Back it up by copying the file (and its
  `-wal`/`-shm` siblings) while the API is stopped, or use `sqlite3 .backup`.
- **Tunnel credentials are secrets.** `~/.cloudflared/*.json` and `cert.pem` authorise the tunnel;
  keep them out of git and out of logs.
- **Two tunnels, not one, for zero-downtime config changes.** Cloudflare's docs recommend running a
  new `cloudflared` replica with the updated config, waiting for it to be ready, then stopping the
  old one.
- **Switching modes is a two-sided change.** Set/clear the Developer Portal endpoint URL *and*
  start/stop `dmb-gateway`, or interactions will be delivered to the wrong place.

---

## 10. Troubleshooting

| Symptom | Likely cause |
| ------- | ------------ |
| Buttons do nothing, and both logs are silent | Interactions Endpoint URL is still set, so Discord is posting over HTTP to nowhere — clear it for relay mode (§6.2) |
| Buttons do nothing, `dmb-gateway` logs a relay timeout | `API_BASE_URL` unreachable from the container, or `ADMIN_API_KEY` differs between `server/.env` and `bot/.env` |
| `/ping` doesn't appear in Discord | `DEV_GUILD_ID` unset so commands are registering globally (up to an hour); or the bot was never invited with the `applications.commands` scope |
| Bot logs in then immediately disconnects | A privileged intent (e.g. `GuildMembers`) is requested but not enabled in the Developer Portal |
| `cloudflared tunnel ingress validate` fails | Missing catch-all `- service: http_status:404`, or no rules at all |
| Site loads but `/api/*` 404s | An ingress rule without `path` sits above the `/api` rule and swallows it |
| Frontend loads, every API call fails with CORS | `CLIENT_ORIGIN` ≠ the tunnel hostname (scheme/host/trailing slash must match exactly) |
| `/api/*` hits the SPA instead of the API | The SPA's dev/preview server is answering; check the tunnel `path` regex and service ports |
| Discord cannot save the Interactions Endpoint URL | Tunnel down, wrong `DISCORD_PUBLIC_KEY`, or URL missing `/api/interactions` |
| `SQLITE_BUSY` / database corruption | Something started the API more than once — check `pm2 list` for duplicate `dmb-api` entries and remove `exec_mode: "cluster"` |
| Button click says "This interaction failed" but the flow ran | A `wait` step pushed the reply past Discord's 3-second window — keep waits short or defer before waiting |
| Only the first flow step runs | The message was sent before the flow was registered — re-send in **bot token** mode or from a template |
| PM2 processes gone after a panel restart | `pm2 save` not run, or no `pm2 startup`/startup-command equivalent |
