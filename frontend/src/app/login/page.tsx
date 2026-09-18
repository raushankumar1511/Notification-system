"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import Nav from "@/components/Nav";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const user = await login(email, password);
      router.push(user.is_staff ? "/admin" : "/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Nav />
      <main className="mx-auto flex max-w-sm flex-col px-4 py-16">
        <div className="card p-8">
          <h1 className="text-xl font-semibold tracking-tight text-zinc-900">
            Welcome back
          </h1>
          <p className="mt-1 text-sm text-zinc-500">
            Logging in fires the <span className="font-medium">Login</span> trigger.
          </p>
          <form onSubmit={onSubmit} className="mt-6 space-y-4">
            <div>
              <label className="label">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label className="label">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
                placeholder="••••••••"
              />
            </div>
            {error && (
              <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">
                {error}
              </p>
            )}
            <button type="submit" disabled={busy} className="btn-primary w-full">
              {busy ? "Logging in…" : "Log in"}
            </button>
          </form>
        </div>
        <p className="mt-6 text-center text-sm text-zinc-600">
          No account?{" "}
          <Link href="/register" className="link">
            Sign up
          </Link>
        </p>
      </main>
    </>
  );
}
