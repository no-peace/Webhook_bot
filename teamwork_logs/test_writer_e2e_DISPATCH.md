# Task Assignment: E2E Test Suite Creation

## Working Directory
`C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\test_writer_e2e`

## Mandatory Reference Documents
- Master Specification: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\ORIGINAL_REQUEST.md`
- Project Master Plan: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\PROJECT.md`
- Test Infrastructure Index: `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\TEST_INFRA.md`
- Live Running App URL: `http://localhost:5175/` (Backend: `http://localhost:3001/`)

## File Ownership
You exclusively own and may edit files in:
- `hoho_manager/server/tests/e2e/` (or create new test files under `hoho_manager/server/tests/`)
- `hoho_manager/client/tests/`
- Root test scripts if needed

Do NOT modify application source code in `server/src` or `client/src`.

## Scope of Work

Design and implement comprehensive automated opaque-box test suites covering all requirements (R1, R2, R3, R4) across the 4 systematic tiers defined in `TEST_INFRA.md`:

1. **Tier 1 — Feature Coverage (>=5 tests per feature)**:
   - F5: Guild list API fetching, selecting guild, returning proper shape.
   - F6: Channels, roles, member search endpoints functionality and input handling.
   - F7: Manual snowflake ID validation and fallback.
   - F8: Bot identity fetching endpoint (`GET /api/send/identity`).
   - F9: Settings endpoint Head Admin authorization (`x-admin-key`, `x-staff-id`, unauthenticated 401/403).
   - F11: Database-backed settings persistence (`log_channel_id`, `head_admin_ids`).
   - F12: Staff member search by name.
   - F13: Mention scrubbing across all vectors (`@everyone`, `@here`, role mentions).
   - F17: Channel allowlist default-deny (empty allowlist denies all channels).
   - F14: Granular cooldowns and max-actions per hour.

2. **Tier 2 — Boundary & Corner Cases (>=5 tests per feature)**:
   - Case-insensitive bypass attempts (`@Everyone`, `@EVERYONE`, `@hErE`).
   - Empty allowlists, wildcard `*` allowlists, invalid snowflake IDs, malformed JSON bodies.
   - Edge cases in rate limits and cooldown expirations.
   - Non-head-admin staff trying to modify settings or bot profiles.

3. **Tier 3 — Cross-Feature Interaction**:
   - Guild context driving channel/role resolution combined with staff permission validation.
   - Mention scrubbing combined with Component V2 flows registration.
   - Dynamic `log_channel_id` updating in settings and immediately impacting audit log destination.

4. **Tier 4 — Real-World Application Workloads**:
   - Full flow: Head Admin sets up audit log and staff permissions -> Staff member sends scoped message -> Mention scrubbing sanitizes disallowed pings -> Audit log entry recorded with correct channel.
   - Full flow: Malicious staff attempts bypass via Component V2 payload or case variations -> Scrubbed and rejected appropriately.

5. **Execution & Documentation**:
   - Run the test suite: `npm test` across server and client.
   - When all tests are created and documented, create `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\TEST_READY.md` summarizing the test suite, test commands, and tier coverage breakdown.

## Completion Deliverables
Write `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\test_writer_e2e\handoff.md`.
Notify the orchestrator via `send_message` when done.


## 2026-10-03T09:58:06Z
Read your task assignment in C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\test_writer_e2e\DISPATCH.md.
Follow all instructions and file ownership rules.
Design and implement the comprehensive E2E test suite across Tiers 1-4 for Hoho Manager.
Run your test suites to verify them.
Create C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\TEST_READY.md when complete.
Write your handoff report to C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\test_writer_e2e\handoff.md and notify me via send_message when done.
