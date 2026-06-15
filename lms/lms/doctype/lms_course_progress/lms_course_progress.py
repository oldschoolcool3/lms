# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

from typing import cast

import frappe
from frappe import _
from frappe.model.document import Document

from lms.lms.utils import recalculate_course_progress


class LMSCourseProgress(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        chapter: DF.Link | None
        course: DF.Link | None
        is_scorm_chapter: DF.Check
        lesson: DF.Link | None
        member: DF.Link | None
        member_name: DF.Data | None
        scorm_content: DF.LongText | None
        status: DF.Literal["Complete", "Partially Complete", "Incomplete"]
    # end: auto-generated types

    def before_insert(self):
        if (
            self.member
            and self.lesson
            and frappe.db.exists("LMS Course Progress", {"member": self.member, "lesson": self.lesson})
        ):
            frappe.throw(
                _("Progress is already recorded for this lesson."),
                frappe.UniqueValidationError,
            )

    def on_update(self):
        recalculate_course_progress(cast("str", self.course), cast("str", self.member))

    def after_delete(self):
        recalculate_course_progress(cast("str", self.course), cast("str", self.member))
