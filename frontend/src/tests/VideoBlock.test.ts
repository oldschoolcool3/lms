/**
 * Component-level tests for VideoBlock.vue.
 *
 * VideoBlock used to normalise "mm:ss" timestamps to seconds and sort the
 * `quizzes` array in place — mutating a prop the parent (and the sibling
 * QuizInVideo modal) shares. The refactor derives a `normalizedQuizzes`
 * computed instead, so the prop must now be left untouched. These tests lock
 * that: they would fail against the old in-place mutation.
 */
import { describe, expect, it, vi } from 'vitest'

// `__('...').format(...)` is used in the read-only quiz list.
;(String.prototype as unknown as { format: unknown }).format = function (
	this: string,
	...args: unknown[]
) {
	return this.replace(/\{(\d+)\}/g, (_m, i) => String(args[Number(i)]))
}

vi.mock('frappe-ui', () => ({
	Button: { template: '<button><slot /><slot name="icon" /></button>' },
	Dialog: { template: '<div><slot name="body" /></div>' },
	Dropdown: { props: ['options'], template: '<div><slot /></div>' },
}))
vi.mock('lucide-vue-next', () => ({
	Pause: { template: '<i />' },
	Maximize: { template: '<i />' },
	Volume2: { template: '<i />' },
	VolumeX: { template: '<i />' },
}))
vi.mock('@/components/Icons/Play.vue', () => ({
	default: { template: '<i />' },
}))
vi.mock('@/components/Modals/QuizInVideo.vue', () => ({
	default: {
		props: ['quizzes', 'saveQuizzes', 'duration', 'modelValue'],
		template: '<div />',
	},
}))
vi.mock('@/stores/settings', () => ({
	useSettings: () => ({ settings: { data: {} } }),
}))
vi.mock('@/utils', () => ({
	formatSeconds: (s: number) => String(s),
	formatTimestamp: (s: number) => String(s),
}))

import { mount, flushPromises } from '@vue/test-utils'
import VideoBlock from '@/components/VideoBlock.vue'

const mountVideo = (quizzes: any[], readOnly = true) =>
	mount(VideoBlock, {
		props: { file: '/x.mp4', readOnly, quizzes },
		global: { mocks: { __: (s: string) => s } },
	})

describe('VideoBlock — leaves the quizzes prop untouched', () => {
	it('does not coerce timestamps or sort the array in place', async () => {
		// Deliberately out of order, with a raw "mm:ss" string that the old
		// code would have rewritten to a number.
		const quizzes = [
			{ quiz: 'Later', time: '120' },
			{ quiz: 'Earlier', time: '1:00' },
		]
		mountVideo(quizzes)
		await flushPromises()

		// Original order and stored values must survive (no sort, no coercion).
		expect(quizzes).toEqual([
			{ quiz: 'Later', time: '120' },
			{ quiz: 'Earlier', time: '1:00' },
		])
	})

	it('renders the read-only quiz list in time-sorted, normalised order', async () => {
		const quizzes = [
			{ quiz: 'Later', time: '120' },
			{ quiz: 'Earlier', time: '1:00' },
		]
		const wrapper = mountVideo(quizzes)
		await flushPromises()

		// The list is the derived view: sorted ascending and "1:00" -> 60.
		const text = wrapper.text()
		expect(text.indexOf('Earlier')).toBeLessThan(text.indexOf('Later'))
		expect(text).toContain('60')
	})
})
