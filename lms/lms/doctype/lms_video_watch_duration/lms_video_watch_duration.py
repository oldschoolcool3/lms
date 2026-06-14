# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LMSVideoWatchDuration(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        chapter: DF.Link | None
        course: DF.Link | None
        lesson: DF.Link
        member: DF.Link
        member_image: DF.AttachImage | None
        member_name: DF.Data | None
        member_username: DF.Data | None
        source: DF.Data
        watch_time: DF.Data
    # end: auto-generated types

    pass
