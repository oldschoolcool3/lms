export {}

declare global {
	// frappe-style translator: extra args (interpolation values) are accepted
	// for compatibility; the LMS translate() reads only `text`.
	function __(text: string, ...args: unknown[]): string

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
		// Installed by translation.ts; the global `__()` translator.
		__?: (text: string, ...args: unknown[]) => string
		// Translation cache populated by translation.ts.
		translatedMessages?: Record<string, string>
		// SCORM 2004 runtime API surface, installed by SCORMChapter.vue so the
		// embedded SCORM package iframe can discover it via window.API_1484_11.
		API_1484_11?: {
			Initialize: () => string
			Terminate: () => string
			GetValue: (key: string) => string
			SetValue: (key: string, value: string) => string
			Commit: () => string
			GetLastError: () => string
			GetErrorString: () => string
			GetDiagnostic: () => string
		}
		// SCORM 1.2 runtime API surface, installed alongside API_1484_11.
		API?: {
			LMSInitialize: () => string
			LMSFinish: () => string
			LMSGetValue: (key: string) => string
			LMSSetValue: (key: string, value: string) => string
			LMSCommit: () => string
			LMSGetLastError: () => string
			LMSGetErrorString: () => string
			LMSGetDiagnostic: () => string
		}
	}

	// Lesson.vue tags <video> elements with these flags so it attaches its
	// 'ended' / 'error' listeners only once per element.
	interface HTMLVideoElement {
		_lmsEndedAttached?: boolean
		_lmsErrorAttached?: boolean
	}

	// Vendor-prefixed fullscreen entry points used by Lesson.vue's Zen mode;
	// the standard requestFullscreen is already declared by the DOM lib.
	interface HTMLElement {
		mozRequestFullScreen?: () => void
		webkitRequestFullscreen?: () => void
		msRequestFullscreen?: () => void
	}
}

// Augment `@vue/runtime-core` (where the interface actually lives) rather than
// the `vue` re-export — only the former merges into the component instance type
// that vue-tsc uses to type-check template expressions like `{{ __('…') }}`.
declare module '@vue/runtime-core' {
	interface ComponentCustomProperties {
		__: (text: string, ...args: unknown[]) => string
		// The Options-API `resources` plugin from frappe-ui injects
		// `this.$resources` onto every component instance. Like the rest of
		// frappe-ui it is part of the untyped boundary (see
		// types/frappe-ui-shim.d.ts), so it is typed `any` rather than modelled.
		$resources: any
	}
}
