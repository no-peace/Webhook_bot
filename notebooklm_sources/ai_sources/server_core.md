# Repository Context Group: server_core
# Source Repository: no-peace/Hoho_manager

### File: `server/.env.example`
```example
# ─── Server ────────────────────────────────────────────────────────────────
NODE_ENV=development
PORT=3001

# Where the browser SPA is served from. Comma-separate multiple origins.
CLIENT_ORIGIN=http://localhost:5173

# ─── Database ──────────────────────────────────────────────────────────────
# Relative paths are resolved from the `server/` directory.
# Swap for a Postgres URL later once the repository layer is pointed at `pg`.
DATABASE_URL=./data/dev.sqlite

# ─── Discord ───────────────────────────────────────────────────────────────
# Developer Portal → your application → General Information → Public Key.
# Used to verify every interaction signature.
DISCORD_PUBLIC_KEY=

# Developer Portal → your application → General Information → Application ID.
DISCORD_APPLICATION_ID=

# Developer Portal → Bot → Token. NEVER expose this to the frontend.
DISCORD_BOT_TOKEN=

# ─── Access control ────────────────────────────────────────────────────────
# Shared secret the client sends (x-admin-key) to call privileged endpoints
# such as /api/send in bot mode. Replace with real auth in Phase 4.
ADMIN_API_KEY=dev-admin-key

# Key used to encrypt bot tokens at rest (AES-256-GCM).
# Generate one with:  node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
ENCRYPTION_KEY=

# ─── Security tuning (optional) ────────────────────────────────────────────
# Requests per window against /api/* before a 429 is returned.
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX=120

```

### File: `server/Dockerfile`
```text
# ── Build stage ────────────────────────────────────────────────────────────
# Compiles @dmb/shared (TS -> dist) and the server (TS -> dist), so the runtime
# image only ever executes plain JavaScript from `dist/`.
FROM node:22-bookworm-slim AS build

# better-sqlite3 needs a toolchain when no prebuilt binary matches.
RUN apt-get update \
  && apt-get install -y --no-install-recommends python3 make g++ \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json package-lock.json* tsconfig.base.json ./
COPY shared/package.json shared/tsconfig.json ./shared/
COPY server/package.json server/tsconfig.json ./server/
COPY client/package.json client/tsconfig.json ./client/
RUN npm install --workspace server --include-workspace-root

COPY shared ./shared
COPY server ./server
RUN npm run build --workspace @dmb/shared \
  && npm run build --workspace server

# ── Runtime stage ──────────────────────────────────────────────────────────
FROM node:22-bookworm-slim AS runtime
ENV NODE_ENV=production
WORKDIR /app

COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/server/node_modules ./server/node_modules
COPY --from=build /app/shared/package.json ./shared/package.json
COPY --from=build /app/shared/dist ./shared/dist
COPY --from=build /app/server/dist ./server/dist
COPY package.json ./

RUN mkdir -p /app/data
EXPOSE 3001

# `server/` is the cwd so DATABASE_URL (./data/...) and the .env lookup resolve
# inside the container.
WORKDIR /app/server
CMD ["node", "dist/index.js"]

```

### File: `server/package.json`
```json
{
  "name": "server",
  "version": "0.1.0",
  "private": true,
  "description": "Express API + Discord interaction endpoint for the message builder.",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc -p tsconfig.build.json",
    "start": "node dist/index.js",
    "migrate": "tsx src/config/migrate.ts",
    "test": "vitest run",
    "typecheck": "tsc -p tsconfig.json --noEmit"
  },
  "dependencies": {
    "@dmb/shared": "*",
    "better-sqlite3": "^13.0.3",
    "cors": "^2.8.6",
    "discord-interactions": "^4.4.0",
    "dotenv": "^18.0.4",
    "express": "^5.2.1",
    "express-rate-limit": "^8.7.0",
    "helmet": "^8.3.0"
  },
  "devDependencies": {
    "@types/better-sqlite3": "^7.6.13",
    "@types/cors": "^2.8.19",
    "@types/express": "^5.0.6",
    "@types/node": "^24.10.1",
    "tsx": "^4.20.6",
    "typescript": "^5.9.3",
    "vitest": "^3.2.7"
  },
  "engines": {
    "node": ">=20"
  }
}

```

### File: `server/tsconfig.build.json`
```json
{
  "extends": "./tsconfig.json",
  "//": "Build-only config: identical to tsconfig.json but without test files, so vitest specs never land in dist/.",
  "exclude": ["dist", "node_modules", "src/**/*.test.ts"]
}

```

### File: `server/tsconfig.json`
```json
{
  "extends": "../tsconfig.base.json",
  "compilerOptions": {
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2023"],
    "types": ["node"],
    "rootDir": "src",
    "outDir": "dist",
    "newLine": "lf"
  },
  "include": ["src/**/*.ts"],
  "exclude": ["dist", "node_modules"]
}

```

### File: `server/vitest.config.ts`
```ts
import { defineConfig } from "vitest/config";
import { fileURLToPath, URL } from "node:url";

/**
 * Vitest config for the server.
 *
 * Mirrors tsconfig: `@dmb/shared` resolves to the shared **source**, so tests
 * run against the same code the server imports — no build step needed.
 */
export default defineConfig({
  resolve: {
    alias: {
      "@dmb/shared": fileURLToPath(new URL("../shared/src/index.ts", import.meta.url)),
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
});

```

