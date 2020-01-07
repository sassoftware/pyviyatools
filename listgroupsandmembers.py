#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# listgroupsandmembers.py
# January 2019
#
# Usage:
# listgroupsandmembers.py [--noheader] [-e] [-d]
#
# Examples:
#
# 1. Return list of all groups and all their members
#        ./listgroupsandmembers.py
#
# 2. Return list of all groups and all their members, including email
#    address for members
#        ./listgroupsandmembers.py -e
#
# Copyright © 2020, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
import argparse
import sys
from sharedfunctions import callrestapi

# Define exception handler so that we only output trace info from errors when in debug mode
def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print "%s: %s" % (exception_type.__name__, exception)

sys.excepthook = exception_handler

parser = argparse.ArgumentParser()
parser.add_argument("--noheader", action='store_true', help="Do not print the header row")
parser.add_argument("-e","--email", action='store_true', help="Show email addresses for users")
parser.add_argument("-d","--debug", action='store_true', help="Debug")
args = parser.parse_args()
noheader=args.noheader
debug=args.debug
show_email=args.email

# Print header row unless noheader argument was specified
if not noheader:
    if show_email:
        print('groupid,groupname,grouptype,groupproviderid,memberid,membername,membertype,memberproviderid,email')
    else:
        print('groupid,groupname,grouptype,groupproviderid,memberid,membername,membertype,memberproviderid')

endpoint='/identities/groups'
method='get'

#make the rest call
groupslist_result_json=callrestapi(endpoint,method)

if debug:
    print(groupslist_result_json)
    print('groupslist_result_json is a '+type(groupslist_result_json).__name__+' object') #groupslist_result_json is a dict object

groups = groupslist_result_json['items']

for group in groups:
    groupid=group['id']
    groupname=group['name']
    grouptype=group['type']
    groupproviderid=group['providerId']

    # List the members of this group
    endpoint='/identities/groups/'+groupid+'/members'
    method='get'
    members_result_json=callrestapi(endpoint,method)
    if debug:
        print(members_result_json)
        print('members_result_json is a '+type(members_result_json).__name__+' object') #members_result_json is a dict object

    members=members_result_json['items']
    
    for member in members:
        memberid=member['id']
        membername=member['name']
        membertype=member['type']
        memberproviderid=member['providerId']
        user_email_string=''
        output=groupid+','+groupname+','+grouptype+','+groupproviderid+','+memberid+','+membername+','+membertype+','+memberproviderid
        
        if show_email:
            output=output+','
            
        if membertype=='user' and show_email:
                
            # List the members of this group
            endpoint='/identities/users/'+memberid
            method='get'
            user_details_json=callrestapi(endpoint,method)
            if debug:
                print(user_details_json)
                print('user_details_json is a '+type(user_details_json).__name__+' object') #user_details_json is a dict object

            if 'emailAddresses' in user_details_json:
                user_emails=user_details_json['emailAddresses']
                user_email_string=''
    
                for email in user_emails:
                    email_address=email['value']
                    if user_email_string!='':
                        user_email_string=user_email_string+';'
                    user_email_string=user_email_string+email_address
        
                output=output+user_email_string
            
        print(output)
