import re
import csv
import json
import click
import datetime

import analysis
import corpus


@click.command()
@click.option(
    "--output",
    required=True,
    type=click.File("w"),
    help="Output file."
    )
@click.option(
    "--token",
    envvar="SLACK_TOKEN",
    help="Slack user token."
    )
@click.option(
    "--cache/--no-cache",
    default=True,
    is_flag=True,
    help="Use disk-cached values instead of real Slack API calls."
    )
@click.option(
    "--channel-threshold",
    default=1,
    type=float,
    help="Exclude channels with more users than `n` times the most joined one."
    )
@click.option(
    "--channel-filter",
    default=r".*",
    help="Exclude channels whose name don't match the regular expression."
    )
def classifier_model(channel_threshold, channel_filter, output, token, cache):
    """Generate a classifier model for the Slack introductions bot."""
    json.dump(analysis.model(analysis.select(
        corpus.build(token=token, refresh=not cache),
        threshold=channel_threshold,
        expression=channel_filter,
        )), output)


if __name__ == "__main__":
    classifier_model()
