#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# readnotifications.py
#
#
# Mark a notification as read in SAS Environment Manager.
#
#
# Change History
# August 2026
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
#  You might need to install the plugin SAS notifications - sas-viya plugins install --repo SAS notifications
#  Use: python3 readnotifications.py -i 48c02a16-e348-4627-8000-70253c47cfee --dryrun
#  Use: python3 readnotifications.py -i 48c02a16-e348-4627-8000-70253c47cfee
#  Use getnotifications.py to determine the ID of a notification.



import argparse
import subprocess

from sharedfunctions import getclicommand

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

parser = argparse.ArgumentParser(description="Mark a notification as read.")
parser.add_argument("-i","--id", help="Notification ID to mark as read.", required='True')
parser.add_argument("--dryrun", help="Print the command without sending it.", action='store_true')

args = parser.parse_args()
id=args.id
dryrun=args.dryrun

command=clicommand+' notifications mark-as-read --id '+id

if dryrun:
    print("\n********** DRY-RUN MODE ********** \n")
    print("Command preview: "+command)
else:
    print("Running command: "+command)
    subprocess.call(command, shell=True)