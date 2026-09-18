"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import Nav from "@/components/Nav";
import LogsPanel from "@/components/LogsPanel";
import TemplateEditor from "@/components/TemplateEditor";
import AddTriggerModal from "@/components/AddTriggerModal";
import * as api from "@/lib/api";
import { useAuth } from "@/lib/auth";
import {
  CHANNELS,
  CHANNEL_LABELS,
  type Channel,
  type Template,
  type Trigger,
} from "@/lib/types";

const CHANNEL_ICON: Record<Channel, string> = {
  whatsapp: "💬",
  email: "✉️",
  webpush: "🔔",
};

export default function AdminPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [triggers, setTriggers] = useState<Trigger[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [editing, setEditing] = useState<{
    trigger: Trigger;
    channel: Channel;
    template: Template | null;
  } | null>(null);
  const [showAdd, setShowAdd] = useState(false);

  useEffect(() => {
    if (!loading && (!user || !user.is_staff)) router.replace("/login");
  }, [loading, user, router]);

  const refresh = useCallback(async () => {
    setLoadingData(true);
    try {
      setTriggers(await api.listTriggers());
    } catch {
      /* ignore */
    } finally {
      setLoadingData(false);
    }
  }, []);

  useEffect(() => {
    if (user?.is_staff) refresh();
  }, [user, refresh]);

  if (loading || !user?.is_staff) {
    return (
      <>
        <Nav />
        <main className="mx-auto max-w-6xl px-4 py-16 text-zinc-500">Loading…</main>
      </>
    );
  }

  function cellTemplate(trigger: Trigger, channel: Channel): Template | null {
    return trigger.templates.find((t) => t.channel === channel) ?? null;
  }

  async function onToggle(template: Template) {
    await api.toggleTemplate(template.id);
    refresh();
  }

  async function onDeleteTrigger(trigger: Trigger) {
    if (
      !window.confirm(
        `Delete the "${trigger.name}" trigger and all its templates? This cannot be undone.`,
      )
    )
      return;
    await api.deleteTrigger(trigger.id);
    refresh();
  }

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-6xl space-y-8 px-4 py-10">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
              Notification Settings
            </h1>
            <p className="mt-1 text-zinc-600">
              Rows are triggers, columns are channels. Each cell is one template.
            </p>
          </div>
          <button onClick={() => setShowAdd(true)} className="btn-primary">
            + Add trigger
          </button>
        </div>

        <section className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] border-collapse text-left text-sm">
              <thead>
                <tr className="border-b border-zinc-200 bg-zinc-50/60">
                  <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-zinc-500">
                    Trigger
                  </th>
                  {CHANNELS.map((ch) => (
                    <th
                      key={ch}
                      className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-zinc-500"
                    >
                      <span className="mr-1.5">{CHANNEL_ICON[ch]}</span>
                      {CHANNEL_LABELS[ch]}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loadingData ? (
                  <tr>
                    <td colSpan={4} className="px-5 py-10 text-center text-zinc-400">
                      Loading…
                    </td>
                  </tr>
                ) : (
                  triggers.map((trigger) => (
                    <tr
                      key={trigger.id}
                      className="border-b border-zinc-100 align-top last:border-0 hover:bg-zinc-50/40"
                    >
                      <td className="px-5 py-4">
                        <div className="font-medium text-zinc-900">{trigger.name}</div>
                        <div className="mt-0.5 font-mono text-xs text-zinc-400">
                          {trigger.slug}
                        </div>
                        <div className="mt-2 flex items-center gap-2">
                          <span
                            className={`badge ${
                              trigger.event_type === "SCHEDULED"
                                ? "bg-violet-50 text-violet-700"
                                : "bg-sky-50 text-sky-700"
                            }`}
                          >
                            {trigger.event_type.toLowerCase()}
                          </span>
                          <button
                            onClick={() => onDeleteTrigger(trigger)}
                            className="text-xs text-zinc-400 hover:text-rose-600"
                            title="Delete trigger"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                      {CHANNELS.map((channel) => {
                        const tpl = cellTemplate(trigger, channel);
                        return (
                          <td key={channel} className="px-5 py-4">
                            <Cell
                              channel={channel}
                              template={tpl}
                              onEdit={() =>
                                setEditing({ trigger, channel, template: tpl })
                              }
                              onToggle={() => tpl && onToggle(tpl)}
                              onTested={refresh}
                            />
                          </td>
                        );
                      })}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        <LogsPanel />
      </main>

      {editing && (
        <TemplateEditor
          trigger={editing.trigger}
          channel={editing.channel}
          template={editing.template}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null);
            refresh();
          }}
        />
      )}

      {showAdd && (
        <AddTriggerModal
          onClose={() => setShowAdd(false)}
          onCreated={() => {
            setShowAdd(false);
            refresh();
          }}
        />
      )}
    </>
  );
}

function Cell({
  channel,
  template,
  onEdit,
  onToggle,
  onTested,
}: {
  channel: Channel;
  template: Template | null;
  onEdit: () => void;
  onToggle: () => void;
  onTested: () => void;
}) {
  const [testMsg, setTestMsg] = useState("");
  const [testing, setTesting] = useState(false);

  if (!template) {
    return (
      <button
        onClick={onEdit}
        className="flex w-full items-center justify-center rounded-lg border border-dashed border-zinc-300 py-3 text-sm text-zinc-500 transition hover:border-zinc-400 hover:text-zinc-700"
      >
        + Create
      </button>
    );
  }

  async function test() {
    const recipient = window.prompt(
      channel === "email"
        ? "Send test email to which address?"
        : channel === "whatsapp"
          ? "Send test WhatsApp to which number? (e.g. +15551234567)"
          : "Web push targets your own subscription. Leave blank and press OK.",
      "",
    );
    if (recipient === null) return;
    setTesting(true);
    setTestMsg("");
    try {
      const res = await api.testSend(template!.id, recipient, {});
      setTestMsg(
        res.status === "sent"
          ? "✓ sent"
          : `${res.status}${res.error ? ": " + res.error : ""}`,
      );
    } catch (err) {
      setTestMsg(err instanceof Error ? err.message : "failed");
    } finally {
      setTesting(false);
      onTested();
    }
  }

  return (
    <div className="space-y-2.5">
      <span
        className={`badge ${
          template.is_enabled
            ? "bg-emerald-50 text-emerald-700"
            : "bg-zinc-100 text-zinc-500"
        }`}
      >
        <span
          className={`mr-1.5 inline-block h-1.5 w-1.5 rounded-full ${
            template.is_enabled ? "bg-emerald-500" : "bg-zinc-400"
          }`}
        />
        {template.is_enabled ? "On" : "Off"}
      </span>
      <p className="line-clamp-2 text-xs leading-relaxed text-zinc-500">
        {template.body || (channel === "email" && template.subject) || "—"}
      </p>
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs">
        <button onClick={onEdit} className="font-medium text-zinc-900 hover:underline">
          Edit
        </button>
        <button onClick={onToggle} className="text-zinc-500 hover:text-zinc-900">
          {template.is_enabled ? "Turn off" : "Turn on"}
        </button>
        <button
          onClick={test}
          disabled={testing}
          className="text-zinc-500 hover:text-zinc-900 disabled:opacity-50"
        >
          {testing ? "Testing…" : "Test"}
        </button>
      </div>
      {testMsg && <p className="text-xs text-zinc-500">{testMsg}</p>}
    </div>
  );
}
