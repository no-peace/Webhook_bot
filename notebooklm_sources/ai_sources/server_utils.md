# Repository Context Group: server_utils
# Source Repository: no-peace/Hoho_manager

### File: `server/src/utils/crypto.test.ts`
```ts
import { describe, expect, it } from "vitest";
import { decrypt, encrypt } from "./crypto.js";

/**
 * Bot tokens are stored encrypted (AES-256-GCM). A round-trip plus tamper
 * detection is the whole contract here.
 */
describe("encrypt / decrypt", () => {
  it("round-trips a secret", () => {
    const secret = "MTIzNDU2Nzg5MDEyMzQ1Njc4.GaBcDe.FgHiJkLmNoP";
    expect(decrypt(encrypt(secret))).toBe(secret);
  });

  it("produces different ciphertexts for the same plaintext (random IV)", () => {
    const a = encrypt("same-input");
    const b = encrypt("same-input");
    expect(a).not.toBe(b);
    expect(decrypt(a)).toBe("same-input");
    expect(decrypt(b)).toBe("same-input");
  });

  it("embeds the auth tag so tampering is detected, not decrypted as garbage", () => {
    const sealed = encrypt("top secret");
    const [iv, tag, data] = sealed.split(".");

    // Flip a *byte* of the ciphertext, then re-encode.
    //
    // Flipping a base64 character instead was flaky: the last character of a
    // base64url group can carry only padding bits, so swapping it between some
    // values (e.g. "A" and "B") decodes to the identical bytes and GCM happily
    // authenticates the "tampered" value. `^ 0xff` always changes a byte.
    const bytes = Buffer.from(data, "base64url");
    const middle = Math.floor(bytes.length / 2);
    bytes[middle] = (bytes[middle] ?? 0) ^ 0xff;

    const flipped = `${iv}.${tag}.${bytes.toString("base64url")}`;
    expect(decrypt(flipped)).toBeNull();
  });

  it("returns null for structurally broken input rather than throwing", () => {
    expect(decrypt("not-a-valid-seal")).toBeNull();
    expect(decrypt("")).toBeNull();
    expect(decrypt("a.b")).toBeNull();
  });
});

```

### File: `server/src/utils/crypto.ts`
```ts
import crypto from "node:crypto";
import { env } from "../config/env.js";
import { logger } from "./logger.js";

/**
 * Symmetric encryption for secrets that must live in the database (bot tokens).
 *
 * Uses AES-256-GCM: authenticated encryption, so tampering is detected on
 * decrypt rather than silently producing garbage.
 *
 * If `ENCRYPTION_KEY` is unset we *derive* a key from `ADMIN_API_KEY` so local
 * development still never writes a plaintext token. Production must set a real
 * key — `validateEnv()` warns about the development default.
 */

const ALGORITHM = "aes-256-gcm";
const IV_LENGTH = 12; // 96-bit nonce, the GCM recommendation

let cachedKey: Buffer | null = null;

const deriveKey = (): Buffer => {
  const secret = env.encryptionKey ?? env.adminApiKey;
  if (!env.encryptionKey) {
    logger.warn(
      "ENCRYPTION_KEY is not set — deriving one from ADMIN_API_KEY. " +
        "Set ENCRYPTION_KEY before deploying; rotating it will invalidate stored tokens.",
    );
  }
  // Always SHA-256 the material down to exactly 32 bytes.
  return crypto.createHash("sha256").update(secret).digest();
};

const getKey = (): Buffer => (cachedKey ??= deriveKey());

/** Encrypt a string. Output: `<iv>.<tag>.<ciphertext>`, all base64url. */
export const encrypt = (plaintext: string): string => {
  const iv = crypto.randomBytes(IV_LENGTH);
  const cipher = crypto.createCipheriv(ALGORITHM, getKey(), iv);
  const encrypted = Buffer.concat([cipher.update(plaintext, "utf8"), cipher.final()]);
  const tag = cipher.getAuthTag();
  return [
    iv.toString("base64url"),
    tag.toString("base64url"),
    encrypted.toString("base64url"),
  ].join(".");
};

/** Decrypt a value produced by {@link encrypt}. Returns `null` if unreadable. */
export const decrypt = (payload: string): string | null => {
  try {
    const [ivPart, tagPart, dataPart] = payload.split(".");
    if (!ivPart || !tagPart || !dataPart) return null;

    const decipher = crypto.createDecipheriv(
      ALGORITHM,
      getKey(),
      Buffer.from(ivPart, "base64url"),
    );
    decipher.setAuthTag(Buffer.from(tagPart, "base64url"));
    const decrypted = Buffer.concat([
      decipher.update(Buffer.from(dataPart, "base64url")),
      decipher.final(),
    ]);
    return decrypted.toString("utf8");
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    logger.error(`Failed to decrypt a stored secret (wrong key?): ${reason}`);
    return null;
  }
};

/** Mask a secret for logging, e.g. `MTIz4••••••••2Y2Q`. */
export const maskSecret = (secret: string | null | undefined): string => {
  if (!secret) return "";
  if (secret.length <= 8) return "\u2022".repeat(secret.length);
  return `${secret.slice(0, 4)}${"\u2022".repeat(8)}${secret.slice(-4)}`;
};

```

### File: `server/src/utils/errors.ts`
```ts
import type { NextFunction, Request, RequestHandler, Response } from "express";

/**
 * Error primitives shared by routes and services.
 */

export interface ApiErrorOptions {
  /** Stable machine-readable code the client can branch on. */
  code?: string;
  details?: unknown;
  /**
   * Whether `message` may be sent to the client.
   *
   * Defaults to `status < 500`: client mistakes are safe to echo back,
   * unexpected server faults are not. An intentional 5xx with a *deliberate,
   * safe* message (e.g. "no bot token configured") opts in explicitly rather
   * than showing the user a useless "Internal server error".
   */
  expose?: boolean;
}

/** An error with an HTTP status and a stable machine-readable code. */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: unknown;
  readonly expose: boolean;

  constructor(status: number, message: string, options: ApiErrorOptions = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = options.code ?? "error";
    this.details = options.details;
    this.expose = options.expose ?? status < 500;
  }

  static badRequest(message: string, details?: unknown): ApiError {
    return new ApiError(400, message, { code: "bad_request", details });
  }

  static unauthorized(message = "Authentication required"): ApiError {
    return new ApiError(401, message, { code: "unauthorized" });
  }

  static forbidden(message = "You do not have permission to do that"): ApiError {
    return new ApiError(403, message, { code: "forbidden" });
  }

  static notFound(message = "Not found"): ApiError {
    return new ApiError(404, message, { code: "not_found" });
  }

  static tooMany(message = "Too many requests"): ApiError {
    return new ApiError(429, message, { code: "rate_limited" });
  }

  static upstream(message: string, details?: unknown): ApiError {
    return new ApiError(502, message, { code: "upstream_error", details });
  }
}

/** A route handler that may be async. */
export type AsyncRouteHandler = (
  req: Request,
  res: Response,
  next: NextFunction,
) => Promise<unknown>;

/**
 * Wrap an async route handler so rejected promises reach Express' error
 * middleware.
 *
 * Express 5 forwards rejected promises automatically, but wrapping keeps the
 * behaviour explicit and identical if you ever pin back to v4.
 */
export const asyncHandler =
  (fn: AsyncRouteHandler): RequestHandler =>
  (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };

```

### File: `server/src/utils/logger.ts`
```ts
/**
 * Tiny structured logger.
 *
 * Deliberately dependency-free; Phase 4 swaps this for `pino` without touching
 * call sites, because everything imports this single module.
 */

export type LogLevel = "debug" | "info" | "warn" | "error";

export interface Logger {
  debug(message: string, meta?: unknown): void;
  info(message: string, meta?: unknown): void;
  warn(message: string, meta?: unknown): void;
  error(message: string, meta?: unknown): void;
  /** Returns a logger that prefixes every line with `[scope] `. */
  child(scope: string): Logger;
}

const LEVELS: Record<LogLevel, number> = { debug: 10, info: 20, warn: 30, error: 40 };

const isLogLevel = (value: unknown): value is LogLevel =>
  typeof value === "string" && Object.prototype.hasOwnProperty.call(LEVELS, value);

// Read once at module load so `LOG_LEVEL` cannot change mid-run.
const configuredLevel = process.env.LOG_LEVEL;
const ACTIVE = isLogLevel(configuredLevel) ? LEVELS[configuredLevel] : LEVELS.info;

const COLORS: Record<LogLevel, string> = {
  debug: "\u001b[90m",
  info: "\u001b[36m",
  warn: "\u001b[33m",
  error: "\u001b[31m",
};
const RESET = "\u001b[0m";

const write = (level: LogLevel, message: string, meta?: unknown): void => {
  if (LEVELS[level] < ACTIVE) return;

  const timestamp = new Date().toISOString();
  const prefix = `${COLORS[level]}${level.toUpperCase().padEnd(5)}${RESET}`;
  const line = `${timestamp} ${prefix} ${message}`;

  const sink = level === "error" ? console.error : level === "warn" ? console.warn : console.log;
  if (meta === undefined) sink(line);
  else sink(line, meta);
};

const createLogger = (scope?: string): Logger => {
  const tag = scope ? `[${scope}] ` : "";
  return {
    debug: (message, meta) => write("debug", `${tag}${message}`, meta),
    info: (message, meta) => write("info", `${tag}${message}`, meta),
    warn: (message, meta) => write("warn", `${tag}${message}`, meta),
    error: (message, meta) => write("error", `${tag}${message}`, meta),
    child: (childScope) => createLogger(scope ? `${scope}:${childScope}` : childScope),
  };
};

export const logger: Logger = createLogger();

```

### File: `server/src/utils/validation.test.ts`
```ts
import { describe, expect, it } from "vitest";
import { ButtonStyle, ComponentType, MessageFlags } from "@dmb/shared";
import { ApiError } from "./errors.js";
import { validateComponentsV2, validateMessagePayload } from "./validation.js";

/**
 * Validation is the last line of defence before Discord, and Discord's own
 * errors ("Invalid Form Body") are famously unhelpful — these tests pin the
 * behaviour of naming the offending field.
 */

const textDisplay = (content: string) => ({ type: ComponentType.TextDisplay, content });

const rowWithButton = (customId = "action:dud") => ({
  type: ComponentType.ActionRow,
  components: [{ type: ComponentType.Button, style: ButtonStyle.Primary, label: "Click", custom_id: customId }],
});

/**
 * The API's error *message* is a summary ("Message payload failed validation");
 * the per-field explanations live in `error.details`. Assert against those.
 */
const payloadErrorDetails = (payload: unknown): string[] => {
  try {
    validateMessagePayload(payload);
  } catch (error) {
    expect(error).toBeInstanceOf(ApiError);
    return (error as ApiError).details as string[];
  }
  throw new Error("expected validateMessagePayload to throw");
};

const expectDetail = (payload: unknown, pattern: RegExp): void => {
  expect(payloadErrorDetails(payload).some((detail) => pattern.test(detail))).toBe(true);
};

describe("validateMessagePayload — classic fields", () => {
  it("accepts a plain content message", () => {
    expect(() => validateMessagePayload({ content: "hello" })).not.toThrow();
  });

  it("rejects a non-object payload", () => {
    expect(() => validateMessagePayload("hello")).toThrow(ApiError);
    expect(() => validateMessagePayload(null)).toThrow(ApiError);
    expect(() => validateMessagePayload([1, 2])).toThrow(ApiError);
  });

  it("rejects oversized content", () => {
    expectDetail({ content: "x".repeat(2001) }, /exceeds 2000/);
  });

  it("rejects too many embeds and oversized embed fields", () => {
    expectDetail({ embeds: Array.from({ length: 11 }, () => ({})) }, /at most 10 embeds/);
    expectDetail({ embeds: [{ title: "x".repeat(257) }] }, /title exceeds/);
    expectDetail({ embeds: [{ description: "x".repeat(4097) }] }, /description exceeds/);
  });

  it("rejects a non-array components field", () => {
    expectDetail({ components: "nope" }, /`components` must be an array/);
  });
});

describe("validateMessagePayload — Components V2 exclusivity", () => {
  it("accepts a V2 payload with the flag and no classic fields", () => {
    expect(() =>
      validateMessagePayload({
        flags: MessageFlags.IsComponentsV2,
        components: [textDisplay("v2 content")],
      }),
    ).not.toThrow();
  });

  it("rejects content alongside Components V2", () => {
    expectDetail(
      {
        flags: MessageFlags.IsComponentsV2,
        content: "classic",
        components: [textDisplay("v2")],
      },
      /content cannot be used together with Components V2/,
    );
  });

  it("rejects embeds alongside Components V2", () => {
    expectDetail(
      {
        flags: MessageFlags.IsComponentsV2,
        embeds: [{ title: "x" }],
        components: [textDisplay("v2")],
      },
      /embeds cannot be used together with Components V2/,
    );
  });
});

describe("validateComponentsV2 — structure", () => {
  it("accepts a valid container tree", () => {
    const tree = [
      {
        type: ComponentType.Container,
        components: [
          textDisplay("text"),
          rowWithButton(),
          { type: ComponentType.Separator, spacing: 1 },
        ],
      },
    ];
    expect(validateComponentsV2(tree)).toEqual([]);
  });

  it("rejects a Button at the top level", () => {
    const errors = validateComponentsV2([
      { type: ComponentType.Button, style: ButtonStyle.Primary, label: "x", custom_id: "a" },
    ]);
    expect(errors.some((e) => e.includes("not allowed at the top level"))).toBe(true);
  });

  it("rejects a non-integer component type", () => {
    const errors = validateComponentsV2([{ type: 999 }]);
    expect(errors.some((e) => e.includes("not allowed at the top level"))).toBe(true);
  });

  it("rejects more than 40 components", () => {
    const tree = Array.from({ length: 41 }, () => textDisplay("x"));
    const errors = validateComponentsV2(tree);
    expect(errors.some((e) => e.includes("more than 40 components"))).toBe(true);
  });

  it("rejects a Section accessory that is not a Thumbnail or Button", () => {
    const errors = validateComponentsV2([
      {
        type: ComponentType.Section,
        components: [textDisplay("text")],
        accessory: { type: ComponentType.Separator },
      },
    ]);
    expect(errors.some((e) => e.includes("accessory"))).toBe(true);
  });

  it("rejects a Section without an accessory", () => {
    const errors = validateComponentsV2([
      { type: ComponentType.Section, components: [textDisplay("text")] },
    ]);
    expect(errors.some((e) => e.includes("requires an `accessory`"))).toBe(true);
  });

  it("rejects a Separator with bad spacing", () => {
    const errors = validateComponentsV2([{ type: ComponentType.Separator, spacing: 5 }]);
    expect(errors.some((e) => e.includes("spacing"))).toBe(true);
  });
});

describe("validateComponentsV2 — interactive components", () => {
  it("rejects a button missing a custom_id", () => {
    const errors = validateComponentsV2([
      {
        type: ComponentType.ActionRow,
        components: [{ type: ComponentType.Button, style: ButtonStyle.Primary, label: "x" }],
      },
    ]);
    expect(errors.some((e) => e.includes("custom_id"))).toBe(true);
  });

  it("rejects an oversized custom_id", () => {
    const errors = validateComponentsV2([rowWithButton("x".repeat(101))]);
    expect(errors.some((e) => e.includes("custom_id exceeds 100"))).toBe(true);
  });

  it("accepts a link button with a url and no custom_id", () => {
    const errors = validateComponentsV2([
      {
        type: ComponentType.ActionRow,
        components: [
          { type: ComponentType.Button, style: ButtonStyle.Link, label: "Docs", url: "https://example.com" },
        ],
      },
    ]);
    expect(errors).toEqual([]);
  });

  it("rejects a link button without a valid url", () => {
    const errors = validateComponentsV2([
      {
        type: ComponentType.ActionRow,
        components: [{ type: ComponentType.Button, style: ButtonStyle.Link, label: "Docs" }],
      },
    ]);
    expect(errors.some((e) => e.includes("Link buttons require"))).toBe(true);
  });

  it("rejects an oversized label", () => {
    const errors = validateComponentsV2([
      {
        type: ComponentType.ActionRow,
        components: [
          { type: ComponentType.Button, style: ButtonStyle.Primary, label: "x".repeat(81), custom_id: "a" },
        ],
      },
    ]);
    expect(errors.some((e) => e.includes("label exceeds 80"))).toBe(true);
  });

  it("rejects a button directly at the top level of a row-less tree", () => {
    // Buttons must be inside an ActionRow, even inside a Container.
    const errors = validateComponentsV2([
      {
        type: ComponentType.Container,
        components: [{ type: ComponentType.Button, style: ButtonStyle.Primary, label: "x", custom_id: "a" }],
      },
    ]);
    expect(errors.some((e) => e.includes("must be inside an ActionRow"))).toBe(true);
  });

  it("rejects a select with more than 25 options", () => {
    const options = Array.from({ length: 26 }, (_, i) => ({ label: `o${i}`, value: `v${i}` }));
    const errors = validateComponentsV2([
      {
        type: ComponentType.ActionRow,
        components: [{ type: ComponentType.StringSelect, custom_id: "a", options }],
      },
    ]);
    expect(errors.some((e) => e.includes("25 options"))).toBe(true);
  });

  it("rejects select options with missing or oversized labels", () => {
    const errors = validateComponentsV2([
      {
        type: ComponentType.ActionRow,
        components: [
          {
            type: ComponentType.StringSelect,
            custom_id: "a",
            options: [{ label: "", value: "v" }, { label: "ok", value: "x".repeat(101) }],
          },
        ],
      },
    ]);
    expect(errors.some((e) => e.includes("options[0].label"))).toBe(true);
    expect(errors.some((e) => e.includes("options[1].value"))).toBe(true);
  });

  it("rejects a bad placeholder", () => {
    const errors = validateComponentsV2([
      {
        type: ComponentType.ActionRow,
        components: [
          { type: ComponentType.StringSelect, custom_id: "a", options: [], placeholder: "x".repeat(151) },
        ],
      },
    ]);
    expect(errors.some((e) => e.includes("placeholder exceeds 150"))).toBe(true);
  });

  it("rejects a TextDisplay with empty or oversized content", () => {
    expect(validateComponentsV2([textDisplay("   ")]).some((e) => e.includes("non-empty"))).toBe(true);
    expect(
      validateComponentsV2([textDisplay("x".repeat(4001))]).some((e) =>
        e.includes("exceeds 4000 characters"),
      ),
    ).toBe(true);
  });
});

```

### File: `server/src/utils/validation.ts`
```ts
import {
  ACTION_PREFIX,
  ACTION_SEPARATOR,
  ButtonStyle,
  ComponentType,
  Limits,
  MessageFlags,
  SNOWFLAKE_REGEX,
  WEBHOOK_URL_REGEX,
} from "@dmb/shared";
import type { DiscordMessagePayload, FlowRegistration } from "@dmb/shared";
import { ApiError } from "./errors.js";

/**
 * Validation helpers for everything the client sends us.
 *
 * Kept dependency-free on purpose: the rules are small and explicit, and this
 * avoids a schema library that would need mirroring on the frontend anyway.
 *
 * Discord's own rejections are famously unhelpful ("Invalid Form Body"), so we
 * check its documented limits here and return a message that names the field and
 * tells the user what to change.
 */

export const isSnowflake = (value: unknown): value is string =>
  typeof value === "string" && SNOWFLAKE_REGEX.test(value);

export const isHttpUrl = (value: unknown): boolean => {
  if (typeof value !== "string") return false;
  try {
    const url = new URL(value);
    return url.protocol === "https:" || url.protocol === "http:";
  } catch {
    return false;
  }
};

export interface ParsedWebhookUrl {
  id: string;
  token: string;
}

/** Extract `{ id, token }` from a valid Discord webhook URL, else `null`. */
export const parseWebhookUrl = (value: unknown): ParsedWebhookUrl | null => {
  const match = typeof value === "string" ? value.match(WEBHOOK_URL_REGEX) : null;
  const [, id, token] = match ?? [];
  return id && token ? { id, token } : null;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

const asString = (value: unknown): string | null =>
  typeof value === "string" ? value : value == null ? null : null;

/* ── Components V2 ───────────────────────────────────────────────────────── */

/** Component types that may appear at the top level of a V2 payload. */
const TOP_LEVEL_TYPES = new Set<number>([
  ComponentType.ActionRow,
  ComponentType.Section,
  ComponentType.TextDisplay,
  ComponentType.MediaGallery,
  ComponentType.File,
  ComponentType.Separator,
  ComponentType.Container,
]);

/** Component types that may hold children in `components`. */
const PARENT_TYPES = new Set<number>([
  ComponentType.ActionRow,
  ComponentType.Section,
  ComponentType.Container,
]);

/** Component types that may be a Section's `accessory`. */
const ACCESSORY_TYPES = new Set<number>([
  ComponentType.Thumbnail,
  ComponentType.Button,
]);

/** Interactive component types that must live inside an ActionRow. */
const ROW_CHILD_TYPES = new Set<number>([
  ComponentType.Button,
  ComponentType.StringSelect,
  ComponentType.UserSelect,
  ComponentType.RoleSelect,
  ComponentType.MentionableSelect,
  ComponentType.ChannelSelect,
]);

const TYPE_LABELS: Record<number, string> = {
  [ComponentType.ActionRow]: "ActionRow",
  [ComponentType.Button]: "Button",
  [ComponentType.StringSelect]: "StringSelect",
  [ComponentType.TextInput]: "TextInput",
  [ComponentType.UserSelect]: "UserSelect",
  [ComponentType.RoleSelect]: "RoleSelect",
  [ComponentType.MentionableSelect]: "MentionableSelect",
  [ComponentType.ChannelSelect]: "ChannelSelect",
  [ComponentType.Section]: "Section",
  [ComponentType.TextDisplay]: "TextDisplay",
  [ComponentType.Thumbnail]: "Thumbnail",
  [ComponentType.MediaGallery]: "MediaGallery",
  [ComponentType.File]: "File",
  [ComponentType.Separator]: "Separator",
  [ComponentType.Container]: "Container",
};

const describeType = (type: unknown): string =>
  typeof type === "number" ? (TYPE_LABELS[type] ?? `type ${type}`) : "component";

/**
 * Depth-first walk over a component tree.
 *
 * Mirrors the client's `tree.ts` traversal: only `components` arrays are
 * followed; `items`/`options`/`accessory` are leaves (the accessory is visited
 * explicitly by the Section check).
 */
const walkComponents = (
  components: unknown,
  visit: (node: Record<string, unknown>, path: string, depth: number) => boolean | void,
): void => {
  if (!Array.isArray(components)) return;

  const recurse = (list: unknown[], path: string, depth: number): boolean => {
    if (depth > 25) return false; // Hard limit on nesting depth
    for (const [index, entry] of list.entries()) {
      if (entry === null || typeof entry !== "object" || Array.isArray(entry)) continue;
      const node = entry as Record<string, unknown>;
      const where = `${path}[${index}]`;
      
      const shouldContinue = visit(node, where, depth);
      if (shouldContinue === false) return false;

      if (Array.isArray(node.components)) {
        if (recurse(node.components, `${where}.components`, depth + 1) === false) {
          return false;
        }
      }
    }
    return true;
  };

  recurse(components, "components", 0);
};

/**
 * Validate a Components V2 tree against Discord's documented rules.
 *
 * This is deliberately a sanity net, not a full spec re-implementation: it
 * catches the mistakes that produce Discord's unhelpful "Invalid Form Body" —
 * nesting violations, missing labels, oversized text, bad select ranges — and
 * names the offending field so the user can fix it.
 */
export const validateComponentsV2 = (components: unknown): string[] => {
  const errors: string[] = [];
  if (!Array.isArray(components)) return errors;

  let nodeCount = 0;
  let sawInteractive = false;

  const fail = (where: string, message: string): void => {
    errors.push(`${where}: ${message}`);
  };

  walkComponents(components, (node, where, depth) => {
    nodeCount += 1;
    if (nodeCount > Limits.components.total) {
      fail(where, `more than ${Limits.components.total} components in one message`);
      return false;
    }

    const type = node.type;
    const label = describeType(type);

    if (depth === 0 && !TOP_LEVEL_TYPES.has(Number(type))) {
      fail(where, `${label} is not allowed at the top level`);
    }
    if (depth > 0 && !PARENT_TYPES.has(Number(type))) {
      // Only reachable when the parent was itself invalid; the parent error
      // already names the real problem, so don't double-report.
    }

    // Text bounds.
    if (type === ComponentType.TextDisplay) {
      const content = node.content;
      if (typeof content !== "string" || content.trim() === "") {
        fail(where, "TextDisplay requires non-empty `content`");
      } else if (content.length > Limits.components.textDisplay) {
        fail(where, `TextDisplay content exceeds ${Limits.components.textDisplay} characters`);
      }
    }

    // Buttons & selects.
    if (ROW_CHILD_TYPES.has(Number(type))) {
      sawInteractive = true;
      if (type === ComponentType.Button) {
        const style = Number(node.style);
        const isLink = style === ButtonStyle.Link;
        const isPremium = style === ButtonStyle.Premium;
        if (!isLink && !isPremium) {
          const customId = node.custom_id;
          if (typeof customId !== "string" || customId.length === 0) {
            fail(where, "Button requires a `custom_id` (or link/premium style)");
          } else if (customId.length > Limits.components.customId) {
            fail(where, `Button custom_id exceeds ${Limits.components.customId} characters`);
          }
        }
        if (isLink && !isHttpUrl(node.url)) {
          fail(where, "Link buttons require a valid `url`");
        }
        const labelText = typeof node.label === "string" ? node.label : "";
        if (!isPremium && labelText.length > Limits.components.label) {
          fail(where, `Button label exceeds ${Limits.components.label} characters`);
        }
      }

      const placeholder = node.placeholder;
      if (typeof placeholder === "string" && placeholder.length > Limits.components.placeholder) {
        fail(where, `placeholder exceeds ${Limits.components.placeholder} characters`);
      }

      if (type !== ComponentType.Button && Array.isArray(node.options)) {
        if (node.options.length > Limits.components.options) {
          fail(where, `select exceeds ${Limits.components.options} options`);
        }
        for (const [optionIndex, option] of node.options.entries()) {
          if (option === null || typeof option !== "object") {
            fail(`${where}.options[${optionIndex}]`, "must be an object");
            continue;
          }
          const record = option as Record<string, unknown>;
          const optionLabel = typeof record.label === "string" ? record.label : "";
          if (optionLabel.length === 0 || optionLabel.length > Limits.components.selectOptionLabel) {
            fail(
              `${where}.options[${optionIndex}].label`,
              `required, 1-${Limits.components.selectOptionLabel} characters`,
            );
          }
          const value = typeof record.value === "string" ? record.value : "";
          if (value.length === 0 || value.length > Limits.components.selectOptionLabel) {
            fail(
              `${where}.options[${optionIndex}].value`,
              `required, 1-${Limits.components.selectOptionLabel} characters`,
            );
          }
          const description = record.description;
          if (
            typeof description === "string" &&
            description.length > Limits.components.selectOptionDescription
          ) {
            fail(
              `${where}.options[${optionIndex}].description`,
              `exceeds ${Limits.components.selectOptionDescription} characters`,
            );
          }
        }

        const minValues = node.min_values;
        if (minValues !== undefined && (!Number.isInteger(minValues) || Number(minValues) < 0)) {
          fail(where, "`min_values` must be a non-negative integer");
        }
        const maxValues = node.max_values;
        if (maxValues !== undefined && (!Number.isInteger(maxValues) || Number(maxValues) < 1)) {
          fail(where, "`max_values` must be a positive integer");
        }
      }
    }

    // Section accessory.
    if (type === ComponentType.Section) {
      const accessory = node.accessory;
      if (accessory !== null && typeof accessory === "object" && !Array.isArray(accessory)) {
        const accessoryType = (accessory as Record<string, unknown>).type;
        if (!ACCESSORY_TYPES.has(Number(accessoryType))) {
          fail(
            `${where}.accessory`,
            `${describeType(accessoryType)} cannot be a section accessory (use Thumbnail or Button)`,
          );
        }
      } else {
        fail(where, "Section requires an `accessory`");
      }
    }

    // Separator spacing.
    if (type === ComponentType.Separator) {
      const spacing = node.spacing;
      if (spacing !== undefined && spacing !== 1 && spacing !== 2) {
        fail(where, "Separator `spacing` must be 1 (small) or 2 (large)");
      }
    }
  });

  // Every interactive component must sit inside an ActionRow.
  if (sawInteractive) {
    const checkRows = (list: unknown[], parentIsRow: boolean, path: string, depth: number): void => {
      if (depth > 25) return;
      for (const [index, entry] of list.entries()) {
        if (entry === null || typeof entry !== "object") continue;
        const node = entry as Record<string, unknown>;
        const where = `${path}[${index}]`;
        if (ROW_CHILD_TYPES.has(Number(node.type)) && !parentIsRow) {
          fail(where, `${describeType(node.type)} must be inside an ActionRow`);
        }
        if (Array.isArray(node.components)) {
          checkRows(node.components, node.type === ComponentType.ActionRow, `${where}.components`, depth + 1);
        }
      }
    };
    checkRows(components, false, "components", 0);
  }

  return errors;
};

/**
 * Reject obviously-oversized payloads before they reach Discord.
 *
 * Returns nothing and throws {@link ApiError} with a 400 listing every problem
 * found, so the user can fix them all at once rather than one per attempt.
 */
export const validateMessagePayload = (payload: unknown): DiscordMessagePayload => {
  if (!isRecord(payload)) {
    throw ApiError.badRequest("`payload` must be a message object");
  }

  const errors: string[] = [];

  const content = asString(payload.content);
  if (payload.content != null && content === null) {
    errors.push("`content` must be a string");
  } else if (content !== null && content.length > Limits.content) {
    errors.push(`\`content\` exceeds ${Limits.content} characters (got ${content.length})`);
  }

  const embeds = payload.embeds;
  if (embeds != null && !Array.isArray(embeds)) {
    errors.push("`embeds` must be an array");
  } else if (Array.isArray(embeds)) {
    if (embeds.length > Limits.embed.embedsPerMessage) {
      errors.push(`A message can contain at most ${Limits.embed.embedsPerMessage} embeds`);
    } else {
      embeds.forEach((embed, index) => {
        const where = `embeds[${index}]`;
        if (!isRecord(embed)) {
          errors.push(`${where} must be an object`);
          return;
        }
        const title = asString(embed.title);
        const description = asString(embed.description);
        if (title !== null && title.length > Limits.embed.title) {
          errors.push(`${where}.title exceeds ${Limits.embed.title} characters`);
        }
        if (description !== null && description.length > Limits.embed.description) {
          errors.push(`${where}.description exceeds ${Limits.embed.description} characters`);
        }
        if (Array.isArray(embed.fields) && embed.fields.length > Limits.embed.fields) {
          errors.push(`${where}.fields exceeds ${Limits.embed.fields} entries`);
        }
      });
    }
  }

  const components = payload.components;
  if (components != null && !Array.isArray(components)) {
    errors.push("`components` must be an array");
  } else if (Array.isArray(components) && components.length > 0) {
    errors.push(...validateComponentsV2(components));

    // Components V2 is mutually exclusive with classic content/embeds.
    const isComponentsV2 =
      typeof payload.flags === "number" &&
      (payload.flags & MessageFlags.IsComponentsV2) !== 0;
    if (isComponentsV2) {
      if (typeof payload.content === "string" && payload.content !== "") {
        errors.push("content cannot be used together with Components V2");
      }
      if (Array.isArray(payload.embeds) && payload.embeds.length > 0) {
        errors.push("embeds cannot be used together with Components V2");
      }
    }
  }

  if (errors.length > 0) {
    throw ApiError.badRequest("Message payload failed validation", errors);
  }

  // Validated against the documented limits above; safe to hand on as-is.
  return payload as DiscordMessagePayload;
};

/**
 * Read the optional `flows` array from a send request.
 *
 * Malformed entries are skipped rather than rejected: a flow is a convenience
 * that upgrades a button from one step to many, and refusing to send the whole
 * message because one step was unexpected would be a worse outcome than sending
 * it with just the inline action in the `custom_id`.
 */
export const parseFlowRegistrations = (value: unknown): FlowRegistration[] => {
  if (!Array.isArray(value)) return [];

  const flows: FlowRegistration[] = [];

  for (const entry of value) {
    if (!isRecord(entry)) continue;

    const customId = entry.customId;
    if (
      typeof customId !== "string" ||
      !customId.startsWith(`${ACTION_PREFIX}${ACTION_SEPARATOR}`) ||
      customId.length > Limits.components.customId
    ) {
      continue;
    }

    if (!Array.isArray(entry.steps)) continue;

    const steps = entry.steps
      .filter(isRecord)
      .map((step) => ({
        type: (typeof step.type === "string" ? step.type : "dud") as FlowRegistration["steps"][number]["type"],
        config: isRecord(step.config) ? step.config : {},
      }));

    if (steps.length === 0) continue;
    flows.push({ customId, steps });
  }

  return flows;
};

/** Parse a positive integer id, or throw a 400. */
export const requireId = (value: unknown, label = "id"): number => {
  const parsed = Number.parseInt(String(value), 10);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    throw ApiError.badRequest(`\`${label}\` must be a positive integer`);
  }
  return parsed;
};

/** Assert required string fields are present and non-empty. */
export const requireStrings = (body: unknown, fields: readonly string[]): void => {
  const record = isRecord(body) ? body : {};
  const missing = fields.filter((field) => {
    const value = record[field];
    return typeof value !== "string" || value.trim() === "";
  });

  if (missing.length > 0) {
    throw ApiError.badRequest(`Missing required field(s): ${missing.join(", ")}`);
  }
};

/** Read an optional string field from a request body. */
export const optionalString = (value: unknown): string | undefined =>
  typeof value === "string" && value.trim() !== "" ? value.trim() : undefined;

/** Read an optional boolean-ish field (accepts `1`, `"true"`, `true`). */
export const optionalFlag = (value: unknown): 1 | 0 | undefined => {
  if (value === undefined || value === null) return undefined;
  if (value === true || value === 1 || value === "1" || value === "true") return 1;
  return 0;
};

```

