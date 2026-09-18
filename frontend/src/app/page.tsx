"use client";

import Link from "next/link";
import Nav from "@/components/Nav";
import { useAuth } from "@/lib/auth";

const CHANNELS = [
  { icon: "💬", name: "WhatsApp", desc: "Cloud API with approved templates." },
  { icon: "✉️", name: "Email", desc: "Transactional email via Resend." },
  { icon: "🔔", name: "Web Push", desc: "Browser notifications, no app needed." },
];

export default function Home() {
  const { user } = useAuth();
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-5xl px-4">
        {/* Hero */}
        <section className="py-20 text-center sm:py-28">
          <span className="badge border border-zinc-200 bg-white text-zinc-600">
            Triggers × Channels, one grid
          </span>
          <h1 className="mx-auto mt-5 max-w-3xl text-4xl font-semibold tracking-tight text-zinc-900 sm:text-5xl">
            One screen for every notification
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-zinc-600">
            Manage templates for every trigger across WhatsApp, Email, and Web Push —
            all from a single admin grid. No jumping between provider dashboards.
          </p>
          <div className="mt-8 flex justify-center gap-3">
            {user ? (
              <Link href={user.is_staff ? "/admin" : "/dashboard"} className="btn-primary">
                {user.is_staff ? "Open admin" : "Go to dashboard"}
              </Link>
            ) : (
              <>
                <Link href="/register" className="btn-primary">
                  Get started
                </Link>
                <Link href="/login" className="btn-secondary">
                  Log in
                </Link>
              </>
            )}
          </div>
        </section>

        {/* Channels */}
        <section className="grid gap-4 pb-16 sm:grid-cols-3">
          {CHANNELS.map((c) => (
            <div key={c.name} className="card p-5">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-100 text-lg">
                {c.icon}
              </div>
              <h3 className="mt-4 font-semibold text-zinc-900">{c.name}</h3>
              <p className="mt-1 text-sm text-zinc-600">{c.desc}</p>
            </div>
          ))}
        </section>

        {/* How it works */}
        <section className="card mb-20 p-8">
          <h2 className="text-lg font-semibold text-zinc-900">How it works</h2>
          <ol className="mt-5 grid gap-6 sm:grid-cols-3">
            {[
              ["1", "Define triggers", "Login, logout, order placed, inactivity — any event on your site."],
              ["2", "Write templates", "Per channel, with {{variables}}, toggled on or off from the grid."],
              ["3", "Fire & deliver", "When a trigger fires, every enabled channel sends automatically."],
            ].map(([n, title, desc]) => (
              <li key={n} className="flex gap-3">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-zinc-900 text-xs font-semibold text-white">
                  {n}
                </span>
                <div>
                  <h3 className="font-medium text-zinc-900">{title}</h3>
                  <p className="mt-1 text-sm text-zinc-600">{desc}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>
      </main>
    </>
  );
}
