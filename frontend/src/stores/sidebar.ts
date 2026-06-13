import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSidebar = defineStore('sidebar', () => {
	const isSidebarCollapsed = ref(false)
	const isWebpagesCollapsed = ref(true)

	const storedSidebarCollapsed = localStorage.getItem('isSidebarCollapsed')
	if (storedSidebarCollapsed) {
		isSidebarCollapsed.value = JSON.parse(storedSidebarCollapsed)
	}

	const storedWebpagesCollapsed = localStorage.getItem('isWebpagesCollapsed')
	if (storedWebpagesCollapsed) {
		isWebpagesCollapsed.value = JSON.parse(storedWebpagesCollapsed)
	}

	return {
		isSidebarCollapsed,
		isWebpagesCollapsed,
	}
})
