# DISPATCH — explorer_m5_remediation_2

## Identity
- Role: Explorer 2 (Discohook Layout Parity & External URL Attachments)
- Archetype: teamwork_preview_explorer
- Working directory: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_remediation_2\

## CRITICAL USER INSTRUCTION
The user has already directly fixed the "Select Server" dropdown bug using `createPortal` with fixed positioning in `SearchableDiscordSelect.tsx`.
DO NOT TOUCH, MODIFY, OR REVERT `SearchableDiscordSelect.tsx`!

## Mission
Investigate and formulate concrete technical design and implementation steps for:
1. **Replicate Discohook's Exact Layout & Move Component Elements/Palette Out of Drawer**:
   - User feedback: "The component elements/palette was put in the toolbox/drawer, which makes it hard to build messages because the user has to keep opening it. You must replicate Discohook's exact layout for where the palette and editor actions go. Literally make everything the same as Discohook's layout."
   - Check Discohook reference source in `discohook_src/packages/site/app/`:
     * `routes/_index.tsx`
     * `components/editor/MessageEditor.client.tsx`
     * `components/editor/` (ActionRowEditor, ComponentEditor, etc.)
   - Check existing client implementation in `hoho_manager/client/src/components/`:
     * `editor/MessageEditor.tsx`
     * `editor/ComponentBuilder.tsx`
     * `editor/EmbedEditor.tsx`
     * `layout/Sidebar.tsx` / `Toolbox.tsx`
   - Map out how Discohook exposes editor action buttons (+ Add Embed, + Action Row / Components, + Files / Attachments) directly within the editor pane workflow, without hiding them in an off-canvas drawer.
   - Specify the exact structure, styles, colors (`#1e1f22`, `#2b2d31`, `#313338`, `#383a40`, Discord blurple `#5865f2`), and layout proportions.
2. **External URL Attachment Support**:
   - User feedback: "The user wants the new File Attachments UI to also support inputting external URLs for files/images (just like Discohook does), in addition to local file uploads. Please ensure the worker builds this into the new layout as well."
   - Check `hoho_manager/client/src/components/editor/FileAttachmentsSection.tsx` and `hoho_manager/client/src/store/messageStore.ts`.
   - Check how Discohook handles URL attachments vs local uploads in `discohook_src/packages/site/app/`.
   - Propose data model and UI: adding attachment by URL input, card rendering with preview, remove button, spoiler toggle, and payload handling.

## Reference Files
- ORIGINAL_REQUEST: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\ORIGINAL_REQUEST.md
- PROJECT: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\PROJECT.md
- SCOPE: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\orchestrator_6\SCOPE.md

Write your report to:
`C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\explorer_m5_remediation_2\analysis.md`
When complete, notify orchestrator via send_message.
