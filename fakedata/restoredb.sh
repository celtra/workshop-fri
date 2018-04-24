#!/bin/bash
##
# Restores DB to heroku
set -eu -o pipefail

function usage() {
    cat <<EOF
Usage: $(basename $0) -H [hostname] -U [username] -D [db_name] -F [filename.dump]
Description:
Options:
    -H        Specify hostname of PostgreSQL db to restore to
    -U        Specify username to use
    -D        Specify database name to use
    -F        Specify filename to use, default: db.dump
EOF
exit 1
}

HOST=
USER=
DB_NAME=
FILENAME=db.dump

while getopts "H:U:D:F:" OPTION
do
     case $OPTION in
         h) usage
            exit 0 ;;
         H) HOST=$OPTARG;;
         U) USER=$OPTARG;;
         D) DB_NAME=$OPTARG;;
         F) FILENAME=$OPTARG;;
         :) usage ;;
     esac
done

if [ "x$HOST" = "x" ] || [ "x$USER" = "x" ] || [ "x$DB_NAME" = "x" ]
then
    usage
fi

pg_restore --verbose --clean --no-acl --no-owner -h $HOST -U $USER -d $DB_NAME $FILENAME
