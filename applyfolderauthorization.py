#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# applyfolderauthorization.py
#
#
# Change History
#
# 17Mar20 Initial development
#
# Format of input csv file is 6 columns
# Column 1 is the full path to the folder
# Column 2 is the principal type
# Column 3 is the principal name
# Column 4 is the access setting (grant or prohibit)
# Column 5 is the permissions on the folder
# Column 6 is the conveyed permissions on the folder's contents
#
# For example:
# /gelcontent/gelcorp/marketing/reports,group,Marketing,grant,"read,add,remove","read,update,add,remove,delete,secure"
#
# Copyright 2020, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
from sharedfunctions import callrestapi, getfolderid, file_accessible, printresult,getapplicationproperties

# get cli location from properties
propertylist=getapplicationproperties()

clidir=propertylist["sascli.location"]
cliexe=propertylist["sascli.executable"]

clicommand=os.path.join(clidir,cliexe)


# setup command-line arguements
parser = argparse.ArgumentParser(description="Apply bulk auths from a CSV file to folders and contents")
parser.add_argument("-f","--file", help="Full path to CSV file. Format of csv: 'folderpath,principaltype,principalid,grant_or_prohibit,perms_on_folder,perms_on_contents",required='True')
args = parser.parse_args()
file=args.file

reqtype="post"

check=file_accessible(file,'r')
constructed_bulk_rules_list=[]

# file can be read
if check:
#    print("file: "+file)
    with open(file, 'rt') as f:
        filecontents = csv.reader(f)
        for row in filecontents:
            folderpath=row[0]
            principaltype=row[1]
            principalname=row[2]
            accesssetting=row[3]
            folderpermissions=row[4]
            conveyedpermissions=row[5]

#            print("Creating auth rules for "+folderpath)

            folderid=getfolderid(folderpath)
            folderuri=folderid[0]
            reqval='/folders/folders/'+folderuri

# Construct JSON objects from auth rules defined in CSV. Two JSON objects are created for each row of CSV; one for perms on the folder object, one for conveyed perms on the object's contents.
            value_dict_object={"description":"Created by applyfolderauthorizations.py",
                        "objectUri":reqval,
                        "permissions":folderpermissions.split(','),
                        "principalType":principaltype,
                        "principal":principalname,
                        "type":accesssetting
                       }
            value_dict_container={"description":"Created by applyfolderauthorizations.py",
                                  "containerUri":reqval,
                                  "permissions":conveyedpermissions.split(','),
                                  "principalType":principaltype,
                                  "principal":principalname,
                                  "type":accesssetting
                                 }

            constructed_rule_dict_object={
                                   "op":"add",
                                    "value":value_dict_object
                                   }
            constructed_rule_dict_container={
                                       "op":"add",
                                       "value":value_dict_container
                                      }
            constructed_bulk_rules_list.append(constructed_rule_dict_object)
            constructed_bulk_rules_list.append(constructed_rule_dict_container)

else:
    print("ERROR: cannot read "+file)

print("Writing out bulk rule JSON file to bulk_rules_list.json")
# Construct JSON schema containing rules
bulk_rules_list_string=json.dumps(constructed_bulk_rules_list,indent=2)
with open("bulk_rules_list.json", "w") as text_file:
    text_file.write(bulk_rules_list_string+'\n')

# Execute sas-admin CLI to apply rules from JSON schema
command=clicommand+' authorization create-rules --file bulk_rules_list.json'
print("Executing command: "+command)
subprocess.call(command, shell=True)
