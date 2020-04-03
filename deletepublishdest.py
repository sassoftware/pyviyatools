#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# deletepublishdest.py
# April 2020
#
# Delete a Viya publishing destination
#
# Change History
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

# Delete a publishing destination, after first validating that it exists

debug=False
folder_exists=False

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

parser = argparse.ArgumentParser(description="Delete a publishing destination")
parser.add_argument("-n","--name", help="Enter the name of the publishing destination to be deleted.",required=True)
parser.add_argument("-d","--debug", action='store_true', help="Debug")
args = parser.parse_args()
publish_name=args.name
debug=args.debug

# Does a publishing destination of the specified name actually exist?
# This call exits with a reasonably clear error message if the publishing destination does not exist,
# so I decided that no other error handling is required for the case where the folder does not exist.
reqval="/modelPublish/destinations/"+publish_name
reqtype="get"
test_exists_result_json=callrestapi(reqval,reqtype)
#print(test_exists_result_json)
#print('test_exists_result_json is a '+type(test_exists_result_json).__name__+' object') #test_exists_result_json is a dict object
if test_exists_result_json['name'] == publish_name:
   folder_exists=True
   if debug:
         print('Publishing destination '+publish_name+' found.')

# Build the rest call
# Aiming for something equivalent to ./callrestapi.py -e /modelPublish/destinations/newcasdest2 -m delete
reqval="/modelPublish/destinations/"+publish_name
reqtype="delete"

# Delete the publishing destination
callrestapi(reqval,reqtype)
print('Publishing destination '+publish_name+' deleted.')
