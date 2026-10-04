# Orchestrator Plan

## Goal
Deliver a complete, robust, verified refactor of Hoho Manager matching Discohook.app layout, live Discord API fetching, database-backed Settings & bot profile consolidation, and advanced staff permissions with rigorous mention scrubbing.

## Milestone Plan
1. **Survey (Phase 0)**:
   - Explorer 1 (Frontend): Analyze existing React components, current layout, modal/action row building, preview rendering, and Discohook layout clone targets.
   - Explorer 2 (Backend & Database): Analyze FastAPI/Flask/backend routes, database models, `.env` config usage (`LOG_CHANNEL_ID`, Head Admin IDs), settings storage, and migration targets.
   - Explorer 3 (Discord Bot API & Permissions): Analyze bot identity, discord API client/endpoints for guilds/channels/roles/members fetching, staff access model, cooldowns, mention scrubbing implementation across webhooks/bot messages/components V2.
2. **Decomposition & Specification (Phase 1)**:
   - Formulate `PROJECT.md` with Feature Inventory, Architecture, Interface Contracts, and Milestones.
   - Formulate `TEST_INFRA.md` for E2E testing track.
3. **Execution & Verification (Phase 2 & 3)**:
   - Implementation Track (M1-M4) via specialized subagents or sub-orchestrators.
   - E2E Testing Track via dedicated test writer / E2E subagent.
   - Final milestone: Pass 100% E2E tests, followed by Tier 5 adversarial hardening.
4. **Final Acceptance & Reporting (Phase 4)**:
   - Full gate audit verification, final handoff, and victory report to Sentinel.
