#!/bin/bash
sudo apt-get update -y && apt-get upgrade -y
cd /opt

# Install collector tar
wget https://github.com/benelser/AWSBOTOQuickStart/blob/master/InsightIDR/InsightSetup-Linux64.tar.gz?raw=true -O ./InsightSetup-Linux64.tar.gz && sudo tar -C /opt -xf ./InsightSetup-Linux64.tar.gz && sudo chmod 755 /opt/InsightSetup-Linux64.sh && sudo /opt/InsightSetup-Linux64.sh -q;

# create key file
AGENT_KEY_FILE=/opt/rapid7/collector/agent-key/Agent_Key.html
if test -f "$AGENT_KEY_FILE"; then 
    sudo cat "$AGENT_KEY_FILE" | cut -d " " -f 4 | cut -d ">" -f2 | cut -d "<" -f1 > /opt/rapid7/collector/agent-key/Agent_Key.txt;
fi