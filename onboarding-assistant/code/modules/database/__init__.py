"""Airtable database driver and volunteer record ingestor.
This module exposes high-level functions for storing volunteer records.
>>>
"""
from airtable import airtable
import amazon


volunteers = airtable.Airtable(
    amazon.configuration["airtable_volunteers_base"],
    api_key=amazon.configuration["airtable_token"]
    )
mails = airtable.Airtable(
    amazon.configuration["airtable_mails_base"],
    api_key=amazon.configuration["airtable_token"]
    )
engagement = airtable.Airtable(
    amazon.configuration["airtable_engagement_base"],
    api_key=amazon.configuration["airtable_token"]
    )


def set_field(base, table, field, value):
    return base.create(table, {field: value})["id"]


def get_records(base, table, field, value):
    filter = {"filter_by_formula": filter_formula(field, value)}
    return base.get(table, **filter)["records"]


def tags(base, table, field, values):
    response=[]
    for value in values:
        response += [
            records[0]["id"]
            if (records := get_records(base, table, field, value)) else
            set_field(base, table, field, value)
            ]
    return list(set(response))


def filter_formula(field, value):
    """Creates an Airtable filter formula that returns fields == value."""
    field = field.replace("{", r"\{").replace("}", r"\}")
    value = value.replace("'", r"\'").replace("\\", "\\\\")
    return f"{{{field}}} = '{value}'"


def insert_volunteer_record(user, address, form):
    volunteer = volunteers.create("Volunteers", {
        "Slack Handle": (
            user["profile"]["display_name_normalized"] or
            user["profile"]["real_name_normalized"]
            ),
        "Slack User ID": user["id"],
        "Profession": form["profession"],
        "External Organization": form.get("organization", ""),
        "LinkedIn Profile": form.get("linkedin", ""),
        "Weekly Capacity (new)": int(form["availability"].pop()),
        "Skills": tags(volunteers, "Skills", "Name", form["skills"]),
        "Languages": tags(volunteers, "Languages", "Language", form["languages"]),
        "Industry": tags(volunteers, "Industries", "Name", form["industries"]),
        "City": (
            address.get("locality") or
            address.get("administrative_area_level_2", "")
            ),
        "Country (new)": address.get("country", ""),
        "State/Province": address.get("administrative_area_level_1", ""),
        "Zip Code": address.get("postal_code", ""),
        "Geolocation": address.get("address", ""),
        "Geocode": ", ".join(map(str, address.get("location", []))),
        "Volunteer Interest": True,
        "Timezone": user["tz_label"],
        "Experience": form["experience"],
        "Management Interest": "leadership" in form["options"],
        "Privacy Policy": "privacy" in form["options"]
        })["id"]
    mail = mails.create("Email Addresses", {
        "Email Address": user["profile"]["email"],
        "Volunteer Record": volunteer
    })
    return volunteer


def insert_event_record(user, category, action, label=""):
    return engagement.create("Events", {
        "User ID": user,
        "Category": tags(engagement, "Categories", "Category", [category]),
        "Action": tags(engagement, "Actions", "Action", [action]),
        "Label": label
        })["id"]


def check_volunteer(identifier):
    """Checks if there is any volunteer with the given Slack identifier."""
    return volunteers.get(
        "Volunteers",
        filter_by_formula=filter_formula("Slack User ID", identifier)
        )["records"]
