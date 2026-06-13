<template>
	<Dialog
		v-model="show"
		:options="{
			title: __('Generate Certificates'),
			size: 'lg',
			actions: [
				{
					label: 'Create',
					variant: 'solid',
					onClick: onCreateClick,
				},
			],
		}"
	>
		<template #body-content>
			<div class="space-y-4">
				<Link
					v-model="details.evaluator"
					:label="__('Evaluator')"
					doctype="Course Evaluator"
				/>
				<FormControl
					type="date"
					v-model="details.issue_date"
					:label="__('Issue Date')"
				/>
				<FormControl
					type="date"
					v-model="details.expiry_date"
					:label="__('Expiry Date')"
				/>
				<FormControl
					type="select"
					v-model="details.course"
					:label="__('Course')"
					:options="getCourses()"
				/>
				<Link
					v-model="details.template"
					:label="__('Template')"
					doctype="Print Format"
					:filters="{
						doc_type: 'LMS Certificate',
					}"
				/>
				<Switch
					size="sm"
					:label="__('Published')"
					:description="
						__(
							'Enabling this will publish the certificate on the certified participants page.'
						)
					"
					v-model="details.published"
				/>
			</div>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
import { inject, reactive } from 'vue'
import { createResource, Dialog, FormControl, toast } from 'frappe-ui'
import Switch from '@/components/Controls/Switch.vue'
import Link from '@/components/Controls/Link.vue'
import type dayjsType from 'dayjs'

const show = defineModel()
const dayjs = inject<typeof dayjsType>('$dayjs')!
const details = reactive<{
	issue_date: string
	expiry_date: string | null
	template?: string
	evaluator?: string
	course?: string
	published: boolean
}>({
	issue_date: dayjs().format('YYYY-MM-DD'),
	expiry_date: null,
	template: undefined,
	evaluator: undefined,
	published: true,
})

const props = defineProps({
	batch: {
		type: [Object, null],
		required: true,
	},
})

const createCertificate = createResource({
	url: 'frappe.client.insert',
	makeParams(values: { course?: string; batch?: string; member?: string }) {
		return {
			doc: {
				doctype: 'LMS Certificate',
				issue_date: details.issue_date,
				expiry_date: details.expiry_date,
				template: details.template,
				published: details.published,
				course: values.course,
				batch_name: values.batch,
				member: values.member,
				evaluator: details.evaluator,
			},
		}
	},
})

const onCreateClick = ({ close }: { close: () => void }) => {
	generateCertificates(close)
}

const generateCertificates = (close: () => void) => {
	props.batch?.students.forEach((student: string) => {
		createCertificate.submit(
			{
				course: details.course,
				batch: props.batch?.name,
				member: student,
			},
			{
				onError(err: { messages?: string[] }) {
					toast.error(err.messages?.[0] || String(err))
				},
			}
		)
	})
	close()
	toast.success(__('Certificates generated successfully'))
}

const getCourses = () => {
	return props.batch?.courses.map((course: { course: string }) => {
		return {
			label: course.course,
			value: course.course,
		}
	})
}
</script>
