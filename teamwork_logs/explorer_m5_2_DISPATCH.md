# DISPATCH — explorer_m5_2

## Identity
- Role: Frontend Auth & Header Explorer
- Working directory: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_2\
- Archetype: teamwork_preview_explorer

## Mission
Investigate the frontend architecture for Milestone 5 (Discord OAuth2 Login and User Header Integration) in `hoho_manager/client`.

## Context & Inputs
- User Request: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\ORIGINAL_REQUEST.md
- Project Scope: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\orchestrator_5\SCOPE.md
- Project Plan: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\PROJECT.md
- Reference: `discohook_src/packages/site/app/components/Header.tsx` (if available)

## Detailed Tasks
1. Inspect `hoho_manager/client/src/` components, specifically:
   - `components/layout/Header.tsx`
   - `components/layout/AccessPanel.tsx`
   - `stores/useGlobalStore.ts`
   - Any API client utilities (`api.ts` or fetch helpers)
2. Plan the OAuth2 Frontend Integration:
   - Session State: How `useGlobalStore` should store `currentUser: { id: string, username: string, avatar: string | null } | null`, `authLoading: boolean`.
   - On app mount: How the frontend checks `/api/auth/me` to restore the active Discord session.
   - Header UX:
     * When unauthenticated: Show sleek "Login with Discord" button (Discord blurple / Discohook styling) that directs to `/api/auth/discord/login`.
     * When authenticated: Display Discord avatar (circular image or fallback initial), username/display name in Header top-right. Add a dropdown menu with user details, status, and a "Log Out" button (calling `/api/auth/logout`).
   - Staff Access & Permission Integration:
     * How the authenticated user's ID replaces manual staff ID entry.
     * In `AccessPanel.tsx`, display the authenticated user info directly rather than a raw manual input, or auto-fill and lock to the authenticated ID.
     * Ensure all API requests automatically pass or leverage session auth credentials.
3. Check Discohook styling in `discohook_src` for header user element and modals/buttons.
4. Deliver a comprehensive report with concrete file paths, component structures, state changes, and step-by-step implementation plan.
5. Write your report to `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_2\handoff.md`.


## 2026-10-04T04:51:11Z
From: 20f80e23-1201-4637-bfaa-c6b5a078c66d
Priority: MESSAGE_PRIORITY_HIGH

You are explorer_m5_2.
Working directory: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_2\
Read your instructions in: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_2\DISPATCH.md
Read the user's original request: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\ORIGINAL_REQUEST.md
Read the project overview: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\PROJECT.md
Read the milestone scope: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\orchestrator_5\SCOPE.md

Your role is Frontend Auth & Header Explorer.
Investigate hoho_manager/client frontend architecture for Discord OAuth2 Login, Header user profile and avatar rendering matching Discohook, and linking authenticated user ID to staff permissions.
Perform your investigation, synthesize your findings and actionable implementation recommendations, and write your report to C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_2\handoff.md.
When finished, notify your parent with send_message including your handoff report path.
