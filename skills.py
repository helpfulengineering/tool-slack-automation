import re

def match(text, skills):
    return sum([
        weight for skill, weight in skills.items()
        if f" {skill} " in f" {text} "
        ])


def search(text, corpus):
    """Search a list of skill tokens in each of the corpus channels."""
    text = re.sub(r"[\W]+", " ", text.casefold())
    matches = [
        [channel, match(text, skills)]
        for channel, skills in corpus.items()
        ]
    return list(filter(
        lambda item: item[1],
        sorted(matches, key=lambda item: item[1], reverse=True)
        ))


def recommend(introduction, corpus, limit=5):
    """Recommends a list of interesting channels."""
    channels = ", ".join([
        f"#{channel[0]}"
        for channel in search(introduction, corpus)
        ][:limit])

    if channels:
        return f"*You might be interested in joining these channels: {channels}*"
    else:
        return ""
