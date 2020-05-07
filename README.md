# Slack select provider
Serverless function for providing search completion data to Slack interaction dialogs

## Static source structure
[`data.json`](./data.json)
```json
{
    "source-1": [
        "item-1",
        "item-2",
        "item-3",
    ],
    "source-2": [
        "item-1",
        "item-2",
        "item-3",
    ]
}
```

## Source selection format
* Query to `source-1` without restricting the number of results:
    `source-1`
* Query to `source-1` with a maximum of 10 results:
    `source-1:10`

## Example intreactive block
```json
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
