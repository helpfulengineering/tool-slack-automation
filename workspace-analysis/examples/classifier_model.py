import os
import re
import csv
import json
import click
import datetime
import airtable

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
    "--slack-token",
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
@click.option(
    "--airtable-table",
    default="",
    help="Airtable table used for building the job model."
    )
@click.option(
    "--airtable-base",
    default="",
    help="Airtable base used for building the job model."
    )
@click.option(
    "--airtable-token",
    default="",
    help="Airtable token used for building the job model."
    )
def classifier_model(
    airtable_base,
    airtable_table,
    airtable_token,
    channel_threshold,
    channel_filter,
    slack_token,
    output,
    cache,
):
    """Generate a classifier model for the Slack introductions bot."""
    open_positions = airtable.Airtable(
        airtable_base,
        airtable_table,
        api_key=airtable_token
        )
    jobs = [
        item["fields"]
        for page in open_positions.get_iter()
        for item in page
        ]
    json.dump(analysis.model(analysis.select(
        corpus.build(token=slack_token, refresh=not cache),
        threshold=channel_threshold,
        expression=channel_filter,
        ), jobs), output)


if __name__ == "__main__":
    classifier_model()
