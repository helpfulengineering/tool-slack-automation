"""Database facade for the onboarding assistant.

This module provides a provider-agnostic interface for the app. It
routes reads and writes to the configured backend and supports feature
flag-style write-through for migration.
"""

import os

from . import airtable, sheets


BACKENDS = {
    "airtable": airtable,
    "sheets": sheets
}


DATA_BACKEND = os.environ.get("DATA_BACKEND", "airtable").lower()
WRITE_BACKENDS = [
    backend.strip().lower()
    for backend in os.environ.get("WRITE_BACKENDS", DATA_BACKEND).split(",")
    if backend.strip()
]


def _backend(name):
    try:
        return BACKENDS[name]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported database backend: {name}. "
            f"Available backends: {', '.join(BACKENDS)}"
        ) from exc


def _primary():
    return _backend(DATA_BACKEND)


def _write_backends():
    return [_backend(name) for name in WRITE_BACKENDS]


def _read(method, *args, **kwargs):
    return getattr(_primary(), method)(*args, **kwargs)


def _write(method, *args, **kwargs):
    result = None
    for backend in _write_backends():
        result = getattr(backend, method)(*args, **kwargs)
    return result


def insert_volunteer_record(user, address, form):
    return _write("insert_volunteer_record", user, address, form)


def insert_event_record(user, category, action, label=""):
    return _write("insert_event_record", user, category, action, label)


def check_volunteer(identifier):
    return _read("check_volunteer", identifier)
