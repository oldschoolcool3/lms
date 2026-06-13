<template>
	<div class="">
		<LayoutHeader>
			<template #left-header>
				<Breadcrumbs
					class="h-7"
					:items="[
						{ label: __('Jobs'), route: { name: 'Jobs' } },
						{
							label: applications.data?.[0]?.job_title,
							route: { name: 'JobDetail', params: { job: props.job } },
						},
						{ label: __('Applications') },
					]"
				/>
			</template>
		</LayoutHeader>
		<div class="mx-auto pt-5 p-4">
			<div class="flex items-center justify-between mb-5">
				<div class="text-lg font-semibold text-ink-gray-9 mb-4 md:mb-0">
					{{ totalApplications.data }}
					{{
						totalApplications.data === 1
							? __('Application')
							: __('Applications')
					}}
				</div>
				<FormControl v-model="search" type="text" placeholder="Search">
					<template #prefix>
						<FeatherIcon name="search" class="size-4 text-ink-gray-5" />
					</template>
				</FormControl>
			</div>

			<div v-if="applications.data?.length">
				<ListView
					:columns="applicationColumns"
					:rows="applicantRows"
					row-key="name"
					:options="{
						showTooltip: false,
						selectable: false,
					}"
					class="h-[79vh] border-b"
				>
					<ListHeader
						class="mb-2 grid items-center rounded bg-surface-white border-b rounded-none p-2"
					>
						<ListHeaderItem
							:item="item"
							v-for="item in applicationColumns"
							:key="item.key"
						>
							<template #prefix="{ item }">
								<FeatherIcon
									v-if="item.icon"
									:name="item.icon?.toString()"
									class="h-4 w-4"
								/>
							</template>
						</ListHeaderItem>
					</ListHeader>
					<ListRows>
						<ListRow
							:row="row"
							v-slot="{ column, item }"
							v-for="row in applicantRows"
							class="cursor-pointer"
						>
							<ListRowItem :item="item">
								<div
									v-if="column.key === 'full_name'"
									class="flex items-center gap-x-3"
								>
									<Avatar
										size="sm"
										:image="row['user_image']"
										:label="row['full_name']"
									/>

									<span>{{ item }}</span>
								</div>
								<div v-else-if="column.key === 'actions'">
									<Dropdown :options="getActionOptions(row)">
										<Button variant="ghost">
											<FeatherIcon name="more-horizontal" class="w-4 h-4" />
										</Button>
									</Dropdown>
								</div>
								<div
									v-else-if="column.key === 'applied_on'"
									class="text-sm text-ink-gray-6"
								>
									{{ item }}
								</div>
								<div v-else>
									{{ item }}
								</div>
							</ListRowItem>
						</ListRow>
					</ListRows>
				</ListView>
				<div class="flex items-center justify-end gap-x-3 mt-3">
					<Button v-if="applications.hasNextPage" @click="applications.next()">
						{{ __('Load More') }}
					</Button>
					<div v-if="applications.hasNextPage" class="h-8 border-s"></div>
					<div class="text-ink-gray-5">
						{{ applications.data?.length }} {{ __('of') }}
						{{ totalApplications.data }}
					</div>
				</div>
			</div>
			<EmptyStateLayout
				v-else-if="!applications.loading"
				name="Job Applications"
			/>
		</div>

		<Dialog
			v-model="showEmailModal"
			:options="{
				title: __('Send Email to {0}').format(selectedApplicant?.full_name),
				size: 'lg',
				actions: [
					{
						label: __('Send'),
						variant: 'solid',
						onClick: sendEmail,
					},
				],
			}"
		>
			<template #body-content>
				<div class="space-y-4">
					<FormControl
						v-model="emailForm.subject"
						:label="__('Subject')"
						:placeholder="__('Enter email subject')"
						required
					/>
					<FormControl
						v-model="emailForm.replyTo"
						:label="__('Reply To')"
						:placeholder="__('Enter reply to email')"
					/>
					<div>
						<div class="text-sm text-ink-gray-5 mb-1">
							{{ __('Message') }}
						</div>
						<TextEditor
							:content="emailForm.message"
							@change="onMessageChange"
							:editable="true"
							:fixedMenu="true"
							editorClass="prose-sm max-w-none border-b border-x border-outline-gray-modals bg-surface-gray-2 rounded-b-md py-1 px-2 min-h-[7rem]"
						/>
					</div>
				</div>
			</template>
		</Dialog>
	</div>
</template>

<script setup lang="ts">
import {
	Avatar,
	Button,
	Breadcrumbs,
	call,
	Dialog,
	Dropdown,
	FeatherIcon,
	FormControl,
	TextEditor,
	ListView,
	ListHeader,
	ListHeaderItem,
	ListRows,
	ListRow,
	ListRowItem,
	createResource,
	createListResource,
	usePageMeta,
	toast,
} from 'frappe-ui'
import { computed, inject, ref, reactive, watch } from 'vue'
import { sessionStore } from '../stores/session'
import EmptyStateLayout from '@/components/Layouts/EmptyStateLayout.vue'
import LayoutHeader from '@/components/Layouts/LayoutHeader.vue'

interface ApplicationUser {
	name: string
	user_image?: string
	full_name?: string
	email?: string
}

interface ApplicantRow {
	name: string
	user: string
	creation: string
	resume?: string
	job_title?: string
	user_image?: string
	full_name?: string
	email?: string
	applied_on?: string
}

const dayjs = inject<typeof import('@/utils/dayjs').default>('$dayjs')!
const { brand } = sessionStore()
const showEmailModal = ref(false)
const selectedApplicant = ref<ApplicantRow | null>(null)
const search = ref('')
const emailForm = reactive({
	subject: '',
	message: '',
	replyTo: '',
})

const props = defineProps({
	job: {
		type: String,
		required: true,
	},
})

const applications = createListResource({
	doctype: 'LMS Job Application',
	fields: ['name', 'user', 'creation', 'resume', 'job_title'],
	filters: {
		job: props.job,
	},
	auto: true,
})

const users = createResource({
	url: 'lms.lms.api.get_application_users',
	makeParams: () => ({
		user_names: (applications.data || []).map((a: ApplicantRow) => a.user),
	}),
})

watch(
	() => applications.data,
	(rows) => {
		if (rows?.length) users.submit()
	}
)

const totalApplications = createResource({
	url: 'frappe.client.get_count',
	params: {
		doctype: 'LMS Job Application',
		filters: {
			job: props.job,
		},
	},
	auto: true,
	cache: ['totalApplications', props.job],
	onError(err: { messages?: string[] }) {
		toast.error(err.messages?.[0] || err)
		console.error('Error fetching total applications:', err)
	},
})

watch(search, () => {
	let filters = {
		job: props.job,
		user: ['like', `%${search.value}%`],
	}
	applications.update({
		filters: filters,
	})
	applications.reload()
	totalApplications.update({
		filters: filters,
	})
	totalApplications.reload()
})

const emailResource = createResource({
	url: 'frappe.core.doctype.communication.email.make',
	makeParams() {
		return {
			recipients: selectedApplicant.value!.email,
			cc: emailForm.replyTo,
			subject: emailForm.subject,
			content: emailForm.message,
			doctype: 'LMS Job Application',
			name: selectedApplicant.value!.name,
			send_email: 1,
			now: true,
		}
	},
})

const openEmailModal = (applicant: ApplicantRow) => {
	selectedApplicant.value = applicant
	emailForm.subject = `Job Application for ${applications.data?.[0]?.job_title} - ${applicant.full_name}`
	emailForm.replyTo = ''
	emailForm.message = ''
	showEmailModal.value = true
}

const sendEmail = (close: () => void) => {
	emailResource.submit(
		{},
		{
			validate() {
				if (!emailForm.subject) {
					return __('Subject is required')
				}
				if (!emailForm.message) {
					return __('Message is required')
				}
			},
			onSuccess: () => {
				toast.success(__('Email sent successfully'))
				close()
			},
			onError: (err: { messages?: string[] }) => {
				toast.error(err.messages?.[0] || err)
			},
		}
	)
}

const onMessageChange = (val: string) => {
	emailForm.message = val
}

const downloadResume = (resumeUrl: string) => {
	window.open(resumeUrl, '_blank')
}

const getActionOptions = (row: ApplicantRow) => {
	const options = []
	if (row.resume) {
		const resume = row.resume
		options.push({
			label: __('View Resume'),
			icon: 'download',
			onClick: () => downloadResume(resume),
		})
	}
	options.push({
		label: __('Send Email'),
		icon: 'mail',
		onClick: () => openEmailModal(row),
	})
	return options
}

const applicationColumns = computed(() => {
	return [
		{
			label: __('Full Name'),
			key: 'full_name',
			width: 3,
			icon: 'user',
		},
		{
			label: __('Email'),
			key: 'email',
			width: 3,
			icon: 'at-sign',
		},
		{
			label: __('Applied On'),
			key: 'applied_on',
			width: 2,
			icon: 'calendar',
		},
		{
			label: '',
			key: 'actions',
			width: 1,
			align: 'right',
		},
	]
})

const applicantRows = computed<ApplicantRow[]>(() => {
	if (!applications.data) return []
	const userMap: Record<string, ApplicationUser> = Object.fromEntries(
		(users.data || []).map((u: ApplicationUser) => [u.name, u])
	)
	return applications.data.map((application: ApplicantRow) => {
		const user = userMap[application.user] || {}
		return {
			...application,
			user_image: user.user_image,
			full_name: user.full_name,
			email: user.email,
			applied_on: dayjs(application.creation).format('DD MMM YYYY'),
		}
	})
})

usePageMeta(() => {
	return {
		title: `Applications - ${applications.data?.[0]?.job_title}`,
		icon: brand.favicon,
	}
})
</script>
