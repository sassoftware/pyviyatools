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
parser = argparse.ArgumentParser(description="Display POSIX attributes for User")

parser.add_argument("-u","--user", help="Enter the user id",required='True')
parser.add_argument("-d","--debug", action='store_true', help="Debug")
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='json')

args = parser.parse_args()
user=args.user
debug=args.debug
output_style=args.output

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