# Repository Context Group: pkg_bot_durable
# Source Repository: discohook/discohook

### File: `packages/bot/src/durable/do-kv.ts`
```ts
import { getSessionManagerStub } from "store";
import type { Env } from "../types/env.js";

export const patchGeneric = async <T>(
  env: Env,
  key: string,
  body: { data?: T; expires?: Date },
): Promise<T | null> => {
  const stub = getSessionManagerStub(env, key);
  const response = await stub.fetch("http://do/", {
    method: "PATCH",
    body: JSON.stringify(body),
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) {
    return null;
  }
  const raw = (await response.json()) as T;
  return raw;
};

export const deleteGeneric = async (env: Env, key: string) => {
  const stub = getSessionManagerStub(env, key);
  await stub.fetch("http://do/", { method: "DELETE" });
};

```

### File: `packages/bot/src/durable/feed-reader.ts`
```ts
export type FeedType =
  | "rss"
  | "atom"
  // We have to sort of re-implement the types here because I think we would
  // want to rename some properties to make more sense for the platform?
  | "bridge.tiktok"
  | "bridge.threads"
  | "bridge.mastodon"
  | "bridge.gocomics" // kill shayypy/daily-peanuts
  | "bridge.bandcamp"
  | "bridge.spotify"; // requires client id/secret, should use local bridge instance
// Maybe
// | "bridge.ao3"
// | "bridge.amazon-prices"
// | "bridge.youtube-community"
// | "bridge.twitch-videos"

// const rssBridge = "https://rss-bridge.org/bridge01/";

/**
 * This durable object polls for changes in various feeds, including:
 * - RSS/Atom feeds
 * - Misc. JSON-formatted automatic feeds (https://github.com/RSS-Bridge/rss-bridge)
 */
// export class FeedReader implements DurableObject {
//   constructor(
//     private state: DurableObjectState,
//     private env: Env,
//   ) {}

//   async fetch(request: Request) {
//     switch (request.method) {
//       default:
//         return json({ message: "Method Not Allowed" }, { status: 405 });
//     }
//   }

//   async alarm() {}
// }

// const getFeedReaderStub = (env: Env) => {
//   // const id = env.READER.idFromName(sessionId);
//   // const stub = env.READER.get(id);
//   // return stub;
// };

```

### File: `packages/bot/src/durable/share-links.ts`
```ts
import type { QueryData } from "store";
import type { Env } from "../types/env.js";

export const putShareLink = async (
  env: Env,
  shareId: string,
  data: QueryData,
  expiresAt: Date,
  origin?: string,
) => {
  const id = env.SHARE_LINKS.idFromName(shareId);
  const stub = env.SHARE_LINKS.get(id);
  await stub.fetch("http://do/", {
    method: "PUT",
    body: JSON.stringify({
      data,
      expiresAt,
      origin,
    }),
    headers: { "Content-Type": "application/json" },
  });
};

export const getShareLinkExists = async (env: Env, shareId: string) => {
  const id = env.SHARE_LINKS.idFromName(shareId);
  const stub = env.SHARE_LINKS.get(id);
  const response = await stub.fetch("http://do/", {
    method: "HEAD",
  });
  return response.ok;
};

export const getShareLink = async (env: Env, shareId: string) => {
  const id = env.SHARE_LINKS.idFromName(shareId);
  const stub = env.SHARE_LINKS.get(id);
  const response = await stub.fetch(`http://do/?shareId=${shareId}`, {
    method: "GET",
  });
  if (!response.ok) {
    throw Error(await response.text());
  }
  const raw = (await response.json()) as {
    data: QueryData;
    alarm: number;
    origin?: string;
  };
  return raw;
};

```

