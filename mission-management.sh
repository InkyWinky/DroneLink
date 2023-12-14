#!/bin/bash
# This is a Bash Script that will automatically install all dependencies and run the Mission Management App
# Steps to use this Script
# 1. Give execution permissions on this file:
# 	chmod +x ./mission-management.sh
# 2. Run the script
# 	bash mission-management.sh
# 3. Add the script to run on startup
# 	a) crontab -e
#	b) Add a line to the file: 
#		@boot <path to script>/mission-management.sh -s

# Optional Arguments
while getopts "hs" option; do
   case $option in
      h) # display Help
        echo Mission Management Help
	echo -h : This help documentation
	echo -s : Starts the Mission Management app without setup
        exit;;
      s) # start the Mission Management App
	npm run serve & python2 ./Backend/DronelinkServer.py
	exit;;
   esac
done

# This code will run if no optional arguments are given
# Set up dependencies and runs the Mission Management App
#sudo apt install python2 curl
#curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
#sudo python2 get-pip.py
#pip2 install -r ./Backend/requirements.txt

sudo apt update
sudo apt-get install -y ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
NODE_MAJOR=18
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
sudo apt update
sudo apt-get install nodejs -y
npm install
npm install core-js@^3.34.0
npm run serve & python2 ./Backend/DronelinkServer.py
