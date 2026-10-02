# 04 server config

package.json
server/package.json
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


tsconfig.json
server/tsconfig.json
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


tsconfig.build.json
server/tsconfig.build.json
```json
{
  "extends": "./tsconfig.json",
  "//": "Build-only config: identical to tsconfig.json but without test files, so vitest specs never land in dist/.",
  "exclude": ["dist", "node_modules", "src/**/*.test.ts"]
}
```


Dockerfile
server/Dockerfile
```dockerfile
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
