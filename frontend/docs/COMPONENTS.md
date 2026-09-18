# Components

## `Nav` (`components/Nav.tsx`)
Top bar. Shows Dashboard/Admin links + logout when signed in, else Log in / Sign up.
Admin link only for `user.is_staff`.

## `TemplateEditor` (`components/TemplateEditor.tsx`)
Modal to create or edit one template (a grid cell). Props: `trigger`, `channel`,
`template | null`, `onClose`, `onSaved`.
- **Email:** subject + body.
- **Web Push:** title + optional open URL + body.
- **WhatsApp:** approved `template_name`, `language_code`, and `param_map` (comma-separated
  variable names, positional); body is a preview only. Shows an inline note about the
  approved-template constraint.
- **Variables:** a `name=sample` textarea → stored as the `variables` dict (sample values
  are used for test-send defaults).
Create → `POST /api/templates/`; edit → `PATCH /api/templates/<id>/`.

## `LogsPanel` (`components/LogsPanel.tsx`)
Fetches `/api/logs/` and renders time / trigger / channel / recipient / status. Status
badge is color-coded (sent green, failed red, skipped amber); hover shows the error.
Has a Refresh button.

## Grid `Cell` (inline in `app/admin/page.tsx`)
Per (trigger, channel): create link when empty; otherwise ON/OFF badge, a body preview,
and Edit / Turn on-off / Test actions. **Test** prompts for a recipient (email address,
WhatsApp number, or blank for web push → your own subscription) and calls
`/api/templates/<id>/test-send/`.
