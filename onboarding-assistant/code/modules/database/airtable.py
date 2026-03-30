"""Airtable database provider implementation."""

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


def _filter_formula(field, value):
    field = field.replace("{", r"\{").replace("}", r"\}")
    value = value.replace("'", r"\'").replace("\\", "\\\\")
    return f"{{{field}}} = '{value}'"


def _get_records(base, table, field, value):
    filter_args = {"filter_by_formula": _filter_formula(field, value)}
    return base.get(table, **filter_args)["records"]


def _tags(base, table, field, values):
    response = []
    for value in values:
        records = _get_records(base, table, field, value)
        if records:
            response.append(records[0]["id"])
        else:
            response.append(_set_field(base, table, field, value))
    return list(set(response))


def _set_field(base, table, field, value):
    return base.create(table, {field: value})["id"]


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
        "Skills": _tags(volunteers, "Skills", "Name", form["skills"]),
        "Languages": _tags(volunteers, "Languages", "Language", form["languages"]),
        "Industry": _tags(volunteers, "Industries", "Name", form["industries"]),
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

    mails.create("Email Addresses", {
        "Email Address": user["profile"]["email"],
        "Volunteer Record": volunteer
    })

    return volunteer


def insert_event_record(user, category, action, label=""):
    return engagement.create("Events", {
        "User ID": user,
        "Category": _tags(engagement, "Categories", "Category", [category]),
        "Action": _tags(engagement, "Actions", "Action", [action]),
        "Label": label
    })["id"]


def check_volunteer(identifier):
    return volunteers.get(
        "Volunteers",
        filter_by_formula=_filter_formula("Slack User ID", identifier)
    )["records"]
