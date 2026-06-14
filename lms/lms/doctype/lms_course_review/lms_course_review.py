# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class LMSCourseReview(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        course: DF.Link
        rating: DF.Rating
        review: DF.SmallText | None
    # end: auto-generated types

    def validate(self):
        self.validate_enrollment()
        self.validate_if_already_reviewed()

    def validate_enrollment(self):
        enrollment = frappe.db.exists("LMS Enrollment", {"course": self.course, "member": self.owner})
        if not enrollment:
            frappe.throw(_("You must be enrolled in the course to submit a review"))

    def validate_if_already_reviewed(self):
        if frappe.db.exists("LMS Course Review", {"course": self.course, "owner": self.owner}):
            frappe.throw(_("You have already reviewed this course"))
