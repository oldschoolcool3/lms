<template>
	<div class="relative flex h-screen flex-col">
		<div
			class="flex flex-1 flex-col overflow-y-auto pb-10"
			id="scrollContainer"
		>
			<slot />
		</div>

		<div class="relative z-20">
			<!-- Dropdown menu -->
			<div
				class="fixed bottom-16 end-2 w-[80%] space-y-4 rounded-md bg-surface-white p-5 text-base shadow-md"
				v-if="showMenu"
				ref="menu"
			>
				<div
					v-for="link in otherLinks"
					:key="link.label"
					class="flex cursor-pointer items-center gap-x-2"
					@click="handleClick(link)"
				>
					<component
						:is="getIcon(link.icon)"
						class="h-4 w-4 stroke-1.5 text-ink-gray-5"
					/>
					<div>{{ link.label }}</div>
				</div>
			</div>

			<!-- Fixed menu -->
			<div
				v-if="sidebarSettings.data"
				class="standalone:pb-4 fixed bottom-0 start-0 z-10 flex w-full items-center justify-around border-t border-outline-gray-2 bg-surface-white"
			>
				<button
					v-for="tab in sidebarLinks"
					:key="tab.label"
					:class="isVisible(tab) ? 'block' : 'hidden'"
					class="flex flex-col items-center justify-center py-3 transition active:scale-95"
					@click="handleClick(tab)"
				>
					<component
						:is="getIcon(tab.icon)"
						class="h-6 w-6 stroke-1.5"
						:class="[isActive(tab) ? 'text-ink-gray-9' : 'text-ink-gray-5']"
					/>
				</button>
				<button @click="toggleMenu">
					<component
						:is="getIcon('List')"
						class="h-6 w-6 stroke-1.5 text-ink-gray-5"
					/>
				</button>
			</div>
		</div>
	</div>
</template>
<script setup lang="ts">
import { getSidebarLinks } from '@/utils'
import { useRouter } from 'vue-router'
import { call } from 'frappe-ui'
import { ref, watch } from 'vue'
import { sessionStore } from '@/stores/session'
import { useSettings } from '@/stores/settings'
import { usersStore } from '@/stores/user'
import * as icons from 'lucide-vue-next'
import type { Component } from 'vue'

interface MobileLink {
	label: string
	icon?: string
	to?: string
	activeFor?: string[]
	items?: MobileLink[]
}

const iconsByName = icons as unknown as Record<string, Component>
const getIcon = (name?: string): Component | undefined =>
	name ? iconsByName[name] : undefined

const { logout, user } = sessionStore()
let { isLoggedIn } = sessionStore()
const { sidebarSettings } = useSettings()
const router = useRouter()
let { userResource } = usersStore()
const sidebarLinks = ref<MobileLink[]>([])
const otherLinks = ref<MobileLink[]>([])
const showMenu = ref(false)
const menu = ref<HTMLElement | null>(null)
const isModerator = ref(false)
const isInstructor = ref(false)

const handleOutsideClick = (e: MouseEvent) => {
	if (menu.value && !menu.value.contains(e.target as Node)) {
		showMenu.value = false
	}
}

watch(showMenu, (val) => {
	if (val) {
		setTimeout(() => {
			document.addEventListener('click', handleOutsideClick)
		}, 0)
	} else {
		document.removeEventListener('click', handleOutsideClick)
	}
})

const destructureSidebarLinks = () => {
	let links: MobileLink[] = []
	sidebarLinks.value.forEach((link) => {
		link.items?.forEach((item) => {
			links.push(item)
		})
	})
	sidebarLinks.value = links
}

const filterLinksToShow = (data: Record<string, unknown>) => {
	Object.keys(data).forEach((key) => {
		if (!parseInt(String(data[key]))) {
			sidebarLinks.value = sidebarLinks.value.filter(
				(link) => link.label.toLowerCase().split(' ').join('_') !== key
			)
		}
	})
}

const addOtherLinks = () => {
	if (user) {
		addLink('Notifications', 'Bell', 'Notifications')
		addLink('Profile', 'UserRound')
		addLink('Log out', 'LogOut')
	} else {
		addLink('Log in', 'LogIn')
	}
}

const addLink = (label: string, icon: string, to = '') => {
	if (otherLinks.value.some((link) => link.label === label)) return
	otherLinks.value.push({
		label: label,
		icon: icon,
		to: to,
	})
}

const updateSidebarLinks = () => {
	sidebarLinks.value = getSidebarLinks(true)
	destructureSidebarLinks()
	sidebarSettings.reload(
		{},
		{
			onSuccess: async (data: Record<string, unknown>) => {
				filterLinksToShow(data)
				await addPrograms()
				if (isModerator.value || isInstructor.value) {
					addQuizzes()
					addAssignments()
					addProgrammingExercises()
				}
				addOtherLinks()
			},
		}
	)
}

const addQuizzes = () => {
	addLink('Quizzes', 'CircleHelp', 'Quizzes')
}

const addAssignments = () => {
	addLink('Assignments', 'Pencil', 'Assignments')
}

const addProgrammingExercises = () => {
	addLink('Programming Exercises', 'Code', 'ProgrammingExercises')
}

const addPrograms = async () => {
	if (sidebarLinks.value.some((link) => link.label === 'Programs')) return
	let canAddProgram = await checkIfCanAddProgram()
	if (!canAddProgram) return
	let activeFor = ['Programs', 'ProgramDetail']
	let index = 1

	sidebarLinks.value.splice(index, 0, {
		label: 'Programs',
		icon: 'Route',
		to: 'Programs',
		activeFor: activeFor,
	})
}

watch(
	userResource,
	async () => {
		await userResource.promise
		if (userResource.data) {
			isModerator.value = userResource.data.is_moderator
			isInstructor.value = userResource.data.is_instructor
		}
		updateSidebarLinks()
	},
	{ immediate: true }
)

const checkIfCanAddProgram = async () => {
	if (!userResource.data) return false
	if (isModerator.value || isInstructor.value) {
		return true
	}
	const programs = await call('lms.lms.utils.get_programs')
	return programs.enrolled.length > 0 || programs.published.length > 0
}

let isActive = (tab: MobileLink) => {
	return tab.activeFor?.includes(router.currentRoute.value.name as string)
}

const handleClick = (tab: MobileLink) => {
	if (tab.label == 'Log in') window.location.href = '/login'
	else if (tab.label == 'Log out')
		logout.submit().then(() => {
			isLoggedIn = false
		})
	else if (tab.label == 'Profile')
		router.push({
			name: 'Profile',
			params: {
				username: userResource.data?.username,
			},
		})
	else router.push({ name: tab.to })
}

const isVisible = (tab: MobileLink) => {
	if (tab.label == 'Log in') return !isLoggedIn
	else if (tab.label == 'Log out') return isLoggedIn
	else return true
}

const toggleMenu = () => {
	showMenu.value = !showMenu.value
}
</script>
