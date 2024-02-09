#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# listcaslibs.py
# January 2019
# April 2023 added -n for name filtering 
#
# Usage:
# listcaslibs.py [-n <name>] [--noheader] [-d]
#
# Examples:
#
# 1. Return list of all CAS libraries on all servers
#        ./listcaslibs.py
#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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

debug=False

# Import Python modules
import argparse, sys, requests
from datetime import datetime
from sharedfunctions import callrestapi

excludeItemLinks = True

parser = argparse.ArgumentParser()

parser.add_argument("-s","--server", help="CAS Server", default='cas-shared-default')
parser.add_argument("-d","--debug", action='store_true', help="Debug")
args = parser.parse_args()
debug=args.debug
serverName = args.server

endpoint='/casManagement/servers'
method='get'

# Create a new session (need to do this so we can assume superuser role next)
endpoint="/casManagement/servers/"+serverName+"/sessions"
method='post'
r = callrestapi(endpoint,method)
mySessionId = r['id']

print('mySessionId = '+ mySessionId)

# Assume superuser role (this is not documented on the public website)
#url = f"{host}/casAccessManagement/servers/{serverName}/admUser/assumeRole/superUser?sessionId={mySessionId}"

#endpoint="/casManagement/servers/"+serverName+"/admUser/assumeRole/superUser?sessionId="+mySessionId
#print(endpoint)
#method='post'
#r = callrestapi(endpoint,method)

# Get a list of sessions. Exclude sessions with owner=sas.*
# limit = Maximum number of items to return in this page of results

limit = 1000
endpoint = "/casManagement/servers/"+serverName+"/sessions?excludeItemLinks=True&limit=1000&sessionId="+mySessionId+"&filter=not(startsWith(owner,'sas.'))"
method='get'
r = callrestapi(endpoint,method)
#print(json.dumps(r.json(), indent=2))

sessions = r['items']
for session in sessions:

    sessionId = str(session['id'])
    method='get'
    endpoint="/casManagement/servers/"+serverName+"/sessions/"+sessionId+"?sessionId="+mySessionId
    rsess = callrestapi(endpoint,method)

    name = rsess['name']
    sessionId = rsess['id']
    state = rsess['state']
    owner = rsess['owner']

    # Parse the CAS session reference from the name
    sessionReference = name[0:len(name)-25]
    # Parse the CAS session start date-time from the name
    sessionStart = name[len(name)-24:len(name)]
    # Day of month needs to be padded with a leading zero to use strptime %d parsing 
    if sessionStart[8:9] == ' ':
        sessionStart=sessionStart[0:8]+'0'+sessionStart[9:len(sessionStart)]
    # Parse to date-time
    sessionStartDttm = datetime.strptime(sessionStart, '%a %b %d %H:%M:%S %Y')

    # Get CAS session state
    method='get' 
    endpoint="/casManagement/servers/"+serverName+"/sessions/"+sessionId+"/state?sessionId="+mySessionId
    runningstate = callrestapi(endpoint,method)
    
    if debug:
        print(f'\nsessionReference = {sessionReference}')
        print(f'sessionStartDttm = {sessionStartDttm}')
        print(f'name={name}, sessionId={sessionId}, state={state}, owner={owner} runningstate={runningstate}')

    # Terminate sessions where state = disconnected and runing state = running
    if state == 'Disconnected' and runningstate == 'running':
        print(f'Terminating CAS session: {sessionId}')
        method='delete' 
        endpoint="/casManagement/servers/"+serverName+"/sessions/"+sessionId+"/?sessionId="+mySessionId
        result=callrestapi(endpoint,method)
        print(result)

# End the CAS session we started for management
# url = f"{host}/casManagement/servers/{serverName}/sessions/{mySessionId}"
# r = requests.request('DELETE', url, headers=headers, verify=False)
# print(r.text)