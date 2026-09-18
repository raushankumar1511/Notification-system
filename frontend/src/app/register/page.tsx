"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import Nav from "@/components/Nav";
import * as api from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({
    email: "",
    username: "",
    password: "",
    phone_number: "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function update(key: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((f) => ({ ...f, [key]: e.target.value }));
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await api.register(form);
      await login(form.email, form.password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
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
            Create your account
          </h1>
          <form onSubmit={onSubmit} className="mt-6 space-y-4">
            <div>
              <label className="label">Email</label>
              <input type="email" required value={form.email} onChange={update("email")} className="input" placeholder="you@example.com" />
            </div>
            <div>
              <label className="label">Username</label>
              <input required value={form.username} onChange={update("username")} className="input" placeholder="jane" />
            </div>
            <div>
              <label className="label">Password</label>
              <input type="password" required minLength={6} value={form.password} onChange={update("password")} className="input" placeholder="At least 6 characters" />
            </div>
            <div>
              <label className="label">
                Phone <span className="font-normal text-zinc-400">(optional, for WhatsApp)</span>
              </label>
              <input value={form.phone_number} onChange={update("phone_number")} className="input" placeholder="+15551234567" />
            </div>
            {error && (
              <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">
                {error}
              </p>
            )}
            <button type="submit" disabled={busy} className="btn-primary w-full">
              {busy ? "Creating…" : "Sign up"}
            </button>
          </form>
        </div>
        <p className="mt-6 text-center text-sm text-zinc-600">
          Already have an account?{" "}
          <Link href="/login" className="link">
            Log in
          </Link>
        </p>
      </main>
    </>
  );
}
