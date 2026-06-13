import json
import os
import re
import secrets
import shutil
import tempfile
import zipfile
from datetime import date, datetime, timedelta

import frappe
from frappe import _
from frappe.utils import escape_html, validate_email_address
from frappe.utils.file_manager import is_safe_path

from lms.lms.utils import create_user as create_lms_user


def export_course_zip(course_name):
    """Export a course and its related data as a downloadable ZIP archive."""
    course = frappe.get_doc("LMS Course", course_name)
    chapters = get_chapters_for_export(course.chapters)
    lessons = get_lessons_for_export(course_name)
    instructors = get_course_instructors(course)
    evaluator = get_course_evaluator(course)
    assets = get_course_assets(course, lessons, instructors, evaluator)
    assessments, questions, test_cases = get_course_assessments(lessons)
    safe_time = frappe.utils.now_datetime().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"{course.name}_{safe_time}_{secrets.token_hex(4)}.zip"
    create_course_zip(
        zip_filename,
        course,
        chapters,
        lessons,
        assets,
        assessments,
        questions,
        test_cases,
        instructors,
        evaluator,
    )


def get_chapters_for_export(chapters: list):
    """Return the Course Chapter documents referenced by the given chapter rows."""
    chapters_list = []
    for row in chapters:
        chapter = frappe.get_doc("Course Chapter", row.chapter)
        chapters_list.append(chapter)
    return chapters_list


def get_lessons_for_export(course_name: str):
    """Return all Course Lesson documents belonging to the given course."""
    lessons = frappe.get_all("Course Lesson", {"course": course_name}, pluck="name")
    lessons_list = []
    for lesson in lessons:
        lesson_doc = frappe.get_doc("Course Lesson", lesson)
        lessons_list.append(lesson_doc)
    return lessons_list


def get_assessment_from_block(block):
    """Return the assessment document referenced by a lesson content block, or None."""
    block_type = block.get("type")
    data_field = "exercise" if block_type == "program" else block_type
    name = block.get("data", {}).get(data_field)
    doctype = get_assessment_map().get(block_type)
    if frappe.db.exists(doctype, name):
        return frappe.get_doc(doctype, name)
    return None


def get_quiz_questions(doc):
    """Return the LMS Question documents linked to a quiz as dicts."""
    questions = []
    for q in doc.questions:
        question_doc = frappe.get_doc("LMS Question", q.question)
        questions.append(question_doc.as_dict())
    return questions


def get_exercise_test_cases(doc):
    """Return the LMS Test Case documents linked to a programming exercise as dicts."""
    test_cases = []
    for tc in doc.test_cases:
        test_case_doc = frappe.get_doc("LMS Test Case", tc.name)
        test_cases.append(test_case_doc.as_dict())
    return test_cases


def get_assessments_from_lesson(lesson):
    """Return the assessments, questions, and test cases referenced in a lesson's content."""
    assessments, questions, test_cases = [], [], []
    content = json.loads(lesson.content) if lesson.content else {}
    for block in content.get("blocks", []):
        if block.get("type") not in ("quiz", "assignment", "program"):
            continue
        doc = get_assessment_from_block(block)
        if not doc:
            continue
        assessments.append(doc.as_dict())
        if doc.doctype == "LMS Quiz":
            questions.extend(get_quiz_questions(doc))
        elif doc.doctype == "LMS Programming Exercise":
            test_cases.extend(get_exercise_test_cases(doc))
    return assessments, questions, test_cases


def get_course_assessments(lessons):
    """Return the combined assessments, questions, and test cases across all lessons."""
    assessments, questions, test_cases = [], [], []
    for lesson in lessons:
        lesson_assessments, lesson_questions, lesson_test_cases = get_assessments_from_lesson(lesson)
        assessments.extend(lesson_assessments)
        questions.extend(lesson_questions)
        test_cases.extend(lesson_test_cases)
    return assessments, questions, test_cases


def get_course_instructors(course):
    """Return user info dicts for each instructor on the course."""
    users = []
    for instructor in course.instructors:
        user_info = frappe.db.get_value(
            "User",
            instructor.instructor,
            ["name", "full_name", "first_name", "last_name", "email", "user_image"],
            as_dict=True,
        )
        if user_info:
            users.append(user_info)
    return users


def get_course_evaluator(course):
    """Return the course's Course Evaluator document as a single-item list, if any."""
    evaluators = []
    if course.evaluator and frappe.db.exists("Course Evaluator", course.evaluator):
        evaluator_info = frappe.get_doc("Course Evaluator", course.evaluator)
        evaluators.append(evaluator_info)
    return evaluators


def get_course_assets(course, lessons, instructors, evaluator):
    """Return the list of asset URLs referenced by the course, lessons, instructors, and evaluator."""
    assets = []
    if course.image:
        assets.append(course.image)
    for lesson in lessons:
        content = json.loads(lesson.content) if lesson.content else {}
        for block in content.get("blocks", []):
            if block.get("type") == "upload":
                url = block.get("data", {}).get("file_url")
                assets.append(url)
    for instructor in instructors:
        if instructor.get("user_image"):
            assets.append(instructor["user_image"])
    if len(evaluator):
        assets.append(evaluator[0].user_image)
    return assets


def read_asset_content(url):
    """Return the raw bytes of the file at the given URL, or None if it cannot be read safely."""
    try:
        file_doc = frappe.get_doc("File", {"file_url": url})
        file_path = file_doc.get_full_path()
        if not is_safe_path(file_path):
            return None
        with open(file_path, "rb") as f:
            return f.read()
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"Could not read asset: {url}")
        return None


def create_course_zip(
    zip_filename,
    course,
    chapters,
    lessons,
    assets,
    assessments,
    questions,
    test_cases,
    instructors,
    evaluator,
):
    """Build the course ZIP, move it to private files, schedule its deletion, and serve it."""
    try:
        tmp_path = os.path.join(tempfile.gettempdir(), zip_filename)
        build_course_zip(
            tmp_path,
            course,
            chapters,
            lessons,
            assets,
            assessments,
            questions,
            test_cases,
            instructors,
            evaluator,
        )
        final_path = move_zip_to_private(tmp_path, zip_filename)
        schedule_file_deletion(final_path, delay_seconds=600)  # 10 minutes
        serve_zip(final_path, zip_filename)
    except Exception as e:
        frappe.throw(_("Could not create the course ZIP file. Please try again later. Error: {0}").format(str(e)))
        return None


def build_course_zip(
    tmp_path, course, chapters, lessons, assets, assessments, questions, test_cases, instructors, evaluator
):
    """Write the course's JSON files and assets into a ZIP archive at the given path."""
    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        write_course_json(zip_file, course)
        write_chapters_json(zip_file, chapters)
        write_lessons_json(zip_file, lessons)
        write_assessments_json(zip_file, assessments, questions, test_cases)
        write_assets(zip_file, assets)
        write_instructors_json(zip_file, instructors)
        write_evaluator_json(zip_file, evaluator)


def write_course_json(zip_file, course):
    """Write the course document as course.json into the ZIP archive."""
    zip_file.writestr("course.json", frappe_json_dumps(course.as_dict()))


def write_chapters_json(zip_file, chapters):
    """Write each chapter document as a JSON file under chapters/ in the ZIP archive."""
    for chapter in chapters:
        chapter_data = chapter.as_dict()
        chapter_json = frappe_json_dumps(chapter_data)
        safe_name = sanitize_string(chapter.name)
        zip_file.writestr(f"chapters/{safe_name}.json", chapter_json)


def write_lessons_json(zip_file, lessons):
    """Write each lesson document as a JSON file under lessons/ in the ZIP archive."""
    for lesson in lessons:
        lesson_data = lesson.as_dict()
        lesson_json = frappe_json_dumps(lesson_data)
        safe_name = sanitize_string(lesson.name)
        zip_file.writestr(f"lessons/{safe_name}.json", lesson_json)


def write_assessments_json(zip_file, assessments, questions, test_cases):
    """Write assessments, questions, and test cases as JSON files under assessments/ in the ZIP."""
    for question in questions:
        question_json = frappe_json_dumps(question)
        safe_name = sanitize_string(question["name"])
        zip_file.writestr(f"assessments/questions/{safe_name}.json", question_json)

    for test_case in test_cases:
        test_case_json = frappe_json_dumps(test_case)
        safe_name = sanitize_string(test_case["name"])
        zip_file.writestr(f"assessments/test_cases/{safe_name}.json", test_case_json)

    for assessment in assessments:
        assessment_json = frappe_json_dumps(assessment)
        doctype = "_".join(assessment["doctype"].lower().split(" "))
        safe_name = "_".join(sanitize_string(assessment["name"]).split(" "))
        zip_file.writestr(f"assessments/{doctype}_{safe_name}.json", assessment_json)


def write_assets(zip_file, assets):
    """Write each safe asset file under assets/ in the ZIP archive."""
    assets = list(set(assets))
    for asset in assets:
        real_path = frappe.get_site_path(asset.lstrip("/"))
        if not asset or not isinstance(asset, str) or not is_safe_path(real_path):
            continue

        file_doc = frappe.get_doc("File", {"file_url": asset})
        file_path = os.path.abspath(file_doc.get_full_path())

        safe_filename = sanitize_string(os.path.basename(asset))
        zip_file.write(file_path, f"assets/{safe_filename}")


def move_zip_to_private(tmp_path, zip_filename):
    """Move the temporary ZIP into the site's private files directory and return its path."""
    final_path = os.path.join(frappe.get_site_path("private", "files"), zip_filename)
    shutil.move(tmp_path, final_path)
    return final_path


def write_instructors_json(zip_file, instructors):
    """Write the instructors list as instructors.json into the ZIP archive."""
    instructors_json = frappe_json_dumps(instructors)
    zip_file.writestr("instructors.json", instructors_json)


def write_evaluator_json(zip_file, evaluator):
    """Write the evaluator document as evaluator.json into the ZIP archive, if present."""
    if not len(evaluator):
        return
    evaluator_json = frappe_json_dumps(evaluator[0].as_dict())
    zip_file.writestr("evaluator.json", evaluator_json)


def serve_zip(final_path, zip_filename):
    """Stream the ZIP file at the given path to the client as a download response."""
    if not os.path.exists(final_path) or not os.path.isfile(final_path):
        frappe.throw(_("File not found"))

    safe_filename = sanitize_string(zip_filename)

    try:
        with open(final_path, "rb") as f:
            frappe.local.response.filename = safe_filename
            frappe.local.response.filecontent = f.read()
            frappe.local.response.type = "download"
            frappe.local.response.content_type = "application/zip"
    except Exception as e:
        frappe.log_error(f"Error serving ZIP file: {str(e)}")
        frappe.throw(_("Error downloading file"))


def schedule_file_deletion(file_path, delay_seconds=600):
    """Enqueue a background job to delete the file at the given path after a delay."""
    frappe.enqueue(
        delete_file,
        file_path=file_path,
        queue="long",
        timeout=delay_seconds,
        at_front=False,
        enqueue_after_commit=True,
    )


def delete_file(file_path):
    """Delete the file at the given path, logging any error."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        frappe.log_error(f"Error deleting exported file {file_path}: {e}")


def frappe_json_dumps(data):
    """Return the data serialized to indented JSON, stringifying date and time objects."""

    def default(obj):
        try:
            if isinstance(obj, (datetime | date | timedelta)):
                return str(obj)
        except Exception as e:
            frappe.log_error(f"Error serializing object {obj}: {e}")

    return json.dumps(data, indent=4, default=default)


def import_course_zip(zip_file_path):
    """Import a course from a ZIP archive and return the new course's name."""
    zip_file_path = zip_file_path.lstrip("/")
    actual_path = frappe.get_site_path(zip_file_path)
    validate_zip_file(actual_path)

    with zipfile.ZipFile(actual_path, "r") as zip_file:
        course_data = read_json_from_zip(zip_file, "course.json")
        if not course_data:
            frappe.throw(_("Invalid course ZIP: Missing course.json"))

        create_assets(zip_file)
        create_user_for_instructors(zip_file)
        create_evaluator(zip_file)
        course_doc = create_course_doc(course_data)
        chapter_docs = create_chapter_docs(zip_file, course_doc.name)
        create_assessment_docs(zip_file)
        create_lesson_docs(zip_file, course_doc.name, chapter_docs)
        save_course_structure(zip_file, course_doc, chapter_docs)
        return course_doc.name


def read_json_from_zip(zip_file, filename):
    """Return the parsed JSON content of a file inside the ZIP, or None on failure."""
    try:
        with zip_file.open(filename) as f:
            return json.load(f)
    except Exception as e:
        frappe.log_error(f"Error reading {filename} from ZIP: {e}")
        return None


def create_user_for_instructors(zip_file):
    """Create User records for any instructors in the ZIP that do not already exist."""
    instructors = read_json_from_zip(zip_file, "instructors.json")
    if not instructors:
        return
    for instructor in instructors:
        if not frappe.db.exists("User", instructor["email"]):
            create_user(instructor)


def sanitize_string(
    value,
    allow_spaces=True,
    max_length=None,
    replacement_char=None,
    escape_html_content=True,
    strip_whitespace=True,
):
    """Unified function to sanitize strings for various use cases.

    Args:
            value: String to sanitize
            allow_spaces: Whether to allow spaces in the output (True for names, False for filenames)
            max_length: Maximum length to truncate to (None for no limit)
            replacement_char: Character to replace invalid chars with (None to remove them)
            escape_html_content: Whether to escape HTML entities
            strip_whitespace: Whether to strip leading/trailing whitespace

    Returns:
            Sanitized string

    """
    if not value:
        return value

    if strip_whitespace:
        value = value.strip()
    if max_length:
        value = value[:max_length]

    if escape_html_content:
        value = escape_html(value)

    if allow_spaces:
        invalid_pattern = r"[^a-zA-Z0-9\s\-\.]"
        valid_pattern = r"^[a-zA-Z0-9\s\-\.]+$"
    else:
        invalid_pattern = r"[^a-zA-Z0-9_\-\.]"
        valid_pattern = r"^[a-zA-Z0-9_\-\.]+$"

    if replacement_char is None:
        if not re.match(valid_pattern, value):
            value = re.sub(invalid_pattern, "", value)
    else:
        value = re.sub(invalid_pattern, replacement_char, value)

    return value


def validate_user_email(user):
    """Validate that the user dict has a well-formed email, throwing otherwise."""
    if not user.get("email") or not validate_email_address(user["email"]):
        frappe.throw(f"Invalid email for user creation: {user.get('email')}")


def get_user_names(user):
    """Return the sanitized first name, last name, and full name derived from a user dict."""
    first_name = sanitize_string(user.get("first_name", ""), max_length=50)
    last_name = sanitize_string(user.get("last_name", ""), max_length=50)
    full_name = sanitize_string(user.get("full_name", ""), max_length=100)
    parts = full_name.split() if full_name else []
    return (
        first_name or (parts[0] if parts else "Imported"),
        last_name or (" ".join(parts[1:]) if len(parts) > 1 else None),
        full_name,
    )


def create_user(user):
    """Create an LMS user with the Course Creator role from the given user dict and return it."""
    first_name, last_name, full_name = get_user_names(user)
    user_doc = create_lms_user(
        email=user["email"],
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        user_image=user.get("user_image"),
        roles=["Course Creator"],
    )
    return user_doc


def create_evaluator(zip_file):
    """Create the Course Evaluator and its backing user from the ZIP, if not already present."""
    evaluator_data = read_json_from_zip(zip_file, "evaluator.json")
    if not evaluator_data:
        return

    if not evaluator_data.get("evaluator") or not validate_email_address(evaluator_data.get("evaluator", "")):
        frappe.log_error(f"Invalid evaluator data: {evaluator_data}")
        return

    if not frappe.db.exists("User", evaluator_data["evaluator"]):
        evaluator_data["email"] = evaluator_data["evaluator"]
        create_user(evaluator_data)

    if not frappe.db.exists("Course Evaluator", evaluator_data["name"]):
        evaluator_doc = frappe.new_doc("Course Evaluator")
        evaluator_doc.update(evaluator_data)
        evaluator_doc.insert(ignore_permissions=True)


def get_course_fields():
    """Return the list of course fields that are copied during import."""
    return [
        "title",
        "tags",
        "image",
        "video_link",
        "card_gradient",
        "short_introduction",
        "description",
        "published",
        "upcoming",
        "featured",
        "disable_self_learning",
        "published_on",
        "category",
        "evaluator",
        "timezone",
        "paid_course",
        "paid_certificate",
        "course_price",
        "currency",
        "amount_usd",
        "enable_certification",
    ]


def add_data_to_course(course_doc, course_data):
    """Copy the importable course fields from the source data onto the course document."""
    for field in get_course_fields():
        if field in course_data:
            course_doc.set(field, course_data[field])


def add_instructors_to_course(course_doc, course_data):
    """Append the instructors from the source data onto the course document."""
    instructors = course_data.get("instructors", [])
    for instructor in instructors:
        course_doc.append("instructors", {"instructor": instructor["instructor"]})


def verify_category(category_name):
    """Create the LMS Category with the given name if it does not already exist."""
    if category_name and not frappe.db.exists("LMS Category", category_name):
        category = frappe.new_doc("LMS Category")
        category.category = category_name
        category.insert(ignore_permissions=True)


def create_course_doc(course_data):
    """Create and insert a new LMS Course document from the imported course data."""
    course_doc = frappe.new_doc("LMS Course")
    add_instructors_to_course(course_doc, course_data)
    verify_category(course_data.get("category"))
    course_data.pop("instructors", None)
    course_data.pop("chapters", None)
    add_data_to_course(course_doc, course_data)
    course_doc.insert(ignore_permissions=True)
    return course_doc


def exclude_meta_fields(data):
    """Return a copy of the data dict without Frappe metadata fields."""
    meta_fields = ["name", "owner", "creation", "created_by", "modified", "modified_by", "docstatus"]
    return {k: v for k, v in data.items() if k not in meta_fields}


def create_chapter_docs(zip_file, course_name):
    """Create Course Chapter documents for the course from the chapters in the ZIP and return them."""
    chapter_docs = []
    for file in zip_file.namelist():
        if file.startswith("chapters/") and file.endswith(".json"):
            chapter_data = read_json_from_zip(zip_file, file)
            chapter_data = exclude_meta_fields(chapter_data)
            if chapter_data:
                chapter_doc = frappe.new_doc("Course Chapter")
                chapter_data.pop("lessons", None)
                chapter_doc.update(chapter_data)
                chapter_doc.course = course_name
                chapter_doc.insert(ignore_permissions=True)
                chapter_docs.append(chapter_doc)
    return chapter_docs


def get_chapter_name_for_lesson(zip_file, lesson_data, chapter_docs):
    """Return the name of the newly created chapter that a lesson belongs to, or None."""
    for file in zip_file.namelist():
        if file.startswith("chapters/") and file.endswith(".json"):
            chapter_data = read_json_from_zip(zip_file, file)
            if chapter_data.get("name") == lesson_data.get("chapter"):
                title = chapter_data.get("title")
                chapter_doc = next((c for c in chapter_docs if c.title == title), None)
                if chapter_doc:
                    return chapter_doc.name
    return None


def get_assessment_map():
    """Return the mapping of content block types to their assessment DocType names."""
    return {"quiz": "LMS Quiz", "assignment": "LMS Assignment", "program": "LMS Programming Exercise"}


def get_assessment_title(zip_file, assessment_name, assessment_type):
    """Return the title of an assessment read from its JSON file in the ZIP, or None."""
    assessment_map = get_assessment_map()
    doctype = "_".join(assessment_map.get(assessment_type).lower().split(" "))
    assessment_name = "_".join(assessment_name.split(" "))
    file_name = f"assessments/{doctype}_{assessment_name}.json"
    try:
        with zip_file.open(file_name) as f:
            assessment_data = json.load(f)
            return assessment_data.get("title")
    except Exception as e:
        frappe.log_error(f"Error reading {file_name} from ZIP: {e}")
        return None


def replace_assessment_names(zip_file, content):
    """Return lesson content JSON with assessment references remapped to the imported records."""
    assessment_types = ["quiz", "assignment", "program"]
    content = json.loads(content)
    for block in content.get("blocks", []):
        if block.get("type") in assessment_types:
            data_field = "exercise" if block.get("type") == "program" else block.get("type")
            assessment_name = block.get("data", {}).get(data_field)
            assessment_title = get_assessment_title(zip_file, assessment_name, block.get("type"))
            doctype = get_assessment_map().get(block.get("type"))
            current_assessment_name = frappe.db.get_value(doctype, {"title": assessment_title}, "name")
            if current_assessment_name:
                block["data"][data_field] = current_assessment_name
    return json.dumps(content)


def replace_assets(content):
    """Remap upload block file URLs in lesson content to the imported LMS Asset URLs."""
    content = json.loads(content)
    for block in content.get("blocks", []):
        if block.get("type") == "upload":
            asset_url = block.get("data", {}).get("file_url")
            if asset_url:
                asset_name = asset_url.split("/")[-1]
                current_asset_url = frappe.db.get_value("LMS Asset", {"file_name": asset_name}, "file_url")
                if current_asset_url:
                    block["data"]["url"] = current_asset_url


def replace_values_in_content(zip_file, content):
    """Return lesson content with imported references substituted in."""
    return replace_assessment_names(zip_file, content)
    # replace_assets(content)


def create_lesson_docs(zip_file, course_name, chapter_docs):
    """Create Course Lesson documents for the course from the lessons in the ZIP and return them."""
    lesson_docs = []
    for file in zip_file.namelist():
        if file.startswith("lessons/") and file.endswith(".json"):
            lesson_data = read_json_from_zip(zip_file, file)
            lesson_data = exclude_meta_fields(lesson_data)
            if lesson_data:
                lesson_doc = frappe.new_doc("Course Lesson")
                lesson_doc.update(lesson_data)
                lesson_doc.course = course_name
                lesson_doc.chapter = get_chapter_name_for_lesson(zip_file, lesson_data, chapter_docs)
                lesson_doc.content = (
                    replace_values_in_content(zip_file, lesson_doc.content) if lesson_doc.content else None
                )
                lesson_doc.insert(ignore_permissions=True)
                lesson_docs.append(lesson_doc)
    return lesson_docs


def create_question_doc(zip_file, file):
    """Create an LMS Question document from a question JSON file in the ZIP."""
    question_data = read_json_from_zip(zip_file, file)
    if question_data:
        doc = frappe.new_doc("LMS Question")
        doc.update(question_data)
        doc.insert(ignore_permissions=True)


def create_test_case_doc(zip_file, file):
    """Create an LMS Test Case document from a test case JSON file in the ZIP."""
    test_case_data = read_json_from_zip(zip_file, file)
    if test_case_data:
        doc = frappe.new_doc("LMS Test Case")
        doc.update(test_case_data)
        doc.insert(ignore_permissions=True)


def add_questions_to_quiz(quiz_doc, questions):
    """Append the imported questions to a quiz document, matching them by detail text."""
    for question in questions:
        question_detail = question["question_detail"]
        question_name = frappe.db.get_value("LMS Question", {"question": question_detail}, "name")
        if question_name:
            quiz_doc.append("questions", {"question": question_name})


def create_supporting_docs(zip_file):
    """Create the question and test case documents that assessments depend on."""
    for file in zip_file.namelist():
        if file.startswith("assessments/questions/") and file.endswith(".json"):
            create_question_doc(zip_file, file)
        elif file.startswith("assessments/test_cases/") and file.endswith(".json"):
            create_test_case_doc(zip_file, file)


def is_assessment_file(file):
    """Return whether the ZIP entry is a top-level assessment JSON file."""
    return (
        file.startswith("assessments/")
        and file.endswith(".json")
        and not file.startswith("assessments/questions/")
        and not file.startswith("assessments/test_cases/")
    )


def build_assessment_doc(assessment_data):
    """Create an assessment document with its questions or test cases from the imported data."""
    doctype = assessment_data.get("doctype")
    if doctype not in ("LMS Quiz", "LMS Assignment", "LMS Programming Exercise"):
        return
    if frappe.db.exists(doctype, assessment_data.get("name")):
        return

    questions = assessment_data.pop("questions", [])
    test_cases = assessment_data.pop("test_cases", [])
    doc = frappe.new_doc(doctype)
    doc.update(assessment_data)

    if doctype == "LMS Quiz":
        add_questions_to_quiz(doc, questions)
    elif doctype == "LMS Programming Exercise":
        for row in test_cases:
            doc.append("test_cases", {"input": row["input"], "expected_output": row["expected_output"]})

    doc.insert(ignore_permissions=True)


def create_main_assessment_docs(zip_file):
    """Create the quiz, assignment, and programming exercise documents from the ZIP."""
    for file in zip_file.namelist():
        if not is_assessment_file(file):
            continue
        assessment_data = read_json_from_zip(zip_file, file)
        if not assessment_data:
            continue
        assessment_data.pop("lesson", None)
        assessment_data.pop("course", None)
        build_assessment_doc(assessment_data)


def create_assessment_docs(zip_file):
    """Create all assessment documents and their supporting records from the ZIP."""
    create_supporting_docs(zip_file)
    create_main_assessment_docs(zip_file)


def create_asset_doc(asset_name, content):
    """Create a File document with the given name and content if it does not already exist."""
    if frappe.db.exists("File", {"file_name": asset_name}):
        return
    asset_doc = frappe.new_doc("File")
    asset_doc.file_name = asset_name
    asset_doc.content = content
    asset_doc.insert()


def process_asset_file(zip_file, file):
    """Create a File document from a single asset entry in the ZIP if its path is safe."""
    if not is_safe_path(file):
        return
    with zip_file.open(file) as f:
        create_asset_doc(file.split("/")[-1], f.read())


def create_assets(zip_file):
    """Create File documents for every asset stored under assets/ in the ZIP."""
    for file in zip_file.namelist():
        if not file.startswith("assets/") or file.endswith("/"):
            continue
        try:
            process_asset_file(zip_file, file)
        except Exception as e:
            frappe.log_error(f"Error processing asset {file}: {e}")


def get_lesson_title(zip_file, lesson_name):
    """Return the title of the lesson with the given name from the ZIP, or None."""
    for file in zip_file.namelist():
        if file.startswith("lessons/") and file.endswith(".json"):
            lesson_data = read_json_from_zip(zip_file, file)
            if lesson_data.get("name") == lesson_name:
                return lesson_data.get("title")
    return None


def add_lessons_to_chapters(zip_file, course_name, chapter_docs):
    """Append each imported lesson to its chapter based on the chapter data in the ZIP."""
    for file in zip_file.namelist():
        if file.startswith("chapters/") and file.endswith(".json"):
            chapter_data = read_json_from_zip(zip_file, file)
            chapter_doc = next((c for c in chapter_docs if c.title == chapter_data.get("title")), None)
            if not chapter_doc:
                continue
            for lesson in chapter_data.get("lessons", []):
                lesson_title = get_lesson_title(zip_file, lesson["lesson"])
                lesson_name = frappe.db.get_value(
                    "Course Lesson", {"title": lesson_title, "course": course_name}, "name"
                )
                if lesson_name:
                    chapter_doc.append("lessons", {"lesson": lesson_name})
            chapter_doc.save(ignore_permissions=True)


def add_chapter_to_course(course_doc, chapter_docs):
    """Append the imported chapters to the course document and save it."""
    course_doc.reload()
    for chapter_doc in chapter_docs:
        course_doc.append("chapters", {"chapter": chapter_doc.name})
    course_doc.save(ignore_permissions=True)


def save_course_structure(zip_file, course_doc, chapter_docs):
    """Link the imported chapters to the course and the lessons to their chapters."""
    add_chapter_to_course(course_doc, chapter_docs)
    add_lessons_to_chapters(zip_file, course_doc.name, chapter_docs)


def validate_zip_file(zip_file_path):
    """Validate that the path points to a real ZIP file with a safe location, throwing otherwise."""
    if not os.path.exists(zip_file_path) or not zipfile.is_zipfile(zip_file_path):
        frappe.throw(_("Invalid ZIP file"))

    if not is_safe_path(zip_file_path):
        frappe.throw(_("Unsafe file path detected"))
