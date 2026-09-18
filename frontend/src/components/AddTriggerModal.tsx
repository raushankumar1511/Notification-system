"use client";

import { useState } from "react";
import { ApiError } from "@/lib/api";
import * as api from "@/lib/api";

interface Props {
  onClose: () => void;
  onCreated: () => void;
}

export default function AddTriggerModal({ onClose, onCreated }: Props) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [eventType, setEventType] = useState<"EVENT" | "SCHEDULED">("EVENT");
  const [days, setDays] = useState("1");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function save() {
    setError("");
    if (!name.trim()) {
      setError("Name is required.");
      return;
    }
    setBusy(true);
    try {
      await api.createTrigger({
        name: name.trim(),
        description: description.trim(),
        event_type: eventType,
        schedule_config:
          eventType === "SCHEDULED"
            ? { inactivity_hours: Math.max(1, Number(days) || 1) * 24 }
            : {},
      });
      onCreated();
    } catch (err) {
      if (err instanceof ApiError && err.data && typeof err.data === "object") {
        const vals = Object.values(err.data as Record<string, unknown>)
          .map((v) => (Array.isArray(v) ? v.join(" ") : String(v)))
          .join(" ");
        setError(vals || err.message);
      } else {
        setError(err instanceof Error ? err.message : "Could not create trigger");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-zinc-900/40 p-4 backdrop-blur-sm">
      <div className="card my-8 w-full max-w-md p-6 shadow-xl">
        <div className="flex items-start justify-between">
          <h2 className="text-lg font-semibold tracking-tight text-zinc-900">
            Add trigger
          </h2>
          <button onClick={onClose} className="btn-ghost -mr-2 -mt-1 px-2">
            ✕
          </button>
        </div>

        <div className="mt-5 space-y-4">
          <div>
            <label className="label">Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="input"
              placeholder="e.g. Cart abandoned"
            />
            <p className="mt-1 text-xs text-zinc-400">
              A URL-safe slug is generated automatically.
            </p>
          </div>

          <div>
            <label className="label">Description (optional)</label>
            <input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="input"
              placeholder="When this should fire"
            />
          </div>

          <div>
            <label className="label">Type</label>
            <div className="grid grid-cols-2 gap-2">
              {(["EVENT", "SCHEDULED"] as const).map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setEventType(t)}
                  className={`rounded-lg border px-3 py-2 text-sm font-medium transition ${
                    eventType === t
                      ? "border-zinc-900 bg-zinc-900 text-white"
                      : "border-zinc-200 bg-white text-zinc-700 hover:bg-zinc-50"
                  }`}
                >
                  {t === "EVENT" ? "Event" : "Scheduled"}
                </button>
              ))}
            </div>
            <p className="mt-1 text-xs text-zinc-400">
              {eventType === "EVENT"
                ? "Fires inline when the app calls its event endpoint."
                : "Fires when a user is inactive for the period below."}
            </p>
          </div>

          {eventType === "SCHEDULED" && (
            <div>
              <label className="label">Inactivity period (days)</label>
              <input
                type="number"
                min={1}
                value={days}
                onChange={(e) => setDays(e.target.value)}
                className="input"
              />
            </div>
          )}

          {error && (
            <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">
              {error}
            </p>
          )}
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button onClick={save} disabled={busy} className="btn-primary">
            {busy ? "Creating…" : "Create trigger"}
          </button>
        </div>
      </div>
    </div>
  );
}
