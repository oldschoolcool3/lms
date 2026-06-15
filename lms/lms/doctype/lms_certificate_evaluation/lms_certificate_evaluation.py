# Copyright (c) 2022, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

from lms.lms.utils import has_moderator_role


class LMSCertificateEvaluation(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        batch_name: DF.Link | None
        course: DF.Link
        date: DF.Date
        end_time: DF.Time | None
        evaluator: DF.Link | None
        evaluator_name: DF.Data | None
        member: DF.Link
        member_name: DF.Data | None
        rating: DF.Rating
        start_time: DF.Time
        status: DF.Literal["Pending", "In Progress", "Pass", "Fail"]
        summary: DF.SmallText | None
    # end: auto-generated types

    def validate(self):
        self.validate_rating()

    def validate_rating(self):
        if self.status not in ["Pending", "In Progress"] and self.rating == 0:
            frappe.throw(_("Rating cannot be 0"))


def has_website_permission(doc, ptype, user, verbose=False):
    if has_moderator_role() or doc.member == frappe.session.user:
        return True
    return False


@frappe.whitelist()
def create_lms_certificate(source_name: str, target_doc: "dict | None" = None):
    doc = get_mapped_doc(
        "LMS Certificate Evaluation",
        source_name,
        {"LMS Certificate Evaluation": {"doctype": "LMS Certificate"}},
        target_doc,
    )
    return doc
