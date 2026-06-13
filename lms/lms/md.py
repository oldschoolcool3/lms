"""The md module extends markdown to add macros.

Macros can be added to the markdown text in the following format.

    {{ MacroName("macro-argument") }}

These macros will be rendered using a pluggable mechanism.

Apps can provide a hook lms_markdown_macro_renderers, a
dictionary mapping the macro name to the function that to render
that macro. The function will get the argument passed to the macro
as argument.
"""

import re
import xml.etree.ElementTree as etree

import frappe
import markdown
from bs4 import BeautifulSoup
from markdown import Extension
from markdown.inlinepatterns import InlineProcessor


def markdown_to_html(text):
    """Render markdown text into html."""
    return markdown.markdown(text, extensions=["fenced_code", MacroExtension()])


def find_macros(text):
    """Return all macros in the given text.

    >>> find_macros(text)
    [
        ('YouTubeVideo': 'abcd1234')
        ('Exercise', 'two-circles'),
        ('Exercise', 'four-circles')
    ]
    """
    if not text:
        return []
    macros = re.findall(MACRO_RE, text)
    # remove the quotes around the argument
    return [(name, _remove_quotes(arg)) for name, arg in macros]


def _remove_quotes(value):
    """Remove quotes around a value.

    Also strips the whitespace.

        >>> _remove_quotes('"hello"')
        'hello'
        >>> _remove_quotes("'hello'")
        'hello'
        >>> _remove_quotes("hello")
        'hello'
    """
    return value.strip(" '\"")


def get_macro_registry():
    """Return a mapping of macro name to its renderer function from the hook registry."""
    d = frappe.get_hooks("lms_markdown_macro_renderers") or {}
    return {name: frappe.get_attr(klass[0]) for name, klass in d.items()}


def render_macro(macro_name, macro_argument):
    """Render a macro to html via its registered renderer, or a fallback for unknown macros."""
    # stripping the quotes on either side of the argument
    macro_argument = _remove_quotes(macro_argument)

    registry = get_macro_registry()
    if macro_name in registry:
        return registry[macro_name](macro_argument)
    else:
        return f"<p>Unknown macro: {macro_name}</p>"


MACRO_RE = r"{{ *(\w+)\(([^{}]*)\) *}}"


class MacroExtension(Extension):
    """MacroExtension is a markdown extension to support macro syntax."""

    def extendMarkdown(self, md):
        """Register the macro inline processor on the given markdown instance."""
        self.md = md
        pattern = MacroInlineProcessor(MACRO_RE)
        pattern.md = md
        md.inlinePatterns.register(pattern, "macro", 75)


class MacroInlineProcessor(InlineProcessor):
    """Render each macro occurrence in the markdown text as an etree node."""

    def handleMatch(self, m, data):
        """Handle each macro match and return its rendered contents as an etree node."""
        macro = m.group(1)
        arg = m.group(2)
        html = render_macro(macro, arg)
        html = sanitize_html(str(html), macro)
        e = etree.fromstring(html)  # noqa: S314 — html is sanitized by sanitize_html() above
        return e, m.start(0), m.end(0)


def sanitize_html(html, macro):
    """Sanitize the html using BeautifulSoup.

    The markdown processor request the correct markup and crashes on
    any broken tags. This makes sures that all those things are fixed
    before passing to the etree parser.
    """
    soup = BeautifulSoup(html, features="lxml")
    nodes = soup.body.children
    classname = ""
    if macro == "YouTubeVideo":
        classname = "lesson-video"

    return "<div class='" + classname + "'>" + "\n".join(str(node) for node in nodes) + "</div>"
