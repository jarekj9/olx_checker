#!/usr/bin/env bash

# need multiple threads and 1 worker for continuous progress reading, before final result
(gunicorn --user www-data --bind 0.0.0.0:5000 api.api:app --workers 1 --threads 100) & nginx -g "daemon off;"
