#!/bin/sh
set -e
#uvicorn main:app --host 0.0.0.0 --port 8008 --reload
#/usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf


if [ "$RUN" = "application" ]; then
  uvicorn main:app --host 0.0.0.0 --port 8008 --reload --workers 8
  exit
fi
#
if [ "$RUN" = "worker" ]; then
 celery -A task worker -l info
 exit
fi
#
if [ "$RUN" = "beat" ]; then
 celery -A task beat --scheduler celery.beat.PersistentScheduler
 exit
fi