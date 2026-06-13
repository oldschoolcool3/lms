import frappe
from frappe.website.doctype.web_template.web_template import WebTemplate

from lms.widgets import Widgets


class CustomWebTemplate(WebTemplate):
    """Web template override that injects LMS widgets into the render context."""

    def render(self, values=None):
        """Render the standard template with parsed values and LMS widgets in context."""
        if not values:
            values = {}
        values = frappe.parse_json(values)
        values.update({"values": values})
        values.update({"widgets": Widgets()})
        template = self.get_template(self.standard)
        return frappe.render_template(template, values)
