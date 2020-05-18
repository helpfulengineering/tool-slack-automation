import os
import json
import matcher
import hashlib
import boto3
from pathlib import Path
from slackeventsapi import SlackEventAdapter
from airtable import airtable
from flask import Flask, request, make_response, Response
from unittest import mock
import slack


application = Flask(__name__)
configuration = json.loads(
    boto3.client("secretsmanager").get_secret_value(
        SecretId=os.environ.get("SECRET_ARN")
        ).get("SecretString")
    )
slack_client = (
    slack.WebClient(token)
    if (token := configuration.get("slack_token")) else
    mock.MagicMock(slack.WebClient)
    )
slack_event_adapter = SlackEventAdapter(
    configuration.get("slack_signing_secret", "a"),
    "/events",
    application
    )
volunteers=airtable.Airtable(
    configuration["airtable_base"],
    api_key=configuration["airtable_token"]
    )
function_prefix = os.environ.get("FUNCTION_PREFIX")

data_directory = Path(__file__).parent / "data"

with open(data_directory / "elements" / "form.json", "r") as form_file:
    form = json.load(form_file)
with open(data_directory / "model.json", "r") as model_file:
    model = json.load(model_file)
with open(data_directory / "elements" / "welcome.json", "r") as welcome_file:
    welcome = json.load(welcome_file)
with open(data_directory / "elements" / "success.json", "r") as success_file:
    success = json.load(success_file)
with open(data_directory / "template.md", "r") as template_file:
    message_template = template_file.read()

@application.route("/interactivity", methods=["POST"])
def message_actions():
    action = json.loads(request.form["payload"])
    if action["type"] == "shortcut":
        handle_team_join({"event": action})
    elif all([
        action["type"] == "block_actions",
        action['actions'][0]['action_id'] == "show_form"
    ]):
        slack_client.views_open(trigger_id=action["trigger_id"], view=form)
    elif action["type"] == "view_submission":
        def extract(value):
            value = list(value.values())[0]
            if value["type"] == "static_select":
                return [value["selected_option"]["value"]]
            elif value["type"] == "multi_external_select":
                return [item["value"] for item in value["selected_options"]]
            elif value["type"] == "plain_text_input":
                return value["value"]
        state = {
            field: extract(value)
            for field, value in action["view"]["state"]["values"].items()
            }
        labels = [
            f"{name}:{value}"
            for name, item in state.items()
            for value in item
            if type(item) is list
        ]
        user = slack_client.users_info(user=action["user"]["id"])["user"]

        volunteers.create(configuration["airtable_table"], {
            "Slack Handle": user["profile"]["display_name_normalized"],
            "Slack User ID":  user["id"],
            # "Email": "",
            # "Profession": "",
            # "External Organization": "",
            "Volunteer Interest": True,
            # # "Weekly Capacity": "",
            # # "Languages": "",
            # # "Industry": "",
            # "City": "",
            # "State/Province": "",
            # "Zip Code": "",
            # # "Country": "",
            "Timezone": user["tz_label"],
            # # "Skills": "",
            "Additional Skills": "; ".join(labels),
            # "Equipment": "",
            # "Experience": "",
            "Management Interest": False,
            "Privacy Policy": True,
            })

        # slack_client.chat_postMessage(
        #     channel="G012HLGCNKY",
        #     link_names=True,
        #     text=
        #     user=action["user"]["id"]
        #     skills=", ".join(state["skills"] + state["languages"])
        #     reasons=state["reasons"]
        #     )

        return success
    else:
        return ""


@slack_event_adapter.on("team_join")
def handle_team_join(event):
    event = event["event"]
    welcome["blocks"][0]["text"]["text"] = (
        welcome["blocks"][0]["text"]["text"].format(user=event["user"]["id"])
        )
    # slack_client.chat_postMessage(
    #     channel=event["user"]["id"],
    #     link_names=True,
    #     **welcome,
    #     text=""
    #     )
    return make_response("", 200)


# DEPRECATED
@slack_event_adapter.on("message")
def handle_message(event):
    event = event["event"]
    if 'bot_profile' in event:
        return
    if 'thread_ts' in event:
        return
    if 'text' not in event:
        return
    suggestion = ""
    channels = "\n".join(matcher.recommend_channels(model, event["text"]))
    jobs = "\n".join(matcher.recommend_jobs(model, event["text"]))
    if channels:
        suggestion += (
            "\n*Recommended channels*\n" + channels + "\n"
            "(#skill channels have people with similar skills in them; "
            "#discussion channels talk about a topic; #project channels "
            "are working on a project)\n"
            )
    if jobs:
        suggestion += "\n*Recommended jobs*\n{}\n".format(jobs)
    message = message_template.format(suggestion=suggestion)

    print(slack_client.chat_postMessage(
        channel=event["channel"],
        thread_ts=event["ts"],
        link_names=True,
        text=message
        ))
    return


@application.before_request
def skip_retry():
    if int(request.headers.get('X-Slack-Retry-Num', '0')):
        return make_response('', 200)


if __name__ == "__main__":
    application.run(
        host="0.0.0.0",
        port=80
        )
