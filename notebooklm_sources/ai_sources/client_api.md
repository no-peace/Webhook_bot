# Repository Context Group: client_api
# Source Repository: no-peace/Hoho_manager

### File: `client/src/api/client.ts`
```ts
import type {
  ActionHandlerMeta,
  ActionType,
  SendMode,
  SendRequestBody,
  SendSuccessResponse,
  StoredActionDefinition,
} from "@dmb/shared";

/**
 * Backend API client.
 *
 * One `request()` helper handles base URL, JSON encoding, the admin key header
 * and error unwrapping, so every call site reads like a function call rather
 * than a fetch dance.
 *
 * An empty base URL is intentional and useful: in development Vite proxies `/api`
 * to the Express server, so relative requests just work.
 */

const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
const ADMIN_KEY = import.meta.env.VITE_ADMIN_API_KEY ?? "";

/** Thrown for any non-2xx response; carries the server's error code. */
export class ApiRequestError extends Error {
  readonly status: number | undefined;
  readonly code: string | undefined;
  readonly details: unknown;

  constructor(
    message: string,
    { status, code, details }: { status?: number; code?: string; details?: unknown } = {},
  ) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  signal?: AbortSignal;
}

const request = async <T>(path: string, { method = "GET", body, signal }: RequestOptions = {}): Promise<T> => {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers: {
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...(ADMIN_KEY ? { "x-admin-key": ADMIN_KEY } : {}),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") throw error;
    throw new ApiRequestError("Can't reach the server. Is it running on port 3001?", {
      code: "network_error",
    });
  }

  if (response.status === 204) return null as T;

  const isJson = (response.headers.get("content-type") ?? "").includes("application/json");
  const payload: unknown = isJson ? await response.json().catch(() => null) : null;

  if (!response.ok) {
    const record = (payload ?? {}) as Record<string, unknown>;
    throw new ApiRequestError(
      typeof record.error === "string" ? record.error : `Request failed (${response.status})`,
      {
        status: response.status,
        code: typeof record.code === "string" ? record.code : undefined,
        details: record.details,
      },
    );
  }

  return payload as T;
};

/* ── Response shapes ──────────────────────────────────────────────────────── */

export interface HealthResponse {
  status: string;
  environment: string;
  uptimeSeconds: number;
  time: string;
  database: { connected: boolean; users: number | null };
  discord: {
    publicKeyConfigured: boolean;
    botTokenConfigured: boolean;
    applicationIdConfigured: boolean;
  };
}

export interface ConfigResponse {
  actionTypes: ActionHandlerMeta[];
  features: { botSendAvailable: boolean; interactionsConfigured: boolean };
}

export interface TemplateListResponse {
  templates: TemplateSummary[];
}

export interface TemplateSummary {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  preview_image_url: string | null;
  is_public: number;
  created_at: string;
  updated_at: string;
}

export interface TemplateDetailResponse {
  template: TemplateSummary & {
    data: unknown;
    actions: StoredActionDefinition[];
  };
}

export interface WebhookProfile {
  id: number;
  user_id: number;
  name: string;
  url: string;
  guild_id: string | null;
  channel_id: string | null;
  avatar_url: string | null;
  is_default: number;
  created_at: string;
  updated_at: string;
}

export interface BotProfile {
  id: number;
  user_id: number;
  name: string;
  public_key: string;
  application_id: string;
  default_guild_id: string | null;
  is_active: number;
  created_at: string;
  updated_at: string;
  has_token: boolean;
}

export interface WebhookListResponse {
  profiles: WebhookProfile[];
}

export interface BotListResponse {
  profiles: BotProfile[];
}

export interface TemplateSaveBody {
  name: string;
  data: unknown;
  actions: unknown[];
}

export const api = {
  health: () => request<HealthResponse>("/api/health"),
  config: () => request<ConfigResponse>("/api/config"),

  /** Send a message through the backend (required for bot-token mode). */
  send: (body: SendRequestBody) =>
    request<SendSuccessResponse>("/api/send", { method: "POST", body }),

  templates: {
    list: (q?: string) =>
      request<TemplateListResponse>(
        `/api/templates${q ? `?q=${encodeURIComponent(q)}` : ""}`,
      ),
    get: (id: number) => request<TemplateDetailResponse>(`/api/templates/${id}`),
    create: (template: TemplateSaveBody) =>
      request<TemplateDetailResponse>("/api/templates", { method: "POST", body: template }),
    update: (id: number, template: TemplateSaveBody) =>
      request<TemplateDetailResponse>(`/api/templates/${id}`, { method: "PUT", body: template }),
    remove: (id: number) => request<null>(`/api/templates/${id}`, { method: "DELETE" }),
  },

  profiles: {
    listWebhooks: () => request<WebhookListResponse>("/api/profiles/webhooks"),
    createWebhook: (profile: Record<string, unknown>) =>
      request<{ profile: WebhookProfile }>("/api/profiles/webhooks", {
        method: "POST",
        body: profile,
      }),
    updateWebhook: (id: number, profile: Record<string, unknown>) =>
      request<{ profile: WebhookProfile }>(`/api/profiles/webhooks/${id}`, {
        method: "PATCH",
        body: profile,
      }),
    setDefaultWebhook: (id: number) =>
      request<{ profile: WebhookProfile }>(`/api/profiles/webhooks/${id}/default`, {
        method: "POST",
      }),
    removeWebhook: (id: number) =>
      request<null>(`/api/profiles/webhooks/${id}`, { method: "DELETE" }),

    listBots: () => request<BotListResponse>("/api/profiles/bots"),
    createBot: (profile: Record<string, unknown>) =>
      request<{ profile: BotProfile }>("/api/profiles/bots", { method: "POST", body: profile }),
    updateBot: (id: number, profile: Record<string, unknown>) =>
      request<{ profile: BotProfile }>(`/api/profiles/bots/${id}`, {
        method: "PATCH",
        body: profile,
      }),
    removeBot: (id: number) => request<null>(`/api/profiles/bots/${id}`, { method: "DELETE" }),
  },
};

export type { ActionType, SendMode };

export default api;

```

### File: `client/src/api/discord.ts`
```ts
import { WEBHOOK_URL_REGEX } from "@dmb/shared";
import type { DiscordMessagePayload } from "@dmb/shared";

/**
 * Direct Discord webhook sending from the browser.
 *
 * Webhook URLs are designed to be used client-side — anyone holding the URL can
 * post, which is exactly why the bot-token path instead goes through the backend
 * proxy. Sending directly here avoids a round trip through our server.
 *
 * Trade-off: Discord's CORS policy allows this, but it does expose the webhook to
 * the network tab, so only ever do it with URLs the user themselves supplied.
 */

/** Error carrying Discord's own message plus retry guidance. */
export class WebhookError extends Error {
  readonly status: number | undefined;
  readonly retryAfterMs: number | undefined;

  constructor(
    message: string,
    { status, retryAfterMs }: { status?: number; retryAfterMs?: number } = {},
  ) {
    super(message);
    this.name = "WebhookError";
    this.status = status;
    this.retryAfterMs = retryAfterMs;
  }
}

interface WebhookIds {
  id: string;
  token: string;
}

const parseWebhook = (url: string): WebhookIds => {
  const match = typeof url === "string" ? url.match(WEBHOOK_URL_REGEX) : null;
  const [, id, token] = match ?? [];
  if (!id || !token) throw new WebhookError("That isn't a valid Discord webhook URL.");
  return { id, token };
};

export interface WebhookSendOptions {
  threadId?: string;
  wait?: boolean;
  signal?: AbortSignal;
}

interface DiscordApiError {
  message?: string;
  retry_after?: number;
}

/**
 * POST a message straight to a webhook.
 *
 * @returns the created message when `wait` is true, otherwise `null`
 */
export const sendWebhookDirect = async (
  webhookUrl: string,
  payload: DiscordMessagePayload,
  options: WebhookSendOptions = {},
): Promise<unknown> => {
  const { threadId, wait = true, signal } = options;
  const { id, token } = parseWebhook(webhookUrl);

  const params = new URLSearchParams();
  if (wait) params.set("wait", "true");
  if (threadId) params.set("thread_id", threadId);

  let response: Response;
  try {
    response = await fetch(
      `https://discord.com/api/v10/webhooks/${id}/${token}?${params.toString()}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...payload,
          // Never let a message ping a whole server by accident.
          allowed_mentions: payload.allowed_mentions ?? { parse: [] },
        }),
        signal,
      },
    );
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") throw error;
    throw new WebhookError(
      "Could not reach Discord. The webhook may have been deleted, or a browser extension blocked the request.",
    );
  }

  if (response.status === 204) return null;

  const data = (await response.json().catch(() => null)) as DiscordApiError | null;

  if (response.status === 429) {
    const retryAfterMs = Math.ceil((data?.retry_after ?? 1) * 1000);
    throw new WebhookError(
      `Rate limited by Discord — try again in ${Math.ceil(retryAfterMs / 1000)}s.`,
      { status: 429, retryAfterMs },
    );
  }

  if (!response.ok) {
    throw new WebhookError(
      data?.message ?? `Discord rejected the message (${response.status}).`,
      { status: response.status },
    );
  }

  return data;
};

export default { sendWebhookDirect };

```

