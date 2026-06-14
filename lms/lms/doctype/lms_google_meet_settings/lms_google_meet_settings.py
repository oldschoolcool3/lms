# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LMSGoogleMeetSettings(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        account_name: DF.Data
        enabled: DF.Check
        google_calendar: DF.Link
        member: DF.Link
        member_image: DF.AttachImage | None
        member_name: DF.Data | None
    # end: auto-generated types

    pass
