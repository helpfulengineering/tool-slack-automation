from multiprocessing import Process, Pipe
import re


def match(pipe, channel, text, skills):
    """Match skill tokens to terms in a channel corpus."""
    weights = sum([
        1 for skill, weight in skills.items()
        if f" {skill} " in text
        ])
    pipe.send([channel, weights / len(skills)])
    pipe.close()


def search(text, corpus):
    """Search a list of skill tokens in each of the corpus channels."""
    text = " " + re.sub(r"[,.;@#?!&\n\t\r_-]+\s*", " ", text.casefold()) + " "
    processes = []
    pipes = []

    for channel, skills in corpus.items():
        parent_pipe, child_pipe = Pipe()
        arguments = (child_pipe, channel, text, skills)
        process = Process(target=match, args=arguments)
        processes.append(process)
        pipes.append(parent_pipe)

    for process in processes:
        process.start()
    for process in processes:
        process.join()

    channels = sorted(
        [pipe.recv() for pipe in pipes],
        key=lambda item: item[1],
        reverse=True
        )

    return list(filter(lambda item: item[1], channels))


def recommend(introduction, corpus, limit=5):
    """Recommends a list of interesting channels."""
    channels = search(introduction, corpus)
    print(channels)
    return " ".join([f"#{channel[0]}" for channel in channels][:limit])
