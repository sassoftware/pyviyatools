#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# applyviyarules.py
#
# Reads in a CSV file, converts it to json format and imports into Viya 
#
# Change History
#
# 12Apr23  Initial development
# 11Sept23 Major update - update to the way the script functions to accommodate current issues
#          currently affecting Viya CLI.
#          This script now runs a comparison of existing rules vs new rules being applied,
#          so that only the delta from this comparison is submitted to Viya.
#          (PMCPFR-1363)
#          This script no longer applies rules with conditions attached to them, but issues
#          a warning notifications and splits the rules to alternative CSV file for manual
#          implementation.
#          (PMCPFR-1364)
# 18Oct23  Fixed a bug that was stopping the conditional rules from being filtered off correctly.
# 11Nov26  Changed the dfcondgrants get_groups lookup to search for the terms "conditional" or "grant",
#          instead of just "grant".
# 16Nov26  New functionality: apply conditional rules through integration with applyconditionalrules.py
#          Updated filter to include prohibit rules
#          Removal of all 'temporary section ...' headers/commentary
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
cwd=os.getcwd()
results_dir="applyviyarules_results"
os.makedirs(results_dir, exist_ok=True)

print('\napplyviyarules.py running...\n')

def cleanup():
    try:
        os.system('rm existing_rules.csv existing_rules_verbose.csv')
        sys.exit()
    except:
        sys.exit()



## Runs listrules.py and compiles exisiting_rules.csv
print('Documenting existing rules... \n')
existingrules = './listrules.py ' +'-o csv > existing_rules_verbose.csv'
subprocess.call(existingrules, shell=True)


## Reads in and trims the existing_rules_verbose.csv file into existing_rules.csv
df = pd.read_csv('existing_rules_verbose.csv',usecols=['objectUri','principalType','principal','setting','permissions','enabled','condition'])
df['permissions']=df['permissions'].str[1:-1]
df['permissions']=df['permissions'].str.replace(' ',',')
df= df[['objectUri','principalType','principal','setting','permissions','enabled','condition']]
df['enabled'] = df['enabled'].apply(lambda x:str(x))
df.to_csv('existing_rules.csv', header=False, index=None, quoting=csv.QUOTE_NONNUMERIC)
with open('existing_rules.csv', 'r') as exr:
    csvrow = exr.readlines()
    for line in csvrow:
        rules=line.split("]") 

newrules=os.path.join(results_dir, 'rulesapplied_'+runtime+'.csv')

print("Checking for new rules to apply... \n")
grepcom = f'grep -Fiv -f existing_rules.csv "{file}" > "{newrules}"'
subprocess.call(grepcom, shell=True)

## Sorts the rules by 'grants' and 'conditional grants' and
## send rules containing conditions to 'conditional_rules.csv'
conditionalrules=os.path.join(results_dir, 'conditional_rules_'+runtime+'.csv')
df2 = pd.read_csv(newrules, quoting=csv.QUOTE_ALL, names=['objectUri','principalType','principal','setting','permissions','enabled','condition'])
df2.sort_values(by=['setting'],inplace=True, ascending=False)
df2= df2.fillna("")
df2= df2.groupby('setting')
dfgrants=None
dfcondgrants=None
try:
    dfgrants = pd.concat( 
    [df2.get_group(name) for name in df2.groups
        if str(name).lower() in ("grant", "prohibit")]
    )
except:
    print("There are \033[1;33mNO NEW RULES\033[0m to be applied. \n ")
else:
    mask= dfgrants['condition'] != ""
    dfgrants= dfgrants[~mask]
    print("\033[1;32mFound",len(dfgrants),"\033[0mNEW RULE(S) to be applied \033[1;32mautomatically. \033[0m \n")

try:
    ### 11Nov26 - Update to include 'conditional' when filtering rules
    ###           (the filter includes "grant" to ensure back-compatability with older Supplement docs)
    dfcondgrants = pd.concat(
    [df2.get_group(name) for name in df2.groups
     if str(name).lower() == "grant" or "conditional" in str(name).lower()]
    )
except:
    pass
else:
    mask= dfcondgrants['condition'] != ""
    dfcondgrants= dfcondgrants[mask]
    print("\033[1;32mFound",len(dfcondgrants),"\033[0mNEW CONDITIONAL RULE(S) to be applied. \033[0m\n")

if dfgrants is None and dfcondgrants is None :
    cleanup()


## Loops through the 'dfgrants' file and outputs JSON entries
if dfgrants is not None and not dfgrants.empty:
    for row in dfgrants.itertuples(index=False):
        objecturi = row.objectUri
        principaltype = row.principalType
        principalname = row.principal
        accesssetting = row.setting
        perms = row.permissions
        enabled = row.enabled
        condition = row.condition

        reqval = objecturi

        ## Construct JSON objects from auth rules in dfgrants
        value_dict_object = {
            "description": "Created by applyviyarules.py",
            "objectUri": reqval,
            "permissions": perms.split(','),
            "principalType": principaltype,
            "principal": principalname,
            "type": accesssetting,
            "enabled": str(enabled),
            "condition": condition
        }

        constructed_rule_dict_object = {
            "op": "add",
            "value": value_dict_object
        }

        constructed_bulk_rules_list.append(
            constructed_rule_dict_object
        )


if constructed_bulk_rules_list:

    newrulesjson = os.path.join(
        results_dir,
        'rulesapplied_' + runtime + '.json'
    )

    with open(newrulesjson, "w") as text_file:
        json.dump(
            constructed_bulk_rules_list,
            text_file,
            indent=2
        )
        text_file.write('\n')

    command = (
        clicommand +
        ' authorization create-rules --file ' +
        newrulesjson
    )

    print(f"Applying {len(constructed_bulk_rules_list)} new rules...\n")
    print("Executing command: " + command)

    subprocess.call(command, shell=True)

else:
    newrulesjson = None

## Apply conditional rules using applyconditionalrules.py
if dfcondgrants is not None and not dfcondgrants.empty:
    #print("file = "+file)
    command=os.path.join(cwd, 'applyconditionalrules.py -f ')
    os.system(command+"'"+file+"'")

else:
    pass

if dfgrants is None:
    print(
        "\033[1;32mFinished processing no standard rules (non-conditional) rules have been applied.\033[0m"
        )

elif newrulesjson is not None:
    print("\nStandard rules (non-conditional) rules applied JSON: \033[1;34m"+newrulesjson+"\033[0m")
    print("Standard rules (non-conditional) rules applied CSV: \033[1;34m" +newrules+" \033[0m")
    print(
        "\033[1;32mFinished processing " + str(len(dfgrants)) +
        " standard (non-conditional) rule(s): "+ str(len(dfgrants))+ " new rules applied.\033[0m"
    )
else:
    print(
        "\033[1;32mFinished processing " + str(len(dfgrants)) +
        " standard (non-conditional) rule(s): No new rules applied.\033[0m"
    )

cleanup()
