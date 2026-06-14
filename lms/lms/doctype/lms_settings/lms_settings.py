# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url_to_list, validate_email_address, validate_url


class LMSSettings(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from lms.lms.doctype.lms_sidebar_item.lms_sidebar_item import LMSSidebarItem
        from lms.lms.doctype.payment_country.payment_country import PaymentCountry

        allow_guest_access: DF.Check
        allow_job_posting: DF.Check
        apply_gst: DF.Check
        apply_rounding: DF.Check
        batch_confirmation_template: DF.Link | None
        batches: DF.Check
        certification_template: DF.Link | None
        certifications: DF.Check
        certified_members: DF.Check
        contact_us_email: DF.Data | None
        contact_us_url: DF.Data | None
        courses: DF.Check
        custom_signup_content: DF.HTMLEditor | None
        default_currency: DF.Link | None
        default_home: DF.Check
        demo_data_present: DF.Check
        disable_pwa: DF.Check
        disable_signup: DF.Check
        enforce_assignment_completion: DF.Check
        enforce_quiz_completion: DF.Check
        enforce_video_completion: DF.Check
        exception_country: DF.TableMultiSelect[PaymentCountry]
        jobs: DF.Check
        lesson_dwell_time: DF.Int
        livecode_url: DF.Data | None
        mentor_request_creation: DF.Link | None
        mentor_request_status_update: DF.Link | None
        meta_description: DF.SmallText | None
        meta_image: DF.AttachImage | None
        meta_keywords: DF.SmallText | None
        notifications: DF.Check
        payment_gateway: DF.Data | None
        payment_reminder_template: DF.Link | None
        persona_captured: DF.Check
        prevent_skipping_videos: DF.Check
        programming_exercises: DF.Check
        send_calendar_invite_for_evaluations: DF.Check
        send_notification_for_published_batches: DF.Literal["", "Email", "In-app"]
        send_notification_for_published_courses: DF.Literal["", "Email", "In-app"]
        send_payment_reminders_for_batch: DF.Check
        send_payment_reminders_for_course: DF.Check
        show_assessments: DF.Check
        show_courses: DF.Check
        show_dashboard: DF.Check
        show_day_view: DF.Check
        show_discussions: DF.Check
        show_emails: DF.Check
        show_live_class: DF.Check
        show_students: DF.Check
        show_usd_equivalent: DF.Check
        sidebar_items: DF.Table[LMSSidebarItem]
        statistics: DF.Check
        unsplash_access_key: DF.Data | None
        user_category: DF.Check
    # end: auto-generated types

    def validate(self):
        self.validate_google_settings()
        self.validate_signup()
        self.validate_contact_us_details()

    def validate_google_settings(self):
        if self.send_calendar_invite_for_evaluations:
            google_settings = frappe.get_single("Google Settings")

            if not google_settings.enable:
                frappe.throw(_("Enable Google API in Google Settings to send calendar invites for evaluations."))

            if not google_settings.client_id or not google_settings.client_secret:
                frappe.throw(
                    _("Enter Client Id and Client Secret in Google Settings to send calendar invites for evaluations.")
                )

            calendars = frappe.db.count("Google Calendar")
            if not calendars:
                frappe.throw(
                    _(
                        "Please add <a href='{0}'>{1}</a> for <a href='{2}'>{3}</a> to send calendar invites for evaluations."  # noqa: E501 — translatable message; keep msgid on one line
                    ).format(
                        get_url_to_list("Google Calendar"),
                        frappe.bold("Google Calendar"),
                        get_url_to_list("Course Evaluator"),
                        frappe.bold("Course Evaluator"),
                    )
                )

    def validate_signup(self):
        if self.has_value_changed("disable_signup"):
            frappe.db.set_single_value("Website Settings", "disable_signup", self.disable_signup)

    def validate_contact_us_details(self):
        if self.contact_us_email and not validate_email_address(self.contact_us_email):
            frappe.throw(_("Please enter a valid Contact Us Email."))
        if self.contact_us_url and not validate_url(self.contact_us_url, True, ["http", "https"]):
            frappe.throw(_("Please enter a valid Contact Us URL."))


@frappe.whitelist()
def check_payments_app():
    installed_apps = frappe.get_installed_apps()
    if "payments" not in installed_apps:
        return False
    else:
        filters = {
            "doctype_or_field": "DocField",
            "doc_type": "LMS Settings",
            "field_name": "payment_gateway",
        }
        if frappe.db.exists("Property Setter", filters):
            return True

        link_property = frappe.new_doc("Property Setter")
        link_property.update(filters)
        link_property.property = "fieldtype"
        link_property.value = "Link"
        link_property.save()

        options_property = frappe.new_doc("Property Setter")
        options_property.update(filters)
        options_property.property = "options"
        options_property.value = "Payment Gateway"
        options_property.save()

        return True
