#!/bin/bash

# Enter here a token and an owner id
TOKEN=""
OWNER=""

if [[ $TOKEN == "" ]] || [[ $OWNER == "" ]]; then
	echo "[ERR] Enter a USER DATA!!!"
	echo "Use and edit the lines: vim docker-run.sh"
	exit
fi

echo "[INFO] Downloading the necessary files and install..."
apt-get update -y
apt-get instsall -y python3 git python3-pip
cd /usr/games/
git clone https://github.com/fecton/assbot.git
cd assbot
pip3 install -r requirements.txt
echo "TOKEN=$TOKEN" >  .env
echo "OWNER=$OWNER" >> .env
