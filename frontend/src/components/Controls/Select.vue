<template>
	<div>
		<label v-if="label" class="block mb-1.5" :class="labelClasses">
			{{ label }}
			<span v-if="required" class="text-ink-red-3">*</span>
		</label>
		<Select
			v-bind="$attrs"
			:modelValue="modelValue"
			:options="options"
			:size="size"
			:variant="variant"
			:placeholder="placeholder"
			:disabled="disabled"
			:emptyText="emptyText"
			:required="required"
			@update:modelValue="(val: string) => emit('update:modelValue', val)"
		/>
		<p v-if="description" class="mt-1 text-xs text-ink-gray-5">
			{{ description }}
		</p>
	</div>
</template>

<script setup lang="ts">
import { Select } from 'frappe-ui'
import { computed } from 'vue'

defineOptions({ inheritAttrs: false })

type SelectSize = 'sm' | 'md' | 'lg' | 'xl'
type SelectVariant = 'subtle' | 'outline' | 'ghost'

// frappe-ui ships SelectOption/SelectOptionValue as untyped (`any`) via the
// shim, so we model the wrapper's own contract here: native <select> values are
// strings (the bound model may start null), and selecting always emits a string.
type SelectOption =
	| string
	| { label: string; value: string | null; description?: string }

const props = withDefaults(
	defineProps<{
		modelValue?: string | null
		options?: SelectOption[]
		label?: string
		description?: string
		placeholder?: string
		required?: boolean
		disabled?: boolean
		size?: SelectSize
		variant?: SelectVariant
		emptyText?: string
	}>(),
	{ size: 'sm' }
)

const emit = defineEmits<{
	(e: 'update:modelValue', value: string): void
}>()

const labelClasses = computed<string[]>(() => {
	const sizeMap: Record<string, string> = { sm: 'text-xs', md: 'text-base' }
	return [sizeMap[props.size || 'sm'], 'text-ink-gray-5']
})
</script>
