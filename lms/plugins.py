"""The plugins module provides various plugins to change the default behaviour some parts of the lms app.

A site specify what plugins to use using appropriate entries in the frappe
hooks, written in the `hooks.py`.

This module exposes two plugins: ProfileTab and PageExtension.

The ProfileTab is used to specify any additional tabs to be displayed
on the profile page of the user.

The PageExtension is used to load additinal stylesheets and scripts to
be loaded in a webpage.
"""

from urllib.parse import quote

import frappe
from frappe import _


class PageExtension:
    """PageExtension is a plugin to inject custom styles and scripts into a web page.

    The subclasses should overwrite the `render_header()` and
    `render_footer()` methods to inject whatever styles/scripts into
    the webpage.
    """

    def __init__(self):
        self.context = frappe._dict()

    def set_context(self, context):
        """Set the page context made available to header and footer rendering."""
        self.context = context

    def render_header(self):
        """Return the HTML snippet to be included in the head section of the web page.

        Typically used to include the stylesheets and javascripts to be
        included in the <head> of the webpage.
        """
        return ""

    def render_footer(self):
        """Return the HTML snippet to be included in the body tag at the end of web page.

        Typically used to include javascripts that need to be executed
        after the page is loaded.
        """
        return ""


class ProfileTab:
    """Base class for profile tabs.

    Every subclass of ProfileTab must implement two methods:
        - get_title()
        - render()
    """

    def __init__(self, user):
        self.user = user

    def get_title(self):
        """Return the title of the tab.

        Every subclass must implement this.
        """
        raise NotImplementedError()

    def render(self):
        """Render the contents of the tab as HTML.

        Every subclass must implement this.
        """
        raise NotImplementedError()


class LiveCodeExtension(PageExtension):
    """Page extension that injects the LiveCode editor styles and scripts into a web page."""

    def render_header(self):
        """Return the rendered LiveCode header HTML snippet for the page head."""
        livecode_url = frappe.get_value("LMS Settings", None, "livecode_url")
        context = {"livecode_url": livecode_url}
        return frappe.render_template("templates/livecode/extension_header.html", context)

    def render_footer(self):
        """Return the rendered LiveCode footer HTML snippet for the end of the page body."""
        livecode_url = frappe.get_value("LMS Settings", None, "livecode_url")
        context = {"livecode_url": livecode_url}
        return frappe.render_template("templates/livecode/extension_footer.html", context)


def quiz_renderer(quiz_name):
    """Return the rendered HTML for a quiz, including its questions and the user's submissions."""
    if frappe.session.user == "Guest":
        return (
            " <div class='alert alert-info'>"
            + _("Quiz is not available to Guest users. Please login to continue.")
            + "</div>"
        )

    quiz = frappe.db.get_value(
        "LMS Quiz",
        quiz_name,
        [
            "name",
            "title",
            "max_attempts",
            "show_answers",
            "show_submission_history",
            "passing_percentage",
        ],
        as_dict=True,
    )
    from lms.lms.doctype.lms_question.lms_question import (
        QUESTION_CORRECTNESS_FIELDS,
        QUESTION_EXPLANATION_FIELDS,
        QUESTION_OPTION_FIELDS,
        QUESTION_POSSIBILITY_FIELDS,
    )

    quiz.questions = []
    fields = [
        "name",
        "question",
        "type",
        "multiple",
        *QUESTION_OPTION_FIELDS,
        *QUESTION_CORRECTNESS_FIELDS,
        *QUESTION_EXPLANATION_FIELDS,
        *QUESTION_POSSIBILITY_FIELDS,
    ]

    questions = frappe.get_all(
        "LMS Quiz Question",
        filters={"parent": quiz.name},
        fields=["question", "marks"],
        order_by="idx",
    )

    for question in questions:
        details = frappe.db.get_value("LMS Question", question.question, fields, as_dict=1)
        details["marks"] = question.marks
        quiz.questions.append(details)

    no_of_attempts = frappe.db.count("LMS Quiz Submission", {"owner": frappe.session.user, "quiz": quiz_name})

    if quiz.show_submission_history:
        all_submissions = frappe.get_all(
            "LMS Quiz Submission",
            {
                "quiz": quiz.name,
                "member": frappe.session.user,
            },
            ["name", "score", "creation"],
            order_by="creation desc",
        )

    # SSTI false positive (reviewed): literal template path, not user input.
    return frappe.render_template(  # nosemgrep: frappe-semgrep-rules.rules.security.frappe-ssti
        "templates/quiz/quiz.html",
        {
            "quiz": quiz,
            "no_of_attempts": no_of_attempts,
            "all_submissions": all_submissions if quiz.show_submission_history else None,
            "hide_quiz": False,
        },
    )


def exercise_renderer(argument):
    """Return the rendered HTML for the given LMS Exercise."""
    exercise = frappe.get_doc("LMS Exercise", argument)
    context = dict(exercise=exercise)
    return frappe.render_template("templates/exercise.html", context)


def youtube_video_renderer(video_id):
    """Return an iframe embedding the given YouTube video."""
    return f"""
    <iframe width="100%" height="400"
        src="https://www.youtube.com/embed/{video_id}"
        title="YouTube video player"
        frameborder="0"
        class="youtube-video
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
    </iframe>
    """


def embed_renderer(details):
    """Return an iframe embedding the source and type encoded in the details string."""
    type = details.split("|||")[0]
    src = details.split("|||")[1]
    width = "100%"
    height = "400"

    if type == "pdf":
        width = "75%"
        height = "600"

    return f"""
	<iframe width={width} height={height}
		src={src}
		title="Embedded Content"
		frameborder="0"
		style="border-radius: var(--border-radius-lg)"
		allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
		allowfullscreen>
	</iframe>
	"""


def video_renderer(src):
    """Return an HTML video player for the given source URL."""
    return (
        f"<video controls width='100%' controls controlsList='nodownload'>"
        f"<source src={quote(src)} type='video/mp4'></video>"
    )


def audio_renderer(src):
    """Return an HTML audio player for the given source URL."""
    return f"<audio width='100%' controls controlsList='nodownload'><source src={quote(src)} type='audio/mp3'></audio>"


def pdf_renderer(src):
    """Return an iframe embedding the PDF at the given source URL."""
    return f"<iframe src='{quote(src)}#toolbar=0' width='100%' height='700px'></iframe>"


def assignment_renderer(detail):
    """Return the rendered HTML for an assignment question and its accepted upload types."""
    supported_types = {
        "Document": (
            ".doc,.docx,.xml,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        "PDF": ".pdf",
        "Image": ".png, .jpg, .jpeg",
        "Video": "video/*",
    }
    question = detail.split("-")[0]
    file_type = detail.split("-")[1]
    accept = supported_types[file_type] if file_type else ""
    # SSTI false positive (reviewed): literal template path, not user input.
    return frappe.render_template(  # nosemgrep: frappe-semgrep-rules.rules.security.frappe-ssti
        "templates/assignment.html",
        {"question": question, "accept": accept, "file_type": file_type},
    )


def show_custom_signup():
    """Return the signup template path, preferring the custom signup form when configured."""
    settings = frappe.get_single("LMS Settings")
    if settings.custom_signup_content or settings.user_category:
        return "lms/templates/signup-form.html"
    return "frappe/templates/signup.html"
