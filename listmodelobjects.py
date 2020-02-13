#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# listmodelobjects.py February 2020
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

# setup command-line arguments. In this block, which is common to all the tools, you setup what parameters
# are passed to the tool.
# the --output parameter is a common one which supports the three styles of output; json, simple or csv

parser = argparse.ArgumentParser()

parser.add_argument("-n","--name", help="Name contains",default=None)
parser.add_argument("-c","--type", help="Content Type (model, project or repository)",default='model')
parser.add_argument("-d","--days", help="List files older than this number of days",default='-1')
parser.add_argument("-m","--modifiedby", help="Last modified id equals",default=None)
parser.add_argument("-s","--sortby", help="Sort the output descending by this field",default='name')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple'],default='csv')

args = parser.parse_args()
output_style=args.output
daysolder=args.days
modby=args.modifiedby
sortby=args.sortby
nameval=args.name
typeval=args.type

# calculate time period for models
now=dt.today()-td(days=int(daysolder))
subset_date=now.strftime("%Y-%m-%dT%H:%M:%S")
datefilter="le(creationTimeStamp,"+subset_date+")"

# create a list for filter conditions
filtercond=[]

# there is always a number of days (default is to show all)
filtercond.append(datefilter)

# construct filter
delimiter = ','
if nameval!=None: filtercond.append('contains(name,"'+nameval+'")')
if modby!=None: filtercond.append("eq(modifiedBy,"+modby+")")
completefilter = 'and('+delimiter.join(filtercond)+')'

# prepare the request according to content type
reqtype='get'
if typeval=='model': reqval="/modelRepository/models?"+completefilter+"&sortBy="+sortby
if typeval=='project': reqval="/modelRepository/projects?"+completefilter+"&sortBy="+sortby
if typeval=='repository': reqval="/modelRepository/repositories?"+completefilter+"&sortBy="+sortby

# Make call, and process & print results
files_result_json=callrestapi(reqval,reqtype)
print("-------------------------------------")
print("Listing "+typeval+" objects")
print("-------------------------------------")
printresult(files_result_json,output_style)


   
 
    
    

   