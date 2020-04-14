import csv
import json
import click
import datetime

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
    required=True,
    help="Slack user token."
    )
@click.option(
    "--format",
    default="JSON",
    type=click.Choice(["JSON", "CSV"], case_sensitive=False),
    help="Output data format."
    )
@click.option(
    "--cache/--no-cache",
    default=True,
    is_flag=True,
    help="Use disk-cached values instead of real Slack API calls."
    )
def channel_list(format, output, token, cache):
    """Export a list of workspace channels and their basic attributes."""
    channels = [{
        "name": channel["name"],
        "pins": channel["pins"],
        "topic": channel["topic"].replace("\n", " "),
        "purpose": channel["purpose"].replace("\n", " "),
        "prefix": channel["name"].split("-")[0].split("_")[0],
        "member_count": channel["information"]["num_members"],
        "read_only": channel["information"].get("is_read_only", False),
        "creation_date": standard_time(channel["information"]["created"]),
        "creator_name": corpus.user(channel["information"]["creator"])["name"],
        "last_update": standard_time(),
        }
        for channel in corpus.build(token=token, refresh=not cache)
        ]

    if format == "CSV":
        writer = csv.DictWriter(output, fieldnames=channels[0].keys())
        writer.writeheader()
        for channel in channels:
            writer.writerow(channel)

    elif format == "JSON":
        json.dump(channels, output, indent=2, sort_keys=True)


def standard_time(epoch=None):
    """Returns the current time or the specified unix epoch time in UTC."""
    return (
        datetime.datetime.utcfromtimestamp(epoch)
        if epoch else datetime.datetime.now()
        ).isoformat().replace("T", " ")


if __name__ == "__main__":
    channel_list()
