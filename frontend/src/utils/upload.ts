import AudioBlock from '@/components/AudioBlock.vue'
import VideoBlock from '@/components/VideoBlock.vue'
import UploadPlugin from '@/components/UploadPlugin.vue'
import { h, createApp } from 'vue'
import { Upload as UploadIcon } from 'lucide-vue-next'
import { createDialog } from '@/utils/dialogs'
import translationPlugin from '../translation'

interface UploadFile {
	file_url?: string
	file_type?: string
	quizzes?: unknown[]
}

interface UploadConfig {
	docname?: string | null
	fieldname?: string
}

export class Upload {
	data: UploadFile
	readOnly: boolean
	config: UploadConfig
	wrapper!: HTMLDivElement

	constructor({
		data,
		config,
		readOnly,
	}: {
		data: UploadFile
		config?: UploadConfig
		readOnly: boolean
	}) {
		this.data = data
		this.readOnly = readOnly
		this.config = config || {}
	}

	static get toolbox() {
		const app = createApp({
			render: () =>
				h(UploadIcon, { size: 18, strokeWidth: 1.5, color: 'black' }),
		})

		const div = document.createElement('div')
		app.mount(div)

		return {
			title: 'Upload',
			icon: div.innerHTML,
		}
	}

	static get isReadOnlySupported() {
		return true
	}

	render() {
		this.wrapper = document.createElement('div')

		if (this.data && this.data.file_url) {
			this.renderFile(this.data)
		} else {
			this.renderFileUploader()
		}

		return this.wrapper
	}

	renderFile(file: UploadFile) {
		const fileType = file.file_type ?? ''
		if (this.isVideo(fileType)) {
			const app = createApp(VideoBlock, {
				file: file.file_url,
				readOnly: this.readOnly,
				quizzes: file.quizzes || [],
				saveQuizzes: (quizzes: unknown[]) => {
					if (this.readOnly) return
					this.data.quizzes = quizzes
				},
			})
			app.use(translationPlugin)
			app.config.globalProperties.$dialog = createDialog
			app.mount(this.wrapper)
			return
		} else if (this.isAudio(fileType)) {
			const app = createApp(AudioBlock, {
				file: file.file_url,
			})
			app.mount(this.wrapper)
			return
		} else if (fileType == 'PDF') {
			this.wrapper.innerHTML = `<iframe src="${
				window.location.origin
			}${encodeURI(
				file.file_url ?? ''
			)}" width='100%' height='700px' class="mb-4" type="application/pdf"></iframe>`
			return
		} else {
			this.wrapper.innerHTML = `<img class="mb-4" src=${encodeURI(
				file.file_url ?? ''
			)} width='100%'>`
			return
		}
	}

	renderFileUploader() {
		const app = createApp(UploadPlugin, {
			docname: this.config.docname || null,
			fieldname: this.config.fieldname || 'content',
			onFileUploaded: (file: UploadFile) => {
				this.data.file_url = file.file_url
				this.data.file_type = file.file_type
				this.renderFile(file)
			},
		})
		app.use(translationPlugin)
		app.mount(this.wrapper)
	}

	validate(savedData: UploadFile) {
		if (!savedData.file_url || !savedData.file_type) {
			return false
		}
		return true
	}

	save() {
		return {
			file_url: this.data.file_url,
			file_type: this.data.file_type,
			quizzes: this.data.quizzes || [],
		}
	}

	isVideo(type: string) {
		return ['mov', 'mp4', 'avi', 'mkv', 'webm'].includes(type.toLowerCase())
	}

	isAudio(type: string) {
		return ['mp3', 'wav', 'ogg'].includes(type.toLowerCase())
	}
}
