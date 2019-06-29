#!/bin/sh

# Read the settings.
. ./config.sh

echo "ssh -f -N -M -S $SOCKET -R $REMOTE_PORT:$LOCAL_ADDR:$LOCAL_PORT $REMOTE_USER@$REMOTE_ADDR"
ssh -f -N -M -S $SOCKET -R $REMOTE_PORT:$LOCAL_ADDR:$LOCAL_PORT $REMOTE_USER@$REMOTE_ADDR
