<template>
	<Dialog
		v-model="show"
		:options="{
			size: '3xl',
		}"
	>
		<template #body-header>
			<div class="flex items-center justify-between mb-5">
				<div class="text-2xl font-semibold leading-6 text-ink-gray-9">
					{{ __('Edit Profile') }}
				</div>
				<div class="flex items-center gap-x-2">
					<Badge v-if="isDirty" theme="orange">
						{{ __('Not Saved') }}
					</Badge>
					<div class="pb-5 float-end">
						<Button variant="solid" @click="saveProfile()">
							{{ __('Save') }}
						</Button>
					</div>
				</div>
			</div>
		</template>
		<template #body-content>
			<div class="text-base">
				<div class="grid grid-cols-2 gap-10">
					<div class="space-y-4">
						<div class="space-y-4">
							<Uploader
								v-model="form.image"
								:label="__('Profile Image')"
								:required="true"
								shape="circle"
							/>

							<FormControl
								v-model="form.first_name"
								:label="__('First Name')"
								:required="true"
							/>
							<FormControl
								v-model="form.last_name"
								:label="__('Last Name')"
								:required="true"
							/>
							<FormControl v-model="form.headline" :label="__('Headline')" />

							<FormControl v-model="form.linkedin" :label="__('LinkedIn ID')" />
							<FormControl v-model="form.github" :label="__('GitHub ID')" />
							<FormControl v-model="form.twitter" :label="__('Twitter ID')" />
						</div>
					</div>
					<div class="space-y-4">
						<FormControl
							v-model="form.open_to"
							type="select"
							:options="[' ', 'Work', 'Hiring']"
							:label="__('Open to')"
							:placeholder="__('Looking for new work or hiring talent?')"
						/>
						<Link
							:label="__('Language')"
							v-model="form.language"
							doctype="Language"
						/>
						<div>
							<div class="mb-1.5 text-sm text-ink-gray-5">
								{{ __('Bio') }}
							</div>
							<TextEditor
								:fixedMenu="true"
								@change="setBio"
								:content="form.bio"
								:rows="15"
								editorClass="prose-sm py-2 px-2 min-h-[280px] border-outline-gray-2 hover:border-outline-gray-3 rounded-b-md bg-surface-gray-3"
							/>
						</div>
					</div>
				</div>
			</div>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
import {
	Badge,
	Button,
	createResource,
	Dialog,
	FormControl,
	TextEditor,
	toast,
} from 'frappe-ui'
import { ref, reactive, watch } from 'vue'
import { sanitizeHTML } from '@/utils'
import type { Resource, UserInfo } from '@/types/api'
import Link from '@/components/Controls/Link.vue'

const show = defineModel<boolean>()
const reloadProfile = defineModel<Resource<unknown> | undefined>(
	'reloadProfile'
)
const hasLanguageChanged = ref(false)
const isDirty = ref(false)

const setBio = (val: string) => {
	form.bio = val
}

const props = defineProps({
	profile: {
		type: Object,
		required: true,
	},
})

const form = reactive({
	first_name: '',
	last_name: '',
	headline: '',
	bio: '',
	image: '',
	open_to: '',
	language: '',
	linkedin: '',
	github: '',
	twitter: '',
})

const updateProfile = createResource({
	url: 'frappe.client.set_value',
	makeParams() {
		return {
			doctype: 'User',
			name: props.profile.data.name,
			fieldname: {
				user_image: form.image || null,
				...form,
			},
		}
	},
	onSuccess(data: UserInfo) {
		// `reloadProfile` is the same resource the parent also passes as
		// `:profile`, so write the optimistic update through the model
		// instead of mutating the prop.
		if (reloadProfile.value) reloadProfile.value.data = data
	},
})

const validateMandatoryFields = () => {
	const missingFields = []
	if (!form.first_name) missingFields.push(__('First Name'))
	if (!form.last_name) missingFields.push(__('Last Name'))
	if (!form.image) missingFields.push(__('Profile Image'))
	if (missingFields.length) {
		toast.error(
			__('Please fill the mandatory fields: {0}').format(
				missingFields.join(', ')
			)
		)
		console.error('Missing mandatory fields:', missingFields)
	}
	return missingFields.length
}

const saveProfile = () => {
	const missingMandatoryFields = validateMandatoryFields()
	if (missingMandatoryFields) return
	form.bio = sanitizeHTML(form.bio)
	updateProfile.submit(
		{},
		{
			onSuccess() {
				show.value = false
				reloadProfile.value?.reload()
				if (hasLanguageChanged.value) {
					hasLanguageChanged.value = false
					window.location.reload()
				}
			},
			onError(err: { messages?: string[] }) {
				toast.error(err.messages?.[0] || err)
			},
		}
	)
}

watch(
	() => form,
	(newVal) => {
		if (!props.profile.data) return
		const keys = Object.keys(newVal) as (keyof typeof form)[]
		keys.splice(keys.indexOf('image'), 1)
		for (const key of keys) {
			if (newVal[key] !== props.profile.data[key]) {
				isDirty.value = true
				return
			}
		}
		if (form.image !== props.profile.data.user_image) {
			isDirty.value = true
			return
		}
		isDirty.value = false
	},
	{ deep: true }
)

watch(
	() => props.profile.data,
	(newVal) => {
		if (newVal) {
			form.first_name = newVal.first_name
			form.last_name = newVal.last_name
			form.headline = newVal.headline
			form.language = newVal.language
			form.bio = newVal.bio
			form.open_to = newVal.open_to
			form.linkedin = newVal.linkedin
			form.github = newVal.github
			form.twitter = newVal.twitter
			form.image = newVal.user_image
			isDirty.value = false
		}
	}
)

watch(
	() => form.language,
	() => {
		if (form.language !== props.profile.data.language) {
			hasLanguageChanged.value = true
		}
	}
)
</script>
