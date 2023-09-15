#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# listtransferpackages.py October 2022
#
#
# For example, list all packages with hr in the name created by sasadm
#
# ./listtransferpackages.py -n "hr" -c sasadm -o csv
#
# 12OCT2022 Initial Creation
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
from sharedfunctions import callrestapi,printresult,getfolderid,getidsanduris,createdatefilter
from datetime import datetime as dt, timedelta as td

parser = argparse.ArgumentParser()

parser = argparse.ArgumentParser(description="Query and list transfer packages stored in the infrastructure data server.")
parser.add_argument("-n","--name", help="Name contains",default=None)
parser.add_argument("-m","--modifiedby", help="Last modified id equals",default=None)
parser.add_argument("-c","--createdby", help="Created id equals",default=None)
parser.add_argument("-d","--days", help="List files older than this number of days",default='-1')
parser.add_argument("-do","--olderoryounger", help="For the date subsetting specify older or younger",choices=['older','younger'],default='older')
parser.add_argument("-s","--sortby", help="Sort the output descending by this field",default='modifiedTimeStamp')
parser.add_argument("-so","--sortorder", help="Sort order",choices=['ascending','descending'],default='descending')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='json')
parser.add_argument("--debug", action='store_true', help="Debug")

args = parser.parse_args()
output_style=args.output
days=args.days
modby=args.modifiedby
createby=args.createdby
sortby=args.sortby
nameval=args.name
debug=args.debug
sortorder=args.sortorder
olderoryounger=args.olderoryounger

packagefile_resultn=None

# build the date filter
datefilter=createdatefilter(olderoryounger=olderoryounger,datevar='creationTimeStamp',days=days)

# create a list for filter conditions
filtercond=[]

# there is always a number of days, the default is zero
filtercond.append(datefilter)

if nameval!=None: filtercond.append('contains($primary,name,"'+nameval+'")')
if modby!=None: filtercond.append("eq(modifiedBy,'"+modby+"')")
if createby!=None: filtercond.append("eq(createdBy,'"+createby+"')")

# set the request type
reqtype='get'
delimiter = ','
completefilter = 'and('+delimiter.join(filtercond)+')'

reqval="/transfer/packages?filter="+completefilter+"&sortBy="+sortby+":"+sortorder+"&limit=10000"

if debug: print(reqval)   

packagefile_result=callrestapi(reqval,reqtype)

cols=['id','name','transferObjectCount','createdBy','creationTimeStamp','modifiedBy','modifiedTimeStamp']

if packagefile_result["count"] ==0 :
   print("No packages returned by query.")
else:
   printresult(packagefile_result,output_style,cols)
 
   
 
    
    

   
