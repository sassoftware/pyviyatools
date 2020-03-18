#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# archivefiles.py January 2018
#
#  allows you to read files from the file service and save them to a directory on the file system.
#  Optionally, the tool will also delete files from the file service in order to free up space.
#  For example, 
#
#  ./archivefiles.py -n log -d 6 -p /job -fp /tmp 
# 
# Blog: https://blogs.sas.com/content/sgf/2019/04/04/where-are-my-viya-files/ 
#
# Change History
#
# 27JAN2019 Comments added
# 20SEP2019 Do not write out binary files
# 20SEP2019 Accept parent folder as a parameter
# 12FEB2020 Bug fix when not query is provided
# 20FEB2020 Fix for python 3 unicode is now str
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
parser = argparse.ArgumentParser(description="Archive and optionally delete files stored in the infrastructure data server.")

parser.add_argument("-n","--name", help="Name contains",default=None)
parser.add_argument("-c","--type", help="Content Type in.",default=None)
parser.add_argument("-p","--parent", help="ParentURI starts with.",default=None)
parser.add_argument("-pf","--parentfolder", help="Parent Folder Name.",default=None)
parser.add_argument("-d","--days", help="List files older than this number of days",default='-1')
parser.add_argument("-m","--modifiedby", help="Last modified id equals",default=None)
parser.add_argument("-fp","--path", help="Path of directory to store files",default='/tmp')
parser.add_argument("-x","--delete", help="Delete Files from Viya",action='store_true')
parser.add_argument("--debug", action='store_true', help="Debug")

args = parser.parse_args()
daysolder=args.days
modby=args.modifiedby
nameval=args.name
puri=args.parent
path=args.path
dodelete=args.delete
pfolder=args.parentfolder
debug=args.debug

# you can subset by parenturi or parentfolder but not both
if puri !=None and pfolder !=None: 
   print("ERROR: cannot use both -p parent and -pf parentfolder at the same time.")
   print("ERROR: Use -pf for folder parents and -p for service parents.")
   sys.exit()

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

if nameval!=None: filtercond.append('contains($primary,name,"'+nameval+'")')
if modby!=None: filtercond.append("eq(modifiedBy,"+modby+")")

# set the request type
reqtype='get'
delimiter = ','

# process items not in folders
if puri!=None: 
   filtercond.append("contains(parentUri,'"+puri+"')")
   completefilter = 'and('+delimiter.join(filtercond)+')'
   reqval="/files/files?filter="+completefilter+"&limit=10000"
        
# process items in folders
elif pfolder!=None:

   folderid=getfolderid(pfolder)[0]     
   # add the start and end and comma delimit the filter
   completefilter = 'and('+delimiter.join(filtercond)+')'
   reqval="/folders/folders/"+folderid+"/members?filter="+completefilter+"&limit=10000"
   
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
   reqval="/files/files?filter="+completefilter+"&limit=10000"

else:

   completefilter = 'and('+delimiter.join(filtercond)+')'
   reqval="/files/files?filter="+completefilter+"&limit=10000"


files_result_json=callrestapi(reqval,reqtype) 

  
#create a directory with a name of the timestamp only if running in execute mode
newdirname="D"+dt.today().strftime("%Y%m%dT%H%MS")

archivepath=os.path.join(path,newdirname )
if os.path.isdir(archivepath)==False: os.makedirs(archivepath)

files = files_result_json['items']

if debug:
   print(reqval)
   #print(json.dumps(files,indent=2))

if len(files):
   if os.path.isdir(archivepath)==False: os.makedirs(archivepath)

# list that contains files that can be archived
passlist=[]

# process each file
for file in files:

   fileid=file['id']
   contenttype=file['contentType']

     
   filename=file['name'] 
   archivefile=os.path.join(archivepath,filename )
       
   reqtype='get'	   
   reqval="/files/files/"+fileid+"/content"
   
   content=callrestapi(reqval,reqtype)

            
   out_type='w'
      
   # decide on write style w+b is binary w is text
   # currently cannot process binary files
   if contenttype.startswith('application/v') or  contenttype.startswith('image') or  contenttype.startswith('video') or  contenttype.startswith('audio') or  contenttype.startswith('application/pdf'): 
   
      out_type="wb"

      print('NOTE: '+filename+' of content type ' +contenttype+' not supported')
      
   else:
   # if files is not binary write it to the archive
            
       if type(content) is dict:
          
          with open(archivefile, out_type) as fp:
             json.dump(content,fp,indent=4)
        
          fp.close()
          passlist.append(filename)
                  
       elif type(content) is unicode or type(content) is str:
          
           with open(archivefile, out_type) as fp:

               if version < 3:
                  fp.write(content.encode('utf8'))          
               else: fp.write(content)

           fp.close()
           passlist.append(filename)
       
       else: print('NOTE: '+filename+' content type not supported')
       
       # delete requested
       if dodelete:

          reqtype='delete'
          reqval="/files/files/"+fileid
                   
          callrestapi(reqval,reqtype)
      

if len(passlist):	  
   print('NOTE: files archived to the directory '+archivepath)
   if dodelete: print('NOTE: files deleted from Viya.')
else:
   print('NOTE: No files that can be processed were found.')
