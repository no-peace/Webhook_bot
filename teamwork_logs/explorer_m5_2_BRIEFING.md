# BRIEFING — 2026-10-04T04:58:00Z

## Mission
Investigate hoho_manager/client frontend architecture for Discord OAuth2 Login, Header user profile and avatar rendering matching Discohook, and linking authenticated user ID to staff permissions.

## 🔒 My Identity
- Archetype: teamwork_preview_explorer
- Roles: Frontend Auth & Header Explorer
- Working directory: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_2\
- Original parent: 20f80e23-1201-4637-bfaa-c6b5a078c66d
- Milestone: Milestone 5 (Discord OAuth2 Login and User Header Integration)

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- All output in .agents/teamwork/explorer_m5_2/ (metadata only, no source/test files here)
- Provide exact file paths, line numbers, and concrete component designs
- Self-contained 5-component handoff report

## Current Parent
- Conversation ID: 20f80e23-1201-4637-bfaa-c6b5a078c66d
- Updated: 2026-10-04T04:58:00Z

## Investigation State
- **Explored paths**:
  - `discohook_src/packages/site/app/components/Header.tsx` (Discohook header, user avatar, drawer & styling patterns)
  - `discohook_src/packages/site/app/util/users.ts` (getUserAvatar, Discord CDN URLs)
  - `hoho_manager/client/src/components/layout/Header.tsx` (Current header, manual staff prompt, top-right controls)
  - `hoho_manager/client/src/components/layout/AccessPanel.tsx` (Staff access management modal and user selector)
  - `hoho_manager/client/src/store/globalStore.ts` (Current global store architecture)
  - `hoho_manager/client/src/api/client.ts` (Fetch request wrapper, headers, staff ID, lack of credentials)
  - `hoho_manager/client/src/App.tsx` (App layout, mount initialization, identity auto-fetch)
  - `hoho_manager/server/src/middleware/staffPermissions.ts` & `auth.ts` (Backend staff and head admin checks)
  - `hoho_manager/shared/src/types.ts` (Shared types and models)
- **Key findings**:
  - Manual staff login in `Header.tsx` (prompting for 17-20 digit ID and writing to localStorage) needs replacement with Discord OAuth2 login button.
  - `api/client.ts` currently lacks `credentials: "include"`, which is mandatory for HTTP-only session cookies.
  - `api/client.ts` needs dynamic staffId integration referencing `currentUser.id` with fallback to `localStorage` for backwards test compatibility.
  - `useGlobalStore.ts` requires `currentUser`, `authLoading`, `fetchCurrentUser()`, and `logout()`.
  - `AccessPanel.tsx` should display current authenticated operator and provide an autofill "Grant to myself" action.
  - Header user component should match Discohook (#1e1f22, circular avatar, username, and dropdown with logout).
  - All 205 existing client tests and typechecks pass; recommendations are 100% backwards-compatible.
- **Unexplored areas**: None for frontend scope.

## Key Decisions Made
- Architecture designed for zero breaking changes: `currentUser.id` takes precedence while maintaining `localStorage` fallback for tests.
- Dropdown menu approach chosen for Header authenticated user, providing quick access to user info, copyable Snowflake ID, permissions summary, and logout.

## Artifact Index
- C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_2\DISPATCH.md — Dispatch instructions
- C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_2\BRIEFING.md — Persistent working memory
- C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_2\progress.md — Liveness heartbeat and milestone checklist
- C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_2\handoff.md — Comprehensive analysis and implementation plan
