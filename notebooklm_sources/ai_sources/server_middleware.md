# Repository Context Group: server_middleware
# Source Repository: no-peace/Hoho_manager

### File: `server/src/middleware/auth.ts`
```ts
import crypto from "node:crypto";
import type { Request, RequestHandler } from "express";
import type { UserRecord, UserRole } from "@dmb/shared";
import { env } from "../config/env.js";
import { userRepository } from "../repositories/userRepository.js";
import { ApiError, asyncHandler } from "../utils/errors.js";

/**
 * Access control.
 *
 * The app is single-user/local today, but every privileged route already goes
 * through real middleware, so swapping in sessions/JWT in Phase 4 is a change to
 * this file only — not to the routes.
 *
 * Two independent checks are supported:
 *   1. {@link attachUser} / {@link requireRole} — role-based.
 *   2. {@link requireAdminKey} — a shared secret header, used for machine callers
 *      and as a stopgap until logins exist.
 */

/** Constant-time string comparison so we don't leak the secret via timing. */
const safeEqual = (a: unknown, b: unknown): boolean => {
  const bufA = Buffer.from(String(a ?? ""));
  const bufB = Buffer.from(String(b ?? ""));
  if (bufA.length !== bufB.length) return false;
  return crypto.timingSafeEqual(bufA, bufB);
};

/**
 * The acting user, guaranteed.
 *
 * `req.user` is optional by type because not every route attaches one. Calling
 * this in a handler that is preceded by `attachUser` narrows it once, instead of
 * sprinkling non-null assertions through the route bodies.
 *
 * @throws ApiError 401 when no user was attached.
 */
export const requireUser = (req: Request): UserRecord => {
  if (!req.user) throw ApiError.unauthorized();
  return req.user;
};

/**
 * Resolve the acting user onto `req.user`.
 *
 * Phase 4 replaces the body of this function with a session/JWT lookup; the
 * routes downstream only ever read `req.user`.
 */
export const attachUser: RequestHandler = asyncHandler(async (req, _res, next) => {
  req.user = await userRepository.findByDiscordId("local-admin");
  // Must hand off explicitly: without this the router never reaches the
  // handler and the request hangs until the client times out.
  next();
});

/** Gate a route behind one or more roles. Always used after {@link attachUser}. */
export const requireRole =
  (...roles: readonly UserRole[]): RequestHandler =>
  (req, _res, next) => {
    if (!req.user) return next(ApiError.unauthorized());

    // An 'admin' implicitly satisfies every role check.
    const allowed = req.user.role === "admin" || roles.includes(req.user.role);
    if (!allowed) {
      return next(ApiError.forbidden(`Requires role: ${roles.join(" or ")}`));
    }
    return next();
  };

/** Alias for the most common case. */
export const requireAdmin: RequestHandler = requireRole("admin");

/**
 * Require the shared `x-admin-key` header. Used for privileged machine-to-machine
 * calls (e.g. sending with a bot token while no login session exists yet).
 */
export const requireAdminKey: RequestHandler = (req, _res, next) => {
  const provided = req.get("x-admin-key");
  if (!provided || !safeEqual(provided, env.adminApiKey)) {
    return next(ApiError.unauthorized("A valid x-admin-key header is required"));
  }
  return next();
};

```

### File: `server/src/middleware/errorHandler.ts`
```ts
import type { NextFunction, Request, RequestHandler, Response } from "express";
import { env } from "../config/env.js";
import { ApiError } from "../utils/errors.js";
import { logger } from "../utils/logger.js";

/**
 * Terminal middleware.
 *
 * `notFoundHandler` runs when no route matched; `errorHandler` runs whenever
 * `next(err)` is called. Both always respond with the same JSON envelope:
 *
 *   { error: string, code: string, details?: unknown }
 */

interface ErrorBody {
  error: string;
  code: string;
  details?: unknown;
  stack?: string;
}

export const notFoundHandler: RequestHandler = (req, res) => {
  res.status(404).json({
    error: `No route matches ${req.method} ${req.originalUrl}`,
    code: "not_found",
  });
};

// The 4-argument signature is how Express identifies error middleware, so
// `_next` cannot be removed even though it is unused.
export const errorHandler = (
  error: unknown,
  req: Request,
  res: Response,
  _next: NextFunction,
): void => {
  const isApiError = error instanceof ApiError;
  const status = isApiError ? error.status : 500;
  const message = error instanceof Error ? error.message : String(error);

  // Only 5xx are worth a full stack trace; 4xx are routine client mistakes.
  if (status >= 500) {
    const stack = error instanceof Error ? error.stack : undefined;
    logger.error(`${req.method} ${req.originalUrl} failed: ${message}`, stack);
  } else {
    logger.debug(`${req.method} ${req.originalUrl} -> ${status}: ${message}`);
  }

  const body: ErrorBody = {
    error: isApiError && error.expose ? error.message : "Internal server error",
    code: isApiError ? error.code : "internal_error",
  };

  if (isApiError && error.details !== undefined) body.details = error.details;
  // Include the stack only in development to speed up debugging.
  if (env.isDev && status >= 500 && error instanceof Error) body.stack = error.stack;

  res.status(status).json(body);
};

```

### File: `server/src/middleware/rateLimit.ts`
```ts
import type { Request, RequestHandler, Response } from "express";
import rateLimit, { ipKeyGenerator } from "express-rate-limit";
import { env } from "../config/env.js";

/**
 * Rate limiting.
 *
 * Two limiters are exported:
 *   - {@link apiLimiter}  general ceiling for the whole `/api` surface
 *   - {@link sendLimiter} tighter budget for `/api/send`, which talks to Discord
 *
 * `/api/interactions` is deliberately unbounded: Discord retries failed
 * interaction deliveries, and throttling them would drop real user clicks.
 */

const json429 = (_req: Request, res: Response): void => {
  res.status(429).json({
    error: "Too many requests",
    code: "rate_limited",
    retryAfterMs: env.rateLimit.windowMs,
  });
};

export const apiLimiter: RequestHandler = rateLimit({
  windowMs: env.rateLimit.windowMs,
  limit: env.rateLimit.max,
  standardHeaders: "draft-7",
  legacyHeaders: false,
  handler: json429,
  // Skip entirely in tests so suites never flake on the limiter.
  skip: () => env.nodeEnv === "test",
});

export const sendLimiter: RequestHandler = rateLimit({
  windowMs: env.rateLimit.windowMs,
  limit: Math.max(10, Math.floor(env.rateLimit.max / 2)),
  standardHeaders: "draft-7",
  legacyHeaders: false,
  handler: json429,
  // `ipKeyGenerator` normalises IPv6 addresses to a /64 prefix; without it,
  // anyone with an IPv6 allocation could sidestep the limit by rotating the
  // host portion of their address.
  keyGenerator: (req: Request): string => req.user?.discord_id ?? ipKeyGenerator(req.ip ?? ""),
  skip: () => env.nodeEnv === "test",
});

```

### File: `server/src/middleware/verifyDiscordSignature.ts`
```ts
import crypto from "node:crypto";
import type { Request, RequestHandler } from "express";
import type { DiscordInteraction } from "@dmb/shared";
import { env } from "../config/env.js";
import { ApiError } from "../utils/errors.js";
import { logger } from "../utils/logger.js";

const log = logger.child("interactions");

export const requireInteraction = (req: Request): DiscordInteraction => {
  if (!req.interaction) {
    throw ApiError.unauthorized("No verified interaction on this request");
  }
  return req.interaction;
};

export const verifyDiscordSignature: RequestHandler = (req, res, next) => {
  const publicKeyHex = env.discord.publicKey?.trim();
  if (!publicKeyHex) {
    res.status(503).json({ error: "Interaction endpoint is not configured" });
    return;
  }

  const signatureHex = req.get("X-Signature-Ed25519")?.trim();
  const timestampStr = req.get("X-Signature-Timestamp")?.trim();
  
  if (!signatureHex || !timestampStr) {
    res.status(401).json({ error: "Missing signature headers" });
    return;
  }

  // 1. Natively capture the raw HTTP stream, completely bypassing Express parsers
  const chunks: Buffer[] = [];
  req.on("data", (chunk) => chunks.push(chunk));
  
  req.on("end", () => {
    const rawBody = Buffer.concat(chunks);
    
    // 2. Mathematically bind the timestamp and exact pristine bytes
    const messageBuffer = Buffer.concat([
      Buffer.from(timestampStr, "utf-8"),
      rawBody
    ]);

    // 3. Verify natively using the C++ engine
    let valid = false;
    try {
      const publicKeyPem = crypto.createPublicKey({
        key: Buffer.concat([
          Buffer.from("302a300506032b6570032100", "hex"),
          Buffer.from(publicKeyHex, "hex")
        ]),
        format: "der",
        type: "spki"
      });

      valid = crypto.verify(
        null, 
        messageBuffer,
        publicKeyPem,
        Buffer.from(signatureHex, "hex")
      );
    } catch (err) {
      log.error(`Native verification failed: ${err}`);
    }

    if (!valid) {
      log.warn("Invalid signature rejected by native stream reader");
      res.status(401).json({ error: "Invalid request signature" });
      return;
    }

    // 4. If valid, parse the JSON and continue to your route
    try {
      req.interaction = JSON.parse(rawBody.toString("utf-8")) as DiscordInteraction;
      next();
    } catch {
      res.status(400).json({ error: "Invalid JSON body" });
    }
  });
};

export default verifyDiscordSignature;
```

