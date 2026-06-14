# Copyright (c) 2023, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LMSBatchTimetable(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        date: DF.Date | None
        day: DF.Int
        duration: DF.Data | None
        end_time: DF.Time | None
        milestone: DF.Check
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        reference_docname: DF.DynamicLink | None
        reference_doctype: DF.Link | None
        start_time: DF.Time | None
    # end: auto-generated types

    pass
