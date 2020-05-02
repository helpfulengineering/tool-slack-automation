#!/bin/bash
cd -- "$(dirname -- "$0")"

virtualenv python
source python/bin/activate
pip install -r requirements.txt
source environment; python application.py
