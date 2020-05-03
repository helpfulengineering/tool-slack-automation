# Slack select provider
Serverless function for providing search completion data to Slack interaction dialogs

## Example block
```
[
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "Tell us more about your skills:"
    },
    "accessory": {
      "action_id": "skills:10",
      "type": "multi_external_select",
      "placeholder": {
        "type": "plain_text",
        "text": "Add skills..."
      },
      "min_query_length": 1
    }
  }
]
```
