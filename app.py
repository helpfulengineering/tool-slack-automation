#!/usr/bin/env python3

import os
from slack import WebClient
from flask import Flask, request, make_response, Response

slack_client = WebClient(os.environ["SLACK_BOT_TOKEN"])
app = Flask(__name__)


def answer_message(event):
    if not "user" in event or "edited" in event or event["channel"] != CHANNEL:
        return  # Exclude global events, editions and messages outside CHANNEL
    user = slack_client.api_call("users.info", user=event["user"])["user"]
    text = event["text"].casefold()
    answer = f"Hello, {user['real_name']}. You've submitted this text: {text}"

    slack_client.api_call(
        "chat.postEphemeral",
        channel=os.environ["SLACK_CHANNEL"],  # "CUXD81R6X" == #introductions
        user=event["user"],
        link_names=True,
        text=answer,
        )


@app.errorhandler(404)
def not_found(error):
    return Response("404")


@app.route("/listening", methods=["GET", "POST"])
def listening():
    data = request.get_json()

    if "challenge" in data:
        return Response(data["challenge"], mimetype="application/json")
    elif data["token"] != os.environ["SLACK_VERIFICATION_TOKEN"]:
        return make_response("", 403)

    if data["event"]["type"] == "message":
        answer_message(data["event"])
        return make_response("", 200)
    else:
        return make_response("", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4444)
