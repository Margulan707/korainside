#!/bin/sh

# Read the settings.
. ./config.sh

while ! ping -c 1 -W 1 8.8.8.8; do
	echo "Waiting for network..."
	sleep 1
done

echo "ssh -f -N -M -S $SOCKET -R $REMOTE_PORT:$LOCAL_ADDR:$LOCAL_PORT $REMOTE_USER@$REMOTE_ADDR"
ssh -f -o ServerAliveInterval=10 -N -M -S $SOCKET -R $REMOTE_PORT:$LOCAL_ADDR:$LOCAL_PORT $REMOTE_USER@$REMOTE_ADDR
