<template>
	<Dialog
		v-model="show"
		:options="{
			title: __('Add web page to sidebar'),
			size: 'lg',
			actions: [
				{
					label: 'Add',
					variant: 'solid',
					onClick: addWebPage,
				},
			],
		}"
	>
		<template #body-content>
			<div class="text-base">
				<Link
					v-model="page.webpage"
					doctype="Web Page"
					:label="__('Web Page')"
					:filters="{
						published: 1,
					}"
				/>
				<IconPicker v-model="page.icon" :label="__('Icon')" class="mt-4" />
			</div>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
import { Dialog, createResource, toast } from 'frappe-ui'
import Link from '@/components/Controls/Link.vue'
import { reactive, watch } from 'vue'
import IconPicker from '@/components/Controls/IconPicker.vue'

const sidebar = defineModel<{ reload: () => void }>('reloadSidebar')
const show = defineModel()
const page = reactive({
	icon: '',
	webpage: '',
})

const props = defineProps({
	page: {
		type: Object,
		default: null,
	},
})

const webPage = createResource({
	url: 'lms.lms.api.update_sidebar_item',
	makeParams() {
		return {
			webpage: page.webpage,
			icon: page.icon,
		}
	},
})

watch(
	() => props.page,
	(newPage) => {
		if (newPage) {
			page.icon = newPage.icon
			page.webpage = newPage.web_page
		}
	},
	{ immediate: true }
)

const addWebPage = (close: () => void) => {
	webPage.submit(
		{},
		{
			onSuccess() {
				sidebar.value?.reload()
				close()
				toast.success(__('Web page added to sidebar'))
			},
			onError(err: { message: string[] }) {
				toast.error(err.message[0] || err)
				close()
			},
		}
	)
}
</script>
