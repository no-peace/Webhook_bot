# Repository Context Group: pkg_bot-rw_types
# Source Repository: discohook/discohook

### File: `packages/bot-rw/src/types/api.ts`
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

