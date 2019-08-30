#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# lisfiles.py January 2018
#
#
# Change History
#
# 27JAN2019 Comments added
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

import argparse , datetime
from sharedfunctions import callrestapi,printresult
from datetime import datetime as dt, timedelta as td

# setup command-line arguements. In this block which is common to all the tools you setup what parameters
# are passed to the tool
# the --output parameter is a common one which supports the three styles of output json, simple or csv

parser = argparse.ArgumentParser()

parser.add_argument("-n","--name", help="Name contains",default=None)
parser.add_argument("-c","--type", help="Content Type in.",default=None)
parser.add_argument("-p","--parent", help="ParentURI starts with.",default=None)
parser.add_argument("-d","--days", help="List files older than this number of days",default='-1')
parser.add_argument("-m","--modifiedby", help="Last modified id equals",default=None)
parser.add_argument("-s","--sortby", help="Sort the output descending by this field",default='modifiedTimeStamp')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple'],default='json')

args = parser.parse_args()
output_style=args.output
daysolder=args.days
modby=args.modifiedby
sortby=args.sortby
nameval=args.name
puri=args.parent

# calculate time period for files
now=dt.today()-td(days=int(daysolder))
subset_date=now.strftime("%Y-%m-%dT%H:%M:%S")
datefilter="le(creationTimeStamp,"+subset_date+")"

# create a list for filter conditions
filtercond=[]

# there is always a number of days, the default is zero
filtercond.append(datefilter)

if nameval!=None: filtercond.append('contains($primary,name,"'+nameval+'")')
if modby!=None: filtercond.append("eq(modifiedBy,"+modby+")")
if puri!=None: filtercond.append("contains(parentUri,'"+puri+"')")

# add the start and end and comma delimit the filter
delimiter = ','
completefilter = 'and('+delimiter.join(filtercond)+')'
    
# set the request type
reqtype='get'
reqval="/files/files?filter="+completefilter+"&sortBy="+sortby+":descending&limit=10000"

#print(reqval)
 
#make the rest call using the callrestapi function
files_result_json=callrestapi(reqval,reqtype)

# print the following columns for csv output
cols=['id','name','contentType','documentType','createdBy','modifiedTimeStamp','size','parentUri']

# print result

printresult(files_result_json,output_style,cols)
 
