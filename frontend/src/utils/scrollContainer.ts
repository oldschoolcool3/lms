export function scrollTo(
	...options: [] | Parameters<HTMLElement['scrollTo']>
): void {
	if (!options || options.length === 0) return
	const container = getScrollContainer()
	if (!container) return
	container.scrollTo(...options)
}

export function getScrollContainer(): HTMLElement | undefined {
	// window.scrollContainer is reference to the scroll container in DesktopLayout.vue and MobileLayout.vue
	return window.scrollContainer
}
