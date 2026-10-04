# Handoff Report: Frontend Discord OAuth2 Login, Header Integration & Staff Permissions

**Agent**: explorer_m5_2 (Frontend Auth & Header Explorer)  
**Date**: 2026-10-04  
**Milestone**: Milestone 5 — Discord OAuth2 Login & File Attachments  
**Status**: Completed Investigation & Architecture Synthesis  

---

## 1. Observation

### 1.1 Existing Manual Staff Auth in Client Header
Direct inspection of `hoho_manager/client/src/components/layout/Header.tsx` revealed the existing manual staff authentication mechanism:
- Lines 62–78:
```tsx
  const handleStaffClick = () => {
    const current = localStorage.getItem("staff_id");
    if (current) {
      if (confirm(`Log out of Staff ID ${current}?`)) {
        localStorage.removeItem("staff_id");
        window.location.reload();
      }
    } else {
      const id = prompt("Enter your Discord User ID to authenticate as Staff:");
      if (id && /^\d{17,20}$/.test(id)) {
        localStorage.setItem("staff_id", id);
        window.location.reload();
      } else if (id) {
        alert("Invalid Discord ID format. Must be 17-20 digits.");
      }
    }
  };
```
- Lines 142–167:
```tsx
          {import.meta.env.VITE_ADMIN_API_KEY && (
            <button
              type="button"
              onClick={() => setAccessOpen(true)}
              className="text-xs flex items-center gap-1.5 font-semibold text-[#f0b232] hover:text-[#f0b232]/80 border border-[#f0b232]/30 bg-[#f0b232]/10 px-2.5 py-1.5 rounded transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5865f2]"
              title="Staff Access Controls"
            >
              <ShieldAlert size={14} />
              <span className="hidden sm:inline">Staff Access</span>
            </button>
          )}

          <button
            type="button"
            onClick={handleStaffClick}
            className={`text-xs flex items-center gap-1.5 font-semibold px-2.5 py-1.5 rounded transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5865f2] ${
              staffId
                ? "text-[#5865f2] border border-[#5865f2]/40 bg-[#5865f2]/10 hover:bg-[#5865f2]/20"
                : "text-[#dbdee1] border border-[#35373c] bg-[#2b2d31] hover:bg-[#35373c] hover:text-white"
            }`}
            title={staffId ? `Authenticated as Staff (${staffId}) - Click to logout` : "Click to authenticate as Staff"}
          >
            {staffId ? `Staff: ${staffId.slice(-4)}` : "Staff Login"}
          </button>
```

### 1.2 Existing Client API Request Wrapper Missing Session Credentials
In `hoho_manager/client/src/api/client.ts` (lines 49–69):
```ts
export const request = async <T>(path: string, { method = "GET", body, signal }: RequestOptions = {}): Promise<T> => {
  let response: Response;
  const staffId = ENV_STAFF_ID || localStorage.getItem("staff_id") || "";
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers: {
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...(ADMIN_KEY ? { "x-admin-key": ADMIN_KEY } : {}),
        ...(staffId && !ADMIN_KEY ? { "x-staff-id": staffId } : {}),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
    });
```
- **Observations**:
  1. `fetch()` does **not** specify `credentials: "include"`. HTTP-only cookies set by `/api/auth/discord/callback` will not be transmitted on requests requiring credentials.
  2. `staffId` is hardcoded to read from `localStorage.getItem("staff_id")` or `ENV_STAFF_ID`, disconnected from Discord OAuth user sessions.
  3. `body` is unconditionally passed to `JSON.stringify(body)` and given `Content-Type: application/json`, preventing `FormData` uploads needed for Milestone 5 R2 (file attachments).

### 1.3 Discohook Reference Header & User Avatar Implementation
In `discohook_src/packages/site/app/components/Header.tsx` (lines 300–354):
- Logged in: renders user avatar button with `Avatar.Root`, `Avatar.Image`, `Avatar.Fallback`, and username (`user.discordUser?.globalName ?? getUserTag(user)`).
- Logged out: renders a Log In button with a login icon and label "Log In".
- Avatar calculation from `discohook_src/packages/site/app/util/users.ts` (lines 60–82):
  - Custom avatar: `https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png?size={size}`
  - Default avatar fallback: `https://cdn.discordapp.com/embed/avatars/{index}.png` where `index = (BigInt(user.id) >> 22n) % 6n`.

### 1.4 AccessPanel User Grant Flow
In `hoho_manager/client/src/components/layout/AccessPanel.tsx` (lines 111–137):
- When creating access (`isCreating`), the user manually searches or types a snowflake ID into `SearchableDiscordSelect`.
- There is currently no connection to the authenticated user (e.g. "Grant access to my logged-in account").
- In the staff list (lines 262–283), records show usernames and snowflake IDs, but does not indicate whether any record belongs to the active session user `(You)`.

### 1.5 App Mount Lifecycle
In `hoho_manager/client/src/App.tsx` (lines 386–405):
- Mount effect currently fetches action types and auto-fetches bot identity (`api.discord.identity()`).
- Does not currently check `/api/auth/me` to hydrate active Discord OAuth sessions.

### 1.6 Baseline Test & Typecheck Verification
- Executed `npm test` in `hoho_manager/client`: **13 test files passed, 205 tests passed (100% pass rate)**.
- Executed `npm run typecheck` across all packages (`@dmb/shared`, `server`, `client`, `bot`): **0 errors, exited with code 0**.

---

## 2. Logic Chain

1. **OAuth2 Session State Storage**:
   - `useGlobalStore` (`hoho_manager/client/src/store/globalStore.ts`) already holds global UI and identity state (`selectedGuildId`, `botIdentity`, `isSidebarOpen`).
   - Adding `currentUser: { id: string; username: string; global_name?: string | null; avatar: string | null } | null` and `authLoading: boolean` allows any component (`Header`, `AccessPanel`, `App`, `api/client.ts`) to immediately read the authenticated Discord user.
   - Adding `fetchCurrentUser()` and `logout()` directly onto `useGlobalStore` keeps session state centralized, reactive, and easily testable without requiring separate boilerplate providers.

2. **App Mount Session Hydration**:
   - When a user authorizes via Discord OAuth2, the backend callback (`/api/auth/discord/callback`) sets the session cookie and redirects the browser back to `/`.
   - On mount in `App.tsx`, invoking `useGlobalStore.getState().fetchCurrentUser()` issues `GET /api/auth/me`.
   - If a valid session cookie exists, the backend returns `{ user: { id, username, global_name, avatar } }`, hydrating `currentUser` instantly. If unauthenticated, it sets `currentUser: null`.

3. **API Client Synchronization (`api/client.ts`)**:
   - Adding `credentials: "include"` ensures the browser always attaches the HTTP-only session cookie to all `/api/*` requests.
   - For `x-staff-id` header resolution:
     - Priority 1: `useGlobalStore.getState()?.currentUser?.id` (authenticated Discord OAuth user).
     - Priority 2: `localStorage.getItem("staff_id")` (manual fallback for dev and headless testing).
     - Priority 3: `VITE_STAFF_DISCORD_ID` (build-time env).
   - This ensures all API calls automatically transmit authenticated user identity without breaking any existing test mocks that rely on `localStorage` or headers.
   - For Milestone 5 R2 (Multipart / File Attachments), checking `body instanceof FormData` allows `fetch` to send raw `FormData` without injecting `Content-Type: application/json`.

4. **Header UX & Discohook-Fidelity Presentation (`Header.tsx`)**:
   - **When Unauthenticated (`currentUser === null`)**:
     - Replace the `prompt()`-based "Staff Login" button with a Discord Blurple button:
       - Discord Clyde SVG icon (`#ffffff`).
       - Label: "Login with Discord" (`text-xs font-semibold`).
       - Styling: `bg-[#5865f2] hover:bg-[#4752c4] active:bg-[#3c45a5] text-white px-3 py-1.5 rounded-lg shadow-sm transition-colors`.
       - Click handler: `window.location.href = "/api/auth/discord/login"`.
     - Retain an optional subtle manual entry shortcut (e.g., Shift+Click or debug link) if developers or offline testers need to test without live Discord OAuth credentials.
   - **When Authenticated (`currentUser !== null`)**:
     - Render user profile trigger:
       - Circular avatar (`w-7 h-7 rounded-full border border-[#35373c] object-cover`).
       - Discord avatar URL using CDN format `https://cdn.discordapp.com/avatars/${currentUser.id}/${currentUser.avatar}.png` with fallback to `https://cdn.discordapp.com/embed/avatars/${(BigInt(currentUser.id) >> 22n) % 6n}.png`.
       - Username or `global_name` (`text-sm font-medium text-[#dbdee1] truncate max-w-[120px] hidden sm:inline`).
       - `ChevronDown` icon (size 12).
     - On click, toggle a Discohook-native popover dropdown (`bg-[#1e1f22] border border-[#111214] rounded-lg shadow-2xl p-3 w-72 z-50`):
       - User profile banner (Avatar, display name, handle `@username`, and copyable Snowflake ID pill).
       - Staff & Admin status pill: queries `/api/settings/auth` and `/api/access/:id/check` to display "Head Admin", "Staff Active", or "Discord User".
       - Direct buttons to open "Staff Access Controls" or "Head Admin Settings" if authorized.
       - "Log Out" action button (`text-[#f28b8b] hover:bg-[#da373c]/10`) calling `logout()`.

5. **Staff Access Management Integration (`AccessPanel.tsx`)**:
   - At the top of `AccessPanel`, display a "Current Operator" card showing the logged-in user's avatar, username, and ID.
   - In the "Grant New Access" form, provide a quick button: "Grant Access to Myself" that auto-fills `formData.discord_user_id = currentUser.id` and `formData.discord_username = currentUser.username`.
   - In the staff member list, render a distinct `(You)` badge on the row corresponding to `currentUser.id`.

---

## 3. Caveats

1. **Local Development Proxying**:
   - In Vite dev server (`vite.config.ts`), `/api` is proxied to `http://localhost:3001` with `changeOrigin: true`. Same-origin cookies work reliably over localhost.
   - When running in production or tunnel setups, ensure the cookie `SameSite` and `Secure` settings from the backend match the host domain/protocol.
2. **Offline / Test Mode Fallback**:
   - During automated test runs (e.g. Vitest), Discord OAuth endpoints will not be reachable without mocks. The design explicitly preserves the `localStorage.getItem("staff_id")` and `x-staff-id` fallback so all 205 existing tests and test helpers continue to function without modification.

---

## 4. Conclusion & Concrete Implementation Plan

### 4.1 Component & Store Specifications

#### Step 1: Update `hoho_manager/client/src/store/globalStore.ts`
```ts
export interface CurrentUser {
  id: string;
  username: string;
  global_name?: string | null;
  avatar: string | null;
}

// Add to GlobalState interface:
currentUser: CurrentUser | null;
authLoading: boolean;
setCurrentUser: (user: CurrentUser | null) => void;
setAuthLoading: (loading: boolean) => void;
fetchCurrentUser: () => Promise<CurrentUser | null>;
logout: () => Promise<void>;

// In create<GlobalState>((set) => ({ ... })):
currentUser: null,
authLoading: false,
setCurrentUser: (user) => set({ currentUser: user }),
setAuthLoading: (loading) => set({ authLoading: loading }),
fetchCurrentUser: async () => {
  set({ authLoading: true });
  try {
    const { default: api } = await import("../api/client");
    const res = await api.auth.me();
    const user = res?.user ?? null;
    set({ currentUser: user, authLoading: false });
    return user;
  } catch {
    set({ currentUser: null, authLoading: false });
    return null;
  }
},
logout: async () => {
  try {
    const { default: api } = await import("../api/client");
    await api.auth.logout();
  } catch {
    // Ignore logout failure
  } finally {
    set({ currentUser: null });
    if (typeof localStorage !== "undefined") {
      localStorage.removeItem("staff_id");
    }
  }
},
```

#### Step 2: Update `hoho_manager/client/src/api/client.ts`
1. Update `request()` to include `credentials: "include"`, dynamic staff ID resolution, and `FormData` handling:
```ts
import { useGlobalStore } from "../store/globalStore";

export const request = async <T>(path: string, { method = "GET", body, signal }: RequestOptions = {}): Promise<T> => {
  let response: Response;
  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;
  
  // Resolve active staff ID: OAuth session > localStorage > ENV
  const storeUser = typeof window !== "undefined" ? useGlobalStore.getState()?.currentUser : null;
  const staffId = storeUser?.id || (typeof localStorage !== "undefined" ? localStorage.getItem("staff_id") : "") || ENV_STAFF_ID || "";

  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      credentials: "include", // CRITICAL: transmit HTTP-only session cookies
      headers: {
        ...(!isFormData && body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...(ADMIN_KEY ? { "x-admin-key": ADMIN_KEY } : {}),
        ...(staffId && !ADMIN_KEY ? { "x-staff-id": staffId } : {}),
      },
      body: isFormData ? (body as FormData) : (body === undefined ? undefined : JSON.stringify(body)),
      signal,
    });
```
2. Add `api.auth` routes to `api` object:
```ts
auth: {
  me: () => request<{ user: CurrentUser | null }>("/api/auth/me"),
  logout: () => request<{ success: boolean }>("/api/auth/logout", { method: "POST" }),
},
```

#### Step 3: Update `hoho_manager/client/src/components/layout/Header.tsx`
1. Import `useGlobalStore`, `LogOut`, `Shield`, `ShieldCheck`, `Copy`, `Check`.
2. Add Discord Avatar URL helper:
```ts
export const getDiscordAvatarUrl = (user: { id: string; avatar?: string | null }, size: number = 64): string => {
  if (user.avatar) {
    const ext = user.avatar.startsWith("a_") ? "gif" : "png";
    return `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.${ext}?size=${size}`;
  }
  try {
    const index = (BigInt(user.id) >> 22n) % 6n;
    return `https://cdn.discordapp.com/embed/avatars/${index}.png`;
  } catch {
    return "https://cdn.discordapp.com/embed/avatars/0.png";
  }
};
```
3. Add Discord Clyde SVG Icon:
```tsx
const DiscordIcon: React.FC<{ size?: number; className?: string }> = ({ size = 16, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" className={className} aria-hidden="true">
    <path d="M19.27 5.33C17.94 4.71 16.5 4.26 15 4a.09.09 0 0 0-.07.03c-.18.33-.39.76-.53 1.09a16.09 16.09 0 0 0-4.8 0c-.14-.34-.35-.76-.54-1.09-.01-.02-.04-.03-.07-.03-1.5.26-2.93.71-4.27 1.33-.01 0-.02.01-.03.02-2.72 4.07-3.47 8.03-3.1 11.95 0 .02.01.04.03.05 1.8 1.32 3.53 2.12 5.24 2.65.03.01.06 0 .07-.02.4-.55.76-1.13 1.07-1.74.02-.04 0-.08-.04-.09-.57-.22-1.11-.48-1.64-.78-.04-.02-.04-.08-.01-.11.11-.08.22-.17.33-.25.02-.02.05-.02.07-.01 3.44 1.57 7.15 1.57 10.55 0 .02-.01.05-.01.07.01.11.09.22.17.33.26.04.03.04.08-.01.11-.52.31-1.07.56-1.64.78-.04.01-.05.06-.04.09.32.61.68 1.19 1.07 1.74.03.01.06.02.09.01 1.72-.53 3.45-1.33 5.25-2.65.02-.01.03-.03.03-.05.44-4.53-.73-8.46-3.1-11.95-.01-.01-.02-.02-.04-.02zM8.52 14.91c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12 0 1.17-.84 2.12-1.89 2.12zm6.97 0c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12 0 1.17-.83 2.12-1.89 2.12z" />
  </svg>
);
```
4. Render unauthenticated "Login with Discord" button:
```tsx
<button
  type="button"
  onClick={() => { window.location.href = "/api/auth/discord/login"; }}
  className="text-xs flex items-center gap-2 font-semibold bg-[#5865f2] hover:bg-[#4752c4] active:bg-[#3c45a5] text-white px-3 py-1.5 rounded transition-colors shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5865f2]"
>
  <DiscordIcon size={15} />
  <span>Login with Discord</span>
</button>
```
5. Render authenticated User Profile Button & Popover Dropdown:
- Profile trigger button:
  - User avatar (`img` with `getDiscordAvatarUrl(currentUser)`).
  - Username label (`currentUser.global_name || currentUser.username`).
  - Chevron toggle icon.
- Popover dropdown menu:
  - User header with larger avatar, global name, `@username`, and Snowflake ID with copy button.
  - Role pill (Head Admin / Staff Member / Member).
  - Action button: Open Staff Access Controls.
  - Action button: Open Settings.
  - Log Out button: calls `logout()` and refreshes/resets.

#### Step 4: Update `hoho_manager/client/src/components/layout/AccessPanel.tsx`
1. Read `currentUser` from `useGlobalStore`.
2. Render "Authenticated Operator" header summary card.
3. In `handleCreate`, add button "Use My Discord Account" (`formData.discord_user_id = currentUser.id`).
4. In the staff records list, append badge `(You)` to the staff member row matching `currentUser.id`.

#### Step 5: Update `hoho_manager/client/src/App.tsx`
In the initial `useEffect`:
```tsx
useEffect(() => {
  void fetchActionTypes();
  void useGlobalStore.getState().fetchCurrentUser(); // Hydrate OAuth2 session
  ...
}, [fetchActionTypes]);
```

---

## 5. Verification Method

To independently verify the implementation:

1. **Client Unit & Layout Tests**:
   - Run Vitest suite:
     ```pwsh
     cd C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\hoho_manager\client
     npm test
     ```
   - **Pass Criterion**: All 13 test files and 205 tests pass.
2. **Typecheck Baseline**:
   - Run workspace typecheck:
     ```pwsh
     cd C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\hoho_manager
     npm run typecheck
     ```
   - **Pass Criterion**: 0 errors across all 4 workspaces (`@dmb/shared`, `server`, `client`, `bot`).
3. **Frontend Build Verification**:
   - Run production Vite build:
     ```pwsh
     cd C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\hoho_manager\client
     npm run build
     ```
   - **Pass Criterion**: Build succeeds with 0 TypeScript/Vite bundling errors and outputs to `dist/`.
4. **Interactive Auth & Header Verification**:
   - Navigate to `http://localhost:5173`.
   - When not logged in: verify the "Login with Discord" blurple button is rendered in the top right.
   - When clicked, verify browser navigates to `/api/auth/discord/login`.
   - When authenticated: verify user avatar and name are displayed; click profile to verify dropdown menu with copyable ID and working "Log Out" button.
   - Open Staff Access modal: verify logged-in user info appears and "Grant to myself" populates the form.
5. **Invalidation Conditions**:
   - If `npm run typecheck` or `npm test` fails.
   - If manual ID entry cannot be used as fallback in test environments.
   - If `/api` requests fail to include credentials when communicating with Express.
