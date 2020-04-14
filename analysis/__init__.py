"""
Analysis functions for the corpus data.
Under construction: ugly/moved code warning.
"""

import re
import json
import pathlib


def tag(categories, text):
    def match(skills, text):
        text = re.sub(r"\W+", " ", text.casefold())
        return sum([1 for skill in skills if f" {skill} " in f" {text} "])
    matches = {
        label: match(skills, text)
        for label, skills in categories.items()
        }
    return {
        category: value / sum(matches.values())
        for category, value in matches.items()
        if sum(matches.values())
        }


def categories():
    with open(pathlib.Path(__file__).parent / "categories.json") as categories:
        return json.load(categories)


def select(channels, expression=r".*", threshold=1):
    """Select the channels that match all the specified conditions:
    * Have less users than `threshold` times the most joined channel.
    * Match the provided regular expression (against the channel)."""
    user_limit = threshold * max(
        len(channel["members"])
        for channel in channels
        )
    return filter(lambda channel: all([
        len(channel["members"]) < user_limit,
        re.match(expression, channel["name"])
        ]), channels)


def model(channels):
    return {
        "channels": {
            channel["name"]: tag(
                text=" ".join(item["text"] for item in channel["messages"]),
                categories=categories(),
                )
            for channel in channels
            },
        "categories": categories()
        }


def recommend(model, text, limit=5):
    tokens = tag(model["categories"], text)
    recommendations = {
        channel: sum([
            weight * tokens.get(category, 0)
            for category, weight in categories.items()
            ])
        for channel, categories in model["channels"].items()
        }
    return [
        "#" + channel
        for channel, weight in sorted(
            recommendations.items(),
            key=lambda item: item[1],
            reverse=True
            )
        if weight
        ][:limit]


def test(model):
    print("Continuous introduction parsing...")
    while True:
        text = input("Paste an introduction text and press [enter]: ")
        categories = tag(model["categories"], text)
        channels = recommend_channels(model, text)
        print("Channels:", channels)
        print("Categories:", sorted(
            categories.items(),
            key=lambda item: item[1],
            reverse=True
            ))
