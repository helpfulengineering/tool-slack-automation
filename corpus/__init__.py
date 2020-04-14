"""
This module provides a workspace-wide text corpus given a Slack token.

>>> channels = corpus.build(token="xoxp-···", refresh=True)
[
    {
        "name": "channel-name",
        "identifier": "ABC123",
        "topic": "channel topic",
        "purpose": "channel purpose",
        "members": ["U123ABCD", ...],
        "messages": [
            {"user": "U123ABCD", "text": "message text", "time": 123}, ...
        ]
        "pins": [
            {"user": "U123ABCD", "text": "message text", "time": 123}, ...
        ]
    }, ...
]
"""

import os
import pathlib
import cachier
import slack


token = os.environ.get('SLACK_TOKEN')


def build(token=token, refresh=False):
    assert token or not refresh, "Tried to refresh the corpus without a token."
    globals()['token'] = token
    if refresh and token:
        for function in [
            channels,
            messages,
            members,
            pins,
            user
            ]:
            function.clear_cache()
    return channels()


def api():
    """Generic Slack API, authenticated through the module's token variable."""
    assert token, "Tried to call the Slack API without a token."
    return slack.WebClient(token)


@cachier.cachier(cache_dir=pathlib.Path(__file__).parent / "cache")
def channels():
    """All the channels, including messages, pins and members."""
    return [{
        "name": channel["name"],
        "identifier": channel["id"],
        "topic": channel["topic"]["value"],
        "purpose": channel["purpose"]["value"],
        "members": [] if channel["is_archived"] else members(channel["id"]),
        "pins": [] if channel["is_archived"] else pins(channel["id"]),
        "messages": messages(channel["id"]),
        "information": {
            **api().conversations_info(channel=channel["id"])["channel"],
            **channel
            }
        }
        for page in api().conversations_list()
        for channel in page["channels"]
        ]


@cachier.cachier(cache_dir=pathlib.Path(__file__).parent / "cache")
def messages(channel):
    """Messages in a given channel."""
    return [{
        "user": message["user"],
        "text": message["text"],
        "time": float(message["ts"])
        }
        for page in api().conversations_history(channel=channel)
        for message in page["messages"] if all([
            message["type"] == "message",
            "user" in message
            ])
            ]


@cachier.cachier(cache_dir=pathlib.Path(__file__).parent / "cache")
def members(channel):
    """Members in a given channel."""
    return [
        member
        for page in api().conversations_members(channel=channel)
        for member in page["members"]
        ]


@cachier.cachier(cache_dir=pathlib.Path(__file__).parent / "cache")
def pins(channel):
    """Pinned messages in a given channel."""
    return [{
        "user": item["message"]["user"],
        "text": item["message"]["text"],
        "time": item["message"]["ts"]
        }
        for item in api().pins_list(channel=channel).get("items", []) if all([
            item["message"]["type"] == "message",
            "user" in item["message"]
            ])
        ]


@cachier.cachier(cache_dir=pathlib.Path(__file__).parent / "cache")
def user(identifier):
    """Profile information for a given user."""
    return dict(api().users_info(user=identifier)["user"])
