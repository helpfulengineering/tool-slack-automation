#!/usr/bin/env python3

import boto3
import os
import json
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

@slack_events_adapter.on("message")
def answer_message(event_data):
    event = event_data["event"]
    #ignore messages in threads and from bots
    if 'thread_ts' not in event and 'bot_profile' not in event:
        text = event["text"].casefold()
        answer = f"Hello. You've submitted this text: {text}"

        slack_client.chat_postMessage(
            channel=event["channel"],
            link_names=True,
            text=answer,
            thread_ts=event["ts"]
            )


@app.errorhandler(404)
def not_found(error):
    return Response("404")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4444)
