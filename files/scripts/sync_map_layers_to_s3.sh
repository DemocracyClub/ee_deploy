#!/bin/sh
set -e

{{ project_root }}/env/bin/python {{ project_root }}/code/manage.py export_boundaries --from 2019-01-01 --to 2019-05-01 --output {{ project_root }}/code/every_election/data/maps
/usr/local/bin/s3cmd put -r {{ project_root }}/code/every_election/data/maps/ s3://ee-maps/ --acl-public -m "application/json"
rm {{ project_root }}/code/every_election/data/maps/*
