# Repository Context Group: drizzle_misc
# Source Repository: discohook/discohook

### File: `drizzle/0000_flawless_william_stryker.sql`
```sql
CREATE TABLE IF NOT EXISTS "Backup" (
	"id" bigint PRIMARY KEY NOT NULL,
	"name" text NOT NULL,
	"updatedAt" timestamp,
	"dataVersion" text NOT NULL,
	"data" json NOT NULL,
	"previewImageUrl" text,
	"importedFromOrg" boolean DEFAULT false NOT NULL,
	"scheduled" boolean DEFAULT false NOT NULL,
	"nextRunAt" timestamp,
	"lastRunData" json,
	"cron" text,
	"timezone" text,
	"ownerId" bigint NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "CustomBot" (
	"id" bigint PRIMARY KEY NOT NULL,
	"applicationId" bigint NOT NULL,
	"applicationUserId" bigint,
	"icon" text,
	"publicKey" text NOT NULL,
	"clientSecret" text,
	"token" text,
	"discriminator" text,
	"avatar" text,
	"name" text NOT NULL,
	"ownerId" bigint NOT NULL,
	"guildId" bigint,
	CONSTRAINT "CustomBot_applicationId_unique" UNIQUE("applicationId")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "DiscordGuild" (
	"id" bigint PRIMARY KEY NOT NULL,
	"name" text DEFAULT 'Unknown Server' NOT NULL,
	"icon" text
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "DiscordGuild_to_Backup" (
	"discordGuildId" bigint NOT NULL,
	"backupId" bigint NOT NULL,
	CONSTRAINT "DiscordGuild_to_Backup_discordGuildId_backupId_pk" PRIMARY KEY("discordGuildId","backupId")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "DiscordMember" (
	"userId" bigint NOT NULL,
	"guildId" bigint NOT NULL,
	"permissions" text DEFAULT '0' NOT NULL,
	"owner" boolean DEFAULT false NOT NULL,
	CONSTRAINT "DiscordMember_userId_guildId_unique" UNIQUE("userId","guildId")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "DiscordMessageComponent" (
	"id" bigint PRIMARY KEY NOT NULL,
	"guildId" bigint,
	"channelId" bigint,
	"messageId" bigint,
	"createdById" bigint,
	"updatedById" bigint,
	"updatedAt" timestamp,
	"type" integer NOT NULL,
	"data" json NOT NULL,
	"draft" boolean DEFAULT false NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "DMC_to_Flow" (
	"dmcId" bigint NOT NULL,
	"flowId" bigint NOT NULL,
	CONSTRAINT "DMC_to_Flow_dmcId_flowId_pk" PRIMARY KEY("dmcId","flowId")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "reaction_roles" (
	"message_id" bigint NOT NULL,
	"channel_id" bigint NOT NULL,
	"guild_id" bigint NOT NULL,
	"role_id" bigint NOT NULL,
	"reaction" text NOT NULL,
	CONSTRAINT "reaction_roles_message_id_reaction_pk" PRIMARY KEY("message_id","reaction")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "DiscordRoles" (
	"id" bigint NOT NULL,
	"guildId" bigint NOT NULL,
	"name" text NOT NULL,
	"color" integer DEFAULT 0,
	"permissions" text DEFAULT '0',
	"icon" text,
	"unicodeEmoji" text,
	"position" integer NOT NULL,
	"hoist" boolean DEFAULT false,
	"managed" boolean DEFAULT false,
	"mentionable" boolean DEFAULT false,
	CONSTRAINT "DiscordRoles_id_unique" UNIQUE("id"),
	CONSTRAINT "DiscordRoles_id_guildId_unique" UNIQUE("id","guildId")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "DiscordUser" (
	"id" bigint PRIMARY KEY NOT NULL,
	"name" text NOT NULL,
	"globalName" text,
	"discriminator" text,
	"avatar" text
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "Action" (
	"id" bigint PRIMARY KEY NOT NULL,
	"type" integer NOT NULL,
	"data" json NOT NULL,
	"flowId" bigint NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "Flow" (
	"id" bigint PRIMARY KEY NOT NULL,
	"name" text
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "GithubPost" (
	"id" bigint PRIMARY KEY NOT NULL,
	"platform" text NOT NULL,
	"type" text NOT NULL,
	"githubId" bigint NOT NULL,
	"repositoryOwner" text NOT NULL,
	"repositoryName" text NOT NULL,
	"channelId" text NOT NULL,
	"postId" text NOT NULL,
	CONSTRAINT "GithubPost_postId_unique" UNIQUE("postId"),
	CONSTRAINT "GithubPost_platform_channelId_type_githubId_unique" UNIQUE("platform","channelId","type","githubId")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "GuildedServer" (
	"id" text PRIMARY KEY NOT NULL,
	"name" text NOT NULL,
	"avatarUrl" text
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "GuildedUser" (
	"id" text PRIMARY KEY NOT NULL,
	"name" text NOT NULL,
	"avatarUrl" text
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "LinkBackup" (
	"id" bigint PRIMARY KEY NOT NULL,
	"code" text NOT NULL,
	"name" text NOT NULL,
	"updatedAt" timestamp,
	"dataVersion" text NOT NULL,
	"data" json NOT NULL,
	"previewImageUrl" text,
	"ownerId" bigint NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "MessageLogEntry" (
	"id" bigint PRIMARY KEY NOT NULL,
	"type" text,
	"webhookId" text NOT NULL,
	"discordGuildId" bigint,
	"guildedServerId" text,
	"channelId" text NOT NULL,
	"messageId" text NOT NULL,
	"threadId" text,
	"userId" bigint,
	"notifiedEveryoneHere" boolean DEFAULT false,
	"notifiedRoles" json,
	"notifiedUsers" json,
	"hasContent" boolean DEFAULT false,
	"embedCount" integer DEFAULT 0
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "OAuthInfo" (
	"id" bigint PRIMARY KEY NOT NULL,
	"discordId" bigint,
	"guildedId" text,
	"botId" bigint,
	"accessToken" text NOT NULL,
	"refreshToken" text,
	"scope" json NOT NULL,
	"expiresAt" timestamp NOT NULL,
	CONSTRAINT "OAuthInfo_discordId_unique" UNIQUE("discordId"),
	CONSTRAINT "OAuthInfo_guildedId_unique" UNIQUE("guildedId"),
	CONSTRAINT "OAuthInfo_botId_unique" UNIQUE("botId")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "ShareLink" (
	"id" bigint PRIMARY KEY NOT NULL,
	"shareId" text NOT NULL,
	"expiresAt" timestamp NOT NULL,
	"origin" text,
	"userId" bigint
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "Token" (
	"id" bigint PRIMARY KEY NOT NULL,
	"platform" text NOT NULL,
	"prefix" text NOT NULL,
	"userId" bigint,
	"expiresAt" timestamp NOT NULL,
	"lastUsedAt" timestamp,
	"lastUsedCountry" text
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "Trigger" (
	"id" bigint PRIMARY KEY NOT NULL,
	"platform" text NOT NULL,
	"event" integer NOT NULL,
	"discordGuildId" bigint,
	"guildedServerId" text,
	"flowId" bigint NOT NULL,
	"updatedById" bigint,
	"updatedAt" timestamp,
	"disabled" boolean DEFAULT false NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "User" (
	"id" bigint PRIMARY KEY NOT NULL,
	"name" text NOT NULL,
	"firstSubscribed" timestamp,
	"subscribedSince" timestamp,
	"subscriptionExpiresAt" timestamp,
	"lifetime" boolean DEFAULT false,
	"discordId" bigint,
	"guildedId" text,
	CONSTRAINT "User_discordId_unique" UNIQUE("discordId"),
	CONSTRAINT "User_guildedId_unique" UNIQUE("guildedId")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "Webhook" (
	"platform" text NOT NULL,
	"id" text NOT NULL,
	"token" text,
	"name" text NOT NULL,
	"avatar" text,
	"channelId" text NOT NULL,
	"applicationId" text,
	"userId" bigint,
	"discordGuildId" bigint,
	"guildedServerId" text,
	CONSTRAINT "Webhook_platform_id_unique" UNIQUE("platform","id")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "autopublish" (
	"channel_id" bigint NOT NULL,
	"added_by_id" bigint,
	"ignore" text
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "buttons" (
	"guild_id" bigint,
	"channel_id" bigint,
	"message_id" bigint,
	"role_id" bigint,
	"style" text,
	"custom_label" text,
	"emoji" text,
	"url" text,
	"custom_ephemeral_message_data" text,
	"custom_dm_message_data" text,
	"custom_id" text,
	"role_ids" bigint[],
	"type" text,
	"custom_public_message_data" text,
	"id" serial NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "message_settings" (
	"guild_id" bigint,
	"channel_id" bigint,
	"message_id" bigint NOT NULL,
	"max_roles" integer
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "welcomer_goodbye" (
	"guild_id" bigint NOT NULL,
	"channel_id" bigint,
	"webhook_id" bigint,
	"webhook_token" text,
	"message_data" text,
	"last_modified_at" timestamp,
	"last_modified_by_id" bigint,
	"override_disabled" boolean,
	"ignore_bots" boolean,
	"delete_messages_after" integer,
	"id" serial NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "welcomer_hello" (
	"guild_id" bigint NOT NULL,
	"channel_id" bigint,
	"webhook_id" bigint,
	"webhook_token" text,
	"message_data" text,
	"last_modified_at" timestamp,
	"last_modified_by_id" bigint,
	"override_disabled" boolean,
	"ignore_bots" boolean,
	"delete_messages_after" integer,
	"id" serial NOT NULL
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "Backup" ADD CONSTRAINT "Backup_ownerId_User_id_fk" FOREIGN KEY ("ownerId") REFERENCES "public"."User"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "CustomBot" ADD CONSTRAINT "CustomBot_ownerId_User_id_fk" FOREIGN KEY ("ownerId") REFERENCES "public"."User"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "CustomBot" ADD CONSTRAINT "CustomBot_guildId_DiscordGuild_id_fk" FOREIGN KEY ("guildId") REFERENCES "public"."DiscordGuild"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "DiscordGuild_to_Backup" ADD CONSTRAINT "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk" FOREIGN KEY ("discordGuildId") REFERENCES "public"."DiscordGuild"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "DiscordGuild_to_Backup" ADD CONSTRAINT "DiscordGuild_to_Backup_backupId_Backup_id_fk" FOREIGN KEY ("backupId") REFERENCES "public"."Backup"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "DiscordMember" ADD CONSTRAINT "DiscordMember_userId_DiscordUser_id_fk" FOREIGN KEY ("userId") REFERENCES "public"."DiscordUser"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "DiscordMember" ADD CONSTRAINT "DiscordMember_guildId_DiscordGuild_id_fk" FOREIGN KEY ("guildId") REFERENCES "public"."DiscordGuild"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "DMC_to_Flow" ADD CONSTRAINT "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk" FOREIGN KEY ("dmcId") REFERENCES "public"."DiscordMessageComponent"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "DMC_to_Flow" ADD CONSTRAINT "DMC_to_Flow_flowId_Flow_id_fk" FOREIGN KEY ("flowId") REFERENCES "public"."Flow"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "reaction_roles" ADD CONSTRAINT "reaction_roles_guild_id_DiscordGuild_id_fk" FOREIGN KEY ("guild_id") REFERENCES "public"."DiscordGuild"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "DiscordRoles" ADD CONSTRAINT "DiscordRoles_guildId_DiscordGuild_id_fk" FOREIGN KEY ("guildId") REFERENCES "public"."DiscordGuild"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "Action" ADD CONSTRAINT "Action_flowId_Flow_id_fk" FOREIGN KEY ("flowId") REFERENCES "public"."Flow"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "LinkBackup" ADD CONSTRAINT "LinkBackup_ownerId_User_id_fk" FOREIGN KEY ("ownerId") REFERENCES "public"."User"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "MessageLogEntry" ADD CONSTRAINT "MessageLogEntry_discordGuildId_DiscordGuild_id_fk" FOREIGN KEY ("discordGuildId") REFERENCES "public"."DiscordGuild"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "MessageLogEntry" ADD CONSTRAINT "MessageLogEntry_guildedServerId_GuildedServer_id_fk" FOREIGN KEY ("guildedServerId") REFERENCES "public"."GuildedServer"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "ShareLink" ADD CONSTRAINT "ShareLink_userId_User_id_fk" FOREIGN KEY ("userId") REFERENCES "public"."User"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "Token" ADD CONSTRAINT "Token_userId_User_id_fk" FOREIGN KEY ("userId") REFERENCES "public"."User"("id") ON DELETE set null ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "Trigger" ADD CONSTRAINT "Trigger_flowId_Flow_id_fk" FOREIGN KEY ("flowId") REFERENCES "public"."Flow"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;

```

### File: `drizzle/0001_hot_sunspot.sql`
```sql
ALTER TABLE "DiscordGuild" ADD COLUMN "ownerDiscordId" bigint;
```

### File: `drizzle/0002_mature_thing.sql`
```sql
ALTER TABLE "DiscordGuild" ADD COLUMN "botJoinedAt" timestamp;
```

### File: `drizzle/0003_fat_george_stacy.sql`
```sql
CREATE TABLE IF NOT EXISTS "scheduled_posts" (
	"id" serial NOT NULL,
	"user_id" bigint,
	"guild_id" bigint,
	"message_data" json,
	"webhook_id" bigint,
	"webhook_token" text,
	"future" timestamp,
	"error" text
);

```

### File: `drizzle/0004_ancient_gorgon.sql`
```sql
CREATE TABLE IF NOT EXISTS "UserToWebhook" (
	"userId" bigint NOT NULL,
	"webhookPlatform" text NOT NULL,
	"webhookId" text NOT NULL,
	"favorite" boolean DEFAULT false NOT NULL,
	CONSTRAINT "UserToWebhook_userId_webhookPlatform_webhookId_unique" UNIQUE("userId","webhookPlatform","webhookId")
);
--> statement-breakpoint
ALTER TABLE "DiscordMember" ADD COLUMN "favorite" boolean DEFAULT false NOT NULL;--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "UserToWebhook" ADD CONSTRAINT "UserToWebhook_userId_User_id_fk" FOREIGN KEY ("userId") REFERENCES "public"."User"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "UserToWebhook" ADD CONSTRAINT "UserToWebhook_fk" FOREIGN KEY ("webhookPlatform","webhookId") REFERENCES "public"."Webhook"("platform","id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;

```

### File: `drizzle/0005_flow-flattening.sql`
```sql
ALTER TABLE "Trigger" ALTER COLUMN "platform" SET DEFAULT 'discord';--> statement-breakpoint
ALTER TABLE "Trigger" ALTER COLUMN "flowId" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "Trigger" ADD COLUMN "flow" json;
```

### File: `drizzle/0006_json-columns.sql`
```sql
-- We updated from 0.32.1 in February 2026:
-- https://github.com/drizzle-team/drizzle-orm/releases/tag/0.33.0
UPDATE "OAuthInfo" SET scope = (scope #>> '{}')::json;--> statement-breakpoint
UPDATE "Backup" SET data = (data #>> '{}')::json;--> statement-breakpoint
UPDATE "Backup" SET "lastRunData" = ("lastRunData" #>> '{}')::json;--> statement-breakpoint
UPDATE "LinkBackup" SET data = (data #>> '{}')::json;--> statement-breakpoint
UPDATE "MessageLogEntry" SET "notifiedRoles" = ("notifiedRoles" #>> '{}')::json;--> statement-breakpoint
UPDATE "MessageLogEntry" SET "notifiedUsers" = ("notifiedUsers" #>> '{}')::json;--> statement-breakpoint
UPDATE "DiscordMessageComponent" SET data = (data #>> '{}')::json;--> statement-breakpoint
UPDATE "Action" SET data = (data #>> '{}')::json;

```

### File: `drizzle/0007_update-at-default-now.sql`
```sql
ALTER TABLE "Backup" ALTER COLUMN "updatedAt" SET DEFAULT now();--> statement-breakpoint
ALTER TABLE "DiscordMessageComponent" ALTER COLUMN "updatedAt" SET DEFAULT now();--> statement-breakpoint
ALTER TABLE "LinkBackup" ALTER COLUMN "updatedAt" SET DEFAULT now();--> statement-breakpoint
ALTER TABLE "Trigger" ALTER COLUMN "updatedAt" SET DEFAULT now();
```

### File: `drizzle/0008_update-at-default-now-utc.sql`
```sql
ALTER TABLE "Backup" ALTER COLUMN "updatedAt" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "DiscordMessageComponent" ALTER COLUMN "updatedAt" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "LinkBackup" ALTER COLUMN "updatedAt" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "Trigger" ALTER COLUMN "updatedAt" DROP DEFAULT;
```

### File: `drizzle/0009_no-guilded.sql`
```sql
ALTER TABLE "GuildedServer" DISABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE "GuildedUser" DISABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE "OAuthInfo" DROP CONSTRAINT "OAuthInfo_guildedId_unique";--> statement-breakpoint
ALTER TABLE "User" DROP CONSTRAINT "User_guildedId_unique";--> statement-breakpoint
ALTER TABLE "MessageLogEntry" DROP CONSTRAINT "MessageLogEntry_guildedServerId_GuildedServer_id_fk";
--> statement-breakpoint
DROP TABLE "GuildedServer" CASCADE;--> statement-breakpoint
DROP TABLE "GuildedUser" CASCADE;--> statement-breakpoint
ALTER TABLE "MessageLogEntry" DROP COLUMN "guildedServerId";--> statement-breakpoint
ALTER TABLE "OAuthInfo" DROP COLUMN "guildedId";--> statement-breakpoint
ALTER TABLE "Trigger" DROP COLUMN "guildedServerId";--> statement-breakpoint
ALTER TABLE "User" DROP COLUMN "guildedId";--> statement-breakpoint
ALTER TABLE "Webhook" DROP COLUMN "guildedServerId";
```

### File: `drizzle/0010_saved-attachments.sql`
```sql
CREATE TABLE "SavedAttachment" (
	"id" bigint PRIMARY KEY NOT NULL,
	"filename" text NOT NULL,
	"url" text NOT NULL,
	"title" text,
	"description" text,
	"contentType" text NOT NULL,
	"discordMessageId" bigint,
	"discordGuildId" bigint NOT NULL,
	"userId" bigint
);
--> statement-breakpoint
ALTER TABLE "DiscordGuild" ADD COLUMN "attachmentChannelId" bigint;--> statement-breakpoint
ALTER TABLE "SavedAttachment" ADD CONSTRAINT "SavedAttachment_discordGuildId_DiscordGuild_id_fk" FOREIGN KEY ("discordGuildId") REFERENCES "public"."DiscordGuild"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "SavedAttachment" ADD CONSTRAINT "SavedAttachment_userId_User_id_fk" FOREIGN KEY ("userId") REFERENCES "public"."User"("id") ON DELETE set null ON UPDATE no action;
```

### File: `drizzle/meta/0000_snapshot.json`
```json
{
  "id": "0a9b61f0-71c9-455a-8ad4-322af8d024f4",
  "prevId": "00000000-0000-0000-0000-000000000000",
  "version": "7",
  "dialect": "postgresql",
  "tables": {
    "public.Backup": {
      "name": "Backup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "importedFromOrg": {
          "name": "importedFromOrg",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "scheduled": {
          "name": "scheduled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "nextRunAt": {
          "name": "nextRunAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastRunData": {
          "name": "lastRunData",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "cron": {
          "name": "cron",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "timezone": {
          "name": "timezone",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Backup_ownerId_User_id_fk": {
          "name": "Backup_ownerId_User_id_fk",
          "tableFrom": "Backup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.CustomBot": {
      "name": "CustomBot",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "applicationUserId": {
          "name": "applicationUserId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "publicKey": {
          "name": "publicKey",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "clientSecret": {
          "name": "clientSecret",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "CustomBot_ownerId_User_id_fk": {
          "name": "CustomBot_ownerId_User_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "CustomBot_guildId_DiscordGuild_id_fk": {
          "name": "CustomBot_guildId_DiscordGuild_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "CustomBot_applicationId_unique": {
          "name": "CustomBot_applicationId_unique",
          "nullsNotDistinct": false,
          "columns": ["applicationId"]
        }
      }
    },
    "public.DiscordGuild": {
      "name": "DiscordGuild",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'Unknown Server'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.DiscordGuild_to_Backup": {
      "name": "DiscordGuild_to_Backup",
      "schema": "",
      "columns": {
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "backupId": {
          "name": "backupId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordGuild_to_Backup_backupId_Backup_id_fk": {
          "name": "DiscordGuild_to_Backup_backupId_Backup_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "Backup",
          "columnsFrom": ["backupId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DiscordGuild_to_Backup_discordGuildId_backupId_pk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_backupId_pk",
          "columns": ["discordGuildId", "backupId"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.DiscordMember": {
      "name": "DiscordMember",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'0'"
        },
        "owner": {
          "name": "owner",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordMember_userId_DiscordUser_id_fk": {
          "name": "DiscordMember_userId_DiscordUser_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordUser",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordMember_guildId_DiscordGuild_id_fk": {
          "name": "DiscordMember_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordMember_userId_guildId_unique": {
          "name": "DiscordMember_userId_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "guildId"]
        }
      }
    },
    "public.DiscordMessageComponent": {
      "name": "DiscordMessageComponent",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "messageId": {
          "name": "messageId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "createdById": {
          "name": "createdById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "draft": {
          "name": "draft",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.DMC_to_Flow": {
      "name": "DMC_to_Flow",
      "schema": "",
      "columns": {
        "dmcId": {
          "name": "dmcId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk": {
          "name": "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "DiscordMessageComponent",
          "columnsFrom": ["dmcId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DMC_to_Flow_flowId_Flow_id_fk": {
          "name": "DMC_to_Flow_flowId_Flow_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DMC_to_Flow_dmcId_flowId_pk": {
          "name": "DMC_to_Flow_dmcId_flowId_pk",
          "columns": ["dmcId", "flowId"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.reaction_roles": {
      "name": "reaction_roles",
      "schema": "",
      "columns": {
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "reaction": {
          "name": "reaction",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "reaction_roles_guild_id_DiscordGuild_id_fk": {
          "name": "reaction_roles_guild_id_DiscordGuild_id_fk",
          "tableFrom": "reaction_roles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guild_id"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "reaction_roles_message_id_reaction_pk": {
          "name": "reaction_roles_message_id_reaction_pk",
          "columns": ["message_id", "reaction"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.DiscordRoles": {
      "name": "DiscordRoles",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "color": {
          "name": "color",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": false,
          "default": "'0'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "unicodeEmoji": {
          "name": "unicodeEmoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "position": {
          "name": "position",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "hoist": {
          "name": "hoist",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "managed": {
          "name": "managed",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "mentionable": {
          "name": "mentionable",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordRoles_guildId_DiscordGuild_id_fk": {
          "name": "DiscordRoles_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordRoles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordRoles_id_unique": {
          "name": "DiscordRoles_id_unique",
          "nullsNotDistinct": false,
          "columns": ["id"]
        },
        "DiscordRoles_id_guildId_unique": {
          "name": "DiscordRoles_id_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["id", "guildId"]
        }
      }
    },
    "public.DiscordUser": {
      "name": "DiscordUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "globalName": {
          "name": "globalName",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Action": {
      "name": "Action",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Action_flowId_Flow_id_fk": {
          "name": "Action_flowId_Flow_id_fk",
          "tableFrom": "Action",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Flow": {
      "name": "Flow",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.GithubPost": {
      "name": "GithubPost",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "githubId": {
          "name": "githubId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryOwner": {
          "name": "repositoryOwner",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryName": {
          "name": "repositoryName",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "postId": {
          "name": "postId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "GithubPost_postId_unique": {
          "name": "GithubPost_postId_unique",
          "nullsNotDistinct": false,
          "columns": ["postId"]
        },
        "GithubPost_platform_channelId_type_githubId_unique": {
          "name": "GithubPost_platform_channelId_type_githubId_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "channelId", "type", "githubId"]
        }
      }
    },
    "public.GuildedServer": {
      "name": "GuildedServer",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.GuildedUser": {
      "name": "GuildedUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.LinkBackup": {
      "name": "LinkBackup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "code": {
          "name": "code",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "LinkBackup_ownerId_User_id_fk": {
          "name": "LinkBackup_ownerId_User_id_fk",
          "tableFrom": "LinkBackup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.MessageLogEntry": {
      "name": "MessageLogEntry",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "messageId": {
          "name": "messageId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "threadId": {
          "name": "threadId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedEveryoneHere": {
          "name": "notifiedEveryoneHere",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "notifiedRoles": {
          "name": "notifiedRoles",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedUsers": {
          "name": "notifiedUsers",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "hasContent": {
          "name": "hasContent",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "embedCount": {
          "name": "embedCount",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        }
      },
      "indexes": {},
      "foreignKeys": {
        "MessageLogEntry_discordGuildId_DiscordGuild_id_fk": {
          "name": "MessageLogEntry_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "MessageLogEntry_guildedServerId_GuildedServer_id_fk": {
          "name": "MessageLogEntry_guildedServerId_GuildedServer_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "GuildedServer",
          "columnsFrom": ["guildedServerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.OAuthInfo": {
      "name": "OAuthInfo",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "botId": {
          "name": "botId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "accessToken": {
          "name": "accessToken",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "refreshToken": {
          "name": "refreshToken",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "scope": {
          "name": "scope",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "OAuthInfo_discordId_unique": {
          "name": "OAuthInfo_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "OAuthInfo_guildedId_unique": {
          "name": "OAuthInfo_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        },
        "OAuthInfo_botId_unique": {
          "name": "OAuthInfo_botId_unique",
          "nullsNotDistinct": false,
          "columns": ["botId"]
        }
      }
    },
    "public.ShareLink": {
      "name": "ShareLink",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "shareId": {
          "name": "shareId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "origin": {
          "name": "origin",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "ShareLink_userId_User_id_fk": {
          "name": "ShareLink_userId_User_id_fk",
          "tableFrom": "ShareLink",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Token": {
      "name": "Token",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "prefix": {
          "name": "prefix",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "lastUsedAt": {
          "name": "lastUsedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastUsedCountry": {
          "name": "lastUsedCountry",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Token_userId_User_id_fk": {
          "name": "Token_userId_User_id_fk",
          "tableFrom": "Token",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "set null",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Trigger": {
      "name": "Trigger",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "event": {
          "name": "event",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "disabled": {
          "name": "disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Trigger_flowId_Flow_id_fk": {
          "name": "Trigger_flowId_Flow_id_fk",
          "tableFrom": "Trigger",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.User": {
      "name": "User",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "firstSubscribed": {
          "name": "firstSubscribed",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscribedSince": {
          "name": "subscribedSince",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscriptionExpiresAt": {
          "name": "subscriptionExpiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lifetime": {
          "name": "lifetime",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "User_discordId_unique": {
          "name": "User_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "User_guildedId_unique": {
          "name": "User_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        }
      }
    },
    "public.Webhook": {
      "name": "Webhook",
      "schema": "",
      "columns": {
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "Webhook_platform_id_unique": {
          "name": "Webhook_platform_id_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "id"]
        }
      }
    },
    "public.autopublish": {
      "name": "autopublish",
      "schema": "",
      "columns": {
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "added_by_id": {
          "name": "added_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "ignore": {
          "name": "ignore",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.buttons": {
      "name": "buttons",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "style": {
          "name": "style",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_label": {
          "name": "custom_label",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "emoji": {
          "name": "emoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "url": {
          "name": "url",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_ephemeral_message_data": {
          "name": "custom_ephemeral_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_dm_message_data": {
          "name": "custom_dm_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_id": {
          "name": "custom_id",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "role_ids": {
          "name": "role_ids",
          "type": "bigint[]",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_public_message_data": {
          "name": "custom_public_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.message_settings": {
      "name": "message_settings",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "max_roles": {
          "name": "max_roles",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.welcomer_goodbye": {
      "name": "welcomer_goodbye",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.welcomer_hello": {
      "name": "welcomer_hello",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    }
  },
  "enums": {},
  "schemas": {},
  "_meta": {
    "columns": {},
    "schemas": {},
    "tables": {}
  }
}

```

### File: `drizzle/meta/0001_snapshot.json`
```json
{
  "id": "6ed0a597-9331-4b7c-bd28-c61485fe46ec",
  "prevId": "0a9b61f0-71c9-455a-8ad4-322af8d024f4",
  "version": "7",
  "dialect": "postgresql",
  "tables": {
    "public.Backup": {
      "name": "Backup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "importedFromOrg": {
          "name": "importedFromOrg",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "scheduled": {
          "name": "scheduled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "nextRunAt": {
          "name": "nextRunAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastRunData": {
          "name": "lastRunData",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "cron": {
          "name": "cron",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "timezone": {
          "name": "timezone",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Backup_ownerId_User_id_fk": {
          "name": "Backup_ownerId_User_id_fk",
          "tableFrom": "Backup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.CustomBot": {
      "name": "CustomBot",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "applicationUserId": {
          "name": "applicationUserId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "publicKey": {
          "name": "publicKey",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "clientSecret": {
          "name": "clientSecret",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "CustomBot_ownerId_User_id_fk": {
          "name": "CustomBot_ownerId_User_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "CustomBot_guildId_DiscordGuild_id_fk": {
          "name": "CustomBot_guildId_DiscordGuild_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "CustomBot_applicationId_unique": {
          "name": "CustomBot_applicationId_unique",
          "nullsNotDistinct": false,
          "columns": ["applicationId"]
        }
      }
    },
    "public.DiscordGuild": {
      "name": "DiscordGuild",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'Unknown Server'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerDiscordId": {
          "name": "ownerDiscordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.DiscordGuild_to_Backup": {
      "name": "DiscordGuild_to_Backup",
      "schema": "",
      "columns": {
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "backupId": {
          "name": "backupId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordGuild_to_Backup_backupId_Backup_id_fk": {
          "name": "DiscordGuild_to_Backup_backupId_Backup_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "Backup",
          "columnsFrom": ["backupId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DiscordGuild_to_Backup_discordGuildId_backupId_pk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_backupId_pk",
          "columns": ["discordGuildId", "backupId"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.DiscordMember": {
      "name": "DiscordMember",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'0'"
        },
        "owner": {
          "name": "owner",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordMember_userId_DiscordUser_id_fk": {
          "name": "DiscordMember_userId_DiscordUser_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordUser",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordMember_guildId_DiscordGuild_id_fk": {
          "name": "DiscordMember_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordMember_userId_guildId_unique": {
          "name": "DiscordMember_userId_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "guildId"]
        }
      }
    },
    "public.DiscordMessageComponent": {
      "name": "DiscordMessageComponent",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "messageId": {
          "name": "messageId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "createdById": {
          "name": "createdById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "draft": {
          "name": "draft",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.DMC_to_Flow": {
      "name": "DMC_to_Flow",
      "schema": "",
      "columns": {
        "dmcId": {
          "name": "dmcId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk": {
          "name": "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "DiscordMessageComponent",
          "columnsFrom": ["dmcId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DMC_to_Flow_flowId_Flow_id_fk": {
          "name": "DMC_to_Flow_flowId_Flow_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DMC_to_Flow_dmcId_flowId_pk": {
          "name": "DMC_to_Flow_dmcId_flowId_pk",
          "columns": ["dmcId", "flowId"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.reaction_roles": {
      "name": "reaction_roles",
      "schema": "",
      "columns": {
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "reaction": {
          "name": "reaction",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "reaction_roles_guild_id_DiscordGuild_id_fk": {
          "name": "reaction_roles_guild_id_DiscordGuild_id_fk",
          "tableFrom": "reaction_roles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guild_id"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "reaction_roles_message_id_reaction_pk": {
          "name": "reaction_roles_message_id_reaction_pk",
          "columns": ["message_id", "reaction"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.DiscordRoles": {
      "name": "DiscordRoles",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "color": {
          "name": "color",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": false,
          "default": "'0'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "unicodeEmoji": {
          "name": "unicodeEmoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "position": {
          "name": "position",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "hoist": {
          "name": "hoist",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "managed": {
          "name": "managed",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "mentionable": {
          "name": "mentionable",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordRoles_guildId_DiscordGuild_id_fk": {
          "name": "DiscordRoles_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordRoles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordRoles_id_unique": {
          "name": "DiscordRoles_id_unique",
          "nullsNotDistinct": false,
          "columns": ["id"]
        },
        "DiscordRoles_id_guildId_unique": {
          "name": "DiscordRoles_id_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["id", "guildId"]
        }
      }
    },
    "public.DiscordUser": {
      "name": "DiscordUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "globalName": {
          "name": "globalName",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Action": {
      "name": "Action",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Action_flowId_Flow_id_fk": {
          "name": "Action_flowId_Flow_id_fk",
          "tableFrom": "Action",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Flow": {
      "name": "Flow",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.GithubPost": {
      "name": "GithubPost",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "githubId": {
          "name": "githubId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryOwner": {
          "name": "repositoryOwner",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryName": {
          "name": "repositoryName",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "postId": {
          "name": "postId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "GithubPost_postId_unique": {
          "name": "GithubPost_postId_unique",
          "nullsNotDistinct": false,
          "columns": ["postId"]
        },
        "GithubPost_platform_channelId_type_githubId_unique": {
          "name": "GithubPost_platform_channelId_type_githubId_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "channelId", "type", "githubId"]
        }
      }
    },
    "public.GuildedServer": {
      "name": "GuildedServer",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.GuildedUser": {
      "name": "GuildedUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.LinkBackup": {
      "name": "LinkBackup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "code": {
          "name": "code",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "LinkBackup_ownerId_User_id_fk": {
          "name": "LinkBackup_ownerId_User_id_fk",
          "tableFrom": "LinkBackup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.MessageLogEntry": {
      "name": "MessageLogEntry",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "messageId": {
          "name": "messageId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "threadId": {
          "name": "threadId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedEveryoneHere": {
          "name": "notifiedEveryoneHere",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "notifiedRoles": {
          "name": "notifiedRoles",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedUsers": {
          "name": "notifiedUsers",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "hasContent": {
          "name": "hasContent",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "embedCount": {
          "name": "embedCount",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        }
      },
      "indexes": {},
      "foreignKeys": {
        "MessageLogEntry_discordGuildId_DiscordGuild_id_fk": {
          "name": "MessageLogEntry_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "MessageLogEntry_guildedServerId_GuildedServer_id_fk": {
          "name": "MessageLogEntry_guildedServerId_GuildedServer_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "GuildedServer",
          "columnsFrom": ["guildedServerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.OAuthInfo": {
      "name": "OAuthInfo",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "botId": {
          "name": "botId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "accessToken": {
          "name": "accessToken",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "refreshToken": {
          "name": "refreshToken",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "scope": {
          "name": "scope",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "OAuthInfo_discordId_unique": {
          "name": "OAuthInfo_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "OAuthInfo_guildedId_unique": {
          "name": "OAuthInfo_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        },
        "OAuthInfo_botId_unique": {
          "name": "OAuthInfo_botId_unique",
          "nullsNotDistinct": false,
          "columns": ["botId"]
        }
      }
    },
    "public.ShareLink": {
      "name": "ShareLink",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "shareId": {
          "name": "shareId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "origin": {
          "name": "origin",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "ShareLink_userId_User_id_fk": {
          "name": "ShareLink_userId_User_id_fk",
          "tableFrom": "ShareLink",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Token": {
      "name": "Token",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "prefix": {
          "name": "prefix",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "lastUsedAt": {
          "name": "lastUsedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastUsedCountry": {
          "name": "lastUsedCountry",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Token_userId_User_id_fk": {
          "name": "Token_userId_User_id_fk",
          "tableFrom": "Token",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "set null",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Trigger": {
      "name": "Trigger",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "event": {
          "name": "event",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "disabled": {
          "name": "disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Trigger_flowId_Flow_id_fk": {
          "name": "Trigger_flowId_Flow_id_fk",
          "tableFrom": "Trigger",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.User": {
      "name": "User",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "firstSubscribed": {
          "name": "firstSubscribed",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscribedSince": {
          "name": "subscribedSince",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscriptionExpiresAt": {
          "name": "subscriptionExpiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lifetime": {
          "name": "lifetime",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "User_discordId_unique": {
          "name": "User_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "User_guildedId_unique": {
          "name": "User_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        }
      }
    },
    "public.Webhook": {
      "name": "Webhook",
      "schema": "",
      "columns": {
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "Webhook_platform_id_unique": {
          "name": "Webhook_platform_id_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "id"]
        }
      }
    },
    "public.autopublish": {
      "name": "autopublish",
      "schema": "",
      "columns": {
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "added_by_id": {
          "name": "added_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "ignore": {
          "name": "ignore",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.buttons": {
      "name": "buttons",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "style": {
          "name": "style",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_label": {
          "name": "custom_label",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "emoji": {
          "name": "emoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "url": {
          "name": "url",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_ephemeral_message_data": {
          "name": "custom_ephemeral_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_dm_message_data": {
          "name": "custom_dm_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_id": {
          "name": "custom_id",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "role_ids": {
          "name": "role_ids",
          "type": "bigint[]",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_public_message_data": {
          "name": "custom_public_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.message_settings": {
      "name": "message_settings",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "max_roles": {
          "name": "max_roles",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.welcomer_goodbye": {
      "name": "welcomer_goodbye",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.welcomer_hello": {
      "name": "welcomer_hello",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    }
  },
  "enums": {},
  "schemas": {},
  "sequences": {},
  "_meta": {
    "columns": {},
    "schemas": {},
    "tables": {}
  }
}

```

### File: `drizzle/meta/0002_snapshot.json`
```json
{
  "id": "e837debb-6384-494c-9e1d-dde85dac5154",
  "prevId": "6ed0a597-9331-4b7c-bd28-c61485fe46ec",
  "version": "7",
  "dialect": "postgresql",
  "tables": {
    "public.Backup": {
      "name": "Backup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "importedFromOrg": {
          "name": "importedFromOrg",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "scheduled": {
          "name": "scheduled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "nextRunAt": {
          "name": "nextRunAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastRunData": {
          "name": "lastRunData",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "cron": {
          "name": "cron",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "timezone": {
          "name": "timezone",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Backup_ownerId_User_id_fk": {
          "name": "Backup_ownerId_User_id_fk",
          "tableFrom": "Backup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.CustomBot": {
      "name": "CustomBot",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "applicationUserId": {
          "name": "applicationUserId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "publicKey": {
          "name": "publicKey",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "clientSecret": {
          "name": "clientSecret",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "CustomBot_ownerId_User_id_fk": {
          "name": "CustomBot_ownerId_User_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "CustomBot_guildId_DiscordGuild_id_fk": {
          "name": "CustomBot_guildId_DiscordGuild_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "CustomBot_applicationId_unique": {
          "name": "CustomBot_applicationId_unique",
          "nullsNotDistinct": false,
          "columns": ["applicationId"]
        }
      }
    },
    "public.DiscordGuild": {
      "name": "DiscordGuild",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'Unknown Server'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerDiscordId": {
          "name": "ownerDiscordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "botJoinedAt": {
          "name": "botJoinedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.DiscordGuild_to_Backup": {
      "name": "DiscordGuild_to_Backup",
      "schema": "",
      "columns": {
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "backupId": {
          "name": "backupId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordGuild_to_Backup_backupId_Backup_id_fk": {
          "name": "DiscordGuild_to_Backup_backupId_Backup_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "Backup",
          "columnsFrom": ["backupId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DiscordGuild_to_Backup_discordGuildId_backupId_pk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_backupId_pk",
          "columns": ["discordGuildId", "backupId"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.DiscordMember": {
      "name": "DiscordMember",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'0'"
        },
        "owner": {
          "name": "owner",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordMember_userId_DiscordUser_id_fk": {
          "name": "DiscordMember_userId_DiscordUser_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordUser",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordMember_guildId_DiscordGuild_id_fk": {
          "name": "DiscordMember_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordMember_userId_guildId_unique": {
          "name": "DiscordMember_userId_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "guildId"]
        }
      }
    },
    "public.DiscordMessageComponent": {
      "name": "DiscordMessageComponent",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "messageId": {
          "name": "messageId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "createdById": {
          "name": "createdById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "draft": {
          "name": "draft",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.DMC_to_Flow": {
      "name": "DMC_to_Flow",
      "schema": "",
      "columns": {
        "dmcId": {
          "name": "dmcId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk": {
          "name": "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "DiscordMessageComponent",
          "columnsFrom": ["dmcId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DMC_to_Flow_flowId_Flow_id_fk": {
          "name": "DMC_to_Flow_flowId_Flow_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DMC_to_Flow_dmcId_flowId_pk": {
          "name": "DMC_to_Flow_dmcId_flowId_pk",
          "columns": ["dmcId", "flowId"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.reaction_roles": {
      "name": "reaction_roles",
      "schema": "",
      "columns": {
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "reaction": {
          "name": "reaction",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "reaction_roles_guild_id_DiscordGuild_id_fk": {
          "name": "reaction_roles_guild_id_DiscordGuild_id_fk",
          "tableFrom": "reaction_roles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guild_id"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "reaction_roles_message_id_reaction_pk": {
          "name": "reaction_roles_message_id_reaction_pk",
          "columns": ["message_id", "reaction"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.DiscordRoles": {
      "name": "DiscordRoles",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "color": {
          "name": "color",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": false,
          "default": "'0'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "unicodeEmoji": {
          "name": "unicodeEmoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "position": {
          "name": "position",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "hoist": {
          "name": "hoist",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "managed": {
          "name": "managed",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "mentionable": {
          "name": "mentionable",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordRoles_guildId_DiscordGuild_id_fk": {
          "name": "DiscordRoles_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordRoles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordRoles_id_unique": {
          "name": "DiscordRoles_id_unique",
          "nullsNotDistinct": false,
          "columns": ["id"]
        },
        "DiscordRoles_id_guildId_unique": {
          "name": "DiscordRoles_id_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["id", "guildId"]
        }
      }
    },
    "public.DiscordUser": {
      "name": "DiscordUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "globalName": {
          "name": "globalName",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Action": {
      "name": "Action",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Action_flowId_Flow_id_fk": {
          "name": "Action_flowId_Flow_id_fk",
          "tableFrom": "Action",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Flow": {
      "name": "Flow",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.GithubPost": {
      "name": "GithubPost",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "githubId": {
          "name": "githubId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryOwner": {
          "name": "repositoryOwner",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryName": {
          "name": "repositoryName",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "postId": {
          "name": "postId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "GithubPost_postId_unique": {
          "name": "GithubPost_postId_unique",
          "nullsNotDistinct": false,
          "columns": ["postId"]
        },
        "GithubPost_platform_channelId_type_githubId_unique": {
          "name": "GithubPost_platform_channelId_type_githubId_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "channelId", "type", "githubId"]
        }
      }
    },
    "public.GuildedServer": {
      "name": "GuildedServer",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.GuildedUser": {
      "name": "GuildedUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.LinkBackup": {
      "name": "LinkBackup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "code": {
          "name": "code",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "LinkBackup_ownerId_User_id_fk": {
          "name": "LinkBackup_ownerId_User_id_fk",
          "tableFrom": "LinkBackup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.MessageLogEntry": {
      "name": "MessageLogEntry",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "messageId": {
          "name": "messageId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "threadId": {
          "name": "threadId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedEveryoneHere": {
          "name": "notifiedEveryoneHere",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "notifiedRoles": {
          "name": "notifiedRoles",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedUsers": {
          "name": "notifiedUsers",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "hasContent": {
          "name": "hasContent",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "embedCount": {
          "name": "embedCount",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        }
      },
      "indexes": {},
      "foreignKeys": {
        "MessageLogEntry_discordGuildId_DiscordGuild_id_fk": {
          "name": "MessageLogEntry_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "MessageLogEntry_guildedServerId_GuildedServer_id_fk": {
          "name": "MessageLogEntry_guildedServerId_GuildedServer_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "GuildedServer",
          "columnsFrom": ["guildedServerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.OAuthInfo": {
      "name": "OAuthInfo",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "botId": {
          "name": "botId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "accessToken": {
          "name": "accessToken",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "refreshToken": {
          "name": "refreshToken",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "scope": {
          "name": "scope",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "OAuthInfo_discordId_unique": {
          "name": "OAuthInfo_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "OAuthInfo_guildedId_unique": {
          "name": "OAuthInfo_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        },
        "OAuthInfo_botId_unique": {
          "name": "OAuthInfo_botId_unique",
          "nullsNotDistinct": false,
          "columns": ["botId"]
        }
      }
    },
    "public.ShareLink": {
      "name": "ShareLink",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "shareId": {
          "name": "shareId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "origin": {
          "name": "origin",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "ShareLink_userId_User_id_fk": {
          "name": "ShareLink_userId_User_id_fk",
          "tableFrom": "ShareLink",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Token": {
      "name": "Token",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "prefix": {
          "name": "prefix",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "lastUsedAt": {
          "name": "lastUsedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastUsedCountry": {
          "name": "lastUsedCountry",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Token_userId_User_id_fk": {
          "name": "Token_userId_User_id_fk",
          "tableFrom": "Token",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "set null",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Trigger": {
      "name": "Trigger",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "event": {
          "name": "event",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "disabled": {
          "name": "disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Trigger_flowId_Flow_id_fk": {
          "name": "Trigger_flowId_Flow_id_fk",
          "tableFrom": "Trigger",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.User": {
      "name": "User",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "firstSubscribed": {
          "name": "firstSubscribed",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscribedSince": {
          "name": "subscribedSince",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscriptionExpiresAt": {
          "name": "subscriptionExpiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lifetime": {
          "name": "lifetime",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "User_discordId_unique": {
          "name": "User_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "User_guildedId_unique": {
          "name": "User_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        }
      }
    },
    "public.Webhook": {
      "name": "Webhook",
      "schema": "",
      "columns": {
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "Webhook_platform_id_unique": {
          "name": "Webhook_platform_id_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "id"]
        }
      }
    },
    "public.autopublish": {
      "name": "autopublish",
      "schema": "",
      "columns": {
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "added_by_id": {
          "name": "added_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "ignore": {
          "name": "ignore",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.buttons": {
      "name": "buttons",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "style": {
          "name": "style",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_label": {
          "name": "custom_label",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "emoji": {
          "name": "emoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "url": {
          "name": "url",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_ephemeral_message_data": {
          "name": "custom_ephemeral_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_dm_message_data": {
          "name": "custom_dm_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_id": {
          "name": "custom_id",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "role_ids": {
          "name": "role_ids",
          "type": "bigint[]",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_public_message_data": {
          "name": "custom_public_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.message_settings": {
      "name": "message_settings",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "max_roles": {
          "name": "max_roles",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.welcomer_goodbye": {
      "name": "welcomer_goodbye",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.welcomer_hello": {
      "name": "welcomer_hello",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    }
  },
  "enums": {},
  "schemas": {},
  "sequences": {},
  "_meta": {
    "columns": {},
    "schemas": {},
    "tables": {}
  }
}

```

### File: `drizzle/meta/0003_snapshot.json`
```json
{
  "id": "205568cf-dbbf-49ae-bf50-052d21e7f25d",
  "prevId": "e837debb-6384-494c-9e1d-dde85dac5154",
  "version": "7",
  "dialect": "postgresql",
  "tables": {
    "public.Backup": {
      "name": "Backup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "importedFromOrg": {
          "name": "importedFromOrg",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "scheduled": {
          "name": "scheduled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "nextRunAt": {
          "name": "nextRunAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastRunData": {
          "name": "lastRunData",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "cron": {
          "name": "cron",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "timezone": {
          "name": "timezone",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Backup_ownerId_User_id_fk": {
          "name": "Backup_ownerId_User_id_fk",
          "tableFrom": "Backup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.CustomBot": {
      "name": "CustomBot",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "applicationUserId": {
          "name": "applicationUserId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "publicKey": {
          "name": "publicKey",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "clientSecret": {
          "name": "clientSecret",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "CustomBot_ownerId_User_id_fk": {
          "name": "CustomBot_ownerId_User_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "CustomBot_guildId_DiscordGuild_id_fk": {
          "name": "CustomBot_guildId_DiscordGuild_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "CustomBot_applicationId_unique": {
          "name": "CustomBot_applicationId_unique",
          "nullsNotDistinct": false,
          "columns": ["applicationId"]
        }
      }
    },
    "public.DiscordGuild": {
      "name": "DiscordGuild",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'Unknown Server'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerDiscordId": {
          "name": "ownerDiscordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "botJoinedAt": {
          "name": "botJoinedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.DiscordGuild_to_Backup": {
      "name": "DiscordGuild_to_Backup",
      "schema": "",
      "columns": {
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "backupId": {
          "name": "backupId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordGuild_to_Backup_backupId_Backup_id_fk": {
          "name": "DiscordGuild_to_Backup_backupId_Backup_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "Backup",
          "columnsFrom": ["backupId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DiscordGuild_to_Backup_discordGuildId_backupId_pk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_backupId_pk",
          "columns": ["discordGuildId", "backupId"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.DiscordMember": {
      "name": "DiscordMember",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'0'"
        },
        "owner": {
          "name": "owner",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordMember_userId_DiscordUser_id_fk": {
          "name": "DiscordMember_userId_DiscordUser_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordUser",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordMember_guildId_DiscordGuild_id_fk": {
          "name": "DiscordMember_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordMember_userId_guildId_unique": {
          "name": "DiscordMember_userId_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "guildId"]
        }
      }
    },
    "public.DiscordMessageComponent": {
      "name": "DiscordMessageComponent",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "messageId": {
          "name": "messageId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "createdById": {
          "name": "createdById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "draft": {
          "name": "draft",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.DMC_to_Flow": {
      "name": "DMC_to_Flow",
      "schema": "",
      "columns": {
        "dmcId": {
          "name": "dmcId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk": {
          "name": "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "DiscordMessageComponent",
          "columnsFrom": ["dmcId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DMC_to_Flow_flowId_Flow_id_fk": {
          "name": "DMC_to_Flow_flowId_Flow_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DMC_to_Flow_dmcId_flowId_pk": {
          "name": "DMC_to_Flow_dmcId_flowId_pk",
          "columns": ["dmcId", "flowId"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.reaction_roles": {
      "name": "reaction_roles",
      "schema": "",
      "columns": {
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "reaction": {
          "name": "reaction",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "reaction_roles_guild_id_DiscordGuild_id_fk": {
          "name": "reaction_roles_guild_id_DiscordGuild_id_fk",
          "tableFrom": "reaction_roles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guild_id"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "reaction_roles_message_id_reaction_pk": {
          "name": "reaction_roles_message_id_reaction_pk",
          "columns": ["message_id", "reaction"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.DiscordRoles": {
      "name": "DiscordRoles",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "color": {
          "name": "color",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": false,
          "default": "'0'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "unicodeEmoji": {
          "name": "unicodeEmoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "position": {
          "name": "position",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "hoist": {
          "name": "hoist",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "managed": {
          "name": "managed",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "mentionable": {
          "name": "mentionable",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordRoles_guildId_DiscordGuild_id_fk": {
          "name": "DiscordRoles_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordRoles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordRoles_id_unique": {
          "name": "DiscordRoles_id_unique",
          "nullsNotDistinct": false,
          "columns": ["id"]
        },
        "DiscordRoles_id_guildId_unique": {
          "name": "DiscordRoles_id_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["id", "guildId"]
        }
      }
    },
    "public.DiscordUser": {
      "name": "DiscordUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "globalName": {
          "name": "globalName",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Action": {
      "name": "Action",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Action_flowId_Flow_id_fk": {
          "name": "Action_flowId_Flow_id_fk",
          "tableFrom": "Action",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Flow": {
      "name": "Flow",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.GithubPost": {
      "name": "GithubPost",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "githubId": {
          "name": "githubId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryOwner": {
          "name": "repositoryOwner",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryName": {
          "name": "repositoryName",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "postId": {
          "name": "postId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "GithubPost_postId_unique": {
          "name": "GithubPost_postId_unique",
          "nullsNotDistinct": false,
          "columns": ["postId"]
        },
        "GithubPost_platform_channelId_type_githubId_unique": {
          "name": "GithubPost_platform_channelId_type_githubId_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "channelId", "type", "githubId"]
        }
      }
    },
    "public.GuildedServer": {
      "name": "GuildedServer",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.GuildedUser": {
      "name": "GuildedUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.LinkBackup": {
      "name": "LinkBackup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "code": {
          "name": "code",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "LinkBackup_ownerId_User_id_fk": {
          "name": "LinkBackup_ownerId_User_id_fk",
          "tableFrom": "LinkBackup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.MessageLogEntry": {
      "name": "MessageLogEntry",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "messageId": {
          "name": "messageId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "threadId": {
          "name": "threadId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedEveryoneHere": {
          "name": "notifiedEveryoneHere",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "notifiedRoles": {
          "name": "notifiedRoles",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedUsers": {
          "name": "notifiedUsers",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "hasContent": {
          "name": "hasContent",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "embedCount": {
          "name": "embedCount",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        }
      },
      "indexes": {},
      "foreignKeys": {
        "MessageLogEntry_discordGuildId_DiscordGuild_id_fk": {
          "name": "MessageLogEntry_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "MessageLogEntry_guildedServerId_GuildedServer_id_fk": {
          "name": "MessageLogEntry_guildedServerId_GuildedServer_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "GuildedServer",
          "columnsFrom": ["guildedServerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.OAuthInfo": {
      "name": "OAuthInfo",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "botId": {
          "name": "botId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "accessToken": {
          "name": "accessToken",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "refreshToken": {
          "name": "refreshToken",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "scope": {
          "name": "scope",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "OAuthInfo_discordId_unique": {
          "name": "OAuthInfo_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "OAuthInfo_guildedId_unique": {
          "name": "OAuthInfo_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        },
        "OAuthInfo_botId_unique": {
          "name": "OAuthInfo_botId_unique",
          "nullsNotDistinct": false,
          "columns": ["botId"]
        }
      }
    },
    "public.ShareLink": {
      "name": "ShareLink",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "shareId": {
          "name": "shareId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "origin": {
          "name": "origin",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "ShareLink_userId_User_id_fk": {
          "name": "ShareLink_userId_User_id_fk",
          "tableFrom": "ShareLink",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Token": {
      "name": "Token",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "prefix": {
          "name": "prefix",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "lastUsedAt": {
          "name": "lastUsedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastUsedCountry": {
          "name": "lastUsedCountry",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Token_userId_User_id_fk": {
          "name": "Token_userId_User_id_fk",
          "tableFrom": "Token",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "set null",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Trigger": {
      "name": "Trigger",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "event": {
          "name": "event",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "disabled": {
          "name": "disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Trigger_flowId_Flow_id_fk": {
          "name": "Trigger_flowId_Flow_id_fk",
          "tableFrom": "Trigger",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.User": {
      "name": "User",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "firstSubscribed": {
          "name": "firstSubscribed",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscribedSince": {
          "name": "subscribedSince",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscriptionExpiresAt": {
          "name": "subscriptionExpiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lifetime": {
          "name": "lifetime",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "User_discordId_unique": {
          "name": "User_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "User_guildedId_unique": {
          "name": "User_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        }
      }
    },
    "public.Webhook": {
      "name": "Webhook",
      "schema": "",
      "columns": {
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "Webhook_platform_id_unique": {
          "name": "Webhook_platform_id_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "id"]
        }
      }
    },
    "public.autopublish": {
      "name": "autopublish",
      "schema": "",
      "columns": {
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "added_by_id": {
          "name": "added_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "ignore": {
          "name": "ignore",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.buttons": {
      "name": "buttons",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "style": {
          "name": "style",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_label": {
          "name": "custom_label",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "emoji": {
          "name": "emoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "url": {
          "name": "url",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_ephemeral_message_data": {
          "name": "custom_ephemeral_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_dm_message_data": {
          "name": "custom_dm_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_id": {
          "name": "custom_id",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "role_ids": {
          "name": "role_ids",
          "type": "bigint[]",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_public_message_data": {
          "name": "custom_public_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.message_settings": {
      "name": "message_settings",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "max_roles": {
          "name": "max_roles",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.scheduled_posts": {
      "name": "scheduled_posts",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        },
        "user_id": {
          "name": "user_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "future": {
          "name": "future",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "error": {
          "name": "error",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.welcomer_goodbye": {
      "name": "welcomer_goodbye",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.welcomer_hello": {
      "name": "welcomer_hello",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    }
  },
  "enums": {},
  "schemas": {},
  "sequences": {},
  "_meta": {
    "columns": {},
    "schemas": {},
    "tables": {}
  }
}

```

### File: `drizzle/meta/0004_snapshot.json`
```json
{
  "id": "e8b5b99d-076c-4191-aed5-0f955914c150",
  "prevId": "205568cf-dbbf-49ae-bf50-052d21e7f25d",
  "version": "7",
  "dialect": "postgresql",
  "tables": {
    "public.Backup": {
      "name": "Backup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "importedFromOrg": {
          "name": "importedFromOrg",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "scheduled": {
          "name": "scheduled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "nextRunAt": {
          "name": "nextRunAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastRunData": {
          "name": "lastRunData",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "cron": {
          "name": "cron",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "timezone": {
          "name": "timezone",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Backup_ownerId_User_id_fk": {
          "name": "Backup_ownerId_User_id_fk",
          "tableFrom": "Backup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.CustomBot": {
      "name": "CustomBot",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "applicationUserId": {
          "name": "applicationUserId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "publicKey": {
          "name": "publicKey",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "clientSecret": {
          "name": "clientSecret",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "CustomBot_ownerId_User_id_fk": {
          "name": "CustomBot_ownerId_User_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "CustomBot_guildId_DiscordGuild_id_fk": {
          "name": "CustomBot_guildId_DiscordGuild_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "CustomBot_applicationId_unique": {
          "name": "CustomBot_applicationId_unique",
          "nullsNotDistinct": false,
          "columns": ["applicationId"]
        }
      }
    },
    "public.DiscordGuild": {
      "name": "DiscordGuild",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'Unknown Server'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerDiscordId": {
          "name": "ownerDiscordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "botJoinedAt": {
          "name": "botJoinedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.DiscordGuild_to_Backup": {
      "name": "DiscordGuild_to_Backup",
      "schema": "",
      "columns": {
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "backupId": {
          "name": "backupId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordGuild_to_Backup_backupId_Backup_id_fk": {
          "name": "DiscordGuild_to_Backup_backupId_Backup_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "Backup",
          "columnsFrom": ["backupId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DiscordGuild_to_Backup_discordGuildId_backupId_pk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_backupId_pk",
          "columns": ["discordGuildId", "backupId"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.DiscordMember": {
      "name": "DiscordMember",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'0'"
        },
        "owner": {
          "name": "owner",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "favorite": {
          "name": "favorite",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordMember_userId_DiscordUser_id_fk": {
          "name": "DiscordMember_userId_DiscordUser_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordUser",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordMember_guildId_DiscordGuild_id_fk": {
          "name": "DiscordMember_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordMember_userId_guildId_unique": {
          "name": "DiscordMember_userId_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "guildId"]
        }
      }
    },
    "public.DiscordMessageComponent": {
      "name": "DiscordMessageComponent",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "messageId": {
          "name": "messageId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "createdById": {
          "name": "createdById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "draft": {
          "name": "draft",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.DMC_to_Flow": {
      "name": "DMC_to_Flow",
      "schema": "",
      "columns": {
        "dmcId": {
          "name": "dmcId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk": {
          "name": "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "DiscordMessageComponent",
          "columnsFrom": ["dmcId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DMC_to_Flow_flowId_Flow_id_fk": {
          "name": "DMC_to_Flow_flowId_Flow_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DMC_to_Flow_dmcId_flowId_pk": {
          "name": "DMC_to_Flow_dmcId_flowId_pk",
          "columns": ["dmcId", "flowId"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.reaction_roles": {
      "name": "reaction_roles",
      "schema": "",
      "columns": {
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "reaction": {
          "name": "reaction",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "reaction_roles_guild_id_DiscordGuild_id_fk": {
          "name": "reaction_roles_guild_id_DiscordGuild_id_fk",
          "tableFrom": "reaction_roles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guild_id"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "reaction_roles_message_id_reaction_pk": {
          "name": "reaction_roles_message_id_reaction_pk",
          "columns": ["message_id", "reaction"]
        }
      },
      "uniqueConstraints": {}
    },
    "public.DiscordRoles": {
      "name": "DiscordRoles",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "color": {
          "name": "color",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": false,
          "default": "'0'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "unicodeEmoji": {
          "name": "unicodeEmoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "position": {
          "name": "position",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "hoist": {
          "name": "hoist",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "managed": {
          "name": "managed",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "mentionable": {
          "name": "mentionable",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordRoles_guildId_DiscordGuild_id_fk": {
          "name": "DiscordRoles_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordRoles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordRoles_id_unique": {
          "name": "DiscordRoles_id_unique",
          "nullsNotDistinct": false,
          "columns": ["id"]
        },
        "DiscordRoles_id_guildId_unique": {
          "name": "DiscordRoles_id_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["id", "guildId"]
        }
      }
    },
    "public.DiscordUser": {
      "name": "DiscordUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "globalName": {
          "name": "globalName",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Action": {
      "name": "Action",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Action_flowId_Flow_id_fk": {
          "name": "Action_flowId_Flow_id_fk",
          "tableFrom": "Action",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Flow": {
      "name": "Flow",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.GithubPost": {
      "name": "GithubPost",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "githubId": {
          "name": "githubId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryOwner": {
          "name": "repositoryOwner",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryName": {
          "name": "repositoryName",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "postId": {
          "name": "postId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "GithubPost_postId_unique": {
          "name": "GithubPost_postId_unique",
          "nullsNotDistinct": false,
          "columns": ["postId"]
        },
        "GithubPost_platform_channelId_type_githubId_unique": {
          "name": "GithubPost_platform_channelId_type_githubId_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "channelId", "type", "githubId"]
        }
      }
    },
    "public.GuildedServer": {
      "name": "GuildedServer",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.GuildedUser": {
      "name": "GuildedUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.LinkBackup": {
      "name": "LinkBackup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "code": {
          "name": "code",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "LinkBackup_ownerId_User_id_fk": {
          "name": "LinkBackup_ownerId_User_id_fk",
          "tableFrom": "LinkBackup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.MessageLogEntry": {
      "name": "MessageLogEntry",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "messageId": {
          "name": "messageId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "threadId": {
          "name": "threadId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedEveryoneHere": {
          "name": "notifiedEveryoneHere",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "notifiedRoles": {
          "name": "notifiedRoles",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedUsers": {
          "name": "notifiedUsers",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "hasContent": {
          "name": "hasContent",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "embedCount": {
          "name": "embedCount",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        }
      },
      "indexes": {},
      "foreignKeys": {
        "MessageLogEntry_discordGuildId_DiscordGuild_id_fk": {
          "name": "MessageLogEntry_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "MessageLogEntry_guildedServerId_GuildedServer_id_fk": {
          "name": "MessageLogEntry_guildedServerId_GuildedServer_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "GuildedServer",
          "columnsFrom": ["guildedServerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.OAuthInfo": {
      "name": "OAuthInfo",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "botId": {
          "name": "botId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "accessToken": {
          "name": "accessToken",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "refreshToken": {
          "name": "refreshToken",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "scope": {
          "name": "scope",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "OAuthInfo_discordId_unique": {
          "name": "OAuthInfo_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "OAuthInfo_guildedId_unique": {
          "name": "OAuthInfo_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        },
        "OAuthInfo_botId_unique": {
          "name": "OAuthInfo_botId_unique",
          "nullsNotDistinct": false,
          "columns": ["botId"]
        }
      }
    },
    "public.ShareLink": {
      "name": "ShareLink",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "shareId": {
          "name": "shareId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "origin": {
          "name": "origin",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "ShareLink_userId_User_id_fk": {
          "name": "ShareLink_userId_User_id_fk",
          "tableFrom": "ShareLink",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Token": {
      "name": "Token",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "prefix": {
          "name": "prefix",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "lastUsedAt": {
          "name": "lastUsedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastUsedCountry": {
          "name": "lastUsedCountry",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Token_userId_User_id_fk": {
          "name": "Token_userId_User_id_fk",
          "tableFrom": "Token",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "set null",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.Trigger": {
      "name": "Trigger",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "event": {
          "name": "event",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "disabled": {
          "name": "disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Trigger_flowId_Flow_id_fk": {
          "name": "Trigger_flowId_Flow_id_fk",
          "tableFrom": "Trigger",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.UserToWebhook": {
      "name": "UserToWebhook",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "webhookPlatform": {
          "name": "webhookPlatform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "favorite": {
          "name": "favorite",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "UserToWebhook_userId_User_id_fk": {
          "name": "UserToWebhook_userId_User_id_fk",
          "tableFrom": "UserToWebhook",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "UserToWebhook_fk": {
          "name": "UserToWebhook_fk",
          "tableFrom": "UserToWebhook",
          "tableTo": "Webhook",
          "columnsFrom": ["webhookPlatform", "webhookId"],
          "columnsTo": ["platform", "id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "UserToWebhook_userId_webhookPlatform_webhookId_unique": {
          "name": "UserToWebhook_userId_webhookPlatform_webhookId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "webhookPlatform", "webhookId"]
        }
      }
    },
    "public.User": {
      "name": "User",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "firstSubscribed": {
          "name": "firstSubscribed",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscribedSince": {
          "name": "subscribedSince",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscriptionExpiresAt": {
          "name": "subscriptionExpiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lifetime": {
          "name": "lifetime",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "User_discordId_unique": {
          "name": "User_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "User_guildedId_unique": {
          "name": "User_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        }
      }
    },
    "public.Webhook": {
      "name": "Webhook",
      "schema": "",
      "columns": {
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "Webhook_platform_id_unique": {
          "name": "Webhook_platform_id_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "id"]
        }
      }
    },
    "public.autopublish": {
      "name": "autopublish",
      "schema": "",
      "columns": {
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "added_by_id": {
          "name": "added_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "ignore": {
          "name": "ignore",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.buttons": {
      "name": "buttons",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "style": {
          "name": "style",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_label": {
          "name": "custom_label",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "emoji": {
          "name": "emoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "url": {
          "name": "url",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_ephemeral_message_data": {
          "name": "custom_ephemeral_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_dm_message_data": {
          "name": "custom_dm_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_id": {
          "name": "custom_id",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "role_ids": {
          "name": "role_ids",
          "type": "bigint[]",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_public_message_data": {
          "name": "custom_public_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.message_settings": {
      "name": "message_settings",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "max_roles": {
          "name": "max_roles",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.scheduled_posts": {
      "name": "scheduled_posts",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        },
        "user_id": {
          "name": "user_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "future": {
          "name": "future",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "error": {
          "name": "error",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.welcomer_goodbye": {
      "name": "welcomer_goodbye",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    },
    "public.welcomer_hello": {
      "name": "welcomer_hello",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {}
    }
  },
  "enums": {},
  "schemas": {},
  "sequences": {},
  "_meta": {
    "columns": {},
    "schemas": {},
    "tables": {}
  }
}

```

### File: `drizzle/meta/0005_snapshot.json`
```json
{
  "id": "58a2c7f1-c791-411f-a7a5-64c00d241d70",
  "prevId": "e8b5b99d-076c-4191-aed5-0f955914c150",
  "version": "7",
  "dialect": "postgresql",
  "tables": {
    "public.Backup": {
      "name": "Backup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "importedFromOrg": {
          "name": "importedFromOrg",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "scheduled": {
          "name": "scheduled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "nextRunAt": {
          "name": "nextRunAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastRunData": {
          "name": "lastRunData",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "cron": {
          "name": "cron",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "timezone": {
          "name": "timezone",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Backup_ownerId_User_id_fk": {
          "name": "Backup_ownerId_User_id_fk",
          "tableFrom": "Backup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.CustomBot": {
      "name": "CustomBot",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "applicationUserId": {
          "name": "applicationUserId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "publicKey": {
          "name": "publicKey",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "clientSecret": {
          "name": "clientSecret",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "CustomBot_ownerId_User_id_fk": {
          "name": "CustomBot_ownerId_User_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "CustomBot_guildId_DiscordGuild_id_fk": {
          "name": "CustomBot_guildId_DiscordGuild_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "CustomBot_applicationId_unique": {
          "name": "CustomBot_applicationId_unique",
          "nullsNotDistinct": false,
          "columns": ["applicationId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordGuild": {
      "name": "DiscordGuild",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'Unknown Server'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerDiscordId": {
          "name": "ownerDiscordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "botJoinedAt": {
          "name": "botJoinedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordGuild_to_Backup": {
      "name": "DiscordGuild_to_Backup",
      "schema": "",
      "columns": {
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "backupId": {
          "name": "backupId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordGuild_to_Backup_backupId_Backup_id_fk": {
          "name": "DiscordGuild_to_Backup_backupId_Backup_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "Backup",
          "columnsFrom": ["backupId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DiscordGuild_to_Backup_discordGuildId_backupId_pk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_backupId_pk",
          "columns": ["discordGuildId", "backupId"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordMember": {
      "name": "DiscordMember",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'0'"
        },
        "owner": {
          "name": "owner",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "favorite": {
          "name": "favorite",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordMember_userId_DiscordUser_id_fk": {
          "name": "DiscordMember_userId_DiscordUser_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordUser",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordMember_guildId_DiscordGuild_id_fk": {
          "name": "DiscordMember_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordMember_userId_guildId_unique": {
          "name": "DiscordMember_userId_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "guildId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordMessageComponent": {
      "name": "DiscordMessageComponent",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "messageId": {
          "name": "messageId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "createdById": {
          "name": "createdById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "draft": {
          "name": "draft",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DMC_to_Flow": {
      "name": "DMC_to_Flow",
      "schema": "",
      "columns": {
        "dmcId": {
          "name": "dmcId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk": {
          "name": "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "DiscordMessageComponent",
          "columnsFrom": ["dmcId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DMC_to_Flow_flowId_Flow_id_fk": {
          "name": "DMC_to_Flow_flowId_Flow_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DMC_to_Flow_dmcId_flowId_pk": {
          "name": "DMC_to_Flow_dmcId_flowId_pk",
          "columns": ["dmcId", "flowId"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.reaction_roles": {
      "name": "reaction_roles",
      "schema": "",
      "columns": {
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "reaction": {
          "name": "reaction",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "reaction_roles_guild_id_DiscordGuild_id_fk": {
          "name": "reaction_roles_guild_id_DiscordGuild_id_fk",
          "tableFrom": "reaction_roles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guild_id"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "reaction_roles_message_id_reaction_pk": {
          "name": "reaction_roles_message_id_reaction_pk",
          "columns": ["message_id", "reaction"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordRoles": {
      "name": "DiscordRoles",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "color": {
          "name": "color",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": false,
          "default": "'0'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "unicodeEmoji": {
          "name": "unicodeEmoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "position": {
          "name": "position",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "hoist": {
          "name": "hoist",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "managed": {
          "name": "managed",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "mentionable": {
          "name": "mentionable",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordRoles_guildId_DiscordGuild_id_fk": {
          "name": "DiscordRoles_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordRoles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordRoles_id_unique": {
          "name": "DiscordRoles_id_unique",
          "nullsNotDistinct": false,
          "columns": ["id"]
        },
        "DiscordRoles_id_guildId_unique": {
          "name": "DiscordRoles_id_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["id", "guildId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordUser": {
      "name": "DiscordUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "globalName": {
          "name": "globalName",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Action": {
      "name": "Action",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Action_flowId_Flow_id_fk": {
          "name": "Action_flowId_Flow_id_fk",
          "tableFrom": "Action",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Flow": {
      "name": "Flow",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.GithubPost": {
      "name": "GithubPost",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "githubId": {
          "name": "githubId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryOwner": {
          "name": "repositoryOwner",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryName": {
          "name": "repositoryName",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "postId": {
          "name": "postId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "GithubPost_postId_unique": {
          "name": "GithubPost_postId_unique",
          "nullsNotDistinct": false,
          "columns": ["postId"]
        },
        "GithubPost_platform_channelId_type_githubId_unique": {
          "name": "GithubPost_platform_channelId_type_githubId_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "channelId", "type", "githubId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.GuildedServer": {
      "name": "GuildedServer",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.GuildedUser": {
      "name": "GuildedUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.LinkBackup": {
      "name": "LinkBackup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "code": {
          "name": "code",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "LinkBackup_ownerId_User_id_fk": {
          "name": "LinkBackup_ownerId_User_id_fk",
          "tableFrom": "LinkBackup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.MessageLogEntry": {
      "name": "MessageLogEntry",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "messageId": {
          "name": "messageId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "threadId": {
          "name": "threadId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedEveryoneHere": {
          "name": "notifiedEveryoneHere",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "notifiedRoles": {
          "name": "notifiedRoles",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedUsers": {
          "name": "notifiedUsers",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "hasContent": {
          "name": "hasContent",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "embedCount": {
          "name": "embedCount",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        }
      },
      "indexes": {},
      "foreignKeys": {
        "MessageLogEntry_discordGuildId_DiscordGuild_id_fk": {
          "name": "MessageLogEntry_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "MessageLogEntry_guildedServerId_GuildedServer_id_fk": {
          "name": "MessageLogEntry_guildedServerId_GuildedServer_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "GuildedServer",
          "columnsFrom": ["guildedServerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.OAuthInfo": {
      "name": "OAuthInfo",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "botId": {
          "name": "botId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "accessToken": {
          "name": "accessToken",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "refreshToken": {
          "name": "refreshToken",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "scope": {
          "name": "scope",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "OAuthInfo_discordId_unique": {
          "name": "OAuthInfo_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "OAuthInfo_guildedId_unique": {
          "name": "OAuthInfo_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        },
        "OAuthInfo_botId_unique": {
          "name": "OAuthInfo_botId_unique",
          "nullsNotDistinct": false,
          "columns": ["botId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.ShareLink": {
      "name": "ShareLink",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "shareId": {
          "name": "shareId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "origin": {
          "name": "origin",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "ShareLink_userId_User_id_fk": {
          "name": "ShareLink_userId_User_id_fk",
          "tableFrom": "ShareLink",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Token": {
      "name": "Token",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "prefix": {
          "name": "prefix",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "lastUsedAt": {
          "name": "lastUsedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastUsedCountry": {
          "name": "lastUsedCountry",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Token_userId_User_id_fk": {
          "name": "Token_userId_User_id_fk",
          "tableFrom": "Token",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "set null",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Trigger": {
      "name": "Trigger",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'discord'"
        },
        "event": {
          "name": "event",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "flow": {
          "name": "flow",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "disabled": {
          "name": "disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Trigger_flowId_Flow_id_fk": {
          "name": "Trigger_flowId_Flow_id_fk",
          "tableFrom": "Trigger",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.UserToWebhook": {
      "name": "UserToWebhook",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "webhookPlatform": {
          "name": "webhookPlatform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "favorite": {
          "name": "favorite",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "UserToWebhook_userId_User_id_fk": {
          "name": "UserToWebhook_userId_User_id_fk",
          "tableFrom": "UserToWebhook",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "UserToWebhook_fk": {
          "name": "UserToWebhook_fk",
          "tableFrom": "UserToWebhook",
          "tableTo": "Webhook",
          "columnsFrom": ["webhookPlatform", "webhookId"],
          "columnsTo": ["platform", "id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "UserToWebhook_userId_webhookPlatform_webhookId_unique": {
          "name": "UserToWebhook_userId_webhookPlatform_webhookId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "webhookPlatform", "webhookId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.User": {
      "name": "User",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "firstSubscribed": {
          "name": "firstSubscribed",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscribedSince": {
          "name": "subscribedSince",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscriptionExpiresAt": {
          "name": "subscriptionExpiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lifetime": {
          "name": "lifetime",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "User_discordId_unique": {
          "name": "User_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "User_guildedId_unique": {
          "name": "User_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Webhook": {
      "name": "Webhook",
      "schema": "",
      "columns": {
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "Webhook_platform_id_unique": {
          "name": "Webhook_platform_id_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "id"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.autopublish": {
      "name": "autopublish",
      "schema": "",
      "columns": {
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "added_by_id": {
          "name": "added_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "ignore": {
          "name": "ignore",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.buttons": {
      "name": "buttons",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "style": {
          "name": "style",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_label": {
          "name": "custom_label",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "emoji": {
          "name": "emoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "url": {
          "name": "url",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_ephemeral_message_data": {
          "name": "custom_ephemeral_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_dm_message_data": {
          "name": "custom_dm_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_id": {
          "name": "custom_id",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "role_ids": {
          "name": "role_ids",
          "type": "bigint[]",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_public_message_data": {
          "name": "custom_public_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.message_settings": {
      "name": "message_settings",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "max_roles": {
          "name": "max_roles",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.scheduled_posts": {
      "name": "scheduled_posts",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        },
        "user_id": {
          "name": "user_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "future": {
          "name": "future",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "error": {
          "name": "error",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.welcomer_goodbye": {
      "name": "welcomer_goodbye",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.welcomer_hello": {
      "name": "welcomer_hello",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    }
  },
  "enums": {},
  "schemas": {},
  "sequences": {},
  "roles": {},
  "policies": {},
  "views": {},
  "_meta": {
    "columns": {},
    "schemas": {},
    "tables": {}
  }
}

```

### File: `drizzle/meta/0006_snapshot.json`
```json
{
  "id": "bfede30a-8476-49da-9fc8-4d67bdd11b91",
  "prevId": "58a2c7f1-c791-411f-a7a5-64c00d241d70",
  "version": "7",
  "dialect": "postgresql",
  "tables": {
    "public.Backup": {
      "name": "Backup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "importedFromOrg": {
          "name": "importedFromOrg",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "scheduled": {
          "name": "scheduled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "nextRunAt": {
          "name": "nextRunAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastRunData": {
          "name": "lastRunData",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "cron": {
          "name": "cron",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "timezone": {
          "name": "timezone",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Backup_ownerId_User_id_fk": {
          "name": "Backup_ownerId_User_id_fk",
          "tableFrom": "Backup",
          "columnsFrom": ["ownerId"],
          "tableTo": "User",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.CustomBot": {
      "name": "CustomBot",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "applicationUserId": {
          "name": "applicationUserId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "publicKey": {
          "name": "publicKey",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "clientSecret": {
          "name": "clientSecret",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "CustomBot_ownerId_User_id_fk": {
          "name": "CustomBot_ownerId_User_id_fk",
          "tableFrom": "CustomBot",
          "columnsFrom": ["ownerId"],
          "tableTo": "User",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        },
        "CustomBot_guildId_DiscordGuild_id_fk": {
          "name": "CustomBot_guildId_DiscordGuild_id_fk",
          "tableFrom": "CustomBot",
          "columnsFrom": ["guildId"],
          "tableTo": "DiscordGuild",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "CustomBot_applicationId_unique": {
          "name": "CustomBot_applicationId_unique",
          "columns": ["applicationId"],
          "nullsNotDistinct": false
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordGuild": {
      "name": "DiscordGuild",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'Unknown Server'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerDiscordId": {
          "name": "ownerDiscordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "botJoinedAt": {
          "name": "botJoinedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordGuild_to_Backup": {
      "name": "DiscordGuild_to_Backup",
      "schema": "",
      "columns": {
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "backupId": {
          "name": "backupId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "columnsFrom": ["discordGuildId"],
          "tableTo": "DiscordGuild",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        },
        "DiscordGuild_to_Backup_backupId_Backup_id_fk": {
          "name": "DiscordGuild_to_Backup_backupId_Backup_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "columnsFrom": ["backupId"],
          "tableTo": "Backup",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        }
      },
      "compositePrimaryKeys": {
        "DiscordGuild_to_Backup_discordGuildId_backupId_pk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_backupId_pk",
          "columns": ["discordGuildId", "backupId"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordMember": {
      "name": "DiscordMember",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'0'"
        },
        "owner": {
          "name": "owner",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "favorite": {
          "name": "favorite",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordMember_userId_DiscordUser_id_fk": {
          "name": "DiscordMember_userId_DiscordUser_id_fk",
          "tableFrom": "DiscordMember",
          "columnsFrom": ["userId"],
          "tableTo": "DiscordUser",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        },
        "DiscordMember_guildId_DiscordGuild_id_fk": {
          "name": "DiscordMember_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordMember",
          "columnsFrom": ["guildId"],
          "tableTo": "DiscordGuild",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordMember_userId_guildId_unique": {
          "name": "DiscordMember_userId_guildId_unique",
          "columns": ["userId", "guildId"],
          "nullsNotDistinct": false
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordMessageComponent": {
      "name": "DiscordMessageComponent",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "messageId": {
          "name": "messageId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "createdById": {
          "name": "createdById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "draft": {
          "name": "draft",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DMC_to_Flow": {
      "name": "DMC_to_Flow",
      "schema": "",
      "columns": {
        "dmcId": {
          "name": "dmcId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk": {
          "name": "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk",
          "tableFrom": "DMC_to_Flow",
          "columnsFrom": ["dmcId"],
          "tableTo": "DiscordMessageComponent",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        },
        "DMC_to_Flow_flowId_Flow_id_fk": {
          "name": "DMC_to_Flow_flowId_Flow_id_fk",
          "tableFrom": "DMC_to_Flow",
          "columnsFrom": ["flowId"],
          "tableTo": "Flow",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        }
      },
      "compositePrimaryKeys": {
        "DMC_to_Flow_dmcId_flowId_pk": {
          "name": "DMC_to_Flow_dmcId_flowId_pk",
          "columns": ["dmcId", "flowId"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.reaction_roles": {
      "name": "reaction_roles",
      "schema": "",
      "columns": {
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "reaction": {
          "name": "reaction",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "reaction_roles_guild_id_DiscordGuild_id_fk": {
          "name": "reaction_roles_guild_id_DiscordGuild_id_fk",
          "tableFrom": "reaction_roles",
          "columnsFrom": ["guild_id"],
          "tableTo": "DiscordGuild",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        }
      },
      "compositePrimaryKeys": {
        "reaction_roles_message_id_reaction_pk": {
          "name": "reaction_roles_message_id_reaction_pk",
          "columns": ["message_id", "reaction"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordRoles": {
      "name": "DiscordRoles",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "color": {
          "name": "color",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": false,
          "default": "'0'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "unicodeEmoji": {
          "name": "unicodeEmoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "position": {
          "name": "position",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "hoist": {
          "name": "hoist",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "managed": {
          "name": "managed",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "mentionable": {
          "name": "mentionable",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordRoles_guildId_DiscordGuild_id_fk": {
          "name": "DiscordRoles_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordRoles",
          "columnsFrom": ["guildId"],
          "tableTo": "DiscordGuild",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordRoles_id_unique": {
          "name": "DiscordRoles_id_unique",
          "columns": ["id"],
          "nullsNotDistinct": false
        },
        "DiscordRoles_id_guildId_unique": {
          "name": "DiscordRoles_id_guildId_unique",
          "columns": ["id", "guildId"],
          "nullsNotDistinct": false
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordUser": {
      "name": "DiscordUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "globalName": {
          "name": "globalName",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Action": {
      "name": "Action",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Action_flowId_Flow_id_fk": {
          "name": "Action_flowId_Flow_id_fk",
          "tableFrom": "Action",
          "columnsFrom": ["flowId"],
          "tableTo": "Flow",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Flow": {
      "name": "Flow",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.GithubPost": {
      "name": "GithubPost",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "githubId": {
          "name": "githubId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryOwner": {
          "name": "repositoryOwner",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryName": {
          "name": "repositoryName",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "postId": {
          "name": "postId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "GithubPost_postId_unique": {
          "name": "GithubPost_postId_unique",
          "columns": ["postId"],
          "nullsNotDistinct": false
        },
        "GithubPost_platform_channelId_type_githubId_unique": {
          "name": "GithubPost_platform_channelId_type_githubId_unique",
          "columns": ["platform", "channelId", "type", "githubId"],
          "nullsNotDistinct": false
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.GuildedServer": {
      "name": "GuildedServer",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.GuildedUser": {
      "name": "GuildedUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.LinkBackup": {
      "name": "LinkBackup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "code": {
          "name": "code",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "LinkBackup_ownerId_User_id_fk": {
          "name": "LinkBackup_ownerId_User_id_fk",
          "tableFrom": "LinkBackup",
          "columnsFrom": ["ownerId"],
          "tableTo": "User",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.MessageLogEntry": {
      "name": "MessageLogEntry",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "messageId": {
          "name": "messageId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "threadId": {
          "name": "threadId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedEveryoneHere": {
          "name": "notifiedEveryoneHere",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "notifiedRoles": {
          "name": "notifiedRoles",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedUsers": {
          "name": "notifiedUsers",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "hasContent": {
          "name": "hasContent",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "embedCount": {
          "name": "embedCount",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        }
      },
      "indexes": {},
      "foreignKeys": {
        "MessageLogEntry_discordGuildId_DiscordGuild_id_fk": {
          "name": "MessageLogEntry_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "MessageLogEntry",
          "columnsFrom": ["discordGuildId"],
          "tableTo": "DiscordGuild",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        },
        "MessageLogEntry_guildedServerId_GuildedServer_id_fk": {
          "name": "MessageLogEntry_guildedServerId_GuildedServer_id_fk",
          "tableFrom": "MessageLogEntry",
          "columnsFrom": ["guildedServerId"],
          "tableTo": "GuildedServer",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.OAuthInfo": {
      "name": "OAuthInfo",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "botId": {
          "name": "botId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "accessToken": {
          "name": "accessToken",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "refreshToken": {
          "name": "refreshToken",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "scope": {
          "name": "scope",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "OAuthInfo_discordId_unique": {
          "name": "OAuthInfo_discordId_unique",
          "columns": ["discordId"],
          "nullsNotDistinct": false
        },
        "OAuthInfo_guildedId_unique": {
          "name": "OAuthInfo_guildedId_unique",
          "columns": ["guildedId"],
          "nullsNotDistinct": false
        },
        "OAuthInfo_botId_unique": {
          "name": "OAuthInfo_botId_unique",
          "columns": ["botId"],
          "nullsNotDistinct": false
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.ShareLink": {
      "name": "ShareLink",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "shareId": {
          "name": "shareId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "origin": {
          "name": "origin",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "ShareLink_userId_User_id_fk": {
          "name": "ShareLink_userId_User_id_fk",
          "tableFrom": "ShareLink",
          "columnsFrom": ["userId"],
          "tableTo": "User",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Token": {
      "name": "Token",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "prefix": {
          "name": "prefix",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "lastUsedAt": {
          "name": "lastUsedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastUsedCountry": {
          "name": "lastUsedCountry",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Token_userId_User_id_fk": {
          "name": "Token_userId_User_id_fk",
          "tableFrom": "Token",
          "columnsFrom": ["userId"],
          "tableTo": "User",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "set null"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Trigger": {
      "name": "Trigger",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'discord'"
        },
        "event": {
          "name": "event",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "flow": {
          "name": "flow",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "disabled": {
          "name": "disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Trigger_flowId_Flow_id_fk": {
          "name": "Trigger_flowId_Flow_id_fk",
          "tableFrom": "Trigger",
          "columnsFrom": ["flowId"],
          "tableTo": "Flow",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.UserToWebhook": {
      "name": "UserToWebhook",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "webhookPlatform": {
          "name": "webhookPlatform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "favorite": {
          "name": "favorite",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "UserToWebhook_userId_User_id_fk": {
          "name": "UserToWebhook_userId_User_id_fk",
          "tableFrom": "UserToWebhook",
          "columnsFrom": ["userId"],
          "tableTo": "User",
          "columnsTo": ["id"],
          "onUpdate": "no action",
          "onDelete": "cascade"
        },
        "UserToWebhook_fk": {
          "name": "UserToWebhook_fk",
          "tableFrom": "UserToWebhook",
          "columnsFrom": ["webhookPlatform", "webhookId"],
          "tableTo": "Webhook",
          "columnsTo": ["platform", "id"],
          "onUpdate": "no action",
          "onDelete": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "UserToWebhook_userId_webhookPlatform_webhookId_unique": {
          "name": "UserToWebhook_userId_webhookPlatform_webhookId_unique",
          "columns": ["userId", "webhookPlatform", "webhookId"],
          "nullsNotDistinct": false
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.User": {
      "name": "User",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "firstSubscribed": {
          "name": "firstSubscribed",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscribedSince": {
          "name": "subscribedSince",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscriptionExpiresAt": {
          "name": "subscriptionExpiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lifetime": {
          "name": "lifetime",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "User_discordId_unique": {
          "name": "User_discordId_unique",
          "columns": ["discordId"],
          "nullsNotDistinct": false
        },
        "User_guildedId_unique": {
          "name": "User_guildedId_unique",
          "columns": ["guildedId"],
          "nullsNotDistinct": false
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Webhook": {
      "name": "Webhook",
      "schema": "",
      "columns": {
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "Webhook_platform_id_unique": {
          "name": "Webhook_platform_id_unique",
          "columns": ["platform", "id"],
          "nullsNotDistinct": false
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.autopublish": {
      "name": "autopublish",
      "schema": "",
      "columns": {
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "added_by_id": {
          "name": "added_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "ignore": {
          "name": "ignore",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.buttons": {
      "name": "buttons",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "style": {
          "name": "style",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_label": {
          "name": "custom_label",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "emoji": {
          "name": "emoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "url": {
          "name": "url",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_ephemeral_message_data": {
          "name": "custom_ephemeral_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_dm_message_data": {
          "name": "custom_dm_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_id": {
          "name": "custom_id",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "role_ids": {
          "name": "role_ids",
          "type": "bigint[]",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_public_message_data": {
          "name": "custom_public_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.message_settings": {
      "name": "message_settings",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "max_roles": {
          "name": "max_roles",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.scheduled_posts": {
      "name": "scheduled_posts",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        },
        "user_id": {
          "name": "user_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "future": {
          "name": "future",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "error": {
          "name": "error",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.welcomer_goodbye": {
      "name": "welcomer_goodbye",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.welcomer_hello": {
      "name": "welcomer_hello",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    }
  },
  "enums": {},
  "schemas": {},
  "views": {},
  "sequences": {},
  "roles": {},
  "policies": {},
  "_meta": {
    "columns": {},
    "schemas": {},
    "tables": {}
  }
}

```

### File: `drizzle/meta/0007_snapshot.json`
```json
{
  "id": "4e9b7ad2-d955-4e3a-b354-39ab32686556",
  "prevId": "bfede30a-8476-49da-9fc8-4d67bdd11b91",
  "version": "7",
  "dialect": "postgresql",
  "tables": {
    "public.Backup": {
      "name": "Backup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false,
          "default": "now()"
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "importedFromOrg": {
          "name": "importedFromOrg",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "scheduled": {
          "name": "scheduled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "nextRunAt": {
          "name": "nextRunAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastRunData": {
          "name": "lastRunData",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "cron": {
          "name": "cron",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "timezone": {
          "name": "timezone",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Backup_ownerId_User_id_fk": {
          "name": "Backup_ownerId_User_id_fk",
          "tableFrom": "Backup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.CustomBot": {
      "name": "CustomBot",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "applicationUserId": {
          "name": "applicationUserId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "publicKey": {
          "name": "publicKey",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "clientSecret": {
          "name": "clientSecret",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "CustomBot_ownerId_User_id_fk": {
          "name": "CustomBot_ownerId_User_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "CustomBot_guildId_DiscordGuild_id_fk": {
          "name": "CustomBot_guildId_DiscordGuild_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "CustomBot_applicationId_unique": {
          "name": "CustomBot_applicationId_unique",
          "nullsNotDistinct": false,
          "columns": ["applicationId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordGuild": {
      "name": "DiscordGuild",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'Unknown Server'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerDiscordId": {
          "name": "ownerDiscordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "botJoinedAt": {
          "name": "botJoinedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordGuild_to_Backup": {
      "name": "DiscordGuild_to_Backup",
      "schema": "",
      "columns": {
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "backupId": {
          "name": "backupId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordGuild_to_Backup_backupId_Backup_id_fk": {
          "name": "DiscordGuild_to_Backup_backupId_Backup_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "Backup",
          "columnsFrom": ["backupId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DiscordGuild_to_Backup_discordGuildId_backupId_pk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_backupId_pk",
          "columns": ["discordGuildId", "backupId"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordMember": {
      "name": "DiscordMember",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'0'"
        },
        "owner": {
          "name": "owner",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "favorite": {
          "name": "favorite",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordMember_userId_DiscordUser_id_fk": {
          "name": "DiscordMember_userId_DiscordUser_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordUser",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordMember_guildId_DiscordGuild_id_fk": {
          "name": "DiscordMember_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordMember_userId_guildId_unique": {
          "name": "DiscordMember_userId_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "guildId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordMessageComponent": {
      "name": "DiscordMessageComponent",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "messageId": {
          "name": "messageId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "createdById": {
          "name": "createdById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false,
          "default": "now()"
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "draft": {
          "name": "draft",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DMC_to_Flow": {
      "name": "DMC_to_Flow",
      "schema": "",
      "columns": {
        "dmcId": {
          "name": "dmcId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk": {
          "name": "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "DiscordMessageComponent",
          "columnsFrom": ["dmcId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DMC_to_Flow_flowId_Flow_id_fk": {
          "name": "DMC_to_Flow_flowId_Flow_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DMC_to_Flow_dmcId_flowId_pk": {
          "name": "DMC_to_Flow_dmcId_flowId_pk",
          "columns": ["dmcId", "flowId"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.reaction_roles": {
      "name": "reaction_roles",
      "schema": "",
      "columns": {
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "reaction": {
          "name": "reaction",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "reaction_roles_guild_id_DiscordGuild_id_fk": {
          "name": "reaction_roles_guild_id_DiscordGuild_id_fk",
          "tableFrom": "reaction_roles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guild_id"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "reaction_roles_message_id_reaction_pk": {
          "name": "reaction_roles_message_id_reaction_pk",
          "columns": ["message_id", "reaction"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordRoles": {
      "name": "DiscordRoles",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "color": {
          "name": "color",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": false,
          "default": "'0'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "unicodeEmoji": {
          "name": "unicodeEmoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "position": {
          "name": "position",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "hoist": {
          "name": "hoist",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "managed": {
          "name": "managed",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "mentionable": {
          "name": "mentionable",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordRoles_guildId_DiscordGuild_id_fk": {
          "name": "DiscordRoles_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordRoles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordRoles_id_unique": {
          "name": "DiscordRoles_id_unique",
          "nullsNotDistinct": false,
          "columns": ["id"]
        },
        "DiscordRoles_id_guildId_unique": {
          "name": "DiscordRoles_id_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["id", "guildId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordUser": {
      "name": "DiscordUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "globalName": {
          "name": "globalName",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Action": {
      "name": "Action",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Action_flowId_Flow_id_fk": {
          "name": "Action_flowId_Flow_id_fk",
          "tableFrom": "Action",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Flow": {
      "name": "Flow",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.GithubPost": {
      "name": "GithubPost",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "githubId": {
          "name": "githubId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryOwner": {
          "name": "repositoryOwner",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryName": {
          "name": "repositoryName",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "postId": {
          "name": "postId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "GithubPost_postId_unique": {
          "name": "GithubPost_postId_unique",
          "nullsNotDistinct": false,
          "columns": ["postId"]
        },
        "GithubPost_platform_channelId_type_githubId_unique": {
          "name": "GithubPost_platform_channelId_type_githubId_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "channelId", "type", "githubId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.GuildedServer": {
      "name": "GuildedServer",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.GuildedUser": {
      "name": "GuildedUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.LinkBackup": {
      "name": "LinkBackup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "code": {
          "name": "code",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false,
          "default": "now()"
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "LinkBackup_ownerId_User_id_fk": {
          "name": "LinkBackup_ownerId_User_id_fk",
          "tableFrom": "LinkBackup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.MessageLogEntry": {
      "name": "MessageLogEntry",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "messageId": {
          "name": "messageId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "threadId": {
          "name": "threadId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedEveryoneHere": {
          "name": "notifiedEveryoneHere",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "notifiedRoles": {
          "name": "notifiedRoles",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedUsers": {
          "name": "notifiedUsers",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "hasContent": {
          "name": "hasContent",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "embedCount": {
          "name": "embedCount",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        }
      },
      "indexes": {},
      "foreignKeys": {
        "MessageLogEntry_discordGuildId_DiscordGuild_id_fk": {
          "name": "MessageLogEntry_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "MessageLogEntry_guildedServerId_GuildedServer_id_fk": {
          "name": "MessageLogEntry_guildedServerId_GuildedServer_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "GuildedServer",
          "columnsFrom": ["guildedServerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.OAuthInfo": {
      "name": "OAuthInfo",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "botId": {
          "name": "botId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "accessToken": {
          "name": "accessToken",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "refreshToken": {
          "name": "refreshToken",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "scope": {
          "name": "scope",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "OAuthInfo_discordId_unique": {
          "name": "OAuthInfo_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "OAuthInfo_guildedId_unique": {
          "name": "OAuthInfo_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        },
        "OAuthInfo_botId_unique": {
          "name": "OAuthInfo_botId_unique",
          "nullsNotDistinct": false,
          "columns": ["botId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.ShareLink": {
      "name": "ShareLink",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "shareId": {
          "name": "shareId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "origin": {
          "name": "origin",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "ShareLink_userId_User_id_fk": {
          "name": "ShareLink_userId_User_id_fk",
          "tableFrom": "ShareLink",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Token": {
      "name": "Token",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "prefix": {
          "name": "prefix",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "lastUsedAt": {
          "name": "lastUsedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastUsedCountry": {
          "name": "lastUsedCountry",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Token_userId_User_id_fk": {
          "name": "Token_userId_User_id_fk",
          "tableFrom": "Token",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "set null",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Trigger": {
      "name": "Trigger",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'discord'"
        },
        "event": {
          "name": "event",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "flow": {
          "name": "flow",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false,
          "default": "now()"
        },
        "disabled": {
          "name": "disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Trigger_flowId_Flow_id_fk": {
          "name": "Trigger_flowId_Flow_id_fk",
          "tableFrom": "Trigger",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.UserToWebhook": {
      "name": "UserToWebhook",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "webhookPlatform": {
          "name": "webhookPlatform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "favorite": {
          "name": "favorite",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "UserToWebhook_userId_User_id_fk": {
          "name": "UserToWebhook_userId_User_id_fk",
          "tableFrom": "UserToWebhook",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "UserToWebhook_fk": {
          "name": "UserToWebhook_fk",
          "tableFrom": "UserToWebhook",
          "tableTo": "Webhook",
          "columnsFrom": ["webhookPlatform", "webhookId"],
          "columnsTo": ["platform", "id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "UserToWebhook_userId_webhookPlatform_webhookId_unique": {
          "name": "UserToWebhook_userId_webhookPlatform_webhookId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "webhookPlatform", "webhookId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.User": {
      "name": "User",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "firstSubscribed": {
          "name": "firstSubscribed",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscribedSince": {
          "name": "subscribedSince",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscriptionExpiresAt": {
          "name": "subscriptionExpiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lifetime": {
          "name": "lifetime",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "User_discordId_unique": {
          "name": "User_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "User_guildedId_unique": {
          "name": "User_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Webhook": {
      "name": "Webhook",
      "schema": "",
      "columns": {
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "Webhook_platform_id_unique": {
          "name": "Webhook_platform_id_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "id"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.autopublish": {
      "name": "autopublish",
      "schema": "",
      "columns": {
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "added_by_id": {
          "name": "added_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "ignore": {
          "name": "ignore",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.buttons": {
      "name": "buttons",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "style": {
          "name": "style",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_label": {
          "name": "custom_label",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "emoji": {
          "name": "emoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "url": {
          "name": "url",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_ephemeral_message_data": {
          "name": "custom_ephemeral_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_dm_message_data": {
          "name": "custom_dm_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_id": {
          "name": "custom_id",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "role_ids": {
          "name": "role_ids",
          "type": "bigint[]",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_public_message_data": {
          "name": "custom_public_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.message_settings": {
      "name": "message_settings",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "max_roles": {
          "name": "max_roles",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.scheduled_posts": {
      "name": "scheduled_posts",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        },
        "user_id": {
          "name": "user_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "future": {
          "name": "future",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "error": {
          "name": "error",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.welcomer_goodbye": {
      "name": "welcomer_goodbye",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.welcomer_hello": {
      "name": "welcomer_hello",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    }
  },
  "enums": {},
  "schemas": {},
  "sequences": {},
  "roles": {},
  "policies": {},
  "views": {},
  "_meta": {
    "columns": {},
    "schemas": {},
    "tables": {}
  }
}

```

### File: `drizzle/meta/0008_snapshot.json`
```json
{
  "id": "04d8405b-f906-4dfb-9187-0d5210f7c4cc",
  "prevId": "4e9b7ad2-d955-4e3a-b354-39ab32686556",
  "version": "7",
  "dialect": "postgresql",
  "tables": {
    "public.Backup": {
      "name": "Backup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "importedFromOrg": {
          "name": "importedFromOrg",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "scheduled": {
          "name": "scheduled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "nextRunAt": {
          "name": "nextRunAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastRunData": {
          "name": "lastRunData",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "cron": {
          "name": "cron",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "timezone": {
          "name": "timezone",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Backup_ownerId_User_id_fk": {
          "name": "Backup_ownerId_User_id_fk",
          "tableFrom": "Backup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.CustomBot": {
      "name": "CustomBot",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "applicationUserId": {
          "name": "applicationUserId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "publicKey": {
          "name": "publicKey",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "clientSecret": {
          "name": "clientSecret",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "CustomBot_ownerId_User_id_fk": {
          "name": "CustomBot_ownerId_User_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "CustomBot_guildId_DiscordGuild_id_fk": {
          "name": "CustomBot_guildId_DiscordGuild_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "CustomBot_applicationId_unique": {
          "name": "CustomBot_applicationId_unique",
          "nullsNotDistinct": false,
          "columns": ["applicationId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordGuild": {
      "name": "DiscordGuild",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'Unknown Server'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerDiscordId": {
          "name": "ownerDiscordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "botJoinedAt": {
          "name": "botJoinedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordGuild_to_Backup": {
      "name": "DiscordGuild_to_Backup",
      "schema": "",
      "columns": {
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "backupId": {
          "name": "backupId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordGuild_to_Backup_backupId_Backup_id_fk": {
          "name": "DiscordGuild_to_Backup_backupId_Backup_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "Backup",
          "columnsFrom": ["backupId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DiscordGuild_to_Backup_discordGuildId_backupId_pk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_backupId_pk",
          "columns": ["discordGuildId", "backupId"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordMember": {
      "name": "DiscordMember",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'0'"
        },
        "owner": {
          "name": "owner",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "favorite": {
          "name": "favorite",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordMember_userId_DiscordUser_id_fk": {
          "name": "DiscordMember_userId_DiscordUser_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordUser",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordMember_guildId_DiscordGuild_id_fk": {
          "name": "DiscordMember_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordMember_userId_guildId_unique": {
          "name": "DiscordMember_userId_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "guildId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordMessageComponent": {
      "name": "DiscordMessageComponent",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "messageId": {
          "name": "messageId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "createdById": {
          "name": "createdById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "draft": {
          "name": "draft",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DMC_to_Flow": {
      "name": "DMC_to_Flow",
      "schema": "",
      "columns": {
        "dmcId": {
          "name": "dmcId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk": {
          "name": "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "DiscordMessageComponent",
          "columnsFrom": ["dmcId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DMC_to_Flow_flowId_Flow_id_fk": {
          "name": "DMC_to_Flow_flowId_Flow_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DMC_to_Flow_dmcId_flowId_pk": {
          "name": "DMC_to_Flow_dmcId_flowId_pk",
          "columns": ["dmcId", "flowId"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.reaction_roles": {
      "name": "reaction_roles",
      "schema": "",
      "columns": {
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "reaction": {
          "name": "reaction",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "reaction_roles_guild_id_DiscordGuild_id_fk": {
          "name": "reaction_roles_guild_id_DiscordGuild_id_fk",
          "tableFrom": "reaction_roles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guild_id"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "reaction_roles_message_id_reaction_pk": {
          "name": "reaction_roles_message_id_reaction_pk",
          "columns": ["message_id", "reaction"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordRoles": {
      "name": "DiscordRoles",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "color": {
          "name": "color",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": false,
          "default": "'0'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "unicodeEmoji": {
          "name": "unicodeEmoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "position": {
          "name": "position",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "hoist": {
          "name": "hoist",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "managed": {
          "name": "managed",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "mentionable": {
          "name": "mentionable",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordRoles_guildId_DiscordGuild_id_fk": {
          "name": "DiscordRoles_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordRoles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordRoles_id_unique": {
          "name": "DiscordRoles_id_unique",
          "nullsNotDistinct": false,
          "columns": ["id"]
        },
        "DiscordRoles_id_guildId_unique": {
          "name": "DiscordRoles_id_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["id", "guildId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordUser": {
      "name": "DiscordUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "globalName": {
          "name": "globalName",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Action": {
      "name": "Action",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Action_flowId_Flow_id_fk": {
          "name": "Action_flowId_Flow_id_fk",
          "tableFrom": "Action",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Flow": {
      "name": "Flow",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.GithubPost": {
      "name": "GithubPost",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "githubId": {
          "name": "githubId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryOwner": {
          "name": "repositoryOwner",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryName": {
          "name": "repositoryName",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "postId": {
          "name": "postId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "GithubPost_postId_unique": {
          "name": "GithubPost_postId_unique",
          "nullsNotDistinct": false,
          "columns": ["postId"]
        },
        "GithubPost_platform_channelId_type_githubId_unique": {
          "name": "GithubPost_platform_channelId_type_githubId_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "channelId", "type", "githubId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.GuildedServer": {
      "name": "GuildedServer",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.GuildedUser": {
      "name": "GuildedUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatarUrl": {
          "name": "avatarUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.LinkBackup": {
      "name": "LinkBackup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "code": {
          "name": "code",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "LinkBackup_ownerId_User_id_fk": {
          "name": "LinkBackup_ownerId_User_id_fk",
          "tableFrom": "LinkBackup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.MessageLogEntry": {
      "name": "MessageLogEntry",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "messageId": {
          "name": "messageId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "threadId": {
          "name": "threadId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedEveryoneHere": {
          "name": "notifiedEveryoneHere",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "notifiedRoles": {
          "name": "notifiedRoles",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedUsers": {
          "name": "notifiedUsers",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "hasContent": {
          "name": "hasContent",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "embedCount": {
          "name": "embedCount",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        }
      },
      "indexes": {},
      "foreignKeys": {
        "MessageLogEntry_discordGuildId_DiscordGuild_id_fk": {
          "name": "MessageLogEntry_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "MessageLogEntry_guildedServerId_GuildedServer_id_fk": {
          "name": "MessageLogEntry_guildedServerId_GuildedServer_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "GuildedServer",
          "columnsFrom": ["guildedServerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.OAuthInfo": {
      "name": "OAuthInfo",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "botId": {
          "name": "botId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "accessToken": {
          "name": "accessToken",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "refreshToken": {
          "name": "refreshToken",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "scope": {
          "name": "scope",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "OAuthInfo_discordId_unique": {
          "name": "OAuthInfo_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "OAuthInfo_guildedId_unique": {
          "name": "OAuthInfo_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        },
        "OAuthInfo_botId_unique": {
          "name": "OAuthInfo_botId_unique",
          "nullsNotDistinct": false,
          "columns": ["botId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.ShareLink": {
      "name": "ShareLink",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "shareId": {
          "name": "shareId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "origin": {
          "name": "origin",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "ShareLink_userId_User_id_fk": {
          "name": "ShareLink_userId_User_id_fk",
          "tableFrom": "ShareLink",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Token": {
      "name": "Token",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "prefix": {
          "name": "prefix",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "lastUsedAt": {
          "name": "lastUsedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastUsedCountry": {
          "name": "lastUsedCountry",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Token_userId_User_id_fk": {
          "name": "Token_userId_User_id_fk",
          "tableFrom": "Token",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "set null",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Trigger": {
      "name": "Trigger",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'discord'"
        },
        "event": {
          "name": "event",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "flow": {
          "name": "flow",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "disabled": {
          "name": "disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Trigger_flowId_Flow_id_fk": {
          "name": "Trigger_flowId_Flow_id_fk",
          "tableFrom": "Trigger",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.UserToWebhook": {
      "name": "UserToWebhook",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "webhookPlatform": {
          "name": "webhookPlatform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "favorite": {
          "name": "favorite",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "UserToWebhook_userId_User_id_fk": {
          "name": "UserToWebhook_userId_User_id_fk",
          "tableFrom": "UserToWebhook",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "UserToWebhook_fk": {
          "name": "UserToWebhook_fk",
          "tableFrom": "UserToWebhook",
          "tableTo": "Webhook",
          "columnsFrom": ["webhookPlatform", "webhookId"],
          "columnsTo": ["platform", "id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "UserToWebhook_userId_webhookPlatform_webhookId_unique": {
          "name": "UserToWebhook_userId_webhookPlatform_webhookId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "webhookPlatform", "webhookId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.User": {
      "name": "User",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "firstSubscribed": {
          "name": "firstSubscribed",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscribedSince": {
          "name": "subscribedSince",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscriptionExpiresAt": {
          "name": "subscriptionExpiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lifetime": {
          "name": "lifetime",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedId": {
          "name": "guildedId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "User_discordId_unique": {
          "name": "User_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "User_guildedId_unique": {
          "name": "User_guildedId_unique",
          "nullsNotDistinct": false,
          "columns": ["guildedId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Webhook": {
      "name": "Webhook",
      "schema": "",
      "columns": {
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guildedServerId": {
          "name": "guildedServerId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "Webhook_platform_id_unique": {
          "name": "Webhook_platform_id_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "id"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.autopublish": {
      "name": "autopublish",
      "schema": "",
      "columns": {
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "added_by_id": {
          "name": "added_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "ignore": {
          "name": "ignore",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.buttons": {
      "name": "buttons",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "style": {
          "name": "style",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_label": {
          "name": "custom_label",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "emoji": {
          "name": "emoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "url": {
          "name": "url",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_ephemeral_message_data": {
          "name": "custom_ephemeral_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_dm_message_data": {
          "name": "custom_dm_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_id": {
          "name": "custom_id",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "role_ids": {
          "name": "role_ids",
          "type": "bigint[]",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_public_message_data": {
          "name": "custom_public_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.message_settings": {
      "name": "message_settings",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "max_roles": {
          "name": "max_roles",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.scheduled_posts": {
      "name": "scheduled_posts",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        },
        "user_id": {
          "name": "user_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "future": {
          "name": "future",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "error": {
          "name": "error",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.welcomer_goodbye": {
      "name": "welcomer_goodbye",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.welcomer_hello": {
      "name": "welcomer_hello",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    }
  },
  "enums": {},
  "schemas": {},
  "sequences": {},
  "roles": {},
  "policies": {},
  "views": {},
  "_meta": {
    "columns": {},
    "schemas": {},
    "tables": {}
  }
}

```

### File: `drizzle/meta/0009_snapshot.json`
```json
{
  "id": "149036c9-97f0-49d6-9dca-ccd36da86952",
  "prevId": "04d8405b-f906-4dfb-9187-0d5210f7c4cc",
  "version": "7",
  "dialect": "postgresql",
  "tables": {
    "public.Backup": {
      "name": "Backup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "importedFromOrg": {
          "name": "importedFromOrg",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "scheduled": {
          "name": "scheduled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "nextRunAt": {
          "name": "nextRunAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastRunData": {
          "name": "lastRunData",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "cron": {
          "name": "cron",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "timezone": {
          "name": "timezone",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Backup_ownerId_User_id_fk": {
          "name": "Backup_ownerId_User_id_fk",
          "tableFrom": "Backup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.CustomBot": {
      "name": "CustomBot",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "applicationUserId": {
          "name": "applicationUserId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "publicKey": {
          "name": "publicKey",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "clientSecret": {
          "name": "clientSecret",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "CustomBot_ownerId_User_id_fk": {
          "name": "CustomBot_ownerId_User_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "CustomBot_guildId_DiscordGuild_id_fk": {
          "name": "CustomBot_guildId_DiscordGuild_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "CustomBot_applicationId_unique": {
          "name": "CustomBot_applicationId_unique",
          "nullsNotDistinct": false,
          "columns": ["applicationId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordGuild": {
      "name": "DiscordGuild",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'Unknown Server'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerDiscordId": {
          "name": "ownerDiscordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "botJoinedAt": {
          "name": "botJoinedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordGuild_to_Backup": {
      "name": "DiscordGuild_to_Backup",
      "schema": "",
      "columns": {
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "backupId": {
          "name": "backupId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordGuild_to_Backup_backupId_Backup_id_fk": {
          "name": "DiscordGuild_to_Backup_backupId_Backup_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "Backup",
          "columnsFrom": ["backupId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DiscordGuild_to_Backup_discordGuildId_backupId_pk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_backupId_pk",
          "columns": ["discordGuildId", "backupId"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordMember": {
      "name": "DiscordMember",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'0'"
        },
        "owner": {
          "name": "owner",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "favorite": {
          "name": "favorite",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordMember_userId_DiscordUser_id_fk": {
          "name": "DiscordMember_userId_DiscordUser_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordUser",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordMember_guildId_DiscordGuild_id_fk": {
          "name": "DiscordMember_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordMember_userId_guildId_unique": {
          "name": "DiscordMember_userId_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "guildId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordMessageComponent": {
      "name": "DiscordMessageComponent",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "messageId": {
          "name": "messageId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "createdById": {
          "name": "createdById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "draft": {
          "name": "draft",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DMC_to_Flow": {
      "name": "DMC_to_Flow",
      "schema": "",
      "columns": {
        "dmcId": {
          "name": "dmcId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk": {
          "name": "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "DiscordMessageComponent",
          "columnsFrom": ["dmcId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DMC_to_Flow_flowId_Flow_id_fk": {
          "name": "DMC_to_Flow_flowId_Flow_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DMC_to_Flow_dmcId_flowId_pk": {
          "name": "DMC_to_Flow_dmcId_flowId_pk",
          "columns": ["dmcId", "flowId"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.reaction_roles": {
      "name": "reaction_roles",
      "schema": "",
      "columns": {
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "reaction": {
          "name": "reaction",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "reaction_roles_guild_id_DiscordGuild_id_fk": {
          "name": "reaction_roles_guild_id_DiscordGuild_id_fk",
          "tableFrom": "reaction_roles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guild_id"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "reaction_roles_message_id_reaction_pk": {
          "name": "reaction_roles_message_id_reaction_pk",
          "columns": ["message_id", "reaction"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordRoles": {
      "name": "DiscordRoles",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "color": {
          "name": "color",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": false,
          "default": "'0'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "unicodeEmoji": {
          "name": "unicodeEmoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "position": {
          "name": "position",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "hoist": {
          "name": "hoist",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "managed": {
          "name": "managed",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "mentionable": {
          "name": "mentionable",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordRoles_guildId_DiscordGuild_id_fk": {
          "name": "DiscordRoles_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordRoles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordRoles_id_unique": {
          "name": "DiscordRoles_id_unique",
          "nullsNotDistinct": false,
          "columns": ["id"]
        },
        "DiscordRoles_id_guildId_unique": {
          "name": "DiscordRoles_id_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["id", "guildId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordUser": {
      "name": "DiscordUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "globalName": {
          "name": "globalName",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Action": {
      "name": "Action",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Action_flowId_Flow_id_fk": {
          "name": "Action_flowId_Flow_id_fk",
          "tableFrom": "Action",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Flow": {
      "name": "Flow",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.GithubPost": {
      "name": "GithubPost",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "githubId": {
          "name": "githubId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryOwner": {
          "name": "repositoryOwner",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryName": {
          "name": "repositoryName",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "postId": {
          "name": "postId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "GithubPost_postId_unique": {
          "name": "GithubPost_postId_unique",
          "nullsNotDistinct": false,
          "columns": ["postId"]
        },
        "GithubPost_platform_channelId_type_githubId_unique": {
          "name": "GithubPost_platform_channelId_type_githubId_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "channelId", "type", "githubId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.LinkBackup": {
      "name": "LinkBackup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "code": {
          "name": "code",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "LinkBackup_ownerId_User_id_fk": {
          "name": "LinkBackup_ownerId_User_id_fk",
          "tableFrom": "LinkBackup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.MessageLogEntry": {
      "name": "MessageLogEntry",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "messageId": {
          "name": "messageId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "threadId": {
          "name": "threadId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedEveryoneHere": {
          "name": "notifiedEveryoneHere",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "notifiedRoles": {
          "name": "notifiedRoles",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedUsers": {
          "name": "notifiedUsers",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "hasContent": {
          "name": "hasContent",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "embedCount": {
          "name": "embedCount",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        }
      },
      "indexes": {},
      "foreignKeys": {
        "MessageLogEntry_discordGuildId_DiscordGuild_id_fk": {
          "name": "MessageLogEntry_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.OAuthInfo": {
      "name": "OAuthInfo",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "botId": {
          "name": "botId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "accessToken": {
          "name": "accessToken",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "refreshToken": {
          "name": "refreshToken",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "scope": {
          "name": "scope",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "OAuthInfo_discordId_unique": {
          "name": "OAuthInfo_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "OAuthInfo_botId_unique": {
          "name": "OAuthInfo_botId_unique",
          "nullsNotDistinct": false,
          "columns": ["botId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.ShareLink": {
      "name": "ShareLink",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "shareId": {
          "name": "shareId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "origin": {
          "name": "origin",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "ShareLink_userId_User_id_fk": {
          "name": "ShareLink_userId_User_id_fk",
          "tableFrom": "ShareLink",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Token": {
      "name": "Token",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "prefix": {
          "name": "prefix",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "lastUsedAt": {
          "name": "lastUsedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastUsedCountry": {
          "name": "lastUsedCountry",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Token_userId_User_id_fk": {
          "name": "Token_userId_User_id_fk",
          "tableFrom": "Token",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "set null",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Trigger": {
      "name": "Trigger",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'discord'"
        },
        "event": {
          "name": "event",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "flow": {
          "name": "flow",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "disabled": {
          "name": "disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Trigger_flowId_Flow_id_fk": {
          "name": "Trigger_flowId_Flow_id_fk",
          "tableFrom": "Trigger",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.UserToWebhook": {
      "name": "UserToWebhook",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "webhookPlatform": {
          "name": "webhookPlatform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "favorite": {
          "name": "favorite",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "UserToWebhook_userId_User_id_fk": {
          "name": "UserToWebhook_userId_User_id_fk",
          "tableFrom": "UserToWebhook",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "UserToWebhook_fk": {
          "name": "UserToWebhook_fk",
          "tableFrom": "UserToWebhook",
          "tableTo": "Webhook",
          "columnsFrom": ["webhookPlatform", "webhookId"],
          "columnsTo": ["platform", "id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "UserToWebhook_userId_webhookPlatform_webhookId_unique": {
          "name": "UserToWebhook_userId_webhookPlatform_webhookId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "webhookPlatform", "webhookId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.User": {
      "name": "User",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "firstSubscribed": {
          "name": "firstSubscribed",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscribedSince": {
          "name": "subscribedSince",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscriptionExpiresAt": {
          "name": "subscriptionExpiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lifetime": {
          "name": "lifetime",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "User_discordId_unique": {
          "name": "User_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Webhook": {
      "name": "Webhook",
      "schema": "",
      "columns": {
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "Webhook_platform_id_unique": {
          "name": "Webhook_platform_id_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "id"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.autopublish": {
      "name": "autopublish",
      "schema": "",
      "columns": {
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "added_by_id": {
          "name": "added_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "ignore": {
          "name": "ignore",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.buttons": {
      "name": "buttons",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "style": {
          "name": "style",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_label": {
          "name": "custom_label",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "emoji": {
          "name": "emoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "url": {
          "name": "url",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_ephemeral_message_data": {
          "name": "custom_ephemeral_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_dm_message_data": {
          "name": "custom_dm_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_id": {
          "name": "custom_id",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "role_ids": {
          "name": "role_ids",
          "type": "bigint[]",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_public_message_data": {
          "name": "custom_public_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.message_settings": {
      "name": "message_settings",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "max_roles": {
          "name": "max_roles",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.scheduled_posts": {
      "name": "scheduled_posts",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        },
        "user_id": {
          "name": "user_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "future": {
          "name": "future",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "error": {
          "name": "error",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.welcomer_goodbye": {
      "name": "welcomer_goodbye",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.welcomer_hello": {
      "name": "welcomer_hello",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    }
  },
  "enums": {},
  "schemas": {},
  "sequences": {},
  "roles": {},
  "policies": {},
  "views": {},
  "_meta": {
    "columns": {},
    "schemas": {},
    "tables": {}
  }
}

```

### File: `drizzle/meta/0010_snapshot.json`
```json
{
  "id": "7e7a0209-b605-4c88-b87f-bf8cc1f3f526",
  "prevId": "149036c9-97f0-49d6-9dca-ccd36da86952",
  "version": "7",
  "dialect": "postgresql",
  "tables": {
    "public.Backup": {
      "name": "Backup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "importedFromOrg": {
          "name": "importedFromOrg",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "scheduled": {
          "name": "scheduled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "nextRunAt": {
          "name": "nextRunAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastRunData": {
          "name": "lastRunData",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "cron": {
          "name": "cron",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "timezone": {
          "name": "timezone",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Backup_ownerId_User_id_fk": {
          "name": "Backup_ownerId_User_id_fk",
          "tableFrom": "Backup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.CustomBot": {
      "name": "CustomBot",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "applicationUserId": {
          "name": "applicationUserId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "publicKey": {
          "name": "publicKey",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "clientSecret": {
          "name": "clientSecret",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "CustomBot_ownerId_User_id_fk": {
          "name": "CustomBot_ownerId_User_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "CustomBot_guildId_DiscordGuild_id_fk": {
          "name": "CustomBot_guildId_DiscordGuild_id_fk",
          "tableFrom": "CustomBot",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "CustomBot_applicationId_unique": {
          "name": "CustomBot_applicationId_unique",
          "nullsNotDistinct": false,
          "columns": ["applicationId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordGuild": {
      "name": "DiscordGuild",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'Unknown Server'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerDiscordId": {
          "name": "ownerDiscordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "botJoinedAt": {
          "name": "botJoinedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "attachmentChannelId": {
          "name": "attachmentChannelId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordGuild_to_Backup": {
      "name": "DiscordGuild_to_Backup",
      "schema": "",
      "columns": {
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "backupId": {
          "name": "backupId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordGuild_to_Backup_backupId_Backup_id_fk": {
          "name": "DiscordGuild_to_Backup_backupId_Backup_id_fk",
          "tableFrom": "DiscordGuild_to_Backup",
          "tableTo": "Backup",
          "columnsFrom": ["backupId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DiscordGuild_to_Backup_discordGuildId_backupId_pk": {
          "name": "DiscordGuild_to_Backup_discordGuildId_backupId_pk",
          "columns": ["discordGuildId", "backupId"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordMember": {
      "name": "DiscordMember",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'0'"
        },
        "owner": {
          "name": "owner",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        },
        "favorite": {
          "name": "favorite",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordMember_userId_DiscordUser_id_fk": {
          "name": "DiscordMember_userId_DiscordUser_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordUser",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DiscordMember_guildId_DiscordGuild_id_fk": {
          "name": "DiscordMember_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordMember",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordMember_userId_guildId_unique": {
          "name": "DiscordMember_userId_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "guildId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordMessageComponent": {
      "name": "DiscordMessageComponent",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "messageId": {
          "name": "messageId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "createdById": {
          "name": "createdById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "draft": {
          "name": "draft",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DMC_to_Flow": {
      "name": "DMC_to_Flow",
      "schema": "",
      "columns": {
        "dmcId": {
          "name": "dmcId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk": {
          "name": "DMC_to_Flow_dmcId_DiscordMessageComponent_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "DiscordMessageComponent",
          "columnsFrom": ["dmcId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "DMC_to_Flow_flowId_Flow_id_fk": {
          "name": "DMC_to_Flow_flowId_Flow_id_fk",
          "tableFrom": "DMC_to_Flow",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "DMC_to_Flow_dmcId_flowId_pk": {
          "name": "DMC_to_Flow_dmcId_flowId_pk",
          "columns": ["dmcId", "flowId"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.reaction_roles": {
      "name": "reaction_roles",
      "schema": "",
      "columns": {
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "reaction": {
          "name": "reaction",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "reaction_roles_guild_id_DiscordGuild_id_fk": {
          "name": "reaction_roles_guild_id_DiscordGuild_id_fk",
          "tableFrom": "reaction_roles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guild_id"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {
        "reaction_roles_message_id_reaction_pk": {
          "name": "reaction_roles_message_id_reaction_pk",
          "columns": ["message_id", "reaction"]
        }
      },
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordRoles": {
      "name": "DiscordRoles",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "guildId": {
          "name": "guildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "color": {
          "name": "color",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        },
        "permissions": {
          "name": "permissions",
          "type": "text",
          "primaryKey": false,
          "notNull": false,
          "default": "'0'"
        },
        "icon": {
          "name": "icon",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "unicodeEmoji": {
          "name": "unicodeEmoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "position": {
          "name": "position",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "hoist": {
          "name": "hoist",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "managed": {
          "name": "managed",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "mentionable": {
          "name": "mentionable",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "DiscordRoles_guildId_DiscordGuild_id_fk": {
          "name": "DiscordRoles_guildId_DiscordGuild_id_fk",
          "tableFrom": "DiscordRoles",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["guildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "DiscordRoles_id_unique": {
          "name": "DiscordRoles_id_unique",
          "nullsNotDistinct": false,
          "columns": ["id"]
        },
        "DiscordRoles_id_guildId_unique": {
          "name": "DiscordRoles_id_guildId_unique",
          "nullsNotDistinct": false,
          "columns": ["id", "guildId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.DiscordUser": {
      "name": "DiscordUser",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "globalName": {
          "name": "globalName",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "discriminator": {
          "name": "discriminator",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Action": {
      "name": "Action",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Action_flowId_Flow_id_fk": {
          "name": "Action_flowId_Flow_id_fk",
          "tableFrom": "Action",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Flow": {
      "name": "Flow",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.GithubPost": {
      "name": "GithubPost",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "githubId": {
          "name": "githubId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryOwner": {
          "name": "repositoryOwner",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "repositoryName": {
          "name": "repositoryName",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "postId": {
          "name": "postId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "GithubPost_postId_unique": {
          "name": "GithubPost_postId_unique",
          "nullsNotDistinct": false,
          "columns": ["postId"]
        },
        "GithubPost_platform_channelId_type_githubId_unique": {
          "name": "GithubPost_platform_channelId_type_githubId_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "channelId", "type", "githubId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.LinkBackup": {
      "name": "LinkBackup",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "code": {
          "name": "code",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "dataVersion": {
          "name": "dataVersion",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "data": {
          "name": "data",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "previewImageUrl": {
          "name": "previewImageUrl",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "ownerId": {
          "name": "ownerId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {
        "LinkBackup_ownerId_User_id_fk": {
          "name": "LinkBackup_ownerId_User_id_fk",
          "tableFrom": "LinkBackup",
          "tableTo": "User",
          "columnsFrom": ["ownerId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.MessageLogEntry": {
      "name": "MessageLogEntry",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "messageId": {
          "name": "messageId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "threadId": {
          "name": "threadId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedEveryoneHere": {
          "name": "notifiedEveryoneHere",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "notifiedRoles": {
          "name": "notifiedRoles",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "notifiedUsers": {
          "name": "notifiedUsers",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "hasContent": {
          "name": "hasContent",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "embedCount": {
          "name": "embedCount",
          "type": "integer",
          "primaryKey": false,
          "notNull": false,
          "default": 0
        }
      },
      "indexes": {},
      "foreignKeys": {
        "MessageLogEntry_discordGuildId_DiscordGuild_id_fk": {
          "name": "MessageLogEntry_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "MessageLogEntry",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.OAuthInfo": {
      "name": "OAuthInfo",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "botId": {
          "name": "botId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "accessToken": {
          "name": "accessToken",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "refreshToken": {
          "name": "refreshToken",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "scope": {
          "name": "scope",
          "type": "json",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "OAuthInfo_discordId_unique": {
          "name": "OAuthInfo_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        },
        "OAuthInfo_botId_unique": {
          "name": "OAuthInfo_botId_unique",
          "nullsNotDistinct": false,
          "columns": ["botId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.SavedAttachment": {
      "name": "SavedAttachment",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "filename": {
          "name": "filename",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "url": {
          "name": "url",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "title": {
          "name": "title",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "description": {
          "name": "description",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "contentType": {
          "name": "contentType",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "discordMessageId": {
          "name": "discordMessageId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "SavedAttachment_discordGuildId_DiscordGuild_id_fk": {
          "name": "SavedAttachment_discordGuildId_DiscordGuild_id_fk",
          "tableFrom": "SavedAttachment",
          "tableTo": "DiscordGuild",
          "columnsFrom": ["discordGuildId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "SavedAttachment_userId_User_id_fk": {
          "name": "SavedAttachment_userId_User_id_fk",
          "tableFrom": "SavedAttachment",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "set null",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.ShareLink": {
      "name": "ShareLink",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "shareId": {
          "name": "shareId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "origin": {
          "name": "origin",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "ShareLink_userId_User_id_fk": {
          "name": "ShareLink_userId_User_id_fk",
          "tableFrom": "ShareLink",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Token": {
      "name": "Token",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "prefix": {
          "name": "prefix",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "expiresAt": {
          "name": "expiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": true
        },
        "lastUsedAt": {
          "name": "lastUsedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lastUsedCountry": {
          "name": "lastUsedCountry",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Token_userId_User_id_fk": {
          "name": "Token_userId_User_id_fk",
          "tableFrom": "Token",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "set null",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Trigger": {
      "name": "Trigger",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true,
          "default": "'discord'"
        },
        "event": {
          "name": "event",
          "type": "integer",
          "primaryKey": false,
          "notNull": true
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "flow": {
          "name": "flow",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "flowId": {
          "name": "flowId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedById": {
          "name": "updatedById",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "updatedAt": {
          "name": "updatedAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "disabled": {
          "name": "disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "Trigger_flowId_Flow_id_fk": {
          "name": "Trigger_flowId_Flow_id_fk",
          "tableFrom": "Trigger",
          "tableTo": "Flow",
          "columnsFrom": ["flowId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.UserToWebhook": {
      "name": "UserToWebhook",
      "schema": "",
      "columns": {
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "webhookPlatform": {
          "name": "webhookPlatform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "webhookId": {
          "name": "webhookId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "favorite": {
          "name": "favorite",
          "type": "boolean",
          "primaryKey": false,
          "notNull": true,
          "default": false
        }
      },
      "indexes": {},
      "foreignKeys": {
        "UserToWebhook_userId_User_id_fk": {
          "name": "UserToWebhook_userId_User_id_fk",
          "tableFrom": "UserToWebhook",
          "tableTo": "User",
          "columnsFrom": ["userId"],
          "columnsTo": ["id"],
          "onDelete": "cascade",
          "onUpdate": "no action"
        },
        "UserToWebhook_fk": {
          "name": "UserToWebhook_fk",
          "tableFrom": "UserToWebhook",
          "tableTo": "Webhook",
          "columnsFrom": ["webhookPlatform", "webhookId"],
          "columnsTo": ["platform", "id"],
          "onDelete": "no action",
          "onUpdate": "no action"
        }
      },
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "UserToWebhook_userId_webhookPlatform_webhookId_unique": {
          "name": "UserToWebhook_userId_webhookPlatform_webhookId_unique",
          "nullsNotDistinct": false,
          "columns": ["userId", "webhookPlatform", "webhookId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.User": {
      "name": "User",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "bigint",
          "primaryKey": true,
          "notNull": true
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "firstSubscribed": {
          "name": "firstSubscribed",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscribedSince": {
          "name": "subscribedSince",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "subscriptionExpiresAt": {
          "name": "subscriptionExpiresAt",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "lifetime": {
          "name": "lifetime",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false,
          "default": false
        },
        "discordId": {
          "name": "discordId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "User_discordId_unique": {
          "name": "User_discordId_unique",
          "nullsNotDistinct": false,
          "columns": ["discordId"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.Webhook": {
      "name": "Webhook",
      "schema": "",
      "columns": {
        "platform": {
          "name": "platform",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "id": {
          "name": "id",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "token": {
          "name": "token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "name": {
          "name": "name",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "avatar": {
          "name": "avatar",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "channelId": {
          "name": "channelId",
          "type": "text",
          "primaryKey": false,
          "notNull": true
        },
        "applicationId": {
          "name": "applicationId",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "userId": {
          "name": "userId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "discordGuildId": {
          "name": "discordGuildId",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {
        "Webhook_platform_id_unique": {
          "name": "Webhook_platform_id_unique",
          "nullsNotDistinct": false,
          "columns": ["platform", "id"]
        }
      },
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.autopublish": {
      "name": "autopublish",
      "schema": "",
      "columns": {
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "added_by_id": {
          "name": "added_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "ignore": {
          "name": "ignore",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.buttons": {
      "name": "buttons",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "role_id": {
          "name": "role_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "style": {
          "name": "style",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_label": {
          "name": "custom_label",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "emoji": {
          "name": "emoji",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "url": {
          "name": "url",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_ephemeral_message_data": {
          "name": "custom_ephemeral_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_dm_message_data": {
          "name": "custom_dm_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_id": {
          "name": "custom_id",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "role_ids": {
          "name": "role_ids",
          "type": "bigint[]",
          "primaryKey": false,
          "notNull": false
        },
        "type": {
          "name": "type",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "custom_public_message_data": {
          "name": "custom_public_message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.message_settings": {
      "name": "message_settings",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_id": {
          "name": "message_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "max_roles": {
          "name": "max_roles",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.scheduled_posts": {
      "name": "scheduled_posts",
      "schema": "",
      "columns": {
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        },
        "user_id": {
          "name": "user_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "json",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "future": {
          "name": "future",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "error": {
          "name": "error",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.welcomer_goodbye": {
      "name": "welcomer_goodbye",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    },
    "public.welcomer_hello": {
      "name": "welcomer_hello",
      "schema": "",
      "columns": {
        "guild_id": {
          "name": "guild_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": true
        },
        "channel_id": {
          "name": "channel_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_id": {
          "name": "webhook_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "webhook_token": {
          "name": "webhook_token",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "message_data": {
          "name": "message_data",
          "type": "text",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_at": {
          "name": "last_modified_at",
          "type": "timestamp",
          "primaryKey": false,
          "notNull": false
        },
        "last_modified_by_id": {
          "name": "last_modified_by_id",
          "type": "bigint",
          "primaryKey": false,
          "notNull": false
        },
        "override_disabled": {
          "name": "override_disabled",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "ignore_bots": {
          "name": "ignore_bots",
          "type": "boolean",
          "primaryKey": false,
          "notNull": false
        },
        "delete_messages_after": {
          "name": "delete_messages_after",
          "type": "integer",
          "primaryKey": false,
          "notNull": false
        },
        "id": {
          "name": "id",
          "type": "serial",
          "primaryKey": false,
          "notNull": true
        }
      },
      "indexes": {},
      "foreignKeys": {},
      "compositePrimaryKeys": {},
      "uniqueConstraints": {},
      "policies": {},
      "checkConstraints": {},
      "isRLSEnabled": false
    }
  },
  "enums": {},
  "schemas": {},
  "sequences": {},
  "roles": {},
  "policies": {},
  "views": {},
  "_meta": {
    "columns": {},
    "schemas": {},
    "tables": {}
  }
}

```

### File: `drizzle/meta/_journal.json`
```json
{
  "version": "7",
  "dialect": "postgresql",
  "entries": [
    {
      "idx": 0,
      "version": "7",
      "when": 1722183044599,
      "tag": "0000_flawless_william_stryker",
      "breakpoints": true
    },
    {
      "idx": 1,
      "version": "7",
      "when": 1722720802315,
      "tag": "0001_hot_sunspot",
      "breakpoints": true
    },
    {
      "idx": 2,
      "version": "7",
      "when": 1723518627269,
      "tag": "0002_mature_thing",
      "breakpoints": true
    },
    {
      "idx": 3,
      "version": "7",
      "when": 1725210494931,
      "tag": "0003_fat_george_stacy",
      "breakpoints": true
    },
    {
      "idx": 4,
      "version": "7",
      "when": 1727658863157,
      "tag": "0004_ancient_gorgon",
      "breakpoints": true
    },
    {
      "idx": 5,
      "version": "7",
      "when": 1768247907412,
      "tag": "0005_flow-flattening",
      "breakpoints": true
    },
    {
      "idx": 6,
      "version": "7",
      "when": 1771435813968,
      "tag": "0006_json-columns",
      "breakpoints": true
    },
    {
      "idx": 7,
      "version": "7",
      "when": 1775160717092,
      "tag": "0007_update-at-default-now",
      "breakpoints": true
    },
    {
      "idx": 8,
      "version": "7",
      "when": 1775165675686,
      "tag": "0008_update-at-default-now-utc",
      "breakpoints": true
    },
    {
      "idx": 9,
      "version": "7",
      "when": 1776183432926,
      "tag": "0009_no-guilded",
      "breakpoints": true
    },
    {
      "idx": 10,
      "version": "7",
      "when": 1776426591652,
      "tag": "0010_saved-attachments",
      "breakpoints": true
    }
  ]
}

```

