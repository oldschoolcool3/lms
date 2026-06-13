import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import type { Ref } from 'vue'

export function useScreenSize() {
	const size = reactive({
		width: window.innerWidth,
		height: window.innerHeight,
	})

	const isMobile = computed(() => size.width < 640)

	const onResize = () => {
		size.width = window.innerWidth
		size.height = window.innerHeight
	}

	onMounted(() => {
		window.addEventListener('resize', onResize)
	})

	onUnmounted(() => {
		window.removeEventListener('resize', onResize)
	})

	return {
		size,
		isMobile,
	}
}

interface SwipeState {
	initialX: number | null
	initialY: number | null
	currentX: number | null
	currentY: number | null
	diffX: number | null
	diffY: number | null
	absDiffX: number | null
	absDiffY: number | null
	direction: 'left' | 'right' | 'up' | 'down' | null
}

export function useSwipe() {
	const swipe = reactive<SwipeState>({
		initialX: null,
		initialY: null,
		currentX: null,
		currentY: null,
		diffX: null,
		diffY: null,
		absDiffX: null,
		absDiffY: null,
		direction: null,
	})

	const onTouchStart = (e: TouchEvent) => {
		swipe.initialX = e.touches[0].clientX
		swipe.initialY = e.touches[0].clientY
		swipe.direction = null
		swipe.diffX = null
		swipe.diffY = null
		swipe.absDiffX = null
		swipe.absDiffY = null
	}

	const onTouchMove = (e: TouchEvent) => {
		const currentX = e.touches[0].clientX
		const currentY = e.touches[0].clientY
		const diffX = (swipe.initialX ?? 0) - currentX
		const diffY = (swipe.initialY ?? 0) - currentY

		swipe.currentX = currentX
		swipe.currentY = currentY
		swipe.diffX = diffX
		swipe.diffY = diffY
		swipe.absDiffX = Math.abs(diffX)
		swipe.absDiffY = Math.abs(diffY)
	}

	const onTouchEnd = () => {
		const { diffX, diffY, absDiffX, absDiffY } = swipe
		if ((absDiffX ?? 0) > (absDiffY ?? 0)) {
			if ((diffX ?? 0) > 0) {
				swipe.direction = 'left'
			} else {
				swipe.direction = 'right'
			}
		} else {
			if ((diffY ?? 0) > 0) {
				swipe.direction = 'up'
			} else {
				swipe.direction = 'down'
			}
		}
	}

	onMounted(() => {
		window.addEventListener('touchstart', onTouchStart)
		window.addEventListener('touchend', onTouchEnd)
		window.addEventListener('touchmove', onTouchMove)
	})

	onUnmounted(() => {
		window.removeEventListener('touchstart', onTouchStart)
		window.removeEventListener('touchend', onTouchEnd)
		window.removeEventListener('touchmove', onTouchMove)
	})

	return swipe
}

export function useLocalStorage<T>(key: string, initialValue: T): Ref<T> {
	const value = ref<T | null>(null) as Ref<T>
	const storedValue = localStorage.getItem(key)
	value.value = storedValue ? JSON.parse(storedValue) : initialValue

	watch(value, (newValue) => {
		localStorage.setItem(key, JSON.stringify(newValue))
	})
	return value
}
