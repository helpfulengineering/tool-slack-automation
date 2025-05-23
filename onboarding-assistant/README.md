# Onboarding assistant

⚠️ **Warning:** commits pushed to the `master` branch get automatically deployed to the production environment through AWS CodeBuild on the `he-sandbox2` account at the `us-east-1` region.

## Common maintenance operations
If you're in charge of updating this application and don't have prior
experience with its internals, you may be interested in taking a look
to some of the following common maintenance operations.

### Modifying the user interface
You can find all the user interface files at [`./code/modules/interface`](./code/modules/interface), in individual [JSON](https://en.wikipedia.org/wiki/JSON) files. These files can be easily edited with the [Slack Block Kit Builder](https://api.slack.com/tools/block-kit-builder) and [committed to this repository](https://docs.github.com/en/free-pro-team@latest/github/managing-files-in-a-repository/editing-files-in-your-repository). If you're not familiar with the syntax used by these messages, you can check the reference documentation [here](https://api.slack.com/reference/surfaces/formatting).

### Modifying the form fields
You'll need to edit the object-relation mappings under [`./code/modules/database`](./code/modules/database) and update the frontend fields by following the steps in the previous section.

If you're interested in modifying the typeahead suggestions for some form fields, you'll need to edit the files under [`./code/menu`](./code/menu).

## Slack Setup

### Identifying the API Gateway Base URL

* In `us-east-1` region of the `he-sandbox2`, find navigate to the [API Gateway](https://us-east-1.console.aws.amazon.com/apigateway/main/apis?api=unselected&region=us-east-1) page and click on the `production-onboarding-assistant` API
* Click on `API settings` option in the side panel (should take you to `/apigateway/main/apis/API_ID_HERE/api-detail`)
* Look for **Default endpoint** on the page (should look like `https://API_ID_HERE.execute-api.us-east-1.amazonaws.com`)

You will need this value to configure Slack interactivity and subscriptions

### Configuring in Slack

#### Finding the app in Slack

* If you have access to the app, navigate to [Your Apps](https://api.slack.com/apps)
* Click on [Onboarding assistant](https://api.slack.com/apps/A010YT72ADN)

#### Ensure Interactivity & Shortcuts is enabled

* Navigate to [Interactivity & Shortcuts](https://api.slack.com/apps/A010YT72ADN/interactive-messages?)
* Under the **Interactivity** heading ensure that the **Request URL** field us using the API Gateway Base URL defined above with a `/production/interactivity` suffix
  * Should look something like `https://API_ID_HERE.execute-api.us-east-1.amazonaws.com/production/interactivity`
* Under the **Select Menus** heading ensure that the **Options Load URL** field us using the API Gateway Base URL defined above with a `/production/search` suffix
  * Should look something like `https://API_ID_HERE.execute-api.us-east-1.amazonaws.com/production/search`

⚠️ **NOTE:** clicking the form button requires a response within 3 seconds, ensure the interactivity endpoint is responsive -- may require adjusting cold start settings including the warmup function to make sure this works consistently

#### Ensure Event Subscriptions is enabled

* Navigate to [Event Subscriptions](https://api.slack.com/apps/A010YT72ADN/event-subscriptions?)
* Under the **Enable Events** heading ensure that the **Request URL** field us using the API Gateway Base URL defined above with a `/production/events` suffix
  * Should look something like `https://API_ID_HERE.execute-api.us-east-1.amazonaws.com/production/events`

⚠️ **NOTE:** after this is updated, you will need to re-install the app (you should be prompted to do this automatically

* Under the **Subscribe to bot events** heading ensure the following are configured:
  * [message.channels](https://api.slack.com/events/message.channels): A message was posted to a channel (scope: `channels:history`)
  * [message.im](https://api.slack.com/events/message.im): A message was posted in a direct message channel (scope: `im:history`)
  * [team_join](https://api.slack.com/events/team_join): A new member has joined (scope: `users:read`)
