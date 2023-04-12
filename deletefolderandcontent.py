#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# deletefolderandcontent.py
# february 2018
#
# Pass in a folder path and delete the folder, its sub-folders and content 
#
# Change History
#
#  27JAN2018 Comments added  
#  03Feb2018 Added quiet mode  
# based on delete folder, but in addition deletes reports. 

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

from sharedfunctions import getfolderid, callrestapi

# get python version  
version=int(str(sys.version_info[0]))

# get input parameters	
parser = argparse.ArgumentParser(description="Delete a folder and its sub-folders and contents")
parser.add_argument("-f","--folderpath", help="Enter the path to the viya folder.",required='True')
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')
args = parser.parse_args()

print("NOTE: folder= "+args.folderpath)
path_to_folder=args.folderpath
quietmode=args.quiet

# call getfolderid to get the folder id
targets=getfolderid(path_to_folder)

# if the folder is found
if targets[0] is not None:
    
    uri=targets[1]

    # if quiet do not prompt
    if quietmode:
        areyousure="Y"
    else:
        
        if version  > 2:
            areyousure=input("Are you sure you want to delete the folder and its contents? (Y)")
        else:
            areyousure=raw_input("Are you sure you want to delete the folder and its contents? (Y)") 
    
    if areyousure.upper() == 'Y':
    
        #delete folder content, recursive call returns all children
        reqval=uri+"/members?recursive=true"
        reqtype='get'
        allchildren=callrestapi(reqval,reqtype)
		
        # get all child items
        if 'items' in allchildren:
    
            itemlist=allchildren['items']

            for children in itemlist:
                
                #if it is a report
                if children['contentType']=='report':
		              
                    linklist=children['links']
		    
                    for linkval in linklist:
                        
                        #find the delete method and call it
                        if linkval['rel']=='deleteResource':
                            reqval=(linkval['uri'])
                            reqtype=(linkval['method']).lower()		    		
                            callrestapi(reqval,reqtype) 
		
        print("NOTE: Deleting folde and content from "+ path_to_folder+" "+uri)

        reqval=uri+"?recursive=true"
        reqtype='delete'
        callrestapi(reqval,reqtype)
        print('NOTE: Folder Deleted.')
				
    else:
        print("Good thing I asked!")
