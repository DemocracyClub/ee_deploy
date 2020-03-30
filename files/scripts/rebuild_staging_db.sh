#!/bin/sh
set -e

export PGPASSWORD={{ vault_DATABASE_PASSWORD }}

# Drop and re-create the staging DB
dropdb -U {{ project_name }} --host={{ vault_DEFAULT_DATABASE_HOST }} {{ staging_db_name }}
createdb -U {{ project_name }} --host={{ vault_DEFAULT_DATABASE_HOST }} {{ staging_db_name }}

# Dump the prod DB and load it into staging
pg_dump -U {{ project_name }} --host={{ vault_DEFAULT_DATABASE_HOST }} {{ project_name }} | psql -U {{ project_name }} --host={{ vault_DEFAULT_DATABASE_HOST }} -d {{ staging_db_name }}
