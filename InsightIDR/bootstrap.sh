#!/bin/bash
sudo apt-get update -y && apt-get upgrade -y
cd /opt

# Install geckdriver
wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz -O /tmp/geckodriver.tar.gz && sudo tar -C /opt -xzf /tmp/geckodriver.tar.gz && sudo chmod 755 /opt/geckodriver && sudo ln -fs /opt/geckodriver /usr/bin/geckodriver && sudo ln -fs /opt/geckodriver /usr/local/bin/geckodriver;

# Install collector tar
wget https://github.com/benelser/AWSBOTOQuickStart/blob/master/InsightIDR/InsightSetup-Linux64.tar.gz?raw=true -O ./InsightSetup-Linux64.tar.gz && sudo tar -C /opt -xf ./InsightSetup-Linux64.tar.gz && sudo chmod 755 /opt/InsightSetup-Linux64.sh && sudo /opt/InsightSetup-Linux64.sh -q;

# check for IPIMS_Client.py dependencies
if dpkg --list firefox; then echo "Firefox installed"; else sudo apt-get install firefox xvfb -y; fi
if dpkg --list python3-pip; then echo "python3-pip installed"; else sudo apt-get install python3-pip -y; fi

# if this is a collector create key file
AGENT_KEY_FILE=/opt/rapid7/collector/agent-key/Agent_Key.html
if test -f "$AGENT_KEY_FILE"; then 
    sudo cat "$AGENT_KEY_FILE" | cut -d " " -f 4 | cut -d ">" -f2 | cut -d "<" -f1 > /opt/rapid7/collector/agent-key/Agent_Key.txt;
fi