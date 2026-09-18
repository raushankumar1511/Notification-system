"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function Nav() {
  const { user, logout } = useAuth();
  const router = useRouter();

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

  return (
    <header className="sticky top-0 z-40 border-b border-zinc-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-zinc-900 text-sm text-white">
            🔔
          </span>
          <span className="text-[15px] font-semibold tracking-tight text-zinc-900">
            Notify
          </span>
        </Link>
        <nav className="flex items-center gap-1 text-sm">
          {user ? (
            <>
              <Link href="/dashboard" className="btn-ghost">
                Dashboard
              </Link>
              {user.is_staff && (
                <Link href="/admin" className="btn-ghost">
                  Admin
                </Link>
              )}
              <span className="mx-2 hidden text-zinc-400 sm:inline">
                {user.email}
              </span>
              <button onClick={handleLogout} className="btn-secondary">
                Log out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="btn-ghost">
                Log in
              </Link>
              <Link href="/register" className="btn-primary">
                Sign up
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
