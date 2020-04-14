# Helpful Engineering Slack data analysis toolkit
A comprehensive set of tools for analyzing the contributions to the
Helpful Engineering Slack community. Currently it's focused on model
generation for a bot-based channel recommendation system, but is versatile
enough to generate even channel-specific word clouds, per-channel activity charts
and some other niceties.

### :book: Usage

1. Initialize a new virtual environment: 
    ```bash
    virtualenv virtual_environment && source $_/bin/activate
    ``` 
    
2. Install the requirements:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the examples:
    ```bash
    python -m examples.channel_list --no-cache --token xoxp-··· \
                                    --format csv --output ./channels.csv

    python -m examples.classifier_model --channel-filter "(project.*|skill.*|communication.*|discussion.*|hardware.*|medical.*|legal.*|comms.*|fundraising.*)" \
                                        --channel-threshold 0.5 \
                                        --output ./model.json

    python -m examples.data_visualization --output ./images_folder
    ```
    
Note: the first run may take eons while gathering the information.

### :lock: Security

After the first run, [`./corpus/cache`](/corpus/cache) is populated with sensitive data, and it should be handled **with the same care** as the token.

***

## Future improvements
- [ ] Integrate [tool-experience-tagger](https://github.com/helpfulengineering/tool-experience-tagger) into this project.
- [ ] Automate the category training method or, at least, make it easier through [prodigy](https://prodi.gy) or [doccano](https://doccano.herokuapp.com).
