#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# disableviyarules.py
#
# Reads in a CSV file, converts it to json format and imports into Viya 
#
# Change History
#
# 12Nov26  Initial development
# 26Nov26  Updated to have better error handling and meaningful messaging when
#          rules don't apply, or the script is re-run without re-enabling previously disabled rules.
#          Added the ability to re-enable rules disabled by a previous run of this script. 
#          To re-enable rules, provide the list of disabled rule IDs and use the -o enable option.
#          e.g. ./disableviyarules.py -o enable -f disabled_rule_ids20261126_170528.txt
#
# Format of input csv file is 6 columns
# Column 1: Object URI
# Column 2: Principal type ["group" | "user"]
# Column 3: Principal id [<groupID> | <userID>]
# Column 4: Access grant type ["grant" | "prohibit")
# Column 5: Applicable permissions ["read","delete","add","create","remove","secure","update"]
# Column 6: Rule's status ["true" | "false"]
# Column 7: Rule's condition, if applicable.
#           This column must either be left blank OR contain a VALID SpEL condition.
#           Use of an invalid condition will see the rule not be created in Viya.
#           If unsure of a conditions validity, test it using the Viya EVM Rules interface.
#           (NGMTS-30861)
#
# For example:
# "/scoreExecution/executions/**","group","role_developer","grant","read,delete,create,secure,update",True,""
#
# Copyright 2026, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
import pandas as pd
from datetime import datetime
from sharedfunctions import callrestapi, file_accessible, printresult, getapplicationproperties, getclicommand


### Sets definitions

def normalise_type(value):
    value = value.lower()
    if "prohibit" in value:
        return "prohibit"
    if "grant" in value:
        return "grant"
    return value

def normalise_principal(value):
    if value in ["", None, "None"]:
        return ""
    return value

def rule_matches(rule1, rule2):
    return (
        rule1.get("objectUri") == rule2.get("objectUri")
        and rule1["principalType"]
            == rule2["principalType"]
        and normalise_principal(rule1.get("principal"))
            == normalise_principal(rule2.get("principal"))
        and normalise_type(rule1["type"])
            == normalise_type(rule2["type"])
        and set(rule1["permissions"])
            == set(rule2["permissions"])
        and rule1.get("condition", "")
            == rule2.get("condition", "")
    )

def scan_results():
    print("\nRule scan results:\n")
    print(f" -> {len(rule_ids)} rule(s) found and disabled")
    print(f" -> {len(rules_already_disabled)} rule(s) already disabled")
    print(f" -> {len(rules_not_found)} input rule(s) do not exist in the target Viya environment\n")

def reasoning1():
    print(f"Rules not found have been saved to: \033[1;34m{rulesnotfound}\033[0m\n")
    print("These rules may not have disabled due to one of the following reasons:\n\033[1;33m"+
          " -> the rule contains a container URI - which this tool does not support\n"+
          " -> the rule has different permissions to those of the rule that it's intended to disable\n\033[0m")

### Sets command-line arguements
parser = argparse.ArgumentParser(description="Disables specified Viya rules")
parser.add_argument("-f","--file", help="Full path to CSV file. Format of csv: 'objecturi,principaltype,principalid,grant_or_prohibit,perms,enabled,condition",required='True')
parser.add_argument("-o","--operator", choices=['enable','disable'], default='disable', help=argparse.SUPPRESS)
args = parser.parse_args()
file=args.file
operator=args.operator

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

reqtype="post"

check=file_accessible(file,'r')
constructed_bulk_rules_list=[]
runtime = datetime.now().strftime("%Y%m%d_%H%M%S")

offrules=file

### Start of processing
print('\ndisableviyarules.py running...\n')

if operator !='disable':
    ## Compiles and runs the Viya CLI commands to change the rules' status
    with open(offrules, "r", newline='') as input:
        reader = csv.reader(input)
        for row in reader:
            id=row[0]
            ## added a 'yes to all parameter'
            #command = clicommand+ ' authorization '+operator+'-rule --id '+id
            command = clicommand+ ' authorization -y enable-rule --id '+id
            print("Executing command: "+command)
            subprocess.call(command, shell=True)
    input.close()
    sys.exit()
else:
    pass


### Loops through the 'offrules' file and converts the CSV rows into JSON entries
if check:
    with open(offrules, 'r') as f:
        filecontents = csv.reader(f, skipinitialspace=True)
        for row in filecontents:
            objecturi=row[0]
            principaltype=row[1]
            principalname=row[2]
            accesssetting=row[3]
            perms=row[4]
            enabled=row[5]
            condition=row[6]
            pattern=str(row)[1:-1]
            pattern=f'{pattern}'

            ## debug ##
            #print('printing pattern: = '+pattern)
            #print("Creating auth rules for "+objecturi)

            reqval=objecturi
        

            ## Construct JSON objects from auth rules defined in CSV
            value_dict_object={"description":"Disabled by disableviyarules.py",
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
### End of loop


### Creates JSON file and contructs schema containing rules
offrulesjson='rulesdisabled_'+runtime+'.json'

bulk_rules_list_string=json.dumps(constructed_bulk_rules_list,indent=2)
with open(offrulesjson, "w") as text_file:
    text_file.write(bulk_rules_list_string+'\n')

print("Input file converted to JSON format: \033[1;34m" +offrulesjson+" \033[0m\n")


### Runs listrules.py and output all existing rules
print('Retrieving Viya environment\'s current rules...\n')
existingrules = './listrules.py ' +'-o json --limit 20000 > existing_rules_verbose.json'
subprocess.call(existingrules, shell=True)


### Runs a loop and outputs the IDs of rules to be disabled
print('Scanning for rule changes...\n')

with open(offrulesjson, "r") as f:
    rules_to_disable = json.load(f)

with open("existing_rules_verbose.json", "r") as f:
    ruleid_data = json.load(f)
    existing_rules = ruleid_data["items"]

rule_ids = []
rules_already_disabled = []
rules_not_found = []

for rule_to_disable in rules_to_disable:
    rule = rule_to_disable["value"]
    matched = False

    for existing_rule in existing_rules:
        # Ignore container rules
        if existing_rule.get("containerUri"):
            continue

        if rule_matches(rule, existing_rule):
            matched = True

            # The rule exists. Only add its ID when it is currently enabled.
            if str(existing_rule.get("enabled", "")).lower() == "false":
                rules_already_disabled.append(rule)
            else:
                rule_ids.append(existing_rule["id"])
            break

    # No matching non-container rule exists in the target Viya environment
    if not matched:
        rules_not_found.append(rule)

### Write rules that genuinely do not exist in the target environment
rulesnotfound = 'rules_not_found_'+runtime+'.csv'
if rules_not_found:
    with open(rulesnotfound, "w", newline="") as f:
        writer = csv.writer(f)
        for rule in rules_not_found:
            writer.writerow([
                rule.get("objectUri", ""),
                rule.get("principalType", ""),
                normalise_principal(rule.get("principal")),
                rule.get("type", ""),
                ",".join(rule.get("permissions", [])),
                rule.get("enabled", ""),
                rule.get("condition", "")
            ])

scan_results()

if rules_not_found and rule_to_disable is None:
    reasoning1()

### Write matched rule IDs out to a txt file, one per line
ruleslist='disabled_rule_ids'+runtime+'.txt'
with open(ruleslist, "w") as f:
    for rule_id in rule_ids:
        f.write(rule_id + "\n")


if not rule_ids:
    if rules_not_found:
        reasoning1()
    print(f"\033[1;32mNo new rules to be disabled.\n\033[0m")
    sys.exit()
else:
    print(f"Successfully retrieved IDs of \033[1;32m{len(rule_ids)} rule(s).\033[0m\n")


### Runs the Viya CLI commands to disable the matched rules
with open(ruleslist, "r") as f:
    for line in f:
        rule_id = line.strip()

        # Ignore blank lines
        if not rule_id:
            continue

        command = clicommand+ ' authorization -y -q '+operator+'-rule --id '+ rule_id

        print("Executing command:" +command)
        subprocess.call(command, shell=True)
print(f"\ndisableviyarules.py completed, \033[1;32m{len(rule_ids)} rule(s)\033[0m were disabled.\n\nAll rule IDs disabled have been saved to: \033[1;34m" +ruleslist + "\033[0m \n")
scan_results()

if rules_not_found:
    reasoning1()
