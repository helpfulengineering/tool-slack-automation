#!/usr/bin/env python3

import os
import re
import json
import string
import asyncio
import secrets
import traceback
import subprocess
from pathlib import Path
from threading import Thread
from flask import Flask, request, make_response, Response
from slackeventsapi import SlackEventAdapter
from slack import WebClient

app = Flask(__name__)
app.debug = True

slack_channel = os.getenv("SLACK_CHANNEL")
slack_api_token = os.getenv("SLACK_TOKEN")
slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")

command = (Path(__file__).parent / "library" / "1password").absolute()

slack_event_adapter = SlackEventAdapter(slack_signing_secret, "/", app)
slack_client = WebClient(slack_api_token)


class ProvisionAccount(Thread):
    def __init__(self, user, address, reason):
        self.user, self.address, self.reason = user, address, reason
        Thread.__init__(self)

    def run(self):
        print(self.user, self.address, self.reason)
        try:
            assert json.loads(subprocess.run(
                [command, "create", "user", self.address, self.user["name"]],
                stdout=subprocess.PIPE,
                timeout=60
                ).stdout)
        except Exception as error:
            identifier = secrets.token_hex(4)
            trace = ''.join(traceback.format_exception(
                tb=error.__traceback__,
                etype=type(error),
                value=error
                ))
            slack_client.chat_postMessage(
                text=(
                    f""":warning: <@{self.user["id"]}> """
                    "*has issued an invalid request* "
                    f"(`{identifier}`)"
                ),
                channel=slack_channel,
                link_names=True
                )
            with open(Path(__file__).parent / "log", "a+") as log:
                json.dump([
                    identifier,
                    self.user["id"],
                    self.address,
                    self.reason,
                    trace
                ], log)
                log.write("\n")


@app.route("/slack/message_actions", methods=["POST"])
def message_actions():
    action = json.loads(request.form["payload"])
    if action["type"] == "shortcut":
        open_dialog = slack_client.views_open(
            trigger_id=action["trigger_id"],
            view={
                "type": "modal",
                "title": {
                    "type": "plain_text",
                    "text": "1Password account"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Request"
                },
                "close": {
                    "type": "plain_text",
                    "text": "Cancel"
                },
                "blocks": [
                    {
                        "type": "input",
                        "element": {
                            "type": "plain_text_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "user@example.com"
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "What's your email address?"
                        }
                    },
                    {
                        "type": "input",
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "I need it because..."
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Why do you need 1Password?"
                        }
                    }
                ]
            })
        return make_response("", 200)

    elif action["type"] == "view_submission":
        user = action["user"]
        blocks = action["view"]["blocks"]
        values = action["view"]["state"]["values"]
        reason_block = blocks[1]["block_id"]
        address_block = blocks[0]["block_id"]
        reason_element = blocks[1]["element"]["action_id"]
        address_element = blocks[0]["element"]["action_id"]
        reason = values[reason_block][reason_element]["value"]
        address = values[address_block][address_element]["value"]
        ProvisionAccount(user, address, reason).start()
        slack_client.chat_postMessage(
            channel=slack_channel,
            link_names=True,
            text=(
                f"""<@{action["user"]["id"]}> """ +
                "requested an account because…\n\n" +
                "\n".join("> " + line for line in reason.split("\n"))
                )
            )

        return {
            "response_action": "update",
            "view": {
                "type": "modal",
                "title": {
                    "type": "plain_text",
                    "text": "Sent!"
                },
                "close": {
                    "type": "plain_text",
                    "text": "Close"
                },
                "blocks": [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            "You’ve applied for a :helpful: 1Password"
                            " account. Once your request is approved,"
                            " you’ll receive an activation email with"
                            " instructions.\n\nPlease read the <https"
                            "://github.com/helpfulengineering/devops/"
                            "blob/master/documentation/guidance/crede"
                            "ntial-sharing.md|credential sharing guid"
                            "e> for more information."
                        )
                    }
                }]
            }
        }


@app.before_request
def skip_retry():
    if int(request.headers.get('X-Slack-Retry-Num', '0')):
        return make_response('', 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
