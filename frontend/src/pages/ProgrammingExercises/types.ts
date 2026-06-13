export interface ProgrammingExercise {
	// Absent while creating a new exercise (assigned by the server on insert).
	name?: string
	title: string
	language: 'Python' | 'JavaScript'
	test_cases_count?: number
	problem_statement: string
	test_cases: TestCase[]
}

// frappe-ui resource submit callbacks (the untyped frappe-ui boundary); the
// error object is dynamic, so model only the field this code reads.
type SubmitOptions = {
	onSuccess?: () => void
	onError?: (err: { messages?: string[] }) => void
}

export interface TestCase {
	name: string
	input: string
	expected_output: string
	output: string
	status: 'Passed' | 'Failed'
}

export interface ProgrammingExerciseSubmission {
	name: string
	exercise: string
	exercise_title: string
	member_name: string
	member_image: string
	status: 'Passed' | 'Failed'
	modified: string
}

export type Filters = {
	exercise?: string
	member?: string
	status?: string
}

export type ProgrammingExercises = {
	data: ProgrammingExercise[]
	reload: () => void
	hasNextPage: boolean
	next: () => void
	setValue: {
		submit: (data: ProgrammingExercise, options?: SubmitOptions) => void
	}
	insert: {
		submit: (data: ProgrammingExercise, options?: SubmitOptions) => void
	}
	delete: {
		submit: (name: string, options?: SubmitOptions) => void
	}
}
