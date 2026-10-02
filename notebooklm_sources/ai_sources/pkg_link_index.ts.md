# Repository Context Group: pkg_link_index.ts
# Source Repository: discohook/discohook

### File: `packages/link/src/index.ts`
```ts
const redirect = (url: string) =>
  new Response(undefined, {
    status: 302,
    headers: {
      Location: url,
    },
  });

export default {
  async fetch(request: Request, env: Env, _context: ExecutionContext) {
    const path = new URL(request.url).pathname;
    if (path === "/") {
      return redirect(`${env.DISCOHOOK_ORIGIN}/link`);
    }
    const part = path.split("/")[1];
    return redirect(`${env.DISCOHOOK_ORIGIN}/link/${part}`);
  },
};

```

