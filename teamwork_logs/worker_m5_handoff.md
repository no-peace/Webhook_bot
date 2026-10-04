# Handoff Report — worker_m5 (Milestone 5)

## 1. Observation
- **Scope & Mission**: Milestone 5: Discord OAuth2 Login and File Attachments across backend (`hoho_manager/server`) and frontend (`hoho_manager/client`), plus updating project documentation (`docs/DEPLOYMENT.md`, `docs/LOCAL_DEVELOPMENT.md`, `docs/PTERODACTYL_DEPLOYMENT.md`, and `chatwithantigravity.md`).
- **Shared Types (`hoho_manager/shared/src/types.ts`)**:
  - Added `DiscordAttachmentPayload`, `AuthUserProfile`, `AuthMeResponse`.
  - Updated `SendRequestBody` with `attachments?: DiscordAttachmentPayload[]` and `editMessageId?: string`.
- **Backend Auth & Session Management (`hoho_manager/server`)**:
  - `src/config/env.ts`: Extracted `clientId`, `clientSecret`, `redirectUri`, `sessionSecret` (defaulting to `adminApiKey`).
  - `src/utils/session.ts`: Built RFC 7519 HMAC-SHA256 session token generator, signature validator, and cookie parser using Node 24 native `node:crypto`.
  - `src/routes/auth.ts`: Implemented `GET /api/auth/discord/login`, `GET /api/auth/discord/callback`, `GET /api/auth/me`, `POST /api/auth/logout`, `POST /api/auth/dev-login`. Mounted at `/api/auth` in `src/app.ts`.
  - `src/middleware/auth.ts`: Updated `attachUser` and `requireHeadAdmin` to recognise authenticated session users while preserving local-admin fallback.
  - `src/middleware/staffPermissions.ts`: Anti-spoofing mechanism implemented. If session user exists, enforces `staffId = sessionUser.id`. Rejects conflicting `x-staff-id` with `403 Forbidden`. Gracefully falls back to headers when unauthenticated.
- **Backend Multipart & File Forwarding (`hoho_manager/server`)**:
  - `src/middleware/multipart.ts`: Node 24 Web Standards in-memory multipart parser via `Readable.toWeb(req)` -> `new Request(...)` -> `webReq.formData()`. Zero disk storage footprint!
  - `src/routes/send.ts`: Mounted `multipartParser` before `attachUser` and `requireStaffPermission("send")`. Forwards `uploadedFiles` to `discordService`.
  - `src/services/discordService.ts`: Updated `apiRequest` to support `body instanceof FormData` (omits `Content-Type` for boundary generation). Updated `sendWebhook`, `sendChannelMessage`, and `editChannelMessage` to forward attachments with `payload_json` and `files[i]`.
- **Backend Verification**:
  - Created `src/routes/auth.test.ts` with 8 comprehensive integration/unit tests.
  - Full server test run: `22 passed (22 test suites), 269 passed (269 tests)` with 100% pass rate.
- **Frontend State & Components (`hoho_manager/client`)**:
  - `src/store/globalStore.ts`: Added `currentUser`, `authLoading`, `setCurrentUser`, `fetchCurrentUser()`, and `logout()`.
  - `src/api/client.ts`: Added `credentials: "include"` on all requests, dynamic staff ID resolution, `FormData` transmission without manual `Content-Type` override, `api.auth.me()`, `api.auth.logout()`, and `api.send(body: SendRequestBody | FormData)`.
  - `src/App.tsx`: Auto-hydrates `fetchCurrentUser()` on mount and cleans `?login=success` URL search params.
  - `src/components/layout/Header.tsx`: Integrated Discord Blurple login button, user avatar fallback `(BigInt(id) >> 22n) % 6n`, and Discohook `#1e1f22` user profile dropdown menu (copyable snowflake ID, role badge, staff access shortcut, logout).
  - `src/components/layout/AccessPanel.tsx`: Added Authenticated Operator card, "Grant to Myself" button in create form, and `(You)` badge on staff rows.
  - `src/store/messageStore.ts`: Added `AttachedFile` interface, file actions (`addFiles`, `removeFile`, `toggleFileSpoiler`, `updateFileDescription`, `clearFiles`), object URL revocation on remove/reset, and ensured exclusion from `partialize`.
  - `src/utils/discord.ts`: Updated `isPayloadEmpty(payload, hasAttachments)` to permit attachment-only messages.
  - `src/hooks/useMessage.ts`: Subscribed to `attachedFiles` and passed `hasAttachments` into `isPayloadEmpty`.
  - `src/components/editor/FileAttachmentsSection.tsx`: Discohook `#1e1f22` accordion, drag & drop zone, thumbnail cards (images, video, audio, docs), spoiler toggle overlay, and size limits (10 files, 25MB each).
  - `src/components/editor/MessageEditor.tsx`: Mounted `FileAttachmentsSection` in both Classic and Components V2 modes.
  - `src/hooks/useSend.ts` & `src/components/send/BotDispatchModal.tsx`: Updated send handlers to package `FormData` with `payload_json` and `files[i]` when `attachedFiles.length > 0`, dispatching via `api.send(formData)`.
  - `src/components/preview/EmbedPreview.tsx`: Added `resolveAttachmentUrl` resolving `attachment://filename.png` references to in-memory preview object URLs.
  - `src/components/preview/MessagePreview.tsx`: Rendered live attachment preview block with interactive spoiler blur toggle.
- **Frontend Verification**:
  - Created `tests/milestone5_auth_attachments.test.ts` covering store state, payload validation, auth store, and API multipart handling.
  - Full client test run: `14 passed (14 test suites), 217 passed (217 tests)` with 100% pass rate.
  - Workspace typecheck: `npm run typecheck` across `@dmb/shared`, `server`, `client`, and `bot` exited with code 0 (0 errors).
- **Documentation Updates**:
  - `docs/DEPLOYMENT.md`: Added `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `DISCORD_REDIRECT_URI`, `SESSION_SECRET`, Discord Developer Portal OAuth2 setup, and file attachments streaming overview.
  - `docs/LOCAL_DEVELOPMENT.md`: Added local OAuth2 variables, `/api/auth/dev-login` instructions, and file attachment specifications.
  - `docs/PTERODACTYL_DEPLOYMENT.md`: Added container environment variables for OAuth2, public tunnel notes, and memory-only attachment handling.
  - `chatwithantigravity.md`: Added Section 6 covering the Milestone 5 OAuth2 and File Attachments system architecture.

## 2. Logic Chain
1. **Zero-Disk Multipart Forwarding**:
   - Node 24 native web streams allow converting incoming Node HTTP streams to Web standard `Request` objects via `Readable.toWeb(req)`.
   - Calling `await webReq.formData()` parses the multipart stream directly into memory buffers without ever writing temporary files to the local file system.
   - Forwarding to Discord via `fetch(..., { body: formData })` without setting `Content-Type` allows the runtime to generate the proper multipart boundary string, meeting Discord's multipart form specifications.
2. **Session Security & Anti-Spoofing**:
   - Authenticated sessions write a signed `dmb_session` cookie containing user snowflake ID, username, and issued-at timestamp using HMAC-SHA256.
   - In `staffPermissions.ts`, the presence of an active session forces `staffId = sessionUser.id`.
   - If an attacker attempts to spoof permissions by supplying an `x-staff-id` header that differs from `sessionUser.id`, the server immediately halts the request with `403 Forbidden`.
   - Unauthenticated callers (such as existing unit tests or headless bot workers) continue using `x-staff-id` and `x-admin-key`, ensuring 100% backwards compatibility without compromising session integrity.
3. **Zustand State Isolation**:
   - Browser `File` and `Blob` instances throw errors or serialize to empty objects `{}` when passed through JSON serialization in `localStorage`.
   - By omitting `attachedFiles` from `partialize` in `messageStore.ts`, the files remain in React memory during the user's active session while persisted message data remains clean.
4. **Live Discord Attachment Resolution**:
   - Discord embeds support `attachment://filename.png` for images and thumbnails.
   - `EmbedPreview.tsx` intercepts image and thumbnail URLs matching `attachment://` and maps them to `previewUrl` (created via `URL.createObjectURL`), allowing live previews of embedded images before sending.

## 3. Caveats
- Discord limits messages to at most 10 file attachments and 25 MB per file (or up to server boost limit of 50 MB / 100 MB). The client enforces 10 files and 25 MB by default.
- For local development without a registered Discord Application, developers can use `POST /api/auth/dev-login` to issue an active session cookie or continue using the `x-admin-key` header.

## 4. Conclusion
Milestone 5 is completely implemented, verified, and documented across the entire codebase. All quality gates pass:
- Server tests: 269/269 passing (22 test suites).
- Client tests: 217/217 passing (14 test suites).
- Monorepo typecheck: 0 errors across `@dmb/shared`, `server`, `client`, and `bot`.
- Documentation updated across all 4 requested deployment and architecture guides.

## 5. Verification Method
Run the following commands in the workspace:
1. `npm run typecheck` in `hoho_manager` (confirms 0 TypeScript errors across all 4 packages).
2. `npm test` in `hoho_manager/server` (confirms all 269 server tests pass).
3. `npm test` in `hoho_manager/client` (confirms all 217 client tests pass).
