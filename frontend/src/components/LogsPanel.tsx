"use client";

import { useCallback, useEffect, useState } from "react";
import * as api from "@/lib/api";
import { CHANNEL_LABELS, type Channel, type NotificationLog } from "@/lib/types";

export default function LogsPanel() {
  const [logs, setLogs] = useState<NotificationLog[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setLogs(await api.listLogs());
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <section className="card p-6">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-zinc-900">Recent notifications</h2>
        <button onClick={refresh} className="btn-secondary">
          Refresh
        </button>
      </div>
      {loading ? (
        <p className="mt-4 text-sm text-zinc-500">Loading…</p>
      ) : logs.length === 0 ? (
        <div className="mt-6 rounded-lg border border-dashed border-zinc-200 py-10 text-center text-sm text-zinc-400">
          No notifications yet. Fire a trigger or test-send a template.
        </div>
      ) : (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wide text-zinc-400">
              <tr className="border-b border-zinc-100">
                <th className="py-2 pr-4 font-semibold">Time</th>
                <th className="py-2 pr-4 font-semibold">Trigger</th>
                <th className="py-2 pr-4 font-semibold">Channel</th>
                <th className="py-2 pr-4 font-semibold">Recipient</th>
                <th className="py-2 pr-4 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="border-b border-zinc-50 last:border-0">
                  <td className="py-2.5 pr-4 text-zinc-500">
                    {new Date(log.created_at).toLocaleTimeString()}
                  </td>
                  <td className="py-2.5 pr-4 text-zinc-800">
                    {log.trigger_slug}
                    {log.is_test && (
                      <span className="badge ml-1.5 bg-zinc-100 text-zinc-500">test</span>
                    )}
                  </td>
                  <td className="py-2.5 pr-4 text-zinc-600">
                    {CHANNEL_LABELS[log.channel as Channel] ?? log.channel}
                  </td>
                  <td className="py-2.5 pr-4 text-zinc-600">{log.recipient || "—"}</td>
                  <td className="py-2.5 pr-4">
                    <StatusBadge status={log.status} error={log.error} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function StatusBadge({ status, error }: { status: string; error: string }) {
  const map: Record<string, string> = {
    sent: "bg-emerald-50 text-emerald-700",
    failed: "bg-rose-50 text-rose-700",
    skipped: "bg-amber-50 text-amber-700",
  };
  return (
    <span
      title={error || undefined}
      className={`badge ${map[status] ?? "bg-zinc-100 text-zinc-600"}`}
    >
      {status}
    </span>
  );
}
