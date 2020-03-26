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
    sm_client = boto3.client("secretsmanager")
    secret_value_response = sm_client.get_secret_value(SecretId=os.environ['SECRET_ARN'])
    tokens = json.loads(secret_value_response['SecretString'])
    return tokens

bot_user_id = os.environ['BOT_USER_ID']
slack_secrets = get_secrets()
slack_client = WebClient(slack_secrets['apiToken'])
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(slack_secrets['signingSecret'], "/listening", app)

@app.errorhandler(404)
def not_found(error):
    return Response("404")

@slack_events_adapter.on("message")
def answer_message(event_data):
    event = event_data["event"]
    # Ignore messages in threads, from bots or without the text attribute
    if 'thread_ts' in event or 'bot_profile' in event or 'text' not in event:
        return
    with open(Path(__file__).parent / "welcome.md", "r") as welcome_message:
        recommendations = "" # skills.recommend(event["text"], corpus)
        slack_client.chat_postMessage(
            text=welcome_message.read() + recommendations
            channel=event["channel"],
            thread_ts=event["ts"],
            link_names=True
            )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4444)
