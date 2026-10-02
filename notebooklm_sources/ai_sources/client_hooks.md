# Repository Context Group: client_hooks
# Source Repository: no-peace/Hoho_manager

### File: `client/src/hooks/useMessage.ts`
```ts
import { useMemo } from "react";
import type { DiscordMessagePayload } from "@dmb/shared";
import { useMessageStore } from "../store/messageStore";
import { isPayloadEmpty } from "../utils/discord";

/**
 * Read-only view of the message document plus derived values.
 *
 * `getPayload`/`getValidationErrors` are functions on the store, which do not
 * trigger re-renders on their own. This hook recomputes them whenever the
 * document changes, so components can read `payload` and `problems` directly.
 */
export interface MessageView {
  mode: ReturnType<typeof useMessageStore.getState>["mode"];
  data: ReturnType<typeof useMessageStore.getState>["data"];
  payload: DiscordMessagePayload;
  problems: string[];
  isEmpty: boolean;
  embedCount: number;
  componentCount: number;
}

export const useMessage = (): MessageView => {
  const mode = useMessageStore((state) => state.mode);
  const data = useMessageStore((state) => state.data);

  const payload = useMemo(
    () => useMessageStore.getState().getPayload(),
    // Recomputed whenever the document changes.
    [mode, data],
  );

  const problems = useMemo(() => useMessageStore.getState().getValidationErrors(), [mode, data]);

  return {
    mode,
    data,
    payload,
    problems,
    isEmpty: isPayloadEmpty(payload),
    embedCount: data.embeds.length,
    componentCount: data.components.length,
  };
};

export default useMessage;

```

### File: `client/src/hooks/useSend.ts`
```ts
import { useCallback } from "react";
import { sendWebhookDirect } from "../api/discord";
import { useActionStore } from "../store/actionStore";
import { useMessageStore } from "../store/messageStore";
import { useProfileStore } from "../store/profileStore";
import { SEND_MODES } from "../utils/constants";
import type { EditorMode, SendModeValue } from "../utils/constants";
import { isPayloadEmpty } from "../utils/discord";

export interface SendResult {
  ok: boolean;
  error?: string;
  result?: unknown;
}

export interface UseSendReturn {
  sendMessage: (editMessageId?: string) => Promise<SendResult>;
  isConfigured: boolean;
  mode: EditorMode;
  sendMode: SendModeValue;
}

export const useSend = (): UseSendReturn => {
  const mode = useMessageStore((state) => state.mode);
  const setSendState = useMessageStore((state) => state.setSendState);

  const sendMode = useProfileStore((state) => state.sendMode);
  const webhookUrl = useProfileStore((state) => state.webhookUrl);
  const channelId = useProfileStore((state) => state.channelId);
  const threadId = useProfileStore((state) => state.threadId);
  const botProfileId = useProfileStore((state) => state.botProfileId);

  const sendMessage = useCallback(async (editMessageId?: string): Promise<SendResult> => {
    const store = useMessageStore.getState();
    const rawPayload = store.getPayload();
    const problems = store.getValidationErrors();

    if (problems.length > 0) {
      setSendState({ status: "error", error: problems[0], result: null });
      return { ok: false, error: problems[0] };
    }
    if (isPayloadEmpty(rawPayload)) {
      setSendState({ status: "error", error: "Message is empty", result: null });
      return { ok: false, error: "Message is empty" };
    }

    setSendState({ status: "sending", error: null, result: null });

    try {
      let result: unknown;
      
      // Cleanse the internal V2 flag (32768) which causes Discord to throw Invalid Form Body
      const payload = { ...rawPayload };
      if (payload.flags !== undefined) {
          payload.flags &= ~32768;
          if (payload.flags === 0) delete payload.flags;
      }

      if (sendMode === SEND_MODES.BOT) {
        const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
        const adminKey = import.meta.env.VITE_ADMIN_API_KEY || '';
        const body = {
          mode: "bot",
          payload,
          channelId,
          profileId: botProfileId,
          flows: useActionStore.getState().toRegistrations(),
          editMessageId
        };
        
        // We use direct fetch to guarantee the editMessageId is not stripped by shared types
        const res = await fetch(`${baseUrl}/api/send`, {
            method: "POST",
            headers: { "Content-Type": "application/json", "x-admin-key": adminKey },
            body: JSON.stringify(body)
        });
        
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || data.message || `API Error ${res.status}`);
        result = data;
      } else {
        result = await sendWebhookDirect(webhookUrl, payload, { threadId: threadId || undefined });
      }

      setSendState({ status: "success", error: null, result });
      return { ok: true, result };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setSendState({ status: "error", error: message, result: null });
      return { ok: false, error: message };
    }
  }, [sendMode, webhookUrl, channelId, threadId, botProfileId, setSendState]);

  const isConfigured = sendMode === SEND_MODES.BOT ? channelId.trim() !== "" : webhookUrl.trim() !== "";
  return { sendMessage, isConfigured, mode, sendMode };
};

export default useSend;
```

### File: `client/src/hooks/useTemplates.ts`
```ts
import { useCallback, useEffect } from "react";
import type { TemplateDetailResponse, TemplateSummary } from "../api/client";
import { useActionStore } from "../store/actionStore";
import { useMessageStore } from "../store/messageStore";
import { useTemplateStore } from "../store/templateStore";
import { fromQueryData, toQueryData } from "../utils/exportImport";

/**
 * Bridges the template store, the message store and the action store.
 *
 * Saving needs data from three places, and loading has to write back to all
 * three — keeping that orchestration in a hook means the components stay
 * declarative and the flow only exists once.
 */
export interface UseTemplatesReturn {
  templates: TemplateSummary[];
  currentId: number | null;
  currentName: string;
  dirty: boolean;
  status: "idle" | "loading" | "error";
  error: string | null;
  saveCurrent(): Promise<TemplateDetailResponse["template"]>;
  loadTemplate(id: number): Promise<TemplateDetailResponse["template"] | null>;
  refresh(query?: string): Promise<void>;
}

export const useTemplates = (): UseTemplatesReturn => {
  const templates = useTemplateStore((state) => state.templates);
  const currentId = useTemplateStore((state) => state.currentId);
  const currentName = useTemplateStore((state) => state.currentName);
  const dirty = useTemplateStore((state) => state.dirty);
  const status = useTemplateStore((state) => state.status);
  const error = useTemplateStore((state) => state.error);
  const fetchTemplates = useTemplateStore((state) => state.fetchTemplates);

  useEffect(() => {
    void fetchTemplates();
  }, [fetchTemplates]);

  const saveCurrent = useCallback(async (): Promise<TemplateDetailResponse["template"]> => {
    const { data, targets } = useMessageStore.getState();
    const actions = useActionStore.getState().toList();
    const document = toQueryData({ data, targets });

    return useTemplateStore.getState().save({ data: document, actions });
  }, []);

  const loadTemplate = useCallback(
    async (id: number): Promise<TemplateDetailResponse["template"] | null> => {
      const template = await useTemplateStore.getState().load(id);
      if (!template) return null;

      const restored = fromQueryData(template.data as never);
      useMessageStore.getState().load(restored);
      useActionStore.getState().loadFromList(template.actions ?? []);
      return template;
    },
    [],
  );

  return {
    templates,
    currentId,
    currentName,
    dirty,
    status,
    error,
    saveCurrent,
    loadTemplate,
    refresh: fetchTemplates,
  };
};

export default useTemplates;

```

