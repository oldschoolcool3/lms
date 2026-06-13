import { CodeXml } from 'lucide-vue-next'
import { createApp, h } from 'vue'
import { escapeHTML } from '@/utils'

interface MarkdownData {
	text?: string
}

interface ParsedBlock {
	type: string
	data: Record<string, unknown>
}

interface ListBlockResult {
	block: ParsedBlock
	nextIndex: number
}

// Minimal view of the Editor.js runtime API surface this tool uses. The full
// API is provided by @editorjs/editorjs at runtime; we type only our usage.
interface EditorBlockApi {
	id: string
	holder: HTMLElement
}

interface EditorApi {
	blocks: {
		getCurrentBlockIndex(): number
		getBlockByIndex(index: number): EditorBlockApi | undefined
		insert(
			type: string,
			data: Record<string, unknown>,
			config: Record<string, unknown>,
			index: number,
			needToFocus: boolean
		): void
		delete(index: number): void
		convert(
			id: string,
			type: string,
			data: Record<string, unknown>
		): Promise<void> | void
	}
	caret: {
		setToBlock(index: number, position: string): void
		focus(atEnd: boolean): void
	}
}

export class Markdown {
	api: EditorApi
	data: MarkdownData
	config: Record<string, unknown>
	readOnly: boolean
	text: string
	placeholder: string
	wrapper!: HTMLDivElement

	constructor({
		data,
		api,
		readOnly,
		config,
	}: {
		data: MarkdownData
		api: EditorApi
		readOnly: boolean
		config?: Record<string, unknown>
	}) {
		this.api = api
		this.data = data || {}
		this.config = config || {}
		this.readOnly = readOnly
		this.text = data.text || ''
		this.placeholder = __("Type '/' for commands or select text to format")
	}

	static get isReadOnlySupported() {
		return true
	}

	static get conversionConfig() {
		return {
			export: 'text',
			import: 'text',
		}
	}

	static get toolbox() {
		const app = createApp({
			render: () => h(CodeXml, { size: 18, strokeWidth: 1.5, color: 'black' }),
		})

		const div = document.createElement('div')
		app.mount(div)
		return { title: '', icon: div.innerHTML }
	}

	static get pasteConfig() {
		return {
			tags: ['P'],
		}
	}

	render() {
		this.wrapper = document.createElement('div')
		this.wrapper.classList.add('cdx-block', 'ce-paragraph')
		this.wrapper.contentEditable = String(!this.readOnly)
		this.wrapper.dataset.placeholder = this.placeholder
		this.wrapper.innerHTML = this.text

		if (!this.readOnly) {
			this.wrapper.addEventListener('focus', () => this._togglePlaceholder())
			this.wrapper.addEventListener('blur', () => this._togglePlaceholder())
			this.wrapper.addEventListener('keydown', (e) => this._onKeyDown(e))
			this.wrapper.addEventListener(
				'paste',
				(e) => this._onNativePaste(e),
				true
			)
		}

		return this.wrapper
	}

	_onNativePaste(event: ClipboardEvent) {
		const clipboardData =
			event.clipboardData ||
			(window as Window & { clipboardData?: DataTransfer }).clipboardData
		if (!clipboardData) return

		const pastedText = clipboardData.getData('text/plain')
		const pastedHTML = clipboardData.getData('text/html')
		const hasHTMLTags = (s: string) => /<(pre|h[1-6]|ul|ol)[\s>]/i.test(s)

		const html =
			(pastedText && hasHTMLTags(pastedText) && pastedText) ||
			(pastedHTML && hasHTMLTags(pastedHTML) && pastedHTML)

		if (html) {
			event.preventDefault()
			event.stopPropagation()
			event.stopImmediatePropagation()

			this._insertBlocks(this._parsePastedHTMLToBlocks(html))
			return
		}

		if (pastedText && this._looksLikeMarkdown(pastedText)) {
			event.preventDefault()
			event.stopPropagation()
			event.stopImmediatePropagation()

			this._insertMarkdownAsBlocks(pastedText)
		}
	}

	_looksLikeMarkdown(text: string) {
		const markdownPatterns = [
			/^#{1,6}\s+/m,
			/^[\-\*]\s+/m,
			/^\d+\.\s+/m,
			/```[\s\S]*```/,
		]

		return markdownPatterns.some((pattern) => pattern.test(text))
	}

	async _insertBlocks(blocks: ParsedBlock[]) {
		if (blocks.length === 0) return

		const currentIndex = this.api.blocks.getCurrentBlockIndex()

		for (let i = 0; i < blocks.length; i++) {
			try {
				await this.api.blocks.insert(
					blocks[i].type,
					blocks[i].data,
					{},
					currentIndex + i,
					false
				)
			} catch (error) {
				console.error('Failed to insert block:', blocks[i], error)
			}
		}

		try {
			await this.api.blocks.delete(currentIndex + blocks.length)
		} catch (e) {
			// original block may already be gone
		}

		setTimeout(() => {
			this.api.caret.setToBlock(currentIndex, 'end')
		}, 100)
	}

	_insertMarkdownAsBlocks(markdown: string) {
		this._insertBlocks(this._parseMarkdownToBlocks(markdown))
	}

	_parseMarkdownToBlocks(markdown: string): ParsedBlock[] {
		const lines = markdown.split('\n')
		const blocks: ParsedBlock[] = []
		let i = 0

		while (i < lines.length) {
			const line = lines[i]

			if (line.trim() === '') {
				i++
				continue
			}

			if (line.trim().startsWith('```')) {
				const codeBlock = this._parseCodeBlock(lines, i)
				blocks.push(codeBlock.block)
				i = codeBlock.nextIndex
				continue
			}

			if (/^#{1,6}\s+/.test(line)) {
				blocks.push(this._parseHeading(line))
				i++
				continue
			}

			if (/^[\s]*[-*+]\s+/.test(line)) {
				const listBlock = this._parseUnorderedList(lines, i)
				blocks.push(listBlock.block)
				i = listBlock.nextIndex
				continue
			}

			if (/^[\s]*(\d+)\.\s+/.test(line)) {
				const listBlock = this._parseOrderedList(lines, i)
				blocks.push(listBlock.block)
				i = listBlock.nextIndex
				continue
			}

			blocks.push({
				type: 'paragraph',
				data: { text: this._parseInlineMarkdown(line) },
			})
			i++
		}

		return blocks
	}

	_parseHeading(line: string): ParsedBlock {
		const match = line.match(/^(#{1,6})\s+(.*)$/)!
		const level = match[1].length
		const text = match[2]

		return {
			type: 'header',
			data: {
				text: this._parseInlineMarkdown(text),
				level: level,
			},
		}
	}

	_parseUnorderedList(lines: string[], startIndex: number): ListBlockResult {
		const items = []
		let i = startIndex

		while (i < lines.length) {
			const line = lines[i]

			if (/^[\s]*[-*+]\s+/.test(line)) {
				const text = line.replace(/^[\s]*[-*+]\s+/, '')
				items.push({
					content: this._parseInlineMarkdown(text),
					items: [],
				})
				i++
			} else if (line.trim() === '') {
				i++
				if (i < lines.length && /^[\s]*[-*+]\s+/.test(lines[i])) {
					continue
				} else {
					break
				}
			} else {
				break
			}
		}

		return {
			block: {
				type: 'list',
				data: {
					style: 'unordered',
					items: items,
				},
			},
			nextIndex: i,
		}
	}

	_parseOrderedList(lines: string[], startIndex: number): ListBlockResult {
		const items = []
		let i = startIndex

		while (i < lines.length) {
			const line = lines[i]

			const match = line.match(/^[\s]*(\d+)\.\s+(.*)$/)

			if (match) {
				const number = match[1]
				const text = match[2]

				if (number === '1') {
					if (items.length > 0) {
						break
					}
				}

				items.push({
					content: this._parseInlineMarkdown(text),
					items: [],
				})
				i++
			} else if (line.trim() === '') {
				i++
				if (i < lines.length && /^[\s]*(\d+)\.\s+/.test(lines[i])) {
					continue
				} else {
					break
				}
			} else {
				break
			}
		}

		return {
			block: {
				type: 'list',
				data: {
					style: 'ordered',
					items: items,
				},
			},
			nextIndex: i,
		}
	}

	_parseCodeBlock(lines: string[], startIndex: number): ListBlockResult {
		let i = startIndex + 1
		const codeLines = []
		const language = lines[startIndex].trim().substring(3).trim()

		while (i < lines.length) {
			if (lines[i].trim().startsWith('```')) {
				i++
				break
			}
			codeLines.push(lines[i])
			i++
		}

		return {
			block: {
				type: 'codeBox',
				data: {
					code: escapeHTML(codeLines.join('\n')),
					language: language || 'plaintext',
				},
			},
			nextIndex: i,
		}
	}

	_parseInlineMarkdown(text: string): string {
		if (!text) return ''

		let html = escapeHTML(text)

		html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')

		html = html.replace(/\*\*([^\*\n]+?)\*\*/g, '<b>$1</b>')
		html = html.replace(/__([^_\n]+?)__/g, '<b>$1</b>')

		html = html.replace(/\*([^\*\n]+?)\*/g, '<i>$1</i>')
		html = html.replace(/(?<!\w)_([^_\n]+?)_(?!\w)/g, '<i>$1</i>')

		html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')

		return html
	}

	_togglePlaceholder() {
		const blocks = document.querySelectorAll<HTMLElement>(
			'.cdx-block.ce-paragraph[data-placeholder]'
		)
		blocks.forEach((block) => {
			if (block !== this.wrapper) delete block.dataset.placeholder
		})

		if (this.wrapper.innerHTML.trim() === '') {
			this.wrapper.dataset.placeholder = this.placeholder
		} else {
			delete this.wrapper.dataset.placeholder
		}
	}

	_onKeyDown(event: KeyboardEvent) {
		const text = this.wrapper.textContent ?? ''

		if (event.key === ' ' && /^#{1,6}$/.test(text)) {
			event.preventDefault()
			const level = text.length
			this.wrapper.textContent = ''
			this._convertBlock('header', { level })
		} else if (event.key === ' ' && text === '-') {
			event.preventDefault()
			this.wrapper.textContent = ''
			this._convertBlock('list', {
				style: 'unordered',
				items: [{ content: '' }],
			})
		} else if (event.key === ' ' && /^1\.$/.test(text)) {
			event.preventDefault()
			this.wrapper.textContent = ''
			this._convertBlock('list', {
				style: 'ordered',
				items: [{ content: '' }],
			})
		} else if (this._isEmbed(text) && event.key === 'Enter') {
			event.preventDefault()
			this.wrapper.textContent = ''
			this._convertBlock('embed', { source: text })
		} else if (event.key === 'Enter') {
			setTimeout(() => this._checkMarkdownAfterEnter(), 0)
		}
	}

	_checkMarkdownAfterEnter() {
		const text = (this.wrapper.textContent ?? '').trim()

		if (this._isImage(text)) {
			this._convertBlock('image', {
				file: { url: this._extractImage(text).url },
			})
		}
	}

	async _convertBlock(type: string, data: Record<string, unknown>) {
		const currentIndex = this.api.blocks.getCurrentBlockIndex()
		const currentBlock = this.api.blocks.getBlockByIndex(currentIndex)

		if (!currentBlock) return

		await this.api.blocks.convert(currentBlock.id, type, data)

		setTimeout(() => {
			const newIndex = this.api.blocks.getCurrentBlockIndex()
			const newBlock = this.api.blocks.getBlockByIndex(newIndex)

			if (newBlock && newBlock.holder) {
				const holder = newBlock.holder.querySelector<HTMLElement>(
					'[contenteditable="true"]'
				)
				if (holder) {
					holder.focus()
					// Place caret at end
					const range = document.createRange()
					range.selectNodeContents(holder)
					range.collapse(false)
					const sel = window.getSelection()
					sel?.removeAllRanges()
					sel?.addRange(range)
				} else {
					this.api.caret.focus(true)
				}
			} else {
				this.api.caret.focus(true)
			}
		}, 0)
	}

	save(blockContent: HTMLElement) {
		return { text: blockContent.innerHTML }
	}

	_isImage(text: string) {
		return /!\[.+?\]\(.+?\)/.test(text)
	}

	_extractImage(text: string): { alt: string; url: string } {
		const match = text.match(/!\[(.+?)\]\((.+?)\)/)
		if (match) return { alt: match[1], url: match[2] }
		return { alt: '', url: '' }
	}

	_isEmbed(text: string) {
		return /^https?:\/\/.+/.test(text.trim())
	}

	_parsePastedHTMLToBlocks(html: string): ParsedBlock[] {
		const doc = new DOMParser().parseFromString(html, 'text/html')
		const blocks: ParsedBlock[] = []

		const walk = (node: Node) => {
			if (node.nodeType === Node.TEXT_NODE) {
				const text = node.textContent?.trim()
				if (text)
					blocks.push({
						type: 'paragraph',
						data: { text: escapeHTML(text) },
					})
				return
			}

			if (node.nodeType !== Node.ELEMENT_NODE) return

			const el = node as Element
			const tag = el.tagName

			if (tag === 'PRE') {
				blocks.push({
					type: 'codeBox',
					data: {
						code: escapeHTML(el.textContent),
						language: 'Auto-detect',
					},
				})
			} else if (/^H[1-6]$/.test(tag)) {
				blocks.push({
					type: 'header',
					data: {
						text: escapeHTML(el.textContent?.trim()),
						level: +tag[1],
					},
				})
			} else if (tag === 'UL' || tag === 'OL') {
				const items = Array.from(el.querySelectorAll(':scope > li')).map(
					(li) => ({
						content: escapeHTML(li.textContent?.trim()),
						items: [],
					})
				)
				blocks.push({
					type: 'list',
					data: {
						style: tag === 'UL' ? 'unordered' : 'ordered',
						items,
					},
				})
			} else if (el.childNodes.length) {
				el.childNodes.forEach((child) => walk(child))
			} else {
				const text = el.textContent?.trim()
				if (text)
					blocks.push({
						type: 'paragraph',
						data: { text: escapeHTML(text) },
					})
			}
		}

		doc.body.childNodes.forEach((child) => walk(child))
		return blocks
	}
}

export default Markdown
