#!/usr/bin/env bash

python -m venv env
source ./env/bin/activate

pip install -r requirement.txt

cd bin
wget -qO- https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz | tar -xzv
