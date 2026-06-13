import frappe
from frappe.permissions import add_permission, update_permission_property

from lms.lms.api import give_discussions_permission


def after_install():
    """Run post-install setup: seed batch sources and grant baseline permissions."""
    create_batch_source()
    give_discussions_permission()
    give_user_list_permission()
    give_event_permission()


def after_sync():
    """Create LMS roles, set the default certificate print format, and assign roles to Administrator."""
    create_lms_roles()
    set_default_certificate_print_format()
    give_lms_roles_to_admin()


def before_uninstall():
    """Remove LMS custom fields and roles before the app is uninstalled."""
    delete_custom_fields()
    delete_lms_roles()


def create_lms_roles():
    """Create the Course Creator, Moderator, Batch Evaluator, and LMS Student roles."""
    create_course_creator_role()
    create_moderator_role()
    create_evaluator_role()
    create_lms_student_role()


def create_course_creator_role():
    """Create the Course Creator role without desk access, or clear its desk access if it exists."""
    if frappe.db.exists("Role", "Course Creator"):
        frappe.db.set_value("Role", "Course Creator", "desk_access", 0)
    else:
        role = frappe.get_doc(
            {
                "doctype": "Role",
                "role_name": "Course Creator",
                "home_page": "",
                "desk_access": 0,
            }
        )
        role.save()


def create_moderator_role():
    """Create the Moderator role without desk access, or clear its desk access if it exists."""
    if frappe.db.exists("Role", "Moderator"):
        frappe.db.set_value("Role", "Moderator", "desk_access", 0)
    else:
        role = frappe.get_doc(
            {
                "doctype": "Role",
                "role_name": "Moderator",
                "home_page": "",
                "desk_access": 0,
            }
        )
        role.save()


def create_evaluator_role():
    """Create the Batch Evaluator role without desk access, or clear its desk access if it exists."""
    if frappe.db.exists("Role", "Batch Evaluator"):
        frappe.db.set_value("Role", "Batch Evaluator", "desk_access", 0)
    else:
        role = frappe.new_doc("Role")
        role.update(
            {
                "role_name": "Batch Evaluator",
                "home_page": "",
                "desk_access": 0,
            }
        )
        role.save()


def create_lms_student_role():
    """Create the LMS Student role without desk access, or clear its desk access if it exists."""
    if frappe.db.exists("Role", "LMS Student"):
        frappe.db.set_value("Role", "LMS Student", "desk_access", 0)
    else:
        role = frappe.new_doc("Role")
        role.update(
            {
                "role_name": "LMS Student",
                "home_page": "",
                "desk_access": 0,
            }
        )
        role.save()


def set_default_certificate_print_format():
    """Set the default print format for LMS Certificate via a Property Setter if not already set."""
    filters = {
        "doc_type": "LMS Certificate",
        "property": "default_print_format",
    }
    if not frappe.db.exists("Property Setter", filters):
        filters.update(
            {
                "doctype_or_field": "DocType",
                "property_type": "Data",
                "value": "Certificate",
            }
        )

        doc = frappe.new_doc("Property Setter")
        doc.update(filters)
        doc.save()


def delete_custom_fields():
    """Delete the User custom fields added by the LMS app."""
    fields = [
        "user_category",
        "headline",
        "college",
        "city",
        "verify_terms",
        "country",
        "preferred_location",
        "preferred_functions",
        "preferred_industries",
        "work_environment_column",
        "time",
        "role",
        "carrer_preference_details",
        "skill",
        "certification_details",
        "internship",
        "branch",
        "github",
        "medium",
        "linkedin",
        "profession",
        "open_to",
        "cover_image",
        "work_environment",
        "dream_companies",
        "career_preference_column",
        "attire",
        "collaboration",
        "location_preference",
        "company_type",
        "skill_details",
        "certification",
        "education",
        "work_experience",
        "education_details",
        "hide_private",
        "work_experience_details",
        "profile_complete",
    ]

    for field in fields:
        frappe.db.delete("Custom Field", {"fieldname": field})


def create_batch_source():
    """Seed the default LMS Source records used as batch lead sources."""
    sources = [
        "Newsletter",
        "LinkedIn",
        "Twitter",
        "Website",
        "Friend/Colleague/Connection",
        "Google Search",
    ]

    for source in sources:
        if not frappe.db.exists("LMS Source", source):
            doc = frappe.new_doc("LMS Source")
            doc.source = source
            doc.save()


def give_lms_roles_to_admin():
    """Assign the LMS management roles to the Administrator user."""
    roles = ["Course Creator", "Moderator", "Batch Evaluator"]
    for role in roles:
        if not frappe.db.exists("Has Role", {"parent": "Administrator", "role": role}):
            doc = frappe.new_doc("Has Role")
            doc.parent = "Administrator"
            doc.parenttype = "User"
            doc.parentfield = "roles"
            doc.role = role
            doc.save()


def give_user_list_permission():
    """Grant LMS management roles permission on the User doctype."""
    doctype = "User"
    roles = ["Course Creator", "Moderator", "Batch Evaluator"]
    for role in roles:
        permlevel = 0
        create_role(doctype, role, permlevel)
    create_role(doctype, "System Manager", 1)


def give_event_permission():
    """Grant Moderator, Batch Evaluator, and System Manager roles permission on the Event doctype."""
    doctype = "Event"
    roles = ["Moderator", "Batch Evaluator"]
    for role in roles:
        permlevel = 0
        create_role(doctype, role, permlevel, 1, 1)
    create_role(doctype, "System Manager", 0, 1, 1)


def create_role(doctype, role, permlevel, write=0, create=0):
    """Add a custom permission for the given role on a doctype, with optional write and create rights."""
    if frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role, "permlevel": permlevel}):
        return

    add_permission(doctype, role, permlevel)
    update_permission_property(doctype, role, permlevel, "select", 1)

    if role in ["Moderator", "System Manager"] or write == 1:
        update_permission_property(doctype, role, permlevel, "write", 1)
    if role == "Moderator" or create == 1:
        update_permission_property(doctype, role, permlevel, "create", 1)


def delete_lms_roles():
    """Delete the LMS roles along with their role assignments and custom permissions."""
    roles = ["Course Creator", "Moderator", "Batch Evaluator", "LMS Student"]
    for role in roles:
        if frappe.db.exists("Role", role):
            frappe.db.delete("Has Role", {"role": role})
            frappe.db.delete("Custom DocPerm", {"role": role})
            frappe.db.delete("Role", role)
