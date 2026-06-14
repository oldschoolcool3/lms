# Copyright (c) 2023, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ScheduledFlow(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        date: DF.Date
        end_time: DF.Time | None
        lesson: DF.Link
        lesson_title: DF.Data | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        start_time: DF.Time | None
    # end: auto-generated types

    pass
