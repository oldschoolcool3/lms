# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LMSProgrammingExerciseSubmission(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from lms.lms.doctype.lms_test_case_submission.lms_test_case_submission import LMSTestCaseSubmission

        code: DF.Code
        exercise: DF.Link
        exercise_title: DF.Data | None
        member: DF.Link
        member_image: DF.Attach | None
        member_name: DF.Data | None
        status: DF.Literal["", "Passed", "Failed"]
        test_cases: DF.Table[LMSTestCaseSubmission]
    # end: auto-generated types

    pass
