# Security

- **Never commit** credentials of any kind: `.env`, API keys, PEM files,
  `site_config.json`, bench site backups.
- **Every `@frappe.whitelist()` method is a public API endpoint.** It must
  enforce authorization itself — check roles or `frappe.has_permission(...)`
  before reading or writing. Don't assume the caller is trusted because the
  frontend only calls it from one place.
- **`allow_guest=True` is an explicit decision**, not a convenience. Guest
  endpoints must never leak user data and must validate every input.
- **No string-interpolated SQL.** Use the ORM (`frappe.get_doc`,
  `frappe.get_all`, `frappe.db.get_value`) or `frappe.qb`; if raw
  `frappe.db.sql` is unavoidable, use parameterized values (`%(name)s`).
- **`ignore_permissions=True` requires justification** — a comment explaining
  why the permission system is bypassed and why that's safe.
- **Sanitize user-supplied HTML/markdown** before rendering or storing.
  Frontend rendering of user content goes through DOMPurify (already a
  dependency); keep it that way.
- **File serving stays hardened** — SCORM/media endpoints have had path
  traversal fixes upstream; preserve their validation when touching them and
  keep their tests green.
- Validate all external input at API boundaries (request args, webhook
  payloads, uploaded files); trust only data already inside the permission
  boundary.
- Payment flows (Razorpay, `lms_payment`) and certificate issuance are
  fraud-sensitive — server-side validation only, never trust amounts or
  completion state sent by the client.
