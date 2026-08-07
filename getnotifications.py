#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getnotifications.py
#
#
# List all notifications in SAS Environment Manager, or show details about
# a single notification when an ID is supplied.
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
#  Use: python3 getnotifications.py --dryrun
#  Use: python3 getnotifications.py
#  Use: python3 getnotifications.py -i 48c02a16-e348-4627-8000-70253c47cfee
#  Use the ID returned by a list to show details for a single notification.



import argparse
import subprocess

from sharedfunctions import getclicommand

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

parser = argparse.ArgumentParser(description="List all notifications, or show details for a single notification.")
parser.add_argument("-i","--id", help="Notification ID. If omitted, all notifications are listed. If supplied, details for that notification are shown.")
parser.add_argument("--dryrun", help="Print the command without sending it.", action='store_true')

args = parser.parse_args()
id=args.id
dryrun=args.dryrun

# no id supplied - list all notifications
# id supplied - show details for that notification
if id:
    command=clicommand+' notifications show --id '+id
else:
    command=clicommand+' notifications list'

if dryrun:
    print("\n********** DRY-RUN MODE ********** \n")
    print("Command preview: "+command)
else:
    print("Running command: "+command)
    subprocess.call(command, shell=True)