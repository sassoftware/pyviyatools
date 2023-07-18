#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# createcaslibjson.py
#
# This script it meant as a pre-step ahead of using the importcaslibs.py script.
# The intent of this file is to read in a CSV file and output a set of formatted
# json files to a 'caslibs' directory.
# Once these files have been created, then importcaslibs.py may be run (with superuser permissions)
# to create new CASLIBs from these json files.
#
# Change History
#
# 13Apr23 Initial development
#
# Format of input csv file is 5 columns
# Column 1: CASLIB name
# Column 2: CASLIB path
# Column 3: CAS server (default: "cas-shared-default"
# Column 4: CASLIB type (e.g. "path")
# Column 5: Sub-directories? <true | false>
#
# For example:
# "Sample_Path","/tmp/samplepath/","cas-shared-default","path","true"
#
# Copyright 2023, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
import json
import subprocess
import sys
from sharedfunctions import callrestapi, getfolderid, file_accessible, printresult, getapplicationproperties

# get cli location from properties
propertylist=getapplicationproperties()

clidir=propertylist["sascli.location"]
cliexe=propertylist["sascli.executable"]
clicommand=os.path.join(clidir,cliexe)


# setup command-line arguements
parser = argparse.ArgumentParser(description="Create basic CASLIBs from a CSV file")
parser.add_argument("-f","--file", help="Full path to CSV file. Format of csv: 'name,path,casserver,type,subdirs",required='True')
args = parser.parse_args()
file=args.file

reqtype="post"

check=file_accessible(file,'r')
constructed_bulk_caslibs_list=[]

## Creates directory for the CASLIB json files
try:
    os.mkdir("caslibs")
    print("Creating \"caslibs\" directory.")
except OSError as error:
    pass

## Checks that CSV file can be read
if check:
    with open(file, 'rt') as f:
        filecontents = csv.reader(f)
        for row in filecontents:
            name=row[0]
            path=row[1]
            casserver=row[2]
            type=row[3]
            subdirs=row[4]

## Construct JSON objects from values defined in CSV.
            optional_attribs_dict_object={
                        "active":"true",
                        "personal":"false",
                        "subDirs":subdirs
                        }
        
            value_dict_object={
                        "attributes":optional_attribs_dict_object,
                        "description":"Created by createcaslibbasic.py",
                        "name":name,
                        "path":path,
                        "scope":"global",
                        "server":casserver,
                        "type":type                        
                       }
            print("Writing CASLIB json: "+name)

            jsonfile="caslibs/"+name+".json"
            #print(jsonfile)
            # Format JSON schema containing rules
            caslibs_string=json.dumps(value_dict_object,indent=4)
            with open(jsonfile, "w") as text_file:
               text_file.write(caslibs_string+'\n')

            ## Removes the double quotes from the 'attributes' values after they've been parsed through json.dumps.
            ## The omission of double quotes for these values is a requirement for Viya CLI to be able to apply the
            ## attribs to the new CASLIBs.
            ## Ideally this section needs re-writing to be more elegant and efficient.

            cleanuptrue = "\"true\""
            cleanupfalse = "\"false\""

            with open(jsonfile, mode = "r", errors='ignore') as file:
              cleaned = file.read().replace(cleanuptrue, 'true') 
            with open(jsonfile, mode = "w", errors='ignore') as newfile:
              newfile.write(cleaned)

            with open(jsonfile, mode = "r", errors='ignore') as file:
              cleaned = file.read().replace(cleanupfalse, 'false') 
            with open(jsonfile, mode = "w", errors='ignore') as newfile:
              newfile.write(cleaned)
              
                     
else:
    print("ERROR: cannot read "+file)

print("CASLIB json files created.")

