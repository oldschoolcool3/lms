export function getLmsBasePath(): string {
	return window.lms_path || 'lms'
}

export function getLmsRoute(path = ''): string {
	const base = getLmsBasePath()
	if (!path) {
		return base
	}
	const normalized = path.startsWith('/') ? path.slice(1) : path
	return `/${base}/${normalized}`
}
