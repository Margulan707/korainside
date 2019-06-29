#!/bin/sh

# Read the settings.
. ./config.sh

echo "ssh -S $SOCKET -O exit $REMOTE_ADDR"
ssh -S $SOCKET -O exit $REMOTE_ADDR
