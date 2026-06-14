/**
 * Component-level tests for CouponDetails.vue (the payment-sensitive coupon
 * editor). The refactor swapped the in-place `props.data` mutation for a
 * `defineModel('data')` two-way binding. These tests lock the behaviour that
 * matters: field edits still write back to the parent's object, and Save still
 * routes new vs existing coupons to the correct resource call with the full
 * payload.
 */
import { describe, expect, it, vi } from 'vitest'

vi.mock('frappe-ui', () => ({
	// No explicit @click emit: Vue falls the parent's @click through to the
	// root <button> as a native listener, so emitting too would double-fire.
	Button: { template: `<button><slot /></button>` },
	FormControl: {
		props: ['modelValue'],
		emits: ['update:modelValue', 'input'],
		template: `<input :value="modelValue" @input="$emit('update:modelValue', $event.target.value); $emit('input', $event)" />`,
	},
	toast: { success: vi.fn(), error: vi.fn() },
}))
vi.mock('@/components/Controls/Switch.vue', () => ({
	default: {
		props: ['modelValue'],
		emits: ['update:modelValue'],
		template: `<button data-testid="switch" @click="$emit('update:modelValue', !modelValue)" />`,
	},
}))
vi.mock('@/components/Controls/Select.vue', () => ({
	default: {
		props: ['modelValue', 'options'],
		emits: ['update:modelValue'],
		template: `<select @change="$emit('update:modelValue', $event.target.value)"><option /></select>`,
	},
}))
vi.mock('@/components/Layouts/SettingsLayout.vue', () => ({
	default: { template: `<div><slot name="header-actions" /><slot /></div>` },
}))
// CouponItems exposes `saveItems()`, which CouponDetails calls through a ref.
vi.mock('@/components/Settings/Coupons/CouponItems.vue', () => ({
	default: {
		props: ['data', 'coupons'],
		setup(_props: unknown, { expose }: { expose: (o: unknown) => void }) {
			expose({
				saveItems: () => [
					{ reference_doctype: 'LMS Course', reference_name: 'C1', name: null },
				],
			})
			return () => null
		},
	},
}))

import { mount, flushPromises } from '@vue/test-utils'
import { reactive } from 'vue'
import CouponDetails from '@/components/Settings/Coupons/CouponDetails.vue'

const makeCoupons = () => ({
	data: [],
	update: vi.fn(),
	insert: { submit: vi.fn() },
	setValue: { submit: vi.fn() },
	reload: vi.fn(),
})

const baseCoupon = (overrides: Record<string, unknown> = {}) =>
	reactive({
		name: '',
		enabled: true,
		code: 'X',
		discount_type: 'Percentage',
		percentage_discount: 10,
		fixed_amount_discount: undefined,
		expires_on: undefined,
		usage_limit: undefined,
		redemptions_count: 0,
		applicable_items: [],
		...overrides,
	})

const mountDetails = (data: any, coupons: any) =>
	mount(CouponDetails, {
		props: { data, coupons },
		global: { mocks: { __: (s: string) => s } },
	})

const clickSave = async (wrapper: ReturnType<typeof mountDetails>) => {
	const save = wrapper.findAll('button').find((b) => b.text().includes('Save'))
	await save!.trigger('click')
}

describe('CouponDetails — edits write back to the parent object', () => {
	it('updates the passed coupon (and upper-cases the code) via the model', async () => {
		const data = baseCoupon()
		const wrapper = mountDetails(data, makeCoupons())
		await flushPromises()

		// The first input is the coupon-code FormControl.
		await wrapper.find('input').setValue('summer10')

		expect(data.code).toBe('SUMMER10')
	})
})

describe('CouponDetails — Save routes to the right resource call', () => {
	it('submits an existing coupon through setValue with the edited payload', async () => {
		const data = baseCoupon({
			name: 'COUPON-001',
			code: 'SAVE20',
			percentage_discount: 20,
		})
		const coupons = makeCoupons()
		const wrapper = mountDetails(data, coupons)
		await flushPromises()

		await clickSave(wrapper)

		expect(coupons.setValue.submit).toHaveBeenCalledTimes(1)
		expect(coupons.insert.submit).not.toHaveBeenCalled()
		expect(coupons.setValue.submit.mock.calls[0][0]).toMatchObject({
			name: 'COUPON-001',
			code: 'SAVE20',
			percentage_discount: 20,
		})
	})

	it('submits a new coupon through insert and attaches applicable items', async () => {
		const data = baseCoupon({ name: '', code: 'NEW5' })
		const coupons = makeCoupons()
		const wrapper = mountDetails(data, coupons)
		await flushPromises()

		await clickSave(wrapper)

		expect(coupons.insert.submit).toHaveBeenCalledTimes(1)
		expect(coupons.setValue.submit).not.toHaveBeenCalled()
		const payload = coupons.insert.submit.mock.calls[0][0]
		expect(payload.code).toBe('NEW5')
		expect(payload.applicable_items).toEqual([
			{ reference_doctype: 'LMS Course', reference_name: 'C1', name: null },
		])
	})

	it('carries the fixed-amount discount in the payload for a Fixed Amount coupon', async () => {
		// The amount-bearing branch of a payment-sensitive form: the value must
		// reach the resource call unchanged.
		const data = baseCoupon({
			name: 'COUPON-FIX',
			discount_type: 'Fixed Amount',
			percentage_discount: undefined,
			fixed_amount_discount: 50,
		})
		const coupons = makeCoupons()
		const wrapper = mountDetails(data, coupons)
		await flushPromises()

		await clickSave(wrapper)

		expect(coupons.setValue.submit).toHaveBeenCalledTimes(1)
		expect(coupons.setValue.submit.mock.calls[0][0]).toMatchObject({
			discount_type: 'Fixed Amount',
			fixed_amount_discount: 50,
		})
	})
})
