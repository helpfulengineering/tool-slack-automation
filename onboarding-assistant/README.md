# Onboarding assistant

## Common maintenance operations
If you're in charge of updating this application and don't have prior
experience with its internals, you may be interested in taking a look
to some of the following common maintenance operations.

### Modifying the user interface
You can find all the user interface files at [`./code/modules/interface`](./code/modules/interface), in individual [JSON](https://en.wikipedia.org/wiki/JSON) files. These files can be easily edited with the [Slack Block Kit Builder](https://api.slack.com/tools/block-kit-builder) and [committed to this repository](https://docs.github.com/en/free-pro-team@latest/github/managing-files-in-a-repository/editing-files-in-your-repository). If you're not familiar with the syntax used by these messages, you can check the reference documentation [here](https://api.slack.com/reference/surfaces/formatting).

### Modifying the form fields
You'll need to edit the object-relation mappings under [`./code/modules/database`](./code/modules/database) and update the frontend fields by following the steps in the previous section.

If you're interested in modifying the typeahead suggestions for some form fields, you'll need to edit the files under [`./code/menu`](./code/menu).
