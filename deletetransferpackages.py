#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# deletetransferpackages.py October 2022
#
#
# For example, delete all packages with hr in the name created by sasadm
#
# ./deletetransferpackages.py -n "hr" -c sasadm -o csv
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

import argparse , datetime, sys, json

from requests import delete
from sharedfunctions import callrestapi,printresult,getfolderid,getidsanduris,createdatefilter
from datetime import datetime as dt, timedelta as td

# setup command-line arguements. In this block which is common to all the tools you setup what parameters
# are passed to the tool
# the --output parameter is a common one which supports the three styles of output json, simple or csv

parser = argparse.ArgumentParser()

parser = argparse.ArgumentParser(description="Query and list files stored in the infrastructure data server.")
parser.add_argument("-n","--name", help="Name contains",default=None)
parser.add_argument("-m","--modifiedby", help="Last modified id equals",default=None)
parser.add_argument("-c","--createdby", help="Created id equals",default=None)
parser.add_argument("-d","--days", help="List files older than this number of days",default='-1')
parser.add_argument("-do","--olderoryounger", help="For the date subsetting specify older or younger",choices=['older','younger'],default='older')
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')
parser.add_argument("--debug", action='store_true', help="Debug")

version=int(str(sys.version_info[0]))

args = parser.parse_args()
output_style='csv'
days=args.days
modby=args.modifiedby
createby=args.createdby
sortby='modifiedTimeStamp'
nameval=args.name
debug=args.debug
sortorder='descending'
olderoryounger=args.olderoryounger
quietmode=args.quiet

packagefile_result=None

# build the date filter
datefilter=createdatefilter(olderoryounger=olderoryounger,datevar='creationTimeStamp',days=days)

# create a list for filter conditions
filtercond=[]

# there is always a number of days, the default is zero
filtercond.append(datefilter)

if nameval!=None: filtercond.append('contains($primary,name,"'+nameval+'")')
if createby!=None: filtercond.append("eq(createdBy,'"+createby+"')")
if modby!=None: filtercond.append("eq(modifiedBy,'"+modby+"')")

# set the request type
reqtype='get'
delimiter = ','
completefilter = 'and('+delimiter.join(filtercond)+')'

reqval="/transfer/packages?filter="+completefilter+"&sortBy="+sortby+":"+sortorder+"&limit=10000"

if debug: print(reqval)   
packagefile_result=callrestapi(reqval,reqtype)

if packagefile_result["count"] ==0 :
   print("No package returned by query.")
else:

   cols=['id','name','transferObjectCount','createdBy','creationTimeStamp','modifiedBy','modifiedTimeStamp']
   
   # if quiet do not prompt
   if quietmode:
      areyousure="Y"
   else:

       printresult(packagefile_result,output_style,cols)

       if version  > 2:
          areyousure=input("Are you sure you want to delete the transfer packages listed above? (Y)")
       else:
          areyousure=raw_input("Are you sure you want to delete the transfer packages listed above? (Y)") 
    
   if areyousure.upper() == 'Y':

      #loop through items returned and delete packages      
      allitems=packagefile_result["items"]

      for item in allitems:

         id=item["id"]
         name=item["name"]

         print("Deleting package with id "+id+" and name "+name)
         reqtype='delete'
         reqval='/transfer/packages/'+id+'#withParts?deletejobs=true'
         if debug: print(reqval)
         rc=callrestapi(reqval,reqtype)
         if debug: print(rc)

      print("NOTE: packages matching criteria have been deleted.")
         

   
 
    
    

   
