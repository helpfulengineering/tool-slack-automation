# 1Password account provisioning for Slack

## Behavior

1. The user clicks a shortcut from the :zap: menu.

2. A simple form pops up asking for an email address and a reason for the request.

3. When submitted, the request reason is sent to the chosen channel (see `slack_channel` below).

4. The application will automatically provision an account with the display name of the requestor and the provided address.

5. If the process fails, the application will send a warning to the same channel with a unique identifier that allows to lookup the request in CloudWatch.

6. A member of the 1Password **Provision Managers** group will review the request from the web interface.

## Customization

The modal views, located at [`./code/views`](./code/views) can be modified with a text editor or the [Slack Block Kit Builder](https://api.slack.com/tools/block-kit-builder). The notifications sent to the `slack_channel` (see below) are hardcoded in [`./code/handler.py`](./code/handler.py) and may be edited directly.


## Deployment

1. Get the 1Password command line tools for your system and architecture from [here](https://1password.com/es/downloads/command-line/) and replace [`./code/modules/onepassword/op`](./code/modules/onepassword/op) with the downloaded executable.

2. Create an AWS SecretsManager secret with the following contents:

       {
           "onepassword_key": "A3-XXXXXX-···",
           "onepassword_password": "Long random password",
           "onepassword_site": "team-name.1password.com",
           "onepassword_user": "mail@domain",
           "slack_channel": "G···",
           "slack_token": "xoxb-···"
       }

3. Assign the secret ARN to the `SECRET_ARN` environment variable for the deployment, either with a simple `export SECRET_ARN=arn:···` or by using [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) along with [AWS CodeBuild](https://docs.aws.amazon.com/codebuild/latest/userguide/welcome.html).

4. Set up [AWS CodeBuild](https://docs.aws.amazon.com/codebuild/latest/userguide/welcome.html) with a build specification along these lines:

       version: 0.2

       phases:
         install:
           commands:
              - cd ./onepassword-provisioning
              - npm install -g serverless
              - npm install
         build:
           commands:
              - export TRANSIT_KEY="$(head -c 32 /dev/random | base64)"
              - serverless deploy --stage production

5. Paste the application endpoint address (`https://...execute-api...amazonaws.com/production/slack_interaction`) into the **Features > Interactivity & Shortcuts** section of the Slack application configuration.

6. Add a shortcut in the aforementioned section in order to allow users to invoke the application.

7. Select the following bot scopes from the **Features > OAuth & Permissions** section of the Slack application configuration:
  * `users:read`
  * `chat:write`
  * `command`

***

> *Note: after the first deployment you might need to wait up to 25 minutes for the 1Password token to refresh.*
