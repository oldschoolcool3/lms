from typing import TYPE_CHECKING, cast

import frappe
from frappe.search.sqlite_search import SQLiteSearch, SQLiteSearchIndexMissingError
from frappe.utils import get_datetime, getdate, nowdate

if TYPE_CHECKING:
    import datetime


class LearningSearch(SQLiteSearch):
    """SQLite full-text search index over LMS courses, batches, jobs, and instructors."""

    INDEX_NAME = "learning.db"

    INDEX_SCHEMA = {
        "metadata_fields": [
            "owner",
            "published",
            "published_on",
            "start_date",
            "status",
            "company_name",
            "creation",
            "parent",
            "parenttype",
        ],
        "tokenizer": "unicode61 remove_diacritics 2 tokenchars '-_'",
    }

    INDEXABLE_DOCTYPES = {
        "LMS Course": {
            "fields": [
                "name",
                "title",
                {"content": "description"},
                "short_introduction",
                "published",
                "category",
                "owner",
                {"modified": "published_on"},
            ],
        },
        "LMS Batch": {
            "fields": [
                "name",
                "title",
                "description",
                {"content": "batch_details"},
                "published",
                "category",
                "owner",
                {"modified": "start_date"},
            ],
        },
        "Job Opportunity": {
            "fields": [
                "name",
                {"title": "job_title"},
                {"content": "description"},
                "owner",
                "location",
                "country",
                "company_name",
                "status",
                "creation",
                {"modified": "creation"},
            ],
        },
        "Course Instructor": {
            "fields": [
                "name",
                {"title": "instructor"},
                {"content": "instructor"},
                "parent",
                "parenttype",
                "modified",
            ]
        },
    }

    COURSE_FIELDS = [
        "name",
        "title",
        "description",
        "short_introduction",
        "category",
        "published",
        "published_on",
        "creation",
        "modified",
        "owner",
    ]

    BATCH_FIELDS = [
        "name",
        "title",
        "description",
        "batch_details",
        "category",
        "start_date",
        "creation",
        "modified",
        "owner",
        "published",
    ]

    JOB_FIELDS = [
        "name",
        "job_title",
        "company_name",
        "description",
        "creation",
        "modified",
        "owner",
    ]

    INSTRUCTOR_FIELDS = [
        "name",
        "instructor",
        "parent",
        "parenttype",
    ]

    DOCTYPE_FIELDS = {
        "LMS Course": COURSE_FIELDS,
        "LMS Batch": BATCH_FIELDS,
        "Job Opportunity": JOB_FIELDS,
        "Course Instructor": INSTRUCTOR_FIELDS,
    }

    def build_index(self):
        """Build the search index, surfacing any failure as a Frappe error."""
        try:
            super().build_index()
        except Exception as e:
            frappe.throw(str(e))

    def get_search_filters(self):
        """Return the metadata filters applied to every search query."""
        return {}

    def prepare_document(self, doc):
        """Return the indexable document for a doc, enriching instructor and date fields."""
        document = super().prepare_document(doc)
        if not document:
            return None

        if doc.doctype == "Course Instructor":
            document = self.get_instructor_details(doc, document)
        else:
            if not document.get("modified"):
                self.set_modified_date(doc, doc.doctype, document)

        return document

    def get_instructor_details(self, doc, document):
        """Return the document populated with its parent course or batch instructor details."""
        instructor = frappe.db.get_value("User", doc.instructor, "full_name")
        fields = self.COURSE_FIELDS if doc.parenttype == "LMS Course" else self.BATCH_FIELDS
        details = frappe.db.get_value(doc.parenttype, doc.parent, fields, as_dict=True)

        if details:
            document["doctype"] = doc.parenttype
            document["name"] = doc.parent
            document["title"] = self._process_content(details.title)
            document["published"] = details.get("published", 0)
            document["content"] = self._process_content(
                f"Instructor: {instructor}\n{details.description}\n{doc.instructor}"
            )
            self.set_modified_date(details, doc.parenttype, document)
            if doc.parenttype == "LMS Course":
                document["published_on"] = details.get("published_on")
            elif doc.parenttype == "LMS Batch":
                document["start_date"] = details.get("start_date")

        return document

    def set_modified_date(self, details, doctype, document):
        """Set the document's modified timestamp and doctype-specific date field."""
        modified_value = None
        if doctype == "LMS Course":
            modified_value = details.get("published_on")
        elif doctype == "LMS Batch":
            modified_value = details.get("start_date")

        if not modified_value:
            modified_value = frappe.db.get_value(doctype, details.name, "creation")

        modified_value = get_datetime(modified_value)
        if doctype == "LMS Course":
            document["published_on"] = getdate(modified_value)
        elif doctype == "LMS Batch":
            document["start_date"] = getdate(modified_value)

        document["modified"] = cast("datetime.datetime", modified_value).timestamp()

    @SQLiteSearch.scoring_function
    def get_doctype_boost(self, row, query, query_words):
        """Return a relevance multiplier favouring published, upcoming courses and batches."""
        doctype = row["doctype"]
        if doctype == "LMS Course":
            if row["published"]:
                return 1.3
        elif doctype == "LMS Batch":
            if row["published"] and row["start_date"] >= nowdate():
                return 1.3
            elif row["published"]:
                return 1.2
        return 1.0


class LearningSearchIndexMissingError(SQLiteSearchIndexMissingError):
    """Raise when the learning search index is queried before it has been built."""

    pass


def build_index():
    """Build the learning search index from scratch."""
    search = LearningSearch()
    search.build_index()


def build_index_in_background():
    """Enqueue a learning search index rebuild unless one is already running."""
    if not frappe.cache().get_value("learning_search_indexing_in_progress"):  # type: ignore[reportOptionalCall]  # frappe.cache is a callable at runtime; stub types it as RedisWrapper | None
        frappe.enqueue(build_index, queue="long")


def build_index_if_not_exists():
    """Build the learning search index only if it does not already exist."""
    search = LearningSearch()
    if not search.index_exists():
        build_index()
