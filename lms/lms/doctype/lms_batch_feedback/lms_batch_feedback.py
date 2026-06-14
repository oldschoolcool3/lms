# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LMSBatchFeedback(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        batch: DF.Link
        content: DF.Rating
        feedback: DF.SmallText
        instructors: DF.Rating
        member: DF.Link
        member_image: DF.AttachImage | None
        member_name: DF.Data | None
        value: DF.Rating
    # end: auto-generated types

    pass
