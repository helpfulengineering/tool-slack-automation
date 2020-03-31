import os
import boto3
from unittest import mock
from slack import WebClient


def get_secrets():
    if os.environ.get("STAGE", "dev") == "test":
        return {"apiToken": "", "signingSecret": "a"}
    else:
        secret_arn = os.environ['SECRET_ARN']
        sm_client = boto3.client("secretsmanager")
        secret_value_response = sm_client.get_secret_value(SecretId=secret_arn)
        tokens = json.loads(secret_value_response['SecretString'])
        return tokens


def get_slack_client(api_token):
    if os.environ.get("STAGE", "dev") == "test":
        return mock.MagicMock(WebClient)
    else:
        return WebClient(api_token)
