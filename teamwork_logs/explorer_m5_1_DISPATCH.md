# DISPATCH — explorer_m5_1

## Identity
- Role: Backend Auth & File Streaming Explorer
- Working directory: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_1\
- Archetype: teamwork_preview_explorer

## Mission
Investigate the backend architecture for Milestone 5 (Discord OAuth2 Login and File Attachments) in `hoho_manager/server`.

## Context & Inputs
- User Request: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\ORIGINAL_REQUEST.md
- Project Scope: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\orchestrator_5\SCOPE.md
- Project Plan: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\PROJECT.md

## Detailed Tasks
1. Inspect `hoho_manager/server/` dependencies (`package.json`), server entry (`src/server.ts`), routes (`src/routes/`), middleware (`src/middleware/auth.ts`, `staffPermissions.ts`), and config (`src/config/`).
2. Plan the Discord OAuth2 implementation:
   - Configuration needed (`DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `DISCORD_REDIRECT_URI`) in env/settings.
   - Endpoints: `GET /api/auth/discord/login` (redirects to Discord authorization URL), `GET /api/auth/discord/callback` (exchanges code for token, gets `/@me` user profile).
   - Session management: How to securely issue an HTTP-only session cookie or signed JWT containing user ID, username, avatar. Check if `cookie-parser` or JWT packages are installed or what lightweight approach fits.
   - Endpoint: `GET /api/auth/me` to return the logged-in user profile, and `POST /api/auth/logout`.
   - Update `staffPermissions.ts` and `auth.ts` to inspect this session cookie/JWT and set authenticated user ID so staff checks can't be spoofed.
3. Plan `/api/send` multipart file handling:
   - How `/api/send` currently handles sends (webhook vs bot token).
   - How `/api/send` can accept `multipart/form-data` with `payload_json` and file buffers (e.g. `multer` memory storage or custom parser) with zero permanent disk storage.
   - How to construct `FormData` to forward files and `payload_json` to Discord API (webhook execution or channel create message).
4. Identify any TypeScript type changes needed in `packages/shared`.
5. Deliver a comprehensive report with concrete file paths, code snippets, interface designs, and step-by-step implementation plan.
6. Write your report to `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_1\handoff.md`.

## 2026-10-04T04:51:11Z
You are explorer_m5_1.
Working directory: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_1\
Read your instructions in: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_1\DISPATCH.md
Read the user's original request: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\ORIGINAL_REQUEST.md
Read the project overview: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\PROJECT.md
Read the milestone scope: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\orchestrator_5\SCOPE.md

Your role is Backend Auth & File Streaming Explorer.
Investigate hoho_manager/server backend architecture for Discord OAuth2 Login and Multipart File Attachments streaming forwarding to Discord API.
Perform your investigation, synthesize your findings and actionable implementation recommendations, and write your report to C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_1\handoff.md.
When finished, notify your parent with send_message including your handoff report path.
