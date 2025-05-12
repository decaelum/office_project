#!/bin/bash

cd ~/Desktop/office_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.:txt
python3 tests/test_runner.py