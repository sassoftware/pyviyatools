#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# createfolders.py
# October 2018
#
#
# Change History
#
# 30oct2018 Initial development
#
# Format of csv file is two columns
# Column 1 is the full path to the folder
# Column 2 is a description
#
# For example:
#/RnD, Folder under root for R&D
#/RnD/reports, reports
#/RnD/analysis, analysis
#/RnD/data plans, data plans
#/temp,My temporary folder

#
# Copyright 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
import argparse
import csv
import os
from sharedfunctions import callrestapi, getfolderid, file_accessible

# setup command-line arguements    
parser = argparse.ArgumentParser(description="Create folders that are read from a csv file")
parser.add_argument("-f","--file", help="Full path to csv file containing folders, format of csv: 'folderpath,description ",required='True')
args = parser.parse_args()
file=args.file

reqtype="post"

check=file_accessible(file,'r')

# file can be read
if check:

    with open(file, 'rt') as f:
        
        filecontents = csv.reader(f)
        for row in filecontents:
            
            #print(row)
            newfolder=row[0]
            description=row[1]
          
                       
            if newfolder[0]!='/': newfolder="/"+newfolder 
            
            folder=os.path.basename(os.path.normpath(newfolder))
            parent_folder=os.path.dirname(newfolder)
            
            data = {}
            data['name'] = folder
            data['description'] = description
            
            
            print ("Creating folder "+newfolder )
                 
            if parent_folder=="/": reqval='/folders/folders'  
            else:  # parent folder create a child
                                                 
                parentinfo=getfolderid(parent_folder)
                
                if parentinfo != None:    
                 
                    parenturi=parentinfo[1]
                    reqval='/folders/folders?parentFolderUri='+parenturi
                                   
                else: print("Parent folder not found")
    
            myresult=callrestapi(reqval,reqtype,data=data,stoponerror=0) 
else:
    print("ERROR: cannot read "+file)
        