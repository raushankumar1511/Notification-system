# Data model

## User (`accounts.User`, extends AbstractUser)
- `email` (unique, login identifier), `username`, `is_staff` (= admin).
- `phone_number` — WhatsApp target (must be on the sandbox allow-list to receive).
- `last_seen` — activity timestamp for scheduled triggers (stamped by the JWT auth class).

## Trigger (`notifications.Trigger`)
- `slug` (unique), `name`, `description`, `is_active`.
- `event_type` — `EVENT` (fires inline) or `SCHEDULED` (evaluated periodically).
- `schedule_config` (JSON) — e.g. `{"inactivity_hours": 168}` for "1 week".

## Template (`notifications.Template`) — one grid cell
- FK `trigger`, `channel` (`whatsapp`|`email`|`webpush`); **unique `(trigger, channel)`**.
- `is_enabled` — the on/off toggle in the grid.
- `subject` (email), `title` (push), `body` (all support `{{variables}}`).
- `provider_config` (JSON) — channel-specific:
  - WhatsApp: `{"template_name", "language_code", "param_map": [var, ...]}`
  - Web Push: `{"url": "https://…"}` (optional)
- `variables` (JSON) — `{name: sample_value}`; sample values are used for test-send
  defaults and UI hints.

## NotificationLog (`notifications.NotificationLog`)
- `user?`, `template?`, `trigger_slug`, `channel`, `recipient`.
- `status` — `sent` | `failed` | `skipped`; `is_test`; `provider_message_id`; `error`.
- `rendered_payload` (JSON) — what was rendered + the provider response.

## SentNotification (`notifications.SentNotification`) — scheduled dedupe
- Unique `(user, trigger, window_key)`. `window_key` = the user's `last_seen` date, so a
  single inactivity episode notifies once; a new episode (new `last_seen`) can notify again.
