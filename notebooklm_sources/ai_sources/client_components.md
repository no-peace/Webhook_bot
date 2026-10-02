# Repository Context Group: client_components
# Source Repository: no-peace/Hoho_manager

### File: `client/src/components/actions/FlowBuilder.tsx`
```tsx
import { useMemo, useState } from "react";
import { AlertTriangle, Wand2 } from "lucide-react";
import type { ComponentNode, FlowStep } from "@dmb/shared";
import { buildCustomId, parseCustomId } from "@dmb/shared";
import { useActionStore } from "../../store/actionStore";
import { useMessageStore } from "../../store/messageStore";
import { StepList } from "./StepList";

/**
 * Flow tab for a button or select.
 *
 * A flow is an ordered list of steps that run top to bottom when the component
 * is clicked — e.g. *add role → check → send DM*. The list is mirrored into two
 * places:
 *
 *   1. The component's `custom_id`, which carries only the **first** step's
 *      params. That keeps ad-hoc webhook sends (where the server is not
 *      involved) working for simple single-step actions.
 *   2. The action store, keyed by `custom_id`, which is saved with a template or
 *      registered with `/api/send` so longer chains can run server-side.
 *
 * `custom_id` is capped at 100 characters, so a long chain can never live
 * entirely in the id — that is exactly why the store exists.
 *
 * Editing itself lives in {@link StepList}, which renders one list and calls
 * itself for a `check` step's `then` / `else` branches. This component owns only
 * the top level, because only the top level changes the `custom_id`.
 */

const cleanedConfig = (config: Record<string, unknown>): Record<string, unknown> =>
  Object.fromEntries(
    Object.entries(config).filter(([, value]) => value !== "" && value !== undefined),
  );

export interface FlowBuilderProps {
  component: ComponentNode;
}

export const FlowBuilder = ({ component }: FlowBuilderProps) => {
  const flows = useActionStore((state) => state.flows);
  const updateComponentById = useMessageStore((state) => state.updateComponentById);
  const [warning, setWarning] = useState<string | null>(null);

  const customId = component.custom_id ?? "";
  const componentId = component._id ?? "";

  // Prefer the stored flow; fall back to whatever the custom_id encodes so an
  // imported message still shows its first step.
  const steps: FlowStep[] = useMemo(() => {
    const stored = flows[customId];
    if (stored && stored.length > 0) return stored;

    const parsed = parseCustomId(customId);
    if (!parsed) return [];
    return [{ _id: "inline", type: parsed.type as FlowStep["type"], config: parsed.params }];
  }, [flows, customId]);

  /**
   * Persist a new step list and keep the component's `custom_id` in step with it.
   * The id is derived from the first step only, both to stay unique per component
   * and to keep the inline fallback meaningful. Branch steps inside a `check` do
   * not affect the id — they always execute server-side.
   */
  const commit = (nextSteps: FlowStep[]): void => {
    const store = useActionStore.getState();
    const first = nextSteps[0];

    let nextCustomId = customId;
    if (first) {
      const config = cleanedConfig(first.config ?? {});
      try {
        nextCustomId = buildCustomId(first.type, config);
        setWarning(null);
      } catch {
        // The params alone overflow 100 chars. Drop them from the id — the full
        // config is still registered server-side, so the flow keeps working. A
        // webhook-only send would lose them, so say so.
        try {
          nextCustomId = buildCustomId(first.type);
        } catch {
          nextCustomId = customId;
        }
        setWarning(
          "This step's settings are too long to fit in the button id, so they only run when the flow is registered (template or bot-token send).",
        );
      }
    } else {
      nextCustomId = "action:dud";
    }

    if (nextCustomId === customId) {
      store.setFlow(customId, nextSteps);
      return;
    }

    // Write under the old key first, then move it, so nothing is dropped.
    store.setFlow(customId, nextSteps);
    store.renameFlow(customId, nextCustomId);
    updateComponentById(componentId, { custom_id: nextCustomId });
  };

  // Branch steps are the only thing that forces server-side execution for this
  // component, so the note below keys off them rather than step count.
  const hasBranches = steps.some((step) => {
    if (step.type !== "check") return false;
    const branchLength = (key: "then" | "else"): number => {
      const value = step.config?.[key];
      return Array.isArray(value) ? value.length : 0;
    };
    return branchLength("then") > 0 || branchLength("else") > 0;
  });

  return (
    <div className="space-y-3">
      <p className="flex items-center gap-1.5 text-[11px] font-semibold text-ink-muted">
        <Wand2 size={12} className="text-blurple" />
        Flow — steps run top to bottom when this is clicked
      </p>

      <StepList steps={steps} onChange={commit} depth={0} />

      <p className="break-all font-mono text-[10px] text-ink-faint">
        custom_id: {customId || "—"} ({customId.length}/100)
      </p>

      {(steps.length > 1 || hasBranches) && (
        <p className="rounded bg-chrome px-2 py-1.5 text-[11px] text-ink-faint">
          Multi-step and branching flows run on the server. Save this as a template, or send it in{" "}
          <span className="text-ink">bot token</span> mode so the steps are registered before the
          message goes out.
        </p>
      )}

      {warning && (
        <p className="flex items-start gap-1.5 rounded bg-warning/10 px-2 py-1.5 text-[11px] text-warning">
          <AlertTriangle size={12} className="mt-0.5 shrink-0" />
          {warning}
        </p>
      )}
    </div>
  );
};

export default FlowBuilder;

```

### File: `client/src/components/actions/StepList.tsx`
```tsx
import { useMemo, useState, type ChangeEvent } from "react";
import {
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  CornerDownRight,
  Plus,
  Trash2,
} from "lucide-react";
import { AdaptiveFields, CheckFunctions, SetVariableModes } from "@dmb/shared";
import type { ActionConfig, CheckCondition, FlowStep } from "@dmb/shared";
import { Button, IconButton } from "../ui/Button";
import { Checkbox, Select, TextArea, TextField } from "../ui/Field";
import { createStep, useActionStore } from "../../store/actionStore";

/**
 * Recursive flow-step editor.
 *
 * A flow is a list of steps, and a `check` step contains **two more lists**
 * (`then` / `else`) in its own config. Rendering that as a flat list would make
 * branching unrepresentable, so this component renders one list and calls itself
 * for each branch. The recursion is the whole point: a check inside a check works
 * without any special case.
 *
 * The nesting is stored in config rather than as sibling rows because the server
 * persists flows to a flat, ordered `action_definitions` table — a tree cannot be
 * expressed by `execution_order` alone. See `server/src/services/branches.ts`.
 */

interface ConfigField {
  key: string;
  label: string;
  placeholder?: string;
  textarea?: boolean;
  type?: string;
}

/**
 * Field descriptors per action type. Keys are the same config keys the server
 * handlers read (`roleId`, `content`, …), so no translation layer is needed.
 *
 * `check` and `set_variable` are absent here on purpose: they need purpose-built
 * controls (a function picker, a mode picker, and for `check`, the branch lists)
 * and are rendered by the switch below. `stop` is a plain field.
 */
const CONFIG_FIELDS: Record<string, readonly ConfigField[]> = {
  dud: [],
  add_role: [{ key: "roleId", label: "Role ID", placeholder: "123456789012345678" }],
  remove_role: [{ key: "roleId", label: "Role ID", placeholder: "123456789012345678" }],
  toggle_role: [{ key: "roleId", label: "Role ID", placeholder: "123456789012345678" }],
  send_ephemeral_reply: [{ key: "content", label: "Reply text", textarea: true }],
  send_dm: [{ key: "content", label: "DM text", textarea: true }],
  open_modal: [
    { key: "title", label: "Modal title", placeholder: "Tell us about you" },
    { key: "customId", label: "Modal custom id", placeholder: "modal:about" },
  ],
  send_message: [
    { key: "channelId", label: "Channel ID (defaults to here)", placeholder: "123456789012345678" },
    { key: "content", label: "Message", textarea: true },
  ],
  send_webhook_message: [
    { key: "webhookProfileId", label: "Webhook profile ID", placeholder: "1" },
    { key: "content", label: "Message", textarea: true },
  ],
  delete_message: [],
  create_thread: [{ key: "name", label: "Thread name", placeholder: "Support ticket" }],
  wait: [{ key: "seconds", label: "Seconds", placeholder: "1", type: "number" }],
  stop: [
    {
      key: "content",
      label: "Message (optional)",
      textarea: true,
      placeholder: "Leave empty to acknowledge the click silently",
    },
  ],
};

const CHECK_KEY = "check";
const SET_VARIABLE_KEY = "set_variable";

/** Past this the server refuses to recurse (`MAX_BRANCH_DEPTH`), so warn first. */
const WARN_DEPTH = 8;

const labelFor = (type: string): string => type.replace(/_/g, " ");

const asText = (value: unknown): string =>
  typeof value === "string" ? value : value == null ? "" : String(value);

/** Read a `check` step's conditions, normalised so the UI never sees `undefined`. */
const readConditions = (config: ActionConfig): CheckCondition[] => {
  if (!Array.isArray(config.conditions)) return [];

  const parsed = config.conditions.flatMap((entry) => {
    if (entry === null || typeof entry !== "object") return [];
    const record = entry as Record<string, unknown>;
    return [{ a: record.a, b: record.b, loose: record.loose === true }];
  });

  return parsed.length > 0 ? parsed : [{ a: "", b: "", loose: false }];
};

/** Read a branch array out of a config, tolerating hand-edited JSON. */
const readBranch = (config: ActionConfig, key: "then" | "else"): FlowStep[] => {
  const value = config[key];
  if (!Array.isArray(value)) return [];

  return value.flatMap((entry) => {
    if (entry === null || typeof entry !== "object") return [];
    const record = entry as Record<string, unknown>;
    return [{ type: (record.type as FlowStep["type"]) ?? "dud", config: (record.config ?? {}) as ActionConfig }];
  });
};

export interface StepListProps {
  steps: FlowStep[];
  /** Receives the complete, edited list. */
  onChange: (steps: FlowStep[]) => void;
  /** 0 for the component's own flow; >0 inside a check branch. */
  depth: number;
}

export const StepList = ({ steps, onChange, depth }: StepListProps) => {
  const [addingType, setAddingType] = useState<string>("add_role");
  const nested = depth > 0;

  // Driven by `GET /api/config` (falling back to a bundled copy) so the picker
  // cannot drift from the server's action registry. `dud` is hidden — it exists
  // for the inline custom-id case, not as something to choose deliberately.
  const actionTypes = useActionStore((state) => state.actionTypes);
  const typeOptions = useMemo(
    () =>
      actionTypes
        .filter((action) => action.type !== "dud")
        .map((action) => ({ value: action.type, label: action.type.replace(/_/g, " ") })),
    [actionTypes],
  );

  const patch = (index: number, next: FlowStep): void => {
    onChange(steps.map((step, i) => (i === index ? next : step)));
  };

  const patchConfig = (index: number, config: ActionConfig): void => {
    const step = steps[index];
    if (!step) return;
    patch(index, { ...step, config });
  };

  const move = (index: number, direction: number): void => {
    const target = index + direction;
    if (target < 0 || target >= steps.length) return;
    const next = [...steps];
    const a = next[index];
    const b = next[target];
    if (!a || !b) return;
    next[index] = b;
    next[target] = a;
    onChange(next);
  };

  const remove = (index: number): void => {
    onChange(steps.filter((_, i) => i !== index));
  };

  const changeType = (index: number, type: string): void => {
    const step = steps[index];
    if (!step) return;
    // Keep the editor `_id` so React does not remount the card mid-edit.
    patch(index, { ...createStep(type as FlowStep["type"]), _id: step._id });
  };

  const renderFields = (index: number, step: FlowStep) => {
    const config = step.config ?? {};

    if (step.type === SET_VARIABLE_KEY) {
      const mode = asText(config.varType) || "static";

      return (
        <>
          <TextField
            label="Variable name"
            value={asText(config.name)}
            placeholder="userId"
            onChange={(event) => patchConfig(index, { ...config, name: event.target.value })}
          />
          <Select
            label="Value source"
            value={mode}
            onChange={(event) => patchConfig(index, { ...config, varType: event.target.value })}
            options={SetVariableModes.map((entry) => ({ value: entry.value, label: entry.label }))}
          />
          {mode === "adaptive" ? (
            <Select
              label="Reading"
              value={asText(config.value)}
              onChange={(event) => patchConfig(index, { ...config, value: event.target.value })}
              options={[
                { value: "", label: "Choose a field…" },
                ...AdaptiveFields.map((field) => ({ value: field, label: field })),
              ]}
            />
          ) : (
            <TextField
              label={mode === "get" ? "Variable to copy" : "Value"}
              value={asText(config.value)}
              placeholder={mode === "get" ? "userId" : "member"}
              onChange={(event) => patchConfig(index, { ...config, value: event.target.value })}
            />
          )}
        </>
      );
    }

    if (step.type === CHECK_KEY) {
      const conditions = readConditions(config);
      const fn = asText(config.function) || "equals";

      const writeConditions = (next: CheckCondition[]): void =>
        patchConfig(index, { ...config, conditions: next });

      return (
        <>
          <Select
            label="Condition"
            value={fn}
            onChange={(event) => patchConfig(index, { ...config, function: event.target.value })}
            options={CheckFunctions.map((entry) => ({ value: entry.value, label: entry.label }))}
          />

          <div className="space-y-2">
            {conditions.map((condition, conditionIndex) => (
              <div
                key={conditionIndex}
                className="space-y-2 rounded-md border border-line-soft bg-raised/40 p-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-semibold uppercase tracking-wide text-ink-faint">
                    {conditions.length > 1 ? `Condition ${conditionIndex + 1}` : "Comparison"}
                  </span>
                  {conditions.length > 1 && (
                    <IconButton
                      icon={Trash2}
                      label="Remove condition"
                      size={11}
                      onClick={() =>
                        writeConditions(conditions.filter((_, i) => i !== conditionIndex))
                      }
                    />
                  )}
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <TextField
                    label="Left"
                    value={asText(condition.a)}
                    placeholder="{{role}}"
                    onChange={(event) =>
                      writeConditions(
                        conditions.map((entry, i) =>
                          i === conditionIndex ? { ...entry, a: event.target.value } : entry,
                        ),
                      )
                    }
                  />
                  <TextField
                    label={fn === "in" ? "In list" : "Right"}
                    value={asText(condition.b)}
                    placeholder={fn === "in" ? "a,b,c" : "member"}
                    onChange={(event) =>
                      writeConditions(
                        conditions.map((entry, i) =>
                          i === conditionIndex ? { ...entry, b: event.target.value } : entry,
                        ),
                      )
                    }
                  />
                </div>

                <Checkbox
                  label="Loose comparison (==)"
                  checked={condition.loose === true}
                  onChange={(loose) =>
                    writeConditions(
                      conditions.map((entry, i) =>
                        i === conditionIndex ? { ...entry, loose } : entry,
                      ),
                    )
                  }
                />
              </div>
            ))}

            <Button
              size="sm"
              variant="outline"
              icon={Plus}
              onClick={() => writeConditions([...conditions, { a: "", b: "", loose: false }])}
            >
              Add condition
            </Button>
          </div>
        </>
      );
    }

    const fields = CONFIG_FIELDS[step.type] ?? [];

    return (
      <>
        {fields.map((field) => {
          const value = asText(config[field.key]);

          return field.textarea ? (
            <TextArea
              key={field.key}
              label={field.label}
              rows={3}
              value={value}
              placeholder={field.placeholder}
              onChange={(event: ChangeEvent<HTMLTextAreaElement>) =>
                patchConfig(index, { ...config, [field.key]: event.target.value })
              }
            />
          ) : (
            <TextField
              key={field.key}
              label={field.label}
              type={field.type ?? "text"}
              value={value}
              placeholder={field.placeholder}
              onChange={(event: ChangeEvent<HTMLInputElement>) =>
                patchConfig(index, { ...config, [field.key]: event.target.value })
              }
            />
          );
        })}
      </>
    );
  };

  return (
    <div className={nested ? "space-y-2" : "space-y-2.5"}>
      {depth > WARN_DEPTH && (
        <p className="flex items-start gap-1.5 rounded bg-warning/10 px-2 py-1.5 text-[11px] text-warning">
          <AlertTriangle size={12} className="mt-0.5 shrink-0" />
          Branches this deep may stop running — the server refuses to recurse past 10 levels.
        </p>
      )}

      {steps.length === 0 ? (
        <p
          className={`rounded-lg border border-dashed border-line px-3 text-center text-[11px] text-ink-faint ${
            nested ? "py-2" : "py-4"
          }`}
        >
          {nested ? "No steps in this branch — it runs nothing." : "No steps yet."}
        </p>
      ) : (
        <ol className={nested ? "space-y-2" : "space-y-2.5"}>
          {steps.map((step, index) => (
            <li
              key={step._id ?? `${depth}-${index}`}
              className="rounded-lg border border-line-soft bg-chrome"
            >
              <div className="flex items-center gap-1 border-b border-line-soft px-2 py-1.5">
                {nested && <CornerDownRight size={11} className="shrink-0 text-ink-faint" />}
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded bg-blurple/20 text-[10px] font-bold text-blurple-300">
                  {index + 1}
                </span>
                <span className="truncate text-[11px] font-semibold text-ink">
                  {labelFor(step.type)}
                </span>

                <span className="ml-auto flex items-center">
                  <IconButton
                    icon={ChevronUp}
                    label="Move step up"
                    size={12}
                    disabled={index === 0}
                    onClick={() => move(index, -1)}
                  />
                  <IconButton
                    icon={ChevronDown}
                    label="Move step down"
                    size={12}
                    disabled={index === steps.length - 1}
                    onClick={() => move(index, 1)}
                  />
                  <IconButton
                    icon={Trash2}
                    label="Remove step"
                    size={12}
                    onClick={() => remove(index)}
                  />
                </span>
              </div>

              <div className="space-y-2.5 p-2.5">
                <Select
                  label="Action"
                  value={step.type}
                  onChange={(event) => changeType(index, event.target.value)}
                  options={typeOptions}
                />

                {renderFields(index, step)}

                {step.type === CHECK_KEY && (
                  <div className="space-y-2 pt-1">
                    <BranchEditor
                      label="Then — condition passed"
                      steps={readBranch(step.config ?? {}, "then")}
                      depth={depth + 1}
                      onChange={(branch) =>
                        patchConfig(index, { ...(step.config ?? {}), then: branch })
                      }
                    />
                    <BranchEditor
                      label="Else — condition failed"
                      steps={readBranch(step.config ?? {}, "else")}
                      depth={depth + 1}
                      onChange={(branch) =>
                        patchConfig(index, { ...(step.config ?? {}), else: branch })
                      }
                    />
                  </div>
                )}
              </div>
            </li>
          ))}
        </ol>
      )}

      <div className="flex items-end gap-2">
        <Select
          className="flex-1"
          label={nested ? "Add to this branch" : "Add a step"}
          value={addingType}
          onChange={(event) => setAddingType(event.target.value)}
          options={typeOptions}
        />
        <Button
          size="sm"
          icon={Plus}
          onClick={() => onChange([...steps, createStep(addingType as FlowStep["type"])])}
        >
          Add
        </Button>
      </div>
    </div>
  );
};

/** A labelled, collapsible sub-list. Thin wrapper so the two branches look alike. */
const BranchEditor = ({
  label,
  steps,
  depth,
  onChange,
}: {
  label: string;
  steps: FlowStep[];
  depth: number;
  onChange: (steps: FlowStep[]) => void;
}) => {
  const [open, setOpen] = useState(true);

  return (
    <div className="rounded-md border border-line-soft bg-raised/30">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center gap-1 px-2 py-1.5 text-left text-[10px] font-semibold uppercase tracking-wide text-ink-muted transition-colors hover:text-ink"
      >
        {open ? <ChevronDown size={11} /> : <ChevronUp size={11} />}
        {label}
        <span className="ml-auto font-normal normal-case text-ink-faint">
          {steps.length} step{steps.length === 1 ? "" : "s"}
        </span>
      </button>

      {open && (
        <div className="border-t border-line-soft p-2">
          <StepList steps={steps} onChange={onChange} depth={depth} />
        </div>
      )}
    </div>
  );
};

export default StepList;

```

### File: `client/src/components/editor/ComponentForms.tsx`
```tsx
import { Plus, Trash2 } from "lucide-react";
// Aliased because `ComponentType` below is Discord's numeric component enum.
import type { ComponentType as ReactComponentType } from "react";
import type { ComponentNode, GalleryItem, SelectOption } from "@dmb/shared";
import { ButtonStyle, ComponentType, Limits } from "@dmb/shared";
import { Button, IconButton } from "../ui/Button";
import { Checkbox, Select, TextArea, TextField } from "../ui/Field";
import { ColorPicker } from "../ui/ColorPicker";
import { BUTTON_STYLE_LABELS, uid } from "../../utils/constants";
import { newGalleryItem } from "../../utils/componentsV2";

/**
 * Property forms, one per component type.
 *
 * `COMPONENT_FORMS` maps a Discord component type to the form that edits it, so
 * the property panel is a single lookup rather than a long conditional. Every
 * form edits through an `update` callback the panel supplies, which routes to
 * `updateComponentById` and walks the tree by `_id`.
 */

export interface ComponentFormProps {
  component: ComponentNode;
  update: (patch: Partial<ComponentNode>) => void;
}

/* ── Content ──────────────────────────────────────────────────────────────── */

const TextDisplayForm = ({ component, update }: ComponentFormProps) => (
  <TextArea
    label="Content"
    limit={Limits.components.textDisplay}
    rows={5}
    value={component.content ?? ""}
    placeholder="**Bold**, *italic*, # heading, - lists — markdown is supported."
    onChange={(event) => update({ content: event.target.value })}
  />
);

const SectionForm = ({ component, update }: ComponentFormProps) => (
  <>
    <TextField
      label="Thumbnail URL"
      value={component.accessory?.media?.url ?? ""}
      placeholder="https://…"
      onChange={(event) =>
        update({
          // Rebuilt rather than spread, so the accessory always keeps a `type`
          // even when the section was imported without one.
          accessory: {
            _id: component.accessory?._id ?? uid(),
            type: component.accessory?.type ?? ComponentType.Thumbnail,
            media: { url: event.target.value },
          },
        })
      }
    />
    <p className="rounded bg-chrome px-2 py-1.5 text-[11px] text-ink-faint">
      Section text is edited in the component tree on the left. A section holds up to three
      text displays plus one accessory.
    </p>
  </>
);

const MediaGalleryForm = ({ component, update }: ComponentFormProps) => {
  const items = component.items ?? [];

  const replaceItem = (index: number, patch: Partial<GalleryItem>): void => {
    const next = [...items];
    const existing = next[index];
    if (!existing) return;
    next[index] = { ...existing, ...patch };
    update({ items: next });
  };

  return (
    <>
      <div className="mb-1.5 flex items-center justify-between">
        <span className="field-label !mb-0">Gallery items</span>
        <Button
          size="sm"
          variant="ghost"
          icon={Plus}
          onClick={() => update({ items: [...items, newGalleryItem()] })}
        >
          Add
        </Button>
      </div>

      {items.length === 0 && (
        <p className="text-[11px] text-ink-faint">No images yet. Add one to start the gallery.</p>
      )}

      <div className="space-y-2">
        {items.map((item, index) => (
          <div key={item._id} className="flex items-end gap-2">
            <TextField
              className="flex-1"
              label={`Image ${index + 1}`}
              value={item.media.url}
              placeholder="https://…"
              onChange={(event) => replaceItem(index, { media: { url: event.target.value } })}
            />
            <IconButton
              icon={Trash2}
              label="Remove item"
              onClick={() => update({ items: items.filter((entry) => entry._id !== item._id) })}
            />
          </div>
        ))}
      </div>
    </>
  );
};

const FileForm = ({ component, update }: ComponentFormProps) => (
  <TextField
    label="File URL"
    value={component.file?.url ?? ""}
    placeholder="attachment://image.png or https://…"
    onChange={(event) => update({ file: { url: event.target.value } })}
  />
);

/* ── Layout ───────────────────────────────────────────────────────────────── */

const ContainerForm = ({ component, update }: ComponentFormProps) => (
  <>
    <ColorPicker
      label="Accent colour"
      value={component.accent_color ?? null}
      onChange={(accent_color) => update({ accent_color })}
    />
    <p className="rounded bg-chrome px-2 py-1.5 text-[11px] text-ink-faint">
      {component.components?.length ?? 0} child component(s). Use the palette on the left to add
      more while this container is selected.
    </p>
  </>
);

const SeparatorForm = ({ component, update }: ComponentFormProps) => (
  <>
    <Checkbox
      label="Show divider line"
      checked={component.divider !== false}
      onChange={(divider) => update({ divider })}
    />
    <Select
      label="Spacing"
      value={String(component.spacing ?? 1)}
      onChange={(event) => update({ spacing: Number(event.target.value) })}
      options={[
        { value: "1", label: "Small" },
        { value: "2", label: "Large" },
      ]}
    />
  </>
);

const ActionRowForm = ({ component }: ComponentFormProps) => (
  <p className="rounded bg-chrome px-2 py-1.5 text-[11px] text-ink-faint">
    {component.components?.length ?? 0} control(s). An action row holds up to{" "}
    {Limits.components.actionRowButtons} buttons, or a single select menu.
  </p>
);

/* ── Interactive ──────────────────────────────────────────────────────────── */

const ButtonForm = ({ component, update }: ComponentFormProps) => {
  const isLink = component.style === ButtonStyle.Link;

  return (
    <>
      <TextField
        label="Label"
        limit={Limits.components.label}
        value={component.label ?? ""}
        onChange={(event) => update({ label: event.target.value })}
      />

      <Select
        label="Style"
        value={String(component.style ?? ButtonStyle.Primary)}
        onChange={(event) => update({ style: Number(event.target.value) })}
        options={Object.entries(BUTTON_STYLE_LABELS).map(([value, label]) => ({ value, label }))}
      />

      {isLink ? (
        <TextField
          label="URL"
          value={component.url ?? ""}
          placeholder="https://discord.com"
          onChange={(event) => update({ url: event.target.value })}
        />
      ) : (
        <p className="rounded bg-chrome px-2 py-1.5 text-[11px] text-ink-faint">
          What this button does is configured on the <span className="text-ink">Flow</span> tab
          above.
        </p>
      )}

      <Checkbox
        label="Disabled"
        checked={Boolean(component.disabled)}
        onChange={(disabled) => update({ disabled })}
      />
    </>
  );
};

const StringSelectForm = ({ component, update }: ComponentFormProps) => {
  const options = component.options ?? [];

  const replaceOption = (index: number, patch: Partial<SelectOption>): void => {
    const next = [...options];
    const existing = next[index];
    if (!existing) return;
    next[index] = { ...existing, ...patch };
    update({ options: next });
  };

  return (
    <>
      <TextField
        label="Placeholder"
        limit={Limits.components.placeholder}
        value={component.placeholder ?? ""}
        onChange={(event) => update({ placeholder: event.target.value })}
      />

      <div className="mb-1.5 flex items-center justify-between">
        <span className="field-label !mb-0">Options</span>
        <Button
          size="sm"
          variant="ghost"
          icon={Plus}
          onClick={() =>
            update({
              options: [
                ...options,
                { _id: uid(), label: "Option", value: `option_${options.length + 1}` },
              ],
            })
          }
        >
          Add
        </Button>
      </div>

      <div className="space-y-2">
        {options.map((option, index) => (
          <div key={option._id} className="flex items-end gap-2">
            <TextField
              className="flex-1"
              label={`Option ${index + 1}`}
              value={option.label}
              onChange={(event) => replaceOption(index, { label: event.target.value })}
            />
            <IconButton
              icon={Trash2}
              label="Remove option"
              onClick={() => update({ options: options.filter((entry) => entry._id !== option._id) })}
            />
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-2">
        <TextField
          label="Min values"
          type="number"
          min={0}
          value={component.min_values ?? 1}
          onChange={(event) => update({ min_values: Number(event.target.value) })}
        />
        <TextField
          label="Max values"
          type="number"
          min={1}
          value={component.max_values ?? 1}
          onChange={(event) => update({ max_values: Number(event.target.value) })}
        />
      </div>

      <p className="rounded bg-chrome px-2 py-1.5 text-[11px] text-ink-faint">
        What this select does is configured on the <span className="text-ink">Flow</span> tab
        above.
      </p>
    </>
  );
};

/**
 * Selection menus share one form: the placeholder/action fields are identical,
 * and the option list only applies to string selects.
 */
export const COMPONENT_FORMS: Record<number, ReactComponentType<ComponentFormProps>> = {
  [ComponentType.TextDisplay]: TextDisplayForm,
  [ComponentType.Section]: SectionForm,
  [ComponentType.MediaGallery]: MediaGalleryForm,
  [ComponentType.File]: FileForm,
  [ComponentType.Container]: ContainerForm,
  [ComponentType.Separator]: SeparatorForm,
  [ComponentType.ActionRow]: ActionRowForm,
  [ComponentType.Button]: ButtonForm,
  [ComponentType.StringSelect]: StringSelectForm,
  [ComponentType.UserSelect]: StringSelectForm,
  [ComponentType.RoleSelect]: StringSelectForm,
  [ComponentType.MentionableSelect]: StringSelectForm,
  [ComponentType.ChannelSelect]: StringSelectForm,
};

export default COMPONENT_FORMS;

```

### File: `client/src/components/editor/ComponentPalette.tsx`
```tsx
import {
  AlignLeft,
  AppWindow,
  Image as ImageIcon,
  LayoutGrid,
  Minus,
  MousePointerClick,
  Paperclip,
} from "lucide-react";
import { ComponentType } from "@dmb/shared";
import { COMPONENT_DEFS, canNestIn, type ComponentGroup } from "../../utils/componentsV2";
import { findComponent } from "../../utils/tree";
import { useMessageStore } from "../../store/messageStore";
import type { IconComponent } from "../ui/icon";

/**
 * Palette of Components V2 blocks.
 *
 * Insertion is selection-aware: if the selected component is a valid parent (a
 * Container or ActionRow) the new component nests inside it, which is how users
 * expect an editor to behave. Incompatible types are disabled rather than hidden,
 * so the layout doesn't jump around while clicking.
 */

const ICONS: Record<number, IconComponent> = {
  [ComponentType.TextDisplay]: AlignLeft,
  [ComponentType.Section]: LayoutGrid,
  [ComponentType.MediaGallery]: ImageIcon,
  [ComponentType.File]: Paperclip,
  [ComponentType.Separator]: Minus,
  [ComponentType.Container]: AppWindow,
  [ComponentType.ActionRow]: MousePointerClick,
};

export const ComponentPalette = () => {
  const addComponent = useMessageStore((state) => state.addComponent);
  const selection = useMessageStore((state) => state.selection);
  const components = useMessageStore((state) => state.data.components);

  // Only a component selection can act as a nesting target.
  const selected =
    selection?.kind === "component" ? findComponent(components, selection.id) : null;

  const groups = COMPONENT_DEFS.reduce<Record<string, typeof COMPONENT_DEFS[number][]>>(
    (accumulator, def) => {
      (accumulator[def.group] ??= []).push(def);
      return accumulator;
    },
    {},
  );

  return (
    <div className="space-y-4">
      {selected && (
        <p className="rounded-md bg-raised px-2 py-1.5 text-[11px] text-ink-muted">
          Adding inside{" "}
          <span className="text-ink">
            {selected.type === ComponentType.ActionRow ? "Action Row" : "Container"}
          </span>
          . Select nothing to add at the top level.
        </p>
      )}

      {(Object.entries(groups) as [ComponentGroup, typeof COMPONENT_DEFS[number][]][]).map(
        ([group, defs]) => (
          <section key={group}>
            <h3 className="field-label">{group}</h3>
            <div className="space-y-1.5">
              {defs.map((def) => {
                const Icon = ICONS[def.type];
                const nests = selected ? canNestIn(selected.type, def.type) : false;
                const disabled = Boolean(selected) && !nests;

                return (
                  <button
                    key={def.type}
                    type="button"
                    disabled={disabled}
                    onClick={() => addComponent(def.type, nests ? (selected?._id ?? null) : null)}
                    className={[
                      "flex w-full items-start gap-2.5 rounded-lg border px-2.5 py-2 text-left transition-colors",
                      disabled
                        ? "cursor-not-allowed border-line-soft/50 opacity-40"
                        : "border-line-soft bg-raised hover:border-blurple hover:bg-hover",
                    ].join(" ")}
                  >
                    {Icon && <Icon size={15} className="mt-0.5 shrink-0 text-blurple" />}
                    <span className="min-w-0">
                      <span className="block text-xs font-semibold text-ink">{def.label}</span>
                      <span className="block text-[11px] leading-snug text-ink-muted">
                        {def.description}
                      </span>
                    </span>
                  </button>
                );
              })}
            </div>
          </section>
        ),
      )}
    </div>
  );
};

export default ComponentPalette;

```

### File: `client/src/components/editor/EmbedEditor.tsx`
```tsx
import { useState } from "react";
import { ChevronDown, ChevronRight, Copy, Plus, Trash2 } from "lucide-react";
import type { EmbedData } from "@dmb/shared";
import { Limits } from "@dmb/shared";
import { Button, IconButton } from "../ui/Button";
import { Checkbox, TextArea, TextField } from "../ui/Field";
import { ColorPicker } from "../ui/ColorPicker";
import { embedCharCount } from "../../utils/discord";
import { useMessageStore } from "../../store/messageStore";

/**
 * Editor for one classic embed.
 *
 * Collapsed by default so a message with several embeds stays scannable, and
 * expanded automatically when it is the selected embed. The character counter
 * uses Discord's real aggregate limit (6000 across the whole embed), which is the
 * constraint people actually hit.
 */
export interface EmbedEditorProps {
  embed: EmbedData;
  index: number;
}

export const EmbedEditor = ({ embed, index }: EmbedEditorProps) => {
  const updateEmbed = useMessageStore((state) => state.updateEmbed);
  const removeEmbed = useMessageStore((state) => state.removeEmbed);
  const duplicateEmbed = useMessageStore((state) => state.duplicateEmbed);
  const moveEmbed = useMessageStore((state) => state.moveEmbed);
  const addEmbedField = useMessageStore((state) => state.addEmbedField);
  const updateEmbedField = useMessageStore((state) => state.updateEmbedField);
  const removeEmbedField = useMessageStore((state) => state.removeEmbedField);
  const selection = useMessageStore((state) => state.selection);
  const select = useMessageStore((state) => state.select);

  const [open, setOpen] = useState(true);
  const id = embed._id ?? "";
  const active = selection?.kind === "embed" && selection.id === id;
  const used = embedCharCount(embed);

  return (
    <div className={`panel ${active ? "border-blurple" : ""}`}>
      <div
        className="panel-header cursor-pointer"
        onClick={() => select({ kind: "embed", id })}
      >
        <div className="flex items-center gap-1.5">
          <IconButton
            icon={open ? ChevronDown : ChevronRight}
            label={open ? "Collapse" : "Expand"}
            onClick={(event) => {
              event.stopPropagation();
              setOpen((value) => !value);
            }}
          />
          <span className="text-xs font-semibold text-ink">
            Embed {index + 1}
            {embed.title ? ` — ${embed.title}` : ""}
          </span>
        </div>

        <div className="flex items-center gap-0.5">
          <span
            className={`mr-1 text-[11px] tabular-nums ${
              used > Limits.embed.total ? "text-danger" : "text-ink-faint"
            }`}
          >
            {used}/{Limits.embed.total}
          </span>
          <IconButton
            icon={Copy}
            label="Duplicate embed"
            size={13}
            onClick={(event) => {
              event.stopPropagation();
              duplicateEmbed(id);
            }}
          />
          <IconButton
            icon={Trash2}
            label="Delete embed"
            size={13}
            onClick={(event) => {
              event.stopPropagation();
              removeEmbed(id);
            }}
          />
        </div>
      </div>

      {open && (
        <div className="space-y-3 p-3">
          <TextField
            label="Title"
            limit={Limits.embed.title}
            value={embed.title ?? ""}
            placeholder="Announcement"
            onChange={(event) => updateEmbed(id, { title: event.target.value })}
          />

          <TextField
            label="Title URL"
            value={embed.url ?? ""}
            placeholder="https://example.com"
            onChange={(event) => updateEmbed(id, { url: event.target.value })}
          />

          <TextArea
            label="Description"
            limit={Limits.embed.description}
            rows={4}
            value={embed.description ?? ""}
            placeholder="Markdown is supported **here**."
            onChange={(event) => updateEmbed(id, { description: event.target.value })}
          />

          <ColorPicker
            value={embed.color ?? null}
            onChange={(color) => updateEmbed(id, { color })}
          />

          {/* Fields */}
          <div>
            <div className="mb-1.5 flex items-center justify-between">
              <span className="field-label !mb-0">Fields</span>
              <Button size="sm" variant="ghost" icon={Plus} onClick={() => addEmbedField(id)}>
                Add field
              </Button>
            </div>

            <div className="space-y-2">
              {(embed.fields ?? []).map((field) => (
                <div key={field._id} className="rounded border border-line-soft p-2">
                  <div className="flex items-start gap-2">
                    <div className="min-w-0 flex-1 space-y-2">
                      <TextField
                        label="Name"
                        limit={Limits.embed.fieldName}
                        value={field.name}
                        onChange={(event) =>
                          updateEmbedField(id, field._id ?? "", { name: event.target.value })
                        }
                      />
                      <TextArea
                        label="Value"
                        limit={Limits.embed.fieldValue}
                        rows={2}
                        value={field.value}
                        onChange={(event) =>
                          updateEmbedField(id, field._id ?? "", { value: event.target.value })
                        }
                      />
                    </div>
                    <IconButton
                      icon={Trash2}
                      label="Remove field"
                      size={13}
                      onClick={() => removeEmbedField(id, field._id ?? "")}
                    />
                  </div>
                  <Checkbox
                    className="mt-2"
                    label="Inline"
                    checked={field.inline}
                    onChange={(inline) => updateEmbedField(id, field._id ?? "", { inline })}
                  />
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <TextField
              label="Author name"
              limit={Limits.embed.authorName}
              value={embed.author?.name ?? ""}
              onChange={(event) =>
                updateEmbed(id, { author: { ...embed.author, name: event.target.value } })
              }
            />
            <TextField
              label="Author icon URL"
              value={embed.author?.icon_url ?? ""}
              onChange={(event) =>
                updateEmbed(id, { author: { ...embed.author, icon_url: event.target.value } })
              }
            />
          </div>

          <TextField
            label="Footer text"
            limit={Limits.embed.footerText}
            value={embed.footer?.text ?? ""}
            onChange={(event) =>
              updateEmbed(id, { footer: { ...embed.footer, text: event.target.value } })
            }
          />

          <div className="grid grid-cols-2 gap-2">
            <TextField
              label="Image URL"
              value={embed.image?.url ?? ""}
              onChange={(event) => updateEmbed(id, { image: { url: event.target.value } })}
            />
            <TextField
              label="Thumbnail URL"
              value={embed.thumbnail?.url ?? ""}
              onChange={(event) => updateEmbed(id, { thumbnail: { url: event.target.value } })}
            />
          </div>

          <div className="flex items-center justify-between">
            <Checkbox
              label="Timestamp"
              checked={Boolean(embed.timestamp)}
              onChange={(checked) =>
                updateEmbed(id, { timestamp: checked ? new Date().toISOString() : null })
              }
            />
            <div className="flex gap-1">
              <IconButton
                icon={ChevronRight}
                label="Move up"
                size={13}
                onClick={() => moveEmbed(id, -1)}
              />
              <IconButton
                icon={ChevronDown}
                label="Move down"
                size={13}
                onClick={() => moveEmbed(id, 1)}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmbedEditor;

```

### File: `client/src/components/editor/LayersPanel.tsx`
```tsx
import { ChevronDown, ChevronUp, Copy, Trash2 } from "lucide-react";
import type { ComponentNode } from "@dmb/shared";
import { IconButton } from "../ui/Button";
import { componentLabel } from "../../utils/componentsV2";
import { useMessageStore } from "../../store/messageStore";

/**
 * The component tree.
 *
 * Rendering is recursive so any nesting depth works, and each row edits by `_id`
 * rather than index — reordering is therefore safe. Nested rows are visually
 * indented, mirroring how the structure reads in the preview.
 */

interface LayerRowProps {
  component: ComponentNode;
  depth: number;
  parentId: string | null;
}

const LayerRow = ({ component, depth, parentId }: LayerRowProps) => {
  const selection = useMessageStore((state) => state.selection);
  const select = useMessageStore((state) => state.select);
  const moveComponent = useMessageStore((state) => state.moveComponentById);
  const removeComponent = useMessageStore((state) => state.removeComponentById);
  const duplicateComponent = useMessageStore((state) => state.duplicateComponentById);

  const active = selection?.kind === "component" && selection.id === component._id;
  const children = component.components ?? [];

  return (
    <>
      <div
        role="treeitem"
        aria-selected={active}
        aria-level={depth + 1}
        onClick={() => component._id && select({ kind: "component", id: component._id })}
        className={[
          "group flex cursor-pointer items-center gap-1 rounded px-2 py-1.5 text-xs transition-colors",
          active ? "bg-blurple/20 text-ink-strong" : "text-ink-muted hover:bg-hover hover:text-ink",
        ].join(" ")}
        style={{ marginLeft: depth * 12 }}
      >
        <span className="truncate">{componentLabel(component)}</span>

        {/* Row actions stay hidden until hover to keep the list calm. */}
        <span className="ml-auto flex items-center opacity-0 transition-opacity group-hover:opacity-100">
          <IconButton
            icon={ChevronUp}
            label="Move up"
            size={12}
            onClick={(event) => {
              event.stopPropagation();
              if (component._id) moveComponent(component._id, -1, parentId);
            }}
          />
          <IconButton
            icon={ChevronDown}
            label="Move down"
            size={12}
            onClick={(event) => {
              event.stopPropagation();
              if (component._id) moveComponent(component._id, 1, parentId);
            }}
          />
          <IconButton
            icon={Copy}
            label="Duplicate"
            size={12}
            onClick={(event) => {
              event.stopPropagation();
              if (component._id) duplicateComponent(component._id);
            }}
          />
          <IconButton
            icon={Trash2}
            label="Delete"
            size={12}
            onClick={(event) => {
              event.stopPropagation();
              if (component._id) removeComponent(component._id);
            }}
          />
        </span>
      </div>

      {children.map((child) => (
        <LayerRow
          key={child._id}
          component={child}
          depth={depth + 1}
          parentId={component._id ?? null}
        />
      ))}
    </>
  );
};

export const LayersPanel = () => {
  const components = useMessageStore((state) => state.data.components);

  if (components.length === 0) {
    return (
      <p className="rounded border border-dashed border-line px-2.5 py-3 text-[11px] text-ink-faint">
        No components yet. Add one from the palette above.
      </p>
    );
  }

  return (
    <div role="tree" aria-label="Message components">
      {components.map((component) => (
        <LayerRow key={component._id} component={component} depth={0} parentId={null} />
      ))}
    </div>
  );
};

export default LayersPanel;

```

### File: `client/src/components/editor/MessageEditor.tsx`
```tsx
import { AlertTriangle, Hash, Image as ImageIcon, Plus, User } from "lucide-react";
import { Limits } from "@dmb/shared";
import { Button } from "../ui/Button";
import { TextArea, TextField } from "../ui/Field";
import { EmbedEditor } from "./EmbedEditor";
import { useMessage } from "../../hooks/useMessage";
import { EDITOR_MODES } from "../../utils/constants";
import { useMessageStore } from "../../store/messageStore";

/**
 * The editor column.
 *
 * Classic mode edits `content` + `embeds`; Components V2 mode replaces both with
 * a component tree, so the content/embed editors are hidden rather than silently
 * ignored. Identity overrides (username, avatar, thread name) apply to both modes
 * and live at the top.
 */
export const MessageEditor = () => {
  const { mode, data, problems } = useMessage();
  const setField = useMessageStore((state) => state.setField);
  const addEmbed = useMessageStore((state) => state.addEmbed);

  const isClassic = mode === EDITOR_MODES.CLASSIC;

  return (
    <div className="space-y-4">
      {/* Validation summary — the fastest way to know why a send failed. */}
      {problems.length > 0 && (
        <div className="rounded border border-danger/40 bg-danger/10 p-3">
          <p className="flex items-center gap-2 text-xs font-semibold text-danger">
            <AlertTriangle size={14} />
            {problems.length} problem{problems.length === 1 ? "" : "s"} to fix
          </p>
          <ul className="mt-1.5 list-inside list-disc space-y-0.5 text-[11px] text-ink-muted">
            {problems.map((problem) => (
              <li key={problem}>{problem}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Identity overrides */}
      <section className="panel p-3">
        <h3 className="field-label">Message identity</h3>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <TextField
            label="Username"
            placeholder="Defaults to the webhook/bot name"
            value={data.username}
            onChange={(event) => setField("username", event.target.value)}
          />
          <TextField
            label="Avatar URL"
            placeholder="https://…"
            value={data.avatar_url}
            onChange={(event) => setField("avatar_url", event.target.value)}
          />
        </div>
        <TextField
          className="mt-2"
          label="Thread name"
          hint="Only used when the webhook target is a forum channel."
          value={data.thread_name}
          onChange={(event) => setField("thread_name", event.target.value)}
        />
      </section>

      {isClassic ? (
        <>
          <section className="panel p-3">
            <TextArea
              label="Content"
              limit={Limits.content}
              rows={5}
              value={data.content}
              placeholder="Say something…"
              onChange={(event) => setField("content", event.target.value)}
            />
          </section>

          <section className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="field-label !mb-0 flex items-center gap-1.5">
                <ImageIcon size={13} /> Embeds
                <span className="text-ink-faint">
                  {data.embeds.length}/{Limits.embed.embedsPerMessage}
                </span>
              </h3>
              <Button
                size="sm"
                variant="secondary"
                icon={Plus}
                onClick={addEmbed}
                disabled={data.embeds.length >= Limits.embed.embedsPerMessage}
              >
                Add embed
              </Button>
            </div>

            {data.embeds.length === 0 ? (
              <p className="rounded border border-dashed border-line px-3 py-6 text-center text-xs text-ink-faint">
                No embeds yet. Add one to build a classic rich message.
              </p>
            ) : (
              data.embeds.map((embed, index) => (
                <EmbedEditor key={embed._id} embed={embed} index={index} />
              ))
            )}
          </section>
        </>
      ) : (
        <section className="panel p-3">
          <h3 className="field-label flex items-center gap-1.5">
            <Hash size={13} /> Components V2
          </h3>
          <p className="text-xs leading-relaxed text-ink-muted">
            This message is built from components. Use the palette on the left to add containers,
            text displays, sections, galleries and action rows, then select any block to edit its
            properties.
          </p>
          <p className="mt-2 rounded bg-chrome px-2.5 py-2 text-[11px] text-ink-faint">
            <User size={11} className="mr-1 inline" />
            Components V2 messages ignore classic <code>content</code> and <code>embeds</code> —
            Discord rejects them if combined.
          </p>
        </section>
      )}
    </div>
  );
};

export default MessageEditor;

```

### File: `client/src/components/editor/PropertyPanel.tsx`
```tsx
import { Copy, MousePointerSquareDashed, Trash2, X } from "lucide-react";
import { useState } from "react";
import { ButtonStyle, ComponentType } from "@dmb/shared";
import { IconButton } from "../ui/Button";
import { FlowBuilder } from "../actions/FlowBuilder";
import { COMPONENT_FORMS } from "./ComponentForms";
import { componentLabel, isInteractiveComponent } from "../../utils/componentsV2";
import { findComponent } from "../../utils/tree";
import { useMessageStore } from "../../store/messageStore";

/**
 * Context-sensitive editor for whatever is selected.
 *
 * Interactive components (buttons and selects) get two tabs, mirroring
 * Discohook: **Properties** for the component's appearance and **Flow** for the
 * ordered chain of actions its click runs. Link buttons have no `custom_id`, so
 * they only show Properties.
 */

type PanelTab = "properties" | "flow";

const TabButton = ({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: string;
}) => (
  <button
    type="button"
    onClick={onClick}
    aria-pressed={active}
    className={[
      "flex-1 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors",
      active
        ? "bg-raised text-ink-strong shadow-sm"
        : "text-ink-muted hover:bg-hover hover:text-ink",
    ].join(" ")}
  >
    {children}
  </button>
);

export const PropertyPanel = () => {
  const [activeTab, setActiveTab] = useState<PanelTab>("properties");
  const selection = useMessageStore((state) => state.selection);
  const components = useMessageStore((state) => state.data.components);
  const select = useMessageStore((state) => state.select);
  const updateComponentById = useMessageStore((state) => state.updateComponentById);
  const removeComponentById = useMessageStore((state) => state.removeComponentById);
  const duplicateComponentById = useMessageStore((state) => state.duplicateComponentById);

  if (!selection) return null;

  const component =
    selection.kind === "component" ? findComponent(components, selection.id) : null;
  const Form = component ? COMPONENT_FORMS[component.type] : undefined;

  const isLinkButton =
    component?.type === ComponentType.Button && component.style === ButtonStyle.Link;
  const hasFlow = isInteractiveComponent(component ?? undefined) && !isLinkButton;

  return (
    <aside className="flex w-80 shrink-0 flex-col border-l border-line-soft bg-sidebar">
      <div className="flex items-center justify-between border-b border-line-soft px-3 py-2.5">
        <h2 className="truncate text-xs font-semibold text-ink-strong">
          {component ? componentLabel(component) : "Embed"}
        </h2>

        <div className="flex items-center gap-0.5">
          {component?._id && (
            <>
              <IconButton
                icon={Copy}
                label="Duplicate"
                size={13}
                onClick={() => duplicateComponentById(component._id as string)}
              />
              <IconButton
                icon={Trash2}
                label="Delete"
                size={13}
                onClick={() => removeComponentById(component._id as string)}
              />
            </>
          )}
          <IconButton icon={X} label="Close" size={13} onClick={() => select(null)} />
        </div>
      </div>

      {component && Form && hasFlow && (
        <div className="flex gap-0.5 bg-sidebar px-3 pt-2.5">
          <TabButton
            active={activeTab === "properties"}
            onClick={() => setActiveTab("properties")}
          >
            Properties
          </TabButton>
          <TabButton active={activeTab === "flow"} onClick={() => setActiveTab("flow")}>
            Flow
          </TabButton>
        </div>
      )}

      <div className="min-h-0 flex-1 space-y-3 overflow-y-auto p-3">
        {component && Form ? (
          activeTab === "flow" && hasFlow ? (
            <FlowBuilder component={component} />
          ) : (
            <Form
              component={component}
              update={(patch) => component._id && updateComponentById(component._id, patch)}
            />
          )
        ) : (
          <p className="flex items-start gap-2 rounded border border-dashed border-line px-3 py-4 text-[11px] text-ink-faint">
            <MousePointerSquareDashed size={14} className="mt-0.5 shrink-0" />
            This embed is edited directly in its card on the left. Select a component in the tree
            to edit it here.
          </p>
        )}
      </div>
    </aside>
  );
};

export default PropertyPanel;

```

### File: `client/src/components/layout/DocsPanel.tsx`
```tsx
import { BookOpen } from "lucide-react";

export const DocsPanel = () => {
  return (
    <div className="bg-[#2b2d31] p-5 rounded-lg border border-[#1e1f22] shadow-sm font-sans flex flex-col gap-4 text-[#dbdee1] h-full overflow-y-auto custom-scrollbar">
      <h3 className="font-bold uppercase text-xs tracking-wider flex items-center gap-2 mb-2">
        <BookOpen size={16} className="text-[#5865f2]" /> Variable Documentation
      </h3>
      
      <p className="text-[12px] text-[#949ba4] leading-relaxed mb-4">
        You can use these variables in your message content, embeds, and action flows. When a user clicks a button or triggers an action, the bot will dynamically replace them with live data.
      </p>

      {/* User Section */}
      <div className="mb-4">
        <h4 className="text-[12px] font-bold text-[#b5bac1] uppercase border-b border-[#1e1f22] pb-1 mb-2">User</h4>
        <div className="flex flex-col gap-1 text-[12px]">
            <div className="flex gap-2 items-center"><code className="text-[#5865f2] bg-[#1e1f22] px-1.5 py-0.5 rounded w-32 shrink-0">{'{user.mention}'}</code><span className="text-[#949ba4]">Mentions the clicker (@ada).</span></div>
            <div className="flex gap-2 items-center"><code className="text-[#5865f2] bg-[#1e1f22] px-1.5 py-0.5 rounded w-32 shrink-0">{'{user.id}'}</code><span className="text-[#949ba4]">Their numeric ID.</span></div>
            <div className="flex gap-2 items-center"><code className="text-[#5865f2] bg-[#1e1f22] px-1.5 py-0.5 rounded w-32 shrink-0">{'{user.name}'}</code><span className="text-[#949ba4]">The exact username.</span></div>
            <div className="flex gap-2 items-center"><code className="text-[#5865f2] bg-[#1e1f22] px-1.5 py-0.5 rounded w-32 shrink-0">{'{user.displayname}'}</code><span className="text-[#949ba4]">The server nickname.</span></div>
            <div className="flex gap-2 items-center"><code className="text-[#5865f2] bg-[#1e1f22] px-1.5 py-0.5 rounded w-32 shrink-0">{'{user.avatar}'}</code><span className="text-[#949ba4]">A link to their avatar URL.</span></div>
            <div className="flex gap-2 items-center"><code className="text-[#5865f2] bg-[#1e1f22] px-1.5 py-0.5 rounded w-32 shrink-0">{'{user.clantag}'}</code><span className="text-[#949ba4]">Extracts [TAG] from their name.</span></div>
        </div>
      </div>

      {/* Server & Channel Section */}
      <div className="mb-4">
        <h4 className="text-[12px] font-bold text-[#b5bac1] uppercase border-b border-[#1e1f22] pb-1 mb-2">Server & Channel</h4>
        <div className="flex flex-col gap-1 text-[12px]">
            <div className="flex gap-2 items-center"><code className="text-[#5865f2] bg-[#1e1f22] px-1.5 py-0.5 rounded w-32 shrink-0">{'{server.id}'}</code><span className="text-[#949ba4]">The server ID.</span></div>
            <div className="flex gap-2 items-center"><code className="text-[#5865f2] bg-[#1e1f22] px-1.5 py-0.5 rounded w-32 shrink-0">{'{channel.mention}'}</code><span className="text-[#949ba4]">Mentions the current channel.</span></div>
            <div className="flex gap-2 items-center"><code className="text-[#5865f2] bg-[#1e1f22] px-1.5 py-0.5 rounded w-32 shrink-0">{'{channel.id}'}</code><span className="text-[#949ba4]">The channel ID.</span></div>
        </div>
      </div>

      {/* Time Section */}
      <div className="mb-4">
        <h4 className="text-[12px] font-bold text-[#b5bac1] uppercase border-b border-[#1e1f22] pb-1 mb-2">Time of Click</h4>
        <div className="flex flex-col gap-1 text-[12px]">
            <div className="flex gap-2 items-center"><code className="text-[#5865f2] bg-[#1e1f22] px-1.5 py-0.5 rounded w-32 shrink-0">{'{now}'}</code><span className="text-[#949ba4]">Current time (Oct 24, 12:00 PM).</span></div>
            <div className="flex gap-2 items-center"><code className="text-[#5865f2] bg-[#1e1f22] px-1.5 py-0.5 rounded w-32 shrink-0">{'{now.relative}'}</code><span className="text-[#949ba4]">Relative (2 minutes ago).</span></div>
            <div className="flex gap-2 items-center"><code className="text-[#5865f2] bg-[#1e1f22] px-1.5 py-0.5 rounded w-32 shrink-0">{'{now.long}'}</code><span className="text-[#949ba4]">Long format (Tuesday, Oct 24).</span></div>
        </div>
      </div>
    </div>
  );
};
```

### File: `client/src/components/layout/Header.tsx`
```tsx
import { MessageSquare } from "lucide-react";

export const Header = () => {
  return (
    <header className="h-12 shrink-0 flex items-center justify-between border-b border-[#111214] bg-[#1e1f22] px-4 z-20 font-sans">
      <div className="flex items-center gap-4">
        {/* Brand Logo */}
        <div className="flex items-center gap-2 cursor-pointer">
          <div className="bg-[#5865f2] text-white p-1 rounded">
             <MessageSquare size={16} fill="currentColor" />
          </div>
        </div>

        {/* Navigation & Profile */}
        <div className="flex items-center gap-2">
          <button className="hidden sm:flex text-[13px] font-bold text-[#dbdee1] items-center gap-2 hover:bg-[#2b2d31] px-2 py-1 rounded transition-colors">
             <div className="w-5 h-5 rounded-full bg-[#f28b8b] border border-[#1e1f22]"></div>
             Peace
          </button>
          <button className="text-[13px] font-medium text-[#b5bac1] hover:text-[#dbdee1] border border-[#35373c] bg-[#2b2d31] px-3 py-1 rounded-full transition-colors">Settings</button>
          <button className="text-[13px] font-medium text-[#b5bac1] hover:text-[#dbdee1] border border-[#35373c] bg-[#2b2d31] px-3 py-1 rounded-full transition-colors hidden sm:block">History</button>
          <a href="/docs" className="text-[13px] font-medium text-[#b5bac1] hover:text-[#dbdee1] border border-[#35373c] bg-[#2b2d31] px-3 py-1 rounded-full transition-colors">Docs</a>
        </div>
      </div>

      {/* Right Side Actions */}
      <div className="flex items-center gap-3">
         <button className="text-[13px] font-medium text-[#b5bac1] hover:text-[#dbdee1] border border-[#35373c] bg-[#2b2d31] px-3 py-1 rounded-full transition-colors hidden sm:block">Help</button>
         <button className="text-[13px] font-medium text-white bg-[#5865f2] hover:bg-[#4752c4] px-4 py-1 rounded-full transition-colors shadow-sm">Donate</button>
      </div>
    </header>
  );
};

export default Header;
```

### File: `client/src/components/layout/ProfilesPanel.tsx`
```tsx
import React, { useState, useEffect } from "react";
import { Trash2, Save, Users, AlertCircle } from "lucide-react";
import { useProfileStore } from "../../store/profileStore";

export const ProfilesPanel = () => {
  const { botProfiles, fetchProfiles, status } = useProfileStore();
  const [name, setName] = useState("");
  const [token, setToken] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    void fetchProfiles();
  }, [fetchProfiles]);

  const handleSave = async () => {
    if (!name || !token) return;
    setIsSaving(true);
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "";
      const adminKey = import.meta.env.VITE_ADMIN_API_KEY || "";
      
      await fetch(`${baseUrl}/api/profiles/bots`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "x-admin-key": adminKey 
        },
        body: JSON.stringify({ name, token })
      });
      
      setName("");
      setToken("");
      void fetchProfiles();
    } catch (e) {
      console.error("Failed to save profile", e);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to delete this bot profile?")) return;
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "";
      const adminKey = import.meta.env.VITE_ADMIN_API_KEY || "";
      
      await fetch(`${baseUrl}/api/profiles/bots/${id}`, {
        method: "DELETE",
        headers: { "x-admin-key": adminKey }
      });
      
      void fetchProfiles();
    } catch (e) {
      console.error("Failed to delete profile", e);
    }
  };

  return (
    <div className="bg-[#2b2d31] p-5 rounded-lg border border-[#1e1f22] shadow-sm font-sans flex flex-col gap-5">
      <h3 className="font-bold text-[#dbdee1] uppercase text-xs tracking-wider flex items-center gap-2">
        <Users size={16} className="text-[#5865f2]" />
        Bot Profiles
      </h3>

      {/* Add New Profile Form */}
      <div className="bg-[#1e1f22] p-4 rounded border border-[#111214] space-y-3">
        <h4 className="text-[12px] font-bold text-[#b5bac1] uppercase">Add New Bot</h4>
        
        <div>
          <label className="block text-[11px] font-bold text-[#949ba4] mb-1">Profile Name</label>
          <input 
            type="text" 
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full bg-[#2b2d31] text-[#dbdee1] border border-[#111214] rounded p-2 text-sm focus:border-[#5865f2] focus:ring-1 focus:ring-[#5865f2] outline-none transition-all"
            placeholder="e.g. Production Bot"
          />
        </div>

        <div>
          <label className="block text-[11px] font-bold text-[#949ba4] mb-1">Bot Token</label>
          <input 
            type="password" 
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="w-full bg-[#2b2d31] text-[#dbdee1] border border-[#111214] rounded p-2 text-sm focus:border-[#5865f2] focus:ring-1 focus:ring-[#5865f2] outline-none transition-all"
            placeholder="Paste Discord Bot Token here"
          />
        </div>

        <button 
          onClick={handleSave}
          disabled={!name || !token || isSaving}
          className="w-full mt-2 flex items-center justify-center gap-2 bg-[#5865f2] hover:bg-[#4752c4] text-white font-medium py-2 rounded text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save size={14} /> {isSaving ? "Saving..." : "Save Bot Profile"}
        </button>
        <p className="text-[10px] text-[#949ba4] mt-2 text-center">Tokens are encrypted and stored securely in your server's database.</p>
      </div>

      {/* Saved Profiles List */}
      <div className="space-y-2 mt-2">
        <h4 className="text-[12px] font-bold text-[#b5bac1] uppercase mb-3">Saved Bots</h4>
        
        {status === "loading" ? (
          <p className="text-[12px] text-[#949ba4]">Loading profiles...</p>
        ) : botProfiles.length === 0 ? (
          <p className="text-[12px] text-[#949ba4] bg-[#1e1f22] p-3 rounded text-center border border-[#111214]">No custom bots saved yet.</p>
        ) : (
          botProfiles.map(profile => (
            <div key={profile.id} className="flex items-center justify-between bg-[#1e1f22] p-3 rounded border border-[#111214]">
              <span className="text-sm font-medium text-[#dbdee1]">{profile.name}</span>
              <button 
                onClick={() => handleDelete(profile.id)}
                className="text-[#f28b8b] hover:text-[#da373c] p-1.5 rounded hover:bg-[#da373c]/10 transition-colors"
                title="Delete Profile"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
```

### File: `client/src/components/layout/Sidebar.tsx`
```tsx
import { useState } from "react";
import { Blocks, BookOpen, Send, Users } from "lucide-react";
import { ComponentPalette } from "../editor/ComponentPalette";
import { LayersPanel } from "../editor/LayersPanel";
import { SendPanel } from "../send/SendPanel";
import { ProfilesPanel } from "./ProfilesPanel";

export const Sidebar = () => {
  const [activeTab, setActiveTab] = useState<'build' | 'send' | 'profiles'>('build');

  return (
    <div className="w-80 h-full bg-[#2b2d31] border-r border-[#1e1f22] flex flex-col shadow-lg z-10 font-sans shrink-0">
      {/* Tab Navigation Rail */}
      <div className="flex p-2 gap-1 bg-[#1e1f22] border-b border-[#111214]">
        <button
          onClick={() => setActiveTab('build')}
          className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded text-[11px] font-bold uppercase tracking-wider transition-all ${
            activeTab === 'build' ? 'bg-[#5865f2] text-white shadow-sm' : 'text-[#b5bac1] hover:bg-[#2b2d31] hover:text-[#dbdee1]'
          }`}
        >
          <Blocks size={14} /> Build
        </button>
        <button
          onClick={() => setActiveTab('send')}
          className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded text-[11px] font-bold uppercase tracking-wider transition-all ${
            activeTab === 'send' ? 'bg-[#5865f2] text-white shadow-sm' : 'text-[#b5bac1] hover:bg-[#2b2d31] hover:text-[#dbdee1]'
          }`}
        >
          <Send size={14} /> Send
        </button>
        <button
          onClick={() => setActiveTab('profiles')}
          className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded text-[11px] font-bold uppercase tracking-wider transition-all ${
            activeTab === 'profiles' ? 'bg-[#5865f2] text-white shadow-sm' : 'text-[#b5bac1] hover:bg-[#2b2d31] hover:text-[#dbdee1]'
          }`}
        >
          <Users size={14} /> Profs
        </button>
        <a
          href="/docs"
          className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded text-[11px] font-bold uppercase tracking-wider text-[#b5bac1] hover:bg-[#2b2d31] hover:text-[#dbdee1] transition-all"
        >
          <BookOpen size={14} /> Docs
        </a>
      </div>

      {/* Tab Content Panels */}
      <div className="flex-1 overflow-y-auto custom-scrollbar flex flex-col relative">
        <div className={`flex flex-col h-full ${activeTab === 'build' ? 'flex' : 'hidden'}`}>
          <div className="p-4 shrink-0 border-b border-[#1e1f22]">
            <ComponentPalette />
          </div>
          <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
            <LayersPanel />
          </div>
        </div>

        <div className={`p-4 h-full ${activeTab === 'send' ? 'block' : 'hidden'}`}>
          <SendPanel />
        </div>

        <div className={`p-4 h-full ${activeTab === 'profiles' ? 'block' : 'hidden'}`}>
          <ProfilesPanel />
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
```

### File: `client/src/components/layout/SplitPane.tsx`
```tsx
import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";

/**
 * Resizable horizontal split.
 *
 * The divider is dragged with pointer events, which unifies mouse and touch and
 * avoids the "drag stops when the cursor leaves the element" problem that plain
 * mousemove listeners have. The ratio is clamped so neither pane can be collapsed
 * by accident.
 */
export interface SplitPaneProps {
  left: ReactNode;
  right: ReactNode;
  initialRatio?: number;
  minRatio?: number;
  maxRatio?: number;
  className?: string;
}

export const SplitPane = ({
  left,
  right,
  initialRatio = 0.5,
  minRatio = 0.25,
  maxRatio = 0.75,
  className = "",
}: SplitPaneProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [ratio, setRatio] = useState(initialRatio);
  const draggingRef = useRef(false);

  const onPointerMove = useCallback(
    (event: PointerEvent) => {
      if (!draggingRef.current || !containerRef.current) return;
      const bounds = containerRef.current.getBoundingClientRect();
      const next = (event.clientX - bounds.left) / bounds.width;
      setRatio(Math.min(Math.max(next, minRatio), maxRatio));
    },
    [minRatio, maxRatio],
  );

  const stopDragging = useCallback(() => {
    draggingRef.current = false;
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
  }, []);

  const startDragging = useCallback(() => {
    draggingRef.current = true;
    // Keep the resize cursor while dragging, even outside the divider.
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  }, []);

  useEffect(() => {
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", stopDragging);
    return () => {
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", stopDragging);
    };
  }, [onPointerMove, stopDragging]);

  return (
    <div ref={containerRef} className={`flex min-h-0 min-w-0 flex-1 ${className}`}>
      <div className="flex min-h-0 min-w-0 flex-col" style={{ width: `${ratio * 100}%` }}>
        {left}
      </div>

      {/* Keyboard-resizable divider so the layout is not mouse-only. */}
      <div
        role="separator"
        aria-orientation="vertical"
        aria-label="Resize editor and preview"
        tabIndex={0}
        onPointerDown={startDragging}
        onKeyDown={(event) => {
          if (event.key === "ArrowLeft") setRatio((r) => Math.max(minRatio, r - 0.02));
          if (event.key === "ArrowRight") setRatio((r) => Math.min(maxRatio, r + 0.02));
        }}
        className="group relative w-px shrink-0 cursor-col-resize bg-line transition-colors hover:bg-blurple"
      >
        {/* Wider invisible hit area so the 1px line is actually grabbable. */}
        <span className="absolute inset-y-0 -left-1.5 -right-1.5 block" />
      </div>

      <div className="flex min-h-0 min-w-0 flex-1 flex-col">{right}</div>
    </div>
  );
};

export default SplitPane;

```

### File: `client/src/components/preview/ActionRowPreview.tsx`
```tsx
import { ChevronDown, ExternalLink } from "lucide-react";
import type { ComponentNode } from "@dmb/shared";
import { ButtonStyle, ComponentType } from "@dmb/shared";

/**
 * Preview of an action row's controls.
 *
 * Buttons render with Discord's real colours so the preview communicates what a
 * click will *feel* like — a red "Danger" button reads very differently from a
 * blurple primary one, and that matters during design.
 */

const BUTTON_CLASSES: Record<number, string> = {
  [ButtonStyle.Primary]: "bg-[#5865f2] hover:bg-[#4752c4] text-white",
  [ButtonStyle.Secondary]: "bg-[#4e5058] hover:bg-[#6d6f78] text-white",
  [ButtonStyle.Success]: "bg-[#248046] hover:bg-[#1a6334] text-white",
  [ButtonStyle.Danger]: "bg-[#da373c] hover:bg-[#a12828] text-white",
  [ButtonStyle.Link]: "bg-[#4e5058] hover:bg-[#6d6f78] text-white",
  [ButtonStyle.Premium]: "bg-[#4e5058] text-white",
};

const SELECT_TYPES: readonly number[] = [
  ComponentType.StringSelect,
  ComponentType.UserSelect,
  ComponentType.RoleSelect,
  ComponentType.ChannelSelect,
  ComponentType.MentionableSelect,
];

const ButtonPreview = ({ button }: { button: ComponentNode }) => {
  const isLink = button.style === ButtonStyle.Link;

  return (
    <button
      type="button"
      disabled={button.disabled}
      className={[
        "inline-flex h-8 items-center gap-1.5 rounded px-4 text-sm font-medium transition-colors",
        BUTTON_CLASSES[button.style ?? ButtonStyle.Primary] ?? BUTTON_CLASSES[ButtonStyle.Primary],
        button.disabled ? "cursor-not-allowed opacity-50" : "",
      ].join(" ")}
    >
      {isLink && <ExternalLink size={14} />}
      {button.label ?? (isLink ? "Link" : "Button")}
    </button>
  );
};

const SelectPreview = ({ select }: { select: ComponentNode }) => (
  <div className="flex h-10 w-full max-w-[400px] items-center justify-between rounded border border-[#3f4147] bg-[#1e1f22] px-3 text-sm text-[#949ba4]">
    <span>{select.placeholder ?? "Make a selection"}</span>
    <ChevronDown size={16} />
  </div>
);

export interface ActionRowPreviewProps {
  component: ComponentNode;
}

export const ActionRowPreview = ({ component }: ActionRowPreviewProps) => (
  <div className="flex flex-wrap items-center gap-2">
    {(component.components ?? []).map((child) =>
      SELECT_TYPES.includes(child.type) ? (
        <SelectPreview key={child._id} select={child} />
      ) : (
        <ButtonPreview key={child._id} button={child} />
      ),
    )}
  </div>
);

export default ActionRowPreview;

```

### File: `client/src/components/preview/ComponentPreview.tsx`
```tsx
import { FileText } from "lucide-react";
import type { ComponentNode } from "@dmb/shared";
import { ComponentType } from "@dmb/shared";
import { Markdown } from "./Markdown";
import { ActionRowPreview } from "./ActionRowPreview";

/**
 * Previews for the components that can sit inside a container (plus action rows,
 * which can also be top-level).
 *
 * Deliberately does **not** handle Container — containers are only legal at the
 * top level, and keeping them out of this file avoids a circular import between
 * the two preview modules.
 */

const TextDisplayPreview = ({ component }: { component: ComponentNode }) => (
  <Markdown content={component.content ?? ""} className="text-sm text-[#dbdee1]" />
);

const SeparatorPreview = ({ component }: { component: ComponentNode }) =>
  component.divider === false ? (
    <div style={{ height: component.spacing === 2 ? 16 : 8 }} />
  ) : (
    <hr
      className="border-0 bg-[#3f4147]"
      style={{ height: 1, margin: `${component.spacing === 2 ? 12 : 6}px 0` }}
    />
  );

const SectionPreview = ({ component }: { component: ComponentNode }) => {
  const thumbnail = component.accessory?.media?.url;

  return (
    <div className="flex items-start gap-3">
      <div className="min-w-0 flex-1 space-y-1">
        {(component.components ?? []).map((child) => (
          <AutoComponent key={child._id} component={child} />
        ))}
      </div>
      {thumbnail && (
        <img src={thumbnail} alt="" className="h-20 w-20 shrink-0 rounded object-cover" />
      )}
    </div>
  );
};

const MediaGalleryPreview = ({ component }: { component: ComponentNode }) => {
  const items = component.items ?? [];
  if (items.length === 0) return <p className="text-xs text-[#6d6f78]">No gallery images</p>;

  const cols = items.length === 1 ? "grid-cols-1" : items.length === 2 ? "grid-cols-2" : "grid-cols-3";

  return (
    <div className={`grid gap-1.5 ${cols}`}>
      {items.map((item) => (
        <img
          key={item._id}
          src={item.media.url}
          alt=""
          className="h-32 w-full rounded object-cover"
        />
      ))}
    </div>
  );
};

const FilePreview = ({ component }: { component: ComponentNode }) => {
  const url = component.file?.url ?? "";
  const name = url.split("/").pop() || "attachment";

  return (
    <div className="inline-flex items-center gap-2 rounded border border-[#3f4147] bg-[#2b2d31] px-3 py-2">
      <FileText size={16} className="text-[#b5bac1]" />
      <span className="text-sm text-[#dbdee1]">{name}</span>
    </div>
  );
};

export interface AutoComponentProps {
  component: ComponentNode;
}

/** Dispatch a non-container component to its preview. */
export const AutoComponent = ({ component }: AutoComponentProps) => {
  switch (component.type) {
    case ComponentType.TextDisplay:
      return <TextDisplayPreview component={component} />;
    case ComponentType.Separator:
      return <SeparatorPreview component={component} />;
    case ComponentType.Section:
      return <SectionPreview component={component} />;
    case ComponentType.MediaGallery:
      return <MediaGalleryPreview component={component} />;
    case ComponentType.File:
      return <FilePreview component={component} />;
    case ComponentType.ActionRow:
      return <ActionRowPreview component={component} />;
    default:
      return null;
  }
};

export { TextDisplayPreview, SeparatorPreview, SectionPreview, MediaGalleryPreview, FilePreview };
export default AutoComponent;

```

### File: `client/src/components/preview/ContainerPreview.tsx`
```tsx
import type { ComponentNode } from "@dmb/shared";
import { AutoComponent } from "./ComponentPreview";
import { decimalToHex } from "../../utils/discord";

/**
 * Container preview.
 *
 * Discord renders containers as a rounded card with an optional solid accent bar
 * down the left edge — implemented here with an absolutely positioned element
 * rather than a border, because a border would be clipped by the rounded corners.
 */
export interface ContainerPreviewProps {
  component: ComponentNode;
}

export const ContainerPreview = ({ component }: ContainerPreviewProps) => {
  const hasAccent = component.accent_color != null;

  return (
    <div className="relative max-w-[520px] overflow-hidden rounded-lg border border-[#3f4147] bg-[#2b2d31] p-4 pl-5">
      {hasAccent && (
        <span
          className="absolute inset-y-0 left-0 w-1"
          style={{ backgroundColor: decimalToHex(component.accent_color) }}
        />
      )}

      <div className="space-y-2">
        {(component.components ?? []).map((child) => (
          <AutoComponent key={child._id} component={child} />
        ))}
      </div>
    </div>
  );
};

export default ContainerPreview;

```

### File: `client/src/components/preview/EmbedPreview.tsx`
```tsx
import type { EmbedData, EmbedField } from "@dmb/shared";
import { Markdown } from "./Markdown";
import { decimalToHex } from "../../utils/discord";

/**
 * Discord-style embed preview.
 *
 * Mirrors the real layout closely: a 4px accent bar on the left, an optional
 * thumbnail floated to the right, and fields laid out in inline rows of up to
 * three. The subtle part is that inline fields wrap *greedily* — three per row
 * only while each still fits — which is why fields are grouped before render.
 */

/** Tailwind cannot generate classes from a template literal, so map explicitly. */
const INLINE_COLS: Record<number, string> = {
  1: "",
  2: "grid-cols-2",
  3: "grid-cols-3",
};

/** Group consecutive inline fields into rows of up to three. */
const groupFields = (fields: readonly EmbedField[] = []): EmbedField[][] => {
  const rows: EmbedField[][] = [];

  for (const field of fields) {
    const current = rows[rows.length - 1];
    const last = current?.[current.length - 1];

    if (current && field.inline && last?.inline && current.length < 3) {
      current.push(field);
    } else {
      rows.push([field]);
    }
  }
  return rows;
};

export interface EmbedPreviewProps {
  embed: EmbedData;
}

export const EmbedPreview = ({ embed }: EmbedPreviewProps) => {
  const accent = embed.color == null ? "#4f545c" : decimalToHex(embed.color);
  const rows = groupFields(embed.fields);

  return (
    <div
      className="max-w-[520px] rounded border-l-4 bg-[#2b2d31] px-3 py-2 pr-4 text-[#dbdee1]"
      style={{ borderLeftColor: accent }}
    >
      {embed.author?.name && (
        <div className="mb-1 flex items-center gap-2">
          {embed.author.icon_url && (
            <img src={embed.author.icon_url} alt="" className="h-6 w-6 rounded-full object-cover" />
          )}
          <span className="text-sm font-semibold">{embed.author.name}</span>
        </div>
      )}

      <div className="flex gap-4">
        <div className="min-w-0 flex-1">
          {embed.title && (
            <p className="mb-1 text-base leading-tight font-semibold text-[#f2f3f5]">
              {embed.url ? (
                <a
                  href={embed.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-link hover:underline"
                >
                  {embed.title}
                </a>
              ) : (
                embed.title
              )}
            </p>
          )}

          {embed.description && <Markdown content={embed.description} className="text-sm" />}
        </div>

        {embed.thumbnail?.url && (
          <img
            src={embed.thumbnail.url}
            alt=""
            className="h-20 max-w-[80px] shrink-0 self-start rounded object-cover"
          />
        )}
      </div>

      {rows.length > 0 && (
        <div className="mt-2 grid grid-cols-1 gap-2">
          {rows.map((row, rowIndex) => (
            <div
              key={rowIndex}
              className={row.length > 1 ? `grid gap-2 ${INLINE_COLS[row.length] ?? ""}` : ""}
            >
              {row.map((field) => (
                <div key={field._id ?? field.name}>
                  <p className="text-sm font-semibold text-[#f2f3f5]">{field.name || "\u00a0"}</p>
                  {field.value && <Markdown content={field.value} className="text-sm" />}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {embed.image?.url && (
        <img src={embed.image.url} alt="" className="mt-2 max-h-72 w-full rounded object-cover" />
      )}

      {(embed.footer?.text || embed.timestamp) && (
        <div className="mt-2 flex items-center gap-2 text-xs font-medium text-[#949ba4]">
          {embed.footer?.icon_url && (
            <img
              src={embed.footer.icon_url}
              alt=""
              className="h-5 w-5 rounded-full object-cover"
            />
          )}
          {embed.footer?.text && <span>{embed.footer.text}</span>}
          {embed.footer?.text && embed.timestamp && <span>•</span>}
          {embed.timestamp && <span>{new Date(embed.timestamp).toLocaleString()}</span>}
        </div>
      )}
    </div>
  );
};

export default EmbedPreview;

```

### File: `client/src/components/preview/Markdown.test.ts`
```ts
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { Markdown } from "./Markdown";

/**
 * Regression tests for the preview markdown renderer.
 *
 * The emphasis branches recurse into the inline renderer. A shared module-level
 * global regex used to leak `lastIndex` across those recursive calls, so any
 * `**bold**` in a Components V2 TextDisplay made the renderer loop forever and
 * freeze the page. These tests assert the output *and* act as a canary: if the
 * shared-regex bug returns, this file hangs instead of failing, because the loop
 * is synchronous and cannot be interrupted by a test timeout.
 */

const render = (content: string): string =>
  renderToStaticMarkup(createElement(Markdown, { content }));

describe("Markdown", () => {
  it("renders bold text without hanging", () => {
    expect(render("**bold**")).toContain("<strong");
    expect(render("**bold**")).toContain("bold");
  });

  it("renders several emphasis tokens in one line", () => {
    const html = render("**one** then *two* then ~~three~~");
    expect(html).toContain("<strong");
    expect(html).toContain("<em");
    expect(html).toContain("line-through");
  });

  it("renders nested emphasis, which is what triggered the recursion", () => {
    const html = render("**bold with `code`**");
    expect(html).toContain("<strong");
    expect(html).toContain("<code");
    expect(html).toContain("code");
  });

  it("renders bold, italic and code inside a paragraph block", () => {
    const html = render("Hello **world**");
    expect(html).toContain("Hello");
    expect(html).toContain("<strong");
  });

  it("leaves plain text and non-markdown content untouched", () => {
    expect(render("just plain text")).toContain("just plain text");
  });

  it("tolerates a custom emoji next to emphasis", () => {
    const html = render("**hi** <:party:123456789012345678>");
    expect(html).toContain("<strong");
    expect(html).toContain("<img");
  });
});

```

### File: `client/src/components/preview/Markdown.tsx`
```tsx
import { Fragment, type ReactNode } from "react";

/**
 * A small Discord-flavoured markdown renderer for the live preview.
 *
 * Scope is deliberate: this covers what people actually put in messages —
 * headings, emphasis, code, quotes, lists, links, mentions and custom emoji. It
 * builds React nodes rather than HTML strings, so there is no
 * `dangerouslySetInnerHTML` and therefore no injection surface.
 *
 * Anything unrecognised renders as plain text, which is exactly how Discord
 * behaves with unsupported syntax.
 */

/* ── Inline ───────────────────────────────────────────────────────────────── */

// Order matters: longer delimiters must be tried before their prefixes.
//
// Kept as a *source string* and compiled per {@link renderInline} call, NOT as a
// shared module-level `g` regex. A global regex carries `lastIndex` between
// calls; because emphasis recurses into `renderInline`, the inner call would
// reset `lastIndex` while the outer loop was mid-scan, making the outer loop
// re-match the same token forever — an infinite loop that froze the whole
// preview the moment a Components V2 TextDisplay contained `**bold**`.
const INLINE_SOURCE = [
  "(`[^`\\n]+`)", // inline code
  "(\\*\\*\\*[^*\\n]+\\*\\*\\*)", // ***bold italic***
  "(\\*\\*[^*\\n]+\\*\\*)", // **bold**
  "(__[^_\\n]+__)", // __underline__
  "(\\*[^*\\n]+\\*)", // *italic*
  "(~~[^~\\n]+~~)", // ~~strike~~
  "(\\|\\|[^|\\n]+\\|\\|)", // ||spoiler||
  "(\\[[^\\]]+\\]\\([^)]+\\))", // [text](url)
  "(<a?:\\w+:\\d+>)", // custom emoji
  "(<@!?\\d+>)", // user mention
  "(<@&\\d+>)", // role mention
  "(<#\\d+>)", // channel mention
  "(<t:\\d+(?::[tTdDfFR])?>)", // timestamp
  "(https?:\\/\\/[^\\s<]+)", // bare URL
].join("|");

const MentionChip = ({ children }: { children: ReactNode }) => (
  <span className="rounded bg-blurple/30 px-1 font-medium text-[#dee0fc]">{children}</span>
);

const renderInline = (text: string, keyPrefix = "i"): ReactNode[] => {
  if (text.length === 0) return [text];

  const nodes: ReactNode[] = [];
  let lastIndex = 0;
  let index = 0;

  // Local instance: recursion gets its own `lastIndex`, so nested emphasis
  // cannot corrupt the outer scan (see {@link INLINE_SOURCE}).
  const pattern = new RegExp(INLINE_SOURCE, "g");
  let match: RegExpExecArray | null;

  while ((match = pattern.exec(text)) !== null) {
    const token = match[0];

    // Safety net: an empty match would spin forever. Every alternative requires
    // at least one character today, but this keeps a future pattern change from
    // reintroducing a freeze.
    if (token.length === 0) {
      pattern.lastIndex += 1;
      continue;
    }

    if (match.index > lastIndex) nodes.push(text.slice(lastIndex, match.index));
    lastIndex = match.index + token.length;
    const key = `${keyPrefix}-${index++}`;

    // Inline code
    if (token.length > 1 && token.startsWith("`") && token.endsWith("`")) {
      nodes.push(
        <code key={key} className="rounded bg-chrome px-1 py-0.5 font-mono text-[0.85em]">
          {token.slice(1, -1)}
        </code>,
      );
      continue;
    }

    // Custom emoji -> image
    const emoji = token.match(/^<(a?):(\w+):(\d+)>$/);
    if (emoji) {
      const [, animated, name, id] = emoji;
      nodes.push(
        <img
          key={key}
          src={`https://cdn.discordapp.com/emojis/${id}.${animated ? "gif" : "png"}?size=32`}
          alt={`:${name}:`}
          title={`:${name}:`}
          className="inline-block h-[1.375em] w-[1.375em] align-[-0.3em]"
        />,
      );
      continue;
    }

    // Mentions and timestamps render as the familiar coloured chips.
    if (/^<@!?\d+>$/.test(token)) {
      nodes.push(
        <MentionChip key={key}>
          <span>@user</span>
        </MentionChip>,
      );
      continue;
    }
    if (/^<@&\d+>$/.test(token)) {
      nodes.push(
        <MentionChip key={key}>
          <span>@role</span>
        </MentionChip>,
      );
      continue;
    }
    if (/^<#\d+>$/.test(token)) {
      nodes.push(
        <MentionChip key={key}>
          <span>#channel</span>
        </MentionChip>,
      );
      continue;
    }
    if (token.startsWith("<t:")) {
      const seconds = Number(token.match(/^<t:(\d+)/)?.[1] ?? 0) * 1000;
      nodes.push(
        <span key={key} className="rounded bg-chrome px-1 text-[0.9em] text-ink-muted">
          {new Date(seconds).toLocaleString()}
        </span>,
      );
      continue;
    }

    // Links
    if (token.startsWith("[")) {
      const link = token.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      const [, label, href] = link ?? [];
      if (label && href) {
        nodes.push(
          <a
            key={key}
            href={href}
            target="_blank"
            rel="noreferrer nofollow"
            className="text-link hover:underline"
          >
            {label}
          </a>,
        );
        continue;
      }
    }
    if (token.startsWith("http")) {
      nodes.push(
        <a
          key={key}
          href={token}
          target="_blank"
          rel="noreferrer nofollow"
          className="text-link hover:underline"
        >
          {token}
        </a>,
      );
      continue;
    }

    // Emphasis — recursion handles nesting, e.g. **bold with `code`**.
    if (token.startsWith("***")) {
      nodes.push(
        <strong key={key} className="font-bold italic">
          {renderInline(token.slice(3, -3), key)}
        </strong>,
      );
    } else if (token.startsWith("**")) {
      nodes.push(
        <strong key={key} className="font-bold">
          {renderInline(token.slice(2, -2), key)}
        </strong>,
      );
    } else if (token.startsWith("__")) {
      nodes.push(
        <span key={key} className="underline">
          {renderInline(token.slice(2, -2), key)}
        </span>,
      );
    } else if (token.startsWith("~~")) {
      nodes.push(
        <span key={key} className="line-through">
          {renderInline(token.slice(2, -2), key)}
        </span>,
      );
    } else if (token.startsWith("||")) {
      nodes.push(
        <span key={key} className="rounded bg-chrome px-1 text-transparent hover:text-ink">
          {token.slice(2, -2)}
        </span>,
      );
    } else if (token.startsWith("*")) {
      nodes.push(
        <em key={key} className="italic">
          {renderInline(token.slice(1, -1), key)}
        </em>,
      );
    } else {
      nodes.push(token);
    }
  }

  if (lastIndex < text.length) nodes.push(text.slice(lastIndex));
  return nodes;
};

/* ── Block level ──────────────────────────────────────────────────────────── */

type Block =
  | { kind: "code"; language: string; content: string }
  | { kind: "heading"; level: number; content: string }
  | { kind: "quote"; content: string }
  | { kind: "list"; ordered: boolean; items: string[] }
  | { kind: "paragraph"; content: string };

const splitBlocks = (content: string): Block[] => {
  const lines = content.split("\n");
  const blocks: Block[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index] ?? "";

    // Fenced code block
    if (line.trimStart().startsWith("```")) {
      const language = line.trim().slice(3);
      const body: string[] = [];
      index += 1;
      while (index < lines.length && !(lines[index] ?? "").trimStart().startsWith("```")) {
        body.push(lines[index] ?? "");
        index += 1;
      }
      index += 1; // closing fence
      blocks.push({ kind: "code", language, content: body.join("\n") });
      continue;
    }

    // Heading
    const heading = line.match(/^(#{1,3})\s+(.*)$/);
    if (heading) {
      blocks.push({
        kind: "heading",
        level: (heading[1] ?? "#").length,
        content: heading[2] ?? "",
      });
      index += 1;
      continue;
    }

    // Blockquote
    if (line.startsWith("> ")) {
      const body: string[] = [];
      while (index < lines.length && (lines[index] ?? "").startsWith("> ")) {
        body.push((lines[index] ?? "").slice(2));
        index += 1;
      }
      blocks.push({ kind: "quote", content: body.join("\n") });
      continue;
    }

    // Lists
    if (/^\s*([-*]|\d+\.)\s+/.test(line)) {
      const ordered = /^\s*\d+\.\s+/.test(line);
      const items: string[] = [];
      while (index < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[index] ?? "")) {
        items.push((lines[index] ?? "").replace(/^\s*([-*]|\d+\.)\s+/, ""));
        index += 1;
      }
      blocks.push({ kind: "list", ordered, items });
      continue;
    }

    // Blank line
    if (line.trim() === "") {
      index += 1;
      continue;
    }

    blocks.push({ kind: "paragraph", content: line });
    index += 1;
  }

  return blocks;
};

export interface MarkdownProps {
  content: string;
  className?: string;
}

/** Render Discord-flavoured markdown as React nodes. */
export const Markdown = ({ content, className = "" }: MarkdownProps) => {
  if (!content) return null;
  const blocks = splitBlocks(content);

  return (
    <div className={`whitespace-pre-wrap break-words ${className}`}>
      {blocks.map((block, index) => {
        switch (block.kind) {
          case "code":
            return (
              <pre
                key={index}
                className="my-1 overflow-x-auto rounded border border-chrome bg-[#2b2d31] p-2 font-mono text-[0.8125rem]"
              >
                <code>{block.content}</code>
              </pre>
            );
          case "heading": {
            const sizes: Record<number, string> = {
              1: "text-xl font-bold",
              2: "text-lg font-bold",
              3: "text-base font-bold",
            };
            return (
              <p key={index} className={`mt-2 first:mt-0 ${sizes[block.level] ?? ""}`}>
                {renderInline(block.content)}
              </p>
            );
          }
          case "quote":
            return (
              <blockquote
                key={index}
                className="my-1 border-l-4 border-[#4f545c] pl-2 text-[0.95em]"
              >
                {renderInline(block.content)}
              </blockquote>
            );
          case "list":
            return block.ordered ? (
              <ol key={index} className="my-1 list-inside list-decimal space-y-0.5">
                {block.items.map((item, itemIndex) => (
                  <li key={itemIndex}>{renderInline(item)}</li>
                ))}
              </ol>
            ) : (
              <ul key={index} className="my-1 list-inside list-disc space-y-0.5">
                {block.items.map((item, itemIndex) => (
                  <li key={itemIndex}>{renderInline(item)}</li>
                ))}
              </ul>
            );
          default:
            return (
              <Fragment key={index}>
                <p className="min-h-[1px]">{renderInline(block.content)}</p>
              </Fragment>
            );
        }
      })}
    </div>
  );
};

export default Markdown;

```

### File: `client/src/components/preview/MessagePreview.tsx`
```tsx
import { useEffect, useState } from "react";
import { Bot, Eye, Info } from "lucide-react";
import type { ComponentNode } from "@dmb/shared";
import { ComponentType, MessageFlags } from "@dmb/shared";
import { Markdown } from "./Markdown";
import { EmbedPreview } from "./EmbedPreview";
import { ContainerPreview } from "./ContainerPreview";
import { AutoComponent } from "./ComponentPreview";
import { useMessage } from "../../hooks/useMessage";
import { EDITOR_MODES } from "../../utils/constants";

/**
 * Live preview of the message as Discord would render it.
 *
 * This is the feedback loop that makes the editor usable, so it aims for visual
 * fidelity rather than structural reuse: embeds, Components V2 blocks and the
 * message chrome are all reproduced with Discord's real colours and spacing.
 *
 * The clock is captured once on mount and refreshed on a timer so the preview
 * doesn't jitter on every keystroke.
 */
const TopLevelComponent = ({ component }: { component: ComponentNode }) =>
  component.type === ComponentType.Container ? (
    <ContainerPreview component={component} />
  ) : (
    <AutoComponent component={component} />
  );

export const MessagePreview = () => {
  const { mode, data, payload, isEmpty } = useMessage();
  const [now, setNow] = useState(() => new Date());

  // Refresh the "Today at …" label every minute.
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 60_000);
    return () => clearInterval(timer);
  }, []);

  const authorName = data.username || "Message Builder";
  const isV2 = mode === EDITOR_MODES.V2;

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex items-center justify-between border-b border-line bg-chrome px-4 py-2.5">
        <h2 className="flex items-center gap-1.5 text-sm font-semibold text-ink-strong">
          <Eye size={14} /> Preview
        </h2>
        <span className="rounded-md bg-raised px-2 py-0.5 text-[10px] font-medium text-ink-muted">
          {isV2 ? "Components V2" : "Classic"}
        </span>
      </div>

      {/* Discord's chat background, kept literal so the preview reads as Discord. */}
      <div className="min-h-0 flex-1 overflow-y-auto bg-[#313338] p-4">
        {isEmpty ? (
          <p className="flex items-center gap-2 text-xs text-ink-faint">
            <Info size={13} /> Nothing to preview yet.
          </p>
        ) : (
          <div className="flex gap-3">
            <div className="h-10 w-10 shrink-0 overflow-hidden rounded-full bg-blurple">
              {data.avatar_url ? (
                <img src={data.avatar_url} alt="" className="h-full w-full object-cover" />
              ) : (
                <span className="flex h-full w-full items-center justify-center">
                  <Bot size={18} className="text-white" />
                </span>
              )}
            </div>

            <div className="min-w-0 flex-1">
              <p className="flex items-center gap-2">
                <span className="text-[15px] font-medium text-[#f2f3f5]">{authorName}</span>
                <span className="rounded bg-blurple px-1 py-px text-[10px] font-semibold text-white">
                  APP
                </span>
                <span className="text-xs text-[#949ba4]">
                  Today at {now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </span>
              </p>

              <div className="mt-0.5 space-y-2">
                {/* Classic message body */}
                {!isV2 && payload.content && (
                  <Markdown content={payload.content} className="text-[15px] text-[#dbdee1]" />
                )}

                {!isV2 &&
                  data.embeds.map((embed) => <EmbedPreview key={embed._id} embed={embed} />)}

                {/* Components V2 body */}
                {isV2 &&
                  data.components.map((component) => (
                    <div key={component._id}>
                      <TopLevelComponent component={component} />
                    </div>
                  ))}

                {/* Classic action rows appear under the content/embeds. */}
                {!isV2 &&
                  data.components
                    .filter((component) => component.type === ComponentType.ActionRow)
                    .map((component) => (
                      <div key={component._id}>
                        <AutoComponent component={component} />
                      </div>
                    ))}
              </div>

              {isV2 && (
                <p className="mt-3 font-mono text-[10px] text-ink-faint">
                  flags: {MessageFlags.IsComponentsV2} (IsComponentsV2)
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessagePreview;

```

### File: `client/src/components/send/BotDispatchModal.tsx`
```tsx
import { useEffect, useState } from "react";
import { Bot, CheckSquare, Server, Square, Edit3, Send } from "lucide-react";
import { Modal } from "../ui/Modal";
import { Button } from "../ui/Button";
import { Select, TextField } from "../ui/Field";
import { useProfileStore } from "../../store/profileStore";
import { useMessageStore } from "../../store/messageStore";
import { useActionStore } from "../../store/actionStore";

export const BotDispatchModal = ({ 
  open, 
  onClose, 
  initialMode = 'send' 
}: { 
  open: boolean; 
  onClose: () => void;
  initialMode?: 'send' | 'edit';
}) => {
  const botProfiles = useProfileStore((state) => state.botProfiles);
  const fetchProfiles = useProfileStore((state) => state.fetchProfiles);
  const botProfileId = useProfileStore((state) => state.botProfileId);
  const setBotProfileId = useProfileStore((state) => state.setBotProfileId);

  const [mode, setMode] = useState<'send' | 'edit'>(initialMode);
  const [channels, setChannels] = useState<{ id: string; name: string }[]>([]);
  
  const [selectedChannels, setSelectedChannels] = useState<string[]>(() => 
    JSON.parse(localStorage.getItem('bot_selected_channels') || '[]')
  );

  // Cached Bot Identities
  const [identities, setIdentities] = useState<Record<string, {name: string, avatar: string}>>(() => 
    JSON.parse(localStorage.getItem('bot_identities_cache') || '{}')
  );

  const [botMessages, setBotMessages] = useState<{id: string, content: string}[]>([]);
  const [targetMessageId, setTargetMessageId] = useState("");
  
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [sendResult, setSendResult] = useState<string | null>(null);

  useEffect(() => { setMode(initialMode); }, [initialMode]);

  useEffect(() => {
    localStorage.setItem('bot_selected_channels', JSON.stringify(selectedChannels));
  }, [selectedChannels]);

  useEffect(() => {
    if (open) {
      void fetchProfiles();
      setSendResult(null);
      
      const cachedBot = localStorage.getItem('bot_selected_profile');
      const initialId = cachedBot !== null && botProfileId === null ? (cachedBot === "default" ? null : Number(cachedBot)) : botProfileId;
      
      setBotProfileId(initialId);
      fetchIdentity(initialId);
      fetchChannels(initialId);
    }
  }, [open]);

  useEffect(() => {
    if (mode === 'edit' && selectedChannels.length === 1) {
      fetchRecentMessages(selectedChannels[0], botProfileId);
    } else {
      setBotMessages([]);
    }
  }, [mode, selectedChannels, botProfileId]);

  const handleBotSelect = (id: number | null) => {
    setBotProfileId(id);
    localStorage.setItem('bot_selected_profile', id === null ? "default" : String(id));
    fetchIdentity(id);
    fetchChannels(id);
    setSelectedChannels([]); // Reset channels on bot change to prevent permission errors
  };

  const fetchIdentity = async (id: number | null) => {
    const key = id === null ? 'default' : String(id);
    if (identities[key]) return; // Skip if already cached

    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "";
      const adminKey = import.meta.env.VITE_ADMIN_API_KEY || "";
      const qs = id ? `?profileId=${id}` : '';
      const res = await fetch(`${baseUrl}/api/send/identity${qs}`, { headers: { "x-admin-key": adminKey } });
      const data = await res.json();
      
      if (data && data.name) {
        const newCache = { ...identities, [key]: data };
        setIdentities(newCache);
        localStorage.setItem('bot_identities_cache', JSON.stringify(newCache));
      }
    } catch (e) {
      console.error("Failed to fetch bot identity", e);
    }
  };

  const fetchChannels = async (id: number | null) => {
    setIsLoading(true);
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "";
      const adminKey = import.meta.env.VITE_ADMIN_API_KEY || "";
      const qs = id ? `?profileId=${id}` : '';
      const res = await fetch(`${baseUrl}/api/send/channels${qs}`, { headers: { "x-admin-key": adminKey } });
      const data = await res.json();
      if (Array.isArray(data)) setChannels(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchRecentMessages = async (cId: string, profileId: number | null) => {
    setIsLoadingMessages(true);
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "";
      const adminKey = import.meta.env.VITE_ADMIN_API_KEY || "";
      const qs = profileId ? `?profileId=${profileId}` : '';
      const res = await fetch(`${baseUrl}/api/send/channels/${cId}/messages${qs}`, { headers: { "x-admin-key": adminKey } });
      const data = await res.json();
      if (Array.isArray(data)) setBotMessages(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoadingMessages(false);
    }
  };

  const toggleChannel = (id: string) => {
    if (mode === 'edit') {
      setSelectedChannels([id]); 
    } else {
      setSelectedChannels((prev) => prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]);
    }
  };

  const handleDispatch = async () => {
    if (selectedChannels.length === 0) return;
    if (mode === 'edit' && !targetMessageId) return;

    setIsSending(true);
    setSendResult(null);
    try {
      const payload = useMessageStore.getState().getPayload();
      const flows = useActionStore.getState().toRegistrations();
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "";
      const adminKey = import.meta.env.VITE_ADMIN_API_KEY || "";

      let successCount = 0;
      for (const cId of selectedChannels) {
        const res = await fetch(`${baseUrl}/api/send`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "x-admin-key": adminKey },
          body: JSON.stringify({
            mode: "bot",
            payload,
            channelId: cId,
            profileId: botProfileId,
            flows,
            editMessageId: mode === 'edit' ? targetMessageId : undefined
          }),
        });
        if (res.ok) successCount++;
      }
      setSendResult(`Successfully ${mode === 'edit' ? 'updated message' : `dispatched to ${successCount} channel(s)`}.`);
      if (successCount === selectedChannels.length) {
        setTimeout(() => onClose(), 2000);
      }
    } catch (e) {
      setSendResult("An error occurred while communicating with the server.");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={`Dispatch via Bot`} width="max-w-2xl">
      <div className="flex flex-col" style={{ maxHeight: 'calc(100vh - 120px)' }}>
        
        <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 flex flex-col gap-6 min-h-0">
          
          <div className="flex bg-[#1e1f22] p-1 rounded-md border border-[#111214] shrink-0 mt-1">
            <button onClick={() => setMode('send')} className={`flex-1 flex items-center justify-center gap-2 py-1.5 rounded text-[11px] font-bold uppercase transition-all ${mode === 'send' ? 'bg-[#5865f2] text-white shadow-sm' : 'text-[#b5bac1] hover:bg-[#2b2d31]'}`}>
              <Send size={14} /> Send New Message
            </button>
            <button onClick={() => setMode('edit')} className={`flex-1 flex items-center justify-center gap-2 py-1.5 rounded text-[11px] font-bold uppercase transition-all ${mode === 'edit' ? 'bg-[#faa61a] text-white shadow-sm' : 'text-[#b5bac1] hover:bg-[#2b2d31]'}`}>
              <Edit3 size={14} /> Edit Existing
            </button>
          </div>

          <div>
            <div className="flex justify-between items-end mb-2">
              <h4 className="text-[12px] font-bold text-[#b5bac1] uppercase">1. Select Bot Identity</h4>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 shrink-0">
              
              {/* Default Token */}
              <div onClick={() => handleBotSelect(null)} className={`p-3 rounded-lg border cursor-pointer flex items-center gap-3 transition-all ${botProfileId === null ? 'border-[#5865f2] bg-[#5865f2]/10' : 'border-[#1e1f22] bg-[#1e1f22] hover:border-[#35373c]'}`}>
                {identities['default']?.avatar ? (
                  <img src={identities['default'].avatar} alt="Bot" className="w-10 h-10 rounded-full shadow-sm object-cover" />
                ) : (
                  <div className="w-10 h-10 rounded-full bg-[#5865f2] flex items-center justify-center text-white shrink-0 shadow-sm"><Server size={20} /></div>
                )}
                <div className="min-w-0">
                  <p className="text-[14px] font-bold text-white truncate">{identities['default'] ? identities['default'].name : "Server Default"}</p>
                  <p className="text-[11px] text-[#949ba4] truncate">Uses primary .env token</p>
                </div>
              </div>
              
              {/* Database Profiles */}
              {botProfiles.map(p => {
                const iden = identities[String(p.id)];
                return (
                  <div key={p.id} onClick={() => handleBotSelect(p.id)} className={`p-3 rounded-lg border cursor-pointer flex items-center gap-3 transition-all ${botProfileId === p.id ? 'border-[#5865f2] bg-[#5865f2]/10' : 'border-[#1e1f22] bg-[#1e1f22] hover:border-[#35373c]'}`}>
                    {iden?.avatar ? (
                      <img src={iden.avatar} alt="Bot" className="w-10 h-10 rounded-full shadow-sm object-cover" />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-[#23a559] flex items-center justify-center text-white shrink-0 shadow-sm overflow-hidden">
                         <Bot size={20} />
                      </div>
                    )}
                    <div className="min-w-0">
                      <p className="text-[14px] font-bold text-white truncate">{iden ? iden.name : p.name}</p>
                      <p className="text-[11px] text-[#949ba4] truncate">ID: {p.application_id || 'Custom'}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div>
            <div className="flex justify-between items-end mb-2">
              <h4 className="text-[12px] font-bold text-[#b5bac1] uppercase">2. Select Target Channel{mode === 'send' ? 's' : ''}</h4>
              {mode === 'send' && (
                <div className="flex gap-3">
                  <button onClick={() => setSelectedChannels(channels.map(c => c.id))} className="text-[11px] font-bold text-[#5865f2] hover:underline uppercase tracking-wide">Select All</button>
                  <button onClick={() => setSelectedChannels([])} className="text-[11px] font-bold text-[#f28b8b] hover:underline uppercase tracking-wide">Clear</button>
                </div>
              )}
            </div>
            
            <div className="bg-[#1e1f22] border border-[#111214] rounded-lg p-2 max-h-48 overflow-y-auto custom-scrollbar shrink-0">
              {isLoading ? (
                <div className="flex h-16 items-center justify-center text-sm text-[#949ba4]">Fetching channels...</div>
              ) : channels.length === 0 ? (
                <div className="flex h-16 items-center justify-center text-sm text-[#949ba4]">No channels found.</div>
              ) : (
                <div className="flex flex-col gap-1">
                  {channels.map((c) => {
                    const isChecked = selectedChannels.includes(c.id);
                    return (
                      <div key={c.id} onClick={() => toggleChannel(c.id)} className={`flex items-center gap-3 p-2 rounded cursor-pointer transition-colors ${isChecked ? 'bg-[#35373c]' : 'hover:bg-[#2b2d31]'}`}>
                        {isChecked ? <CheckSquare size={16} className="text-[#5865f2]" /> : <Square size={16} className="text-[#949ba4]" />}
                        <span className={`text-[13px] font-medium ${isChecked ? 'text-white' : 'text-[#dbdee1]'}`}># {c.name}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {mode === 'edit' && (
            <div className="bg-[#2b2d31] rounded-lg shrink-0 pb-2">
              <h4 className="text-[12px] font-bold text-[#b5bac1] uppercase mb-2">3. Select Message to Edit</h4>
              <div className="flex flex-col sm:flex-row gap-2 items-start">
                <div className="flex-1 w-full">
                  <Select
                    value={targetMessageId}
                    onChange={(e) => setTargetMessageId(e.target.value)}
                    options={
                      isLoadingMessages ? [{ value: "", label: "Fetching recent messages..." }]
                      : botMessages.length === 0 ? [{ value: "", label: "No recent messages found." }]
                      : [{ value: "", label: "Select a message..." }, ...botMessages.map(m => ({ value: m.id, label: `${m.content.substring(0, 30)} (${m.id})` }))]
                    }
                  />
                </div>
                <div className="flex-1 w-full">
                  <TextField
                    value={targetMessageId}
                    placeholder="Or paste Message ID/Link"
                    onChange={(e) => {
                      const val = e.target.value;
                      const urlMatch = val.match(/\/channels\/\d+\/\d+\/(\d+)/);
                      setTargetMessageId(urlMatch ? urlMatch[1] : val);
                    }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between border-t border-[#1e1f22] pt-4 mt-2 shrink-0 bg-[#313338]">
          <div className="text-[12px] font-medium text-[#23a559] truncate pr-4">{sendResult && sendResult}</div>
          <div className="flex gap-2 ml-auto shrink-0">
            <Button variant="secondary" onClick={onClose} className="bg-[#1e1f22] text-[#b5bac1] hover:text-white border-[#111214]">Cancel</Button>
            <Button 
              className={`${mode === 'edit' ? 'bg-[#faa61a] hover:bg-[#e09415]' : 'bg-[#5865f2] hover:bg-[#4752c4]'} text-white border-none flex items-center gap-2`} 
              onClick={handleDispatch}
              loading={isSending}
              disabled={selectedChannels.length === 0 || isSending || (mode === 'edit' && !targetMessageId)}
            >
              {mode === 'edit' ? <><Edit3 size={16} /> Update Message</> : <><Send size={16} /> Dispatch to {selectedChannels.length}</>}
            </Button>
          </div>
        </div>

      </div>
    </Modal>
  );
};
```

### File: `client/src/components/ui/Button.tsx`
```tsx
import type { ButtonHTMLAttributes, ReactNode } from "react";
import type { IconComponent } from "./icon";

/**
 * Button.
 *
 * One component with variants rather than several near-identical ones, so the
 * look stays consistent everywhere. The styling mirrors Discohook's own Button:
 * rounded-lg, ~32px tall, a hairline light border, and blurple as the only
 * saturated accent.
 */

const BASE =
  "relative inline-flex items-center justify-center gap-1.5 border border-white/[0.08] rounded-lg font-medium transition shrink-0 disabled:cursor-not-allowed disabled:opacity-50";

const VARIANTS = {
  primary: "bg-blurple-500 hover:bg-blurple-600 active:bg-blurple-700 text-white",
  secondary:
    "bg-[#97979f1f] hover:bg-[#97979f33] active:bg-[#50505a4d] text-[#ebebed] border-[#97979f0a]",
  success: "bg-[#00863a] hover:bg-[#047e37] active:bg-[#057332] text-white",
  danger: "bg-[#d22d39] hover:bg-[#b42831] active:bg-[#a4232c] text-white",
  ghost: "border-transparent bg-transparent text-ink-muted hover:bg-hover hover:text-ink",
  outline: "border-line bg-transparent text-ink hover:bg-hover",
} as const;

export type ButtonVariant = keyof typeof VARIANTS;

const SIZES = {
  sm: "h-7 px-2.5 text-xs min-w-[44px]",
  md: "h-8 px-4 text-sm min-w-[60px]",
  lg: "h-9 px-5 text-sm min-w-[60px]",
} as const;

export type ButtonSize = keyof typeof SIZES;

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  icon?: IconComponent;
  children?: ReactNode;
}

export const Button = ({
  children,
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  icon: Icon,
  className = "",
  type = "button",
  ...props
}: ButtonProps) => (
  <button
    type={type}
    disabled={disabled || loading}
    className={[BASE, VARIANTS[variant], SIZES[size], className].join(" ")}
    {...props}
  >
    {loading ? (
      <span
        className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent"
        aria-hidden="true"
      />
    ) : (
      Icon && <Icon size={size === "sm" ? 13 : 15} aria-hidden="true" />
    )}
    {children}
  </button>
);

export interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon: IconComponent;
  label: string;
  variant?: ButtonVariant;
  size?: number;
}

/** Square icon-only button, for toolbars and list rows. */
export const IconButton = ({
  icon: Icon,
  label,
  variant = "ghost",
  size = 15,
  className = "",
  ...props
}: IconButtonProps) => (
  <button
    type="button"
    title={label}
    aria-label={label}
    className={[
      "inline-flex items-center justify-center rounded-lg p-1.5 transition-colors",
      "disabled:cursor-not-allowed disabled:opacity-40",
      VARIANTS[variant],
      className,
    ].join(" ")}
    {...props}
  >
    <Icon size={size} aria-hidden="true" />
  </button>
);

export default Button;

```

### File: `client/src/components/ui/ColorPicker.tsx`
```tsx
import { Check } from "lucide-react";
import { EMBED_COLOR_PRESETS } from "../../utils/constants";
import { decimalToHex, parseHexColor } from "../../utils/discord";

/**
 * Colour picker for embed/container accents.
 *
 * Discord stores colours as a 24-bit integer, which nobody wants to type. This
 * exposes presets plus a native colour input, and keeps the decimal value as the
 * source of truth so nothing needs converting at send time.
 *
 * The hex text field only commits once the input is a valid 6-digit colour, so
 * a half-typed value never blanks the accent.
 */
export interface ColorPickerProps {
  label?: string;
  value: number | null;
  onChange: (value: number | null) => void;
  allowClear?: boolean;
}

export const ColorPicker = ({
  label = "Colour",
  value,
  onChange,
  allowClear = true,
}: ColorPickerProps) => {
  const hex = value == null ? "#000000" : decimalToHex(value);

  return (
    <div>
      <span className="field-label">{label}</span>

      <div className="flex flex-wrap items-center gap-1.5">
        {EMBED_COLOR_PRESETS.map((preset) => (
          <button
            key={preset.name}
            type="button"
            title={preset.name}
            aria-label={preset.name}
            onClick={() => onChange(preset.value)}
            style={{ backgroundColor: decimalToHex(preset.value) }}
            className="flex h-6 w-6 items-center justify-center rounded-full ring-1 ring-black/30 transition-transform hover:scale-110"
          >
            {value === preset.value && <Check size={12} className="text-white drop-shadow" />}
          </button>
        ))}

        <input
          type="color"
          aria-label="Custom colour"
          value={hex}
          onChange={(event) => onChange(parseHexColor(event.target.value) ?? null)}
          className="h-6 w-6 cursor-pointer rounded border-0 bg-transparent p-0"
        />

        {allowClear && (
          <button
            type="button"
            onClick={() => onChange(null)}
            className="rounded px-2 py-1 text-[11px] text-ink-muted hover:bg-hover hover:text-ink"
          >
            None
          </button>
        )}
      </div>

      <div className="mt-1.5 flex items-center gap-2">
        <input
          className="field !w-28 font-mono"
          value={value == null ? "" : decimalToHex(value)}
          placeholder="#5865f2"
          onChange={(event) => {
            const parsed = parseHexColor(event.target.value);
            if (parsed !== null) onChange(parsed);
          }}
        />
        <span className="font-mono text-[11px] text-ink-faint">
          {value == null ? "no accent" : `0x${value.toString(16)}`}
        </span>
      </div>
    </div>
  );
};

export default ColorPicker;

```

### File: `client/src/components/ui/Field.tsx`
```tsx
import { Check } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { createPortal } from "react-dom";
import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";

export const VARIABLES = [
  { group: "User / Clicker" },
  { tag: "{user.mention}", label: "@ada", desc: "Mentions the user who clicked" },
  { tag: "{user.name}", label: "ada", desc: "The user's exact username" },
  { tag: "{user.displayname}", label: "Ada L.", desc: "Server nickname or global name" },
  { tag: "{user.id}", label: "123456789", desc: "The user's numeric ID" },
  { tag: "{user.avatar}", label: "https://...", desc: "Link to user's profile picture" },
  { tag: "{user.created}", label: "Oct 24, 2015", desc: "When the account was created" },
  { tag: "{user.joined}", label: "2 years ago", desc: "When they joined the server" },
  
  { group: "Server" },
  { tag: "{server.name}", label: "Discohook", desc: "The server's name" },
  { tag: "{server.id}", label: "987654321", desc: "ID of the current server" },
  { tag: "{server.icon}", label: "https://...", desc: "The server's icon URL" },
  { tag: "{server.members}", label: "1542", desc: "Total server member count" },
  { tag: "{server.boosts}", label: "14", desc: "Number of server boosts" },
  
  { group: "Channel & Bot" },
  { tag: "{channel.mention}", label: "#general", desc: "Mentions the current channel" },
  { tag: "{channel.name}", label: "general", desc: "Name of the channel" },
  { tag: "{channel.id}", label: "456789123", desc: "ID of the current channel" },
  { tag: "{bot.mention}", label: "@Bot", desc: "Mentions the bot" },
  { tag: "{bot.id}", label: "11223344", desc: "The bot's ID" },

  { group: "Time & Date" },
  { tag: "{now}", label: "12:00 PM", desc: "Current time (Dynamic to reader)" },
  { tag: "{now.relative}", label: "2 mins ago", desc: "Relative time (Dynamic to reader)" },
  { tag: "{now.long}", label: "Tuesday, Oct 24", desc: "Long format date (Dynamic)" },
  { tag: "{now.unix}", label: "1698144000", desc: "Raw Unix timestamp number" },
];

const VariablePicker = ({ onSelect }: { onSelect: (tag: string) => void }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [coords, setCoords] = useState({ top: 0, left: 0 });
  const buttonRef = useRef<HTMLButtonElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

const toggleDropdown = () => {
    if (!isOpen && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      const dropWidth = 256; // 64rem (w-64 in Tailwind)
      const dropHeight = 300; // max-h constraint
      
      // Calculate Top/Bottom
      let top = rect.bottom + 4;
      if (top + dropHeight > window.innerHeight) {
        top = rect.top - dropHeight - 4; // Flip upwards if too close to bottom
      }
      
      // Calculate Left/Right with STRICT screen edge clamping
      let left = rect.right - dropWidth;
      
      // FIX: If the left coordinate is less than 10px from the screen edge, force it to 10px!
      if (left < 10) {
        left = 10;
      }
      // If the right edge bleeds off the screen, pin it to the right edge
      if (left + dropWidth > window.innerWidth) {
        left = window.innerWidth - dropWidth - 10;
      }
      
      setCoords({ top, left });
    }
    setIsOpen(!isOpen);
  };

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node) &&
          buttonRef.current && !buttonRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    
    const handleScroll = (e: Event) => {
      if (dropdownRef.current && dropdownRef.current.contains(e.target as Node)) return;
      setIsOpen(false);
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      window.addEventListener("scroll", handleScroll, true);
    }
    
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      window.removeEventListener("scroll", handleScroll, true);
    };
  }, [isOpen]);

  return (
    <>
      <button ref={buttonRef} type="button" onClick={toggleDropdown} className="absolute right-2 top-1.5 z-10 flex h-[22px] items-center justify-center rounded bg-[#2b2d31] px-2 text-[11px] font-mono font-bold text-[#b5bac1] hover:bg-[#5865f2] hover:text-white transition-colors border border-[#1e1f22] shadow-sm" title="Insert Variable">
        {"{ }"}
      </button>
      
      {isOpen && createPortal(
        <div ref={dropdownRef} style={{ top: coords.top, left: coords.left }} className="fixed w-64 rounded-md border border-[#1e1f22] bg-[#2b2d31] shadow-2xl z-[99999] overflow-hidden flex flex-col max-h-[300px]">
          <div className="p-2 border-b border-[#1e1f22] shrink-0 bg-[#2b2d31]">
            <p className="text-[11px] font-bold uppercase text-[#b5bac1] tracking-wider mb-1">Search Variables</p>
            <p className="text-[10px] text-[#949ba4]">Filled in dynamically on click.</p>
          </div>
          <div className="flex-1 overflow-y-auto custom-scrollbar p-1">
            {VARIABLES.map((v, i) => v.group ? (
              <div key={`group-${i}`} className="px-2 pt-3 pb-1 text-[10px] font-bold uppercase text-[#949ba4] tracking-wider border-b border-[#1e1f22]/50 mb-1 mt-1 first:mt-0">{v.group}</div>
            ) : (
              <button key={v.tag} type="button" onClick={() => { onSelect(v.tag!); setIsOpen(false); }} className="flex flex-col items-start justify-center rounded px-2 py-1.5 w-full hover:bg-[#5865f2] hover:text-white group transition-colors text-left mb-0.5">
                <div className="flex w-full items-baseline justify-between">
                  <span className="font-mono text-[11px] font-bold text-[#5865f2] group-hover:text-white">{v.tag}</span>
                  <span className="text-[10px] text-[#949ba4] group-hover:text-indigo-200">{v.label}</span>
                </div>
                <span className="text-[10px] text-[#b5bac1] group-hover:text-indigo-100 line-clamp-1">{v.desc}</span>
              </button>
            ))}
          </div>
        </div>,
        document.body
      )}
    </>
  );
};

interface FieldShellProps { label?: ReactNode; hint?: ReactNode; counterValue?: string; limit?: number; className?: string; children: ReactNode; }

const FieldShell = ({ label, hint, counterValue = "", limit, className = "", children }: FieldShellProps) => (
  <label className={`block ${className}`}>
    {(label !== undefined || limit !== undefined) && (
      <span className="mb-1 flex items-baseline justify-between gap-2">
        <span className="field-label !mb-0">{label}</span>
        {limit !== undefined && <span className={`text-[11px] italic tabular-nums font-medium ${counterValue.length > limit ? "text-[#da373c]" : counterValue.length / limit >= 0.9 ? "text-[#faa61a]" : "text-[#949ba4]"}`}>{counterValue.length}/{limit}</span>}
      </span>
    )}
    {children}
    {hint && <span className="mt-1 block text-[11px] text-[#949ba4]">{hint}</span>}
  </label>
);

const asText = (value: unknown): string => typeof value === "string" ? value : value == null ? "" : String(value);

export interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> { label?: string; hint?: ReactNode; limit?: number; }

export const TextField = ({ label, hint, limit, className, ...props }: TextFieldProps) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const handleInsertVariable = (tag: string) => {
    const input = inputRef.current;
    if (!input || !props.onChange) return;
    const currentVal = asText(props.value);
    const start = input.selectionStart ?? currentVal.length;
    const end = input.selectionEnd ?? currentVal.length;
    const newVal = currentVal.substring(0, start) + tag + currentVal.substring(end);
    const e = { target: { value: newVal } } as any;
    props.onChange(e);
    setTimeout(() => { input.focus(); input.setSelectionRange(start + tag.length, start + tag.length); }, 0);
  };
  return (
    <FieldShell label={label ?? (limit !== undefined ? label : undefined)} hint={hint} limit={limit} counterValue={asText(props.value)} className={className}>
      <div className="relative w-full">
        <input ref={inputRef} className="field w-full pr-10 bg-[#1e1f22] text-[#dbdee1] border-[#111214] focus:border-[#5865f2] focus:ring-1 focus:ring-[#5865f2]" {...props} />
        <VariablePicker onSelect={handleInsertVariable} />
      </div>
    </FieldShell>
  );
};

export interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> { label?: string; hint?: ReactNode; limit?: number; }

export const TextArea = ({ label, hint, limit, rows = 4, className, ...props }: TextAreaProps) => {
  const textAreaRef = useRef<HTMLTextAreaElement>(null);
  const handleInsertVariable = (tag: string) => {
    const input = textAreaRef.current;
    if (!input || !props.onChange) return;
    const currentVal = asText(props.value);
    const start = input.selectionStart ?? currentVal.length;
    const end = input.selectionEnd ?? currentVal.length;
    const newVal = currentVal.substring(0, start) + tag + currentVal.substring(end);
    const e = { target: { value: newVal } } as any;
    props.onChange(e);
    setTimeout(() => { input.focus(); input.setSelectionRange(start + tag.length, start + tag.length); }, 0);
  };
  return (
    <FieldShell label={label} hint={hint} limit={limit} counterValue={asText(props.value)} className={className}>
      <div className="relative w-full">
        <textarea ref={textAreaRef} rows={rows} className="field resize-y w-full pr-10 bg-[#1e1f22] text-[#dbdee1] border-[#111214] focus:border-[#5865f2] focus:ring-1 focus:ring-[#5865f2] py-2" {...props} />
        <VariablePicker onSelect={handleInsertVariable} />
      </div>
    </FieldShell>
  );
};

export interface SelectOption_ { value: string; label: string; }
export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> { label?: string; hint?: ReactNode; options: readonly SelectOption_[]; }
export const Select = ({ label, hint, options, className, ...props }: SelectProps) => (
  <FieldShell label={label} hint={hint} className={className}>
    <select className="field cursor-pointer w-full bg-[#1e1f22] text-[#dbdee1] border-[#111214] focus:border-[#5865f2] focus:ring-1 focus:ring-[#5865f2]" {...props}>
      {options.map((o) => (<option key={o.value} value={o.value}>{o.label}</option>))}
    </select>
  </FieldShell>
);

export interface CheckboxProps { label?: ReactNode; checked?: boolean; onChange: (checked: boolean) => void; className?: string; }
export const Checkbox = ({ label, checked, onChange, className = "" }: CheckboxProps) => (
  <label className={`flex cursor-pointer items-center gap-2 text-sm font-normal text-[#dbdee1] ${className}`}>
    <input type="checkbox" checked={Boolean(checked)} onChange={(e) => onChange(e.target.checked)} className="peer hidden" />
    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md border border-[#82838A] text-transparent transition-colors peer-checked:border-transparent peer-checked:bg-[#5865f2] peer-checked:text-white"><Check size={16} aria-hidden="true" /></span>
    {label}
  </label>
);
export default TextField;
```

### File: `client/src/components/ui/Modal.tsx`
```tsx
import { useEffect, type ReactNode } from "react";
import { X } from "lucide-react";

/**
 * Modal dialog.
 *
 * Closes on Escape and on backdrop click. `role="dialog"` plus `aria-modal`
 * conveys the state to screen readers, and focus moves to the panel on open so
 * keyboard users are not left behind on the page that opened it.
 */
export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  footer?: ReactNode;
  width?: string;
}

export const Modal = ({
  open,
  onClose,
  title,
  children,
  footer,
  width = "max-w-lg",
}: ModalProps) => {
  useEffect(() => {
    if (!open) return undefined;

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        autoFocus
        tabIndex={-1}
        onClick={(event) => event.stopPropagation()}
        className={`w-full ${width} max-h-[85vh] overflow-hidden rounded-xl border border-line-soft bg-raised shadow-2xl`}
      >
        <div className="flex items-center justify-between border-b border-line-soft px-4 py-3">
          <h2 className="text-base font-semibold text-ink-strong">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="rounded p-1 text-ink-muted hover:bg-hover hover:text-ink"
          >
            <X size={16} />
          </button>
        </div>

        <div className="max-h-[65vh] overflow-y-auto p-4">{children}</div>

        {footer && (
          <div className="flex items-center justify-end gap-2 border-t border-line-soft px-4 py-3">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

export default Modal;

```

### File: `client/src/components/ui/Tabs.tsx`
```tsx
import type { ReactNode } from "react";
import type { IconComponent } from "./icon";

/**
 * Tabs.
 *
 * Purely presentational — the caller owns which tab is active, which keeps this
 * usable for both the sidebar sections and the property panel's context tabs.
 */
export interface TabDef {
  id: string;
  label: string;
  icon?: IconComponent;
  badge?: ReactNode;
}

export interface TabsProps {
  tabs: readonly TabDef[];
  activeId: string;
  onChange: (id: string) => void;
  className?: string;
}

export const Tabs = ({ tabs, activeId, onChange, className = "" }: TabsProps) => (
  <div role="tablist" className={`flex gap-1 border-b border-line-soft ${className}`}>
    {tabs.map((tab) => {
      const active = tab.id === activeId;
      const Icon = tab.icon;
      return (
        <button
          key={tab.id}
          role="tab"
          type="button"
          aria-selected={active}
          onClick={() => onChange(tab.id)}
          className={[
            "relative -mb-px flex items-center gap-1.5 px-3 py-2 text-xs font-semibold transition-colors",
            active
              ? "border-b-2 border-blurple text-ink-strong"
              : "border-b-2 border-transparent text-ink-muted hover:text-ink",
          ].join(" ")}
        >
          {Icon && <Icon size={13} aria-hidden="true" />}
          {tab.label}
          {tab.badge != null && (
            <span className="rounded-full bg-raised px-1.5 text-[10px] text-ink-muted">
              {tab.badge}
            </span>
          )}
        </button>
      );
    })}
  </div>
);

export default Tabs;

```

### File: `client/src/components/ui/icon.ts`
```ts
import type { ComponentType, SVGProps } from "react";

/**
 * The shape of an icon component (anything from `lucide-react`).
 *
 * Declared structurally rather than importing `LucideIcon` by name, so a major
 * version of the icon library that renames its exported type cannot break the
 * build.
 */
export type IconComponent = ComponentType<
  SVGProps<SVGSVGElement> & { size?: number | string }
>;

```

