# Repository Context Group: bot_listeners
# Source Repository: no-peace/Hoho_manager

### File: `bot/src/listeners/interactionRelay.ts`
```ts
import { Listener } from '@sapphire/framework';
import { env } from '../lib/env.js';

export class RawInteractionRelay extends Listener {
  public constructor(context: Listener.Context, options: Listener.Options) {
    // Omitting 'emitter' safely defaults to the standard Discord client
    super(context, {
      ...options,
      event: 'raw' 
    });
  }

  public async run(packet: any) {
    if (packet.t !== 'INTERACTION_CREATE') return;

    const rawInteraction = packet.d;

    try {
      // Using the strictly-typed camelCase properties from your env.ts
      const res = await fetch(`${env.apiBaseUrl}/api/interactions/relay`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-admin-key': env.adminApiKey,
        },
        // Safely convert BigInts to strings so Express doesn't crash
        body: JSON.stringify(rawInteraction, (_, v) => typeof v === 'bigint' ? v.toString() : v)
      });

      if (!res.ok) {
        const text = await res.text();
        this.container.logger.warn(`API rejected relay: ${res.status} - ${text}`);
      } else {
        this.container.logger.info(`✅ Successfully relayed button click to API!`);
      }
    } catch (error) {
      this.container.logger.error(`Failed to reach the API at ${env.apiBaseUrl}`, error);
    }
  }
}
```

### File: `bot/src/listeners/ready.ts`
```ts
import { Listener } from "@sapphire/framework";
import { Events, type Client } from "discord.js";
import { env } from "../lib/env.js";

/**
 * Fires once when the gateway connection is established.
 *
 * Sustained `run(...args: unknown[])` rather than narrowing the parameter type:
 * Sapphire dispatches every listener through the same base signature, so a
 * narrower override would not be a valid subtype. The cast is the single place
 * where the event's real payload is recovered.
 */
export class ReadyListener extends Listener {
  public constructor(context: Listener.LoaderContext, options: Listener.Options) {
    super(context, { ...options, once: true, event: Events.ClientReady });
  }

  public override run(...args: unknown[]): void {
    const client = args[0] as Client<true>;

    console.log(`[bot] ready as ${client.user.tag} — ${client.guilds.cache.size} guild(s)`);
    console.log(
      env.devGuildId
        ? `[bot] application commands scoped to guild ${env.devGuildId}`
        : "[bot] application commands registered globally (may take up to an hour to appear)",
    );
  }
}

```

