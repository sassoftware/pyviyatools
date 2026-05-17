#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getposixidentity.py
# February 2021
#
# Returns the posix attributes of a user similar to the Linux "id" command
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

import argparse

from sharedfunctions import printresult, callrestapi

# setup command-line arguements
parser = argparse.ArgumentParser(description="Display POSIX attributes for User or ALL users(default)")

parser.add_argument("-u","--user", help="Enter the user id or leave blank for all users.",default='all')
parser.add_argument("-q","--query", help="Enter a valid rest query of usernames.",default="not(blank(id))")
parser.add_argument("-c","--custom", action='store_true', help="Display local (custom) users as well")
parser.add_argument("-l","--limit", type=int,help="Specify the number of records to pull. Default is 1000.",default=1000)
parser.add_argument("-d","--debug", action='store_true', help="Debug")
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='json')

args = parser.parse_args()
user=args.user
query=args.query
local=args.custom
limit=args.limit
debug=args.debug
output_style=args.output

if user=='all':

     reqtype='get'

     if local:
        # get all users satisfying provided filter even the local ones
        reqval='/identities/users/?filter='+query+'&limit='+str(limit)
     else:
        # get all non-local users satisfying provided filter
        reqval='/identities/users/?filter=and(ne(providerId,"local"),'+query+')&limit='+str(limit)

     if debug: print(reqval)
     
     userslist_result_json=callrestapi(reqval,reqtype)

     users = userslist_result_json['items']

     for user in users:
         userid=user['id']
         reqval='/identities/users/'+userid+'/identifier'

         if debug: print(reqval)

         posixinfo_result_json=callrestapi(reqval,reqtype,stoponerror=0,noprint=1)
     
         # if a dictionary is returned posix attributes are available
         if isinstance(posixinfo_result_json,dict):

            # get uid
            user["uid"]=posixinfo_result_json["uid"]
            # get gid
            user["gid"]=posixinfo_result_json["gid"]

            if "secondaryGids" in posixinfo_result_json:
               user["secgid"]=posixinfo_result_json["secondaryGids"]
            else:
               user["secgid"]=[""]
         else:
            user["uid"]=""
            user["gid"]=""
            user["secgid"]=[""]


     cols=['id','uid','gid','secgid','name','state','providerId']
     printresult(userslist_result_json,output_style,cols)

else:

    # set the request type
    reqtype='get'
    # set the endpoint to call
    reqval='/identities/users/'+user+"/identifier"

    if debug: print(reqval)

    #make the rest call using the callrestapi function. You can have one or many calls
    user_info_result_json=callrestapi(reqval,reqtype)

    # seems to be returning non standard results add id to make it standard
    # print result expects there to an id so use uid

    user_info_result_json['id']=user_info_result_json["uid"]
    user_info_result_json['username']=user

    printresult(user_info_result_json,output_style)
