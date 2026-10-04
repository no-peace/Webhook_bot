# Implementation Plan: Discohook Clone & Action System

Goal Description
The objective is to fix the current crash/stuck errors related to Components V2, redesign the frontend to perfectly match the aesthetic of discohook_src, add the highly requested "Action" tab to power multi-step conditional workflows, and finally update the documentation.

User Review Required
IMPORTANT

Because discohook_src uses Remix and our bot_src uses Vite + React, I will be extracting and adapting the exact Tailwind utility classes, layouts, and colors from discohook_src's React components into bot_src's components rather than directly copy-pasting incompatible framework files. **Resolved: approved.**
The reskin keeps bot_src's Vite/React structure and ports Discohook's design tokens,
control shapes (rounded-lg inputs/buttons), `#1E1F22` chrome, `#2F3136` cards and the
vertical tab rail into it. The Flow tab was built in the same style rather than copied.

Open Questions
NOTE

Do you want the multi-step action flows to support conditional branching (e.g. "if user has role X, do Y, else do Z"), or just linear sequences (e.g. "step 1, step 2, step 3") for now?

**Resolved: multi-step flows with nested conditional branches.** The Flow tab builds an
ordered chain (`add_role`, `remove_role`, `toggle_role`, `send_dm`,
`send_ephemeral_reply`, `send_message`, `send_webhook_message`, `open_modal`,
`delete_message`, `create_thread`, `wait`, `set_variable`, `check`). Steps run top to
bottom and stop at the first visible reply. `check` evaluates conditions server-side
and supports nested **Then** and **Else** step lists in the builder.

Proposed Changes
Backend & Component V2 Fixes
[MODIFY] bot_src/server/src/utils/validation.ts
The recursion in walkComponents currently does not abort properly when the component limit is reached; it just returns from the callback while the loop continues, potentially causing a CPU block on large payloads. I will fix this by introducing a strict depth limit (Discord's max nesting depth) and properly short-circuiting the recursion. I will also add a timeout to checkRows to prevent any possibility of the server getting stuck.

[MODIFY] bot_src/server/src/services/actionExecutor.ts
Extend the action executor to support "multi-step flows" and conditional execution steps.

Frontend Styling Clone
[MODIFY] bot_src/client/tailwind.config.js
Copy the design tokens (colors, spacing, fonts) from discohook_src/packages/site/tailwind.config.ts.

[MODIFY] bot_src/client/src/styles/globals.css
Copy the base layer styles and custom CSS variables from discohook_src.

[MODIFY] bot_src/client/src/components/layout/*
Rebuild Header, Sidebar, and SplitPane to match Discohook's layout pixel-for-pixel using their exact Tailwind classes.

[MODIFY] bot_src/client/src/components/editor/*
Redesign the property panels and message editor to match Discohook. Add a new "Action" tab to interactive components (Buttons, Selects) where users can visually build multi-step flows (e.g., Add Role -> Send DM -> Ephemeral Reply).

Documentation
[MODIFY] docs/LOCAL_DEVELOPMENT.md & docs/DEPLOYMENT.md
[MODIFY] bot_src/README.md
Update the guides to reflect the new features (Action System flows) and ensure they are accurate.

Verification Plan
Automated Tests
I will run npm run test (if available) and npm run build for both client and server workspaces to ensure there are no TypeScript compilation errors.

Manual Verification
Open the preview editor locally and confirm it visually matches Discohook.
Build a Component V2 message with a nested button, assign a multi-step action, and trigger it to ensure the server processes it quickly and correctly without getting stuck.
