<template>
	<div>
		<div class="mb-1.5 text-sm text-ink-gray-7">
			{{ __(label) }}
		</div>
		<div class="flex items-center">
			{{ tags }}
			<div
				v-for="tag in tags?.split(', ')"
				class="flex items-center bg-surface-gray-2 p-2 rounded-md me-2"
			>
				{{ tag }}
				<X
					class="stroke-1.5 w-3 h-3 ms-2 cursor-pointer"
					@click="removeTag(tag)"
				/>
			</div>
			<FormControl v-model="newTag" @keyup.enter="updateTags()" />
		</div>
	</div>
</template>
<script setup lang="ts">
import { FormControl } from 'frappe-ui'
import { X } from 'lucide-vue-next'
import { ref } from 'vue'

const props = defineProps({
	modelValue: {
		type: String,
		default: '',
	},
	label: {
		type: String,
		default: 'Tags',
	},
})
const tags = ref(props.modelValue)
const emit = defineEmits(['update:modelValue'])
const newTag = ref('')

const emitChange = (value: string) => {
	emit('update:modelValue', value)
}

const updateTags = () => {
	// Fixes a latent bug surfaced by the TS conversion: the original read the
	// `newTag` ref object instead of `newTag.value`, so adding a tag rendered
	// "[object Object]" and stored the ref. Use `.value`.
	if (newTag.value) {
		tags.value = tags.value ? `${tags.value}, ${newTag.value}` : newTag.value
		newTag.value = ''
		emitChange(tags.value)
	}
}

const removeTag = (tag: string) => {
	tags.value = tags.value.replace(tag, '').replace(', ,', ',')
	emitChange(tags.value)
}
</script>
