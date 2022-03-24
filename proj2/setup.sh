#!/bin/bash

python3 -m venv venv
source venv/bin/activate
pip3 install -r my_requirements.txt
./getSpacy.sh
./getSpanBert.sh
