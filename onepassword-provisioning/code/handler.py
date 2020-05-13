import os
import json
import boto3
import secrets
import traceback
import subprocess
import onepassword
from pathlib import Path
from slack import WebClient
from itsdangerous import URLSafeSerializer


with open(Path(__file__).parent / "views" / "form.json") as form_view_file:
    form_view = form_view_file.read()
with open(Path(__file__).parent / "views" / "end.json") as end_view_file:
    end_view = end_view_file.read()

configuration = json.loads(
    boto3.client("secretsmanager").get_secret_value(
        SecretId=os.environ.get("SECRET_ARN")
        ).get("SecretString")
    )

serializer = URLSafeSerializer(os.environ.get("TRANSIT_KEY", " "))
slack_client = WebClient(configuration["slack_token"])
function_prefix = os.environ.get("FUNCTION_PREFIX")


def slack_interaction(event, context):
    action = json.loads(event["body"]["payload"])

    if action["type"] == "view_submission":
        payload = [
            action["user"],
            action["view"]["state"]["values"]["address"]["address"]["value"],
            action["view"]["state"]["values"]["reason"]["reason"]["value"]
            ]
        boto3.client('lambda').invoke(
            FunctionName=os.environ.get("FUNCTION_PREFIX") + "create_account",
            Payload=json.dumps({"payload": serializer.dumps(payload)}),
            InvocationType='Event'
            )
        return {
            "response_action": "update",
            "view": end_view
            }

    elif action["type"] == "shortcut":
        slack_client.views_open(
            trigger_id=action["trigger_id"],
            view=form_view
            )

    return ""


def create_account(event, context):
    user, address, reason = serializer.loads(event["payload"])

    try:
        onepassword.run("create", "user", address, user["name"])
    except Exception as error:
        trace = ''.join(traceback.format_exception(
            tb=error.__traceback__,
            etype=type(error),
            value=error
            ))
        slack_client.chat_postMessage(
            channel=configuration["slack_channel"],
            link_names=True,
            text=(
                f""":warning: <@{user["id"]}> """
                "*has issued an invalid request* "
                f"(`{(identifier := secrets.token_hex(4))}`)"
                )
            )
        print(json.dumps({
            "request": identifier,
            "user": user["id"],
            "address": address,
            "reason": reason,
            "trace": trace
            }))
    finally:
        notification = (
            f"""<@{user["id"]}> requested an account because…"""
            "\n\n" + "\n".join("> " + line for line in reason.split("\n"))
            )
        slack_client.chat_postMessage(
            channel=configuration["slack_channel"],
            text=notification,
            link_names=True
            )


def refresh_token(event, context):
    onepassword.authenticate()
