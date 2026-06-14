# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from lms.lms.utils import get_lesson_count


class CourseChapter(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from lms.lms.doctype.lesson_reference.lesson_reference import LessonReference

        course: DF.Link
        course_title: DF.Data | None
        is_scorm_package: DF.Check
        launch_file: DF.Code | None
        lessons: DF.Table[LessonReference]
        manifest_file: DF.Code | None
        scorm_package: DF.Link | None
        scorm_package_path: DF.Code | None
        title: DF.Data
    # end: auto-generated types

    def on_update(self):
        self.update_lesson_count()

    def update_lesson_count(self):
        """Update lesson count in the course"""
        frappe.db.set_value("LMS Course", self.course, "lessons", get_lesson_count(self.course))
