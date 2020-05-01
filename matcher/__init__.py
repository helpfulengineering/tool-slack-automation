"""
This module uses a trained model and a list of categorized skills to obtain
customized Slack channel recommendations from an introduction message.

>>> model = model.build(skills.train(), corpus.channels(), threshold=0.5)
>>> matcher.recommend_channels(model, "I'm a 40 year old physician with a cat")
{"skill-medical-personnel": 0.8, "skill-pet-feeding": 0.2, ...}
"""

import re


def extract_categories(text, categories):
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


# FIXME: crippled normalization
def recommend_channels(model, text, limit=3):
    tokenized_text = extract_categories(text, model["categories"])
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


def recommend_jobs(model, text, limit=3):
    recommendations = extract_categories(text, {
        identifier: job["tags"] for identifier, job in model["jobs"].items()
        })
    return [
        f"""• <{model["jobs"][job]["link"]}|{job}>""" for job, weight in sorted(
            recommendations.items(), reverse=True, key=lambda item: item[1]
            )
        if weight
        ][:limit]
