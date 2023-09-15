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
#
# Format of input csv file is 6 columns
# Column 1: Object URI
# Column 2: Principal type ["group" | "user"]
# Column 3: Principal id [<groupID> | <userID>]
# Column 4: Access grant type ["grant" | "conditional grant" | "prohibit")
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
from sharedfunctions import callrestapi, getfolderid, file_accessible, printresult, getapplicationproperties


## get cli location from properties
propertylist=getapplicationproperties()

clidir=propertylist["sascli.location"]
cliexe=propertylist["sascli.executable"]
clicommand=os.path.join(clidir,cliexe)


## setup command-line arguements
parser = argparse.ArgumentParser(description="Apply bulk auths from a CSV file to folders and contents")
parser.add_argument("-f","--file", help="Full path to CSV file. Format of csv: 'objecturi,principaltype,principalid,grant_or_prohibit,perms,enabled,condition",required='True')
args = parser.parse_args()
file=args.file

reqtype="post"

check=file_accessible(file,'r')
constructed_bulk_rules_list=[]
runtime = datetime.now().strftime("%Y%m%d_%H%M%S")


#newrules=file
print('\napplyviyarules.py running...\n')

##########################################################
## Temporary section 1
##########################################################
## Runs a comparison of the file submitted by the user against existing_rules.csv
## This section may be removed once PMCPFR-1363 is resolved.

## Runs listrules.py and compiles exisiting_rules.csv
print('Documenting existing rules... \n')
existingrules = './listrules.py ' +'-o csv > existing_rules_verbose.csv'
subprocess.call(existingrules, shell=True)

#pd.set_option('display.max_columns', None)

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

newrules='rulesapplied_'+runtime+'.csv'

print("Checking for new rules to apply... \n")
print("Printing results (CSV format) to: \033[1;34m"+newrules+"\033[0m \n")
grepcom='grep -Fiv -f existing_rules.csv '+'"'+ file +'"' + ' > '+newrules
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
conditionalrules='conditional_rules_'+runtime+'.csv'
df2 = pd.read_csv(newrules, quoting=csv.QUOTE_ALL, names=['objectUri','principalType','principal','setting','permissions','enabled','condition'])
df2.sort_values(by=['setting'],inplace=True, ascending=False)
df2= df2.fillna("")
df2= df2.groupby('setting')
dfgrants=None
dfcondgrants=None
try:
    dfgrants= df2.get_group("grant")
except:
    print("There are \033[1;33mNO NEW RULES\033[0m to be applied. \n ")
else:
    mask= dfgrants['condition'] != ""
    dfgrants= dfgrants[~mask]
    dfgrants.to_csv(newrules, header=False, index=None, quoting=csv.QUOTE_ALL)
    print("\033[1;32mFound",len(dfgrants),"\033[0mNEW RULE(S) to be applied \033[1;32mautomatically. \033[0m \n")

try:
    dfcondgrants= df2.get_group("conditional grant")
except:
    pass
else:
    mask= dfcondgrants['condition'] != ""
    dfcondgrants= dfcondgrants[mask]
    dfcondgrants.to_csv(open(conditionalrules,'w'), header=False, index=None, quoting=csv.QUOTE_NONNUMERIC)
    print("\033[1;32mFound",len(dfcondgrants),"\033[0mNEW CONDITIONAL RULE(S) to be applied \033[1;31mmanually. \033[0m \n")

if dfgrants is None and dfcondgrants is None :
    sys.exit()
##########################################################
# End of Temporary section 2
##########################################################


## Loops through the 'newrules' file and converts the CSV rows into JSON entries
if check:
    with open(newrules, 'r') as f:
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

## This if/else statement can be removed and the following section dedented
## once PMCPFR-1364 is resolved.
if dfgrants is not None:
    newrulesjson='rulesapplied_'+runtime+'.json'
    print("Printing new rules (JSON format) to: \033[1;34m" +newrulesjson+" \033[0m \n")

    ## Construct JSON schema containing rules
    bulk_rules_list_string=json.dumps(constructed_bulk_rules_list,indent=2)
    with open(newrulesjson, "w") as text_file:
        text_file.write(bulk_rules_list_string+'\n')

    ## Execute sas-admin CLI to apply rules from JSON schema
    command=clicommand+' authorization create-rules --file '+newrulesjson
    print("Applying new rules...\n")
    print("Executing command: "+command)
    subprocess.call(command, shell=True)

else:
    pass

##########################################################
# Temporary section 3
##########################################################
## Prints a note to inform the user that the conditional
## rules have been output to a CSV file and NOT applied.
## This section may be removed once PMCPFR-1364 is resolved.
if dfcondgrants is not None:
    print(
     '''
     !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
     !!!                                    !!!
     !!!\033[1;31m    IMPORTANT NOTE - PLEASE READ\033[0m    !!!
     !!!                                    !!!
     !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
     Due to a known issue currently affecting
     the Viya CLI, it is recommended that all
     Viya rules that include a condition/
     conditional grant, be implemented manually
     through SAS Environment Manager interface.

     A list of rules for manual implementation
     has been output to:

     ''')
    print('     \033[1;33m'+conditionalrules+'\033[0m')
    print(
     '''

     (September 2023 - PMCPFR-1364)

     '''
              )
else:
    print("\n\033[1;33mNo conditional rules found in: "+file+"\033[0m")
##########################################################
# End of Temporary section 3
##########################################################

## Cleans up tmp files
try:
    os.system('rm existing_rules.csv existing_rules_verbose.csv')
except:
    pass
