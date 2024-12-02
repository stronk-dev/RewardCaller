> [!WARNING]  
> This repository has been superseded by the [OrchestratorSiphon](https://github.com/Stronk-Tech/OrchestratorSiphon)

## better call reward

This script uses a list of configured URL's Orchestrator CLI URL's to get info on the last reward call round and current Livepeer round
Then compare these numbers and if they are not the same calls `reward`.

Modify the `ORCH_TARGETS` variable in `RewardCall.py` to set your Orchestrator URL's

### Dependencies

Requires python 3 and pip: `sudo pacman -S python python-pip`

Then install the requests library using pip `python -m pip install requests`

### Running the script

Recommended to run `better-call-reward.py` as a systemd service:
Move the script to an accessible location, like `/usr/local/bin`
`sudo nano /etc/systemd/system/rewardCaller.service`
```
[Unit]
Description=Reward Caller
After=multi-user.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /usr/local/bin/RewardCall.py

[Install]
WantedBy=multi-user.target
```
