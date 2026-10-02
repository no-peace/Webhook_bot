# Repository Context Group: pkg_store_util
# Source Repository: discohook/discohook

### File: `packages/store/src/util/text.ts`
```ts
export const randomString = (length: number) => {
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < length; i += 1) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }

  return result;
};

```

