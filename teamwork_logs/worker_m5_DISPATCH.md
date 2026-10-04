# DISPATCH — worker_m5

## Identity
- Role: Milestone 5 Implementation Worker
- Working directory: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\worker_m5\
- Archetype: teamwork_preview_worker

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Context & Inputs
- User Request: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\ORIGINAL_REQUEST.md
- Project Scope: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\orchestrator_5\SCOPE.md
- Project Plan: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\PROJECT.md
- Backend Blueprint: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_1\handoff.md
- Frontend Blueprint: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_2\handoff.md
- File Attachments Blueprint: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_3\handoff.md

## Mission
Implement Milestone 5: Discord OAuth2 Login and File Attachments for Hoho Manager across both backend and frontend.

### 1. Backend Implementation (`hoho_manager/server`)
1. **OAuth2 & Session Management (`src/routes/auth.ts`, `src/config/env.ts`, `src/app.ts`)**:
   - Add OAuth2 environment variables in `src/config/env.ts` (`DISCORD_CLIENT_ID` defaulting to `applicationId`, `DISCORD_CLIENT_SECRET`, `DISCORD_REDIRECT_URI`).
   - Implement `GET /api/auth/discord/login`: Redirects to Discord authorization URL (`identify` scope).
   - Implement `GET /api/auth/discord/callback`: Exchanges code for token (`POST https://discord.com/api/v10/oauth2/token`), fetches user (`GET https://discord.com/api/v10/users/@me`), upserts user via `userRepository.upsert`, signs secure session cookie (`dmb_session`) using HMAC-SHA256 (`env.adminApiKey`), redirects to client `/?login=success`.
   - Implement `GET /api/auth/me`: Reads cookie or Bearer token, validates signature, returns `{ user: { id, username, global_name, avatar, role, isAdmin } }` or `{ user: null }`.
   - Implement `POST /api/auth/logout`: Clears session cookie, returns `{ success: true }`.
   - Implement `POST /api/auth/dev-login`: For development/testing, accepts `{ discordId, username, avatar, role }`, issues valid session cookie.
2. **Anti-Spoofing & Staff Permissions (`src/middleware/staffPermissions.ts`, `src/middleware/auth.ts`)**:
   - Extract session user from cookie/bearer token.
   - If session user exists: enforce `staffId = sessionUser.id`. If client also provided `x-staff-id` and it does NOT match `sessionUser.id`, reject with `403 Forbidden` (anti-spoofing).
   - If no session user exists: fall back to `x-staff-id` / `x-admin-key` to preserve backward compatibility for automated tests and headless scripts.
   - In `auth.ts`, update `attachUser` and `requireHeadAdmin` to recognize the session user.
3. **Multipart File Forwarding (`src/routes/send.ts`, `src/services/discordService.ts`)**:
   - Implement multipart parser middleware mounted on `POST /api/send` **BEFORE** `requireStaffPermission("send")`. Use Node 24 native Web Standards (`Readable.toWeb` -> `Request.formData()`) or in-memory parsing. Zero permanent disk storage! Populates `req.body` (including `channelId`, `payload`, etc.) and `req.files`.
   - Update `discordService.ts` (`apiRequest`): Support `body instanceof FormData`. When `FormData` is passed, omit `Content-Type` header so `fetch` sets the multipart boundary.
   - In `send.ts`: When `req.files` are present, construct outbound `FormData` with `payload_json` and `files[i]`, forward to Discord webhook or channel message endpoint.

### 2. Frontend Implementation (`hoho_manager/client`)
1. **Session & Auth State (`src/store/globalStore.ts`, `src/api/client.ts`, `src/App.tsx`)**:
   - In `globalStore.ts`: Add `currentUser: { id: string, username: string, global_name?: string, avatar: string | null } | null`, `authLoading: boolean`, `fetchCurrentUser()`, `logout()`.
   - In `client.ts`: Add `credentials: "include"` on all fetches. When `body instanceof FormData`, do not stringify and do not set `Content-Type`. Pass `currentUser.id` dynamically.
   - In `App.tsx`: On mount (`useEffect`), call `fetchCurrentUser()`.
2. **Header Integration (`src/components/layout/Header.tsx`)**:
   - Unauthenticated: Display "Login with Discord" button (Discord blurple `#5865f2`, Discord icon, redirects to `/api/auth/discord/login`).
   - Authenticated: Display user avatar (with fallback calculation `(BigInt(id) >> 22n) % 6n`), username, and sleek dropdown menu matching Discohook `#1e1f22` aesthetic (showing user banner, snowflake ID with click-to-copy, staff status, and Logout button).
3. **AccessPanel Integration (`src/components/layout/AccessPanel.tsx`)**:
   - Display authenticated operator banner/card.
   - Add "Grant to Myself" button when creating staff access.
   - Mark matching user in staff list with `(You)` badge.
4. **File Attachments Section (`src/components/editor/FileAttachmentsSection.tsx`, `MessageEditor.tsx`)**:
   - Create `FileAttachmentsSection.tsx` matching Discohook aesthetic:
     * Header with file count e.g. `Files (0/10)` and "+ Add File" button.
     * Drag-and-drop zone.
     * Horizontal scroll / grid of attachment cards with image/doc thumbnail, filename, size, spoiler toggle badge, delete button.
   - In `messageStore.ts`: Keep attachment files in memory (excluded from localStorage `partialize`!).
   - In `src/utils/discord.ts`: Update `isPayloadEmpty` so messages with attachments only are considered valid.
   - In `hooks/useSend.ts`: Route both Bot and Webhook sends with attachments through `/api/send` using `FormData` (`payload_json` + files).

### 3. Verification & Quality Gates
- Run `npm test` in `hoho_manager/server` to ensure all existing tests pass and add unit/integration tests for auth endpoints and multipart file forwarding.
- Run `npm run typecheck` across all packages (`client`, `server`, etc.) ensuring 0 errors.
- Document all changes and verification commands in your handoff report.
- Write your handoff report to `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\worker_m5\handoff.md`.

## 2026-10-04T05:39:00Z
**Context**: Milestone 5 Implementation
**Content**: The user has requested that you also update the documentation files (`docs/DEPLOYMENT.md`, `docs/LOCAL_DEVELOPMENT.md`, `docs/PTERODACTYL_DEPLOYMENT.md`, and `chatwithantigravity.md` / `handoff.md`) to reflect the new Discord OAuth2 login requirements (like new environment variables for Client ID/Secret) and the file attachment features. Please have the worker or a dedicated document reviewer handle this before the milestone is marked complete!
**Action**: Please update these 4 documentation files (`docs/DEPLOYMENT.md`, `docs/LOCAL_DEVELOPMENT.md`, `docs/PTERODACTYL_DEPLOYMENT.md`, and `chatwithantigravity.md`) with the new OAuth2 environment variables (DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DISCORD_REDIRECT_URI, SESSION_SECRET / JWT secret) and file attachment features before delivering your final handoff.
