"""Amazon AWS helper module.
This module provides some trivially named high-level abstractions for the
most commonly used AWS characteristics.
"""

import os
import json
import boto3

dynamodb = boto3.resource('dynamodb')

configuration = json.loads(
    boto3.client("secretsmanager").get_secret_value(
        SecretId=os.environ.get("SECRET_ARN")
        ).get("SecretString")
    )

def invoke_lambda(name, payload, invocation="Event"):
    boto3.client('lambda').invoke(
        FunctionName=os.environ.get("FUNCTION_PREFIX") + name,
        InvocationType=invocation,
        Payload=payload
        )
