# Discord Message Builder Website - Implementation Plan

## 1. Design Thoughts & Decisions

### Why This Architecture?

| Decision | Rationale |
|----------|-----------|
| **Vite + React + Tailwind + Zustand** | React provides the mature component ecosystem needed for complex visual editors (Discohook uses React). Zustand offers simple, boilerplate-free state management for the message builder state. Tailwind accelerates UI development matching Discord's design system. |
| **Express.js Backend** | Best Discord interaction examples, official `discord-interactions` middleware for signature verification, Termux-friendly, high AI coding success rate. |
| **Hybrid Sending (Webhook direct / Bot Token proxied)** | Webhook URLs are safe for client-side use. Bot tokens **must never** reach the frontend. The backend `/api/send` endpoint acts as a secure proxy. |
| **SQLite (`better-sqlite3`) with Repository Pattern** | Zero-config, works in Termux and on servers. Abstracting behind a repository interface enables painless PostgreSQL migration later. |
| **Action System = Custom ID + Backend Router** | Each interactive component gets a unique `custom_id` encoding the action type and parameters. Backend `/api/interactions` verifies Discord signatures, parses the `custom_id`, and executes the corresponding action handler. |
| **Separate Frontend/Backend Repos (or folders)** | Clear separation of concerns. Frontend is a static SPA deployable to Vercel/Cloudflare Pages. Backend is a Node service deployable to Railway/Render/VPS. |
| **Components V2 First** | Discord is moving to Components V2 (Containers, TextDisplay, Sections, MediaGallery). The editor should default to this with classic embeds as a legacy option. |
| **No Auth Initially** | Single-user/local-only per requirements. Middleware scaffolded for future role-based access (admin vs. friend permissions). |

### Key Discord API Gotchas Addressed
- **`MessageFlags.IsComponentsV2` (1 << 15)** must be set for Components V2 messages
- **Interaction signature verification** via `discord-interactions` middleware using the bot's Public Key
- **Ephemeral responses** for button clicks (only visible to clicker)
- **15-minute interaction token expiry** - use followups for delayed actions
- **Rate limits** - implement retry logic with exponential backoff

---

## 2. Architecture & Communication Flow

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Vite + React)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Message      │  │ Components   │  │ Action       │  │ Template/    │   │
│  │ Editor       │  │ V2 Builder   │  │ Builder      │  │ Profile Mgr  │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │                 │           │
│         └─────────────────┼─────────────────┼─────────────────┘           │
│                           ▼                 ▼                              │
│                    ┌──────────────────────────────┐                       │
│                    │ Zustand Store (Message State) │                       │
│                    └──────────────┬───────────────┘                       │
│                                   │                                       │
│              ┌────────────────────┼────────────────────┐                  │
│              ▼                    ▼                    ▼                  │
│    ┌───────────────┐    ┌───────────────┐    ┌───────────────┐           │
│    │ Live Preview  │    │ Webhook URL   │    │ Bot Token     │           │
│    │ (Discord-like)│    │ Send (Direct) │    │ Send (Proxy)  │           │
│    └───────────────┘    └───────┬───────┘    └───────┬───────┘           │
└─────────────────────────────────│────────────────────│────────────────────┘
                                  │                    │
                    ┌─────────────┘                    └─────────────┐
                    ▼                                              ▼
         ┌─────────────────────┐                        ┌─────────────────────┐
         │   Discord API       │                        │   BACKEND           │
         │   (Webhook Endpoint)│                        │   (Express.js)      │
         └─────────────────────┘                        │                     │
                                                        │  ┌───────────────┐  │
                                                        │  │ /api/send     │  │
                                                        │  │ - Validate    │  │
                                                        │  │ - Proxy to    │  │
                                                        │  │   Discord     │  │
                                                        │  └───────────────┘  │
                                                        │  ┌───────────────┐  │
                                                        │  │ /api/interact │  │
                                                        │  │ - Verify Sig  │  │
                                                        │  │ - Route Action│  │
                                                        │  │ - Execute     │  │
                                                        │  └───────────────┘  │
                                                        │  ┌───────────────┐  │
                                                        │  │ /api/templates│  │
                                                        │  │ - CRUD        │  │
                                                        │  └───────────────┘  │
                                                        │  ┌───────────────┐  │
                                                        │  │ SQLite DB     │  │
                                                        │  │ (Repository)  │  │
                                                        │  └───────────────┘  │
                                                        └─────────────────────┘
```

### Communication Flows

#### Flow 1: Send via Webhook URL (Client-Side Direct)
```
User clicks "Send" → Frontend validates payload → POST directly to Discord webhook URL
→ Discord returns 200/204 → Frontend shows success
```
- **Security**: Webhook URLs are public-by-design, safe to use client-side
- **Rate limits**: Handled by Discord, frontend shows retry-after

#### Flow 2: Send via Bot Token (Backend Proxy)
```
User clicks "Send" → Frontend POSTs payload to /api/send { mode: "bot", ... }
→ Backend validates (user is admin) → Uses bot token to call Discord API
→ Discord returns message → Backend returns to frontend
```
- **Security**: Bot token never leaves backend
- **Features**: Can send to any channel bot has access to, supports Components V2

#### Flow 3: Button/Select Click (Action Execution)
```
User clicks button in Discord → Discord POSTs to /api/interactions
→ Backend verifies signature (discord-interactions middleware)
→ Parse custom_id → Route to action handler
→ Execute action (AddRole, SendDM, OpenModal, etc.)
→ Respond with ephemeral message or update
```
- **Custom ID Format**: `action:{type}:{params}` (e.g., `action:add_role:123456789`)
- **Multi-step flows**: Store flow state in DB keyed by interaction token

---

## 3. Folder Structure

```
discord-message-builder/
├── client/                          # Frontend (Vite + React)
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── editor/              # Message editor components
│   │   │   │   ├── MessageEditor.jsx
│   │   │   │   ├── EmbedEditor.jsx
│   │   │   │   ├── ContainerEditor.jsx
│   │   │   │   ├── ActionRowEditor.jsx
│   │   │   │   ├── ComponentPalette.jsx
│   │   │   │   └── PropertyPanel.jsx
│   │   │   ├── preview/             # Live preview (Discord-like)
│   │   │   │   ├── MessagePreview.jsx
│   │   │   │   ├── ContainerPreview.jsx
│   │   │   │   ├── EmbedPreview.jsx
│   │   │   │   └── ActionRowPreview.jsx
│   │   │   ├── actions/             # Action builder UI
│   │   │   │   ├── ActionBuilder.jsx
│   │   │   │   ├── ActionTypeSelect.jsx
│   │   │   │   └── ActionForms/     # Per-action-type forms
│   │   │   ├── ui/                  # Reusable UI primitives
│   │   │   │   ├── Button.jsx
│   │   │   │   ├── Modal.jsx
│   │   │   │   ├── Select.jsx
│   │   │   │   ├── ColorPicker.jsx
│   │   │   │   └── DraggableList.jsx
│   │   │   └── layout/
│   │   │       ├── Header.jsx
│   │   │       ├── Sidebar.jsx
│   │   │       └── SplitPane.jsx
│   │   ├── store/
│   │   │   ├── messageStore.js      # Zustand: message data, components, embeds
│   │   │   ├── actionStore.js       # Zustand: action definitions per custom_id
│   │   │   ├── templateStore.js     # Zustand: saved templates
│   │   │   └── profileStore.js      # Zustand: webhook profiles, bot config
│   │   ├── hooks/
│   │   │   ├── useMessage.js
│   │   │   ├── useActions.js
│   │   │   ├── useTemplates.js
│   │   │   └── useDiscordPreview.js
│   │   ├── utils/
│   │   │   ├── discord.js           # Payload builders, validation
│   │   │   ├── componentsV2.js      # Components V2 helpers
│   │   │   ├── exportImport.js      # JSON import/export (Discohook compat)
│   │   │   └── constants.js         # Discord limits, component types
│   │   ├── api/
│   │   │   ├── client.js            # Axios/fetch wrapper for backend
│   │   │   └── discord.js           # Direct Discord webhook calls
│   │   ├── styles/
│   │   │   └── globals.css
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── routes.jsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env.example
│
├── server/                          # Backend (Express.js)
│   ├── src/
│   │   ├── config/
│   │   │   ├── env.js               # Validated env vars
│   │   │   └── database.js          # SQLite connection + migrations
│   │   ├── middleware/
│   │   │   ├── verifyDiscordSignature.js  # discord-interactions
│   │   │   ├── auth.js              # Admin check (scaffold for RBAC)
│   │   │   ├── rateLimit.js         # Express rate limiter
│   │   │   └── errorHandler.js
│   │   ├── routes/
│   │   │   ├── send.js              # POST /api/send
│   │   │   ├── interactions.js      # POST /api/interactions
│   │   │   ├── templates.js         # CRUD /api/templates
│   │   │   ├── profiles.js          # CRUD /api/profiles
│   │   │   └── health.js            # GET /api/health
│   │   ├── services/
│   │   │   ├── discordService.js    # Discord API calls (bot token)
│   │   │   ├── actionExecutor.js    # Executes action handlers
│   │   │   ├── templateService.js   # Template CRUD logic
│   │   │   └── profileService.js    # Webhook/bot profile management
│   │   ├── actions/                 # Action implementations
│   │   │   ├── index.js             # Router: custom_id → handler
│   │   │   ├── addRole.js
│   │   │   ├── removeRole.js
│   │   │   ├── toggleRole.js
│   │   │   ├── sendDm.js
│   │   │   ├── sendEphemeralReply.js
│   │   │   ├── openModal.js
│   │   │   ├── sendMessage.js
│   │   │   ├── deleteMessage.js
│   │   │   └── wait.js
│   │   ├── repositories/            # DB abstraction (for Postgres migration)
│   │   │   ├── baseRepository.js
│   │   │   ├── templateRepository.js
│   │   │   ├── actionRepository.js
│   │   │   ├── profileRepository.js
│   │   │   └── userRepository.js
│   │   ├── utils/
│   │   │   ├── snowflake.js         # Discord ID helpers
│   │   │   ├── validation.js        # Payload validation
│   │   │   └── logger.js
│   │   ├── app.js                   # Express app setup
│   │   └── index.js                 # Entry point
│   ├── package.json
│   ├── .env.example
│   └── Dockerfile
│
├── shared/                          # Shared types/constants (optional)
│   └── constants.js
│
├── docker-compose.yml               # Local dev: client + server + db
├── README.md
└── project_architecture_plan.md     # This file
```

---

## 4. Database Schema (SQLite)

### Tables

```sql
-- Users (for future multi-user, admin flag for now)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id TEXT UNIQUE NOT NULL,      -- Discord user ID (snowflake)
    username TEXT NOT NULL,
    avatar TEXT,
    is_admin INTEGER DEFAULT 1,           -- 1 = admin, 0 = limited (future)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Webhook Profiles (saved webhook URLs + metadata)
CREATE TABLE webhook_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    url TEXT NOT NULL,                    -- Full webhook URL
    channel_id TEXT,                      -- Parsed from URL
    guild_id TEXT,                        -- Parsed from URL
    avatar_url TEXT,
    is_default INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bot Profiles (for bot token sending - admin only)
CREATE TABLE bot_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    token_encrypted TEXT NOT NULL,        -- Encrypted bot token
    public_key TEXT NOT NULL,             -- Discord public key for verification
    application_id TEXT NOT NULL,
    default_guild_id TEXT,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Message Templates (saved message configurations)
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    data TEXT NOT NULL,                   -- JSON: full QueryData (Discohook format)
    preview_image_url TEXT,               -- Generated preview thumbnail
    is_public INTEGER DEFAULT 0,          -- For future sharing
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Action Definitions (linked to component custom_ids)
CREATE TABLE action_definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER REFERENCES templates(id) ON DELETE CASCADE,
    message_id TEXT,                      -- Ad-hoc message ID; null for template-owned flows
    custom_id TEXT NOT NULL,              -- e.g., "action:add_role:123456789"
    action_type TEXT NOT NULL,            -- add_role, remove_role, toggle_role, send_dm, etc.
    config TEXT NOT NULL,                 -- JSON: action-specific parameters
    execution_order INTEGER DEFAULT 0,    -- For multi-action sequences
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Action Execution Logs (audit trail)
CREATE TABLE action_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_definition_id INTEGER REFERENCES action_definitions(id) ON DELETE SET NULL,
    interaction_id TEXT NOT NULL,         -- Discord interaction ID
    user_id TEXT NOT NULL,                -- Discord user who triggered
    guild_id TEXT,
    channel_id TEXT,
    status TEXT NOT NULL,                 -- success, failed, pending
    response TEXT,                        -- JSON response/error
    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Scheduled Messages (for future cron-like sending)
CREATE TABLE scheduled_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    webhook_profile_id INTEGER REFERENCES webhook_profiles(id) ON DELETE SET NULL,
    bot_profile_id INTEGER REFERENCES bot_profiles(id) ON DELETE SET NULL,
    cron_expression TEXT,                 -- Standard cron
    next_run_at DATETIME,
    last_run_at DATETIME,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indices
CREATE INDEX idx_templates_user ON templates(user_id);
CREATE INDEX idx_actions_template ON action_definitions(template_id);
CREATE INDEX idx_actions_custom_id ON action_definitions(custom_id);
CREATE INDEX idx_actions_message_custom ON action_definitions(message_id, custom_id);
CREATE INDEX idx_logs_interaction ON action_logs(interaction_id);
CREATE INDEX idx_scheduled_next_run ON scheduled_messages(next_run_at);
```

### Repository Pattern (for Postgres Migration)

Each repository exposes a clean interface:
```javascript
// repositories/templateRepository.js
class TemplateRepository {
  constructor(db) { this.db = db; }
  async create(data) { /* INSERT */ }
  async findById(id) { /* SELECT */ }
  async findByUser(userId) { /* SELECT */ }
  async update(id, data) { /* UPDATE */ }
  async delete(id) { /* DELETE */ }
  async search(query) { /* SELECT with filters */ }
}
```

**Migration Path**: Swap `better-sqlite3` for `pg` in `config/database.js`, update SQL dialect in repositories only.

---

## 5. Development Phases

### Phase 1: Core Editor & Preview (Weeks 1-2)
**Goal**: Functional message builder with live preview, classic embeds, Components V2, webhook sending.

| Task | Details |
|------|---------|
| **1.1 Project Setup** | `npm create vite@latest client -- --template react`, install Tailwind, Zustand, Lucide icons, `@dnd-kit` for drag-drop |
| **1.2 Layout & State** | Split-pane layout (editor left, preview right). Zustand store for `messageData` (QueryData format). |
| **1.3 Classic Embed Editor** | Form for all embed fields (title, description, fields, color, footer, author, image, thumbnail). Validation against Discord limits (6000 total chars, 256 title, etc.). |
| **1.4 Components V2 Editor** | Builders for: Container, TextDisplay (markdown), Section + Thumbnail, Separator, MediaGallery, File, ActionRow (Buttons, Selects). Mirror Discohook's component palette + property panel pattern. |
| **1.5 Live Preview** | Render message using Discord-like styling (adapt Discohook's preview components). Toggle between classic/Components V2 modes. |
| **1.6 Webhook URL Sending** | Input field for webhook URL → POST directly to Discord from frontend. Handle rate limits, show success/error. |
| **1.7 Import/Export** | JSON import/export compatible with Discohook format. LocalStorage backups. |
| **1.8 File Attachments** | Drag-drop file upload → convert to `attachment://` references. Preview images/videos. |

**Deliverable**: Working message builder at `localhost:5173` that can send via webhook URL.

---

### Phase 2: Backend & Bot Token Proxy (Weeks 3-4)
**Goal**: Express backend with bot token sending, signature verification, SQLite persistence.

| Task | Details |
|------|---------|
| **2.1 Express Server Setup** | `express`, `discord-interactions`, `better-sqlite3`, `cors`, `helmet`, `dotenv`. Structure per folder layout. |
| **2.2 Database Layer** | Initialize SQLite, run migrations, implement repository classes. Seed admin user. |
| **2.3 Bot Profile Management** | UI to add bot token (encrypted at rest), public key, application ID. Store in `bot_profiles`. |
| **2.4 `/api/send` Endpoint** | Accept `{ mode: "bot" | "webhook", payload, profileId }`. Validate admin. Proxy to Discord using bot token or webhook URL. |
| **2.5 `/api/interactions` Endpoint** | Mount `discord-interactions` middleware with public key. Parse `custom_id`, route to action executor. Respond with ephemeral messages. |
| **2.6 Template CRUD API** | `/api/templates` - full CRUD for saving/loading message templates. |
| **2.7 Profile CRUD API** | `/api/profiles` - manage webhook/bot profiles. |
| **2.8 Frontend Integration** | Connect "Send via Bot Token" to `/api/send`. Load/save templates from backend. |

**Deliverable**: Full stack app. Send via bot token works. Templates persist to SQLite.

---

### Phase 3: Action System (Weeks 5-7)
**Goal**: Buttons/selects execute real Discord actions (roles, DMs, modals, multi-step).

| Task | Details |
|------|---------|
| **3.1 Action Builder UI** | In Component editor, when adding Button/Select with `custom_id`, show "Action" tab. Action type selector + dynamic form per type. |
| **3.2 Custom ID Schema** | Format: `action:{type}:{encodedParams}`. Examples: `action:add_role:123456`, `action:send_dm:{"templateId": 5}`. |
| **3.3 Action Executor Core** | Router in `actions/index.js` mapping action_type → handler module. Each handler receives `(interaction, config, context)`. |
| **3.4 Core Actions** | Implement: `add_role`, `remove_role`, `toggle_role`, `send_dm`, `send_ephemeral_reply`, `open_modal`, `send_message` (from template), `delete_message`, `wait`. |
| **3.5 Multi-Step Flows** | Support `check` (conditions) and `set_variable` actions. Store flow state in DB keyed by interaction token for async steps. |
| **3.6 Modal Support** | `open_modal` action → returns Modal payload. Handle `ModalSubmit` interaction type in `/api/interactions`. |
| **3.7 Action Persistence** | Save action definitions to `action_definitions` linked to template. Load when template loaded. |
| **3.8 Testing Harness** | Local test page to simulate button clicks without Discord. |

**Deliverable**: Buttons in sent messages actually add/remove roles, send DMs, open forms.

---

### Phase 4: Polish, Deploy & Extensibility (Weeks 8+)
**Goal**: Production-ready, deployable, extensible for friends.

| Task | Details |
|------|---------|
| **4.1 Auth & RBAC Scaffold** | JWT-based auth (even if single-user now). Middleware `requireRole("admin")` on sensitive routes. User roles table. |
| **4.2 Rate Limiting & Security** | Express rate limiter on `/api/*`. Helmet CSP. Input sanitization. Bot token encryption (AES-GCM). |
| **4.3 Error Handling & Logging** | Structured logging (pino). Friendly error UI. Discord error code mapping. |
| **4.4 Mobile Responsive** | Tailwind breakpoints. Collapsible sidebar. Touch-friendly drag-drop. |
| **4.5 Share Links** | Generate short-lived share URLs for templates (like Discohook). |
| **4.6 Scheduled Sending** | Background worker (node-cron) for `scheduled_messages`. |
| **4.7 Docker & Deploy** | `docker-compose.yml` for local. Dockerfiles for client (static nginx) + server. Deploy guides for Vercel + Railway/Render. |
| **4.8 Postgres Migration Prep** | Verify all repositories use parameterized queries. Test with Postgres locally. |
| **4.9 Documentation** | API docs (OpenAPI), component library storybook, contribution guide. |

**Deliverable**: Production deployment. Friends can be granted limited access via RBAC.

---

## Quick Reference: Key Files to Reference from Discohook Source

| Feature | Discohook Source Path |
|---------|----------------------|
| Message Editor State | `packages/site/app/components/editor/MessageEditor.client.tsx` |
| Components V2 Preview | `packages/site/app/components/preview/Container.tsx`, `TextDisplay.tsx`, `Section.tsx` |
| Embed Preview | `packages/site/app/components/preview/Embed.tsx` |
| Action/Flow System | `packages/bot-rw/src/flows/flows.ts`, `packages/store/src/types/components.ts` |
| Interaction Handling | `packages/bot-rw/src/interactions.ts` |
| Database Schema | `packages/store/src/schema/schema.ts` |
| Webhook Sending | `packages/bot-rw/src/flows/backup.ts` |
| QueryData Format | `packages/store/src/types/backups.ts` |

---
