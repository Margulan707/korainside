#!/bin/sh
while ! ping -c 1 -W 1 134.209.255.83; do
    echo "Waiting for google.com - network interface might be down..."
    sleep 1
done
cd /home/margulan/Desktop/tunnel
sh start_tunnel.sh
touch /home/margulan/Desktop/YASDELAL.txt
