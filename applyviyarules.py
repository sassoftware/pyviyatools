#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# applyviyarules.py
#
# Reads in a CSV file, converts it to json format and imports into Viya 
#
# Change History
#
# 12Apr23 Initial development
#
# Format of input csv file is 6 columns
# Column 1: Object URI
# Column 2: Principal type ["group" | "user"]
# Column 3: Principal id [<groupID> | <userID>]
# Column 4: Access setting ["grant" | "prohibit")
# Column 5: Applicable permissions ["read","delete","add","create","remove","secure","update"]
# Column 6: Rule's status ["true" | "false"]
# Column 7: Rule's condition, if applicable.
#           This column must either be left blank OR contain a VALID SpEL condition.
#           Use of an invalid condition will see the rule not be created in Viya.
#           If unsure of a conditions validity, test it using the Viya EVM Rules interface.
#
# For example:
# "/scoreExecution/executions/**","group","role_developer","grant","read,delete,create,secure,update",True,""
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
parser = argparse.ArgumentParser(description="Apply bulk auths from a CSV file to folders and contents")
parser.add_argument("-f","--file", help="Full path to CSV file. Format of csv: 'objecturi,principaltype,principalid,grant_or_prohibit,perms,enabled,condition",required='True')
args = parser.parse_args()
file=args.file

reqtype="post"

check=file_accessible(file,'r')
constructed_bulk_rules_list=[]

## Checks that file can be read
if check:
    with open(file, 'rt') as f:
        filecontents = csv.reader(f)
        for row in filecontents:
            objecturi=row[0]
            principaltype=row[1]
            principalname=row[2]
            accesssetting=row[3]
            perms=row[4]
            enabled=row[5]
            condition=row[6]

            print("Creating auth rules for "+objecturi)

            reqval=objecturi

## Construct JSON objects from auth rules defined in CSV.
            value_dict_object={"description":"Created by applyviyarules.py",
                        "objectUri":reqval,
                        "permissions":perms.split(','),
                        "principalType":principaltype,
                        "principal":principalname,
                        "type":accesssetting,
                        "enabled":enabled,
                        "condition":condition                        
                       }

            constructed_rule_dict_object={
                                   "op":"add",
                                    "value":value_dict_object
                                   }

            constructed_bulk_rules_list.append(constructed_rule_dict_object)

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
