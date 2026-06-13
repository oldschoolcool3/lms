import frappe
from frappe.utils import nowdate


@frappe.whitelist()
def search_sqlite(query: str):
    """Return grouped command-palette search results from the SQLite learning index."""
    from lms.sqlite import LearningSearch, LearningSearchIndexMissingError

    search = LearningSearch()

    try:
        result = search.search(query)
    except LearningSearchIndexMissingError:
        return []

    return prepare_search_results(result)


def prepare_search_results(result: dict):
    """Group, de-duplicate, and sort raw search results into titled sections by recency."""
    groups = get_grouped_results(result)

    out = []
    for key in groups:
        groups[key] = remove_duplicates(groups[key])
        groups[key].sort(key=lambda x: x.get("modified"), reverse=True)
        out.append({"title": key, "items": groups[key]})

    return out


def get_grouped_results(result):
    """Bucket accessible search results by doctype into Courses, Batches, and Job Opportunities."""
    roles = frappe.get_roles()
    groups = {}
    for r in result["results"]:
        doctype = r["doctype"]
        if doctype == "LMS Course" and can_access_course(r, roles):
            r["author_info"] = get_instructor_info(doctype, r)
            groups.setdefault("Courses", []).append(r)
        elif doctype == "LMS Batch" and can_access_batch(r, roles):
            r["author_info"] = get_instructor_info(doctype, r)
            groups.setdefault("Batches", []).append(r)
        elif doctype == "Job Opportunity" and can_access_job(r, roles):
            r["author_info"] = get_instructor_info(doctype, r)
            groups.setdefault("Job Opportunities", []).append(r)
    return groups


def remove_duplicates(items):
    """Return the items with duplicate names removed, preserving order."""
    seen = set()
    unique_items = []
    for item in items:
        if item["name"] not in seen:
            seen.add(item["name"])
            unique_items.append(item)
    return unique_items


def can_access_course(course, roles):
    """Return whether the roles may see the course (creators always, others only if published)."""
    if can_create_course(roles):
        return True
    elif course.get("published"):
        return True
    return False


def can_access_batch(batch, roles):
    """Return whether the roles may see the batch (creators always, others only if published and upcoming)."""
    if can_create_batch(roles):
        return True
    elif batch.get("published") and batch.get("start_date") >= nowdate():
        return True
    return False


def can_access_job(job, roles):
    """Return whether the roles may see the job (moderators always, others only if it is open)."""
    if "Moderator" in roles:
        return True
    return job.get("status") == "Open"


def can_create_course(roles):
    """Return whether the roles include Course Creator or Moderator."""
    return "Course Creator" in roles or "Moderator" in roles


def can_create_batch(roles):
    """Return whether the roles include Batch Evaluator or Moderator."""
    return "Batch Evaluator" in roles or "Moderator" in roles


def get_instructor_info(doctype, record):
    """Return the resolved instructor's user details for a course or batch search result."""
    instructors = frappe.get_all(
        "Course Instructor", filters={"parenttype": doctype, "parent": record.get("name")}, pluck="instructor"
    )
    instructor = record.get("author")
    if len(instructors):
        for ins in instructors:
            if ins.split("@")[0] in record.get("content"):
                instructor = ins
                break
        if not instructor:
            instructor = instructors[0]

    return frappe.db.get_value(
        "User",
        instructor,
        ["full_name", "email", "user_image", "username"],
        as_dict=True,
    )
