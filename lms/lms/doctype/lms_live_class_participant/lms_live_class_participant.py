# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LMSLiveClassParticipant(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        duration: DF.Int
        joined_at: DF.Datetime
        left_at: DF.Datetime
        live_class: DF.Link
        member: DF.Link
        member_image: DF.AttachImage | None
        member_name: DF.Data | None
        member_username: DF.Data | None
    # end: auto-generated types

    pass
