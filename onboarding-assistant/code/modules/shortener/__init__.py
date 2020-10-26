"""Link shortener with metadata support.
This module provides link shortening capabilities with metadata support.
>>> shortener.shorten("https://google.com", user="me")
>>> link, information = shortener.expand(_)
"""
import os
import re
import json
import secrets
import amazon
import analytics


table = amazon.dynamodb.Table(os.getenv("SHORTENER_TABLE"))


def shorten(link, **information):
    """Shortens the given link along with the provided additional information.
    >>> shortener.shorten('https://google.com', user='me')
    'https://short/A1B2C3'
    """
    def put(code, link, information):
        """Creates an unique record; otherwise returns False."""
        exceptions = amazon.dynamodb.meta.client.exceptions
        try:
            table.put_item(
                ExpressionAttributeValues={':code': code},
                ConditionExpression='code <> :code',
                Item={
                    "information": information,
                    "link": link,
                    "code": code,
                    "visits": 0
                    })
        except exceptions.ConditionalCheckFailedException:
            return False
        else:
            return True

    while not put(code := secrets.token_urlsafe(4), link, information):
        print("warning: link shortener collision detected")
    return amazon.configuration["shortener_prefix"] + code


def query(link):
    """Retrieves all the supporting data for a given short link or code.
    >>> shortener.query('https://short/A1B2C3')
    'https://google.com'
    """
    code = link.split("/").pop()  # extract the last address component
    return table.get_item(Key={"code": code}).get("Item", False)


def expand(link):
    """Expands a given short link or code into its corresponding full link.
    >>> shortener.expand('https://short/A1B2C3')
    'https://google.com'
    """
    if (item := query(link)):
        table.update_item(
            UpdateExpression="SET visits = visits + :increment",
            ExpressionAttributeValues={":increment": 1},
            Key={"code": item["code"]}
            )
        return item["link"], item["information"], item["visits"]
    else:
        return False  # not found


def replace(string, **information):
    """Replaces every Slack Mrkdwn link on a string with its shortened variant.
    >>> shortener.replace('See <https://google.com|this> link!', user='me')
    'See <https://short/A1B2C3|this> link!'
    """
    def process(match):
        link = match.group("link")
        text = match.group("text")
        return "<" + shorten(link, **information) + (text or "") + ">"
    link_matcher = r"<(?P<link>[^#@][^<|>]+?)(?P<text>\|[^<|>]+)?>"
    return re.sub(link_matcher, process, string)


def replacer(**information):
    """Returns a `replacer` partial function with fixed information.
    >>> shortener.replacer(user='me')('See <https://google.com|this> link!')
    'See <https://short/A1B2C3|this> link!'
    """
    def partial(string, **arguments):
        return replace(string, **{**information, **arguments})
    return partial
