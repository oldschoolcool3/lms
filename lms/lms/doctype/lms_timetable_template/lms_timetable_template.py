# Copyright (c) 2023, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LMSTimetableTemplate(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from lms.lms.doctype.lms_batch_timetable.lms_batch_timetable import LMSBatchTimetable
        from lms.lms.doctype.lms_timetable_legend.lms_timetable_legend import LMSTimetableLegend

        timetable: DF.Table[LMSBatchTimetable]
        timetable_legends: DF.Table[LMSTimetableLegend]
        title: DF.Data | None
    # end: auto-generated types

    pass
