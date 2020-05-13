# Slack select menu provider
Serve search completion data to interactive Slack select menus.

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

## Dynamic source structure
:warning: Not implemented yet

## Source selection format
* Query to `source-1` without restricting the number of results:
    `source-1`
* Query to `source-2` with a maximum of 10 results:
    `source-2:10`

## Example interactive block
```json
[
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "Select items from source-1..."
    },
    "accessory": {
      "action_id": "source-2:10",
      "type": "multi_external_select",
      "placeholder": {
        "type": "plain_text",
        "text": "Select items..."
      },
      "min_query_length": 0
    }
  }
]
```
