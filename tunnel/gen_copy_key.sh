#!/bin/sh

# Read the settings.
. ./config.sh

cat /dev/zero | ssh-keygen -q -N ""

ssh-copy-id $REMOTE_USER@$REMOTE_ADDR
