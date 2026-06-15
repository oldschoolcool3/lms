# Copyright (c) 2021, FOSS United and Contributors
# See license.txt

import frappe
from frappe.utils import getdate, to_timedelta

from lms.lms.doctype.lms_certificate.lms_certificate import is_certified
from lms.lms.test_helpers import BaseTestUtils
from lms.lms.utils import (
    create_user,
    get_assessments,
    get_average_rating,
    get_batch_details,
    get_chapters,
    get_course_details,
    get_courses,
    get_evaluator,
    get_instructors,
    get_lesson,
    get_lesson_index,
    get_lesson_url,
    get_lessons,
    get_lms_route,
    get_membership,
    get_reviews,
    has_course_instructor_role,
    has_evaluator_role,
    has_moderator_role,
    has_student_role,
    is_instructor,
    slugify,
)


class TestLMSUtils(BaseTestUtils):
    def setUp(self):
        super().setUp()

        self._setup_course_flow()
        self._setup_batch_flow()

    def test_simple_slugs(self):
        self.assertEqual(slugify("hello-world"), "hello-world")
        self.assertEqual(slugify("Hello World"), "hello-world")
        self.assertEqual(slugify("Hello, World!"), "hello-world")

    def test_duplicates_slugs(self):
        self.assertEqual(slugify("Hello World", ["hello-world"]), "hello-world-2")
        self.assertEqual(slugify("Hello World", ["hello-world", "hello-world-2"]), "hello-world-3")

    def test_get_membership(self):
        membership = get_membership(self.course.name, self.student1.email)
        self.assertIsNotNone(membership)
        self.assertEqual(membership.course, self.course.name)
        self.assertEqual(membership.member, self.student1.email)

    def test_get_chapters(self):
        chapters = get_chapters(self.course.name)
        self.assertEqual(len(chapters), len(self.course.chapters))

        for i, chapter in enumerate(chapters, start=1):
            self.assertEqual(chapter.title, f"Chapter {i}")

    def test_get_lessons(self):
        lessons = get_lessons(self.course.name)
        all_lessons = frappe.db.count("Course Lesson", {"course": self.course.name})
        self.assertEqual(len(lessons), all_lessons)

    def test_get_instructors(self):
        instructors = get_instructors("LMS Course", self.course.name)
        self.assertEqual(len(instructors), len(self.course.instructors))
        self.assertEqual(instructors[0].name, "frappe@example.com")

    def test_get_average_rating(self):
        average_rating = get_average_rating(self.course.name)
        self.assertEqual(average_rating, 4.5)

    def test_get_reviews(self):
        reviews = get_reviews(self.course.name)
        self.assertEqual(len(reviews), 2)

    def test_get_lesson_index(self):
        lessons = get_lessons(self.course.name)
        for lesson in lessons:
            self.assertEqual(get_lesson_index(lesson.name), lesson.number)

    def test_get_lesson_url(self):
        lessons = get_lessons(self.course.name)
        for lesson in lessons:
            expected_url = get_lms_route(f"courses/{self.course.name}/learn/{lesson.number}")
            self.assertEqual(get_lesson_url(self.course.name, lesson.number), expected_url)

    def test_is_instructor(self):
        frappe.session.user = "frappe@example.com"
        self.assertTrue(is_instructor(self.course.name))
        frappe.session.user = "Administrator"
        self.assertFalse(is_instructor(self.course.name))

    def test_has_course_instructor_role(self):
        self.assertIsNotNone(has_course_instructor_role("frappe@example.com"))
        self.assertIsNone(has_course_instructor_role("student1@example.com"))

    def test_has_moderator_role(self):
        self.assertIsNotNone(has_moderator_role("frappe@example.com"))
        self.assertIsNone(has_moderator_role("student2@example.com"))

    def test_has_evaluator_role(self):
        self.assertIsNotNone(has_evaluator_role("frappe@example.com"))
        self.assertIsNone(has_evaluator_role("student2@example.com"))

    def test_has_student_role(self):
        self.assertIsNotNone(has_student_role("student1@example.com"))
        self.assertIsNotNone(has_student_role("student2@example.com"))

    def test_is_certified(self):
        frappe.session.user = self.student1.email
        self.assertIsNotNone(is_certified(self.course.name))
        frappe.session.user = self.student2.email
        self.assertIsNone(is_certified(self.course.name))
        frappe.session.user = "Administrator"

    def test_rating_validation(self):
        student3 = self._create_user("student3@example.com", "Emily", "Cooper", ["LMS Student"])
        with self.assertRaises(frappe.exceptions.ValidationError):
            frappe.session.user = student3.email
            review = frappe.new_doc("LMS Course Review")
            review.course = self.course.name
            review.rating = -0.5
            review.review = "Bad course"
            review.save()
        frappe.session.user = "Administrator"

    def test_get_evaluator(self):
        evaluator_email = get_evaluator(self.course.name, self.batch.name)
        self.assertEqual(evaluator_email, self.evaluator.evaluator)

    def test_get_course_details(self):
        course_details = get_course_details(self.course.name)
        self.assertEqual(course_details.name, self.course.name)
        self.assertEqual(course_details.title, self.course.title)
        self.assertEqual(course_details.category, self.course.category)
        self.assertEqual(course_details.description, self.course.description)
        self.assertEqual(course_details.short_introduction, self.course.short_introduction)
        self.assertEqual(course_details.tags, self.course.tags)
        self.assertEqual(course_details.published, 1)
        self.assertEqual(len(course_details.instructors), len(self.course.instructors))

    def test_get_batch_details(self):
        batch_details = get_batch_details(self.batch.name)
        self.assertEqual(batch_details.name, self.batch.name)
        self.assertEqual(batch_details.title, self.batch.title)
        self.assertEqual(batch_details.start_date, getdate(self.batch.start_date))
        self.assertEqual(batch_details.end_date, getdate(self.batch.end_date))
        self.assertEqual(batch_details.start_time, to_timedelta(self.batch.start_time))
        self.assertEqual(batch_details.end_time, to_timedelta(self.batch.end_time))
        self.assertEqual(batch_details.timezone, self.batch.timezone)
        self.assertEqual(batch_details.published, 1)
        self.assertEqual(batch_details.description, self.batch.description)
        self.assertEqual(batch_details.batch_details, self.batch.batch_details)
        self.assertEqual(len(batch_details.courses), len(self.batch.courses))
        self.assertEqual(batch_details.evaluation_end_date, getdate(self.batch.evaluation_end_date))
        self.assertEqual(len(batch_details.instructors), len(self.batch.instructors))
        self.assertEqual(len(batch_details.students), 2)

    def test_create_user(self):
        user = create_user(email="testuser@example.com", first_name="Test", last_name="User", roles=["LMS Student"])
        self.assertEqual(user.email, "testuser@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.full_name, "Test User")
        self.assertIn("LMS Student", [role.role for role in user.roles])
        self.cleanup_items.append(("User", user.name))

    def test_create_user_with_full_name(self):
        user = create_user(email="fullnameuser@example.com", full_name="John Michael Doe", roles=["Course Creator"])
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Michael Doe")
        self.assertEqual(user.full_name, "John Michael Doe")
        self.assertIn("Course Creator", [role.role for role in user.roles])
        self.cleanup_items.append(("User", user.name))

    # --- Guest / instructor exposure regression tests (PR #7 security fixes) ---

    def test_get_courses_forces_published_filter_for_guests(self):
        """Guests cannot enumerate unpublished courses, even by passing published=0.

        Regression test for the get_courses hardening: a guest-supplied `published`
        filter is overwritten with published=1 server-side.
        """
        draft = self._create_course(title="Hidden Draft Course")
        frappe.db.set_value("LMS Course", draft.name, "published", 0)

        # The published override only runs once guest access is allowed; otherwise
        # get_courses short-circuits to [] before reaching it.
        settings = frappe.get_doc("LMS Settings")
        original_guest_access = settings.allow_guest_access
        settings.allow_guest_access = 1
        settings.save(ignore_permissions=True)
        try:
            frappe.session.user = "Guest"
            guest_names = [course.name for course in get_courses(filters={"published": 0})]
            self.assertNotIn(draft.name, guest_names)

            # Guests still see published courses; the draft stays hidden.
            visible = [course.name for course in get_courses()]
            self.assertIn(self.course.name, visible)
            self.assertNotIn(draft.name, visible)
        finally:
            frappe.session.user = "Administrator"
            settings = frappe.get_doc("LMS Settings")
            settings.allow_guest_access = original_guest_access
            settings.save(ignore_permissions=True)

    def test_get_courses_published_filter_not_forced_for_moderators(self):
        """The published override is guest-only — moderators can still list drafts."""
        draft = self._create_course(title="Hidden Draft Course")
        frappe.db.set_value("LMS Course", draft.name, "published", 0)

        frappe.session.user = "frappe@example.com"  # Moderator + course instructor
        try:
            names = [course.name for course in get_courses(filters={"published": 0})]
            self.assertIn(draft.name, names)
        finally:
            frappe.session.user = "Administrator"

    def test_get_lesson_strips_instructor_fields_for_students(self):
        """instructor_notes/instructor_content reach instructors only, not enrolled students.

        Regression test for the get_lesson hardening: its access gate also admits
        enrolled students, so the author-only fields are stripped unless the viewer
        can author the course (can_access_lesson(instructor_only=True)).
        """
        chapter_name = frappe.db.get_value("Chapter Reference", {"parent": self.course.name, "idx": 1}, "chapter")
        lesson_name = frappe.db.get_value("Lesson Reference", {"parent": chapter_name, "idx": 1}, "lesson")
        frappe.db.set_value(
            "Course Lesson",
            lesson_name,
            {
                "instructor_notes": "Author-only grading notes",
                "instructor_content": "Secret instructor walkthrough",
            },
        )

        try:
            # Instructor/moderator sees the author-only fields.
            frappe.session.user = "frappe@example.com"
            as_instructor = get_lesson(self.course.name, 1, 1)
            self.assertEqual(as_instructor.get("instructor_notes"), "Author-only grading notes")
            self.assertEqual(as_instructor.get("instructor_content"), "Secret instructor walkthrough")

            # Enrolled student still sees the lesson, but the author-only fields are stripped.
            frappe.session.user = self.student1.email
            as_student = get_lesson(self.course.name, 1, 1)
            self.assertNotIn("no_preview", as_student)
            self.assertIsNotNone(as_student.get("title"))
            self.assertIsNone(as_student.get("instructor_notes"))
            self.assertIsNone(as_student.get("instructor_content"))
        finally:
            frappe.session.user = "Administrator"

    def test_get_assessments_includes_exercise_details(self):
        """get_assessments returns programming-exercise rows fully populated.

        Regression test for get_exercise_details: it now returns the assessment
        dict (like its assignment/quiz siblings) instead of None, so the row that
        get_assessments yields carries the exercise title, status, and edit_url.
        """
        batch = frappe.get_doc("LMS Batch", self.batch.name)
        batch.append(
            "assessment",
            {
                "assessment_type": "LMS Programming Exercise",
                "assessment_name": self.programming_exercise.name,
            },
        )
        batch.save()

        frappe.session.user = self.student1.email
        try:
            assessments = get_assessments(self.batch.name)
        finally:
            frappe.session.user = "Administrator"

        exercise = next(
            assessment for assessment in assessments if assessment.assessment_type == "LMS Programming Exercise"
        )
        self.assertEqual(exercise.assessment_name, self.programming_exercise.name)
        self.assertEqual(exercise.title, self.programming_exercise.title)
        # student1 has a passing submission seeded by _add_student_progress.
        self.assertTrue(exercise.completed)
        self.assertEqual(exercise.status, "Passed")
        self.assertIn(self.programming_exercise.name, exercise.edit_url)
