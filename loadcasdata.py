#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# loaddatatocas.py
# July2023
#
# load data to cas from a csv
#
#
#  Column 1 caslib
#  Column 2 table name (or *)
#  Column 3 casserver
#
#  You do not need the column names in the first two. If you do want tp include them
#  use --skipfirstrow
#
# caslib, tablename, casserver
# hrdl, *, cas-shared-default
# salesdl, *, cas-shared-default
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
import argparse, csv, os, sys, subprocess
from sharedfunctions import callrestapi, getfolderid, file_accessible, getidsanduris, getapplicationproperties,getclicommand

version=int(str(sys.version_info[0]))

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

if version==2:
    from io import open

# setup command-line arguements
parser = argparse.ArgumentParser(description="Load CAS data: File Format: column1=caslib,column2=tablename,column3=casserver")
parser.add_argument("-f","--file", help="Full path to csv file containing data to load ",required='True')
parser.add_argument("--debug", action='store_true', help="Debug")
parser.add_argument("--skipfirstrow", action='store_true', help="Skip the first row if it is a header.")

if version==2: parser.add_argument("--encoding",default="ascii",help="default is ascii for python2")
else: parser.add_argument("--encoding",default="utf-8",help="default is utf-8 for python3")

args = parser.parse_args()
file=args.file
skipfirstrow=args.skipfirstrow
debug=args.debug
encoding=args.encoding

reqtype="post"

check=file_accessible(file,'r')

# file can be read
if check:

   with open(file, 'rt',encoding=encoding, errors="ignore") as f:

        filecontents = csv.reader(f)

        if skipfirstrow: next(filecontents,None)

        for row in filecontents:

            cols=len(row)

            # skip row and output a message if only 1 column
            if cols>2:

                caslib=row[0].strip()
                tablename=row[1].strip()
                casserver=row[2].strip()
            
                command=clicommand+' --output fulljson cas tables load --caslib="'+caslib+'" --table='+tablename+' --server='+casserver
                print(command)
                subprocess.call(command, shell=True)
            
            else: print("WARNING: too few columns in row, row must have at least three columns: caslib, tablename, and casserver.")

else:
    print("ERROR: cannot read csv file: "+file)

