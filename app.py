#!/usr/bin/env python3

import os
import json
import boto3
import skills
from pathlib import Path
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from flask import Flask, request, make_response, Response


def get_secrets():
    secret_arn = os.environ['SECRET_ARN']
    sm_client = boto3.client("secretsmanager")
    secret_value_response = sm_client.get_secret_value(SecretId=secret_arn)
    tokens = json.loads(secret_value_response['SecretString'])
    return tokens

slack_secrets = get_secrets()
slack_api_token = slack_secrets['apiToken']
slack_signing_secret =slack_secrets['signingSecret']

app = Flask(__name__)
slack_client = WebClient(slack_api_token)
slack_event_adapter = SlackEventAdapter(slack_signing_secret, "/", app)

with open(Path(__file__).parent / "data" / "template.md", "r") as template_file:
    message_template = template_file.read()
with open(Path(__file__).parent / "data" / "corpus.json", "r") as corpus_file:
    corpus = json.load(corpus_file)

def answer_message(event_data):
    event = event_data["event"]
    if 'bot_profile' in event:
        return
    if 'thread_ts' in event:
        return
    if 'text' not in event:
        return
    channels = skills.recommend(event["text"], corpus, limit=3)
    message = message_template.format(channels = channels)
    slack_client.chat_postMessage(
        channel=event["channel"],
        thread_ts=event["ts"],
        link_names=True,
        text=message
        )

@slack_event_adapter.on("message")
def handle_event(event_data):
    answer_message(event_data)
    return

@app.before_request
def skip_retry():
    if int(request.headers.get('X-Slack-Retry-Num', '0')):
        return make_response('', 200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4444)
