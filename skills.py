from multiprocessing import Process, Pipe


def match(pipe, channel, skills, terms):
    """Match skill tokens to terms in a channel corpus."""
    weight = sum([1 for token in skills if token in terms]) / len(terms)
    pipe.send([channel, weight])
    pipe.close()


def search(skills, corpus):
    """Search a list of skill tokens in each of the corpus channels."""
    processes = []
    pipes = []

    for channel, terms in corpus.items():
        parent_pipe, child_pipe = Pipe()
        arguments = (child_pipe, channel, skills, terms)
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

    return filter(lambda item: item[1], channels)  


def tokenize(text):
    """Returns a list of skill tokens (strings) for a given text."""
    import re  # Moved here the import because this code should change soon
    return re.findall(r"[\w']+", text.casefold())


def recommend(introduction, corpus, limit=5):
    """Recommends a list of interesting channels."""
    channels = search(tokenize(introduction), corpus)
    return " ".join([f"#{channel[0]}" for channel in channels][:limit])
