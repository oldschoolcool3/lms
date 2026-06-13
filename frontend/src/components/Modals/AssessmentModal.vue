<template>
	<Dialog
		v-model="show"
		:options="{
			title: __('Add an assessment'),
			size: 'sm',
			actions: [
				{
					label: __('Submit'),
					variant: 'solid',
					onClick: (close: () => void) => addAssessment(close),
				},
			],
		}"
	>
		<template #body-content>
			<div class="space-y-4">
				<FormControl
					type="select"
					:options="assessmentTypes"
					v-model="assessmentType"
					:label="__('Type')"
					placeholder=" "
					@update:modelValue="() => (assessment = undefined)"
				/>
				<Link
					v-if="assessmentType"
					v-model="assessment"
					:doctype="assessmentType"
					:label="__('Assessment')"
					placeholder=" "
					:onCreate="onAssessmentCreate"
				/>
			</div>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
import { Dialog, FormControl, createResource, toast } from 'frappe-ui'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { Resource } from '@/types/api'
import Link from '@/components/Controls/Link.vue'

const show = defineModel<boolean>()
const assessmentType = ref<string | undefined>()
const assessment = ref<string | undefined>()
const assessments = defineModel<Resource<unknown> | undefined>('assessments')
const router = useRouter()

const props = defineProps({
	batch: {
		type: String,
		default: null,
	},
})

const assessmentResource = createResource({
	url: 'frappe.client.insert',
	makeParams() {
		return {
			doc: {
				doctype: 'LMS Assessment',
				parent: props.batch,
				parenttype: 'LMS Batch',
				parentfield: 'assessment',
				assessment_type: assessmentType.value,
				assessment_name: assessment.value,
			},
		}
	},
})

const onAssessmentCreate = (_value: string | null, close?: () => void) => {
	// Preserve the original inline handler's unconditional close() call. Link.vue's
	// live create path (handleCreate -> onCreate?.(null)) passes no close arg, so this
	// throws just as the pre-conversion code did; the `!` keeps that behaviour intact.
	close!()
	if (assessmentType.value === 'LMS Quiz') {
		router.push({
			name: 'QuizForm',
			params: {
				quizID: 'new',
			},
		})
	} else if (assessmentType.value === 'LMS Assignment') {
		router.push({
			name: 'Assignments',
		})
	}
}

const addAssessment = (close: () => void) => {
	assessmentResource.submit(
		{},
		{
			onSuccess() {
				assessments.value?.reload()
				toast.success(__('Assessment added successfully'))
				close()
			},
		}
	)
}

const assessmentTypes = computed(() => {
	return [
		{ label: 'Quiz', value: 'LMS Quiz' },
		{ label: 'Assignment', value: 'LMS Assignment' },
		{ label: 'Programming Exercise', value: 'LMS Programming Exercise' },
	]
})
</script>
