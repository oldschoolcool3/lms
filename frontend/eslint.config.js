// Flat ESLint config for the LMS SPA (Vue 3 + TypeScript, with some legacy JS).
//
// Scope: catch real bugs (undeclared vars, unreachable code, Vue template/SFC
// mistakes) without fighting Prettier (formatting is owned by `prettier --check
// src`, see package.json `lint`) and without demanding a big-bang TypeScript
// rewrite of the ~40% of the app that is still plain JS. Rules that would only
// produce stylistic churn across upstream-derived components are relaxed here,
// not in the upstream files themselves (fork hygiene).
import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import {
	defineConfigWithVueTs,
	vueTsConfigs,
} from '@vue/eslint-config-typescript'
import eslintConfigPrettier from 'eslint-config-prettier'
import globals from 'globals'

export default defineConfigWithVueTs(
	{
		// Generated, vendored, or build-output files — never hand-linted.
		ignores: [
			'dist/**',
			'dev-dist/**',
			'public/**',
			'auto-imports.d.ts',
			'components.d.ts',
			'src/utils/frappe-ui-colors.json',
		],
	},

	// Plain JS (entry points, stores, utils not yet migrated to TS). Core
	// recommended only — typescript-eslint rules don't apply to `.js`.
	{
		files: ['**/*.js'],
		...js.configs.recommended,
		rules: {
			...js.configs.recommended.rules,
			// `_`-prefixed args/vars are intentional throwaways.
			'no-unused-vars': [
				'error',
				{
					argsIgnorePattern: '^_',
					varsIgnorePattern: '^_',
					caughtErrors: 'none',
				},
			],
		},
	},

	// Build/tooling config files run in Node, not the browser.
	{
		files: ['*.config.{js,ts}', 'vite.config.js', 'vitest.config.ts'],
		languageOptions: { globals: globals.node },
	},

	// TypeScript + Vue single-file components.
	pluginVue.configs['flat/essential'],
	vueTsConfigs.recommended,

	{
		languageOptions: {
			ecmaVersion: 2022,
			sourceType: 'module',
			globals: {
				...globals.browser,
				// App globals injected at runtime / by the Frappe host page.
				__: 'readonly',
				frappe: 'readonly',
				posthog: 'readonly',
			},
		},
		rules: {
			// `any` is pervasive in this Frappe frontend (untyped resources, editor.js,
			// charting libs). Banning it now would be pure churn; tighten incrementally
			// as files migrate to real types (Track A, PR-A3).
			'@typescript-eslint/no-explicit-any': 'off',
			// Single-word component names (Sidebar, Uploader, …) are intentional.
			'vue/multi-word-component-names': 'off',
			// SFCs are mid-migration to `<script lang="ts">`; don't force it (PR-A3).
			'vue/block-lang': 'off',
		},
	},

	// `_`-prefixed args/vars are intentional throwaways (TS/Vue scopes).
	{
		files: ['**/*.{ts,mts,tsx,vue}'],
		rules: {
			'@typescript-eslint/no-unused-vars': [
				'error',
				{
					argsIgnorePattern: '^_',
					varsIgnorePattern: '^_',
					caughtErrors: 'none',
				},
			],
		},
	},

	// Vitest specs lean on loose mocks.
	{
		files: ['src/tests/**'],
		rules: {
			'@typescript-eslint/no-explicit-any': 'off',
		},
	},

	// Must come last: turns off every rule that would conflict with Prettier.
	eslintConfigPrettier
)
