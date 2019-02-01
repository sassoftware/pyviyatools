#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# archivefiles.py January 2018
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

import argparse , datetime, os, time, json, sys
from sharedfunctions import callrestapi,printresult
from datetime import datetime as dt, timedelta as td

# get python version
version=int(str(sys.version_info[0]))

# setup command-line arguements. In this block which is common to all the tools you setup what parameters
# are passed to the tool
# the --output parameter is a common one which supports the three styles of output json, simple or csv

parser = argparse.ArgumentParser()

parser.add_argument("-n","--name", help="Name contains",default=None)
parser.add_argument("-c","--type", help="Content Type in.",default=None)
parser.add_argument("-p","--parent", help="ParentURI starts with.",default=None)
parser.add_argument("-d","--days", help="List files older than this number of days",default='0')
parser.add_argument("-m","--modifiedby", help="Last modified id equals",default=None)
parser.add_argument("-fp","--path", help="Path of directory to store files",default='/tmp')
parser.add_argument("-x","--delete", help="Delete Files from Viya",action='store_true')

args = parser.parse_args()
daysolder=args.days
modby=args.modifiedby
nameval=args.name
puri=args.parent
path=args.path
dodelete=args.delete


if dodelete:

   if version  > 2:
      areyousure=input("The files will be archived. Do you also want to delete the files? (Y)")
   else:
      areyousure=raw_input("The files will be archived. Do you also want to delete the files? (Y))") 

   if areyousure !='Y': dodelete=False

# content filter
#contentfilter='in(contentType,"application/vnd.sas.collection","text/plain","application/vnd.sas.collection+json","text/plain;charset=UTF-8","application/octet-stream")'

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
reqval="/files/files?filter="+completefilter+"&limit=10000"

#print(reqval)

#create a directory with a name of the timestamp only if running in execmodeute mode
newdirname="D"+dt.today().strftime("%Y%m%dT%H%MS")

archivepath=os.path.join(path,newdirname )
if os.path.isdir(archivepath)==False: os.makedirs(archivepath)


#make the rest call using the callrestapi function. You can have one or many calls
files_result_json=callrestapi(reqval,reqtype)

files = files_result_json['items']
if len(files):
   if os.path.isdir(archivepath)==False: os.makedirs(archivepath)

for file in files:

   fileid=file['id']
   
   filename=file['name'] 
   archivefile=os.path.join(archivepath,filename )
       
   reqtype='get'	   
   reqval="/files/files/"+fileid+"/content"
   
   content=callrestapi(reqval,reqtype)
         
   if type(content) is dict:
	  
      with open(archivefile, 'w') as fp:
         json.dump(content,fp,indent=4)
	
      fp.close()
    	      
   elif type(content) is unicode:
      
       with open(archivefile, 'w') as fp:
          fp.write(content.encode('utf8'))          
	
       fp.close()
   else: print('NOTE: ',filename,' content type not supported')
   
   if dodelete:

      reqtype='delete'
      reqval="/files/files/"+fileid
	           
      callrestapi(reqval,reqtype)
      

if len(files):	  
   print('NOTE: files archived to the directory '+archivepath)
   if dodelete: print('NOTE: files deleted from Viya.')
else:
   print('NOTE: No files found')