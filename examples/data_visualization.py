import json
import click
import pathlib
import datetime
import wordcloud
import collections
import matplotlib

import analysis
import corpus


@click.command()
@click.option(
    "--output",
    required=True,
    type=click.Path(exists=False, resolve_path=True),
    help="Output folder."
    )
@click.option(
    "--model",
    type=click.File("r"),
    help="Classifier model file."
    )
@click.option(
    "--token",
    envvar="SLACK_TOKEN",
    help="Slack token."
    )
@click.option(
    "--cache/--no-cache",
    default=True,
    is_flag=True,
    help="Enable or disable the persistent Slack API call cache."
    )
def generate_charts(model, output, token, cache):
    directory = pathlib.Path(output)
    directory.mkdir()

    channels = corpus.build(token=token, refresh=not cache)
    model = json.load(model) if model else analysis.model(channels)

    matplotlib.use('Agg')

    print("Generating daily channel activity charts...")
    channel_activity = directory / "channel_activity"
    channel_activity.mkdir()

    for channel in channels:
        activity = collections.Counter(
            message["time"] // (3600 * 24)
            for message in channel["messages"]
            )
        data = {
            datetime.datetime.fromtimestamp(item[0] * 3600 * 24): item[1]
            for item in sorted(activity.items(), key=lambda item: item[0])
            }

        figure, axes = matplotlib.pyplot.subplots()
        axes.grid(True, which="both", linestyle=":")
        axes.plot(list(data.keys()), list(data.values()))
        axes.xaxis.set_minor_locator(matplotlib.dates.DayLocator())
        axes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y%m%d"))
        axes.xaxis.set_major_locator(matplotlib.dates.WeekdayLocator())
        figure.subplots_adjust(bottom=0.3)

        matplotlib.pyplot.xticks(rotation=90)
        matplotlib.pyplot.ylabel("Posted messages")
        matplotlib.pyplot.title("Messages in " + channel["name"])
        matplotlib.pyplot.savefig(channel_activity / f"{channel['name']}.png")
        matplotlib.pyplot.close()
        print(channel["name"])

    print("Generating channel category bar charts...")
    channel_categories = directory / "channel_categories"
    channel_categories.mkdir()

    for channel, categories in model["channels"].items():
        ticks = range(len(categories))
        matplotlib.pyplot.figure(num=None, figsize=(32, 18))
        matplotlib.pyplot.title("Categories for " + channel)
        matplotlib.pyplot.xticks(ticks, categories.keys())
        matplotlib.pyplot.ylabel("Weight")
        matplotlib.pyplot.bar(ticks, [
            category if category > max(categories.values()) * 0.75 else 0
            for category in categories.values()
            ], color="green", alpha=0.5)
        matplotlib.pyplot.bar(ticks, categories.values(), alpha=0.5)
        matplotlib.pyplot.savefig(channel_categories / f"{channel}.png")
        matplotlib.pyplot.close()
        print(channel)

    print("Generating channel terms word clouds...")
    channel_terms = directory / "channel_terms"
    channel_terms.mkdir()

    for channel in channels:
        wordcloud.WordCloud(
            width=1024,
            height=1024,
            background_color="white"
            ).generate(" ".join([item["text"] for item in channel["messages"]])
            ).to_file(channel_terms / f"{channel['name']}.png")
        print(channel["name"])

    print("Generating category channel clouds...")
    category_channels = directory / "category_channels"
    category_channels.mkdir()

    for category in model["categories"].keys():
        frequencies = {
            name: weights[category]
            for name, weights in model["channels"].items()
            if category in weights
            }
        wordcloud.WordCloud(
            width=1024,
            height=1024,
            background_color="white"
            ).generate_from_frequencies(frequencies
            ).to_file(category_channels / f"{category}.png")
        print(category)


if __name__ == "__main__":
    generate_charts()
