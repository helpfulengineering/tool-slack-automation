"""Slack graphical user interface views.
This module loads every sibling JSON file from the file system and exposes
their contents in a more pythonic way.
>>> import interface
>>> interface.example
{"example": true}
"""
import collections
import pathlib
import json


class View(collections.UserDict):
    """Slack user interface view."""
    def format(self, *arguments, function=None, **keyword_arguments):
        """Applies the `format()` method and, optionally, `function()` to
        every string on the view object."""
        def recurse(object):
            if type(object) is dict:
                return {
                    key.format(*arguments, **keyword_arguments):
                    recurse(value)
                    for key, value in object.items()
                    }
            elif type(object) is list:
                return [
                    recurse(item)
                    for item in object
                    ]
            elif type(object) is str:
                formatted = object.format(*arguments, **keyword_arguments)
                return function(formatted) if function else formatted
            else:
                return object
        return recurse(dict(self))


views = {
    path.stem: View(json.load(open(path)))
    for path in pathlib.Path(__file__).parent.glob('*.json')
    }
