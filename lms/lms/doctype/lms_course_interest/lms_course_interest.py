# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class LMSCourseInterest(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        course: DF.Link | None
        email_sent: DF.Check
        user: DF.Link | None
    # end: auto-generated types

    pass
