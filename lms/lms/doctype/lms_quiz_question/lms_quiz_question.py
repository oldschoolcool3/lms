# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LMSQuizQuestion(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        marks: DF.Int
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        question: DF.Link
        question_detail: DF.Text | None
        type: DF.Literal["Choices", "User Input", "Open Ended"]
    # end: auto-generated types

    pass
