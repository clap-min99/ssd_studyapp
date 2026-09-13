#!/usr/bin/env bash
# Render가 배포할 때 자동으로 실행하는 빌드 스크립트
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
