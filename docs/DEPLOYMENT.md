# Deployment guide

Two guides, two jobs:

- **`docs/LOCAL_DEVELOPMENT.md`** — run and test everything on your own machine.
- **This file** — put it on the internet so you (and a few friends) can use it from anywhere,
  and so Discord can deliver button clicks to a permanent URL.

If you haven't run the project locally yet, do that first — everything below assumes the app
already works on `localhost`.

---

## 1. What you're deploying

The repo builds **two deployable pieces** from one codebase:

| Piece              | Build output                                | What it needs to run                |
| ------------------ | ------------------------------------------- | ----------------------------------- |
| **Frontend (SPA)** | `client/dist/` static files                 | Any static host — no Node needed    |
| **Backend (API)**  | `server/dist/` + `node server/dist/index.js`| A Node 20+ host with a persistent disk |

A third piece, `shared/`, is not deployed — it's compiled into both during `npm run build`.

```
Browser ──► static SPA (Vercel / Cloudflare Pages)
              │
              │  fetch /api/...  (VITE_API_BASE_URL)
              ▼
        Express API (Railway / Render / VPS)
              │                       ▲
              ├── SQLite/Postgres     │
              └── Discord API ◄───────┘── signed interactions from Discord
```

---

## 2. Recommended hosting (and why)

You can host both pieces anywhere; this is the path that works best for this app as built:

| Piece    | Recommendation                        | Why                                                                                     |
| -------- | ------------------------------------- | --------------------------------------------------------------------------------------- |
| Frontend | **Cloudflare Pages** (or Vercel)      | Free static hosting, global CDN, `VITE_*` env vars, builds `client/dist` from a repo     |
| Backend  | **Railway** (or Render)               | Node 20 runtime, persistent **volume** for the SQLite file, public URL, env vars, deploys from git |
| Database | **SQLite file on a persistent volume**| Zero-config start; the repository layer is built for a later Postgres swap if you outgrow it |

> **Why split frontend and backend?** The SPA is static files — hosts like Cloudflare Pages serve
> those far cheaper and faster than a Node server. The backend is the only part that needs a
> long-running process (SQLite file + Discord signature verification).

> **Why not host the SPA on the Express server?** You could (serve `client/dist` from Express),
> and that simplifies CORS to nothing. It's a fine option on a VPS. The split below assumes
> separate hosts, which is the more common setup.

Cheaper-but-more-work alternative: a $4–6/mo **VPS** (Hetzner, DigitalOcean) running Node behind
nginx or Caddy. Same env vars, same build commands, more sysadmin. Pick Railway/Render if you
want "push to deploy".

### 2.1 Or: one host, no public ports (Pterodactyl / restricted containers)

If the host only gives you one or two ports — the normal situation inside a **Pterodactyl**
container — skip the split-host setup entirely. Run the API and the SPA on **loopback** ports and
supervise both with **PM2** (`ecosystem.config.cjs` is in the repo). That part works anywhere; the
only remaining question is how Discord reaches you, and there are two answers (see
[§5.1](#51-how-discord-reaches-your-server)):

- **A public HTTPS address**, if the host has one — a Cloudflare Tunnel is the usual way to get one
  without opening a port, because `cloudflared` dials *outbound*.
- **The gateway relay**, if it does not. The Sapphire worker connects to Discord's gateway
  (outbound WebSocket, also needs no port) and forwards button clicks to the API over loopback. No
  public address exists at all, and none is needed.

Full walkthrough, including PM2, the relay, and the tunnel `ingress` rules:
[`PTERODACTYL_DEPLOYMENT.md`](./PTERODACTYL_DEPLOYMENT.md).

> A tunnel needs a `cloudflared` credential *on the host running the app*. Where that credential is
> not available — the common case on a shared container — the relay is the only option, and it is
> why `bot/` exists as more than a slash-command runner.

> The same PM2 ecosystem file is useful on an ordinary VPS — it gives you crash restarts, log
> rotation targets and boot persistence without writing systemd units by hand.

### 2.2 Create your accounts

You'll need:

- A GitHub repo with this code (Railway/Pages deploy from git).
- <https://railway.app> (or Render) — sign in with GitHub.
- <https://dash.cloudflare.com> (or vercel.com) — for the frontend.

---

## 3. Deploy the backend (Railway)

### 3.1 Create the project

1. Railway → **New Project** → **Deploy from GitHub repo** → pick your repo.
2. Railway auto-detects Node. Open the service → **Settings** → **Build & Deploy**:
   - **Build command:** `npm install && npm run build:server` (installs workspaces + compiles `server/dist`)
   - **Start command:** `node server/dist/index.js`
3. Add a **Volume** to the service (Railway: service → **Volumes** → mount at `/data`).
   This is where the SQLite file lives — without a volume, your database is wiped on every deploy.

### 3.2 Set the environment variables

Service → **Variables** (raw editor is fastest). Everything from `server/.env.example`:

```ini
NODE_ENV=production
PORT=3001                          # Railway injects PORT; keep the default if unsure
CLIENT_ORIGIN=https://your-app.pages.dev   # your frontend's URL (add more, comma-separated)

DATABASE_URL=/data/prod.sqlite     # on the volume → survives deploys

DISCORD_PUBLIC_KEY=<your app's public key>
DISCORD_APPLICATION_ID=<your app's application id>
DISCORD_BOT_TOKEN=<your bot token — never in client code>

# Discord OAuth2 Authentication (Milestone 5)
DISCORD_CLIENT_ID=<your app's application id>
DISCORD_CLIENT_SECRET=<your app's OAuth2 client secret>
DISCORD_REDIRECT_URI=https://<your-backend>.up.railway.app/api/auth/discord/callback
SESSION_SECRET=<64 random hex chars for HMAC-SHA256 session token; falls back to ADMIN_API_KEY>

# Generate a NEW random value — not "dev-admin-key":
ADMIN_API_KEY=<64 random hex chars>
#   node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Generate (same command as above). Rotating it invalidates saved bot profiles:
ENCRYPTION_KEY=<64 random hex chars>

RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX=120
```

> ⚠️ **Discord Developer Portal Setup for OAuth2:**
> 1. In <https://discord.com/developers/applications> → your app → **OAuth2**:
> 2. Add your Redirect URI: `https://<your-backend>.up.railway.app/api/auth/discord/callback`.
> 3. Save changes. Users can now log in securely via the "Login with Discord" blurple button in the header.

> ℹ️ **File Attachments & Uploads:**
> The server includes an in-memory multipart parser on `/api/send`. Uploaded files (up to 10 files, 25MB each) are forwarded straight to Discord's API as multipart attachments (`payload_json` + files) with zero permanent disk writes.

> ⚠️ **Do not set `VITE_ADMIN_API_KEY` on the frontend in production.** Anything `VITE_`-prefixed
> is compiled into the browser bundle — every visitor could read it and call `/api/send` in bot
> mode. Locally it's a convenience; in production it's a hole. Production users authenticate
> via Discord OAuth2 login or granular Staff Permissions.

### 3.3 Run migrations on the server

After the first deploy, run migrations once against the deployed instance (Railway:
service → **...** → **Shell** or a one-off `railway run`):

```bash
npm run migrate
```

Migrations are idempotent — they track what's applied — so re-running is safe.

### 3.4 Verify

```bash
curl https://<your-backend>.up.railway.app/api/health
# → {"status":"ok",...}
```

---

## 4. Deploy the frontend (Cloudflare Pages)

1. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Build settings:
   - **Build command:** `npm install && npm run build:client`
   - **Build output directory:** `client/dist`
   - **Environment variables:** `NODE_VERSION=20` (or `22`), plus:
     - `VITE_API_BASE_URL=https://<your-backend>.up.railway.app`
     - (nothing else — leave the admin key out)
3. Deploy. You'll get a URL like `https://discord-message-builder.pages.dev`.

### 4.1 Sanity-check the pairing

From the deployed site, open DevTools → Network while sending in **bot mode** — the request
should go to your Railway URL, and the backend log should show the request arriving. If you see
CORS errors, the `CLIENT_ORIGIN` on the backend doesn't match the frontend URL exactly
(scheme + host, no trailing slash).

---

## 5. Point Discord at the deployed backend

1. <https://discord.com/developers/applications> → your app → **General Information** →
   **Interactions Endpoint URL**:
   ```
   https://<your-backend>.up.railway.app/api/interactions
   ```
2. **Save.** Discord sends a signed `PING`; the endpoint verifies the Ed25519 signature with
   `DISCORD_PUBLIC_KEY` and replies `PONG`. A red banner means: tunnel/server down, wrong public
   key, or wrong URL (must include `/api/interactions`).
3. That's it — buttons and selects in messages sent by your bot now execute their action chains
   (roles, DMs, modals, threads, multi-step and branching flows) against the deployed server.

### 5.1 How Discord reaches your server

Discord picks a delivery method based on whether that endpoint URL is set, and the two are
**mutually exclusive per application** — the moment a URL is configured, every interaction goes
over HTTP and the gateway receives none.

| | **HTTP webhook** | **Gateway relay** |
| --- | --- | --- |
| Endpoint URL | set | **left empty** |
| Needs a public HTTPS address | yes | **no** |
| Who receives it | your `/api/interactions` | the `bot/` worker, over the gateway WebSocket |
| Who replies | the API, in the HTTP response | the API, via `POST /interactions/{id}/{token}/callback` |
| Slash commands | worker only, if you run it | worker (**required**) |

Both paths converge on `handleInteraction()` (`server/src/services/interactionHandler.ts`), so a
flow behaves identically either way; only the transport differs.

In relay mode the worker forwards the raw interaction to `POST /api/interactions/relay` over
loopback using `x-admin-key`, the API runs the flow, and the reply is posted back to Discord using
the **interaction token** — which is itself the credential for the callback endpoint. That is why
the API can answer an interaction it never received over HTTP, and why **no inbound port and no
tunnel are required.**

If the API is unreachable, the worker answers the user itself with a readable error rather than
leaving them with "This interaction failed".

> **Sending a message and handling a click are separate concerns.** Sending needs the API (it holds
> the bot token). Delivering a *click* needs either a public address or a gateway connection. A
> host with neither can still send, but cannot run flows — which is exactly the case `bot/` solves.


> **Multi-step flows and the database.** A `custom_id` can only carry ~100 characters, so the
> editor registers a component's full chain with `POST /api/send` just before the message goes
> out. Those rows live in `action_definitions` (with a null `template_id`), which means the
> deployed backend's SQLite file must be on the persistent volume — otherwise the flows vanish on
> the next deploy and buttons fall back to only their first inline step.

---

## 6. Security checklist

- [ ] `ADMIN_API_KEY` is a fresh random value (not `dev-admin-key`) and is shared only with people who may use bot-mode sending.
- [ ] `VITE_ADMIN_API_KEY` is **not** set on the frontend host (or you accept that anyone can read it — recommended: don't).
- [ ] `DISCORD_BOT_TOKEN` exists **only** in backend env vars; never committed, never in client code.
- [ ] `ENCRYPTION_KEY` generated, backed up somewhere safe; rotating it invalidates saved bot profiles.
- [ ] `CLIENT_ORIGIN` lists your real frontend URL(s) — nothing else.
- [ ] `NODE_ENV=production` (enables `trust proxy` so rate limiting sees real client IPs).
- prod SSL is handled by Railway/Pages automatically — nothing to do.
- [ ] Local `.env` files stay out of git (already `.gitignore`d).

## 7. Troubleshooting

| Symptom                                        | Likely cause                                                                                     |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Frontend loads but every API call fails/CORS   | `CLIENT_ORIGIN` on backend ≠ frontend URL (scheme/host/trailing slash must match exactly)        |
| 401 on bot-mode send                           | `x-admin-key` header missing/mismatched — frontend and backend `ADMIN_API_KEY` must be equal     |
| Bot-mode send returns 401 from *Discord*       | `DISCORD_BOT_TOKEN` wrong or bot not in the target server                                        |
| Interactions Endpoint URL won't save           | Backend unreachable from Discord, wrong public key, or URL missing `/api/interactions`           |
| Buttons do nothing in production               | Endpoint URL still pointing at an old tunnel; or `DISCORD_PUBLIC_KEY` mismatch                   |
| Buttons do nothing, and no request reaches the API at all | No public address *and* no gateway worker running. Clear the endpoint URL and start `dmb-gateway` (§5.1) |
| Relay logs `Can't reach the API`                | `bot/.env` `API_BASE_URL`/`ADMIN_API_KEY` wrong, or `dmb-api` is not running                          |
| Button says "This interaction failed" but the flow ran | A `wait` step pushed the reply past Discord's 3-second window                                  |
| Only the first flow step runs                   | The message was sent before the flow was registered, or the DB was wiped — re-send in bot-token mode |
| Database resets after every deploy             | SQLite file not on a persistent volume (`DATABASE_URL` pointing outside the mount)               |
| Everything works then starts 429ing            | Rate limiter (`RATE_LIMIT_MAX` per `RATE_LIMIT_WINDOW_MS`); raise it or wait out the window      |

---

## 8. Process supervision with PM2

The repo ships `bot_src/ecosystem.config.cjs`, which declares:

| App | What it is | Mode |
| --- | ---------- | ---- |
| `dmb-api` | Express API + interactions endpoint | `fork`, **1 instance** |
| `dmb-web` | Built SPA via `vite preview` | `fork` |
| `dmb-gateway` | Sapphire gateway worker — **required** in relay mode, optional otherwise | `fork` (commented out) |
| `dmb-tunnel` | Optional `cloudflared` | `fork` (commented out) |

```bash
npm i -g pm2
npm run build
pm2 start ecosystem.config.cjs --env production
pm2 save && pm2 startup
```

> **Uncomment `dmb-gateway` if Discord has no way in.** With an Interactions Endpoint URL set, the
> worker only adds slash commands. Without one, it is the *only* thing that delivers button clicks
> — see [§5.1](#51-how-discord-reaches-your-server).

> **Do not enable cluster mode for `dmb-api`.** PM2's `-i max` / `exec_mode: "cluster"` starts
> several OS processes; SQLite is a single-writer embedded database, so more than one API process
> on the same file causes `SQLITE_BUSY` and eventually corruption. Scale out only after moving to
> Postgres (see §9).

## 9. When you outgrow SQLite

The database sits behind a repository layer with an async `DatabaseClient` interface — the
Postgres swap point. When a single file on a volume stops being enough (concurrent writes,
multiple server instances):

1. Provision Postgres (Railway has a one-click Postgres; Neon/Supabase work too).
2. Implement the `DatabaseClient` interface with `pg` in `server/src/config/database.ts` and
   translate the migrations to SQL.
3. Point `DATABASE_URL` at the Postgres connection string and redeploy.

No client changes needed — the API contract stays identical.
