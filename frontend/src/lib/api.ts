"use client";

import type {
  NotificationLog,
  Template,
  Trigger,
  User,
} from "./types";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
  "http://localhost:8000";

const ACCESS_KEY = "ns_access";
const REFRESH_KEY = "ns_refresh";

// --- token storage (localStorage; wrapped for SSR/private-mode safety) ---
export function getAccess(): string | null {
  try {
    return typeof window === "undefined" ? null : localStorage.getItem(ACCESS_KEY);
  } catch {
    return null;
  }
}

function setTokens(access: string, refresh?: string) {
  try {
    localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  } catch {
    /* ignore */
  }
}

export function clearTokens() {
  try {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  } catch {
    /* ignore */
  }
}

export class ApiError extends Error {
  status: number;
  data: unknown;
  constructor(status: number, message: string, data?: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  retry = true,
): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }
  const access = getAccess();
  if (access) headers.set("Authorization", `Bearer ${access}`);

  const resp = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  // Try one refresh on 401.
  if (resp.status === 401 && retry) {
    const refreshed = await tryRefresh();
    if (refreshed) return request<T>(path, options, false);
  }

  if (!resp.ok) {
    let data: unknown = null;
    let message = `Request failed (${resp.status})`;
    try {
      data = await resp.json();
      message =
        (data as { detail?: string })?.detail ||
        JSON.stringify(data) ||
        message;
    } catch {
      /* non-json */
    }
    throw new ApiError(resp.status, message, data);
  }

  if (resp.status === 204) return undefined as T;
  return (await resp.json()) as T;
}

async function tryRefresh(): Promise<boolean> {
  let refresh: string | null = null;
  try {
    refresh = localStorage.getItem(REFRESH_KEY);
  } catch {
    return false;
  }
  if (!refresh) return false;
  try {
    const resp = await fetch(`${BASE_URL}/api/auth/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (!resp.ok) return false;
    const data = (await resp.json()) as { access: string };
    setTokens(data.access);
    return true;
  } catch {
    return false;
  }
}

// --- auth ---
export async function login(email: string, password: string): Promise<User> {
  const data = await request<{ access: string; refresh: string; user: User }>(
    "/api/auth/login/",
    { method: "POST", body: JSON.stringify({ email, password }) },
  );
  setTokens(data.access, data.refresh);
  return data.user;
}

export async function register(payload: {
  email: string;
  username: string;
  password: string;
  phone_number?: string;
}): Promise<User> {
  return request<User>("/api/auth/register/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function logout(): Promise<void> {
  try {
    await request("/api/auth/logout/", { method: "POST" });
  } finally {
    clearTokens();
  }
}

export async function me(): Promise<User> {
  return request<User>("/api/auth/me/");
}

// --- events ---
export async function fireEvent(
  slug: string,
  context: Record<string, unknown> = {},
): Promise<{ trigger: string; sent: { channel: string; status: string; error: string }[] }> {
  return request("/api/events/" + slug + "/", {
    method: "POST",
    body: JSON.stringify({ context }),
  });
}

// --- admin: triggers ---
export async function listTriggers(): Promise<Trigger[]> {
  return request<Trigger[]>("/api/triggers/");
}

export async function createTrigger(payload: Partial<Trigger>): Promise<Trigger> {
  return request<Trigger>("/api/triggers/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function deleteTrigger(id: number): Promise<void> {
  return request<void>(`/api/triggers/${id}/`, { method: "DELETE" });
}

// --- admin: templates ---
export async function createTemplate(payload: Partial<Template>): Promise<Template> {
  return request<Template>("/api/templates/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateTemplate(
  id: number,
  payload: Partial<Template>,
): Promise<Template> {
  return request<Template>(`/api/templates/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function toggleTemplate(id: number): Promise<Template> {
  return request<Template>(`/api/templates/${id}/toggle/`, { method: "POST" });
}

export async function testSend(
  id: number,
  recipient: string,
  context: Record<string, unknown> = {},
): Promise<{ status: string; recipient: string; error: string }> {
  return request(`/api/templates/${id}/test-send/`, {
    method: "POST",
    body: JSON.stringify({ recipient, context }),
  });
}

// --- admin: logs ---
export async function listLogs(): Promise<NotificationLog[]> {
  return request<NotificationLog[]>("/api/logs/");
}
