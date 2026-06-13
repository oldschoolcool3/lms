import { Dialog, ErrorMessage } from 'frappe-ui'
import { h, reactive, ref } from 'vue'

interface DialogOptions {
	title?: string
	message?: string
	error?: string
	[key: string]: unknown
}

interface DialogInstance extends DialogOptions {
	key: string
	show: boolean
}

const dialogs = ref<DialogInstance[]>([])

export const Dialogs = {
	name: 'Dialogs',
	render() {
		return dialogs.value.map((dialog) => {
			return h(
				Dialog,
				{
					options: dialog,
					modelValue: dialog.show,
					'onUpdate:modelValue': (val: boolean) => (dialog.show = val),
				},
				() => [
					h('p', { class: 'text-p-base text-ink-gray-7' }, dialog.message),
					h(ErrorMessage, { class: 'mt-2', message: dialog.error }),
				]
			)
		})
	},
}

export function createDialog(options: DialogOptions): void {
	const dialog = reactive(options) as DialogInstance
	dialog.key = `dialog-${Math.random().toString(36).slice(2, 9)}`
	dialogs.value.push(dialog)
	dialog.show = true
}
