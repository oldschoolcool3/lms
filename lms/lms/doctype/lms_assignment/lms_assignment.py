# Copyright (c) 2023, Frappe and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class LMSAssignment(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        answer: DF.TextEditor | None
        course: DF.Link | None
        grade_assignment: DF.Check
        question: DF.TextEditor
        show_answer: DF.Check
        title: DF.Data
        type: DF.Literal["Document", "PDF", "URL", "Image", "Text"]
    # end: auto-generated types

    pass
