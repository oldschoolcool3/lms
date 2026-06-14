# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class LMSProgrammingExercise(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from lms.lms.doctype.lms_test_case.lms_test_case import LMSTestCase

        language: DF.Literal["Python", "JavaScript", "Rust", "Go"]
        problem_statement: DF.TextEditor
        test_cases: DF.Table[LMSTestCase]
        title: DF.Data
    # end: auto-generated types

    def validate(self):
        self.validate_test_cases()

    def validate_test_cases(self):
        if not self.test_cases:
            frappe.throw(_("At least one test case is required for the programming exercise."))
