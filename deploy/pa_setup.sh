#!/bin/bash
# PythonAnywhere setup helper - run this on PythonAnywhere or adapt locally
# 1) Clone repo (or `cd` to existing repo)
# 2) Create and activate a virtualenv, then install requirements
# 3) Copy .env from .env.example and edit secrets

set -e

if [ ! -d "$HOME/ClinicConnect" ]; then
  git clone https://github.com/niyati10000/ClinicConnect.git "$HOME/ClinicConnect"
fi
cd "$HOME/ClinicConnect"
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create .env from example if missing
if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "Created .env from .env.example — edit it with your secrets before starting the web app"
fi

echo "PythonAnywhere setup helper finished. Configure the web app to use WSGI file: $HOME/ClinicConnect/wsgi.py and virtualenv: $HOME/ClinicConnect/venv"
