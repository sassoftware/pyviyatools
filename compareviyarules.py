#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# compareviyarules.py
#
# Extracts all rules from a Viya env and compares them against a CSV file of new rules
#
# Change History
#
# 30Apr26  Initial development
#
# Format of input csv file is 6 columns
# Column 1: Object URI
# Column 2: Principal type ["group" | "user"]
# Column 3: Principal id [<groupID> | <userID>]
# Column 4: Access grant type ["grant" | "prohibit")
# Column 5: Applicable permissions ["read","delete","add","create","remove","secure","update"]
# Column 6: Rule's status ["true" | "false"]
# Column 7: Rule's condition - this column must either be left blank OR contain a SpEL condition.
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
import argparse, csv, os, subprocess, sys, re
import re
import pandas as pd
from datetime import datetime
from sharedfunctions import callrestapi, getfolderid, file_accessible, printresult, getapplicationproperties, getclicommand


## setup command-line arguements
parser = argparse.ArgumentParser(description="Receives bulk auths from a CSV file and compares to what exists")
parser.add_argument("-f","--file", help="Full path to CSV file. Format of csv: 'objecturi,principaltype,principalid,grant_or_prohibit,perms,enabled,condition",required='True')
args = parser.parse_args()
file=args.file

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

reqtype="post"

check=file_accessible(file,'r')
#constructed_bulk_rules_list=[]
runtime = datetime.now().strftime("%Y%m%d_%H%M%S")


print('\ncompareviyarules.py running...\n')


###### Runs a comparison of the file submitted by the user against existing_rules.csv
# Runs listrules.py and compiles exisiting_rules.csv
print('Documenting existing rules and comparing... \n')
existingrules = './listrules.py ' +'-o csv > existing_rules_verbose.csv'
subprocess.call(existingrules, shell=True)

## Reads in and trims the existing_rules_verbose.csv file into existing_rules.csv
df = pd.read_csv('existing_rules_verbose.csv',usecols=['objectUri','containerUri','principalType','principal','setting','permissions','enabled','condition'])
#df.drop(df[df['condition'].notna()].index, inplace=True)
df['permissions']=df['permissions'].str[1:-1]
df['permissions']=df['permissions'].str.replace(' ',',')
df= df[['objectUri','containerUri','principalType','principal','setting','permissions','enabled','condition']]
df['enabled'] = df['enabled'].apply(lambda x:str(x))
df.to_csv('existing_rules.csv', header=False, index=None, quoting=csv.QUOTE_NONNUMERIC)
with open('existing_rules.csv', 'r') as exr:
    csvrow = exr.readlines()
    for line in csvrow:
        rules=line.split("]") 

newrules='rulesdelta_all_'+runtime+'.csv'

grepcom='grep -Fiv -f existing_rules.csv '+'"'+ file +'"' + ' > '+newrules
subprocess.call(grepcom, shell=True)


###### Sorts the rules by 'grants' and 'conditional grants'.
## Send rules containing quotes to a rulesdelta file for manual validation.
missingrules='rulesdelta_grant_'+runtime+'.csv'
conditionalrules='rulesdelta_cond_'+runtime+'.csv'
df2 = pd.read_csv(newrules, quoting=csv.QUOTE_ALL, names=['objectUri','containerUri','principalType','principal','setting','permissions','enabled','condition'])
df2.sort_values(by=['setting'],inplace=True, ascending=False)
df2= df2.fillna("")
df2= df2.groupby('setting')
dfgrants=None
dfcondgrants=None
try:
    dfgrants= df2.get_group("grant")
except:
    print("\033[1;32mALL rules without conditions have been correctly applied. \033[0m\n ")
else:
    mask= dfgrants['condition'] != ""
    dfgrants= dfgrants[~mask]
    dfgrants.to_csv(missingrules, header=False, index=None, quoting=csv.QUOTE_ALL)
    print("\033[1;31mFound",len(dfgrants),"\033[0mMISSING/INCOMPLETE RULE(S). \033[1;31mPlease review these in your Viya environment. \033[0m \n")

try:
    dfcondgrants= df2.get_group("conditional grant")
except:
    print("\033[1;32mALL 'conditional grant' rules are correctly applied. \033[0m\n ")
else:
    mask= dfcondgrants['condition'] != ""
    dfcondgrants= dfcondgrants[mask]
    dfcondgrants.to_csv(open(conditionalrules,'w'), header=False, index=None, quoting=csv.QUOTE_NONNUMERIC)
    print("\033[1;31mFound",len(dfcondgrants),"\033[0mUNCHECKABLE CONDITIONAL RULE(S). \033[1;31mPlease review these in your Viya environment. \033[0m \n")


if dfgrants is not None and dfcondgrants is not None:
    print("Rules to manually validate have been output to: \033[1;34m\n"+missingrules+"\n"+conditionalrules+"\033[0m\n")
elif dfgrants is not None and dfcondgrants is None:
    print("Rules to manually validate have been output to: \033[1;34m\n"+missingrules+"\033[0m\n")
elif dfgrants is None and dfcondgrants is not None:
    print("Rules to manually validate have been output to: \033[1;34m\n"+conditionalrules+"\033[0m\n")
else:
    pass

## Cleans up tmp files
try:
    os.system('rm existing_rules.csv existing_rules_verbose.csv '+newrules)
except:
    pass
