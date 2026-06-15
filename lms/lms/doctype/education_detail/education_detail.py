# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EducationDetail(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        degree_type: DF.Data
        end_date: DF.Date | None
        grade: DF.Data | None
        grade_type: DF.Literal[
            "Percentage (e.g. 70%)",
            "Point of Score (e.g. 70)",
            "Letter Grade (e.g. A, B-)",
            "UK Grading  (e.g. 1st, 2:2)",
            "French (e.g. Distinction)",  # type: ignore[reportUndefinedVariable]  # DF.Literal option, not a forward ref
            "CGPA/4",
        ]
        institution_name: DF.Data
        location: DF.Data
        major: DF.Data
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        start_date: DF.Date | None
    # end: auto-generated types

    pass
