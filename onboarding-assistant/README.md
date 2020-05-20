# Onboarding assistant
<!--
[`./code/menu/static.json`](./code/menu/static.json)
## Deployment instructions
1. Create an app in Slack
2. Give it the scopes "channels:history" and "chat:write"
3. Install it in your workspace
4. In AWS, create a secret in Secrets Manager based on smsecrets.json.example but with the information from your bot in slack
5. In your local environment, create local_config.yml based on local_config.yml.example and add the arn from Secrets Manager
6. Deploy the lambda using serverless
7. From AWS, get the url for your lambda from API Gateway
8. In Slack, put that url into the event subscriptions
9. In Slack under event subscriptions, subscribe to message.channels under "Subscribe to Bot Events"
10. Invite the bot to the channel you want it in
-->
