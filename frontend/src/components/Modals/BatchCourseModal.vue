<template>
	<Dialog
		v-model="show"
		:options="{
			title: __('Add a course to the batch'),
			size: 'lg',
			actions: [
				{
					label: __('Submit'),
					variant: 'solid',
					onClick: (close: () => void) => addCourse(close),
				},
			],
		}"
	>
		<template #body-content>
			<Link
				doctype="LMS Course"
				v-model="course"
				:label="__('Course')"
				:required="true"
				:filters="{ published: 1 }"
				variant="outline"
				:onCreate="onCourseCreate"
			/>
			<Link
				doctype="Course Evaluator"
				v-model="evaluator"
				:label="__('Evaluator')"
				class="mt-4"
			/>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
import { Dialog, toast } from 'frappe-ui'
import { ref, inject } from 'vue'
import type { SessionUser } from '@/types/api'
import Link from '@/components/Controls/Link.vue'
import { useOnboarding } from 'frappe-ui/frappe'
import { useRouter } from 'vue-router'

interface Courses {
	insert: {
		submit: (
			params: {
				course: string | undefined
				evaluator: string | undefined
				parent: string | null
				parenttype: string
				parentfield: string
			},
			options: {
				onSuccess: () => void
				onError: (err: { messages?: string[] }) => void
			}
		) => void
	}
}

const show = defineModel<boolean>()
const course = ref<string | undefined>()
const evaluator = ref<string | undefined>()
const user = inject<SessionUser>('$user')!
const courses = defineModel<Courses>('courses')
const router = useRouter()
const { updateOnboardingStep } = useOnboarding('learning')

const onCourseCreate = (_value: string | null, close?: () => void) => {
	close?.()
	router.push({
		name: 'Courses',
		query: { newCourse: '1' },
	})
}

const props = defineProps({
	batch: {
		type: String,
		default: null,
	},
})

const addCourse = (close: () => void) => {
	courses.value?.insert.submit(
		{
			course: course.value,
			evaluator: evaluator.value,
			parent: props.batch,
			parenttype: 'LMS Batch',
			parentfield: 'courses',
		},
		{
			onSuccess() {
				if (user.data?.is_system_manager)
					updateOnboardingStep('add_batch_course')

				close()
				course.value = undefined
				evaluator.value = undefined
				toast.success(__('Course added to batch successfully'))
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
				console.log(err)
			},
		}
	)
}
</script>
