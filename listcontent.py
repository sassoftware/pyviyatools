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

from sharedfunctions import getfolderid, callrestapi, printresult, getfolderid, getidsanduris, getpath, json

# get python version  
version=int(str(sys.version_info[0]))

# get input parameters	
parser = argparse.ArgumentParser(description="List folder and its sub-folders and contents")
parser.add_argument("-f","--folderpath", help="Enter the path to the viya folder to start the listing.",required='True')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='json')
parser.add_argument("--debug", action='store_true', help="Debug")

args = parser.parse_args()

debug=args.debug
path_to_folder=args.folderpath
output_style=args.output

def getfoldercontent(path_to_folder):

    # call getfolderid to get the folder id
    targets=getfolderid(path_to_folder)

    if debug: print(targets)

    # if the folder is found
    if targets[0] is not None:
        
        uri=targets[1]
        
        #get folder content, recursive call returns all children
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
            
            #if contenttype=='folder': path_to_item=getpath(itemuri)
            #else: path_to_item=getpath(parentFolderUri)
            path_to_item=getpath(itemuri)

            itemlist[i]["pathtoitem"]=path_to_item
            itemlist[i]["pathanditemname"]=path_to_item+name
            #print(path_to_item,name,contenttype)  
 
    return folders_result_json

   
cols=["pathtoitem","name","contentType","createdBy","creationTimeStamp","uri"]

# root folder, loop sub-folders and print
if path_to_folder=="/":
       
    # get a list of root folders

    # get the json result for each one

    # append them together for printing

    reqval='/folders/rootFolders'
    reqtype='get'
    rootfolderresult=callrestapi(reqval,reqtype)
    rootfolders=rootfolderresult["items"]
   
    z=0

    for folder in rootfolders:
        
        foldername="/"+folder["name"]
        result_json=getfoldercontent(foldername)

        content_count=result_json['count']
        
        # print if there is content in the folder
        if content_count: 

            # printer header only for the first group    
            if z==0: printresult(result_json,output_style,cols)
            else: printresult(result_json,output_style,cols,header=0)
            z=z+1
            
else:
    
    # print folder content
    result_json=getfoldercontent(path_to_folder)
    printresult(result_json,output_style,cols)
            

