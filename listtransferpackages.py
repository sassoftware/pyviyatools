#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# lisfiles.py January 2018
#
# provides an easy interface to query what files are currently stored in the infrastructure data server.
# You can list all files sorted by modified date or size of file, and query based on date modified,
# user who last modified the file,  parentUri or filename. The output provides the size of each file, 
# so that you can check the space being used to store files. 
# Use this tool to view files managed by the files service and stored in the infrastructure data server.
#
# For example, if I want to see all potential log files, 
# created by the /jobexecution service that are older than 6 days old.
#
# ./listfiles.py -n log -p /jobExecution -d 6 -o csv
#
# 27JAN2019 Comments added
# 12SEP2019 Added the ability to specifiy a folder as an alternative to a URI
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

import argparse , datetime, sys
from sharedfunctions import callrestapi,printresult,getfolderid,getidsanduris
from datetime import datetime as dt, timedelta as td

# setup command-line arguements. In this block which is common to all the tools you setup what parameters
# are passed to the tool
# the --output parameter is a common one which supports the three styles of output json, simple or csv

parser = argparse.ArgumentParser()

parser = argparse.ArgumentParser(description="Query and list files stored in the infrastructure data server.")
parser.add_argument("-n","--name", help="Name contains",default=None)
parser.add_argument("-d","--days", help="List files older than this number of days",default='-1')
parser.add_argument("-do","--olderoryounger", help="For the date subsetting specify older or younger",choices=['older','younger'],default='older')
parser.add_argument("-m","--modifiedby", help="Last modified id equals",default=None)
parser.add_argument("-s","--sortby", help="Sort the output descending by this field",default='modifiedTimeStamp')
parser.add_argument("-so","--sortorder", help="Sort order",choices=['ascending','descending'],default='descending')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='json')
parser.add_argument("--debug", action='store_true', help="Debug")

args = parser.parse_args()
output_style=args.output
days=args.days
modby=args.modifiedby
sortby=args.sortby
nameval=args.name
debug=args.debug
sortorder=args.sortorder
olderoryounger=args.olderoryounger

packagefile_result_json=None

# calculate time period for files
# calculate time period for files
now=dt.today()-td(days=int(days))
subset_date=now.strftime("%Y-%m-%dT%H:%M:%S")

if olderoryounger=='older':
  datefilter="le(creationTimeStamp,"+subset_date+")"
else: datefilter="ge(creationTimeStamp,"+subset_date+")"

# create a list for filter conditions
filtercond=[]

# there is always a number of days, the default is zero
filtercond.append(datefilter)

if nameval!=None: filtercond.append('contains($primary,name,"'+nameval+'")')
if modby!=None: filtercond.append("eq(modifiedBy,"+modby+")")

# set the request type
reqtype='get'
delimiter = ','
completefilter = 'and('+delimiter.join(filtercond)+')'

reqval="/transfer/packages?filter="+completefilter+"&sortBy="+sortby+":"+sortorder+"&limit=10000"

if debug: print(reqval)   

packagefile_result_json=callrestapi(reqval,reqtype)

cols=['id','name','transferObjectCount','createdBy','creationTimeStamp','modifiedBy','modifiedTimeStamp']
# print result

if packagefile_result_json == None:
   print("No files returned by query.")
else:
   printresult(packagefile_result_json,output_style,cols)
 
   
 
    
    

   
