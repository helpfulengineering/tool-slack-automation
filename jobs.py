import functools
import airtable
import os

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")  # key···
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")  # app···
AIRTABLE_TABLE = os.getenv("AIRTABLE_TABLE")  # Table

def get():
    open_positions = airtable.Airtable(
        AIRTABLE_BASE,
        AIRTABLE_TABLE,
        api_key=AIRTABLE_TOKEN
        )
    return [
        item["fields"]
        for page in open_positions.get_iter()
        for item in page
        ]
