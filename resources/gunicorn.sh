#!/bin/bash
pushd /app
gunicorn -c gunicorn.conf.py wsgi:application
popd
