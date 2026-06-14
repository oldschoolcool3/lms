<template>
	<SettingsLayout
		:title="data?.name ? __('Edit Coupon') : __('New Coupon')"
		:description="
			__(
				'Set the discount, validity, and the courses or batches this coupon applies to.'
			)
		"
		:show-back="true"
		@back="emit('updateStep', 'list')"
	>
		<template #header-actions>
			<Button variant="solid" @click="saveCoupon()">
				{{ __('Save') }}
			</Button>
		</template>

		<div class="space-y-4">
			<div>
				<Switch
					size="sm"
					v-model="data.enabled"
					:label="__('Enabled')"
					:description="__('Allow this coupon to be used for discounts.')"
				/>
			</div>
			<div class="grid grid-cols-2 gap-4">
				<FormControl
					v-model="data.code"
					:label="__('Coupon Code')"
					:required="true"
					:placeholder="__('e.g. WELCOME10')"
					@input="() => (data.code = data.code.toUpperCase())"
				/>

				<Select
					v-model="data.discount_type"
					:label="__('Discount Type')"
					:required="true"
					:options="['Percentage', 'Fixed Amount']"
					class="w-full"
				/>

				<FormControl
					v-model="data.expires_on"
					:label="__('Expires On')"
					type="date"
				/>

				<FormControl
					v-if="data.discount_type === 'Percentage'"
					v-model="data.percentage_discount"
					:required="true"
					:label="__('Discount Percentage')"
					type="number"
				/>
				<FormControl
					v-else
					v-model="data.fixed_amount_discount"
					:required="true"
					:label="__('Discount Amount')"
					type="number"
				/>
				<FormControl
					v-model="data.usage_limit"
					:label="__('Usage Limit')"
					type="number"
				/>

				<FormControl
					v-model="data.redemptions_count"
					:label="__('Redemptions Count')"
					type="number"
					:disabled="true"
				/>
			</div>
			<div class="pt-4">
				<div class="font-semibold text-ink-gray-9 mb-3">
					{{ __('Applicable For') }}
				</div>
				<CouponItems ref="couponItems" :data="data" :coupons="coupons" />
			</div>
		</div>
	</SettingsLayout>
</template>
<script setup lang="ts">
import { Button, FormControl, toast } from 'frappe-ui'
import Switch from '@/components/Controls/Switch.vue'
import { ref } from 'vue'
import type { Coupon, Coupons } from './types'
import CouponItems from '@/components/Settings/Coupons/CouponItems.vue'
import SettingsLayout from '@/components/Layouts/SettingsLayout.vue'
import Select from '@/components/Controls/Select.vue'

const couponItems = ref<any>(null)
const emit = defineEmits(['updateStep'])

// The parent owns the coupon draft; this form edits it in place via v-model
// (`data.value.*`), so the edits flow back through the shared object.
const data = defineModel<Coupon>('data', { required: true })

const props = defineProps<{
	coupons: Coupons
}>()

const saveCoupon = () => {
	if (data.value?.name) {
		editCoupon()
	} else {
		createCoupon()
	}
}

const editCoupon = () => {
	props.coupons.setValue.submit(
		{
			...data.value,
		},
		{
			onSuccess(_data: Coupon) {
				if (couponItems.value) {
					couponItems.value.saveItems()
				}
			},
		}
	)
}

const createCoupon = () => {
	if (couponItems.value) {
		const rows = couponItems.value.saveItems()
		data.value.applicable_items = rows
	}
	props.coupons.insert.submit(
		{
			...data.value,
		},
		{
			onSuccess(createdCoupon: Coupon) {
				toast.success(__('Coupon created successfully'))
				emit('updateStep', 'details', { ...createdCoupon })
			},
			onError(err: any) {
				toast.error(err.messages?.[0] || err.message || err)
				console.error(err)
			},
		}
	)
}
</script>
