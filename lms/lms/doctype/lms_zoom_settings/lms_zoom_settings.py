# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LMSZoomSettings(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        account_id: DF.Data
        account_name: DF.Data
        client_id: DF.Data
        client_secret: DF.Password
        enabled: DF.Check
        member: DF.Link
        member_image: DF.AttachImage | None
        member_name: DF.Data | None
    # end: auto-generated types

    pass
