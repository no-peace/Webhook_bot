# Repository Context Group: server_routes
# Source Repository: no-peace/Hoho_manager

### File: `server/src/routes/config.ts`
```ts
import { Router } from "express";
import { listActionTypes } from "../actions/index.js";
import { env } from "../config/env.js";
import { asyncHandler } from "../utils/errors.js";

const router = Router();

/**
 * GET /api/config
 *
 * Public, non-sensitive runtime information. The editor uses this so the action
 * picker is driven by the server's registry rather than a duplicated list that
 * can fall out of sync.
 */
router.get(
  "/",
  asyncHandler(async (_req, res) => {
    res.json({
      actionTypes: listActionTypes(),
      features: {
        botSendAvailable: Boolean(env.discord.botToken),
        interactionsConfigured: Boolean(env.discord.publicKey),
      },
    });
  }),
);

export default router;

```

### File: `server/src/routes/health.ts`
```ts
import { Router } from "express";
import { db } from "../config/database.js";
import { env } from "../config/env.js";
import { asyncHandler } from "../utils/errors.js";

const router = Router();

interface CountRow {
  count: number;
}

/**
 * GET /api/health
 *
 * Readiness probe. Reports which optional integrations are configured so
 * deployment mistakes ("I forgot the bot token") are visible immediately.
 */
router.get(
  "/",
  asyncHandler(async (_req, res) => {
    const users = await db
      .get<CountRow>("SELECT COUNT(*) AS count FROM users")
      .catch(() => undefined);

    res.json({
      status: "ok",
      environment: env.nodeEnv,
      uptimeSeconds: Math.round(process.uptime()),
      time: new Date().toISOString(),
      database: { connected: users !== undefined, users: users?.count ?? null },
      discord: {
        publicKeyConfigured: Boolean(env.discord.publicKey),
        botTokenConfigured: Boolean(env.discord.botToken),
        applicationIdConfigured: Boolean(env.discord.applicationId),
      },
    });
  }),
);

export default router;

```

### File: `server/src/routes/interactions.ts`
```ts
import express, { Router } from "express";
import { InteractionResponseType } from "@dmb/shared";
import type { DiscordInteraction } from "@dmb/shared";
import { requireAdminKey } from "../middleware/auth.js";
import { requireInteraction, verifyDiscordSignature } from "../middleware/verifyDiscordSignature.js";
import { handleInteraction } from "../services/interactionHandler.js";
import * as discord from "../services/discordService.js";
import { ApiError, asyncHandler } from "../utils/errors.js";
import { logger } from "../utils/logger.js";

console.log("MY PUBLIC KEY IS:", process.env.DISCORD_PUBLIC_KEY);

const router = Router();
const log = logger.child("interactions");

/**
 * Interaction delivery.
 *
 * Discord delivers interactions in exactly **one** of two ways, and which one is
 * determined by the app's *Interactions Endpoint URL* — the two are mutually
 * exclusive per application:
 *
 *   - **Endpoint URL set** → Discord POSTs to `POST /api/interactions`. This needs
 *     a public HTTPS address (a Cloudflare Tunnel, in the laptop setup).
 *   - **No endpoint URL** → Discord sends `INTERACTION_CREATE` over the gateway.
 *     The gateway worker then forwards the payload to `POST /api/interactions/relay`
 *     on this same server, which is a plain localhost call — so a machine with no
 *     public address and no tunnel can still run the action system.
 *
 * Both routes converge on {@link handleInteraction} so a flow behaves identically
 * whichever delivery is in play. Only the transport differs.
 */

/* ── 1. Webhook delivery (public HTTPS) ────────────────────────────────────── */

/**
 * POST /api/interactions
 *
 * Pipeline:
 *   1. `express.raw` keeps the body as a Buffer — signatures cover the exact
 *      bytes, so parsing first would break verification.
 *   2. `verifyDiscordSignature` validates the Ed25519 signature and parses the
 *      payload onto `req.interaction`.
 *   3. We route by `data.custom_id` through the action executor and reply with
 *      whatever the first responding action returned.
 *
 * Discord requires a response within **3 seconds** or it shows the user
 * "This interaction failed", so every path here must reply — including errors.
 */

router.post(
  "/",
  //express.raw({ type: "application/json" }),

  verifyDiscordSignature,
  asyncHandler(async (req, res) => {
    const interaction = requireInteraction(req);
    console.log("🎉 IT WORKED! Received interaction type:", interaction.type);
    res.json(await handleInteraction(interaction));
  }),
);

/* ── 2. Gateway relay (no public address needed) ───────────────────────────── */

/** Fields the relay cannot work without; Discord signs none of them for us. */
const isRelayable = (value: unknown): value is DiscordInteraction => {
  if (value === null || typeof value !== "object") return false;
  const record = value as Record<string, unknown>;
  return (
    typeof record.id === "string" &&
    typeof record.token === "string" &&
    typeof record.application_id === "string"
  );
};

/**
 * POST /api/interactions/relay
 *
 * Called by the gateway worker, not by Discord, so it authenticates with the
 * shared `x-admin-key` instead of an Ed25519 signature.
 *
 * We do **not** verify a signature here because there is none to verify: the
 * payload is re-serialised by the worker, and Discord's signature covers the
 * original bytes. The admin key plus the fact that the route is only ever
 * reached over the API's own port is the trust boundary — bind the API to
 * localhost (or a private network) and it is not reachable from outside.
 *
 * The reply is delivered by *this* process via
 * `POST /interactions/{id}/{token}/callback`. That endpoint is authenticated by
 * the interaction token itself, which is exactly how the webhook path replies —
 * a gateway connection is not needed to answer a gateway-delivered interaction.
 *
 * The worker therefore has nothing to send back to Discord; it only needs to
 * know whether the reply landed so it can fall back to its own error message when
 * the API is unreachable.
 */
router.post(
  "/relay",
  requireAdminKey,
  express.json({ limit: "1mb" }),
  asyncHandler(async (req, res) => {
    if (!isRelayable(req.body)) {
      throw ApiError.badRequest(
        "Relay body must be the raw interaction, including id, token and application_id.",
      );
    }

    const interaction = req.body;
    const response = await handleInteraction(interaction);

    // A Ping never reaches this route (the worker only relays components and
    // modals), but posting a Pong to the callback endpoint would be nonsense.
    if (response.type === InteractionResponseType.Pong) {
      res.json({ ok: true, delivered: false, type: response.type });
      return;
    }

    try {
      await discord.createInteractionResponse(
        interaction.application_id,
        interaction.token,
        response,
      );
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error);
      log.error(`Relay could not deliver a reply for ${interaction.id}: ${reason}`);
      // `delivered: false` is what lets the worker decide to answer in-process.
      res.status(502).json({ ok: false, delivered: false, error: reason });
      return;
    }

    res.json({ ok: true, delivered: true, type: response.type });
  }),
);

export default router;

```

### File: `server/src/routes/profiles.ts`
```ts
import { Router } from "express";
import { attachUser, requireRole, requireUser } from "../middleware/auth.js";
import { botProfileService, webhookProfileService } from "../services/profileService.js";
import { asyncHandler } from "../utils/errors.js";
import { optionalFlag, optionalString, requireId, requireStrings } from "../utils/validation.js";

const router = Router();

router.use(attachUser);

const readBody = (body: unknown): Record<string, unknown> =>
  (body ?? {}) as Record<string, unknown>;

/* ── Webhook profiles ─────────────────────────────────────────────────────── */

router.get(
  "/webhooks",
  asyncHandler(async (req, res) => {
    res.json({ profiles: await webhookProfileService.list(requireUser(req).id) });
  }),
);

router.post(
  "/webhooks",
  asyncHandler(async (req, res) => {
    const body = readBody(req.body);
    requireStrings(body, ["name", "url"]);

    const profile = await webhookProfileService.create(requireUser(req).id, {
      name: String(body.name),
      url: String(body.url),
      avatarUrl: optionalString(body.avatarUrl) ?? null,
      isDefault: optionalFlag(body.isDefault) ?? 0,
    });
    res.status(201).json({ profile });
  }),
);

router.patch(
  "/webhooks/:id",
  asyncHandler(async (req, res) => {
    const body = readBody(req.body);
    const profile = await webhookProfileService.update(
      requireId(req.params.id),
      requireUser(req).id,
      {
        name: optionalString(body.name),
        url: optionalString(body.url),
        avatar_url: optionalString(body.avatarUrl),
        is_default: optionalFlag(body.isDefault),
      },
    );
    res.json({ profile });
  }),
);

router.post(
  "/webhooks/:id/default",
  asyncHandler(async (req, res) => {
    const profile = await webhookProfileService.setDefault(
      requireId(req.params.id),
      requireUser(req).id,
    );
    res.json({ profile });
  }),
);

router.delete(
  "/webhooks/:id",
  asyncHandler(async (req, res) => {
    await webhookProfileService.remove(requireId(req.params.id), requireUser(req).id);
    res.status(204).end();
  }),
);

/* ── Bot profiles (admin only — these hold credentials) ───────────────────── */

router.get(
  "/bots",
  requireRole("admin"),
  asyncHandler(async (req, res) => {
    res.json({ profiles: await botProfileService.list(requireUser(req).id) });
  }),
);

router.post(
  "/bots",
  requireRole("admin"),
  asyncHandler(async (req, res) => {
    const body = readBody(req.body);
    requireStrings(body, ["name", "token", "applicationId", "publicKey"]);

    const profile = await botProfileService.create(requireUser(req).id, {
      name: String(body.name),
      token: String(body.token),
      applicationId: String(body.applicationId),
      publicKey: String(body.publicKey),
      defaultGuildId: optionalString(body.defaultGuildId) ?? null,
    });
    res.status(201).json({ profile });
  }),
);

router.patch(
  "/bots/:id",
  requireRole("admin"),
  asyncHandler(async (req, res) => {
    const body = readBody(req.body);
    const profile = await botProfileService.update(
      requireId(req.params.id),
      requireUser(req).id,
      {
        name: optionalString(body.name),
        token: optionalString(body.token),
        public_key: optionalString(body.publicKey),
        application_id: optionalString(body.applicationId),
        default_guild_id: optionalString(body.defaultGuildId),
        is_active: optionalFlag(body.isActive),
      },
    );
    res.json({ profile });
  }),
);

router.delete(
  "/bots/:id",
  asyncHandler(async (req, res) => {
    await botProfileService.remove(requireId(req.params.id), requireUser(req).id);
    res.status(204).end();
  }),
);

export default router;

```

### File: `server/src/routes/send.ts`
```ts
import { env } from "../config/env.js";
import { Router } from "express";
import { attachUser, requireAdminKey } from "../middleware/auth.js";
import { sendLimiter } from "../middleware/rateLimit.js";
import { actionRepository } from "../repositories/actionRepository.js";
import * as discord from "../services/discordService.js";
import { ApiError, asyncHandler } from "../utils/errors.js";
import { logger } from "../utils/logger.js";
import { parseFlowRegistrations, validateMessagePayload } from "../utils/validation.js";

const router = Router();
const log = logger.child("send");

router.post(
  "/",
  attachUser,
  sendLimiter,
  requireAdminKey,
  asyncHandler(async (req, res) => {
    const { mode, payload: rawPayload, channelId, webhookUrl, threadId, profileId, editMessageId, ...body } = req.body;

    // STRICT SANITIZATION: Remove internal IDs and empty arrays that cause Invalid Form Body
    const message = validateMessagePayload(rawPayload);
    if (message.embeds && message.embeds.length === 0) delete message.embeds;
    if (message.components && message.components.length === 0) delete message.components;
    if (message.flags === 0 || message.flags === 32768) delete message.flags;
    
    // Cleanse UI-only _id properties recursively
    const cleanseIds = (obj: any): any => {
      if (Array.isArray(obj)) return obj.map(cleanseIds);
      if (obj !== null && typeof obj === 'object') {
        const newObj: any = {};
        for (const [k, v] of Object.entries(obj)) {
          if (k !== '_id') newObj[k] = cleanseIds(v);
        }
        return newObj;
      }
      return obj;
    };
    const sanitizedMessage = cleanseIds(message);

    const flows = parseFlowRegistrations(body.flows);
    if (flows.length > 0) {
      await actionRepository.registerFlows(flows);
      log.info(`Registered ${flows.length} action flow(s) for this message`);
    }

    if (mode === "webhook") {
      if (typeof webhookUrl !== "string") {
        throw ApiError.badRequest('`webhookUrl` is required when mode is "webhook"');
      }
      const sent = await discord.sendWebhook(webhookUrl, sanitizedMessage, {
        wait: true,
        threadId: typeof threadId === "string" ? threadId : null,
      });
      log.info(`Webhook send by user ${req.user?.id ?? "?"}`);
      return res.json({ ok: true, mode, message: sent });
    }

    if (typeof channelId !== "string") {
      throw ApiError.badRequest('`channelId` is required when mode is "bot"');
    }

    let sent;
    if (typeof editMessageId === "string" && editMessageId.trim() !== "") {
      const token = env.discord.botToken;
      const patchRes = await fetch(`https://discord.com/api/v10/channels/${channelId}/messages/${editMessageId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", Authorization: `Bot ${token}` },
        body: JSON.stringify(sanitizedMessage)
      });
      if (!patchRes.ok) {
        const errText = await patchRes.text();
        throw new Error(`Discord Edit Failed: ${patchRes.status} - ${errText}`);
      }
      sent = await patchRes.json();
      log.info(`Bot edited message ${editMessageId} in ${channelId} by user ${req.user?.id ?? "?"}`);
    } else {
      sent = await discord.sendChannelMessage(channelId, sanitizedMessage, {
        profileId: typeof profileId === "number" ? profileId : null,
      });
      log.info(`Bot send to ${channelId} by user ${req.user?.id ?? "?"}`);
    }

    return res.json({ ok: true, mode, message: sent });
  }),
);

// ... KEEP YOUR EXISTING GET ROUTES BELOW THIS

router.get("/channels", asyncHandler(async (_req, res) => {
  const token = env.discord.botToken;
  if (!token) return res.json([]);

  const guildReq = await fetch("https://discord.com/api/v10/users/@me/guilds", {
    headers: { Authorization: `Bot ${token}` }
  });
  const guilds = await guildReq.json();
  if (!Array.isArray(guilds) || guilds.length === 0) return res.json([]);

  const channelReq = await fetch(`https://discord.com/api/v10/guilds/${guilds[0].id}/channels`, {
    headers: { Authorization: `Bot ${token}` }
  });
  const channels = await channelReq.json();
  if (!Array.isArray(channels)) return res.json([]);

  const textChannels = channels
    .filter((c: any) => c.type === 0 || c.type === 5)
    .map((c: any) => ({ id: c.id, name: c.name }));

  res.json(textChannels);
}));

// GET /api/send/channels/:channelId/messages - Fetches recent messages sent by the bot
router.get("/channels/:channelId/messages", asyncHandler(async (req, res) => {
  const token = env.discord.botToken;
  if (!token) return res.json([]);
  
  const channelId = req.params.channelId;

  const meReq = await fetch("https://discord.com/api/v10/users/@me", {
    headers: { Authorization: `Bot ${token}` }
  });
  const me = (await meReq.json()) as any;

  if (!me?.id) return res.json([]);

  const msgReq = await fetch(`https://discord.com/api/v10/channels/${channelId}/messages?limit=50`, {
    headers: { Authorization: `Bot ${token}` }
  });
  const messages = (await msgReq.json()) as any;

  if (!Array.isArray(messages)) return res.json([]);

  // NEW: Filter out slash command interactions so they don't clutter the Edit dropdown
  const botMessages = messages
    .filter((m: any) => m.author?.id === me.id && !m.interaction && !m.interaction_metadata)
    .map((m: any) => ({
      id: m.id,
      content: m.content || "Embed / Component Message",
      timestamp: m.timestamp,
      raw: m
    }));

  res.json(botMessages);
}));

// Auto-Fetch Bot Identity for the Frontend
// Auto-Fetch Bot Identity for the Frontend
router.get(
  "/identity",
  attachUser,
  requireAdminKey,
  asyncHandler(async (req, res) => {
    // TypeScript fix: explicitly pass undefined if no ID is provided
    const profileId = req.query.profileId ? Number(req.query.profileId) : undefined;
    
    // FIX 1: resolveBotToken only takes 1 argument max
    const token = await discord.resolveBotToken(profileId);
    if (!token) return res.json(null);
    
    const reqMe = await fetch("https://discord.com/api/v10/users/@me", {
      headers: { Authorization: `Bot ${token}` }
    });
    
    // FIX 2: Cast the response to 'any' so TS allows reading properties like data.id
    const data = (await reqMe.json()) as any;
    if (!data || !data.id) return res.json(null);
    
    return res.json({
      name: data.username,
      avatar: data.avatar ? `https://cdn.discordapp.com/avatars/${data.id}/${data.avatar}.png` : ""
    });
  })
);

export default router;
```

### File: `server/src/routes/templates.ts`
```ts
import { Router } from "express";
import type { QueryData, StoredActionDefinition } from "@dmb/shared";
import { attachUser, requireUser } from "../middleware/auth.js";
import { templateService } from "../services/templateService.js";
import { ApiError, asyncHandler } from "../utils/errors.js";
import { optionalFlag, optionalString, requireId, requireStrings } from "../utils/validation.js";

const router = Router();

// Every template route acts on behalf of a user.
router.use(attachUser);

const readBody = (body: unknown): Record<string, unknown> =>
  (body ?? {}) as Record<string, unknown>;

/** GET /api/templates?q=search — list the current user's templates. */
router.get(
  "/",
  asyncHandler(async (req, res) => {
    const q = typeof req.query.q === "string" ? req.query.q : undefined;
    res.json({ templates: await templateService.list(requireUser(req).id, { q }) });
  }),
);

/** GET /api/templates/:id — full template document including its actions. */
router.get(
  "/:id",
  asyncHandler(async (req, res) => {
    const template = await templateService.get(
      requireId(req.params.id),
      requireUser(req).id,
    );
    res.json({ template });
  }),
);

/** POST /api/templates — create a template (optionally with its action chain). */
router.post(
  "/",
  asyncHandler(async (req, res) => {
    const body = readBody(req.body);
    requireStrings(body, ["name"]);
    if (body.data === undefined) throw ApiError.badRequest("`data` is required");

    const template = await templateService.create(requireUser(req).id, {
      name: String(body.name),
      description: optionalString(body.description) ?? null,
      data: body.data as QueryData,
      actions: Array.isArray(body.actions) ? (body.actions as StoredActionDefinition[]) : [],
      isPublic: optionalFlag(body.isPublic) ?? 0,
    });
    res.status(201).json({ template });
  }),
);

/** PUT /api/templates/:id — partial update; `actions` replaces the whole chain. */
router.put(
  "/:id",
  asyncHandler(async (req, res) => {
    const body = readBody(req.body);
    const template = await templateService.update(
      requireId(req.params.id),
      requireUser(req).id,
      {
        name: optionalString(body.name),
        description: optionalString(body.description) ?? null,
        data: body.data as QueryData | undefined,
        actions: Array.isArray(body.actions)
          ? (body.actions as StoredActionDefinition[])
          : undefined,
        isPublic: optionalFlag(body.isPublic),
      },
    );
    res.json({ template });
  }),
);

/** DELETE /api/templates/:id */
router.delete(
  "/:id",
  asyncHandler(async (req, res) => {
    await templateService.remove(requireId(req.params.id), requireUser(req).id);
    res.status(204).end();
  }),
);

export default router;

```

