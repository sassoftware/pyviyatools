#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getpathsplus.py
# October 2022 - Initial commit
# Conceptually based on getpathsplus.py, getpathsplus.ph enables mass objectURI --> path
# conversion as well as options to return additional details.
#
# Change History
# DDMMMYYY - 
#
# Usage:
# getpathsplus.py [-o] [-m "all", "name", "createdby"] -u objectURI [-d]
#
# Examples:
#
# 1. Return path of folder identified by objectURI
#        ./getpathsplus.py -u /folders/folders/060c0ea4-07ee-43ea-aa79-a1696b7f8f52
#
# 2. Return path of report identified by objectURI
#        ./getpathsplus.py -u /reports/reports/43de1f98-d7ef-4490-bb46-cc177f995052
#
# 3. Return path of report and folder from their objectURIs
#	 ./getpathsplus.py -u /folders/folders/060c0ea4-07ee-43ea-aa79-a1696b7f8f52 /reports/reports/43de1f98-d7ef-4490-bb46-cc177f995052
#
# 4. Return path of of folder identified by objectURI including the folder's name
#        ./getpathsplus.py -m name -u /folders/folders/060c0ea4-07ee-43ea-aa79-a1696b7f8f52
#
# 5. Return path of of folder identified by objectURI including the createdBy field
#        ./getpathsplus.py -m createdby -u /folders/folders/060c0ea4-07ee-43ea-aa79-a1696b7f8f52
#
# 6. Return path of of folder identified by objectURI including the folder's name and the createdBy field AND prefixing the output with the Object's URI
#        ./getpathsplus.py -o -m all -u /folders/folders/060c0ea4-07ee-43ea-aa79-a1696b7f8f52
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


# Import Python modules
import argparse
import sys
import os
from sharedfunctions import getpath, getapplicationproperties, getobjectdetails

# get python version
version=int(str(sys.version_info[0]))

# get cli location from properties
propertylist=getapplicationproperties()

clidir=propertylist["sascli.location"]
cliexe=propertylist["sascli.executable"]

clicommand=os.path.join(clidir,cliexe)

debug=False

# Define exception handler so that we only output trace info from errors when in debug mode
def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print (exception_type.__name__, exception)

sys.excepthook = exception_handler

parser = argparse.ArgumentParser()
parser.add_argument("-m","--more", action='store', const='all', nargs='?', choices=['all', 'name', 'createdby'], help="Returns additional details for each Object (default: all)")
parser.add_argument("-o", action='store_const', const="yes", help="Prepends ObjectURIs to each row output")
parser.add_argument("-u","--objecturi", action='store', dest='urilist', type=str, nargs='*', default=['objecturi1', 'objecturi2', 'objecturi3'], help="Object URI of folder or other object contained within a folder. Lists should be used WITHOUT quotes and delimited with a space. E.g. getpathsplus.py -u /files/files/1234 /files/files/abcd ", required=True)
parser.add_argument("-d","--debug", action='store_true', help="Debug")
args = parser.parse_args()
urilist=args.urilist
more=args.more
oid=args.o
debug=args.debug

# checks for user input of at least ONE objecturi
if len(urilist) == 0:
   print("ERROR: At least one ObjectURI input is required.")
   exit()
else:
   print("Running...".format(args.urilist))

# checks for use of 'more' flag
if more is None:

    # loop to retrieve all path values
    i = 0
    while i < len(urilist):
        path=getpath(urilist[i])
	# checks for 'o' flag and includes objecturis in output if it's set
        # output from: -o -u <objecturi>
	if oid =="yes":
           print(urilist[i]+","+path)
           i=i+1
        # output from: -u <objecturi>
	else:
	   print(path)
	   i=i+1
else:
    # loop to retrieve all objecturi values entered + object name
    i = 0
    while i < len(urilist):
        path=getpath(urilist[i])
        name=getobjectdetails(urilist[i])
        creator=getobjectdetails(urilist[i])
        # checks for 'o' flag and includes objecturis in output if it's set
	if oid == "yes":
	   # output from: -o -m name -u <objecturi>
    	   if more == "name":
	      print(urilist[i]+","+path+name[0])
	      i=i+1
           # output from: -o -m createdby -u <objecturi>
	   elif more == "createdby":
	      print(urilist[i]+","+path+","+creator[1])
	      i=i+1
           # output from: -o -m all|<blank> -u <objecturi>
	   else:
	      print(urilist[i]+","+path+name[0]+","+creator[1])
	      i=i+1
	else:
           # output from: -m name -u <objecturi>
           if more == "name":
              print(path+name[0])
              i=i+1
           # output from: -m createdby -u <objecturi>
           elif more == "createdby":
              print(path+","+creator[1])
              i=i+1
           # output from: -m all|<blank> -u <objecturi>
           else:
              print(path+name[0]+","+creator[1])
              i=i+1
