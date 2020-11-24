#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# updatepreferences.py
# October 2018
#
# Update user preferences for a single user of a group of users
#
# Change History
#
# 30OCT2018 first version
#
# Copyright © 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


####################################################################
#### COMMAND LINE EXAMPLE                                       ####
####################################################################
#### ./updatepreferences.py -                                   ####
####                        -t user                             ####
####                        -tn myUser                          ####
####                        -pi VA.geo.drivedistance.unit       ####
####                        -pv kilometers                      ####
####################################################################
#### POSSIBLE VALUES                                            ####
####################################################################
#### sas.welcome.suppress = true/false                          ####
#### sas.drive.show.pinned = true/false                         ####
#### VA.geo.drivedistance.unit = kilometers/miles               ####
#### OpenUI.Theme.Default = sas_corporate/sas_inspire/sas_hcb   ####
####################################################################

import argparse
from sharedfunctions import callrestapi

parser = argparse.ArgumentParser(description="Update user preferences for a user or a group of users")
parser.add_argument("-t", "--target", help="Type the target of the update: user or group", required=True, choices=['user', 'group','all'])
parser.add_argument("-tn", "--targetname", help="ID of the user or group to which the update applies.", required=True)
parser.add_argument("-pi", "--preferenceid", help="ID of the preference to be updated", required=True)
parser.add_argument("-pv", "--preferencevalue", help="Value to be set for the preference", required=True)

args = parser.parse_args()
target = args.target
targetName = args.targetname
preferenceID = args.preferenceid
preferenceValue = args.preferencevalue

json= {"application": "SAS Visual Analytics", "version": 1,"id": preferenceID ,"value": preferenceValue}


# apply for all users
if target=='all' :

    reqtype='get'
    reqval='/identities/users/'
    resultdata=callrestapi(reqval,reqtype)

    reqtype="put"

    if 'items' in resultdata:

        returned_items=len(resultdata['items'])
        for i in range(0,returned_items):

           id=resultdata['items'][i]['id']
           type=resultdata['items'][i]['type']

           if type=="user":
               reqval="/preferences/preferences/"+ id +"/" + preferenceID
               result=callrestapi(reqval, reqtype,data=json,stoponerror=0)
               print("Updating Preference "+reqval+" = "+preferenceValue)


# Function to update preference of a specific user
if target == 'user' :

    userID=targetName

    reqtype='get'
    reqval="/identities/users/"+userID

    userexist=callrestapi(reqval,reqtype)

    reqtype="put"
    reqval="/preferences/preferences/"+ userID +"/" + preferenceID
    result=callrestapi(reqval,reqtype,data=json)
    print("Updating Preference "+reqval+" = "+preferenceValue)


else: # Execute actual code to update the preference for a user or a group

    reqtype='get'
    reqval='/identities/groups/'+ targetName +'/members?limit=1000&depth=-1'
    resultdata=callrestapi(reqval,reqtype,contentType="application/vnd.sas.identity.group.member.flat")

    reqtype="put"

    if 'items' in resultdata:

        returned_items=len(resultdata['items'])
        for i in range(0,returned_items):

           id=resultdata['items'][i]['id']
           type=resultdata['items'][i]['type']

           if type=="user":
               reqval="/preferences/preferences/"+ id +"/" + preferenceID
               result=callrestapi(reqval, reqtype,data=json,stoponerror=0)
               print("Updating Preference "+reqval+" = "+preferenceValue)
           else: print("Cannot set preferences for a group "+id )