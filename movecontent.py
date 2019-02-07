#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# movecontent.py
# December 2017
#
# Moves content from one folder to another
#
# Change History
#
#  27JAN2018 Comments added  
#  03Feb2018 Added quiet mode
#  03Mar2018 Made prompt comparison case-insensitive  
#
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
    
parser = argparse.ArgumentParser(description="Move content from a source to a target folder")
parser.add_argument("-s","--sourcefolder", help="Enter the path to the source folder.",required='True')
parser.add_argument("-t","--targetfolder", help="Enter the path to the source folder.",required='True')
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')
args = parser.parse_args()

source=args.sourcefolder
target=args.targetfolder

quietmode=args.quiet

sourceinfo=getfolderid(source)
targetinfo=getfolderid(target)

if sourceinfo[0] is not None: 
    
    id=sourceinfo[0]
	
    if quietmode:
        areyousure="Y"
    else:
        
        if version  > 2:
            areyousure=input("Are you sure you want to move content from "+source+" to "+target+"? (Y)")
        else:
            areyousure=raw_input("Are you sure you want to move content from "+source+" to "+target+"? (Y)") 
   
    if areyousure.upper() == 'Y':    
    
        # get all the content in folder
        reqtype='get'
        reqval='/folders/folders/'+id+"/members"
        members=callrestapi(reqval,reqtype)
                
		# create a list of items
        items=members["items"]
        
        for item in items:
    
            # delete from folder
            
            reqtype="delete"
            reqval='/folders/folders/'+id+"/members/"+item["id"]
            rc=callrestapi(reqval,reqtype)
                    
            #build dictionary of item
            
            thisitem={"uri":item["uri"],"name":item["name"],"type":item["type"],"contentType":item["contentType"]}
            
            #add to new folder
            
            reqtype="post"
            reqval="/folders/folders/"+targetinfo[0]+"/members"
            rc=callrestapi(reqval,reqtype,data=thisitem)
            
        print("NOTE: content moved between folder "+source+" and "+target)
                       
        
    else:
        print("Good thing I asked!")
