<template>
	<FileUploader
		:fileTypes="['image/*', 'video/*', 'audio/*', '.pdf']"
		:uploadArgs="uploadArgs"
		:validateFile="validateFile"
		@success="addFile"
		ref="fileUploader"
		class="hide"
	/>
</template>
<script setup lang="ts">
import { FileUploader } from 'frappe-ui'
import { onMounted, ref, nextTick, computed } from 'vue'

const fileUploader = ref()
const emit = defineEmits(['fileUploaded'])

const props = defineProps({
	onFileUploaded: {
		type: Function,
		required: true,
	},
	docname: {
		type: String,
		default: null,
	},
	fieldname: {
		type: String,
		default: 'content',
	},
})

const uploadArgs = computed(() => ({
	private: true,
	doctype: 'Course Lesson',
	docname: props.docname,
	fieldname: props.fieldname,
}))

onMounted(async () => {
	await nextTick()
	const fileInput = fileUploader.value.$el.querySelector('input[type="file"]')
	if (fileInput) {
		fileInput.click()
	}
})

const addFile = (file: { file_url: string; file_type: string }) => {
	props.onFileUploaded({
		file_url: file.file_url,
		file_type: file.file_type,
	})
}

const validateFile = (file: File) => {
	let extension = (file.name.split('.').pop() ?? '').toLowerCase()
	if (!['jpg', 'jpeg', 'png', 'mp4', 'mov', 'mp3', 'pdf'].includes(extension)) {
		return 'Only image and video files are allowed.'
	}
}

const isVideo = (type: string) => {
	return ['mov', 'mp4', 'avi', 'mkv', 'webm'].includes(type.toLowerCase())
}

const isAudio = (type: string) => {
	return ['mp3', 'wav', 'ogg'].includes(type.toLowerCase())
}
</script>
