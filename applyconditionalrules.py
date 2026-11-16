#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# applyconditionalrules.py
#
# Reads in a CSV of conditional rules file, converts it to json format and imports into Viya 
#
# Change History
#
# 16NOV26  Initial development
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
import re
import pandas as pd
from datetime import datetime
from sharedfunctions import callrestapi, getfolderid, file_accessible, printresult, getapplicationproperties, getclicommand



## setup command-line arguements
parser = argparse.ArgumentParser(description="Apply bulk auths from a CSV file to folders and contents")
parser.add_argument("-f","--file", help="Full path to CSV file. Format of csv: 'objecturi,principaltype,principalid,grant_or_prohibit,perms,enabled,condition",required='True')
args = parser.parse_args()
file=args.file

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

reqtype="post"

check=file_accessible(file,'r')
constructed_bulk_rules_list=[]
runtime = datetime.now().strftime("%Y%m%d_%H%M%S")


#newrules=file
print('\napplyconditionalrules.py running...\n')

def nonewrules():
    print("There are \033[1;33mNO NEW CONDITIONAL RULES\033[0m to be applied. \n ")
    sys.exit()

##########################################################
## Output directory
##########################################################
cwd = os.getcwd()
results_dir = os.path.join(cwd, "applyconditionalrules_results")
os.makedirs(results_dir, exist_ok=True)

##########################################################
## Temporary section 1
##########################################################
## Runs a comparison of the file submitted by the user against existing_rules.csv
## This section may be removed once PMCPFR-1363 is resolved.

## Runs listrules.py and compiles exisiting_rules.csv
print('Documenting existing rules... \n')
existing_rules_verbose = os.path.join(results_dir, 'existing_rules_verbose.csv')
existingrules = './listrules.py -o csv > \"' + existing_rules_verbose + '\"'
subprocess.call(existingrules, shell=True)

#pd.set_option('display.max_columns', None)

## Reads in and trims the existing_rules_verbose.csv file into existing_rules.csv
df = pd.read_csv(existing_rules_verbose,usecols=['objectUri','principalType','principal','setting','permissions','enabled','condition'])
df['permissions']=df['permissions'].str[1:-1]
df['permissions']=df['permissions'].str.replace(' ',',')
df= df[['objectUri','principalType','principal','setting','permissions','enabled','condition']]
df['enabled'] = df['enabled'].apply(lambda x:str(x))
existing_rules = os.path.join(results_dir, 'existing_rules.csv')
df.to_csv(existing_rules, header=False, index=None, quoting=csv.QUOTE_NONNUMERIC)
with open(existing_rules, 'r') as exr:
    csvrow = exr.readlines()
    for line in csvrow:
        rules=line.split("]") 

newrules=os.path.join(results_dir, 'rulesapplied_'+runtime+'.csv')

print("Checking for new rules to apply... \n")
#print("Printing results (CSV format) to: \033[1;34m"+newrules+"\033[0m \n")
grepcom='grep -Fiv -f "' + existing_rules + '" "' + file + '" > "' + newrules + '"'
subprocess.call(grepcom, shell=True)
##########################################################
# End of Temporary section 1
##########################################################


##########################################################
# Temporary section 2
##########################################################
## Sorts the rules by 'grants' and 'conditional grants' and
## send rules containing conditions to 'conditional_rules.csv'
## for manual implementation.
## This section may be removed once PMCPFR-1364 is resolved.
conditionalrules=os.path.join(results_dir, 'conditional_rules_'+runtime+'.csv')
df2 = pd.read_csv(newrules, quoting=csv.QUOTE_ALL, names=['objectUri','principalType','principal','setting','permissions','enabled','condition'])
df2.sort_values(by=['setting'],inplace=True, ascending=False)
df2= df2.fillna("")
df2= df2.groupby('setting')
dfcondgrants=None

try:
    ### 11Nov26 - Enhancement to include 'conditional' when filtering rules
    ###           (the filter includes "grant" to ensure back-compatability with older Supplement docs)
    #dfcondgrants= df2.get_group("grant")
    dfcondgrants = pd.concat(
    [df2.get_group(name) for name in df2.groups
     if str(name).lower() == "grant" or "conditional" in str(name).lower()]
    )
    ### End of enhancement
except:
    nonewrules()
else:
    mask= dfcondgrants['condition'] != ""
    dfcondgrants= dfcondgrants[mask]

if  dfcondgrants is not None :
    dfcondgrants.to_csv(open(conditionalrules,'w'), header=False, index=None, quoting=csv.QUOTE_NONNUMERIC)
    print("\033[1;32mFound",len(dfcondgrants),"\033[0mNEW CONDITIONAL RULE(S) to be applied.\n")
    
else:
    nonewrules()
##########################################################
# End of Temporary section 2
##########################################################


## Loops through the 'conditionalrules' file and converts each CSV row
## into its own JSON file, then applies each rule individually.
if check:
    rule_count = 0
    successful_rule_count = 0
    failed_rules = []

    failed_rules_json = os.path.join(results_dir, "failed_conditional_rules_" + runtime + ".json")
    failed_rules_csv = os.path.join(results_dir, "failed_conditional_rules_" + runtime + ".csv")

    with open(conditionalrules, 'r') as f:
        filecontents = csv.reader(f, skipinitialspace=True)

        for row in filecontents:
            objecturi = row[0]
            principaltype = row[1]
            principalname = row[2]
            accesssetting = row[3].strip()
            if accesssetting.lower().startswith("conditional "):
                accesssetting = accesssetting[len("conditional "):]
            perms = row[4]
            enabled = row[5]
            condition = row[6]

            pattern = str(row)[1:-1]
            pattern = f'{pattern}'

            ## debug ##
            # print('printing pattern: = ' + pattern)
            # print("Creating auth rule for " + objecturi)

            reqval = objecturi
            rule_count += 1

            ## Construct JSON object for this rule
            value_dict_object = {
                "description": "Created by applyviyarules.py",
                "objectUri": reqval,
                "permissions": perms.split(','),
                "principalType": principaltype,
                "principal": principalname,
                "type": accesssetting,
                "enabled": enabled,
                "condition": condition
            }

            constructed_rule_dict_object = {
                "op": "add",
                "value": value_dict_object
            }

            ## create-rules expects an array, so put the single rule
            ## inside a one-element list.
            single_rule_list = [constructed_rule_dict_object]

            ## Each rule gets its own JSON file
            single_rule_json = os.path.join(results_dir, "condrule_" + str(rule_count) + "_" + runtime + ".json")

            with open(single_rule_json, "w") as text_file:
                json.dump(single_rule_list, text_file, indent=2)
                text_file.write('\n')

            print(
                "Printing conditional rule " + str(rule_count) +
                " to: \033[1;34m" + single_rule_json + "\033[0m"
            )

            ## Apply this rule before moving to the next one
            command = (
                clicommand +
                ' authorization create-rules --file "' +
                single_rule_json +
                '"'
            )

            print("Applying conditional rule " + str(rule_count) + "...")
            print("Executing command: " + command)

            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            cli_output = result.stdout or ""
            print(cli_output, end="" if cli_output.endswith("\n") else "\n")

            zero_rules_created = re.search(
                r"\b0\s+rules?\s+were\s+created\.?",
                cli_output,
                flags=re.IGNORECASE
            ) is not None

            if result.returncode != 0 or zero_rules_created:
                if zero_rules_created:
                    failure_reason = "Viya CLI reported that 0 rules were created. The SpEL condition may be invalid."
                else:
                    failure_reason = "Viya CLI returned exit code " + str(result.returncode) + "."

                failed_rules.append({
                    "ruleNumber": rule_count,
                    "failureReason": failure_reason,
                    "cliReturnCode": result.returncode,
                    "cliOutput": cli_output.strip(),
                    "sourceJsonFile": single_rule_json,
                    "rule": constructed_rule_dict_object
                })
                print("\033[1;31mERROR: conditional rule " + str(rule_count) + " was not created.\033[0m")
                print("Reason: " + failure_reason)
            else:
                successful_rule_count += 1
                print("\033[1;32mConditional rule " + str(rule_count) + " applied successfully.\033[0m")

            print()

    if failed_rules:
        with open(failed_rules_json, "w") as text_file:
            json.dump([item["rule"] for item in failed_rules], text_file, indent=2)
            text_file.write('\n')

        with open(failed_rules_csv, "w", newline='') as csv_file:
            fieldnames = ["ruleNumber", "objectUri", "principalType", "principal", "type", "permissions", "enabled", "condition", "failureReason", "cliReturnCode", "cliOutput", "sourceJsonFile"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for item in failed_rules:
                value = item["rule"]["value"]
                writer.writerow({
                    "ruleNumber": item["ruleNumber"],
                    "objectUri": value["objectUri"],
                    "principalType": value["principalType"],
                    "principal": value["principal"],
                    "type": value["type"],
                    "permissions": ",".join(value["permissions"]),
                    "enabled": value["enabled"],
                    "condition": value["condition"],
                    "failureReason": item["failureReason"],
                    "cliReturnCode": item["cliReturnCode"],
                    "cliOutput": item["cliOutput"],
                    "sourceJsonFile": item["sourceJsonFile"]
                })

        print("\033[1;31m" + str(len(failed_rules)) + " conditional rule(s) were not created.\033[0m")
        print("Failed rules JSON: \033[1;34m" + failed_rules_json + "\033[0m")
        print("Failed rules CSV:  \033[1;34m" + failed_rules_csv + "\033[0m")

    print(
        "\033[1;32mFinished processing " + str(rule_count) +
        " conditional rules: " + str(successful_rule_count) + " created, " +
        str(len(failed_rules)) + " failed.\033[0m"
    )

    if failed_rules:
        sys.exit(1)

else:
    print("ERROR: cannot read " + conditionalrules)
