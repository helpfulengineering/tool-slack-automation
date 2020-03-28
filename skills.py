import re


def match(channel, text, skills):
    """Match skill tokens to terms in a channel corpus."""
    weights = sum([
        1 for skill, weight in skills.items()
        if f" {skill} " in text
        ])
    return [channel, weights/len(skills)]


def search(text, corpus):
    """Search a list of skill tokens in each of the corpus channels."""
    text = " " + re.sub(r"[,.;@#?!&\n\t\r_-]+\s*", " ", text.casefold()) + " "
    items = []

    for channel, skills in corpus.items():
        items.append(match(channel, text, skills))

    channels = sorted(
        items,
        key=lambda item: item[1],
        reverse=True
        )

    return list(filter(lambda item: item[1], channels))


def recommend(introduction, corpus, limit=5):
    """Recommends a list of interesting channels."""
    channels = search(introduction, corpus)
    return " ".join([f"#{channel[0]}" for channel in channels][:limit])
