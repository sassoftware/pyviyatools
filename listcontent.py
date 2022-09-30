#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# listcontent.py
# february 2018
#
# Pass in a folder path and list content
# Change History

#
# Copyright © 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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

import argparse, sys

from sharedfunctions import getfolderid, callrestapi, printresult, getfolderid, getidsanduris, getpath

# get python version  
version=int(str(sys.version_info[0]))

# get input parameters	
parser = argparse.ArgumentParser(description="List folder and its sub-folders and contents")
parser.add_argument("-f","--folderpath", help="Enter the path to the viya folder to start the listing.",required='True')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='json')
parser.add_argument("--debug", action='store_true', help="Debug")

args = parser.parse_args()

print(args.folderpath)
debug=args.debug
path_to_folder=args.folderpath
output_style=args.output

# call getfolderid to get the folder id
targets=getfolderid(path_to_folder)

if debug: print(targets)

cols=["pathtoitem","name","contentType","createdBy","creationTimeStamp","uri"]

# if the folder is found
if targets[0] is not None:
    
    uri=targets[1]
    
    #delete folder content, recursive call returns all children
    reqval=uri+"/members?recursive=true&limit=100000"
    reqtype='get'

    if debug: print(reqval)
    folders_result_json=callrestapi(reqval,reqtype)
    
    # add a loop of folder result that adds the parent folder path
    # add the path back into the json for printing
    total_items=folders_result_json['count']
    itemlist=folders_result_json['items']
    returned_items=len(itemlist)
    
    for i in range(0,returned_items):

        itemuri=itemlist[i]["uri"]
        name=itemlist[i]["name"]
        contenttype=itemlist[i]["contentType"]
                
        parentFolderUri=itemlist[i]["parentFolderUri"]   
        
        if contenttype=='folder': path_to_item=getpath(itemuri)
        else: path_to_item=getpath(parentFolderUri)

        itemlist[i]["pathtoitem"]=path_to_item
        itemlist[i]["pathanditemname"]=path_to_item+name
        #print(path_to_item,name,contenttype)  

    printresult(folders_result_json,output_style,cols)
		
else: print("NOTE: No content in Folder.")
