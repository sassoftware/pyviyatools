#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# comparecontent.py
# Sep 2024
#
#
# Change History
#
# Copyright © 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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

import difflib, argparse, sys

# get python version
version=int(str(sys.version_info[0]))

# get input parameters
parser = argparse.ArgumentParser(description="Compare two content lists.")
parser.add_argument("--file1", help="Enter the first content file.",required='True')
parser.add_argument("--file2", help="Enter the second content file.",required='True')
parser.add_argument("-d","--debug", action='store_true', help="Debug")

args = parser.parse_args()
file1=args.file1
file2=args.file2

with open(file1, 'r') as f1, open(file2, 'r') as f2:
    lines1 = f1.readlines()
    lines2 = f2.readlines()

# check that there is a header line and it matches

if not lines1[0] == lines2[0]:
    print("ERROR: Files must have a matching header line in the first line.")
    sys.exit()  


# Find lines that are in file1 but not in file2
diff1 = difflib.ndiff(lines1, lines2)
only_in_file1 = [line[2:] for line in diff1 if line.startswith('- ')]

# Find lines that are in file2 but not in file1
diff2 = difflib.ndiff(lines1, lines2)
only_in_file2 = [line[2:] for line in diff2 if line.startswith('+ ')]

print("NOTE: compare the content of file1="+file1+" and file2="+file2)
print("NOTE: SUMMARY")
if only_in_file1: print("NOTE: there is nothing in file1 that is not in file2.")
if only_in_file2: print("NOTE: there is nothing in file2 that is not in file1.")
if only_in_file1 or only_in_file2: print("NOTE: DETAILS")
else: print("NOTE: Files ar the same")

if only_in_file1:
    
    print("NOTE: Content in file1 but not in file2:")
    print(lines1[0])
    for line in only_in_file1:
        print(line)



if only_in_file2:
    print("NOTE: Content in file2 but not in file1:")
    print(lines2[0])
    for line in only_in_file2:
        print(line)

