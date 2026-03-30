"""Google Sheets database provider implementation.

This module provides the same public API as the Airtable provider so the
app can switch backends by configuration. It stores volunteers, email
addresses, events, and tag sheets in a single Google Sheets workbook.

Required configuration keys in AWS Secrets Manager:
- google_sheets_spreadsheet_id
- google_service_account_key

The service account key may be stored as JSON text or as a path to a JSON
file.
"""

import json
import os
import time
import uuid
from pathlib import Path
from urllib.parse import quote

import requests
import amazon

# Required Google Sheets configuration.
SPREADSHEET_ID = amazon.configuration.get("google_sheets_spreadsheet_id")
SERVICE_ACCOUNT_KEY = amazon.configuration.get("google_service_account_key")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
BASE_URL = "https://sheets.googleapis.com/v4/spreadsheets"

VOLUNTEERS_SHEET = "Volunteers"
EMAILS_SHEET = "Email Addresses"
EVENTS_SHEET = "Events"
SKILLS_SHEET = "Skills"
LANGUAGES_SHEET = "Languages"
INDUSTRIES_SHEET = "Industries"

SHEET_HEADERS = {
    VOLUNTEERS_SHEET: [
        "Volunteer ID",
        "Slack Handle",
        "Slack User ID",
        "Profession",
        "External Organization",
        "LinkedIn Profile",
        "Weekly Capacity",
        "Skills",
        "Languages",
        "Industries",
        "City",
        "State/Province",
        "Country",
        "Zip Code",
        "Geolocation",
        "Geocode",
        "Volunteer Interest",
        "Timezone",
        "Experience",
        "Management Interest",
        "Privacy Policy",
        "Created At"
    ],
    EMAILS_SHEET: [
        "Email ID",
        "Volunteer ID",
        "Email Address",
        "Created At"
    ],
    EVENTS_SHEET: [
        "Event ID",
        "User ID",
        "Category",
        "Action",
        "Label",
        "Created At"
    ],
    SKILLS_SHEET: ["Skill ID", "Name"],
    LANGUAGES_SHEET: ["Language ID", "Name"],
    INDUSTRIES_SHEET: ["Industry ID", "Name"]
}

TAG_SHEET_MAP = {
    SKILLS_SHEET: "skill",
    LANGUAGES_SHEET: "language",
    INDUSTRIES_SHEET: "industry"
}


def _ensure_ready():
    if not SPREADSHEET_ID or not SERVICE_ACCOUNT_KEY:
        raise RuntimeError(
            "Google Sheets provider requires google_sheets_spreadsheet_id "
            "and google_service_account_key in configuration."
        )


def _service_account_info():
    if SERVICE_ACCOUNT_KEY.strip().startswith("{"):
        return json.loads(SERVICE_ACCOUNT_KEY)
    if Path(SERVICE_ACCOUNT_KEY).exists():
        with open(SERVICE_ACCOUNT_KEY, "r", encoding="utf-8") as handle:
            return json.load(handle)
    raise ValueError(
        "google_service_account_key must be either JSON text or a path to a JSON file."
    )


def _get_credentials():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import service_account
    except ImportError as exc:
        raise RuntimeError(
            "google-auth is required for Sheets provider. "
            "Install it via requirements or poetry."
        ) from exc

    info = _service_account_info()
    credentials = service_account.Credentials.from_service_account_info(
        info,
        scopes=SCOPES
    )
    credentials.refresh(Request())
    return credentials


def _headers():
    creds = _get_credentials()
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json"
    }


def _encode_range(sheet_name, range_name="A:Z"):
    raw = f"{sheet_name}!{range_name}"
    return quote(raw, safe='!:$,()')


def _get_values(sheet_name, range_name="A:Z"):
    url = f"{BASE_URL}/{SPREADSHEET_ID}/values/{_encode_range(sheet_name, range_name)}"
    response = requests.get(url, headers=_headers())
    if response.status_code == 404:
        return []
    response.raise_for_status()
    return response.json().get("values", [])


def _append_values(sheet_name, row_values):
    url = (
        f"{BASE_URL}/{SPREADSHEET_ID}/values/"
        f"{_encode_range(sheet_name, 'A:Z')}:append"
        f"?valueInputOption=RAW"
    )
    body = {"values": [row_values]}
    response = requests.post(url, headers=_headers(), json=body)
    response.raise_for_status()
    return response.json()


def _get_sheet_header(sheet_name):
    values = _get_values(sheet_name, "A:Z")
    return values[0] if values else []


def _ensure_sheet_header(sheet_name):
    header = _get_sheet_header(sheet_name)
    if not header:
        _append_values(sheet_name, SHEET_HEADERS[sheet_name])
        return SHEET_HEADERS[sheet_name]
    return header


def _find_row(sheet_name, column_name, value):
    values = _get_values(sheet_name, "A:Z")
    if not values:
        return None, None
    header = values[0]
    try:
        index = header.index(column_name)
    except ValueError:
        return None, None
    for row_number, row in enumerate(values[1:], start=2):
        if index < len(row) and row[index] == value:
            return row, row_number
    return None, None


def _row_to_record(sheet_name, row):
    header = _get_sheet_header(sheet_name)
    fields = {
        header[idx]: row[idx]
        for idx in range(min(len(header), len(row)))
    }
    return {
        "id": row[0] if row else "",
        "fields": fields
    }


def _normalize_tag_name(name):
    return name.strip()


def _serialize_ids(ids):
    return "|".join(ids)


def _make_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _get_or_create_tag_id(sheet_name, tag_name):
    tag_name = _normalize_tag_name(tag_name)
    if not tag_name:
        raise ValueError("Tag name cannot be empty")

    _ensure_sheet_header(sheet_name)
    values = _get_values(sheet_name, "A:B")
    for row in values[1:]:
        if len(row) >= 2 and row[1].strip().lower() == tag_name.lower():
            return row[0]

    tag_id = _make_id(TAG_SHEET_MAP[sheet_name])
    _append_values(sheet_name, [tag_id, tag_name])
    return tag_id


def _append_email_address(volunteer_id, email_address):
    _ensure_sheet_header(EMAILS_SHEET)
    email_id = _make_id("email")
    _append_values(
        EMAILS_SHEET,
        [email_id, volunteer_id, email_address, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())]
    )
    return email_id


def insert_volunteer_record(user, address, form):
    _ensure_ready()
    volunteer_id = _make_id("vol")
    skills = [
        _get_or_create_tag_id(SKILLS_SHEET, skill)
        for skill in form.get("skills", [])
    ]
    languages = [
        _get_or_create_tag_id(LANGUAGES_SHEET, language)
        for language in form.get("languages", [])
    ]
    industries = [
        _get_or_create_tag_id(INDUSTRIES_SHEET, industry)
        for industry in form.get("industries", [])
    ]
    availability = form.get("availability", [])
    weekly_capacity = availability.pop() if availability else ""
    row = [
        volunteer_id,
        user["profile"].get("display_name_normalized") or user["profile"].get("real_name_normalized"),
        user.get("id", ""),
        form.get("profession", ""),
        form.get("organization", ""),
        form.get("linkedin", ""),
        weekly_capacity,
        _serialize_ids(skills),
        _serialize_ids(languages),
        _serialize_ids(industries),
        address.get("locality") or address.get("administrative_area_level_2", ""),
        address.get("administrative_area_level_1", ""),
        address.get("country", ""),
        address.get("postal_code", ""),
        address.get("address", ""),
        ", ".join(map(str, address.get("location", []))) if address.get("location") else "",
        "TRUE",
        user.get("tz_label", ""),
        form.get("experience", ""),
        "TRUE" if "leadership" in form.get("options", []) else "FALSE",
        "TRUE" if "privacy" in form.get("options", []) else "FALSE",
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    ]
    _ensure_sheet_header(VOLUNTEERS_SHEET)
    _append_values(VOLUNTEERS_SHEET, row)
    email = user["profile"].get("email")
    if email:
        _append_email_address(volunteer_id, email)
    return volunteer_id


def insert_event_record(user, category, action, label=""):
    _ensure_ready()
    _ensure_sheet_header(EVENTS_SHEET)
    event_id = _make_id("evt")
    _append_values(
        EVENTS_SHEET,
        [
            event_id,
            user,
            category,
            action,
            label,
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        ]
    )
    return event_id


def check_volunteer(identifier):
    _ensure_ready()
    row, _ = _find_row(VOLUNTEERS_SHEET, "Slack User ID", identifier)
    if not row:
        return []
    return [_row_to_record(VOLUNTEERS_SHEET, row)]
