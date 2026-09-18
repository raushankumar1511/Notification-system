"use client";

import { useState } from "react";
import { ApiError } from "@/lib/api";
import * as api from "@/lib/api";
import { CHANNEL_LABELS, type Channel, type Template, type Trigger } from "@/lib/types";

interface Props {
  trigger: Trigger;
  channel: Channel;
  template: Template | null;
  onClose: () => void;
  onSaved: () => void;
}

type Errors = Record<string, string>;

function variablesToText(vars: Record<string, string>): string {
  return Object.entries(vars || {})
    .map(([k, v]) => `${k}=${v}`)
    .join("\n");
}

function textToVariables(text: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const line of text.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    const idx = trimmed.indexOf("=");
    if (idx === -1) out[trimmed] = "";
    else out[trimmed.slice(0, idx).trim()] = trimmed.slice(idx + 1).trim();
  }
  return out;
}

export default function TemplateEditor({
  trigger,
  channel,
  template,
  onClose,
  onSaved,
}: Props) {
  const cfg = (template?.provider_config ?? {}) as Record<string, string>;
  const [subject, setSubject] = useState(template?.subject ?? "");
  const [title, setTitle] = useState(template?.title ?? "");
  const [body, setBody] = useState(template?.body ?? "");
  const [varsText, setVarsText] = useState(variablesToText(template?.variables ?? {}));
  const [waName, setWaName] = useState(cfg.template_name ?? "");
  const [waLang, setWaLang] = useState(cfg.language_code ?? "en_US");
  const [waParams, setWaParams] = useState(
    Array.isArray(cfg.param_map) ? (cfg.param_map as string[]).join(", ") : "",
  );
  const [pushUrl, setPushUrl] = useState(cfg.url ?? "");

  const [errors, setErrors] = useState<Errors>({});
  const [formError, setFormError] = useState("");
  const [busy, setBusy] = useState(false);

  function validate(): Errors {
    const e: Errors = {};
    if (channel === "email") {
      if (!subject.trim()) e.subject = "Subject is required.";
      if (!body.trim()) e.body = "Body is required.";
    } else if (channel === "webpush") {
      if (!title.trim()) e.title = "Title is required.";
      if (!body.trim()) e.body = "Body is required.";
    } else if (channel === "whatsapp") {
      if (!waName.trim()) e.provider_config = "An approved template name is required.";
    }
    return e;
  }

  async function save() {
    const clientErrors = validate();
    setErrors(clientErrors);
    setFormError("");
    if (Object.keys(clientErrors).length > 0) return;

    setBusy(true);
    const provider_config: Record<string, unknown> = {};
    if (channel === "whatsapp") {
      provider_config.template_name = waName.trim();
      provider_config.language_code = waLang.trim() || "en_US";
      provider_config.param_map = waParams
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
    }
    if (channel === "webpush" && pushUrl.trim()) {
      provider_config.url = pushUrl.trim();
    }
    const payload: Partial<Template> = {
      trigger: trigger.id,
      channel,
      subject,
      title,
      body,
      variables: textToVariables(varsText),
      provider_config,
    };
    try {
      if (template) await api.updateTemplate(template.id, payload);
      else await api.createTemplate(payload);
      onSaved();
    } catch (err) {
      if (err instanceof ApiError && err.data && typeof err.data === "object") {
        const data = err.data as Record<string, unknown>;
        const mapped: Errors = {};
        let general = "";
        for (const [k, v] of Object.entries(data)) {
          const text = Array.isArray(v) ? v.join(" ") : String(v);
          if (k === "non_field_errors" || k === "detail") general = text;
          else mapped[k] = text;
        }
        setErrors(mapped);
        setFormError(general);
        if (!general && Object.keys(mapped).length === 0) {
          setFormError(err.message);
        }
      } else {
        setFormError(err instanceof Error ? err.message : "Save failed");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-zinc-900/40 p-4 backdrop-blur-sm">
      <div className="card my-8 w-full max-w-lg p-6 shadow-xl">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold tracking-tight text-zinc-900">
              {template ? "Edit" : "Create"} template
            </h2>
            <p className="text-sm text-zinc-500">
              {trigger.name} · {CHANNEL_LABELS[channel]}
            </p>
          </div>
          <button onClick={onClose} className="btn-ghost -mr-2 -mt-1 px-2">
            ✕
          </button>
        </div>

        <div className="mt-5 space-y-4">
          {channel === "whatsapp" && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs leading-relaxed text-amber-800">
              WhatsApp business-initiated messages must use a{" "}
              <b>Meta-approved template</b>. Enter the approved template name + language +
              the variables (in order) that fill its <code>{"{{1}}, {{2}}"}</code> params.
              The body below is a preview only.
            </div>
          )}

          {channel === "email" && (
            <Field label="Subject" error={errors.subject}>
              <input
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className={`input ${errors.subject ? "input-error" : ""}`}
                placeholder="Welcome back, {{name}}!"
              />
            </Field>
          )}

          {channel === "webpush" && (
            <>
              <Field label="Title" error={errors.title}>
                <input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className={`input ${errors.title ? "input-error" : ""}`}
                  placeholder="Welcome back!"
                />
              </Field>
              <Field label="Open URL (optional)">
                <input
                  value={pushUrl}
                  onChange={(e) => setPushUrl(e.target.value)}
                  className="input"
                  placeholder="https://…"
                />
              </Field>
            </>
          )}

          {channel === "whatsapp" && (
            <>
              <Field label="Approved template name" error={errors.provider_config}>
                <input
                  value={waName}
                  onChange={(e) => setWaName(e.target.value)}
                  className={`input ${errors.provider_config ? "input-error" : ""}`}
                  placeholder="e.g. hello_world"
                />
              </Field>
              <Field label="Language code">
                <input
                  value={waLang}
                  onChange={(e) => setWaLang(e.target.value)}
                  className="input"
                  placeholder="en_US"
                />
              </Field>
              <Field label="Param map (variable names in order, comma-separated)">
                <input
                  value={waParams}
                  onChange={(e) => setWaParams(e.target.value)}
                  className="input"
                  placeholder="name, day"
                />
              </Field>
            </>
          )}

          <Field
            label={channel === "whatsapp" ? "Body (preview only)" : "Body — supports {{variables}}"}
            error={errors.body}
          >
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              rows={4}
              className={`input ${errors.body ? "input-error" : ""}`}
              placeholder="Hi {{name}}, welcome back!"
            />
          </Field>

          <Field label="Variables (one per line, name=sample value)">
            <textarea
              value={varsText}
              onChange={(e) => setVarsText(e.target.value)}
              rows={3}
              className="input font-mono text-xs"
              placeholder={"name=Jane\nday=Monday"}
            />
          </Field>

          {formError && (
            <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">
              {formError}
            </p>
          )}
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button onClick={save} disabled={busy} className="btn-primary">
            {busy ? "Saving…" : "Save template"}
          </button>
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="label">{label}</label>
      {children}
      {error && <p className="field-error">{error}</p>}
    </div>
  );
}
