# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import frappe

base_url = "https://api.unsplash.com"


def get_by_keyword(keyword):
    """Return Unsplash photo search results matching the given keyword."""
    data = make_unsplash_request(f"/search/photos?query={keyword}")
    return data.get("results")


def get_list():
    """Return a list of photos from Unsplash."""
    return make_unsplash_request("/photos")


def get_random(params=None):
    """Return a random Unsplash photo filtered by the given query parameters."""
    query_string = ""
    for key, value in params.items():
        query_string += f"{key}={value}&"
    return make_unsplash_request(f"/photos/random?{query_string}")


def make_unsplash_request(path):
    """Send an authenticated GET request to the Unsplash API and return the parsed JSON."""
    unsplash_access_key = frappe.db.get_single_value("LMS Settings", "unsplash_access_key")
    if not unsplash_access_key:
        return

    import requests

    url = f"{base_url}{path}"
    res = requests.get(
        url,
        headers={
            "Accept-Version": "v1",
            "Authorization": f"Client-ID {unsplash_access_key}",
        },
        timeout=30,
    )
    res.raise_for_status()
    data = res.json()
    return data
