# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

from typing import TYPE_CHECKING, cast

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, get_link_to_form, getdate, validate_url
from frappe.utils.user import get_system_managers

from lms.lms.utils import generate_slug, validate_image

if TYPE_CHECKING:
    from frappe.utils.data import DateTimeLikeObject


class JobOpportunity(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        company_email_address: DF.Data
        company_logo: DF.AttachImage
        company_name: DF.Data
        company_website: DF.Data
        country: DF.Link
        description: DF.TextEditor
        job_title: DF.Data
        location: DF.Data
        status: DF.Literal["Open", "Closed"]
        type: DF.Literal["Full Time", "Part Time", "Freelance", "Contract"]
        work_mode: DF.Literal["", "Remote", "Hybrid", "On-site"]
    # end: auto-generated types

    def validate(self):
        self.validate_urls()
        self.company_logo = validate_image(self.company_logo)

    def validate_urls(self):
        validate_url(self.company_website, True, ["http", "https"])

    def autoname(self):
        if not self.name:
            self.name = generate_slug(f"{self.job_title}-${self.company_name}", "LMS Course")


def update_job_openings():
    old_jobs = frappe.get_all(
        "Job Opportunity",
        filters={"status": "Open", "creation": ["<=", add_months(cast("DateTimeLikeObject", getdate()), -3)]},
        pluck="name",
    )

    for job in old_jobs:
        frappe.db.set_value("Job Opportunity", job, "status", "Closed")


@frappe.whitelist()
def report(job: str, reason: str):
    system_managers = get_system_managers(only_name=True)
    user = frappe.db.get_value("User", frappe.session.user, "full_name")
    subject = _("User {0} has reported the job post {1}").format(user, job)
    args = {
        "job": job,
        "job_url": get_link_to_form("Job Opportunity", job),
        "user": user,
        "reason": reason,
    }
    frappe.sendmail(
        recipients=system_managers,
        subject=subject,
        header=[subject, "green"],
        template="job_report",
        args=args,
        now=True,
    )
