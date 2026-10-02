# Repository Context Group: pkg_bouncer_core
# Source Repository: discohook/discohook

### File: `packages/bouncer/.gitignore`
```gitignore
# dependencies (bun install)
node_modules

# output
out
dist
*.tgz

# code coverage
coverage
*.lcov

# logs
logs
_.log
report.[0-9]_.[0-9]_.[0-9]_.[0-9]_.json

# dotenv environment variable files
.env
.env.development.local
.env.test.local
.env.production.local
.env.local

# caches
.eslintcache
.cache
*.tsbuildinfo

# IntelliJ based IDEs
.idea

# Finder (MacOS) folder config
.DS_Store

```

### File: `packages/bouncer/README.md`
```md
# bouncer

Serverful mini-server that can wait indefinitely (as configured) to pause or 'bounce' a multi-step flow started on a worker. Discohook is in a sort of unique situation in that it needs to execute long processes in response to a service which will only allow 3 seconds before a timeout, so it must use `waitUntil()` which does not allow unlimited wall time.

### Workflow

Assume a user has defined a flow (for a component/trigger) with these actions:
1. Send Message
2. Wait 900 seconds (15min)
3. Delete Message

If Discohook attempts to wait 900 seconds in a `waitUntil()`, Cloudflare will eventually kill the process and the flow will not reach step 3. Instead, consider the following:

1. User presses a button
2. Discohook reads the flow actions
3. Before executing any actions, Discohook sums the longest possible wait time. If it is sufficiently long, a request is sent to `bouncer` with the current state of the flow + authorization and the flow returns (the `waitUntil()` is now over).
4. The `bouncer` server immediately sends the same state back in a new request to the bot worker. Instead of deferring, `bouncer` can keep this connection open which allows Discohook to execute the remainder of the flow for as long as it wants, since Cloudflare imposes "no hard limit" for "as long as the client that sent the request remains connected"[1].

If a flow can be executed without bouncing, it will avoid doing so in order to reduce latency.

### Why not a Durable Object alarm?

1. Expensive
2. There is a hard 15 minute limit imposed on alarm duration

### References

- [1] https://developers.cloudflare.com/workers/platform/limits/#duration

### Develop

To install dependencies:

```bash
bun install
```

To run:

```bash
bun run index.ts
```

This project was created using `bun init` in bun v1.2.8. [Bun](https://bun.sh) is a fast all-in-one JavaScript runtime.

```

### File: `packages/bouncer/index.ts`
```ts
import type { Serve } from "bun";
import { AutoRouter, type IRequest, json } from "itty-router";
import { jwtVerify, SignJWT } from "jose";
import { z } from "zod";

const USER_AGENT =
  "discohook-bouncer/1.0.0 (+https://github.com/discohook/discohook)";

const getIp = (request: IRequest) => {
  const g = (name: string) => request.headers.get(name);
  return (
    g("X-Real-IP") ?? g("X-Forwarded-For") ?? g("Client-IP") ?? g("Forwarded")
  );
};

const router = AutoRouter({
  before: [
    async (request) => {
      const token = request.headers.get("Authorization");
      if (!token) {
        console.log("401:", getIp(request));
        return json({ message: "Unauthorized" }, { status: 401 });
      }

      const key = new TextEncoder().encode(Bun.env.JWT_KEY);
      try {
        await jwtVerify(token, key, {
          issuer: "discohook:bot",
          audience: "discohook:bouncer",
        });
      } catch {
        console.log("403:", getIp(request));
        return json({ message: "Forbidden" }, { status: 403 });
      }
      console.log(
        `OK Auth: ${request.method} ${new URL(request.url).pathname} from ${getIp(request)}`,
      );
    },
  ],
});

let ping: {
  at: number;
  latency: number;
} | null = null;

const now = () => new Date().valueOf();

router.post("/flow/pause", async (request) => {
  const received = now();
  const data = await z
    .object({
      until: z
        .number()
        .int()
        // 60s - 2hr
        .min(received + 60_000)
        .max(received + 7_200_000)
        .optional(),
      payload: z.object({}).loose(),
    })
    .parseAsync(await request.json());

  // after 1 hour
  if (!ping || now() - ping.at > 3_600_000) {
    // re-measure latency for better precision. this doesn't take into account
    // overhead like token verification. the purpose of this is to send the
    // final request at the `until` time minus the latency recorded below such
    // that the server receives it _at the `until` time_ and is able to then
    // process it immediately, making the whole thing appear faster.
    // Unfortunately there is no guarantee that the two systems' clocks are
    // sufficiently synced but we just have to assume that it's negligible.
    const bench1 = now();
    await fetch(Bun.env.BOT_ORIGIN, {
      method: "GET",
      headers: { "User-Agent": USER_AGENT },
    });
    const bench2 = now();
    ping = {
      at: bench1,
      latency: bench2 - bench1,
    };
  }

  const key = new TextEncoder().encode(Bun.env.JWT_KEY);
  const jwt = await new SignJWT()
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setIssuer("discohook:bouncer")
    .setAudience("discohook:bot")
    .setExpirationTime("1 minute")
    .sign(key);
  const resumeRequest = new Request(`${Bun.env.BOT_ORIGIN}/flow/resume`, {
    method: "POST",
    body: JSON.stringify({ payload: data.payload }),
    headers: { Authorization: jwt, "User-Agent": USER_AGENT },
  });

  const startSleeping = async (until: number, pingLatency: number) => {
    const processingLatency = now() - received;
    await Bun.sleep(new Date(until - pingLatency - processingLatency));

    // this should never allow a timeout so that the worker can run for as
    // long as it wants
    // https://developers.cloudflare.com/workers/platform/limits/#duration
    const response = await fetch(resumeRequest);
    if (!response.ok) {
      console.log(await response.json());
    }
  };

  if (data.until !== undefined) {
    startSleeping(data.until, ping.latency);
  } else {
    (async () => {
      const response = await fetch(resumeRequest);
      if (!response.ok) {
        console.log(await response.json());
      }
    })();
  }
  return new Response(null, { status: 204 });
});

export default {
  // shouldn't affect our sleep timeout or the
  // indefinitely-long resume request
  idleTimeout: 20,
  fetch: router.fetch,
} satisfies Serve;

```

### File: `packages/bouncer/package.json`
```json
{
  "name": "bouncer",
  "module": "index.ts",
  "type": "module",
  "scripts": {
    "dev": "PORT=8792 bun --hot index.ts",
    "start": "PORT=8792 bun index.ts"
  },
  "private": true,
  "devDependencies": {
    "@types/bun": "^1.2.16"
  },
  "peerDependencies": {
    "typescript": "^5"
  },
  "dependencies": {
    "itty-router": "^5.0.18",
    "jose": "^6.0.11",
    "zod": "^4.1.5"
  }
}

```

### File: `packages/bouncer/tsconfig.json`
```json
{
  "compilerOptions": {
    // Environment setup & latest features
    "lib": ["ESNext"],
    "target": "ESNext",
    "module": "ESNext",
    "moduleDetection": "force",
    "jsx": "react-jsx",
    "allowJs": true,

    // Bundler mode
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "noEmit": true,

    // Best practices
    "strict": true,
    "skipLibCheck": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,

    // Some stricter flags (disabled by default)
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noPropertyAccessFromIndexSignature": false
  }
}

```

