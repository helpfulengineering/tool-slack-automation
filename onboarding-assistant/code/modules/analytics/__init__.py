"""Analytics event API.
This module provides useful functions for interfacing with various analytics
tools  and tracking events from the application code.
>>> import analytics
>>> analytics.event("user", "category", "action")
"""
import hashlib
import requests
import database
import amazon


def google_event(user, category, action, label=""):
    """Track an event through the Google Analytics API."""
    user = {"uid": hashlib.sha256(user.encode('ascii')).hexdigest()}
    property = {"tid": amazon.configuration["google_analytics_property"]}
    settings = {"t": "event", "cid": 555, "aip": "1", "v": "1"}
    details = {"ec": category, "ea": action, "el": label}
    requests.post(
        "https://www.google-analytics.com/collect",
        headers={"user-agent": "Onboarding assitant"},
        data={**user, **property, **settings, **details}
        )


def airtable_event(user, category, action, label=""):
    """Insert an event record into Airtable."""
    database.insert_event_record(user, category, action, label)


def event_worker(event, context=None):
    """Analytics Lambda function that runs in the background."""
    google_event(**event)
    airtable_event(**event)


def event(user, category, action, label=""):
    """Track an event in the background."""
    amazon.invoke_lambda("analytics", {
        "user": user,
        "category": category,
        "action": action,
        "label": label
        })

