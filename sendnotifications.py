#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# sendnotifications.py
# 
#
# Send a notification message that appears in the Notifications area for all SAS Viya users.
# 
# 
# Change History
# July 2026
#
#
# Copyright © 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License);
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  Dev Notes:
#  You might need to install the pluging SAS notification - directory plugins install --repo SAS notifications
#  Use: python3 sendnotifications.py -m "Your message here" -s "Your subject here" -l info --dryrun
#  Use : python3 sendnotifications.py -m "Your message here" -s "Your subject here" -l info
#  See complete list of the notification sent: sas-viya notifications list



import argparse
import subprocess

from sharedfunctions import getclicommand

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

parser = argparse.ArgumentParser(description="Send a notification message to all SAS Viya platform users.")
parser.add_argument("-m","--message", help="Notification text (max 100 characters).", required='True')
parser.add_argument("-s","--subject", help="Notification subject.", required='True')
parser.add_argument("-l","--level", help="Notification severity.", choices=['alert','warn','info'], required='True')
parser.add_argument("--dryrun", help="Print the command without sending it.", action='store_true')

args = parser.parse_args()
message=args.message
subject=args.subject
level=args.level
dryrun=args.dryrun

command=clicommand+' notifications send --message "'+message+'" --subject "'+subject+'" --level '+level

if dryrun:
    print("\n********** DRY-RUN MODE ********** \n")
    print("Command preview: "+command)
else:
    print("Running command: "+command)
    subprocess.call(command, shell=True)