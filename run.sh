#!/bin/bash
cd -- "$(dirname -- "$0")"

if ! test -d ./python; then
  virtualenv python
  source python/bin/activate
  pip install -r requirements.txt
fi

source environment
source python/bin/activate
export FLASK_APP=application.py 
python -m flask run --host=0.0.0.0 --port 80
