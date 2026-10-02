# Repository Context Group: shared_core
# Source Repository: no-peace/Hoho_manager

### File: `shared/package.json`
```json
{
  "name": "@dmb/shared",
  "version": "0.1.0",
  "private": true,
  "description": "Types and constants shared by the client and server.",
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js"
    }
  },
  "files": [
    "dist"
  ],
  "scripts": {
    "build": "tsc -p tsconfig.build.json",
    "test": "vitest run",
    "typecheck": "tsc -p tsconfig.json --noEmit"
  },
  "devDependencies": {
    "typescript": "^5.9.3",
    "vitest": "^3.2.7"
  }
}

```

### File: `shared/tsconfig.build.json`
```json
{
  "extends": "./tsconfig.json",
  "//": "Build-only config: identical to tsconfig.json but without test files, so vitest specs never land in dist/.",
  "exclude": ["src/**/*.test.ts"]
}

```

### File: `shared/tsconfig.json`
```json
{
  "extends": "../tsconfig.base.json",
  "compilerOptions": {
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "rootDir": "src",
    "outDir": "dist",
    "noUnusedLocals": false,
    "noUnusedParameters": false
  },
  "include": ["src/**/*.ts"]
}

```

