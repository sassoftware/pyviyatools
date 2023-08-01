#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# toggleviyarules.py
#
# Reads in a CSV file, looks up the rule IDs and either disables or enables the rule 
#
# Change History
#
# 15May23 Initial development
# 25May23 First release
# 01AUG23 Major update - rule replacement functionality added
#
#
# Basic Usage
# >> Disables or enables rules read from a CSV file input.
#
# > Example:
# toggleviyarules.py -f <input_csv.csv> -o {disable|enable}
#
#
# Advanced Usage:
# >> Disables rules read from a CSV file input, whilst skipping the first row,
# >> then creates new copies (replacements) the same rules for a principal (user or group)
# >> specified with the -p and -ptype flags.
#
# > Example:
# toggleviyarules.py -f <input_csv.csv> -o replace -p <PRINCIPAL> -ptype <PRINCIPALTYPE> --skipfirstrow
#
#
# Input CSV format requirements:
# Column 1: Object URI
# Column 2: Principal id [<groupID> | <userID> | "authenticatedUsers" | "guest" | "everyone"]
#
# >> Example:
# "/jobExecution/jobRequests/*","authenticatedUsers"
#
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
import subprocess
import sys
from sharedfunctions import callrestapi, getfolderid, file_accessible, printresult, getapplicationproperties

## Get cli location from properties
propertylist=getapplicationproperties()

clidir=propertylist["sascli.location"]
cliexe=propertylist["sascli.executable"]
clicommand=os.path.join(clidir,cliexe)


## Setup command-line arguements
parser = argparse.ArgumentParser(description="Enables or Disables Viya rules in bulk.")
parser.add_argument("-f","--file", help="Full path to CSV file. Format of csv: 'objecturi,principal",required='True')
parser.add_argument("-o","--operator", help="Option to enable, disable or replace rules", choices=['enable','disable','replace'], required='True')
parser.add_argument("--skipfirstrow", help="Skip first row/header of the input csv file", action='store_true')
parser.add_argument("-p","--princ", help="Requires operator option \'replace\'. Sets the principal (account/group) name to be used for the replacement copies of the rules being applied.")
parser.add_argument("-ptype","--princtype", help="Requires operator option \'replace\'. Sets the principal TYPE to be used for the replacement copies of the rules being created and applied.", choices=['group','user','guest','authenticated-users','everyone'])


args = parser.parse_args()
file=args.file
skipfirstrow=args.skipfirstrow
## Set new vars based on operator arg input
if args.operator == 'replace':
    operator='disable'
    replaceop='replace'
else:
    operator=args.operator
    replaceop="None"

reqtype="post"
check=file_accessible(file,'r')


## Checks for previous unfinished or partial runs and clears tmp or old files
if os.path.exists('tmpcsv.csv'):
    os.remove('tmpcsv.csv')
else: pass

if os.path.exists('tmpcsv2.csv'):
    os.remove('tmpcsv2.csv')
else: pass

if os.path.exists("replacementrules.csv"):
    os.remove("replacementrules.csv")
else: pass


## Checks that file can be read
if check:
    with open(file, 'rt') as f:
        filecontents = csv.reader(f)
        ## Skips first row if arg has been parsed
        if skipfirstrow: next(filecontents,None)
        ## Retrieves the rule ID values using getruleid.py
        for row in filecontents:
            objecturi=row[0]
            principal=row[1]
            with open('tmpcsv.csv', 'ab') as out:
                commandcsv = subprocess.check_output(['./getruleid.py', '-u', objecturi, '-p', principal, '-o', 'csv'])
                out.write(commandcsv)
            with open('tmptxt.txt', 'ab') as out:
                commandtxt = subprocess.check_output(['./getruleid.py', '-u', objecturi, '-p', principal, '-o', 'simple'])
                out.write(commandtxt)


## Removes the header lines that are returned when getruleid.py is run
with open("tmpcsv.csv", "r") as input, open("tmpcsv2.csv", "w") as tmpout:
    for line in input:
        # only keep lines which begin with a quote
        if line.startswith('"'):
            tmpout.write(line)


## Cycles the csv file to keep just the rule ID values
with open('tmpcsv2.csv') as input, open('ruleids.csv', "w") as output:
    reader = csv.reader(input)
    for row in reader:
        output.write(row[0] + "\n")
print("Writing out bulk rule IDs to ruleids.csv")


## Compiles and runs the Viya CLI commands to change the rules' status
with open("ruleids.csv", "r", newline='') as input:
    reader = csv.reader(input)
    for row in reader:
        id=row[0]
        command = clicommand+ ' authorization '+operator+'-rule --id '+id
        print("Executing command: "+command)
        subprocess.call(command, shell=True)
input.close()


#### Optional sub-section for the 'replace' operator's functions
if replaceop == 'replace': 

    ## Validates arguments being parsed in
    if args.princtype is None:
        parser.error("When using --operator \'replace\' --princtype must also be set")

    if args.princ is None and (args.princtype in ('group', 'user')):
        parser.error("When using --princtype \'group\' or \'user\' a principal (user or group name) must be set using --princ")
    elif args.princ is not None and (args.princtype in ('group', 'user')):
        principaltype=args.princtype
        replaceprinc=args.princ
    else:
        principaltype="--"+str(args.princtype)
        replaceprinc=args.princ


    ## Reads in the tmptxt.txt file created in earlier section, and formats the output into single rows
    with open('tmptxt.txt') as rulesin, open ('tmptxt2.txt', 'w') as rulesout:
        for line in rulesin:

            if line.startswith(('condition', 'objectUri', 'permissions')):
                if line.startswith("condition"):
                    condition=line.replace('condition =  ','')
                    condition=condition.replace('\n','')
                    rulesout.write("found:"+f'"{condition}"'+',')
                elif line.startswith("objectUri"):
                    uri=line.strip("objectUri =  ").replace('\n','')
                    rulesout.write(uri+',')           
                elif line.startswith("permissions"):
                    perms=line.strip("permissions =  ").replace(' ','')
                    perms=perms.replace('\'','')
                    perms=perms[1:-2]
                    rulesout.write(f'"{perms}"\n')


    ## Secondary if statements which reformat the rows produced in tmptxt2.txt
    ## This is required to format the CSV with non-conditional (standard) rules.
    with open('tmptxt2.txt') as rulesin2, open ('rulesout.txt', 'w') as rulesout2:
        for line in rulesin2:
            if line.startswith("found:"):
                newline=line.replace("found:",'')
                rulesout2.write(newline)
            else:
                rulesout2.write("\"\","+line)


    ## Compiles the rulesout.txt file into a new CSV file in a format to be consumed by applyviyarules.py
    with open ('rulesout.txt', 'r') as f:
        newrules = csv.reader(f)
        for row in newrules:
            condition=f'"{row[0]}"'
            objecturi=f'"{row[1]}"'
            permissions=f'"{row[2]}"'
            with open ('replacementrules.csv', 'a') as newcsv:
                rule=objecturi+','+principaltype+','+replaceprinc+',grant,'+permissions+',True,'+condition+'\n'
                newcsv.write(rule)
            input.close()


    ## Runs applyviyarules.py with CSV entries found in replacementrules.csv
    applycommand = './applyviyarules.py '+'-f '+'replacementrules.csv'
    subprocess.call(applycommand, shell=True)

    
    ## Cleans up tmp files created by this optional sub-section only
    os.system('rm tmptxt2.txt rulesout.txt replacementrules.csv')


## Cleans up tmp files
os.system('rm tmpcsv.csv tmpcsv2.csv tmptxt.txt ruleids.csv')
