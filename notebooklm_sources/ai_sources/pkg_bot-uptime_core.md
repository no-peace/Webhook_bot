# Repository Context Group: pkg_bot-uptime_core
# Source Repository: discohook/discohook

### File: `packages/bot-uptime/.gitignore`
```gitignore
# dependencies (bun install)
node_modules

# output
out
dist
*.tgz

# code coverage
coverage
*.lcov

# logs
logs
_.log
report.[0-9]_.[0-9]_.[0-9]_.[0-9]_.json

# dotenv environment variable files
.env
.env.development.local
.env.test.local
.env.production.local
.env.local

# caches
.eslintcache
.cache
*.tsbuildinfo

# IntelliJ based IDEs
.idea

# Finder (MacOS) folder config
.DS_Store

```

### File: `packages/bot-uptime/README.md`
```md
# bot-uptime

To install dependencies:

```bash
bun install
```

To run:

```bash
bun run index.ts
```

This project was created using `bun init` in bun v1.2.21. [Bun](https://bun.com) is a fast all-in-one JavaScript runtime.

```

### File: `packages/bot-uptime/index.ts`
```ts
import path from "node:path";

let checked = Date.now();
const statuses: Record<number, { shards: Record<number, boolean> }> = {};

const loadStatuses = async () => {
  const glob = new Bun.Glob(path.join(Bun.env.BOT_DIR, "status", "[0-9].json"));
  for await (const file of glob.scan()) {
    const cluster = Number(path.parse(file).name);
    const data = (await Bun.file(file).json()) as {
      shards: Record<number, boolean>;
    };
    statuses[cluster] = data;
  }
  checked = Date.now();
};

const interval = setInterval(loadStatuses, 300000);
interval.unref();

await loadStatuses();
const config = (await Bun.file(
  path.join(Bun.env.BOT_DIR, "config.json"),
).json()) as { shards: number };

const getShardStatus = (shardId: number) => {
  let clusterId = 0;
  let online: boolean | undefined;
  for (const [cluster, { shards }] of Object.entries(statuses)) {
    if (shards[shardId] !== undefined) {
      clusterId = Number(cluster);
      online = shards[shardId];
      break;
    }
  }
  return { clusterId, online };
};

Bun.serve({
  routes: {
    "/guilds/:guildId": {
      async GET(req) {
        const guildId = req.params.guildId;
        if (!/\d{17,21}/.test(guildId)) {
          return Response.json({ message: "Invalid guild ID" }, 400);
        }
        const shardId = Number(
          (BigInt(guildId) >> 22n) % BigInt(config.shards),
        );

        const status = getShardStatus(shardId);
        if (status.online === undefined) {
          return Response.json(
            { message: "Guild would belong to an unknown shard ID" },
            404,
          );
        }
        return Response.json({ shardId, ...status, checked });
      },
    },
    "/shards/:shard": {
      async GET(req) {
        const shardId = Number(req.params.shard);
        if (Number.isNaN(shardId) || shardId < 0) {
          return Response.json({ message: "Invalid shard ID" }, 400);
        }
        const status = getShardStatus(shardId);
        if (status.online === undefined) {
          return Response.json({ message: "Unknown shard ID" }, 404);
        }
        return Response.json({ ...status, checked });
      },
    },
    "/clusters/:cluster": {
      async GET(req) {
        const clusterId = Number(req.params.cluster);
        if (Number.isNaN(clusterId) || clusterId < 0) {
          return Response.json({ message: "Invalid cluster ID" }, 400);
        }
        return Response.json({
          shards: (statuses[clusterId] ?? { shards: {} }).shards,
          checked,
        });
      },
    },
  },
  development: Bun.env.NODE_ENV !== "production",
  port: "8793",
});

```

### File: `packages/bot-uptime/package.json`
```json
{
  "name": "bot-uptime",
  "module": "index.ts",
  "type": "module",
  "private": true,
  "scripts": {
    "dev": "bun --watch index.ts",
    "start": "NODE_ENV=production bun index.ts"
  },
  "devDependencies": {
    "@types/bun": "latest"
  },
  "peerDependencies": {
    "typescript": "^5"
  }
}

```

### File: `packages/bot-uptime/tsconfig.json`
```json
{
  "compilerOptions": {
    // Environment setup & latest features
    "lib": ["ESNext"],
    "target": "ESNext",
    "module": "Preserve",
    "moduleDetection": "force",
    "jsx": "react-jsx",
    "allowJs": true,

    // Bundler mode
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "noEmit": true,

    // Best practices
    "strict": true,
    "skipLibCheck": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,

    // Some stricter flags (disabled by default)
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noPropertyAccessFromIndexSignature": false
  }
}

```

