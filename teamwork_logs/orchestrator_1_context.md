# Orchestrator Context

## Project Summary
- Project: Hoho Manager (Discord Webhook & Bot Manager)
- Root directory: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot
- Working directory: C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\.agents\teamwork\orchestrator_1
- Parent ID: 66368d85-58fc-46a5-8c5e-c5d8578b67b4

## Core Requirements Overview
- R1: Discohook 3-pane layout clone (Sidebar, Editor, unified Preview), unified preview handling Classic and V2 data, Discord bot avatar loading, intuitive Modals and Action Rows.
- R2: Global "Selected Server (Guild)" dropdown, live searchable Discord API dropdowns for channels/roles/users (with manual ID fallback, no server-side caching of Discord entity data), auto-fetch bot identity on load.
- R3: Settings page/modal for Head Admins only, Bot & Webhook profile management in Settings, migrate `.env` variables (`LOG_CHANNEL_ID`, Head Admin IDs) to database-backed Settings supporting global/guild config.
- R4: Advanced staff permissions: search/fetch members by name (ID as primary key), strict mention scrubbing across bot messages/webhooks/V2 payloads/role IDs/regex, granular cooldowns and max-actions-per-hour, dropdowns for allowed_channel_ids and allowed_role_mention_ids, Staff Access modal backdrop/close handling.
