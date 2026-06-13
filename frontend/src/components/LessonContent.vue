<template>
	<div v-if="youtube">
		<iframe
			class="youtube-video"
			:src="getYouTubeVideoSource(youtube.split('/').pop()!)"
			width="100%"
			:height="videoHeight"
			frameborder="0"
			allowfullscreen
		></iframe>
	</div>
	<div v-for="(block, index) in content?.split('\n\n')" :key="index">
		<div v-if="block.includes('{{ YouTubeVideo')">
			<iframe
				class="youtube-video"
				:src="getYouTubeVideoSource(block)"
				width="100%"
				:height="videoHeight"
				frameborder="0"
				allowfullscreen
			></iframe>
		</div>
		<div v-else-if="block.includes('{{ Quiz')">
			<Quiz :quiz="getId(block)" />
		</div>
		<div v-else-if="block.includes('{{ Video')">
			<video
				controls
				width="100%"
				controlsList="nodownload"
				oncontextmenu="return false"
			>
				<source :src="getId(block)" type="video/mp4" />
			</video>
		</div>
		<div v-else-if="block.includes('{{ PDF')">
			<iframe
				:src="getPDFSource(block)"
				width="100%"
				height="700px"
				frameborder="0"
				allowfullscreen
			></iframe>
		</div>
		<div v-else-if="block.includes('{{ Audio')">
			<audio width="100%" controls controlsList="nodownload">
				<source :src="getId(block)" type="audio/mp3" />
			</audio>
		</div>
		<div v-else-if="block.includes('{{ Embed')">
			<iframe
				width="100%"
				height="400"
				:src="getId(block)"
				frameborder="0"
				allowfullscreen
			>
			</iframe>
		</div>
		<div v-else v-html="renderSafe(block)"></div>
	</div>
	<div v-if="quizId">
		<Quiz :quiz="quizId" />
	</div>
</template>
<script setup lang="ts">
import Quiz from '@/components/QuizBlock.vue'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import { computed } from 'vue'
import { useScreenSize } from '@/utils/composables'

const screenSize = useScreenSize()

// NOTE (pre-existing): useScreenSize() returns { size, isMobile }, so
// `screenSize.width` is undefined and this ternary always evaluates to 400.
// Preserved verbatim — this is a conversion-only change, not a bug fix.
const videoHeight = computed(() =>
	(screenSize as { width?: number }).width! < 640 ? 200 : 400
)

const markdown = new MarkdownIt({
	html: true,
	linkify: true,
})

const renderSafe = (block: string) => DOMPurify.sanitize(markdown.render(block))

defineProps({
	content: {
		type: String,
		required: true,
	},
	youtube: {
		type: String,
		required: false,
	},
	quizId: {
		type: String,
		required: false,
	},
})

const getYouTubeVideoSource = (block: string) => {
	if (block.includes('{{')) {
		block = getId(block)
	}
	return `https://www.youtube.com/embed/${block}`
}

const getPDFSource = (block: string) => {
	return `${getId(block)}#toolbar=0`
}

const getId = (block: string) => {
	return block.match(/\(["']([^"']+?)["']\)/)![1]
}
</script>
