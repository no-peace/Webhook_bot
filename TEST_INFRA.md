# E2E Test Infra: Hoho Manager Refactor

## Test Philosophy
- Opaque-box, requirement-driven.
- Verifies system behaviors directly through API endpoints, HTTP requests, and integration flows without mock dependencies where possible.
- 4-Tier Methodology: Category-Partition (Tier 1), Boundary Value Analysis (Tier 2), Cross-Feature Interaction (Tier 3), and Real-World Application Workloads (Tier 4), followed by Tier 5 adversarial stress testing.

## Feature Inventory Mapping
| # | Feature | Requirement | Tier 1 | Tier 2 | Tier 3 |
|---|---------|-------------|:------:|:------:|:------:|
| 1 | Discohook 3-Pane Layout & Live Preview | R1 | 5 | 5 | ✓ |
| 2 | Bot Avatar in Live Preview | R1 | 5 | 5 | ✓ |
| 3 | Visual Action Rows & Modal Building | R1 | 5 | 5 | ✓ |
| 4 | Global Guild Context & Dynamic API Fetching | R2 | 5 | 5 | ✓ |
| 5 | Manual ID Fallback with Searchable Comboboxes | R2 | 5 | 5 | ✓ |
| 6 | Auto-Fetch Bot Identity on Startup | R2 | 5 | 5 | ✓ |
| 7 | Database Settings & Head Admin Authorization | R3 | 5 | 5 | ✓ |
| 8 | Dynamic `LOG_CHANNEL_ID` & Head Admin IDs in DB | R3 | 5 | 5 | ✓ |
| 9 | Bot & Webhook Profile Management in Settings | R3 | 5 | 5 | ✓ |
| 10 | Staff Search by Name & Member Lookup | R4 | 5 | 5 | ✓ |
| 11 | Zero-Bypass Mention Scrubbing across All Paths | R4 | 5 | 5 | ✓ |
| 12 | Channel Allowlist Default-Deny Security | R4 | 5 | 5 | ✓ |
| 13 | Granular Cooldowns & Max Actions per Hour | R4 | 5 | 5 | ✓ |
| 14 | Staff Access Modal Backdrop & Close Navigation | R4 | 5 | 5 | ✓ |

## Test Architecture
- Test Runner: Node.js / Vitest automated test suite executing E2E and integration tests.
- Runner Location: `hoho_manager/server/tests/e2e` and `hoho_manager/client/tests`
- Verification Semantics:
  - Tests verify live HTTP responses, database mutations, and rendered HTML/DOM structures.
  - Zero mock bypasses: all security assertions test the actual middleware and sanitizers.
- Pass/Fail Semantics: Clean exit code 0, 100% test assertions pass.

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Head Admin Configures Guild Settings & Logs | F5, F7, F8, F9, F11 | High |
| 2 | Staff Member Granted Scoped Channels & Roles Sends Announcement | F5, F6, F7, F12, F13, F14, F17 | High |
| 3 | Malicious Mention Injection Attempt Blocked Across All Channels | F11, F13, F17 | High |
| 4 | Component V2 Multi-Button Workflow Design & Preview | F1, F2, F3, F4 | Medium |
| 5 | Staff Access Panel Workflow: Open, Edit Permissions, Dismiss Backdrop | F12, F14, F15, F16 | Medium |

## Coverage Thresholds
- Tier 1: ≥5 per feature
- Tier 2: ≥5 boundary/corner test cases
- Tier 3: Pairwise coverage of cross-feature interactions
- Tier 4: ≥5 realistic end-to-end scenarios
- Tier 5: Adversarial penetration and bypass attempts
