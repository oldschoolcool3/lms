import type { Component, Ref } from 'vue'
import type { LMSCourse } from './lms/LMSCourse'

export interface Resource<T = unknown> {
	data: T
	loading: boolean
	error: unknown
	doc?: T
	hasNextPage?: boolean
	reload(): void
	fetch(): void
	next?(): void
	submit(params?: unknown, opts?: unknown): void
	update(opts: unknown): void
	setValue: { submit(values: unknown, opts?: unknown): void }
}

export interface UserInfo {
	name: string
	full_name?: string
	first_name?: string
	last_name?: string
	email?: string
	username?: string
	user_image?: string
	open_to?: 'Work' | 'Hiring' | string
}

export interface SessionUser {
	data?: UserInfo & {
		is_moderator?: boolean
		is_instructor?: boolean
		is_evaluator?: boolean
		is_student?: boolean
		is_system_manager?: boolean
		sitename?: string
	}
	reload(): Promise<unknown>
}

export interface CourseInstructorInfo extends UserInfo {
	instructor?: string
	bio?: string | null
}

export interface Membership {
	name?: string
	member?: string
	progress?: number
	current_lesson?: string
	purchased_certificate?: 0 | 1 | boolean
	certificate?: string
}

export interface CourseDetails
	extends Omit<LMSCourse, 'instructors' | 'rating'> {
	price?: string
	current_lesson?: string
	instructors: CourseInstructorInfo[]
	membership?: Membership | null
	rating?: string
	rating_count?: number
	quiz_count?: number
}

export interface CourseReviewInfo {
	name: string
	creation: string
	rating: number
	review?: string
	owner_details: UserInfo
}

export interface OutlineLesson {
	name: string
	title: string
	number: string
	icon?: string
	is_complete?: boolean
	include_in_preview?: boolean | 0 | 1
}

export interface OutlineChapter {
	name: string
	title: string
	idx: number
	is_scorm_package?: 0 | 1
	scorm_package?: { file_name: string; file_size: number } | null
	lessons?: OutlineLesson[]
}

export interface CertificationInfo {
	certificate?: { name: string; template: string } | null
	membership?: {
		purchased_certificate?: 0 | 1
		certificate?: string
	} | null
	paid_certificate?: 0 | 1
}

export interface ChapterDetailInput {
	name?: string
	title?: string
	is_scorm_package?: 0 | 1
	scorm_package?: { file_name: string; file_size: number } | null
}

export interface CourseFormMeta {
	description: string
	keywords: string
}

export interface CourseFormContext {
	resource: Resource<LMSCourse | null>
	instructors: Ref<string[]>
	relatedCourses: Ref<string[]>
	meta: CourseFormMeta
	markDirty: () => void
}

export interface SettingsField {
	label: string
	name: string
	type: string
	description?: string
	options?: string[]
	doctype?: string
	reqd?: boolean
	default?: unknown
	rows?: number
	placeholder?: string
	size?: string
	mode?: string
	value?: number | boolean | null
}

export interface SettingsColumn {
	fields: SettingsField[]
}

export interface SettingsSection {
	label?: string
	columns: SettingsColumn[]
}

export interface SettingsTabItem {
	label: string
	description?: string
	icon?: string
	hideLabel?: boolean
	sections?: SettingsSection[]
	template?: Component
	condition?: () => unknown
}

export interface SettingsTabGroup {
	label: string
	hideLabel: boolean
	items: SettingsTabItem[]
}
