# Frontend Coding Style (Vue SPA)

- Vue 3 **Composition API with `<script setup>`** for all new components
- TypeScript for new code — types for DocTypes and API responses live in
  `frontend/src/types/`; plain JS persists in older files, don't churn it
- Formatting: **prettier** (`frontend/.prettierrc.json`: no semicolons, single
  quotes; tabs via `.editorconfig`) — `task format:frontend`
- **frappe-ui first**: use its components (Button, Dialog, FormControl, ListView,
  …) and its data layer (`createResource`, `createListResource`,
  `createDocumentResource`) before writing custom equivalents
- State: Pinia stores in `src/stores/`; component-local state stays local
- Routing: add pages under `src/pages/` and register in `src/router.js`
- Styling: Tailwind utility classes; respect RTL support — use logical
  properties/classes (`ms-`/`me-`, `start`/`end`) not `ml-`/`mr-`, per the
  Tailwind RTL semgrep rules in `.github/semgrep/`
- All user-facing strings wrapped in `__()` (see `src/translation.js`)
- Icons: lucide-vue-next
- `import type` for type-only imports; `const` over `let`, no `var`
