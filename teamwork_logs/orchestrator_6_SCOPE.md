# Scope: Milestone 5 Remediation (Iteration 2)

## Architecture & Context
Hoho Manager is a Discord webhook and bot manager built with React, Vite, Tailwind CSS, Express, TypeScript, and SQLite.
Milestone 5 adds Discord OAuth2 login, file attachments, and addresses UI layout parity with Discohook.app (`discohook_src/packages/site/app/`).

## Feature Inventory
| # | Feature | Description | Milestone | Status |
|---|---------|-------------|-----------|--------|
| 1 | Select Server (Guild) Fix | User already fixed directly in `SearchableDiscordSelect.tsx` using `createPortal`. DO NOT TOUCH / DO NOT REVERT. | M5 Remediation | SKIPPED (Completed by User) |
| 2 | Discohook Editor Layout Parity | Move component elements / palette out of the drawer and place them directly in the editor area (matching Discohook layout from `discohook_src/packages/site/app/`). Match Classic & V2 styling, spacing, and colors. | M5 Remediation | Pending |
| 3 | External URL File Attachments | In `FileAttachmentsSection.tsx`, support adding attachments via external URLs alongside local uploads & drag-and-drop. | M5 Remediation | Pending |
| 4 | Multi-Select Channels in Bot Dispatch | Channel selector in `BotDispatchModal.tsx` supports multi-select (array of target channels) to send/edit across multiple channels. | M5 Remediation | Pending |
| 5 | Knowledge Preservation (.md copy) | Recursively copy all `.md` files from `.agents/teamwork/` into `docs/` (e.g. `docs/teamwork/`). Copy, NEVER move! | M5 Remediation | Pending |
| 6 | Documentation Updates | Update `docs/DEPLOYMENT.md`, `docs/LOCAL_DEVELOPMENT.md`, `docs/PTERODACTYL_DEPLOYMENT.md`, and `chatwithantigravity.md` with OAuth2 env vars, file attachments, and multi-channel dispatch. | M5 Remediation | Pending |
| 7 | Full Quality Gate Verification | Zero typecheck errors, all server and client tests pass, 2 Reviewers, 2 Challengers, 1 Forensic Auditor. | M5 Remediation | Pending |

## Critical Constraints
- **DO NOT TOUCH OR REVERT** the user's dropdown fix in `SearchableDiscordSelect.tsx`.
- All subagents must specify `Model: "inherit"`.
