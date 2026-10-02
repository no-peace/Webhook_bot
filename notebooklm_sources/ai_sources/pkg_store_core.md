# Repository Context Group: pkg_store_core
# Source Repository: discohook/discohook

### File: `packages/store/.gitignore`
```gitignore
node_modules
# Keep environment variables out of version control
.env

```

### File: `packages/store/README.md`
```md
# store

Shared database/redis package for Discohook.

## Migrations

### February 2026: Drizzle 0.33 breaking change

Prerequisites:
- Run a `yarn install` to ensure you are up to date (above drizzle-orm version 0.32.1)

Run `yarn db-migrate` (root dir) to update all your old json columns which were previously incorrectly stringified by drizzle. If you cannot, just make sure [migration 006](/drizzle/0006_json-columns.sql) is applied.

```

### File: `packages/store/index.ts`
```ts
import { FlowActionType } from "./src/types/index.js";

export * from "./src/db.js";
export * from "./src/kv.js";
export * from "./src/redis.js";
export * from "./src/schema/index.js";
export * from "./src/types/index.js";
export * from "./src/zod/index.js";

export const flowActionTypeMeta: Partial<
  Record<
    FlowActionType,
    {
      /** This action can finalize an interaction flow */
      isResponse?: boolean;
      /** This action must happen after a response */
      mustFollow?: boolean;
    }
  >
> = {
  [FlowActionType.Dud]: { isResponse: true },
  [FlowActionType.Wait]: { mustFollow: true },
  [FlowActionType.SendMessage]: { isResponse: true },
};

```

### File: `packages/store/package.json`
```json
{
  "name": "store",
  "version": "0.0.0",
  "main": "index.ts",
  "repository": "https://github.com/discohook/discohook",
  "author": "shayypy",
  "license": "MIT",
  "private": true,
  "type": "module",
  "scripts": {
    "snowflake": "node ./scripts/snowflake.js"
  },
  "dependencies": {
    "discord-api-types": "^0.38.32",
    "discord-snowflake": "^2.0.0",
    "drizzle-orm": "^0.45.1",
    "json-with-bigint": "^3.5.3",
    "postgres": "^3.4.5",
    "tif-snowflake": "discohook/snowflake",
    "zod": "^4.1.5",
    "zodix": "npm:@coji/zodix@^0.5.0"
  },
  "devDependencies": {
    "@discordjs/rest": "^2.5.0",
    "@types/bun": "^1.3.9",
    "drizzle-kit": "^0.31.9",
    "typescript": "^5.3.3"
  }
}

```

### File: `packages/store/scripts/snowflake.js`
```js
import { Snowflake } from "tif-snowflake";

export const EPOCH = Date.UTC(2024, 1, 1).valueOf();

/** @type {(timestamp?: number | Date) => string} */
export const generateId = (timestamp) => {
  return Snowflake.generate({
    timestamp,
    epoch: EPOCH,
  });
};

console.log(generateId());

```

### File: `packages/store/tsconfig.json`
```json
{
  "extends": "@tsconfig/node18/tsconfig.json",
  "compilerOptions": {
    "lib": ["es2017", "dom"],
    "types": ["@cloudflare/workers-types/2023-03-01", "bun"]
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules"]
}

```

