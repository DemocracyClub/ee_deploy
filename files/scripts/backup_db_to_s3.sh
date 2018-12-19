#!/bin/sh
set -x
#### BEGIN CONFIGURATION ####

# set dates for backup rotation
NOWDATE=`date +%Y-%m-%d-%H`
DAY_OF_MONTH=`date +%d`
EXPIRE=true
if  [ $DAY_OF_MONTH = 01 ] ;
then
    EXPIRE=false
fi

# set backup directory variables
SRCDIR='/tmp/s3backups_every_election'
DESTDIR='{{ project_name }}'
SHORT_TERM_BUCKET='dc-ee-short-term-backups'

#### END CONFIGURATION ####


# make the temp directory if it doesn't exist
mkdir -p $SRCDIR

pg_dump --host={{ vault_DATABASE_HOST }} -Fc {{ project_name }} -f $SRCDIR/$NOWDATE-backup.dump

if [ $? -ne 0 ]
then
  # if pg_dump failed,
  # clean up
  cd
  rm -f $SRCDIR/*

  # exit with error
  exit 1
fi

# # upload backup to s3
/usr/local/bin/s3cmd put $SRCDIR/$NOWDATE-backup.dump s3://$SHORT_TERM_BUCKET/$DESTDIR/ --storage-class=STANDARD_IA

/usr/local/bin/s3cmd expire s3://$SHORT_TERM_BUCKET --expiry-days=60


#remove all files in our source directory
cd
rm -f $SRCDIR/*
