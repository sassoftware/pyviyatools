#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# setposixattributes.py
# March 2025
#
# Change History
# 18MAR2025 Initial commit
#
# Accepts a CSV file with the following format:
# Column 1: Principal Type (User or Group)
# Column 2: User ID or Group ID
# Column 3: Numeric Override User or Group ID
# Column 4: Numeric Override Primary UID or GID
#
# Example:
# GROUP,HR,99999
# USER,Santiago,9000,9001
# USER,Hugh,8000,8001
# USER,Fay,7000,9001
#
# Copyright © 2025, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either 
#  express or implied. See the License for the specific language governing permissions and limitations under the License.
# 
import argparse
import csv
import os
from sharedfunctions import callrestapi

# setup command-line arguments
parser = argparse.ArgumentParser(description="Set POSIX attributes for User and Group (uid and gid) file format: principal type,principal,id of user or group, primary gid for users")
parser.add_argument("-f", "--file", help="Full path to csv containing posix attributes.", required=True)
parser.add_argument("-d", "--debug", action='store_true', help="Debug")
args = parser.parse_args()
file = args.file
debug = args.debug

# Split the incoming CSV into two, one for groups and one for users, changing the principal type to lower case.
def split_csv(file):
    user_file = file.replace('.csv', '_users.csv')
    group_file = file.replace('.csv', '_groups.csv')
    with open(file, 'r') as infile, open(user_file, 'w', newline='') as user_outfile, open(group_file, 'w', newline='') as group_outfile:
        reader = csv.reader(infile)
        user_writer = csv.writer(user_outfile)
        group_writer = csv.writer(group_outfile)
        for row in reader:
            if row[0].strip().lower() == 'user':
                row[0] = 'user'
                user_writer.writerow(row)
            elif row[0].strip().lower() == 'group':
                row[0] = 'group'
                group_writer.writerow(row)
    return user_file, group_file

user_file, group_file = split_csv(file)

# POST the user file to /identities/users/identifier/loader
reqtype = "post"
reqval = "/identities/users/identifier/loader"
result = callrestapi(reqval, reqtype, file=user_file)
print("User file processed:", result)

# POST the group file to /identities/groups/identifier/loader
reqval = "/identities/groups/identifier/loader"
result = callrestapi(reqval, reqtype, file=group_file)
print("Group file processed:", result)

# Clean up the temporary files
os.remove(user_file)
os.remove(group_file)
print("Temporary files removed.")
