// Pragmatic typing boundary for the Editor.js block plugins.
//
// These @editorjs/* packages ship no TypeScript declarations (their
// package.json has no `types`/`typings`), so under `strict`'s noImplicitAny a
// bare `import Header from '@editorjs/header'` fails with TS7016. We treat them
// as untyped (`any`) modules — the same approach as frappe-ui-shim.d.ts. Our
// own Editor.js tool classes (utils/quiz, utils/upload, utils/code, …) are
// still fully type-checked; only the third-party plugin API is `any`.
// (@editorjs/table and @editorjs/editorjs DO ship types and are left alone.)
declare module '@editorjs/header'
declare module '@editorjs/paragraph'
declare module '@editorjs/nested-list'
declare module '@editorjs/inline-code'
declare module '@editorjs/embed'
declare module '@editorjs/simple-image'
