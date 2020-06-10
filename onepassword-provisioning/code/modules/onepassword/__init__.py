"""
1Password command-line interface wrapper with AWS SecretsManager integration.
"""
import subprocess
import datetime
import tempfile
import pathlib
import shutil
import base64
import boto3
import json
import os


def run(*arguments, timeout=60) -> str:
    """
    Runs a 1Password command-line interface command (authenticated).
    """
    with tempfile.TemporaryDirectory() as directory:
        artifacts, token = _retrieve_secret()["onepassword_state"].split(":")
        _extract_artifacts(artifacts, directory)
        return _run_binary(
            "--session=" + token, *arguments,
            directory=directory,
            timeout=timeout / 2
            )


def authenticate(timeout=60) -> dict:
    """
    Gets and refreshes an 1Password session token from SecretsManager.
    """
    secret = _retrieve_secret()
    with tempfile.TemporaryDirectory() as directory:
        if (state := secret.get("onepassword_state")):
            _extract_artifacts(state.split(":")[0], directory)
        token = _run_binary(
            "signin",
            "--raw",
            secret["onepassword_site"],
            secret["onepassword_user"],
            secret["onepassword_key"],
            input=secret["onepassword_password"] + "\n",
            directory=directory,
            timeout=timeout,
            ).strip()
        secret["onepassword_state"] = _pack_artifacts(directory) + ":" + token
        assert len(token) == 43
        _update_secret(secret)


def _run_binary(*arguments, directory, input="", timeout=60) -> str:
    """
    Runs a 1Password binary command-line interface command.
    """
    environment = {variable: directory for variable in ["HOME", "TMPDIR"]}
    binary = pathlib.Path(__file__).parent / "op"
    process = subprocess.run(
        [binary, *arguments],
        capture_output=True,
        timeout=timeout / 2,
        env=environment,
        input=input,
        text=True
        )

    assert not process.stderr, process.stderr + process.stdout
    return process.stdout


def _retrieve_secret(arn=os.environ.get("SECRET_ARN")) -> dict:
    """
    Retrieves a JSON secret from AWS SecretsManager.
    """
    secrets_manager = boto3.client("secretsmanager")
    return json.loads(
        secrets_manager
        .get_secret_value(SecretId=arn)
        .get("SecretString")
        )


def _update_secret(secret: dict, arn=os.environ.get("SECRET_ARN")):
    """
    Updates a JSON secret stored on AWS SecretsManager.
    """
    secrets_manager = boto3.client("secretsmanager")
    secrets_manager.update_secret(
        SecretString=json.dumps(secret),
        SecretId=arn
        )


def _pack_artifacts(directory: pathlib.Path) -> str:
    """
    Packs the given directory contents into a Base64 .tar.gz string.
    """
    path = pathlib.Path(directory) / "artifacts"

    sessions = [
        [session.stat().st_mtime, session]
        for session in path.glob('com.agilebits.op.*/.*')
        if session.is_file()
        ]
    sessions.sort(key=lambda item: item[0])
    for old_session in sessions[:-1]:
        old_session[1].unlink()

    shutil.make_archive(path, "gztar", directory)
    with open(path.with_suffix('.tar.gz'), "rb") as artifacts_file:
        return base64.b64encode(artifacts_file.read()).decode('ascii')
    path.with_suffix('.tar.gz').unlink()


def _extract_artifacts(artifacts: str, directory: pathlib.Path):
    """
    Unpacks a given Base64 .tar.gz string contents into the given directory.
    """
    path = pathlib.Path(directory) / "artifacts"
    with open(path.with_suffix('.tar.gz'), "wb") as artifacts_file:
        artifacts_file.write(base64.b64decode(artifacts))
    shutil.unpack_archive(path.with_suffix('.tar.gz'), directory)
    path.with_suffix('.tar.gz').unlink()
