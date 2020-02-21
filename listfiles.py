#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# lisfiles.py January 2018
#
#
# Change History
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

parser.add_argument("-n","--name", help="Name contains",default=None)
parser.add_argument("-c","--type", help="Content Type in.",default=None)
parser.add_argument("-p","--parent", help="ParentURI starts with.",default=None)
parser.add_argument("-pf","--parentfolder", help="Parent Folder Name.",default=None)
parser.add_argument("-d","--days", help="List files older than this number of days",default='-1')
parser.add_argument("-m","--modifiedby", help="Last modified id equals",default=None)
parser.add_argument("-s","--sortby", help="Sort the output descending by this field",default='modifiedTimeStamp')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='json')

args = parser.parse_args()
output_style=args.output
daysolder=args.days
modby=args.modifiedby
sortby=args.sortby
nameval=args.name
puri=args.parent
pfolder=args.parentfolder

# you can subset by parenturi or parentfolder but not both
if puri !=None and pfolder !=None: 
   print("ERROR: cannot use both -p parent and -pf parentfolder at the same time.")
   print("ERROR: Use -pf for folder parents and -p for service parents.")
   sys.exit()

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

# set the request type
reqtype='get'
delimiter = ','

# process items not in folders
if puri!=None: 
   filtercond.append("contains(parentUri,'"+puri+"')")
   completefilter = 'and('+delimiter.join(filtercond)+')'
   reqval="/files/files?filter="+completefilter+"&sortBy="+sortby+":descending&limit=10000"
   files_result_json=callrestapi(reqval,reqtype)
     
# process items in folders
if pfolder!=None:

   folderid=getfolderid(pfolder)[0]     
   # add the start and end and comma delimit the filter
   completefilter = 'and('+delimiter.join(filtercond)+')'
   reqval="/folders/folders/"+folderid+"/members?filter="+completefilter+"&sortBy="+sortby+":descending&limit=10000"
   
   files_in_folder=callrestapi(reqval,reqtype)
      
   #now get the file objects using the ids returned
   iddict=getidsanduris(files_in_folder)
   
   # get the uris of the files   
   uris=iddict['uris']
   
   #get id, need to do this because only the uri of the folder is returned
   
   idlist=[]
   
   for item in uris:
       
       vallist=item.rsplit('/')
       idlist.append(vallist[-1])
    
   #inclause = ','.join(map(str, ids))
   inclause=(', '.join("'" + item + "'" for item in idlist))
   
   filtercond.append("in(id,"+inclause+")")
   completefilter = 'and('+delimiter.join(filtercond)+')'
   #print(completefilter)
   reqval="/files/files?filter="+completefilter+"&sortBy="+sortby+":descending&limit=10000"
   
   #make the rest call using the callrestapi function
   files_result_json=callrestapi(reqval,reqtype)

cols=['id','name','contentType','documentType','createdBy','modifiedTimeStamp','size','parentUri']
# print result
printresult(files_result_json,output_style,cols)
 
   
 
    
    

   