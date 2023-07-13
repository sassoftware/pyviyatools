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
#
# Format of input csv file is 2 columns
# Column 1: Object URI
# Column 2: Principal id [<groupID> | <userID> | "authenticatedUsers" | "guest" | "everyone"]
#
# For example:
# "/jobExecution/jobRequests/*","authenticatedUsers"
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

## get cli location from properties
propertylist=getapplicationproperties()

clidir=propertylist["sascli.location"]
cliexe=propertylist["sascli.executable"]
clicommand=os.path.join(clidir,cliexe)


## setup command-line arguements
parser = argparse.ArgumentParser(description="Enables or Disables Viya rules in bulk.")
parser.add_argument("-f","--file", help="Full path to CSV file. Format of csv: 'objecturi,principal",required='True')
parser.add_argument("-o","--operator", help="Option to disable or enable rules", choices=['enable','disable'], required='True')
parser.add_argument("--skipfirstrow", help="Skip first row/header of the input csv file", action='store_true')

args = parser.parse_args()
file=args.file
operator=args.operator
skipfirstrow=args.skipfirstrow

reqtype="post"
check=file_accessible(file,'r')


## Checks for previous unfinished or partial runs and clears tmp files
if os.path.exists('tmpcsv.csv'):
    os.remove('tmpcsv.csv')
else: pass

if os.path.exists('tmpcsv2.csv'):
    os.remove('tmpcsv2.csv')
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
                command = subprocess.check_output(['./getruleid.py', '-u', objecturi, '-p', principal, '-o', 'csv'])
                out.write(command)


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


## Cleans up temporary files
os.system('rm tmpcsv.csv tmpcsv2.csv')


## Compiles and runs the Viya CLI commands to changes the rules' status
with open("ruleids.csv", "r", newline='') as input:
    reader = csv.reader(input)
    for row in reader:
        id=row[0]
        command = clicommand+ ' authorization '+operator+'-rule --id '+id
        print("Executing command: "+command)
        subprocess.call(command, shell=True)
input.close()
