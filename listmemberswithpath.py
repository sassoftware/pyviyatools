#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# listmemberswithpath.py
# January 2019
#
# Usage:
# listmemberswithpath.py -u objectURI [-r] [-d]
#
# Examples:
#
# 1. Return list of members of a folder identified by objectURI
#        ./listmemberswithpath.py -u /folders/folders/060c0ea4-07ee-43ea-aa79-a1696b7f8f52
#
# 2. Return list of all members of a folder identified by objectURI, recursively searching subfolders
#        ./listmemberswithpath.py -u /folders/folders/060c0ea4-07ee-43ea-aa79-a1696b7f8f52 -r
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
import argparse
import sys
from sharedfunctions import callrestapi,getpath

# Define exception handler so that we only output trace info from errors when in debug mode
def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print "%s: %s" % (exception_type.__name__, exception)

sys.excepthook = exception_handler

parser = argparse.ArgumentParser()
parser.add_argument("-u","--objecturi", help="Object URI of folder or other object that can be contained within a folder.", required=True)
parser.add_argument("-r","--recursive", action='store_true', help="Debug")
parser.add_argument("-d","--debug", action='store_true', help="Debug")
args = parser.parse_args()
objecturi=args.objecturi
recursive=args.recursive
debug=args.debug

#We expect a URI, but if the objectURI does not begin with a /, assume it is a folder id. This may be nonsense, but it's much more likely to just fail than return data for the wrong object.
if not objecturi.startswith("/"):
    objecturi='/folders/folders/'+objecturi

#Exit if the objecURI is not a folder
if not objecturi.startswith("/folders/folders/"):
    raise Exception('ObjectURI must be a folder, and should begin with /folders/folders/.')

#First, use the /folders/{folderId}/members endpoint to ask for a list of objects which are in the folder passed in by objecturi
#See Folders API documentation in swagger at http://swagger.na.sas.com/apis/folders/v1/apidoc.html#op:getAncestors
endpoint=objecturi+'/members'
if recursive:
    endpoint=endpoint+'?recursive=true'
method='get'

#make the rest call
members_result_json=callrestapi(endpoint,method)

if debug:
    print(members_result_json)
    #print('members_result_json is a '+type(members_result_json).__name__+' object') #members_result_json is a dict object

members = members_result_json['items']

for member in members:
    outstr=''
    path=getpath(member['uri'])
    outstr=outstr+path+','+member['id']+','+member['name']+','+member['type']
    if 'description' in member:
        outstr=outstr+','+member['description']
    else:
        outstr=outstr+','
    outstr=outstr+','+member['uri']
    print outstr
