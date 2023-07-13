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
# Column 2: Group Name ID
# Column 3: Permissions
#
# For example:
# "BI","sasdevelopers","readInfo,select,limitedPromote,promote,createTable,dropTable,deleteSource,insert,update,delete,alterTable,alterCaslib,manageAccess"
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
parser = argparse.ArgumentParser(description="Create CASLIBs Authorization files from a CSV file")
parser.add_argument("-f","--file", help="Full path to CSV file. Format of csv: 'CASLIB,ID,permissions",required='True')
args = parser.parse_args()
file=args.file

reqtype="post"

check=file_accessible(file,'r')
unique_caslibs=[]
caslib_auth_dict={}

# create a dictionary structure for the authorization
if check:

    # build a dictionary of lists, each list is named for unique caslibs in the csv
    with open(file, 'rt') as f:
        filecontents = csv.reader(f)
        for row in filecontents:
            name=row[0]
            if name not in unique_caslibs:

                unique_caslibs.append(name)

    for caslib in unique_caslibs:

      dict={"items":[]}
      caslib_auth_dict[caslib]=dict


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
            id=row[1]
            perms=row[2]
            perms=(perms.split(','))


## Construct JSON objects from values defined in CSV.
            for auth in perms:
                value_dict_object={
                ## for debug purposes only
                            "name":name,
                ##
                            "identity":id,
                            "identityType":"group",
                            "permission":auth,
                            "type":"grant",
                            "version": 1
                            }

                
                # append permissions to caslibs list
                caslib_auth_dict[name]["items"].append(value_dict_object)


    # write out authorization files
    for name in unique_caslibs:

      print("Writing CASLIB authorization file: "+name)
      jsonfile="caslibs/"+name+"_authorization_.json"

      caslibs_string=json.dumps(caslib_auth_dict[name],indent=4)

      with open(jsonfile, "w") as text_file:
        text_file.write(caslibs_string+'\n')


else:
    print("ERROR: cannot read "+file)

print("Successfully created CASLIB authorization files.")


