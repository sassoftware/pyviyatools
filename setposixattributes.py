#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# setposixidentity.py
# April 2022
#
# sets the posix attributes of a user similar to the Linux "id" command
#
# Format of csv file is three columns no header
# Column 1 userid
# Column 2 numeric override uid
# Column 3 numeric override primary gid
#
# For example:
#Santiago,9000,9001
#Hugh,8000,8001
#Fay,7000,9001
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

import argparse
import csv
import os

from sharedfunctions import printresult, callrestapi, file_accessible

# setup command-line arguements
parser = argparse.ArgumentParser(description="Display POSIX attributes for User")

parser.add_argument("-f","--file", help="Full path to csv containing posix attribute override settings",required='True')
parser.add_argument("-d","--debug", action='store_true', help="Debug")
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='json')

args = parser.parse_args()
file=args.file
debug=args.debug
output_style=args.output

reqtype="put"
# set the endpoint to call

check=file_accessible(file,'r')

# file can be read
if check:

    with open(file, 'rt') as f:
        
        filecontents = csv.reader(f)
        for row in filecontents:
        
            
            user=row[0]
            uid=row[1]
            gid=row[2]
            secgids=row[3]

            reqval='/identities/users/'+user+"/identifier"
            
            # build the json
            data = {}
            data['username'] = user
            data['gid'] = gid
            data['uid'] = uid
            
            # print debug info
            if debug: 
                
                print(reqval)
                print(row)
                print(data)
                
            reqaccept='application/vnd.sas.identity.identifier+json'

            #make the rest call using the callrestapi function. You can have one or many calls
            user_info_result_json=callrestapi(reqval,reqtype,data=data)
          
            print("NOTE: Finished Processing "+file)
else:
    print("ERROR: "+file+" not available.")