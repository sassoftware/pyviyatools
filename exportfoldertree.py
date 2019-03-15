#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# exportfoldertree.py
# March 2018
#
# Pass in a directory and this tool will export the complete viya folder
# structure to a sub-directory named for the current date and time
# There will be a json file for each viya folder at the root level.
#   
#
# Change History
#
#
# Copyright Â© 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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

import argparse, sys, subprocess, uuid, time, os

from sharedfunctions import getfolderid, callrestapi

# get python version  
version=int(str(sys.version_info[0]))


# CHANGE THIS VARIABLE IF YOUR CLI IS IN A DIFFERENT LOCATION
clidir='/opt/sas/viya/home/bin/'


# get input parameters	
parser = argparse.ArgumentParser(description="Export the complete Viya folder tree")
parser.add_argument("-d","--directory", help="Directory for Export",required='True')
args= parser.parse_args()
basedir=args.directory

# create output directory: was giving the directory a name
#now=time.localtime()
#dirname="D_"+time.strftime('%Y-%m-%dT%H:%M:%S',now)
#path=os.path.join(basedir,dirname)

# I now just use the directory the user specifies
path=basedir
if not os.path.exists(path): os.makedirs(path)

# retrieve root folders
reqtype='get'
reqval='/folders/rootFolders'
resultdata=callrestapi(reqval,reqtype)


# loop root folders
if 'items' in resultdata:
  
    total_items=resultdata['count']
        
    returned_items=len(resultdata['items'])
        
    if total_items == 0: print("Note: No items returned.")
    else:
     
        # export each folder and download the package file to the directory
		
	for i in range(0,returned_items):   
			
	     id=resultdata['items'][i]["id"]
             package_name=str(uuid.uuid1())
	     json_name=resultdata['items'][i]["name"].replace(" ","")+'_'+str(i)
					
	     command=clidir+'sas-admin transfer export -u /folders/folders/'+id+' --name "'+package_name+'"'
	     print(command)     
	     subprocess.call(command, shell=True)

	     reqval='/transfer/packages?filter=eq(name,"'+package_name+'")'                
	     package_info=callrestapi(reqval,reqtype)
			
	     package_id=package_info['items'][0]['id']
			
	     completefile=os.path.join(path,json_name+'.json')
	     command=clidir+'sas-admin transfer download --file '+completefile+' --id '+package_id    
	     print(command)
	     subprocess.call(command, shell=True)

print("NOTE: Viya root folders exported to json files in "+path) 
         

