<template>
	<Dialog
		v-model="show"
		:options="{
			title: __('Enroll a Student'),
			size: 'lg',
			actions: [
				{
					label: 'Submit',
					variant: 'solid',
					onClick: addStudent,
				},
			],
		}"
	>
		<template #body-content>
			<div class="flex flex-col gap-4">
				<Link
					doctype="User"
					:modelValue="student ?? undefined"
					@update:modelValue="(val) => (student = val)"
					placeholder=" "
					:label="__('Student')"
					:onCreate="
						() => {
							openSettings('Members')
							show = false
						}
					"
					:required="true"
				/>
				<Link
					doctype="LMS Payment"
					:modelValue="payment ?? undefined"
					@update:modelValue="(val) => (payment = val)"
					placeholder=" "
					:label="__('Payment')"
					:onCreate="
						() => {
							openSettings('Transactions')
							show = false
						}
					"
				/>
			</div>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
import { call, Dialog, toast } from 'frappe-ui'
import { ref, inject } from 'vue'
import { useOnboarding } from 'frappe-ui/frappe'
import { openSettings } from '@/utils'
import Link from '@/components/Controls/Link.vue'
import type { SessionUser } from '@/types/api'

const student = ref<string | null>(null)
const payment = ref<string | null>(null)
const user = inject<SessionUser>('$user')!
const { updateOnboardingStep } = useOnboarding('learning')
const show = defineModel()

const props = defineProps({
	batch: {
		type: Object,
		default: null,
	},
	students: {
		type: Object,
		default: null,
	},
})

const addStudent = (close: () => void) => {
	props.students.insert.submit(
		{
			member: student.value,
			payment: payment.value,
			batch: props.batch.data?.name,
		},
		{
			onSuccess() {
				if (user.data?.is_system_manager)
					updateOnboardingStep('add_batch_student')

				student.value = null
				payment.value = null
				props.batch.reload()
				close()
			},
			onError(err: { messages?: string[] }) {
				toast.error(err.messages?.[0] || err)
				console.error(err)
			},
		}
	)
}
</script>
