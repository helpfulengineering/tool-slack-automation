"""Channel and job recommendation engine.
This module uses a trained model and a list of categorized skills to obtain
customized Slack channel recommendations from an introduction message.
>>> recommendations.channels("I'm a data scientist", limit=1)
["#skill-data-science"]
"""
import re
import json
import pathlib


with open(pathlib.Path(__file__).parent / "model.json") as model_file:
    model = json.load(model_file)


def categories(text, categories):
    """Extracts categories from a model."""
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


def channels(text, default=None, model=model, limit=3):
    """Recommends interesting channels by analyzing an introduction."""
    tokenized_text = categories(text, model["categories"])
    total_skills = len(model["categories"])
    recommendations = {
        channel: sum([
            category_weight * tokenized_text.get(channel_category, 0)
            for channel_category, category_weight in channel_categories.items()
            ]) / total_skills
        for channel, channel_categories in model["channels"].items()
        }
    return [
        "#" + channel for channel, weight in sorted(
            recommendations.items(), reverse=True, key=lambda item: item[1]
            )
        if weight
        ][:limit]


def jobs(text, model=model, limit=3):
    """Recommends interesting jobs by analyzing an introduction."""
    recommendations = categories(text, {
        identifier: job["tags"] for identifier, job in model["jobs"].items()
        })
    return [
        f"""• <{model["jobs"][job]["link"]}|{job}>""" for job, weight in sorted(
            recommendations.items(), reverse=True, key=lambda item: item[1]
            )
        if weight
        ][:limit]
