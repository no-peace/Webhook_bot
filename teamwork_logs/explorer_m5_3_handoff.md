# Handoff Report: File Attachments & Discohook Spec Miner

**Agent ID**: `explorer_m5_3`  
**Role**: File Attachments & Discohook Spec Miner Explorer  
**Milestone**: Milestone 5 — Discord OAuth2 Login & File Attachments (R2: File Attachments & Media Upload)  
**Date**: 2026-10-04  

---

## 1. Observation

### 1.1 Reference Implementation in Discohook (`discohook_src`)
Direct inspection of `discohook_src` reveals the exact UI patterns, data models, and Discord multipart upload specifications used by Discohook:

1. **`discohook_src/packages/site/app/components/editor/MessageEditor.client.tsx:874-1240` (`MessageAttachmentsSection`)**:
   - **Header & Section**: Wrapped in `EmbedEditorSection` with title `Files (${count})`, an error badge when a local file is missing, and a warning badge when duplicate filenames are detected.
   - **Card Structure**: A horizontal scroll row (`flex gap-2 overflow-x-auto`) of attachment cards. Each card has:
     - Card container: `relative rounded-lg bg-background-secondary dark:bg-background-secondary-dark border border-border-normal dark:border-border-normal-dark py-1.5 px-2 w-32 box-border shrink-0`.
     - Aspect ratio box (`w-full aspect-[1.15/1] rounded-lg flex relative bg-gray-200 dark:bg-[#97979F]/[0.08]`):
       - Image preview: `<img src={attachment.url} className="object-contain h-fit w-max max-w-full max-h-full rounded-lg m-auto" />`.
       - Video preview: `<video src={attachment.url} className="object-contain ... select-none" />`.
       - Generic document: Document icon centered.
       - Spoiler overlay: If `isSpoiler`, an overlay with `backdrop-blur-2xl rounded-lg` and a central black pill `bg-black/60 px-3 py-0.5` displaying uppercase "SPOILER".
     - Control buttons (top-right corner overlay of card):
       - Spoiler toggle button (Hide/Show eye icon) to toggle `AttachmentFlags.IsSpoiler`.
       - Edit button (pencil icon) opening `AttachmentEditModal` (for alt text description / renaming).
       - Delete button (trash icon) removing the attachment from state.
     - Reorder buttons: Chevrons (`Chevron_Left` and `Chevron_Right`) in bottom corners to reorder attachments.
     - Filename button: Truncated filename with click-to-copy functionality and formatted filesize tooltip.
   - **Upload Controls**:
     - Hidden file input: `<input id="files-${mid}" type="file" hidden multiple onChange={...} />`.
     - "+ Add File" button (`<Button onClick={() => input.click()} disabled={files.length >= 10}>Add File</Button>`).
     - Paste button / drag-and-drop zone (`PasteFileButton`).

2. **`discohook_src/packages/site/app/util/files.ts`**:
   - Line 9: `MAX_FILES_PER_MESSAGE = 10`.
   - Line 17-23: `ATTACHMENT_URI_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".gif"] as const`.
   - Line 39-43: `transformFileName`:
     ```ts
     export const transformFileName = (filename: string) =>
       filename
         .replace(/ /g, "_")
         .replace(/[^a-zA-Z0-9._-]/g, "")
         .trim() || "unknown";
     ```
   - Line 45-55: `attachmentFromFile`: Maps local file to `APIAttachment` with `URL.createObjectURL(file)`.

3. **`discohook_src/packages/site/app/components/preview/Embed.tsx:26-60` (`resolveAttachmentUri`)**:
   - Embeds can reference uploaded attachments using the URI scheme `attachment://filename.ext` in `image.url`, `thumbnail.url`, `author.icon_url`, or `footer.icon_url`.
   - `resolveAttachmentUri` resolves `attachment://filename` to the local object URL `attachment.url` in the preview so embed images display immediately without external image hosts.

4. **`discohook_src/packages/site/app/util/discord.ts:124-144, 288-318, 387-425`**:
   - Outbound multipart request construction:
     ```ts
     body = new FormData();
     body.set("payload_json", JSON.stringify(payload));
     let i = 0;
     for (const { file, key } of options.files) {
       body.append(key ?? `files[${i}]`, file, file.name);
       i += 1;
     }
     ```
   - Payload attachments mapping:
     `payload.attachments = localAttachments.map((a, i) => ({ id: i, filename: a.filename, description: a.description, is_spoiler: ... }))`.

---

### 1.2 Current Hoho Manager Codebase Observations

1. **`hoho_manager/client/src/components/editor/MessageEditor.tsx:1-177`**:
   - Only contains Editor Mode Tabs (`Classic` / `Components V2`), `TextArea` for content, `identitySection` (Username, Avatar URL, Thread name), and `EmbedEditor` list.
   - **Zero** file attachment UI exists.

2. **`hoho_manager/client/src/store/messageStore.ts:52-94, 397-407`**:
   - `MessageState` contains: `mode`, `data: MessageData`, `targets: TargetData[]`, `selection`, `send: SendState`.
   - `persist` middleware partializes:
     ```ts
     partialize: (state) => ({
       mode: state.mode,
       data: state.data,
       targets: state.targets,
     })
     ```
   - **Crucial observation**: Native browser `File` or `Blob` objects **cannot** be JSON-serialized into `localStorage`. Any file attachment state stored in Zustand must either be excluded from `partialize` or managed in a non-persisted store / field to avoid corrupting localStorage or crashing during state rehydration.

3. **`hoho_manager/client/src/utils/discord.ts:98-102` (`isPayloadEmpty`)**:
   ```ts
   export const isPayloadEmpty = (payload: DiscordMessagePayload): boolean =>
     !payload.content &&
     !(payload.embeds && payload.embeds.length > 0) &&
     !(payload.components && payload.components.length > 0);
   ```
   - **Defect/Blocker**: If a user uploads an image/file attachment with no text content and no embeds, `isPayloadEmpty` evaluates to `true`, and `useSend.ts:42-45` rejects the send with `"Message is empty"`. In Discord, a message consisting purely of an attachment is valid.

4. **`hoho_manager/client/src/hooks/useSend.ts:53-77`**:
   - When `sendMode === SEND_MODES.BOT`, it sends JSON via `fetch(`${baseUrl}/api/send`, { headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })`.
   - When `sendMode === SEND_MODES.WEBHOOK`, it calls `sendWebhookDirect(webhookUrl, payload, ...)` directly in the browser, bypassing the server's `/api/send`, skipping mention scrubbing, audit logging, and multipart handling.

5. **`hoho_manager/server/src/routes/send.ts:26-44, 115-144`**:
   - Handles `POST /api/send`.
   - Expects `req.body` parsed as JSON by `express.json()`.
   - Does not have `multer` or multipart parsing.
   - Calls `discord.sendWebhook(webhookUrl, finalMessage)` or `discord.sendChannelMessage(channelId, finalMessage)`.

6. **`hoho_manager/server/src/services/discordService.ts:141-217` (`apiRequest`)**:
   - Lines 156-165:
     ```ts
     const headers: Record<string, string> = { "Content-Type": "application/json" };
     if (token) headers.Authorization = `${auth} ${token}`;
     response = await fetch(url, {
       method,
       headers,
       body: body === undefined ? undefined : JSON.stringify(body),
     });
     ```
   - `apiRequest` only handles JSON string bodies. It does not accept or forward file buffers or `FormData`.

7. **`hoho_manager/server/package.json:16-25`**:
   - Dependencies: `@dmb/shared`, `better-sqlite3`, `cors`, `discord-interactions`, `dotenv`, `express` (v5.2.1), `express-rate-limit`, `helmet`.
   - `multer` is **not** currently installed.
   - Node engine: `>=20`. Node 20 natively provides global `FormData`, `Blob`, `File`, and `fetch`.

---

## 2. Logic Chain

### 2.1 Discord API Multi-Part Attachments Protocol
To send attachments to Discord via either Webhook (`POST /webhooks/:id/:token?wait=true`) or Bot Channel Message (`POST /channels/:id/messages`), Discord's REST API requires the following wire protocol:

1. **Request Content-Type**:
   - Must be `multipart/form-data; boundary=---------------------------...`.
   - When using native `fetch` with `FormData` in Node 20+ or browser, **do NOT set the `Content-Type` header manually**; the runtime will generate the header complete with the multipart boundary.

2. **Form Fields**:
   - `payload_json` (string, content-type `application/json`):
     - The JSON representation of the message payload (identical to normal JSON payload: `content`, `embeds`, `components`, `allowed_mentions`, etc.).
     - Contains an `attachments` metadata array:
       ```json
       "attachments": [
         {
           "id": 0,
           "filename": "chart.png",
           "description": "Sales chart for Q3",
           "is_spoiler": false
         },
         {
           "id": 1,
           "filename": "SPOILER_secret.pdf",
           "description": "Confidential report",
           "is_spoiler": true
         }
       ]
       ```
   - `files[0]`, `files[1]`, ..., `files[N-1]` (binary form-data parts):
     - Each part's form field name must match `files[${id}]` where `${id}` matches the integer `id` declared in `payload_json.attachments`.
     - `Content-Disposition: form-data; name="files[0]"; filename="chart.png"`.
     - `Content-Type: image/png` (matching MIME type or `application/octet-stream`).

3. **Discord Limits & Constraints**:
   - **Max Files Per Message**: 10 files.
   - **Max File Size**: 25 MB (standard non-boosted Discord guild limit).
   - **Filename Sanitization**: Discord strips non-ASCII and converts spaces to underscores (`transformFileName`).
   - **Spoiler Handling**:
     - Either prefix the filename with `SPOILER_` (e.g., `SPOILER_cat.png`),
     - Or provide `is_spoiler: true` in the `attachments[n]` metadata object. Providing both guarantees spoiler styling across all Discord desktop, web, and mobile clients.

---

### 2.2 Client-Server-Discord Transport Architecture

```
┌────────────────────────────────────────────────────────┐
│                      Client                            │
│  MessageEditor: FileAttachmentsSection                 │
│  attachedFiles: [ { id, file: File, previewUrl, ... } ] │
└──────────────────────────┬─────────────────────────────┘
                           │ POST /api/send
                           │ Content-Type: multipart/form-data
                           │ Field 1: payload_json = JSON.stringify({ mode, channelId, webhookUrl, payload, ... })
                           │ Field 2..N: files = File binaries
                           ▼
┌────────────────────────────────────────────────────────┐
│               Backend Express Server                   │
│  1. multer.memoryStorage() parses multipart in memory  │
│  2. Extracts req.body.payload_json -> req.body         │
│  3. req.files -> Array of in-memory Buffer objects     │
│  4. Runs attachUser, sendLimiter, requireStaffPerm     │
│  5. scrubMentions & scrubFlows on payload              │
│  6. ZERO local disk storage (instant GC)               │
└──────────────────────────┬─────────────────────────────┘
                           │ Forward to Discord REST API
                           │ FormData with payload_json + files[0..n]
                           ▼
┌────────────────────────────────────────────────────────┐
│                   Discord REST API                     │
│  POST /channels/:id/messages (Bot)                     │
│  OR POST /webhooks/:id/:token?wait=true (Webhook)      │
└────────────────────────────────────────────────────────┘
```

#### Step 1: Client State Modeling
In `hoho_manager/client/src/store/messageStore.ts`:
- Define `AttachedFile`:
  ```ts
  export interface AttachedFile {
    id: string; // unique client id, e.g. "att_123"
    file: File; // native browser File
    name: string; // original name
    size: number; // bytes
    type: string; // MIME type
    previewUrl: string; // URL.createObjectURL(file)
    spoiler?: boolean;
    description?: string; // alt text
  }
  ```
- Store actions:
  - `addFiles(files: File[])`: Validates file size (≤ 25MB) and total count (≤ 10). Generates object URL and appends to `attachedFiles`.
  - `removeFile(id: string)`: Revokes object URL (`URL.revokeObjectURL`) and filters out file.
  - `toggleFileSpoiler(id: string)`: Inverts spoiler flag.
  - `updateFileDescription(id: string, description: string)`: Updates alt text.
  - `clearFiles()`: Revokes all object URLs and empties the list.
- **Persistence Safety**: In `messageStore.ts:partialize`, **DO NOT** include `attachedFiles`. `attachedFiles` stays in memory for the session.

#### Step 2: Empty Payload Validation Fix
In `hoho_manager/client/src/utils/discord.ts`:
Update `isPayloadEmpty`:
```ts
export const isPayloadEmpty = (
  payload: DiscordMessagePayload,
  hasAttachments: boolean = false,
): boolean =>
  !hasAttachments &&
  !payload.content &&
  !(payload.embeds && payload.embeds.length > 0) &&
  !(payload.components && payload.components.length > 0);
```

#### Step 3: Embed Preview Attachment URI Resolver
In `hoho_manager/client/src/components/preview/EmbedPreview.tsx`:
Implement `resolveAttachmentUri`:
If `embed.image?.url?.startsWith("attachment://")` or `embed.thumbnail?.url?.startsWith("attachment://")`, look up the filename in `attachedFiles` and substitute the local `previewUrl`. This reproduces Discohook's feature where local attachments can be embedded directly into embed previews.

#### Step 4: Client Send Packaging
In `hoho_manager/client/src/hooks/useSend.ts` and `BotDispatchModal.tsx`:
- If `attachedFiles.length === 0`: Continue sending standard `application/json` as before.
- If `attachedFiles.length > 0`:
  - Construct a browser `FormData`:
  - Prepare `payload_json` payload object with:
    - `mode` ("bot" | "webhook")
    - `channelId`, `webhookUrl`, `threadId`, `profileId`, `editMessageId`, `flows`
    - `payload`: sanitized message payload with `attachments` metadata:
      ```ts
      attachments: attachedFiles.map((f, idx) => ({
        id: idx,
        filename: f.spoiler && !f.name.startsWith("SPOILER_") ? `SPOILER_${f.name}` : f.name,
        description: f.description,
        is_spoiler: f.spoiler ?? false,
      }))
      ```
  - `formData.append("payload_json", JSON.stringify(body));`
  - For each file:
    `formData.append("files", f.file, f.spoiler && !f.name.startsWith("SPOILER_") ? `SPOILER_${f.name}` : f.name);`
  - POST to `/api/send` with headers: `{ "x-admin-key": adminKey }` (omit `Content-Type`).

#### Step 5: Backend In-Memory Multipart Handling
In `hoho_manager/server`:
- Install `multer` and `@types/multer`.
- In `routes/send.ts`:
  ```ts
  import multer from "multer";
  const upload = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: 25 * 1024 * 1024, files: 10 },
  });
  ```
- Insert `upload.any()` before request handlers:
  ```ts
  router.post(
    "/",
    upload.any(),
    (req, _res, next) => {
      if (req.body.payload_json) {
        try {
          const parsed = JSON.parse(req.body.payload_json);
          req.body = { ...parsed, ...req.body };
        } catch {
          throw ApiError.badRequest("Invalid `payload_json` format");
        }
      }
      next();
    },
    attachUser,
    sendLimiter,
    requireStaffPermission("send"),
    ...
  );
  ```
- File buffers extracted from `(req.files as Express.Multer.File[])`.
- Zero disk storage: buffers reside exclusively in RAM and are cleaned up by Node's V8 garbage collector immediately after request completion.

#### Step 6: Backend-to-Discord API Streaming
In `hoho_manager/server/src/services/discordService.ts`:
- Enhance `apiRequest` to accept `files?: Array<{ buffer: Buffer; originalname: string; mimetype: string }>`:
  ```ts
  if (files && files.length > 0) {
    const formData = new FormData();
    const payloadJson = typeof body === "object" && body !== null ? { ...body } : {};
    
    if (!payloadJson.attachments) {
      payloadJson.attachments = files.map((f, idx) => ({
        id: idx,
        filename: f.originalname,
      }));
    }
    
    formData.append("payload_json", JSON.stringify(payloadJson));
    files.forEach((f, idx) => {
      const blob = new Blob([f.buffer], { type: f.mimetype || "application/octet-stream" });
      formData.append(`files[${idx}]`, blob, f.originalname);
    });
    
    // In Node 20+, fetch with FormData automatically sets multipart/form-data boundary
    requestBody = formData;
  } else {
    headers["Content-Type"] = "application/json";
    requestBody = body === undefined ? undefined : JSON.stringify(body);
  }
  ```
- Pass `files` through `sendWebhook`, `sendChannelMessage`, and `editChannelMessage`.

---

## 3. Caveats

1. **Discord Guild Boost Limits**:
   - Default Discord servers allow up to 25 MB per attachment.
   - Boosted servers allow 50 MB (Tier 2) or 100 MB (Tier 3).
   - Our validation is set to 25 MB max per file as the safe, universally supported default. A clear warning message is shown if a file exceeds 25 MB.

2. **Memory Footprint for In-Memory Buffers**:
   - 10 files * 25 MB = 250 MB peak memory per simultaneous send request.
   - Node 20 process handles this comfortably, and memory is released immediately once the outbound fetch to Discord finishes. No permanent disk files are created.

3. **Rate Limiting on Large Uploads**:
   - Uploading multiple 20MB files over slower uplinks takes a few seconds. The client UI should show a distinct loading/sending state with "Uploading attachments..." to avoid impatient double-clicks.

4. **Webhook Execution Route Consolidation**:
   - Previously, client-side webhook sends in `useSend.ts` called Discord's webhook URL directly from the browser (`sendWebhookDirect`), while bot sends went through `/api/send`.
   - Webhook sends with attachments must route through `/api/send` (`mode: "webhook"`), which guarantees mention scrubbing, audit logging, and consistent error handling without browser CORS complications.

---

## 4. Conclusion & Actionable Recommendations

### 4.1 UI Component Blueprint: `FileAttachmentsSection.tsx`
Create `hoho_manager/client/src/components/editor/FileAttachmentsSection.tsx` matching Discohook's `#1e1f22` dark aesthetic:

```tsx
import React, { useRef, useState } from "react";
import { ChevronDown, ChevronRight, Eye, EyeOff, Paperclip, Trash2, Upload, AlertCircle } from "lucide-react";
import { Button } from "../ui/Button";
import { useMessageStore } from "../../store/messageStore";

const MAX_FILES = 10;
const MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024; // 25 MB

const formatBytes = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

export const FileAttachmentsSection: React.FC = () => {
  const [open, setOpen] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const attachedFiles = useMessageStore((state) => state.attachedFiles);
  const addFiles = useMessageStore((state) => state.addFiles);
  const removeFile = useMessageStore((state) => state.removeFile);
  const toggleFileSpoiler = useMessageStore((state) => state.toggleFileSpoiler);

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    setErrorMsg(null);
    const files = Array.from(fileList);

    if (attachedFiles.length + files.length > MAX_FILES) {
      setErrorMsg(`Maximum ${MAX_FILES} attachments allowed per message.`);
      return;
    }

    const oversized = files.filter((f) => f.size > MAX_FILE_SIZE_BYTES);
    if (oversized.length > 0) {
      setErrorMsg(`File "${oversized[0].name}" exceeds the 25 MB limit.`);
      return;
    }

    addFiles(files);
  };

  return (
    <section className="bg-[#232428] rounded border border-[#1e1f22]">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-2.5 text-left text-xs font-bold text-[#949ba4] hover:text-[#dbdee1] transition-colors"
      >
        <span className="flex items-center gap-1.5 uppercase tracking-wide text-[11px]">
          <Paperclip size={13} /> File Attachments ({attachedFiles.length}/{MAX_FILES})
        </span>
        {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
      </button>

      {open && (
        <div className="p-2.5 pt-0 border-t border-[#1e1f22] space-y-3 mt-1">
          {errorMsg && (
            <div className="flex items-center gap-1.5 p-2 rounded bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
              <AlertCircle size={14} />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Drag & Drop Zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(e) => { e.preventDefault(); setIsDragging(false); handleFiles(e.dataTransfer.files); }}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-all ${
              isDragging
                ? "border-[#5865f2] bg-[#5865f2]/10"
                : "border-[#35373c] hover:border-[#4e5058] bg-[#1e1f22]/50 hover:bg-[#1e1f22]"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={(e) => handleFiles(e.target.files)}
            />
            <Upload size={20} className="mx-auto text-[#949ba4] mb-1.5" />
            <p className="text-xs font-medium text-[#dbdee1]">
              Drag & drop files here, or <span className="text-[#5865f2] hover:underline">browse</span>
            </p>
            <p className="text-[11px] text-[#949ba4] mt-0.5">
              Supports images, videos, audio, and documents up to 25 MB each.
            </p>
          </div>

          {/* Attached Files List */}
          {attachedFiles.length > 0 && (
            <div className="flex gap-2 overflow-x-auto pb-1.5 pt-1">
              {attachedFiles.map((file) => (
                <div
                  key={file.id}
                  className="relative group rounded-lg bg-[#1e1f22] border border-[#2b2d31] p-1.5 w-32 shrink-0 flex flex-col justify-between"
                >
                  {/* Thumbnail / Media Container */}
                  <div className="w-full aspect-[1.15/1] rounded bg-[#2b2d31] flex relative overflow-hidden items-center justify-center">
                    {file.type.startsWith("image/") ? (
                      <img src={file.previewUrl} alt={file.name} className="object-cover w-full h-full" />
                    ) : (
                      <Paperclip size={24} className="text-[#949ba4]" />
                    )}

                    {file.spoiler && (
                      <div className="absolute inset-0 bg-black/70 backdrop-blur-xs flex items-center justify-center">
                        <span className="text-[10px] font-bold text-white uppercase tracking-wider bg-black/60 px-2 py-0.5 rounded-full">
                          Spoiler
                        </span>
                      </div>
                    )}

                    {/* Overlay Action Buttons */}
                    <div className="absolute top-1 right-1 flex gap-1 bg-[#1e1f22]/90 rounded p-0.5 opacity-90 group-hover:opacity-100 transition-opacity">
                      <button
                        type="button"
                        onClick={(e) => { e.stopPropagation(); toggleFileSpoiler(file.id); }}
                        title={file.spoiler ? "Remove spoiler" : "Mark as spoiler"}
                        className="p-1 hover:text-[#5865f2] text-[#949ba4]"
                      >
                        {file.spoiler ? <EyeOff size={12} /> : <Eye size={12} />}
                      </button>
                      <button
                        type="button"
                        onClick={(e) => { e.stopPropagation(); removeFile(file.id); }}
                        title="Delete file"
                        className="p-1 hover:text-red-400 text-[#949ba4]"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </div>

                  {/* Metadata */}
                  <div className="mt-1.5">
                    <p className="text-[11px] font-medium text-[#dbdee1] truncate" title={file.name}>
                      {file.name}
                    </p>
                    <p className="text-[10px] text-[#949ba4]">
                      {formatBytes(file.size)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
};
```

### 4.2 Required Modifications by File

| Target File | Change Description |
|---|---|
| `hoho_manager/server/package.json` | Add `"multer": "^1.4.5-lts.1"` to dependencies, `"@types/multer": "^1.4.12"` to devDependencies. |
| `hoho_manager/server/src/services/discordService.ts` | Update `apiRequest` to accept `files` array. When files are present, assemble Node 20 `FormData` with `payload_json` and `files[idx]`. Pass `files` through `sendWebhook`, `sendChannelMessage`, and `editChannelMessage`. |
| `hoho_manager/server/src/routes/send.ts` | Mount `multer({ storage: multer.memoryStorage(), limits: { fileSize: 25 * 1024 * 1024, files: 10 } }).any()`. Parse `payload_json` if present into `req.body`. Extract `req.files` and forward to `discordService`. |
| `hoho_manager/client/src/store/messageStore.ts` | Add `attachedFiles: AttachedFile[]` state and actions (`addFiles`, `removeFile`, `toggleFileSpoiler`, `clearFiles`). Exclude `attachedFiles` from `partialize`. Clean up object URLs on reset. |
| `hoho_manager/client/src/utils/discord.ts` | Update `isPayloadEmpty` to accept `hasAttachments` boolean so messages with only files are not rejected. |
| `hoho_manager/client/src/components/editor/FileAttachmentsSection.tsx` | New component implementing the Discohook `#1e1f22` file attachment accordion, drag/drop zone, and file card list. |
| `hoho_manager/client/src/components/editor/MessageEditor.tsx` | Mount `FileAttachmentsSection` in both Classic and Components V2 modes. |
| `hoho_manager/client/src/components/preview/MessagePreview.tsx` | Render attached files in the live preview (images in a responsive grid, files as document cards with spoiler blur support). |
| `hoho_manager/client/src/components/preview/EmbedPreview.tsx` | Support resolving `attachment://filename` to the local file's `previewUrl`. |
| `hoho_manager/client/src/hooks/useSend.ts` | Package `FormData` with `payload_json` and `files` when `attachedFiles.length > 0`. Route both bot and webhook sends through `/api/send`. |
| `hoho_manager/client/src/components/send/BotDispatchModal.tsx` | When files are present, package `FormData` for multi-channel dispatch to `/api/send`. |

---

## 5. Verification Method

### 5.1 Automated Typecheck & Test Commands
Run across all packages to verify zero regressions:
```powershell
# From C:\Users\Nipun\Desktop\projects\Utility\discord_bots\webhook_bot\hoho_manager
npm run typecheck
npm run test
```

### 5.2 Unit & Integration Tests
1. **Server Route Tests (`hoho_manager/server/src/routes/send.test.ts`)**:
   - Send `multipart/form-data` with `payload_json` and binary attachment file buffer.
   - Verify `200 OK` response.
   - Verify mock `discord.sendChannelMessage` or `discord.sendWebhook` receives the parsed message and `files` array.
   - Verify mention scrubber executes on `payload_json` content when `x-staff-id` is supplied.
2. **Client Validation Tests (`hoho_manager/client/src/utils/discord.test.ts`)**:
   - Verify `isPayloadEmpty({}, true)` returns `false`.
   - Verify `isPayloadEmpty({}, false)` returns `true`.

### 5.3 Live E2E Verification
As authorized in the project guidelines (server `906426036772818954`, test channel `1363426163892162591`):
1. Launch app on `http://localhost:5173`.
2. Attach a sample `.png` file and a `.txt` file using the new "File Attachments" section in `MessageEditor`.
3. Toggle spoiler on the `.png` file — verify spoiler blur appears in the editor card and in the live preview.
4. Send the message via Bot to the authorized test channel.
5. Verify the message arrives in Discord with both attachments rendered natively without server errors or permanent disk files.
