#!/bin/python3
import requests
import time
import sys
from datetime import datetime


# EDIT THIS to set your O cliAddr targets which this script should call reward on
ORCH_TARGETS = ['http://127.0.0.1:7935'] 


# Global Constants
sleepTimeActive = 60        # Wait time when there is any O which has to call reward this round
sleepTimeIdle = 60 * 60 * 4 # Wait time between round checks

# Logs `info` to the terminal with an attached datetime
def log(info):
    print("[", datetime.now(), "] - ", info)
    sys.stdout.flush()

# Gets the last round the orch called reward
def getLastRewardRound(url):
    try:
        r = requests.get(url + '/orchestratorInfo')
    except requests.exceptions.RequestException as e:
        return 0
    if r.status_code != 200:
        return 0
    return r.json()['Transcoder']['LastRewardRound']

# Return the current active Livepeer round
def getCurrentRound(url):
    try:
        r = requests.get(url + '/currentRound')
    except requests.exceptions.RequestException as e:
        return 0
    if r.status_code != 200:
        return 0
    return int(r.content.hex(), 16)

class Orchestrator:
  def __init__(self, uri):
    self.uri = uri
    self.rewardRound = 0
    self.currentRound = 0
    self.hasReward = False

latestRound = 0
orchestrators = []
# Init orch objecs
for url in ORCH_TARGETS:
    log("Adding Orchestrator with URL '" + url + "'")
    orchestrators.append(Orchestrator(url))
# Main loop
while True:
    # Init delay to a long sleep time. Override later if an O requires reward calling
    delay = sleepTimeIdle
    for i in range(len(orchestrators)):
        # Update last round if we have a new one
        currentRound = getCurrentRound(orchestrators[i].uri)
        if currentRound == 0:
            log("Error: can't get current round info on '" + url + "'")
            orchestrators[i].hasReward = False
            delay = sleepTimeActive
            continue
        if currentRound > latestRound:
            latestRound = currentRound
            # Reset hasReward flags for all O's since the latest round has changed
            for j in range(len(orchestrators)):
                orchestrators[j].hasReward = False
        # If we are behind in rounds, notify user
        if currentRound < latestRound:
            log("Orchestrator '" + orchestrators[i].uri + "' is behind in block syncing!")
        # We can continue now if the latest round has not changed
        if orchestrators[i].hasReward:
            log("Skipping Orchestrator '" + orchestrators[i].uri + "' since they have called reward this round")
            continue
        # Check the last reward round
        lastRewardRound = getLastRewardRound(orchestrators[i].uri)
        if lastRewardRound == 0:
            log("Error: can't get last reward round info on '" + url + "'")
            orchestrators[i].hasReward = False
            delay = sleepTimeActive
            continue
        log("Latest reward round for Orchestrator '" + orchestrators[i].uri + "' is "  + str(lastRewardRound) +  " and the latest livepeer round is " + str(latestRound))
        if lastRewardRound < latestRound:
            log("Calling reward for '" + orchestrators[i].uri + "'")
            r = requests.get(orchestrators[i].uri + '/reward')
            log(r)
            if r.status_code == 200:
                log('Call to reward success.')
                orchestrators[i].hasReward = True
            else:
                log('Call to reward fail. Error: ' + str(r))
                orchestrators[i].hasReward = False
                delay = sleepTimeActive
        else:
            orchestrators[i].hasReward = True
            log("Orchestrator '" + orchestrators[i].uri + "' has already called reward in round " + str(latestRound))
    # Sleep a long or short time based on whether all Orchestrators have been handled 
    while delay > 0:
        log("Next check in " + str(delay) + " seconds...")
        delay = delay - 30
        time.sleep(30)
