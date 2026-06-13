import type { LMSProgramCourse } from './lms/LMSProgramCourse'
import type { LMSProgramMember } from './lms/LMSProgramMember'

// Child-table rows as the Program form works with them: freshly added rows are
// partial (only the link field + idx) until persisted, so the DocType fields are
// all optional here.
export type ProgramCourse = Partial<LMSProgramCourse>
export type ProgramMember = Partial<LMSProgramMember>

// The form's working copy of a Program. `published`/`enforce_course_order` are
// bound to checkbox controls as booleans here (the DocType stores them as 0|1).
export interface Program {
	name: string
	title: string
	published: boolean
	enforce_course_order: boolean
	program_courses: ProgramCourse[]
	program_members: ProgramMember[]
	course_count?: number
	member_count?: number
}

// A program row as returned by `lms.lms.utils.get_programs`, keyed by category
// (enrolled programs additionally carry the member's `progress`).
export interface StudentProgram {
	name: string
	course_count?: number
	member_count?: number
	progress?: number
}

// The `programs` model is a frappe-ui list resource (createListResource) for the
// LMS Program doctype. Only the members the form actually touches are typed; the
// underlying frappe-ui API is otherwise the untyped `any` boundary.
export interface Programs {
	data: Program[]
	reload(): void
	insert: { submit(values: unknown, opts?: unknown): void }
	setValue: { submit(values: unknown, opts?: unknown): void }
	delete: { submit(name: string | null, opts?: unknown): void }
}
