# Scope: Milestone 5 — Discord OAuth2 Login & File Attachments

## Architecture
- **Backend Auth & Session (`hoho_manager/server`)**:
  - `GET /api/auth/discord/login`: Redirects user to Discord OAuth2 authorization URL with `identify` scope.
  - `GET /api/auth/discord/callback`: Exchanges OAuth2 code for Discord token, fetches user profile (`/@me`), signs secure JWT / HTTP-only session cookie containing user ID, username, discriminator/global_name, and avatar.
  - `GET /api/auth/me`: Returns the authenticated user session profile.
  - `POST /api/auth/logout`: Clears session cookie.
  - Auth Middleware (`staffPermissions.ts` / `auth.ts`): Automatically extracts authenticated user ID from session cookie / JWT for staff permission validation if present, while gracefully supporting fallback or headers if needed.
- **Backend File Streaming (`hoho_manager/server/src/routes/send.ts`)**:
  - `/api/send` upgraded to accept both `application/json` and `multipart/form-data`.
  - Files handled in memory/stream via `multer` (memory storage) or similar, zero permanent disk storage.
  - Forwarded to Discord Webhook / Channel message endpoint using `FormData` / `Blob` / buffer with `files[n]` and `payload_json`.
- **Frontend OAuth & Header (`hoho_manager/client`)**:
  - Top-right Header: When logged out, display "Login with Discord" button (Discord blurple or Discohook style).
  - When logged in, display Discord avatar, username, and dropdown with user info and Logout button.
  - State managed in global store (`useGlobalStore` or `useAuthStore`).
  - AccessPanel and other components use authenticated user ID automatically.
- **Frontend File Attachments (`hoho_manager/client/src/components/editor`)**:
  - New "File Attachments" collapsible section in `MessageEditor.tsx`, styled after Discohook (`#1e1f22`, dashed drag-and-drop zone or "+ Add File" button).
  - Previews attached files with file name, size, type icon / thumbnail, and remove button.
  - Attached files passed into send payload as `FormData`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Discord OAuth2 Endpoints | `/api/auth/discord/login` and `/api/auth/discord/callback` flow with code exchange | M5 | R1 |
| 2 | Session & Auth Middleware | HTTP-only cookie / signed JWT storing user ID and avatar; middleware uses authenticated ID for staff permissions | M5 | R1 |
| 3 | Frontend OAuth Header & State | "Login with Discord" button, user avatar & username in top right Header, logout action | M5 | R1 |
| 4 | File Attachment Editor UI | File upload UI section in Message Editor matching Discohook design, file preview & remove | M5 | R2 |
| 5 | Multipart Send & Discord Forwarding | `/api/send` accepts `multipart/form-data`, streams files directly to Discord API via `FormData` without disk storage | M5 | R2 |
| 6 | Native Discohook #1e1f22 Polish | Cohesive dark UI polish, smooth transitions, accessible controls | M5 | R3 |
| 7 | Documentation Updates | Update `docs/DEPLOYMENT.md`, `docs/LOCAL_DEVELOPMENT.md`, `docs/PTERODACTYL_DEPLOYMENT.md`, and `chatwithantigravity.md` with OAuth2 env vars and file attachment features | M5 | R4 |
| 8 | Fix Server Dropdown Fetch & UI | Fix Selected Server dropdown fetching bug, ensure guild list populates smoothly from bot API | M5 | Remediation |
| 9 | Discohook Exact Layout & Palette Relocation | Move component elements/palette out of drawer/toolbox into editor/actions matching Discohook's exact layout; style Classic and V2 editors to perfectly match Discohook | M5 | Remediation |
| 10 | Knowledge Preservation | Copy all `.md` files from `.agents/teamwork/` and its subdirectories into `docs/` (copy, NOT move) | M5 | Remediation |

## Interface Contracts

### 1. Auth API
- `GET /api/auth/discord/login`: Redirects to `https://discord.com/oauth2/authorize?client_id=...&response_type=code&scope=identify&redirect_uri=...`
- `GET /api/auth/discord/callback?code=...`: Exchanges code with Discord API, sets HTTP-only cookie (`token` or `session`), redirects to frontend.
- `GET /api/auth/me`: Returns `{ user: { id: string, username: string, global_name?: string, avatar: string | null } | null }`.
- `POST /api/auth/logout`: Clears session cookie, returns `{ success: true }`.

### 2. Send API (`/api/send`)
- Supports `application/json` (existing) AND `multipart/form-data`.
- For `multipart/form-data`:
  - `payload_json`: JSON stringified message payload (target, message, flows, etc.).
  - `files`: Array of uploaded file buffers.
- Discord forwarding:
  - Constructs `FormData` with `payload_json` and `files[0]`, `files[1]`, etc.
  - Posts to Discord webhook or channel message endpoint.
- Zero local file storage.

## Quality Gates
- TypeScript typecheck passes across all packages (`npm run typecheck` 0 errors).
- All existing tests pass.
- Reviewer, Challenger, and Forensic Auditor pass.
