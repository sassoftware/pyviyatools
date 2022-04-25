#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# setposixidentity.py
# April 2022
#
# sets the posix attributes of a user 
#
# Format of csv file is three columns no header
# Column 1 Principal Type (User or Group)
# Column 2 userid or group
# Column 3 numeric override user or group
# Column 4 numeric override primary uid or gid
#
# For example:
#GROUP,HR,99999
#USER,Santiago,9000,9001
#USER,Hugh,8000,8001
#USER,Fay,7000,9001
#
# Copyright © 2022, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
parser = argparse.ArgumentParser(description="Set POSIX attributes for User and Group (uid and gid) file format: principal type,principal,id of user or group, primary gid for users")

parser.add_argument("-f","--file", help="Full path to csv containing posix attributes.",required='True')
parser.add_argument("-d","--debug", action='store_true', help="Debug")

args = parser.parse_args()
file=args.file
debug=args.debug

# put request
reqtype="put"

# check that the csv file exist and can be read
check=file_accessible(file,'r')

# file can be read
if check:

    with open(file, 'rt') as f:
        
        # loop the csv file and set the attributes
        filecontents = csv.reader(f)
        for row in filecontents:
        
            # column1 is principal type, column 2 is principal, column3 is id column3 is gid for user
            
            principal_type=row[0]
            principal=row[1]
            id=row[2]

            if principal_type.upper()=="USER":

                gid=row[3]
                
                #request
                reqval='/identities/users/'+principal+"/identifier"
                # build the json
                data = {}
                data['gid'] = gid
                data['uid'] = id
                print("NOTE: Upating Posix Attributes for "+principal_type+" "+principal+": uid= "+id+", gid= "+gid)
                
            elif principal_type.upper()=="GROUP":     
                #request
                reqval='/identities/groups/'+principal+"/identifier"
                data = {}
                data['gid'] = id
                print("NOTE: Upating Posix Attributes for "+principal_type+" "+principal+": gid= "+id)

            else:
                print("ERROR: principal type is "+principal_type+" for principal "+principal+". P rincipal type (column1 in csv) must be USER or GROUP.")

            reqaccept='application/vnd.sas.identity.identifier+json'

            #make the rest call using the callrestapi function. 
            user_info_result_json=callrestapi(reqval,reqtype,data=data,stoponerror=0)
         
          
        print("NOTE: Finished Processing "+file)
else:
    print("ERROR: "+file+" not available.")