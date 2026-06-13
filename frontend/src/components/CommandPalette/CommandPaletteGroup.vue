<template>
	<div
		v-for="(result, resultIndex) in list"
		:key="resultIndex"
		class="px-2.5 space-y-2"
	>
		<div class="text-ink-gray-5 px-2">
			{{ result.title }}
		</div>
		<div class="">
			<div
				v-for="(item, itemIndex) in result.items"
				:key="itemIndex"
				class="flex items-center justify-between p-2 rounded hover:bg-surface-gray-2 cursor-pointer"
				:class="{ 'bg-surface-gray-2': item.isActive }"
				@click="emit('navigateTo', item.route)"
			>
				<div class="flex items-center gap-x-3">
					<component
						v-if="item.icon"
						:is="item.icon"
						class="size-4 stroke-1.5 text-ink-gray-6"
					/>
					<div v-html="item.title"></div>
				</div>
				<div v-if="item.modified" class="text-ink-gray-5">
					{{ dayjs.unix(item.modified).fromNow(true) }}
				</div>
			</div>
		</div>
	</div>
</template>
<script lang="ts" setup>
import { inject } from 'vue'

const dayjs = inject<any>('$dayjs')
const emit = defineEmits(['navigateTo'])

defineProps<{
	list: Array<{
		title: string
		items: Array<{
			title: string
			route: {
				name: string
				params?: Record<string, any>
				query?: Record<string, any>
			}
			icon?: any
			isActive?: boolean
			modified?: string
		}>
	}>
}>()
</script>
