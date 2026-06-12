// Pragmatic typing boundary for frappe-ui.
//
// frappe-ui ships its TypeScript types as raw Vue source — its package.json
// `exports["."].types` points at `src/index.ts`, not a built `.d.ts`. Letting
// the type-checker resolve into it pulls ~200 of frappe-ui's own `.vue` and
// `~icons/*` files into our program, flooding `vue-tsc` with errors that live
// in a dependency we can't patch.
//
// These shorthand ambient module declarations make frappe-ui an untyped (`any`)
// boundary instead: all of our own code is still fully type-checked — only the
// frappe-ui API surface is `any`. Under `moduleResolution: Node`, bare
// `frappe-ui` has no resolvable entry point, so these declarations win.
// Revisit if/when frappe-ui publishes built `.d.ts` declarations.
declare module 'frappe-ui'
declare module 'frappe-ui/frappe'
