## HOW TO USE
1.	Write unique number to `REMOTE_PORT` variable in `config.sh`. This will be port, which you will use to connect to this machine.
2.	Run `gen_copy_key.sh`. Enter password `123456`, when prompted.
3.	Add `start_tunnel.sh` to startup.
4.	You can always close tunnel with `stop_tunnel.sh`.

## FILES
	- `config.sh` contains all configuration variables (ip, port, etc).
	- `gen_copy_key.sh` generates ssh public key (if needed), and sends to the hub.
	- `start_tunnel.sh` starts reverse ssh tunnel.
	- `stop_tunnel.sh` stops reverse ssh tunnel.

