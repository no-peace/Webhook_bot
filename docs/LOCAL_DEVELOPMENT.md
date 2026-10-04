# Local development guide (from zero)

This guide assumes you have **never** set up a project like this before. Follow the steps in
order — don't skip ahead. Everything here happens on your own computer.

> Throughout, lines starting with `$` are terminal commands. Type them **without** the `$`.
>
> - **Windows:** use the terminal that ships with Git (Git Bash) or PowerShell with Git installed.
> - **macOS:** use Terminal.
> - **Linux:** you already know what a terminal is. 🙂

---

## 1. Install the tools

### 1.1 Node.js (version 20 or newer)

1. Go to <https://nodejs.org>.
2. Download the **LTS** installer (the green button on the left).
3. Run the installer, keep clicking *Next*.
4. Verify it worked — open a terminal and run:

   ```bash
   node --version
   ```

   You should see something like `v20.11.0` (or higher). If you see
   `command not found` or `'node' is not recognized`, restart your terminal (or your computer)
   and try again.

npm (the package manager) comes bundled with Node — verify with:

```bash
npm --version
```

### 1.2 Git (optional but recommended)

If you don't have the code yet you'll need Git to download it: <https://git-scm.com>.
If you already have the project folder on your machine, skip this.

### 1.3 A Discord account

You need Discord to create webhooks and (optionally) a bot. If you don't have an account,
make one at <https://discord.com>.

---

## 2. Set up the project

Open a terminal in the folder where you put the project. On Windows you can open the folder in
File Explorer, click the address bar, type `cmd` and press Enter — or right-click → "Git Bash here".

### 2.1 Install dependencies

```bash
npm install
```

This downloads everything for **all four parts** of the app at once (they're npm workspaces):

| Folder    | What it is                                        |
| --------- | ------------------------------------------------- |
| `client/` | The website you'll see in your browser            |
| `server/` | The API + interaction endpoint (Node/Express)     |
| `shared/` | Code the above two use (types, constants)         |
| `bot/`    | Optional Discord bot (slash commands + interaction relay) |

### 2.2 Create your `.env` files

`.env` files hold secrets and settings. They are **never** committed to git (they're already in
`.gitignore`). Copy the provided templates:

```bash
cp server/.env.example server/.env
cp client/.env.example client/.env
cp bot/.env.example bot/.env        # only needed for the bot in section 7
```

Now open **`server/.env`** in any text editor (VS Code, Notepad, whatever). It looks like this:

```ini
NODE_ENV=development
PORT=3001
CLIENT_ORIGIN=http://localhost:5173
DATABASE_URL=./data/dev.sqlite

DISCORD_PUBLIC_KEY=
DISCORD_APPLICATION_ID=
DISCORD_BOT_TOKEN=

# Discord OAuth2 Login (Milestone 5)
DISCORD_CLIENT_ID=
DISCORD_CLIENT_SECRET=
DISCORD_REDIRECT_URI=http://localhost:3001/api/auth/discord/callback
SESSION_SECRET=dev-session-secret

ADMIN_API_KEY=dev-admin-key
ENCRYPTION_KEY=
```

**What to change now (minimum for local dev):**

- `ENCRYPTION_KEY` — needed only if you save bot-token profiles. Generate one:

  ```bash
  node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
  ```

  Paste the long hex string after `ENCRYPTION_KEY=`.

- `DISCORD_PUBLIC_KEY`, `DISCORD_APPLICATION_ID`, `DISCORD_BOT_TOKEN` — you can leave these
  **empty** for now. They're only needed if you want to test *button clicks* (see
  [Step 6](#6-optional-test-button-clicks-interactions)). Sending messages via **webhook URL
  works with none of them filled in**, because the browser talks straight to Discord.

- **Discord OAuth2 Login (Optional locally):**
  If testing Discord login locally, configure your Discord Application:
  1. Set `DISCORD_CLIENT_ID` to your Discord Application ID.
  2. Set `DISCORD_CLIENT_SECRET` from Discord Developer Portal -> OAuth2.
  3. In Developer Portal -> OAuth2 -> Redirects, add `http://localhost:3001/api/auth/discord/callback`.
  4. For automated testing or quick local logins without real Discord credentials, `POST /api/auth/dev-login` can issue an active session cookie directly!

- **File Attachments & Media Uploads:**
  The Message Editor features a Discohook-style File Attachments section (supporting up to 10 files, 25MB each, spoiler badges, and preview thumbnails). All uploads are buffered in RAM and forwarded directly to Discord's API with zero disk storage.

**`client/.env`** defaults are already correct for local development — no edits needed.

> ⚠️ The `VITE_ADMIN_API_KEY` in `client/.env` is a **development convenience only**. Anything
> starting with `VITE_` is bundled into the browser and visible to everyone. In production,
> user authorization is secured via Discord OAuth2 session cookies (`dmb_session`) and granular Staff Permissions.

### 2.3 Create the database

```bash
npm run migrate
```

This creates the SQLite file at `server/data/dev.sqlite` (folders included) and runs the schema
migrations. You should see each migration listed as applied.

### 2.4 Start everything

```bash
npm run dev
```

One command runs both servers side by side (colored output: `server` in blue, `client` in magenta):

- **Editor:** <http://localhost:5173>
- **API health check:** <http://localhost:3001/api/health>

To stop: click the terminal and press **Ctrl+C**.

Quick sanity checks (with the dev server running, use a second terminal or your browser):

```bash
curl http://localhost:3001/api/health
curl http://localhost:3001/api/config
```

`/api/config` should list 15 action types — that's the action registry the editor's **Flow**
tab picker is built from. (If you see fewer, the server build is stale: `npm run build:shared`.)

---

## 3. Make your first message in the editor

1. Open <http://localhost:5173>.
2. On the left is the **editor**, on the right the **live preview**. Type in the message content
   box and watch the preview update.
3. Add an embed with the embed controls (title, description, color…).
4. For Components V2, use the **component palette** to drag in containers, sections, buttons,
   etc. Discord's V2 components don't support the classic `content`/`embeds` fields together,
   so the preview switches to a V2-only layout automatically.
5. Select a button or select menu and open its **Action** tab. Add steps and order them with the
   up/down arrows — for example *Add role* → *Send DM* → *Ephemeral reply*. Steps run top to
   bottom and stop at the first one that sends a visible reply.

   The Action tab mirrors Discohook's, so these are available:

   | Step | What it does |
   | ---- | ------------ |
   | **check** | Compares values and runs a different list of steps for **Then** vs **Else**. Branches nest, and each can hold more steps (including another check) |
   | **set variable** | Stores a value for later steps. *Static* is a literal; *From the interaction* reads a field like `user.id` or the picked select values; *Copy another variable* mirrors an existing one |
   | **stop** | Ends the flow here — useful at the end of a branch so it does not fall through into the steps after the check |

   Reference variables in action-flow text fields with `{name}` or `{{name}}`, and inside a check
   with `{user.id}` style dotted paths. They resolve when the interaction runs, not in the initial
   message. **Multi-step and branching flows run on the server**, so send
   in bot-token mode (or from a saved template) for them to work — see the note at the end of
   section 6.
6. Everything you build is saved in your browser automatically (localStorage), so a refresh
   won't lose your draft.

---

## 4. Send a message with a webhook (the easy path)

A **webhook** is Discord's "post to this channel from outside" URL. Anyone with the URL can post,
so treat it like a password.

### 4.1 Get a webhook URL from Discord

1. In Discord, open your test server (make one if you don't have one — it's free).
2. Click the **⚙ gear** next to a channel → **Integrations** → **Webhooks** → **New Webhook**.
3. Optionally rename it / pick an avatar, then click **Copy Webhook URL**.

   It looks like:
   `https://discord.com/api/webhooks/1234567890/AbCdEf...`

### 4.2 Send from the builder

1. In the editor, open the **Send** panel.
2. Paste the webhook URL and click validate — it will check the URL and show the webhook's
   name/avatar.
3. Click **Send**. The browser posts **directly to Discord** — no server involved. Check your
   channel; the message should appear. 🎉

You can also save webhook profiles (name + URL) so you don't paste it every time.

> If Discord answers with `403` or `404`, the URL is wrong or the webhook was deleted.
> `400` usually means the message payload is invalid (e.g. an empty message, or classic fields
> mixed with Components V2).

---

## 5. Sending with a bot token (goes through your server)

This mode routes through **your** backend so the token never appears in the browser:

1. Create an application + bot: <https://discord.com/developers/applications> →
   **New Application** → **Bot** tab → **Reset Token** → copy it.
2. Put the token in `server/.env` as `DISCORD_BOT_TOKEN=`, save, restart `npm run dev`.
3. Invite the bot to your server: Developer Portal → **OAuth2** → check `bot` scope, give it
   **Send Messages** (+ role permissions if you'll use role actions), open the generated URL.
4. In the builder's Send panel, switch the mode to **bot token** and send. The request goes
   `browser → POST /api/send (x-admin-key header) → Discord`, and your token stays on the server.

---

## 6. (Optional) Test button clicks — interactions

When a user clicks a button your bot made, Discord calls **your** server at
`POST /api/interactions`. Discord must be able to *reach* your machine, which — since your
computer is behind your home router — needs a temporary public tunnel.

### 6.1 Get a tunnel + your app credentials

1. Install Cloudflare's tunnel tool: <https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/>
   (on Windows: `winget install --id Cloudflare.cloudflared`).
2. In your app's Developer Portal page → **General Information**, copy:
   - **Public Key** → goes into `server/.env` as `DISCORD_PUBLIC_KEY`
   - **Application ID** → `DISCORD_APPLICATION_ID`
3. Start the tunnel (in a **second** terminal, keep `npm run dev` running):

   ```bash
   cloudflared tunnel --url http://localhost:3001
   ```

   It prints a public URL like `https://something-words.trycloudflare.com`.

### 6.2 Point Discord at your tunnel

1. Developer Portal → your app → **General Information** → **Interactions Endpoint URL**.
2. Enter `https://something-words.trycloudflare.com/api/interactions` and **Save**.
3. Discord immediately sends a signed `PING`. Your server verifies the Ed25519 signature with
   your public key and answers `PONG`. If Discord says "failed to verify", check that
   `DISCORD_PUBLIC_KEY` in `server/.env` matches and that `npm run dev` is running.

### 6.3 Try it

1. Send a message **in bot mode** with a button whose action is e.g. *send DM* or *add role*.
2. Click the button in Discord. Your tunnel receives the interaction, the server looks up the
   flow and runs the handler chain in order — including multi-step flows (`wait`, `check`,
   `set_variable`).
3. Watch the blue `server` output in your terminal to see the interaction arrive.

> **Multi-step flows need the server.** A `custom_id` holds only 100 characters, so only the
> *first* step's parameters fit inline. When you send in **bot token** mode, the editor registers
> the whole chain with `/api/send` before the message goes out. Save the message as a template
> and its flows are stored too. A message sent through a **webhook URL** goes straight from the
> browser to Discord, so only that first inline step can run.

> **Already wired up?** Buttons whose flow you have not touched default to `action:dud` (do
> nothing) — pick a real action on the Action tab before sending if you want a click to do
> something.

> Tunnel URLs change every time you restart `cloudflared`, so re-save the endpoint URL after a
> restart. This is why production uses a real deployed URL — see `docs/DEPLOYMENT.md`.

---

## 7. (Optional) The Discord bot: slash commands and the relay

`bot/` is a [Sapphire](https://sapphirejs.dev) worker that connects to Discord's **gateway**. It
does two things, and the second one is the reason it exists at all:

1. **Slash commands** — `/ping`, `/status`, `/server`, `/send`.
2. **The interaction relay** — the only way button clicks reach the server when it has **no public
   address**.

### 7.1 Why the relay is needed (and where)

Discord delivers interactions in one of two ways, and they are mutually exclusive per application:

- **Endpoint URL set** → Discord POSTs to your `/api/interactions`. This is what the tunnel in
  section 6 provides, and it is what you use **on your laptop**.
- **Endpoint URL empty** → Discord sends the interaction over the gateway connection.

> ⚠️ **The Cloudflare Tunnel only exists on your laptop.** When the app runs on a server (for
example a Pterodactyl container) there is no tunnel and no public URL, so Discord has nowhere to
POST to. In that case, **leave the Interactions Endpoint URL empty** and run this bot: it receives
the click over the gateway (an *outbound* WebSocket, so no port has to be opened) and forwards it
to the API on `localhost`. The API runs the flow and posts the reply back to Discord using the
interaction token, so the reply path needs no inbound port either.

Both routes run the same flow code, so a button behaves identically either way.

### 7.2 Run it

1. Create an application + bot if you have not already (section 5).
2. Copy the env template and fill it in:

   ```bash
   cp bot/.env.example bot/.env
   ```

   ```ini
   DISCORD_BOT_TOKEN=<the same token as server/.env>
   API_BASE_URL=http://localhost:3001
   ADMIN_API_KEY=<the same value as server/.env — required, or the relay is refused>
   DEV_GUILD_ID=<optional: your server's id, so commands appear instantly>
   ```

3. Keep `npm run dev` running (the API must be up), then in a second terminal:

   ```bash
   npm run dev:bot
   ```

   You should see `[bot] logged in as …` and `[bot] ready as …`.

4. In Discord, try `/ping` (latency), `/status` (API + integrations health) and `/server`
   (server name, member/channel/role counts, boost tier, owner, age).

> **Slash commands need `DEV_GUILD_ID`, or patience.** Registered globally, new commands can take
> up to an hour to appear. Scoping them to one guild makes changes instant — that is what
> `DEV_GUILD_ID` is for.

> **Switching modes is a two-sided change.** Whenever you flip between laptop (tunnel) and server
> (relay), update the Interactions Endpoint URL in the Developer Portal *and* start/stop the bot.
> Setting a URL while the bot runs sends every click to HTTP, so the bot sees nothing.

---

## 8. Everyday commands cheat sheet

| Command                        | What it does                                    |
| ------------------------------ | ----------------------------------------------- |
| `npm run dev`                  | Run client + server together (hot reload)       |
| `npm run dev:client`           | Only the website (Vite)                         |
| `npm run dev:server`           | Only the API (`tsx watch`, restarts on save)    |
| `npm run dev:bot`              | Only the Discord bot (`tsx watch`)              |
| `npm run start:bot`            | Run the *built* bot (`node bot/dist`)           |
| `npm run build:shared`         | Rebuild `shared/` types (needed on its own when editing `shared/`) |
| `npm run migrate`              | Create/upgrade the SQLite database              |
| `npm run typecheck`            | Type-check all four workspaces                  |
| `npm run test`                 | Run every workspace's test suite                |
| `npm run build`                | Production build (shared → client → server → bot) |
| `npm start`                    | Run the *built* server (`node server/dist`)     |

## 9. Troubleshooting

| Symptom                                            | Fix                                                                                       |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `EADDRINUSE :3001` or `:5173`                      | Another process is using the port — close the old terminal, or change `PORT` in `server/.env` and the Vite port. |
| Sending in bot mode returns 401/403                | Bot token wrong, or bot not invited to the server. Re-invite with `bot` scope.            |
| Send panel says sending isn't available            | `/api/config` reports `botSendAvailable: false` → `DISCORD_BOT_TOKEN` is empty. Fill it in and restart. |
| Endpoint URL won't save in the Developer Portal    | Tunnel not running, URL missing `/api/interactions`, or public key mismatch.              |
| Buttons do nothing when clicked                    | Same as above — interactions aren't reaching your server yet. Check `server` output on click. |
| Database errors / "no such table"                  | Run `npm run migrate` again. Delete `server/data/dev.sqlite` to start fresh (loses saved templates/profiles). |
| Weird build errors after pulling changes           | `rm -rf node_modules && npm install`, then `npm run typecheck`.                            |
| `@dmb/shared` type errors after editing `shared/`  | The server reads the package's built types — run `npm run build:shared` (or just `npm run dev`, which does it first). |
| A multi-step button only does its first action      | Webhook sends can't register flows. Send in **bot token** mode, or save and send from a template. |
| Button says "isn't wired up to an action"            | The `custom_id` is not `action:…`. Re-pick an action on the **Flow** tab.                   |
| A branching flow does nothing on click              | Branching runs server-side — send in **bot token** mode or from a template so the flow is registered. |
| Button click says "This interaction failed" but the flow ran | A `wait` step pushed the reply past Discord's 3-second window. Keep waits short.      |
| `/ping` never appears in Discord                    | Set `DEV_GUILD_ID` in `bot/.env` and restart the bot — global registration can take an hour. |
| Bot logs in but clicks still don't reach it         | The Interactions Endpoint URL is still set, so Discord is using HTTP instead of the gateway. Clear it and restart the bot. |

> **Note (Windows):** to stop a stuck Node process: `netstat -ano | findstr :3001` to find the
> PID, then `taskkill /F /PID <pid>`. In Git Bash, use `taskkill //F //PID <pid>` (double slash).
