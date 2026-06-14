# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, nowdate


class LMSCoupon(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from lms.lms.doctype.lms_coupon_item.lms_coupon_item import LMSCouponItem

        applicable_items: DF.Table[LMSCouponItem]
        code: DF.Data
        discount_type: DF.Literal["Percentage", "Fixed Amount"]
        enabled: DF.Check
        expires_on: DF.Date | None
        fixed_amount_discount: DF.Int
        percentage_discount: DF.Int
        redemption_count: DF.Int
        usage_limit: DF.Int
    # end: auto-generated types

    def validate(self):
        self.convert_to_uppercase()
        self.validate_expiry_date()
        self.validate_applicable_items()
        self.validate_usage_limit()

    def convert_to_uppercase(self):
        if self.code:
            self.code = self.code.strip().upper()

    def validate_expiry_date(self):
        if not self.enabled:
            return

        if self.expires_on and str(self.expires_on) < nowdate():
            frappe.throw(_("Expiry date cannot be in the past"))

    def validate_applicable_items(self):
        if not self.get("applicable_items") or len(self.get("applicable_items")) == 0:
            frappe.throw(_("At least one applicable item is required"))

    def validate_usage_limit(self):
        if self.usage_limit is not None and cint(self.usage_limit) < 0:
            frappe.throw(_("Usage limit cannot be negative"))
