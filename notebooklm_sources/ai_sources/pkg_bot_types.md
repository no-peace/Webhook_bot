# Repository Context Group: pkg_bot_types
# Source Repository: discohook/discohook

### File: `packages/bot/src/types/api.ts`
```ts
import type {
  APIPartialChannel,
  APIThreadChannel,
  ChannelType,
} from "discord-api-types/v10";

export type APIPartialResolvedChannelBase = APIPartialChannel & {
  permissions: string;
};

export type APIPartialResolvedThread = APIPartialResolvedChannelBase & {
  type:
    | ChannelType.AnnouncementThread
    | ChannelType.PublicThread
    | ChannelType.PrivateThread;
  thread_metadata: APIThreadChannel["thread_metadata"];
  parent_id: APIThreadChannel["parent_id"];
};

export type APIPartialResolvedChannel =
  | APIPartialResolvedChannelBase
  | APIPartialResolvedThread;

```

### File: `packages/bot/src/types/env.ts`
```ts
import type { Service } from "@cloudflare/workers-types";
import type { RedisKV } from "store";

export interface Env {
  ENVIRONMENT: "dev" | "preview" | "production";
  PREMIUM_SKUS: string[];
  LIFETIME_SKU: string;
  DISCORD_APPLICATION_ID: string;
  DISCORD_PUBLIC_KEY: string;
  DISCORD_TOKEN: string;
  DISCORD_PROXY_API?: string;
  DISCOHOOK_ORIGIN: string;
  BOUNCER_ORIGIN?: string;
  BOUNCER_JWT_KEY?: string;
  TOKEN_SECRET: string;
  DATABASE_URL: string;
  REDIS_URL: string;
  KV: RedisKV;

  GUILD_ID?: string;
  DONATOR_ROLE_ID?: string;
  SUBSCRIBER_ROLE_ID?: string;

  APPLICATIONS: Record<string, string>;
  APPLICATIONS_RAW?: string;
  HYPERDRIVE: Hyperdrive;
  COMPONENTS: DurableObjectNamespace;
  DRAFT_CLEANER: DurableObjectNamespace;
  SHARE_LINKS: DurableObjectNamespace;
  EMOJIS: DurableObjectNamespace;
  SESSIONS: DurableObjectNamespace;
  SITE: Service;

  DEV_GUILD_ID?: string;
  DEV_OWNER_ID?: string;
}

```

### File: `packages/bot/src/types/webhook-events.ts`
```ts
import type {
  APIEntitlement,
  APIGuild,
  APIUser,
  ApplicationIntegrationType,
} from "discord-api-types/v10";

export enum WebhookEventType {
  Ping = 0,
  Event = 1,
}

export interface APIWebhookEventBase<T extends WebhookEventType, E> {
  version: number;
  application_id: string;
  type: T;
  event: E;
}

export type APIWebhookEventPing = APIWebhookEventBase<
  WebhookEventType.Ping,
  undefined
>;

export enum WebhookEvents {
  ApplicationAuthorized = "APPLICATION_AUTHORIZED",
  EntitlementCreate = "ENTITLEMENT_CREATE",
  QuestUserEnrollment = "QUEST_USER_ENROLLMENT",
}

export interface APIWebhookEventBodyBase<T> {
  type: WebhookEvents;
  timestamp: string;
  data?: T;
}

export interface APIWebhookEventBodyApplicationAuthorizedBase<
  I extends ApplicationIntegrationType = ApplicationIntegrationType,
> {
  integration_type?: I;
  user: APIUser;
  scopes: string[];
  guild: I extends ApplicationIntegrationType.GuildInstall
    ? APIGuild
    : undefined;
}

export type APIWebhookEventBodyApplicationAuthorizedGuild =
  APIWebhookEventBodyApplicationAuthorizedBase<ApplicationIntegrationType.GuildInstall>;

export type APIWebhookEventBodyApplicationAuthorizedUser =
  APIWebhookEventBodyApplicationAuthorizedBase<ApplicationIntegrationType.UserInstall>;

export type APIWebhookEventBodyApplicationAuthorized<
  I extends ApplicationIntegrationType = ApplicationIntegrationType,
> = APIWebhookEventBodyBase<APIWebhookEventBodyApplicationAuthorizedBase<I>>;

export type APIWebhookEventApplicationAuthorized = APIWebhookEventBase<
  WebhookEventType.Event,
  APIWebhookEventBodyApplicationAuthorized
>;

export type APIWebhookEventBodyEntitlementCreate =
  APIWebhookEventBodyBase<APIEntitlement>;

export type APIWebhookEventEntitlementCreate = APIWebhookEventBase<
  WebhookEventType.Event,
  APIWebhookEventBodyEntitlementCreate
>;

export type APIWebhookEvent =
  | APIWebhookEventPing
  | APIWebhookEventApplicationAuthorized
  | APIWebhookEventEntitlementCreate;

export type APIWebhookEventBody =
  | APIWebhookEventBodyApplicationAuthorized
  | APIWebhookEventBodyEntitlementCreate;

```

