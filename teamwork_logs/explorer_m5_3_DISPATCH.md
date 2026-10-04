# DISPATCH — explorer_m5_3

## Identity
- Role: File Attachments & Discohook Spec Miner Explorer
- Working directory: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_3\
- Archetype: teamwork_preview_explorer

## Mission
Investigate the File Attachments & Media Upload architecture for Milestone 5 in both frontend (`hoho_manager/client`) and Discord API payload specs, referencing Discohook.

## Context & Inputs
- User Request: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\ORIGINAL_REQUEST.md
- Project Scope: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\orchestrator_5\SCOPE.md
- Project Plan: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\PROJECT.md
- Reference: `discohook_src/packages/site/app/` (check how Discohook handles attachments/files if present)

## Detailed Tasks
1. Inspect `hoho_manager/client/src/components/editor/MessageEditor.tsx` and related message editor components.
2. Check how files/attachments should be modeled in the message state (e.g. array of `{ id: string, file: File, name: string, size: number, type: string, previewUrl?: string }`).
3. Design the "File Attachments" UI component:
   - Section in `MessageEditor.tsx` (collapsible accordion or dedicated card matching Discohook's `#1e1f22` dark theme).
   - "Upload File" / "Add Attachment" button and drag-and-drop file target.
   - List of attached files: display filename, formatted file size (e.g. KB/MB), thumbnail/icon, and remove button.
   - Validation & limits (file size limit e.g. 25MB max per Discord default, total count limit e.g. up to 10 files).
4. Investigate the Send flow:
   - How `MessageEditor` or `App.tsx` sends messages to `/api/send`.
   - When files are present, how the client packages the send request: `FormData` with `payload_json` (stringified message JSON) and `files` (array of `File` objects).
5. Investigate Discord API expectations:
   - For Discord webhooks and bot message create: multipart/form-data with `payload_json` containing message data and `attachments` metadata array (`[{ id: 0, filename: "foo.png", description?: string }]`), plus `files[0]` matching each attachment ID.
   - Verify compatibility with both Webhook execution (`POST /webhooks/:id/:token`) and Bot message create (`POST /channels/:id/messages`).
6. Deliver a comprehensive report with file paths, component wireframes/code structures, exact payload formats, and edge cases.
7. Write your report to `C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_3\handoff.md`.

## 2026-10-04T04:51:11Z
[Message] sender=20f80e23-1201-4637-bfaa-c6b5a078c66d
You are explorer_m5_3.
Working directory: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_3\
Read your instructions in: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_3\DISPATCH.md
Read the user's original request: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\ORIGINAL_REQUEST.md
Read the project overview: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\PROJECT.md
Read the milestone scope: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\orchestrator_5\SCOPE.md

Your role is File Attachments & Discohook Spec Miner Explorer.
Investigate MessageEditor file attachments UI (matching Discohook aesthetic) and Discord API attachments protocol (multipart/form-data payload_json + files[n]).
Perform your investigation, synthesize your findings and actionable implementation recommendations, and write your report to C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_3\handoff.md.
When finished, notify your parent with send_message including your handoff report path.
