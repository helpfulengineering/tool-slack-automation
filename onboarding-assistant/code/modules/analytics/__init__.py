"""Analytics event API.
This module provides useful functions for interfacing with the Google Analytics
Events API and tracking events from the application code.
>>> import analytics
>>> analytics.event("user", "category", "action")
"""
import hashlib
import requests
import airtable
import amazon

def event(user, category, action, label=""):
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
