#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#
#  allows you to read files from the file service and save them to a directory on the file system.
#  Optionally, the tool will also delete files from the file service in order to free up space.
#  For example, 
#
#
#
# Copyright © 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#  express or implied. See the License for the specific language governing permissions and limitations under the License.
#

import argparse , datetime, os, time, json, sys
from sharedfunctions import callrestapi,printresult,getfolderid,getidsanduris
from datetime import datetime as dt, timedelta as td

# get python version
version=int(str(sys.version_info[0]))

# in python3 unicode is now string
if version >= 3: unicode = str

# setup command-line arguements. In this block which is common to all the tools you setup what parameters
# are passed to the tool
# the --output parameter is a common one which supports the styles of output json, simplejson, simple or csv

parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description="Manage, inclding deletting notifications.")

parser.add_argument("-d","--days", help="List files older than this number of days",default='-1')
parser.add_argument("-m","--modifiedby", help="Last modified id equals",default=None)
parser.add_argument("-x","--delete", help="Delete Files from Viya",action='store_true')
parser.add_argument("--debug", action='store_true', help="Debug")

args = parser.parse_args()
daysolder=args.days
modby=args.modifiedby
debug=args.debug
dodelete=args.delete


# prompt if delete is requested
if dodelete:

   if version  > 2:
      areyousure=input("The files will be archived. Do you also want to delete the files? (Y)")
   else:
      areyousure=raw_input("The files will be archived. Do you also want to delete the files? (Y))") 

   if areyousure !='Y': dodelete=False


# calculate time period for files
now=dt.today()-td(days=int(daysolder))
subset_date=now.strftime("%Y-%m-%dT%H:%M:%S")
datefilter="le(creationTimeStamp,"+subset_date+")"

# create a list for filter conditions
filtercond=[]

# there is always a number of days, the default is zero
filtercond.append(datefilter)

if modby!=None: filtercond.append("eq(modifiedBy,"+modby+")")

# set the request type
reqtype='get'
delimiter = ','

completefilter = 'and('+delimiter.join(filtercond)+')'
reqval="/notifications/notifications?filter="+completefilter+"&limit=10000"
        

content=callrestapi(reqval,reqtype)


