export {}

declare global {
	function __(text: string): string

	interface String {
		format(...args: any[]): string
	}

	// Globals injected onto `window` by the Frappe host page / boot.
	interface Window {
		lms_path?: string
		lang?: string
		read_only_mode?: boolean
		// Set by Desktop/MobileLayout.vue; the app's scroll viewport.
		scrollContainer?: HTMLElement
	}
}

// Augment `@vue/runtime-core` (where the interface actually lives) rather than
// the `vue` re-export — only the former merges into the component instance type
// that vue-tsc uses to type-check template expressions like `{{ __('…') }}`.
declare module '@vue/runtime-core' {
	interface ComponentCustomProperties {
		__: (text: string) => string
	}
}
