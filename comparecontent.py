#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# comparecontent.py
# Sep 2024
#
# This script compares two content files and reports the differences.
# It checks for a matching header line and lists content that is unique to each file.
# It is designed to be run from the command line with two file arguments.
# you can use it to compare the content of two runs of listcontent.py or liscaslib.py.
# Typically, you would run this script after making changes to content files to see what has changed.
# It uses the difflib module to find differences between the two files.
# usage: python comparecontent.py --file1 <path_to_file1> --file2 <path_to_file2> [--label1 <label1>] [--label2 <label2>] [-d|--debug]
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
parser.add_argument("-f1","--file1", help="Enter the full path to the first content file.",required='True')
parser.add_argument("-f2","--file2", help="Enter the full path to the second content file.", required='True')
parser.add_argument("-f1l","--file1label", help="Optional label for the first file being compared.", default="First file.")
parser.add_argument("-fl2","--file2label", help="Optional label for the second file being compared.", default="Second file.")
parser.add_argument("-d","--debug", action='store_true', help="Debug")

args = parser.parse_args()
file1=args.file1
file2=args.file2
label1=args.file1label
label2=args.file2label

with open(file1, 'r') as f1, open(file2, 'r') as f2:
    lines1 = f1.readlines()
    lines2 = f2.readlines()

# check that there is a header line and it matches

if not lines1[0] == lines2[0]:
    print("ERROR: Files must have a matching header line in the first line.")
    sys.exit()  

# Find lines that are in file1 but not in file2, and vice versa
diff = difflib.ndiff(lines1, lines2)
# Find lines that are in file1 but not in file2
only_in_file1 = [line[2:] for line in diff if line.startswith('- ')]
# Find lines that are in file2 but not in file1
diff = difflib.ndiff(lines1, lines2)
only_in_file2 = [line[2:] for line in diff if line.startswith('+ ')]

print("NOTE: Compare the content of file1 (" + label1 + ") and file2 (" + label2 + ")")

print("NOTE: SUMMARY")
if only_in_file1: print("NOTE: There is content in file1 (" + label1 + ") that is not in file2 (" + label2 + ").")
if only_in_file2: print("NOTE: There is content in file2 (" + label2 + ") that is not in file1 (" + label1 + ").")

if only_in_file1 or only_in_file2:
    print("NOTE: DETAILS")
else:
    print("NOTE: Files are the same.")

if only_in_file1:
    
    print("NOTE: The content listed below is in file1 (" + label1 + ") but not in file2 (" + label2 + "):")
    print(lines1[0])
    for line in only_in_file1:
        print(line)

if only_in_file2:
    print("NOTE: The content listed below is in file2 (" + label2 + ") but not in file1 (" + label1 + "):")
    print(lines2[0])
    for line in only_in_file2:
        print(line)
    print(lines2[0])
    for line in only_in_file2:
        print(line)


