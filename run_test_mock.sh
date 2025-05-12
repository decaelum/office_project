#!/bin/bash

cd ~/Desktop/office_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_tests.txt
python3 tests/Mock/ python3 mock_server.py
