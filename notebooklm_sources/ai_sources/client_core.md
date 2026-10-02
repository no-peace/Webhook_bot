# Repository Context Group: client_core
# Source Repository: no-peace/Hoho_manager

### File: `client/.env.example`
```example
# Base URL of the Express API.
# Leave empty to use the Vite dev proxy (relative /api calls).
VITE_API_BASE_URL=http://localhost:3001

# Shared secret sent as `x-admin-key` for privileged endpoints such as
# /api/send in bot-token mode. Must match server/.env ADMIN_API_KEY.
# NOTE: anything prefixed with VITE_ is bundled into the client, so this is a
# local-development convenience only. Replace with real auth before deploying.
VITE_ADMIN_API_KEY=dev-admin-key

```

### File: `client/Dockerfile`
```text
# Production-style image: builds the SPA and serves `client/dist` with nginx.
# (Local development does not need this image — `npm run dev` is faster.)
FROM node:22-bookworm-slim AS build

# Base URL of the API, baked into the bundle at build time (Vite inlines all
# VITE_* vars). Empty means same-origin — set it when API and SPA host apart.
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

WORKDIR /app

COPY package.json package-lock.json* tsconfig.base.json ./
COPY shared/package.json shared/tsconfig.json ./shared/
COPY client/package.json client/tsconfig.json ./client/
COPY server/package.json ./server/
RUN npm install --workspace client --include-workspace-root

COPY shared ./shared
COPY client ./client
# @dmb/shared resolves to source via the Vite alias, so no shared build needed.
RUN npm run build --workspace client

FROM nginx:1.27-alpine
COPY --from=build /app/client/dist /usr/share/nginx/html
# SPA fallback: every unknown path serves index.html.
RUN printf 'server {\n\
  listen 80;\n\
  root /usr/share/nginx/html;\n\
  location / {\n\
    try_files $uri $uri/ /index.html;\n\
  }\n\
}\n' > /etc/nginx/conf.d/default.conf
EXPOSE 80

```

### File: `client/index.html`
```html
<!doctype html>
<html lang="en" class="dark">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Discord Message Builder</title>
    <meta
      name="description"
      content="Build and send rich Discord messages — embeds, Components V2 and interactive actions."
    />
    <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect width='24' height='24' rx='6' fill='%235865F2'/%3E%3C/svg%3E" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>

```

### File: `client/package.json`
```json
{
  "name": "client",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "description": "Visual Discord message builder (Discohook-style) — Vite + React + Tailwind + Zustand.",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "typecheck": "tsc -p tsconfig.json --noEmit"
  },
  "dependencies": {
    "@dmb/shared": "*",
    "lucide-react": "^1.48.0",
    "react": "^19.3.0",
    "react-dom": "^19.3.0",
    "zustand": "^5.0.15"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.3.3",
    "@types/node": "^24.10.1",
    "@types/react": "^19.2.7",
    "@types/react-dom": "^19.2.7",
    "@vitejs/plugin-react": "^6.1.1",
    "tailwindcss": "^4.3.3",
    "typescript": "^5.9.3",
    "vite": "^8.3.1",
    "vitest": "^3.2.7"
  },
  "engines": {
    "node": ">=20"
  }
}

```

### File: `client/tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src", "vite-env.d.ts", "vite.config.ts"]
}
```

### File: `client/vite.config.ts`
```ts
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

/**
 * Vite configuration.
 *
 * - `@` aliases the client source root so imports stay short.
 * - `@dmb/shared` points at the shared package's **source**, so editing a shared
 *   constant is picked up by HMR without rebuilding that package. Vite compiles
 *   TypeScript itself, so no build step is needed here.
 * - In development, `/api` is proxied to the Express server so the browser never
 *   needs CORS and the frontend can use relative URLs.
 */
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
      "@dmb/shared": fileURLToPath(new URL("../shared/src/index.ts", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    // Files above the project root (../shared) must be explicitly allowed.
    fs: { allow: [".."] },
    proxy: {
      "/api": {
        target: "http://localhost:3001",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
});

```

### File: `client/vitest.config.ts`
```ts
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vitest/config";

/**
 * Vitest config for the client.
 *
 * Mirrors `vite.config.ts`: `@dmb/shared` resolves to the shared **source** and
 * `@` to the client src root, so tests run against the same code Vite bundles.
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

