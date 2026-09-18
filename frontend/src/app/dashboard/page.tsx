"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Nav from "@/components/Nav";
import * as api from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { initOneSignal, subscribeWebPush, isPushSupported } from "@/lib/onesignal";
import { CHANNEL_LABELS, type Channel } from "@/lib/types";

type FireResult = { channel: string; status: string; error: string };

export default function DashboardPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [results, setResults] = useState<FireResult[]>([]);
  const [msg, setMsg] = useState("");
  const [pushMsg, setPushMsg] = useState("");

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  useEffect(() => {
    if (user) initOneSignal(user.id).catch(() => {});
  }, [user]);

  if (loading || !user) {
    return (
      <>
        <Nav />
        <main className="mx-auto max-w-3xl px-4 py-16 text-zinc-500">Loading…</main>
      </>
    );
  }

  async function fire(slug: string, label: string) {
    setMsg(`Firing "${label}"…`);
    setResults([]);
    try {
      const res = await api.fireEvent(slug);
      setResults(res.sent);
      setMsg(
        res.sent.length
          ? `Fired "${label}" — ${res.sent.length} channel(s) attempted.`
          : `Fired "${label}", but no channels are enabled for it yet.`,
      );
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Failed to fire trigger");
    }
  }

  async function enablePush() {
    setPushMsg("Requesting permission…");
    try {
      await subscribeWebPush();
      setPushMsg("Subscribed. Web Push sends will now arrive in this browser.");
    } catch {
      setPushMsg("Could not subscribe — check browser permissions / OneSignal config.");
    }
  }

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-3xl space-y-6 px-4 py-10">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
            Welcome, {user.username || user.email}
          </h1>
          <p className="mt-1 text-zinc-600">
            Trigger events below. Enabled channels send using the templates configured
            in the admin panel.
          </p>
        </div>

        <section className="card p-6">
          <h2 className="font-semibold text-zinc-900">Fire a trigger</h2>
          <p className="mt-1 text-sm text-zinc-500">
            Login already fired when you signed in. Log out from the top bar to fire
            Logout.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <button onClick={() => fire("order_placed", "Order placed")} className="btn-primary">
              🛒 Place an order
            </button>
            <button onClick={() => fire("password_reset", "Password reset")} className="btn-secondary">
              🔑 Request password reset
            </button>
          </div>
          {msg && <p className="mt-4 text-sm text-zinc-700">{msg}</p>}
          {results.length > 0 && (
            <ul className="mt-3 divide-y divide-zinc-100 rounded-lg border border-zinc-100">
              {results.map((r, i) => (
                <li key={i} className="flex items-center gap-2 px-3 py-2 text-sm">
                  <StatusDot status={r.status} />
                  <span className="font-medium text-zinc-800">
                    {CHANNEL_LABELS[r.channel as Channel] ?? r.channel}
                  </span>
                  <span className="text-zinc-500">— {r.status}</span>
                  {r.error && (
                    <span className="truncate text-xs text-rose-500">({r.error})</span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="card p-6">
          <h2 className="font-semibold text-zinc-900">Web Push</h2>
          <p className="mt-1 text-sm text-zinc-500">
            Subscribe this browser to receive Web Push notifications. Requires HTTPS
            (works on the deployed site).
          </p>
          <button onClick={enablePush} disabled={!isPushSupported()} className="btn-primary mt-4">
            Enable web push
          </button>
          {!isPushSupported() && (
            <p className="mt-2 text-sm text-amber-600">
              This browser does not support web push.
            </p>
          )}
          {pushMsg && <p className="mt-3 text-sm text-zinc-700">{pushMsg}</p>}
        </section>
      </main>
    </>
  );
}

function StatusDot({ status }: { status: string }) {
  const color =
    status === "sent"
      ? "bg-emerald-500"
      : status === "failed"
        ? "bg-rose-500"
        : "bg-amber-400";
  return <span className={`inline-block h-2 w-2 rounded-full ${color}`} />;
}
