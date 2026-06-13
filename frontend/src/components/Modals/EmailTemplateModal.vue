<template>
	<Dialog
		v-model="show"
		:options="{
			title:
				templateID == 'new'
					? __('New Email Template')
					: __('Edit Email Template'),
			size: 'lg',
			actions: [
				{
					label: __('Save'),
					variant: 'solid',
					onClick: onSave,
				},
			],
		}"
	>
		<template #body-content>
			<div class="space-y-4">
				<FormControl
					:label="__('Name')"
					v-model="template.name"
					type="text"
					:required="true"
					:placeholder="__('Batch Enrollment Confirmation')"
				/>
				<FormControl
					:label="__('Subject')"
					v-model="template.subject"
					type="text"
					:required="true"
					:placeholder="__('Your enrollment in {{ batch_name }} is confirmed')"
				/>
				<Switch
					size="sm"
					:description="__('Use HTML content for the email response')"
					:label="__('Use HTML')"
					v-model="template.use_html"
				/>
				<FormControl
					v-if="template.use_html"
					:label="__('Content')"
					v-model="template.response_html"
					type="textarea"
					:required="true"
					:rows="10"
					:placeholder="
						__(
							'<p>Dear {{ member_name }},</p>\n\n<p>You have been enrolled in our upcoming batch {{ batch_name }}.</p>\n\n<p>Thanks,</p>\n<p>Frappe Learning</p>'
						)
					"
				/>
				<div v-else>
					<div class="text-xs text-ink-gray-5 mb-2">
						{{ __('Content') }}
						<span class="text-ink-red-3">*</span>
					</div>
					<TextEditor
						:content="template.response"
						@change="onResponseChange"
						:editable="true"
						:fixedMenu="true"
						:placeholder="
							__(
								'Dear {{ member_name }},\n\nYou have been enrolled in our upcoming batch {{ batch_name }}.\n\nThanks,\nFrappe Learning'
							)
						"
						editorClass="prose-sm max-w-none border-b border-x border-outline-gray-modals bg-surface-gray-2 rounded-b-md py-1 px-2 min-h-[7rem] max-h-[18rem] overflow-y-auto"
					/>
				</div>
			</div>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
import { call, Dialog, FormControl, TextEditor, toast } from 'frappe-ui'
import Switch from '@/components/Controls/Switch.vue'
import { reactive, watch } from 'vue'
import type { PropType } from 'vue'
import { cleanError } from '@/utils'

interface SubmitError {
	messages: string[]
}

interface EmailTemplateRow {
	name: string
	subject: string
	use_html: boolean
	response: string
	response_html: string
}

// frappe-ui's createListResource is an untyped (`any`) boundary via the
// frappe-ui shim; this narrow shape describes only the members this modal
// uses on the resource passed in through v-model.
interface SubmitOptions {
	onSuccess?: () => void
	onError?: (err: SubmitError) => void
}
interface EmailTemplatesResource {
	data: EmailTemplateRow[]
	reload: () => void
	insert: {
		submit: (values: Record<string, unknown>, opts: SubmitOptions) => void
	}
	setValue: {
		submit: (values: Record<string, unknown>, opts: SubmitOptions) => void
	}
}

type CloseFn = () => void

const props = defineProps({
	templateID: {
		type: String as PropType<string | null>,
		default: 'new',
	},
})

const show = defineModel<boolean>()
const emailTemplates = defineModel<EmailTemplatesResource>('emailTemplates')
const emit = defineEmits(['created'])
const template = reactive({
	name: '',
	subject: '',
	use_html: false,
	response: '',
	response_html: '',
})

const saveTemplate = (close: CloseFn) => {
	if (props.templateID == 'new') {
		createNewTemplate(close)
	} else {
		updateTemplate(close)
	}
}

const onSave = (args: { close: CloseFn }) => {
	saveTemplate(args.close)
}

const onResponseChange = (val: string) => {
	template.response = val
}

const createNewTemplate = (close: CloseFn) => {
	// Parent always binds the resource via v-model, so it is present here.
	emailTemplates.value!.insert.submit(
		{
			__newname: template.name,
			...template,
		},
		{
			onSuccess() {
				emailTemplates.value!.reload()
				emit('created', template.name)
				refreshForm(close)
				toast.success(__('Email Template created successfully'))
			},
			onError(err: SubmitError) {
				refreshForm(close)
				toast.error(
					cleanError(err.messages[0]) || __('Error creating email template')
				)
			},
		}
	)
}

const updateTemplate = async (close: CloseFn) => {
	if (props.templateID != template.name) {
		await renameDoc()
	}
	setValue(close)
}

const setValue = (close: CloseFn) => {
	emailTemplates.value!.setValue.submit(
		{
			...template,
			name: template.name,
		},
		{
			onSuccess() {
				emailTemplates.value!.reload()
				refreshForm(close)
				toast.success(__('Email Template updated successfully'))
			},
			onError(err: SubmitError) {
				refreshForm(close)
				toast.error(
					cleanError(err.messages[0]) || __('Error updating email template')
				)
			},
		}
	)
}

const renameDoc = async () => {
	await call('frappe.client.rename_doc', {
		doctype: 'Email Template',
		old_name: props.templateID,
		new_name: template.name,
	})
}

watch(
	() => props.templateID,
	(val: string | null) => {
		if (val !== 'new') {
			emailTemplates.value?.data.forEach((row: EmailTemplateRow) => {
				if (row.name === val) {
					template.name = row.name
					template.subject = row.subject
					template.use_html = row.use_html
					template.response = row.response
					template.response_html = row.response_html
				}
			})
		}
	},
	{ flush: 'post' }
)

const refreshForm = (close: CloseFn) => {
	close()
	template.name = ''
	template.subject = ''
	template.use_html = false
	template.response = ''
	template.response_html = ''
}
</script>
