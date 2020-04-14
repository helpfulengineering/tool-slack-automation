# Helpful Engineering Slack data analysis toolkit
A comprehensive set of tools for analyzing the contributions to the
Helpful Engineering Slack community. Currently it's focused on model
generation for a bot-based channel recommendation system, but is versatile
enough to generate even channel-specific word clouds, per-channel activity charts
and some other niceties.

### Usage

```bash
virtualenv virtual_environment && source $_/bin/activate

pip install -r requirements.txt

python -m examples.channel_list --no-cache --token xoxp-··· \
                                --format csv --output ./channels.csv

python -m examples.classifier_model --channel-filter "project-.*" \
                                    --channel-threshold 0.5 \
                                    --output ./model.json

python -m examples.data_visualization --output ./images_folder
```
***

## Future improvements
- [ ] Integrate [tool-experience-tagger](https://github.com/helpfulengineering/tool-experience-tagger) into this project.
- [ ] Automate the category training method or, at least, make it easier through [prodigy](https://prodi.gy) or [doccano](https://doccano.herokuapp.com).
