import json
import slack

import amazon
import analytics
import database
import interface
import shortener
import maps
import recommendations

from flask import Flask, request, make_response, Response
from slackeventsapi import SlackEventAdapter


application = Flask(__name__)
slack_token = amazon.configuration["slack_token"]
slack_secret = amazon.configuration["slack_signing_secret"]
slack_event_adapter = SlackEventAdapter(slack_secret, "/events", application)
slack_client = slack.WebClient(slack_token)


@application.route("/interactivity", methods=["POST"])
def handle_interactivity():
    """Handles Slack Interactivity Payloads."""
    action = json.loads(request.form["payload"])
    if action["type"] == "shortcut":
        handle_team_join({"event": action})
    elif action["type"] == "view_submission":
        # Run handle_form_submission() in the background
        amazon.invoke_lambda("form", action)
    elif action["type"] == "block_actions":
        if action["actions"][0]["action_id"] == "show_form":
            handle_show_form_action(action)
    return ""


def handle_show_form_action(action):
    """Shows the volunteer form when triggered."""
    if database.check_volunteer(action["user"]["id"]):
        analytics.event(action["user"]["id"], "form", "fill-duplicate")
        error = "Error: it looks like you've already filled the form."
        slack_client.chat_postMessage(text=error, channel=action["user"]["id"])
    else:
        analytics.event(action["user"]["id"], "form", "fill")
        form = interface.views["form"].format(session=action["trigger_id"])
        slack_client.views_open(trigger_id=action["trigger_id"], view=form)


def handle_form_submission(event, context=None):
    """Handles a form submission backend- and frontend-wise."""
    def extract(value):
        """Extracts a form field from the event."""
        value = list(value.values())[0]
        if value["type"] in ("static_select", "external_select"):
            return [value.get("selected_option", {}).get("value")]
        elif value["type"] in ("multi_external_select", "checkboxes"):
            return [item["value"] for item in value.get("selected_options", [])]
        elif value["type"] == "plain_text_input":
            return value.get("value", "")
    form = {
        field: extract(value)
        for field, value in event["view"]["state"]["values"].items()
        }
    database.insert_volunteer_record(
        slack_client.users_info(user=event["user"]["id"])["user"],
        maps.address(form["location"].pop()),
        form
        )
    introduction_message = interface.views["introduction"].format(
        user=event["user"]["id"],
        skills=", ".join(form["skills"] + form["languages"]),
        experience=form["experience"]
        )
    user = slack_client.users_info(user=event["user"]["id"])["user"]
    slack_client.chat_postMessage(
        username=(
            user["profile"]["display_name_normalized"] or
            user["profile"]["real_name_normalized"]
            ),
        icon_url=user["profile"]["image_512"],
        **introduction_message,
        channel="CUXD81R6X",
        link_names=True,
        text="",
        )
    introduction = "\n".join([
        form["experience"],
        form["profession"],
        " ".join(form["skills"]),
        " ".join(form["industries"])
        ])
    channels = "\n".join(recommendations.channels(introduction))
    jobs = "\n".join(recommendations.jobs(introduction))
    slack_client.chat_postMessage(
        **interface.views["thanks"].format(
            function=shortener.replacer(
                user=event["user"]["id"],
                source="private"
                ),
            user=event["user"]["id"],
            channels=channels,
            jobs=jobs
            ),
        channel=event["user"]["id"],
        link_names=True,
        text=""
        )
    analytics.event(event["user"]["id"], "form", "submit")


@application.route('/', defaults={'path': ''})
@application.route('/<path:path>')
def handle_redirect(path):
    """Catch-all route for the link shortener."""
    if (item := shortener.expand(path)):
        link, information, visits = item
        user = information.get("user", "")
        label = information.get("label", "")
        analytics.event(user, "link", link, label)
        headers = {"Location": link, "Cache-Control": "no-store"}
        return make_response("Redirecting...", 302, headers)
    else:
        return make_response("Not found", 404)


@slack_event_adapter.on("team_join")
def handle_team_join(event):
    user = event["event"]["user"]["id"]
    replacer = shortener.replacer(user=user)
    welcome = interface.views["welcome"].format(function=replacer, user=user)
    slack_client.chat_postMessage(
        channel=event["event"]["user"]["id"],
        link_names=True,
        **welcome,
        text=""
        )
    analytics.event(user, "team", "join")
    return ""


@slack_event_adapter.on("message")
def handle_message(event):
    if event["event"].get("subtype") == "bot_message":
        return
    if 'bot_profile' in event["event"]:
        return
    if 'thread_ts' in event["event"]:
        return
    if 'text' not in event["event"]:
        return

    blocks = interface.views["welcome"]["blocks"]

    suggestion = "\n\n*Recommended channels*\n" + "\n".join(set(
        recommendations.channels(event["event"]["text"]) + [
            "#skill-software-devops",
            "#skill-medical-personnel",
            "#skill-project-managers-office",
            "#skill-research",
            "#skill-software-datascience",
            "#skill-writer"
            ]
        ))
    if (jobs := "\n".join(recommendations.jobs(event["event"]["text"]))):
        suggestion += "\n\n*Recommended jobs*\n" + jobs
    suggestion_block = [
        {"type": "divider"},
        {"type": "context", "elements": [
            {"type": "mrkdwn", "text": suggestion}]}]

    user = event["event"]["user"]
    replacer = shortener.replacer(user=user, source="public")
    slack_client.chat_postMessage(
        channel=event["event"]["channel"],
        thread_ts=event["event"]["ts"],
        link_names=True,
        text=suggestion,
        **interface.View({"blocks": blocks + suggestion_block}).format(
            user=user, function=replacer
            )
        )
    return ""


@application.before_request
def ignore_retry():
    """Ignores API retries to avoid duplicate requests with slow Lambdas."""
    if int(request.headers.get('X-Slack-Retry-Num', '0')):
        return make_response('', 200)


@application.after_request
def skip_cache(request):
    """Tells the client not to cache the responses."""
    request.headers["Cache-Control"] = "no-store"
    return request
