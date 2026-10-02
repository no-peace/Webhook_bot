# Repository Context Group: pkg_bot-rw_util
# Source Repository: discohook/discohook

### File: `packages/bot-rw/src/util/cdn.ts`
```ts
import { CDN, type ImageURLOptions } from "@discordjs/rest";
import { getUserDefaultAvatar } from "./user.js";

export const cdn = new CDN();

export const userAvatarUrl = (
  user: { id: string; avatar: string | null; discriminator: string },
  options?: ImageURLOptions,
): string => {
  if (user.avatar) {
    return cdn.avatar(user.id, user.avatar, options);
  } else {
    return cdn.defaultAvatar(getUserDefaultAvatar(user));
  }
};

export const webhookAvatarUrl = (
  webhook: { id: string; avatar: string | null },
  options?: ImageURLOptions,
): string => {
  if (webhook.avatar) {
    return cdn.avatar(webhook.id, webhook.avatar, options);
  } else {
    return cdn.defaultAvatar(
      getUserDefaultAvatar({ id: webhook.id, discriminator: "0" }),
    );
  }
};

export const readAttachment = async (url: string) => {
  const response = await fetch(url, { method: "GET" });
  if (!response.ok) {
    throw new Error(`Failed to fetch attachment with URL ${url}`);
  }
  const type = response.headers.get("Content-Type");
  const buffer = await response.arrayBuffer();

  // This was often failing with files that were 'too large' (a few hundred KB)
  // so we have to fragmentedly compile the data instead of doing it all at once
  // Thanks https://stackoverflow.com/a/60782610
  let binary = "";
  const bytes = new Uint8Array(buffer);
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return `data:${type ?? "application/octet-stream"};base64,${btoa(binary)}`;
};

```

### File: `packages/bot-rw/src/util/components.ts`
```ts
import {
  type ButtonBuilder,
  type ChannelSelectMenuBuilder,
  type MentionableSelectMenuBuilder,
  ModalBuilder,
  type RoleSelectMenuBuilder,
  type StringSelectMenuBuilder,
  TextDisplayBuilder,
  type UserSelectMenuBuilder,
} from "@discordjs/builders";
import { isLinkButton } from "discord-api-types/utils";
import {
  type APIActionRowComponent,
  type APIButtonComponent,
  type APIButtonComponentWithCustomId,
  type APIButtonComponentWithSKUId,
  type APIButtonComponentWithURL,
  type APIChannelSelectComponent,
  type APIComponentInContainer,
  type APIComponentInMessageActionRow,
  type APIMentionableSelectComponent,
  type APIMessage,
  type APIMessageComponent,
  type APIMessageTopLevelComponent,
  type APIRoleSelectComponent,
  type APISelectMenuComponent,
  type APIStringSelectComponent,
  type APITextInputComponent,
  type APIUserSelectComponent,
  ButtonStyle,
  ComponentType,
  MessageFlags,
} from "discord-api-types/v10";
import { MessageFlagsBitField } from "discord-bitflag";
import { type DraftComponent, generateId } from "store";
import type { MinimumKVComponentState } from "../components.js";
import { MAX_TOTAL_COMPONENTS } from "./constants";

export const getCustomId = (temporary = false) => {
  if (!temporary) {
    return `p_${generateId()}`;
  }
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let result = "t_";
  for (let i = 0; i < 98; i += 1) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }

  return result;
};

type Builder =
  | ButtonBuilder
  | StringSelectMenuBuilder
  | RoleSelectMenuBuilder
  | UserSelectMenuBuilder
  | ChannelSelectMenuBuilder
  | MentionableSelectMenuBuilder
  | ModalBuilder;

export const storeComponents = async <
  T extends [Builder, MinimumKVComponentState][],
>(
  kv: Bun.Env["KV"],
  ...components: T
): Promise<T[number][0][]> => {
  for (const [component, state] of components) {
    // These shouldn't necessarily be passed to this function in the first place
    // but it might happen and we don't want to assign a custom_id
    const data = component.data;
    if (
      "type" in data &&
      data.type === ComponentType.Button &&
      data.style === ButtonStyle.Link
    ) {
      continue;
    }

    if (!("custom_id" in data)) {
      component.setCustomId(getCustomId(true));
    }

    if ("type" in data && "custom_id" in data) {
      await kv.put(
        `component-${data.type}-${data.custom_id}`,
        JSON.stringify(state),
        { expirationTtl: state.componentTimeout },
      );
    } else if (component instanceof ModalBuilder) {
      await kv.put(`modal-${component.data.custom_id}`, JSON.stringify(state), {
        expirationTtl: state.componentTimeout,
      });
    }
  }
  return components.map((c) => c[0]);
};

export const getComponentWidth = (component: {
  type: ComponentType;
}): number => {
  switch (component.type) {
    case ComponentType.Button:
      return 1;
    case ComponentType.StringSelect:
    case ComponentType.UserSelect:
    case ComponentType.RoleSelect:
    case ComponentType.MentionableSelect:
    case ComponentType.ChannelSelect:
    case ComponentType.TextInput:
      return 5;
    default:
      break;
  }
  return 0;
};

export const getRowWidth = (
  row: APIActionRowComponent<
    | APIButtonComponent
    | APIStringSelectComponent
    | APIUserSelectComponent
    | APIRoleSelectComponent
    | APIMentionableSelectComponent
    | APIChannelSelectComponent
    | APITextInputComponent
  >,
): number => {
  return row.components.reduce(
    (last, component) => getComponentWidth(component) + last,
    0,
  );
};

export const parseAutoComponentId = <P extends string>(
  customId: string,
  ...parameters: P[]
) => {
  const [_, routingId, rest] = customId.split("_");

  return {
    routingId,
    ...(Object.fromEntries(
      rest?.split(":").map((value, i) => [parameters[i], value]) ?? [],
    ) as Record<P, string>),
  };
};

export const isSkuButton = (
  component: Pick<APIButtonComponent, "type" | "style">,
): component is APIButtonComponentWithSKUId =>
  component.type === ComponentType.Button &&
  component.style === ButtonStyle.Premium;

export const hasCustomId = (
  component: APIMessageComponent,
): component is APIButtonComponentWithCustomId | APISelectMenuComponent =>
  (component.type === ComponentType.Button &&
    !isSkuButton(component) &&
    !isLinkButton(component)) ||
  component.type === ComponentType.StringSelect ||
  component.type === ComponentType.RoleSelect ||
  component.type === ComponentType.UserSelect ||
  component.type === ComponentType.ChannelSelect ||
  component.type === ComponentType.MentionableSelect;

export const getComponentId = (
  component:
    | Pick<APIButtonComponentWithCustomId, "type" | "style" | "custom_id">
    | Pick<APIButtonComponentWithURL, "type" | "style" | "label" | "url">
    | Pick<APIButtonComponentWithSKUId, "type" | "style" | "sku_id">
    | Pick<APISelectMenuComponent, "type" | "custom_id">,
  components?: { id: bigint; data: DraftComponent }[],
) => {
  if (
    component.type === ComponentType.Button &&
    component.style === ButtonStyle.Link
  ) {
    const url = new URL(component.url);
    const id = url.searchParams.get("dhc-id");
    if (id) {
      try {
        return BigInt(id);
      } catch {}
    }
    if (components) {
      const match = components.find(
        (c) =>
          c.data.type === component.type &&
          c.data.style === component.style &&
          c.data.url === component.url &&
          c.data.label === component.label,
      );
      return match?.id;
    }
    return undefined;
  }
  if ("sku_id" in component) return undefined;

  return /^p_\d+/.test(component.custom_id)
    ? BigInt(component.custom_id.replace(/^p_/, ""))
    : undefined;
};

export const isActionRow = (
  component: APIMessageTopLevelComponent,
): component is APIActionRowComponent<APIComponentInMessageActionRow> =>
  component.type === ComponentType.ActionRow;

export const onlyActionRows = (
  components: APIMessageTopLevelComponent[],
  /**
   * Also look for action rows within containers,
   * useful if you do not need sibling context.
   */
  includeNested?: boolean,
) => {
  const rows: APIActionRowComponent<APIComponentInMessageActionRow>[] = [];
  if (includeNested) {
    for (const component of components) {
      if (component.type === ComponentType.Container) {
        rows.push(...component.components.filter(isActionRow));
      } else if (component.type === ComponentType.ActionRow) {
        rows.push(component);
      }
    }
  } else {
    rows.push(...components.filter(isActionRow));
  }
  return rows;
};

export const isComponentsV2 = (message: Pick<APIMessage, "flags">): boolean =>
  new MessageFlagsBitField(message.flags ?? 0).has(MessageFlags.IsComponentsV2);

export const isStorableComponent = (
  component:
    | APIComponentInMessageActionRow
    | APIMessageTopLevelComponent
    | APIComponentInContainer,
): component is
  | APIButtonComponentWithCustomId
  | APIButtonComponentWithURL
  | APISelectMenuComponent => {
  return (
    [
      ComponentType.StringSelect,
      ComponentType.ChannelSelect,
      ComponentType.MentionableSelect,
      ComponentType.RoleSelect,
      ComponentType.UserSelect,
    ].includes(component.type) ||
    (component.type === ComponentType.Button &&
      component.style !== ButtonStyle.Premium)
  );
};

export const getTotalComponentsCount = (
  components: APIMessageTopLevelComponent[],
): number =>
  components
    ?.map((c) => 1 + ("components" in c ? c.components.length : 0))
    .reduce((a, b) => a + b, 0) ?? 0;

export const getRemainingComponentsCount = (
  components: APIMessageTopLevelComponent[],
  v2?: boolean,
): number => {
  const isV2 =
    v2 ??
    // Auto detect if not provided
    components.find((c) => c.type !== ComponentType.ActionRow) !== undefined;
  return isV2
    ? MAX_TOTAL_COMPONENTS - getTotalComponentsCount(components)
    : 5 - components.length;
};

// This is used for select option arrays, which is why it's in this file
/** Slice `array` into multiple chunks of, at maximum, `chunkSize` length */
export const chunkArray = <T extends Array<unknown>>(
  array: T,
  chunkSize: number,
): T[] => {
  const chunks: T[] = [];
  for (let i = 0; i < array.length; i += chunkSize) {
    chunks.push(array.slice(i, i + chunkSize) as T);
  }
  return chunks;
};

export const textDisplay = (content: string) =>
  new TextDisplayBuilder().setContent(content);

```

### File: `packages/bot-rw/src/util/constants.ts`
```ts
export const MAX_ACTION_ROW_WIDTH = 5;
export const MAX_SELECT_OPTIONS = 25;
export const MAX_TOTAL_COMPONENTS = 40;

```

### File: `packages/bot-rw/src/util/error.ts`
```ts
import type { RESTError } from "discord-api-types/v10";

interface DiscordError {
  code: number;
  rawError: RESTError;
}

export const isDiscordError = (error: any): error is DiscordError => {
  return "code" in error && "rawError" in error;
};

```

### File: `packages/bot-rw/src/util/guards.ts`
```ts
import {
  type APIChannel,
  type APIGuildChannel,
  type APIThreadChannel,
  ChannelType,
} from "discord-api-types/v10";

export const isThread = (
  channel: APIChannel | APIGuildChannel<ChannelType>,
): channel is APIThreadChannel =>
  [
    ChannelType.PublicThread,
    ChannelType.PrivateThread,
    ChannelType.AnnouncementThread,
  ].includes(channel.type);

```

### File: `packages/bot-rw/src/util/messages.ts`
```ts
import type { APIMessage } from "discord-api-types/v10";

export const isThreadMessage = (
  message: Pick<APIMessage, "id" | "channel_id" | "position">,
) =>
  // `position` should only be present for thread messages.
  // If this breaks, reopen this:
  // https://github.com/discord/discord-api-docs/issues/7570
  message.position !== undefined ||
  // starter messages may be missing a position but still share an ID with
  // their parent
  message.id === message.channel_id;

// TODO: probably won't need this since we're using djs/api now
export const getWebhookThreadQuery = (
  message: Pick<APIMessage, "id" | "channel_id" | "position">,
) => {
  const params = new URLSearchParams();
  if (isThreadMessage(message)) {
    params.set("thread_id", message.channel_id);
  }
  return params;
};

```

### File: `packages/bot-rw/src/util/meta.ts`
```ts
import type { APIMessageComponentEmoji } from "discord-api-types/v10";

export const color = 0x58b9ff;

export const deluxeColor = 0xff81ff;

export const boolEmoji = (value: boolean | null) =>
  value === null
    ? "<:null:1263857962892660786>"
    : value
      ? "<:true:1263857933209571329>"
      : "<:false:1263857948086505482>";

export const boolPartialEmoji = (
  value: boolean | null,
): APIMessageComponentEmoji =>
  value === null
    ? { name: "null", id: "1263857962892660786" }
    : value
      ? { name: "true", id: "1263857933209571329" }
      : { name: "false", id: "1263857948086505482" };

```

### File: `packages/bot-rw/src/util/regex.ts`
```ts
export const BUTTON_URL_RE = /^(?:https?|discord):\/\/[^ ]+$/;

export const spaceEnum = (value: string) =>
  value.replaceAll(/[A-Z]/g, (match) => ` ${match}`).trim();

```

### File: `packages/bot-rw/src/util/text.ts`
```ts
export const randomString = (length: number) => {
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < length; i += 1) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }

  return result;
};

export const base64Decode = (urlSafeBase64: string) => {
  const base64 = urlSafeBase64.replace(/-/g, "+").replace(/_/g, "/");

  try {
    return Buffer.from(base64, "base64").toString("utf8");
  } catch {}

  try {
    const encoded = atob(base64)
      .split("")
      .map((char) => char.charCodeAt(0).toString(16))
      .map((hex) => `%${hex.padStart(2, "0").slice(-2)}`)
      .join("");

    return decodeURIComponent(encoded);
  } catch {
    // return nothing
  }
};

export const base64Encode = (utf8: string) => {
  try {
    return Buffer.from(utf8, "utf8").toString("base64");
  } catch {}

  const encoded = encodeURIComponent(utf8);

  const escaped = encoded.replace(/%[\dA-F]{2}/g, (hex) => {
    return String.fromCharCode(Number.parseInt(hex.slice(1), 16));
  });

  return btoa(escaped);
};

export const base64UrlEncode = (utf8: string) => {
  return base64Encode(utf8)
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=/g, "");
};

```

### File: `packages/bot-rw/src/util/user.ts`
```ts
import type { APIUser } from "discord-api-types/v10";
import type { upsertDiscordUser } from "store";

export const getUserTag = (user: APIUser): string =>
  user.discriminator === "0"
    ? user.username
    : `${user.username}#${user.discriminator}`;

export const getUserDefaultAvatar = (user: {
  id: string;
  discriminator: string;
}): number =>
  user.discriminator === "0"
    ? Number((BigInt(user.id) >> BigInt(22)) % BigInt(6))
    : Number(user.discriminator) % 5;

type PUser = Pick<
  Awaited<ReturnType<typeof upsertDiscordUser>>,
  | "lifetime"
  | "discordId"
  | "subscribedSince"
  | "subscriptionExpiresAt"
  | "firstSubscribed"
>;

export const getUserPremiumDetails = (
  user: PUser,
): { active: boolean; grace?: boolean; graceDaysRemaining?: number } => {
  // Development mode
  // if (String(user.discordId) === "115238234778370049") {
  //   return {
  //     active: true,
  //     grace: true,
  //     graceDaysRemaining: 3,
  //   };
  // }
  if (user.lifetime) return { active: true, grace: false };
  // This value should be wiped in ON_ENTITLEMENT_DELETE
  if (!user.subscribedSince) return { active: false };

  if (user.subscriptionExpiresAt) {
    const now = new Date();
    const ttl = new Date(user.subscriptionExpiresAt).getTime() - now.getTime();
    // 3 day grace period
    return {
      active: ttl >= -259_200_000,
      grace: ttl <= 0,
      graceDaysRemaining: Math.floor((259_200_000 - ttl) / 86400000),
    };
  }
  return { active: true };
};

export const userIsPremium = (user: PUser) =>
  getUserPremiumDetails(user).active;

```

