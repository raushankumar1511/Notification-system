# API reference

Base path: `/api/`. Auth: `Authorization: Bearer <access>` (JWT). Admin endpoints
require `is_staff`.

## Auth
| Method | Path | Auth | Body | Notes |
|---|---|---|---|---|
| POST | `/api/auth/register/` | none | `email, username, password, phone_number?` | Creates a user |
| POST | `/api/auth/login/` | none | `email, password` | Returns `access`, `refresh`, `user`. Fires the `login` trigger |
| POST | `/api/auth/refresh/` | none | `refresh` | Returns a new `access` |
| POST | `/api/auth/logout/` | user | — | Fires the `logout` trigger (token discard is client-side) |
| GET/PATCH | `/api/auth/me/` | user | — | Current user; PATCH can update `phone_number` |

## Events
| Method | Path | Auth | Body | Notes |
|---|---|---|---|---|
| POST | `/api/events/<slug>/` | user | `{ "context": {...} }` | Fires an EVENT trigger for the current user (e.g. `order_placed`, `password_reset`) |

## Admin — triggers (rows)
| Method | Path | Notes |
|---|---|---|
| GET | `/api/triggers/` | List triggers, each with nested `templates` (powers the grid) |
| POST | `/api/triggers/` | Create a trigger (`slug`, `name`, `event_type`, `schedule_config`) |
| PATCH/DELETE | `/api/triggers/<id>/` | Update / delete |

## Admin — templates (cells)
| Method | Path | Notes |
|---|---|---|
| POST | `/api/templates/` | Create a template (`trigger`, `channel`, `subject`/`title`/`body`, `provider_config`, `variables`) |
| PATCH | `/api/templates/<id>/` | Update fields |
| POST | `/api/templates/<id>/toggle/` | Flip `is_enabled` |
| POST | `/api/templates/<id>/test-send/` | Body `{ recipient, context }`. Sends via the pipeline, bypassing the toggle, `is_test=True` |

## Admin — logs
| Method | Path | Notes |
|---|---|---|
| GET | `/api/logs/?channel=<c>` | Last 200 NotificationLog rows |

## Internal
| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/api/internal/run-scheduled/` | header `X-Scheduled-Secret: <SCHEDULED_RUN_SECRET>` | Runs scheduled-trigger evaluation (idempotent) |
| GET | `/health/` | none | Health check |

### Channels
`whatsapp` · `email` · `webpush`. A template is unique per `(trigger, channel)`.
