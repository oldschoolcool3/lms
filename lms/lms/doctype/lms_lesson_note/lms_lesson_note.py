# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LMSLessonNote(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        color: DF.Literal["Red", "Blue", "Green", "Yellow", "Purple"]
        course: DF.Link | None
        highlighted_text: DF.SmallText | None
        lesson: DF.Link
        member: DF.Link
        note: DF.TextEditor | None
    # end: auto-generated types

    pass
