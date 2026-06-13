import { createResource } from 'frappe-ui'
import type { App } from 'vue'

export default function translationPlugin(app: App): void {
	app.config.globalProperties.__ = translate
	window.__ = translate
	if (!window.translatedMessages) fetchTranslations()
}

function translate(message: string): string {
	const translatedMessages = window.translatedMessages || {}
	const translatedMessage = translatedMessages[message] || message

	const hasPlaceholders = /{\d+}/.test(message)
	if (!hasPlaceholders) {
		return translatedMessage
	}
	// Messages with `{0}` placeholders return a formatter object whose
	// `.format(...)` interpolates the args. The global `__`/`String.format`
	// contract (see global.d.ts) models the result as a string, so cast to it.
	return {
		format: function (...args: unknown[]): string {
			return translatedMessage.replace(
				/{(\d+)}/g,
				function (match: string, number: string): string {
					const arg = args[Number(number)]
					return typeof arg != 'undefined' ? String(arg) : match
				}
			)
		},
	} as unknown as string
}

function fetchTranslations(): void {
	createResource({
		url: 'lms.lms.api.get_translations',
		cache: 'translations',
		auto: true,
		transform: (data: Record<string, string>) => {
			window.translatedMessages = data
		},
	})
}
