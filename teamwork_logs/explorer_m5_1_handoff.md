# Handoff Report: Milestone 5 Backend Architecture (Discord OAuth2 & Multipart File Streaming)

- **Author**: `explorer_m5_1` (Backend Auth & File Streaming Explorer)
- **Role**: Backend Architecture Analysis, Discord OAuth2 Flow, and Multipart File Attachment Forwarding
- **Target Location**: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_1\handoff.md`

---

## 1. Observation

### 1.1 Existing Environment & Server Dependencies
1. **Node.js Environment**: The local Node runtime is `v24.13.0` (`node -v`).
   - Native Web Standards: `globalThis.FormData`, `globalThis.Blob`, `globalThis.File`, and `Request.prototype.formData` are all natively available without polyfills.
   - Built-in Crypto: `node:crypto` supports high-performance HMAC-SHA256 and constant-time string comparison (`crypto.timingSafeEqual`).
2. **`hoho_manager/server/package.json`**:
   - Dependencies: `express: ^5.2.1`, `better-sqlite3: ^13.0.3`, `cors: ^2.8.6`, `discord-interactions: ^4.4.0`, `dotenv: ^18.0.4`, `express-rate-limit: ^8.7.0`, `helmet: ^8.3.0`.
   - Workspace dependency: `@dmb/shared: *` (located at `hoho_manager/shared`).
   - `cookie` (`^0.7.2`) and `cookie-signature` (`^1.2.1`) are already present in `node_modules` (resolved via `express` dependencies in `package-lock.json`).
   - Currently, neither `multer` nor `jsonwebtoken` is in `package.json`.
3. **`hoho_manager/server/src/app.ts`**:
   - Lines 48-62: CORS is configured with `credentials: true` and `allowedHeaders: ["Content-Type", "Authorization", "x-admin-key", "x-staff-id"]`. In development (`env.isDev`), any origin is accepted (`callback(null, true)`).
   - Lines 68-73: Global body parsers `express.json()` and `express.urlencoded()` run before API routes. Note: `express.json()` exclusively parses requests where `Content-Type: application/json`; incoming `multipart/form-data` requests bypass it without consuming the request stream.

### 1.2 Current Authentication & Staff Permission Architecture
1. **`hoho_manager/server/src/middleware/auth.ts`**:
   - Lines 50-55:
     ```ts
     export const attachUser: RequestHandler = asyncHandler(async (req, _res, next) => {
       req.user = await userRepository.findByDiscordId("local-admin");
       next();
     });
     ```
     `attachUser` hardcodes `findByDiscordId("local-admin")`, which was put in place as a placeholder for Milestone 1-4.
   - Lines 90-112: `requireHeadAdmin` checks `x-admin-key` against `env.adminApiKey`, or checks `x-staff-id` against `settingsService.isHeadAdmin(staffId)`.
2. **`hoho_manager/server/src/middleware/staffPermissions.ts`**:
   - Line 59: `const staffId = req.get("x-staff-id");`
   - Lines 67-70: If `staffId` matches a Head Admin, it grants admin access.
   - Lines 73-81: If `staffId` is missing, it returns 401.
   - Lines 140-143: Channel allowlist check inspects `req.body?.channelId`.
   - **Vulnerability**: Currently, `x-staff-id` can be spoofed by any HTTP client simply sending another user's Discord snowflake ID.
3. **`hoho_manager/server/src/repositories/userRepository.ts`**:
   - Lines 53-69: `userRepository.upsert({ discordId, username, avatar, role })` is already implemented and uses `INSERT ... ON CONFLICT(discord_id) DO UPDATE`.
4. **`hoho_manager/server/src/config/env.ts`**:
   - Has `env.discord.applicationId` (`1553701585237053450`), `env.discord.botToken`, `env.adminApiKey`.
   - Does NOT currently expose `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, or `DISCORD_REDIRECT_URI`.

### 1.3 Message Send & Discord Forwarding Pipeline
1. **`hoho_manager/server/src/routes/send.ts`**:
   - Line 26: `router.post("/", attachUser, sendLimiter, requireStaffPermission("send"), asyncHandler(async (req, res) => ...))`
   - Line 32: Destructures `{ mode, payload: rawPayload, channelId, webhookUrl, threadId, profileId, editMessageId, ...body } = req.body;`.
   - Line 115: Webhook path: `discord.sendWebhook(webhookUrl, finalMessage, { wait: true, threadId })`.
   - Line 139: Bot path: `discord.sendChannelMessage(channelId, finalMessage, { profileId })` or `discord.editChannelMessage(...)`.
2. **`hoho_manager/server/src/services/discordService.ts`**:
   - Lines 141-217: `apiRequest` executes `fetch` against Discord API with retry logic.
   - Currently, `apiRequest` defaults to `headers["Content-Type"] = "application/json"` and `JSON.stringify(body)`. It has no support for `FormData` or multipart attachments.
3. **Discohook Reference Architecture (`discohook_src/packages/site/app/util/discord.ts:125-144`)**:
   - Discohook constructs `FormData`:
     ```ts
     body = new FormData();
     body.set("payload_json", JSON.stringify(payload));
     for (const { file, key } of options.files) {
       body.append(key ?? `files[${i}]`, file, file.name);
       i++;
     }
     ```
   - Headers: omits `Content-Type` header so that `fetch` automatically computes the boundary string (`multipart/form-data; boundary=...`).
4. **Test Suite Baseline**:
   - `npm test` in `hoho_manager/server`: 21 test files passed, 261 tests passed (100% pass rate).

---

## 2. Logic Chain

### 2.1 Discord OAuth2 Architecture & Zero-Dependency Session Management
- **Observation**: `DISCORD_APPLICATION_ID` (`1553701585237053450`) is already present in `.env`. Node `v24` has built-in `node:crypto`, and `cookie` (`0.7.2`) is present in `node_modules`.
- **Reasoning**:
  1. In Discord Developer applications, `DISCORD_CLIENT_ID` is identical to `DISCORD_APPLICATION_ID`. Setting `DISCORD_CLIENT_ID = env.discord.applicationId` provides a seamless default.
  2. The OAuth2 authorization code grant requires:
     - Authorization URL: `https://discord.com/oauth2/authorize?client_id=${clientId}&response_type=code&redirect_uri=${encodeURIComponent(redirectUri)}&scope=identify`
     - Token Exchange: `POST https://discord.com/api/v10/oauth2/token` with `client_id`, `client_secret`, `grant_type=authorization_code`, `code`, `redirect_uri`.
     - Identity Fetch: `GET https://discord.com/api/v10/users/@me` with `Authorization: Bearer ${accessToken}`.
  3. Instead of introducing heavy external JWT or session store dependencies, we can implement an RFC 7519 compliant signed JWT using `node:crypto` (`createHmac("sha256", env.adminApiKey)`).
     - Token structure: `base64url(header).base64url(payload).base64url(hmacSignature)`.
     - Verification is constant-time (`crypto.timingSafeEqual`) and synchronous (<0.05ms).
     - Payload includes: `{ id: string, username: string, global_name: string | null, avatar: string | null, role: string, exp: number }`.
  4. Session Delivery:
     - Set in an HTTP-only, `SameSite=lax` cookie named `dmb_session` with a 7-day expiration (`maxAge: 7 * 24 * 60 * 60 * 1000`).
     - In development (`env.isDev`), `secure: false`; in production (`env.isProd`), `secure: true`.
     - Also accept `Authorization: Bearer <token>` for API clients/scripts.
  5. Persistence:
     - Upon login, call `userRepository.upsert({ discordId, username, avatar, role })`. If user is Head Admin in DB settings or in `env.ownerDiscordIds`, role is `"admin"`; otherwise `"editor"`.
  6. Endpoints in `src/routes/auth.ts`:
     - `GET /api/auth/discord/login`: Redirects to Discord OAuth authorization URL. In dev mode with missing client secret, provides actionable diagnostic warning.
     - `GET /api/auth/discord/callback`: Exchanges code, fetches user, upserts DB user, sets cookie, redirects to `${clientOrigin}/?login=success`.
     - `GET /api/auth/me`: Reads cookie/bearer token, validates HMAC signature and expiration, returns `{ user: { id, username, global_name, avatar, avatarUrl, role, isAdmin } }` or `{ user: null }`.
     - `POST /api/auth/logout`: Clears cookie via `res.clearCookie("dmb_session", { path: "/" })`, returns `{ success: true }`.
     - `POST /api/auth/dev-login`: Gated to `env.isDev` or test runners; allows setting session for test automation without manual Discord browser clicks.

### 2.2 Anti-Spoofing & Staff Permission Hardening
- **Observation**: `staffPermissions.ts` reads `req.get("x-staff-id")`, allowing an attacker to impersonate any staff member if they know the ID. Furthermore, `staffPermissions.ts:140` inspects `req.body?.channelId`.
- **Reasoning**:
  1. We must introduce a session extractor helper `getSessionUserFromRequest(req)` that decodes and validates the session cookie or Bearer token.
  2. Anti-Spoofing Rule in `staffPermissions.ts`:
     - If an authenticated session is active (`sessionUser` exists):
       - If the client also sent `x-staff-id`, and `x-staff-id !== sessionUser.id`: REJECT with `403 Forbidden` ("Provided x-staff-id does not match authenticated user session") and log an audit security event (`STAFF_SPOOF_ATTEMPT`).
       - If no `x-staff-id` was provided, automatically assign `staffId = sessionUser.id`.
     - If no session is active:
       - Fall back to `req.get("x-staff-id")` (or `x-admin-key`) to maintain 100% backward compatibility with automated test suites and headless API scripts.
  3. In `auth.ts` (`attachUser`):
     - If `sessionUser` exists, resolve `req.user` to `userRepository.findByDiscordId(sessionUser.id)`.
     - If not, fall back to `userRepository.findByDiscordId("local-admin")`.
  4. In `auth.ts` (`requireHeadAdmin`):
     - Caller can satisfy Head Admin via `x-admin-key` OR `sessionUser.id` in Head Admins OR `x-staff-id` (if no session).

### 2.3 Multipart File Streaming with Zero Disk Storage
- **Observation**: Node `v24` natively parses multipart streams into Web Standard `FormData` via `Readable.toWeb(req)` -> `new Request(...)` -> `await webReq.formData()`.
- **Reasoning**:
  1. **Crucial Ordering Requirement**: If multipart parsing were to occur in the route handler of `/api/send`, `requireStaffPermission("send")` would execute first. At that point, `req.body` would be empty because `express.json()` skips multipart requests. The channel allowlist check (`req.body?.channelId`) would evaluate `channelId` as `undefined`!
  2. **Solution**: Create a dedicated `multipartParser` middleware mounted directly on `POST /api/send` before `requireStaffPermission("send")`:
     ```ts
     router.post(
       "/",
       multipartParser,
       attachUser,
       sendLimiter,
       requireStaffPermission("send"),
       asyncHandler(async (req, res) => ...),
     );
     ```
  3. How `multipartParser` works:
     - If `req.headers["content-type"]?.includes("multipart/form-data")`:
       - Constructs web `Request`: `new Request(url, { method: "POST", headers: req.headers, body: Readable.toWeb(req), duplex: "half" })`.
       - Calls `const fd = await webReq.formData();`.
       - Extracts `payload_json = fd.get("payload_json")` and parses JSON into `req.body`.
       - Collects all file entries (`files[0]`, `files[1]`, etc.) into `req.files` in memory.
     - If `req.headers["content-type"]?.includes("application/json")`:
       - Passes through immediately to `next()` (since `express.json()` already parsed `req.body`).
  4. Forwarding to Discord in `discordService.ts`:
     - Both `sendWebhook` and `sendChannelMessage` / `editChannelMessage` accept an optional `files?: Array<{ file: Blob | File; filename: string; key?: string }>`.
     - When `files && files.length > 0`:
       - Construct outgoing Discord `FormData`:
         ```ts
         const discordForm = new FormData();
         discordForm.append("payload_json", JSON.stringify(bodyPayload));
         for (let i = 0; i < files.length; i++) {
           discordForm.append(files[i].key ?? `files[${i}]`, files[i].file, files[i].filename);
         }
         ```
       - `apiRequest` sends `body: discordForm` without setting `Content-Type` (allowing Node `fetch` to automatically format the boundary header), while retaining `Authorization: Bot <token>` (for bot messages).
  5. Disk Storage: **0 bytes written to disk**. The buffers exist strictly in RAM during HTTP execution and are immediately freed upon Discord API response.

---

## 3. Caveats

1. **Discord Client Secret Configuration**:
   - The user must register a Redirect URI in the Discord Developer Portal under OAuth2: `http://localhost:3001/api/auth/discord/callback` (or their production domain).
   - In dev environments where `DISCORD_CLIENT_SECRET` is not yet configured, the server must not crash. We provide a dev fallback route (`POST /api/auth/dev-login`) and user-friendly error messages on `/login`.
2. **Discord Upload Size Limits**:
   - Standard Discord bots can upload files up to 25 MB per request. Nitro boosted servers allow up to 100 MB.
   - We should enforce a defensive limit (e.g., 25 MB total or per file in memory) to prevent Denial of Service via memory bloat.
3. **Cross-Origin Cookie Propagation**:
   - When frontend (`localhost:5173`) calls backend (`localhost:3001`), `fetch` calls must set `credentials: "include"` for the browser to send the `dmb_session` cookie.
   - Express CORS is already configured with `credentials: true`.
4. **No other uninvestigated areas**: Full backend codebase, middleware, routes, services, and shared types were directly reviewed.

---

## 4. Conclusion & Actionable Blueprint

### 4.1 Recommended Implementation Plan

#### Step 1: Update `@dmb/shared` Types (`hoho_manager/shared/src/types.ts`)
Add the following interfaces:
```ts
export interface DiscordAttachmentPayload {
  id: number | string;
  filename: string;
  description?: string;
  content_type?: string;
  size?: number;
  url?: string;
}

export interface AuthUserProfile {
  id: string;
  username: string;
  global_name: string | null;
  avatar: string | null;
  avatarUrl?: string;
  role: string;
  isAdmin: boolean;
}

export interface AuthMeResponse {
  user: AuthUserProfile | null;
}
```
Update `DiscordMessagePayload`:
```ts
export interface DiscordMessagePayload {
  content?: string | null;
  embeds?: EmbedData[] | null;
  components?: ComponentNode[];
  username?: string;
  avatar_url?: string;
  thread_name?: string;
  flags?: number;
  allowed_mentions?: { parse?: string[]; roles?: string[]; users?: string[] };
  attachments?: DiscordAttachmentPayload[];
}
```
Update `SendRequestBody`:
```ts
export interface SendRequestBody {
  mode: SendMode;
  payload: DiscordMessagePayload;
  channelId?: string;
  webhookUrl?: string;
  profileId?: number | null;
  threadId?: string;
  editMessageId?: string;
  flows?: FlowRegistration[];
  attachments?: DiscordAttachmentPayload[];
}
```

#### Step 2: Environment Configuration (`hoho_manager/server/src/config/env.ts`)
Add to `DiscordEnv`:
```ts
export interface DiscordEnv {
  readonly publicKey: string | undefined;
  readonly applicationId: string | undefined;
  readonly botToken: string | undefined;
  readonly clientId: string | undefined;
  readonly clientSecret: string | undefined;
  readonly redirectUri: string;
}
```
In `env` object:
```ts
discord: Object.freeze({
  publicKey: str("DISCORD_PUBLIC_KEY"),
  applicationId: str("DISCORD_APPLICATION_ID"),
  botToken: str("DISCORD_BOT_TOKEN"),
  clientId: str("DISCORD_CLIENT_ID", str("DISCORD_APPLICATION_ID")),
  clientSecret: str("DISCORD_CLIENT_SECRET"),
  redirectUri: str("DISCORD_REDIRECT_URI", "http://localhost:3001/api/auth/discord/callback")!,
}),
sessionSecret: str("SESSION_SECRET", str("ADMIN_API_KEY", "dev-session-secret")),
```

#### Step 3: Session Service (`hoho_manager/server/src/utils/session.ts`)
A clean, zero-dependency session token generator and validator:
```ts
import crypto from "node:crypto";
import type { Request } from "express";
import * as cookie from "cookie";
import { env } from "../config/env.js";

export interface SessionUser {
  id: string;
  username: string;
  global_name?: string | null;
  avatar?: string | null;
  role: string;
}

const getSecret = (): string => env.adminApiKey || "default-session-secret";

export const createSessionToken = (user: SessionUser): string => {
  const header = Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString("base64url");
  const payload = Buffer.from(
    JSON.stringify({
      ...user,
      exp: Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60, // 7 days
      iat: Math.floor(Date.now() / 1000),
    })
  ).toString("base64url");
  const sig = crypto.createHmac("sha256", getSecret()).update(`${header}.${payload}`).digest("base64url");
  return `${header}.${payload}.${sig}`;
};

export const verifySessionToken = (token: string): SessionUser | null => {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const [h, p, s] = parts;
    const expected = crypto.createHmac("sha256", getSecret()).update(`${h}.${p}`).digest("base64url");
    const bufA = Buffer.from(s);
    const bufB = Buffer.from(expected);
    if (bufA.length !== bufB.length || !crypto.timingSafeEqual(bufA, bufB)) return null;

    const data = JSON.parse(Buffer.from(p, "base64url").toString("utf8"));
    if (data.exp && data.exp < Math.floor(Date.now() / 1000)) return null;
    return {
      id: data.id,
      username: data.username,
      global_name: data.global_name ?? null,
      avatar: data.avatar ?? null,
      role: data.role ?? "editor",
    };
  } catch {
    return null;
  }
};

export const getSessionUserFromRequest = (req: Request): SessionUser | null => {
  const header = req.headers.cookie;
  if (header) {
    const cookies = cookie.parse(header);
    if (cookies.dmb_session) {
      const user = verifySessionToken(cookies.dmb_session);
      if (user) return user;
    }
  }

  const authHeader = req.get("authorization");
  if (authHeader && authHeader.startsWith("Bearer ")) {
    const token = authHeader.slice(7).trim();
    const user = verifySessionToken(token);
    if (user) return user;
  }

  return null;
};
```

#### Step 4: Discord OAuth2 Routes (`hoho_manager/server/src/routes/auth.ts`)
```ts
import { Router } from "express";
import crypto from "node:crypto";
import { env } from "../config/env.js";
import { userRepository } from "../repositories/userRepository.js";
import { settingsService } from "../services/settingsService.js";
import { createSessionToken, getSessionUserFromRequest } from "../utils/session.js";
import { ApiError, asyncHandler } from "../utils/errors.js";
import { logger } from "../utils/logger.js";

const router = Router();
const log = logger.child("auth");

// GET /api/auth/discord/login
router.get("/discord/login", (req, res) => {
  if (!env.discord.clientSecret && env.isProd) {
    throw ApiError.upstream("DISCORD_CLIENT_SECRET is not configured on the server");
  }

  const state = crypto.randomBytes(16).toString("hex");
  res.cookie("oauth_state", state, {
    httpOnly: true,
    secure: env.isProd,
    sameSite: "lax",
    maxAge: 10 * 60 * 1000,
    path: "/",
  });

  const params = new URLSearchParams({
    client_id: env.discord.clientId || env.discord.applicationId || "",
    response_type: "code",
    redirect_uri: env.discord.redirectUri,
    scope: "identify",
    state,
  });

  res.redirect(`https://discord.com/oauth2/authorize?${params.toString()}`);
});

// GET /api/auth/discord/callback
router.get(
  "/discord/callback",
  asyncHandler(async (req, res) => {
    const { code, state, error, error_description } = req.query;
    if (error) {
      log.warn(`OAuth error: ${error} - ${error_description}`);
      return res.redirect(`${env.clientOrigins[0]}/?error=${encodeURIComponent(String(error_description || error))}`);
    }
    if (!code || typeof code !== "string") {
      throw ApiError.badRequest("Authorization code is required");
    }

    const tokenRes = await fetch("https://discord.com/api/v10/oauth2/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: env.discord.clientId || env.discord.applicationId || "",
        client_secret: env.discord.clientSecret || "",
        grant_type: "authorization_code",
        code,
        redirect_uri: env.discord.redirectUri,
      }),
    });

    if (!tokenRes.ok) {
      const errBody = await tokenRes.text();
      log.error(`Discord token exchange failed: ${errBody}`);
      return res.redirect(`${env.clientOrigins[0]}/?error=token_exchange_failed`);
    }

    const tokenData = (await tokenRes.json()) as { access_token: string };

    const userRes = await fetch("https://discord.com/api/v10/users/@me", {
      headers: { Authorization: `Bearer ${tokenData.access_token}` },
    });

    if (!userRes.ok) {
      return res.redirect(`${env.clientOrigins[0]}/?error=fetch_user_failed`);
    }

    const discordUser = (await userRes.json()) as {
      id: string;
      username: string;
      global_name?: string | null;
      avatar?: string | null;
    };

    const isHead = await settingsService.isHeadAdmin(discordUser.id);
    const isOwner = env.ownerDiscordIds.includes(discordUser.id);
    const role = isHead || isOwner ? "admin" : "editor";

    await userRepository.upsert({
      discordId: discordUser.id,
      username: discordUser.global_name || discordUser.username,
      avatar: discordUser.avatar,
      role,
    });

    const sessionUser = {
      id: discordUser.id,
      username: discordUser.global_name || discordUser.username,
      global_name: discordUser.global_name ?? null,
      avatar: discordUser.avatar ?? null,
      role,
    };

    const sessionToken = createSessionToken(sessionUser);

    res.cookie("dmb_session", sessionToken, {
      httpOnly: true,
      secure: env.isProd,
      sameSite: "lax",
      maxAge: 7 * 24 * 60 * 60 * 1000,
      path: "/",
    });

    res.clearCookie("oauth_state", { path: "/" });
    res.redirect(`${env.clientOrigins[0]}/?login=success`);
  })
);

// GET /api/auth/me
router.get(
  "/me",
  asyncHandler(async (req, res) => {
    const user = getSessionUserFromRequest(req);
    if (!user) return res.json({ user: null });

    const isHead = await settingsService.isHeadAdmin(user.id);
    const isOwner = env.ownerDiscordIds.includes(user.id);
    const isAdmin = isHead || isOwner || user.role === "admin";

    const avatarUrl = user.avatar
      ? `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png`
      : `https://cdn.discordapp.com/embed/avatars/${(BigInt(user.id) >> 22n) % 6n}.png`;

    res.json({
      user: {
        id: user.id,
        username: user.username,
        global_name: user.global_name,
        avatar: user.avatar,
        avatarUrl,
        role: user.role,
        isAdmin,
      },
    });
  })
);

// POST /api/auth/logout
router.post("/logout", (_req, res) => {
  res.clearCookie("dmb_session", { path: "/" });
  res.json({ success: true, ok: true });
});

// POST /api/auth/dev-login (dev/test only)
router.post(
  "/dev-login",
  asyncHandler(async (req, res) => {
    if (!env.isDev) throw ApiError.notFound();
    const { discordId, username, avatar } = req.body;
    if (!discordId || typeof discordId !== "string") throw ApiError.badRequest("discordId required");

    const isHead = await settingsService.isHeadAdmin(discordId);
    const role = isHead || env.ownerDiscordIds.includes(discordId) ? "admin" : "editor";

    await userRepository.upsert({
      discordId,
      username: username || `User_${discordId.slice(-4)}`,
      avatar: avatar || null,
      role,
    });

    const sessionUser = {
      id: discordId,
      username: username || `User_${discordId.slice(-4)}`,
      global_name: username || null,
      avatar: avatar || null,
      role,
    };

    const token = createSessionToken(sessionUser);
    res.cookie("dmb_session", token, {
      httpOnly: true,
      secure: false,
      sameSite: "lax",
      maxAge: 7 * 24 * 60 * 60 * 1000,
      path: "/",
    });

    res.json({ ok: true, user: sessionUser, token });
  })
);

export default router;
```

#### Step 5: Multipart Parser Middleware (`hoho_manager/server/src/middleware/multipart.ts`)
```ts
import type { Request, Response, NextFunction } from "express";
import { Readable } from "node:stream";
import { ApiError } from "../utils/errors.js";

export interface UploadedFile {
  key: string;
  filename: string;
  size: number;
  type: string;
  file: File | Blob;
}

export const multipartParser = async (req: Request, _res: Response, next: NextFunction) => {
  const contentType = req.headers["content-type"] || "";
  if (!contentType.includes("multipart/form-data")) {
    return next();
  }

  try {
    const webReq = new Request(`http://${req.headers.host || "localhost"}${req.url}`, {
      method: req.method,
      headers: req.headers as HeadersInit,
      body: Readable.toWeb(req),
      duplex: "half",
    });

    const formData = await webReq.formData();
    const payloadJsonStr = formData.get("payload_json");

    if (typeof payloadJsonStr === "string") {
      req.body = JSON.parse(payloadJsonStr);
    } else {
      req.body = {};
    }

    const files: UploadedFile[] = [];
    let i = 0;
    for (const [key, value] of formData.entries()) {
      if (typeof value === "object" && "name" in value && "size" in value) {
        const fileObj = value as File;
        files.push({
          key: key.startsWith("files[") ? key : `files[${i}]`,
          filename: fileObj.name,
          size: fileObj.size,
          type: fileObj.type,
          file: fileObj,
        });
        i++;
      }
    }

    (req as any).uploadedFiles = files;
    next();
  } catch (err) {
    next(ApiError.badRequest(`Failed to parse multipart/form-data: ${err instanceof Error ? err.message : String(err)}`));
  }
};
```

#### Step 6: Update `staffPermissions.ts` and `auth.ts`
In `staffPermissions.ts`:
```ts
const sessionUser = getSessionUserFromRequest(req);
const headerStaffId = req.get("x-staff-id");

// Anti-spoofing enforcement
if (sessionUser && headerStaffId && headerStaffId !== sessionUser.id) {
  auditLog({
    event: "STAFF_ACCESS_DENIED",
    actorDiscordId: sessionUser.id,
    reason: `Spoofing attempt: claimed ${headerStaffId} but authenticated as ${sessionUser.id}`,
    ip,
    requestId,
  });
  return next(ApiError.forbidden("Provided x-staff-id does not match authenticated user session"));
}

const staffId = sessionUser?.id ?? headerStaffId;
```
In `auth.ts` (`requireHeadAdmin`):
```ts
const sessionUser = getSessionUserFromRequest(req);
const staffId = sessionUser?.id ?? req.get("x-staff-id");
```

#### Step 7: Update `discordService.ts` for Outbound Multipart Forwarding
Update `apiRequest`:
```ts
interface ApiRequestOptions {
  body?: unknown;
  files?: Array<{ file: Blob | File; filename: string; key?: string }>;
  token?: string;
  auth?: string;
  retries?: number;
  absoluteUrl?: string;
}
```
In `apiRequest`:
```ts
let bodyToSend: BodyInit | undefined;
const headers: Record<string, string> = {};
if (token) headers.Authorization = `${auth} ${token}`;

if (files && files.length > 0) {
  const formData = new FormData();
  formData.append("payload_json", JSON.stringify(body ?? {}));
  for (let i = 0; i < files.length; i++) {
    formData.append(files[i].key ?? `files[${i}]`, files[i].file, files[i].filename);
  }
  bodyToSend = formData;
  // NOTE: do NOT set Content-Type header; fetch sets boundary automatically!
} else {
  headers["Content-Type"] = "application/json";
  bodyToSend = body === undefined ? undefined : JSON.stringify(body);
}

response = await fetch(url, {
  method,
  headers,
  body: bodyToSend,
});
```

---

## 5. Verification Method

1. **Server Unit & E2E Tests**:
   - Run: `npm test` in `hoho_manager/server`.
   - Invalidation condition: Any existing test failure across the 21 test files.
2. **TypeScript Typecheck**:
   - Run: `npm run typecheck` across all workspaces (`hoho_manager/shared`, `hoho_manager/server`, `hoho_manager/client`).
   - Invalidation condition: Any TypeScript compiler error or missing property.
3. **Multipart Send Verification**:
   - Execute test script sending `multipart/form-data` with `payload_json` and file blob to `POST /api/send`.
   - Verify `req.body.channelId` is parsed and checked by `requireStaffPermission`, and file is received as `FormData` by Discord mock without writing to disk.
4. **Anti-Spoofing Verification**:
   - Issue request with valid session token for User A, but send header `x-staff-id: User B`.
   - Verify HTTP 403 Forbidden is returned and `STAFF_ACCESS_DENIED` audit log is triggered.
5. **Discord OAuth Session Verification**:
   - Request `GET /api/auth/me` with session cookie; verify user profile response with avatar URL.
   - Request `POST /api/auth/logout`; verify cookie is cleared and subsequent `/me` returns `{ user: null }`.
