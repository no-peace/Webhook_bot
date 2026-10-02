# 03 client config

package.json
client/package.json
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


tsconfig.json
client/tsconfig.json
```json
{
  "extends": "../tsconfig.base.json",
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2023", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "types": ["vite/client", "node"],
    "noEmit": true,
    "declaration": false,
    "declarationMap": false,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@dmb/shared": ["../shared/src/index.ts"]
    }
  },
  "include": ["src", "vite.config.ts"]
}
```


Dockerfile
client/Dockerfile
```dockerfile
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


globals.css
client/src/styles/globals.css
```css
@import "tailwindcss";

/*
 * Design system.
 *
 * The palette and control shapes are lifted from Discohook's own Tailwind theme
 * so the editor reads as the same product: a #1E1F22 chrome, #2F3136 cards,
 * rounded-lg controls, and blurple as the single accent.
 *
 * Tailwind v4 is configured in CSS (no tailwind.config.js needed): tokens
 * declared in @theme become real utilities (--color-raised -> bg-raised).
 */
@theme {
  --font-sans: "Whitney", "gg sans", "Noto Sans", "Helvetica Neue", Helvetica, Arial, ui-sans-serif, system-ui, sans-serif;
  --font-code: "Source Code Pro", "Consolas", "Andale Mono WT", "Andale Mono", "Lucida Console", "Lucida Sans Typewriter", "DejaVu Sans Mono", "Bitstream Vera Sans Mono", "Liberation Mono", "Nimbus Mono L", "Monaco", "Courier New", "Courier", "monospace";

  /* Discohook brand colours */
  --color-brand-blue: #58B9FF;
  --color-brand-pink: #FF81FF;

  --color-primary-130: #EFF0F3;
  --color-primary-160: #EBEDEF;
  --color-primary-200: #E3E5E8;
  --color-primary-230: #DBDEE1;
  --color-primary-300: #C4C9CE;
  --color-primary-400: #80848E;
  --color-primary-500: #4E5058;
  --color-primary-600: #2E2E33;
  --color-primary-630: #202225;
  --color-primary-700: #17181A;

  --color-blurple-50: #eef3ff;
  --color-blurple-100: #e0e9ff;
  --color-blurple-200: #c6d6ff;
  --color-blurple-260: #C9CDFB;
  --color-blurple-300: #a4b9fd;
  --color-blurple-400: #8093f9;
  --color-blurple-DEFAULT: #5865f2;
  --color-blurple-500: #5865f2;
  --color-blurple-600: #4654c0;
  --color-blurple-700: #3a48a3;
  --color-blurple-800: #2f2fa4;
  --color-blurple-900: #2d2f82;
  --color-blurple-950: #1a1a4c;

  --color-blue-345: #86AFEF;
  --color-blue-430: #3172DB;

  --color-gray-100: #F3F3F4;
  --color-gray-200: #EAEAEC;
  --color-gray-300: #e3e5e8;
  --color-gray-400: #d4d7dc;
  --color-gray-500: #606069;
  --color-gray-600: #4f545c;
  --color-gray-700: #36393f;
  --color-gray-800: #2f3136;
  --color-gray-900: #202225;

  --color-muted: #5C5E65;
  --color-muted-dark: #959BA3;

  --color-border-normal: #D9D9DC;
  --color-border-normal-dark: #4A4A51;

  /* Surfaces */
  --color-chrome: #1E1F22;   /* header, tab rails, app background */
  --color-sidebar: #2B2D31;  /* side panels */
  --color-surface: #1E1F22;  /* main content background */
  --color-raised: #2F3136;   /* cards, collapsible panels */
  --color-hover: #35373C;
  --color-input: #333338;

  /* Lines */
  --color-line: #404248;
  --color-line-soft: #35373C;

  /* Text */
  --color-ink: #DBDEE1;
  --color-ink-strong: #F2F3F5;
  --color-ink-muted: #959BA3;
  --color-ink-faint: #6D6F78;

  /* Brand + status */
  --color-blurple: #5865f2;
  --color-blurple-hover: #4752c4;
  --color-online: #00863a;
  --color-danger: #d22d39;
  --color-danger-hover: #b42831;
  --color-warning: #f0b132;
  --color-link: #00a8fc;

  --radius-card: 0.5rem;
}

/*
 * Dark-first; these base rules remove browser chrome that would clash with it.
 */
@layer base {
  :root {
    /* Makes native selects, date pickers and scrollbars use a dark palette. */
    color-scheme: dark;
  }

  html,
  body,
  #root {
    height: 100%;
  }

  body {
    @apply bg-chrome text-ink font-sans antialiased;
    margin: 0;
  }

  button {
    cursor: pointer;
  }

  /* Discohook-style scrollbars. */
  * {
    scrollbar-width: thin;
    scrollbar-color: #1A1B1E #2B2D31;
  }

  *::-webkit-scrollbar {
    width: 10px;
    height: 10px;
  }

  *::-webkit-scrollbar-thumb {
    background: #1A1B1E;
    border-radius: 999px;
  }

  *::-webkit-scrollbar-track {
    background: #2B2D31;
    border-radius: 999px;
  }

  :focus-visible {
    outline: 2px solid var(--color-blurple);
    outline-offset: 2px;
  }
}

/* Reusable classes — keeps JSX free of repeated utility soup. */
@layer components {
  /* Discohook's TextInput: rounded-lg, 36px tall, #333338 surface. */
  .field {
    @apply min-h-[36px] w-full rounded-lg border border-border-normal-dark bg-input
           px-3.5 py-2 text-sm text-ink placeholder-ink-faint
           transition focus:border-blue-345 focus:outline-none
           disabled:cursor-not-allowed disabled:text-ink-faint;
  }

  .field-label {
    @apply mb-1 block text-sm font-medium text-ink;
  }

  /* A card. Matches Discohook's collapsible panel (`bg-gray-800`). */
  .panel {
    @apply rounded-lg border border-line-soft bg-raised;
  }

  .panel-header {
    @apply flex items-center justify-between border-b border-line-soft px-3 py-2;
  }

  /* Discohook's tab rail: a rounded #1E1F22 container with pill items. */
  .tab-rail {
    @apply flex gap-0.5 rounded-lg bg-chrome p-0.5 shadow-md;
  }

  .tab-item {
    @apply rounded-lg px-4 py-1.5 text-sm font-medium transition-colors;
  }

  .tab-item-active {
    @apply bg-gray-800 text-ink-strong;
  }

  .tab-item-idle {
    @apply text-ink-muted hover:bg-gray-800 hover:text-ink;
  }

  .link {
    @apply font-medium text-link hover:underline;
  }
}
```
