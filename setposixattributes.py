#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# setposixidentity.py
# April 2022
#
# sets the posix attributes of a user 
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
parser = argparse.ArgumentParser(description="Set POSIX attributes for User (uid and gid) file format: user,uid,gid")

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
        
            # column1 is user, column2 is uid column3 is gid
            user=row[0]
            uid=row[1]
            gid=row[2]
            
            #request
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
            
            print("NOTE: Upating Posix Attributes for "+user+": uid= "+uid+", gid= "+gid)
                
            reqaccept='application/vnd.sas.identity.identifier+json'

            #make the rest call using the callrestapi function. 
            user_info_result_json=callrestapi(reqval,reqtype,data=data,stoponerror=0)
         
          
        print("NOTE: Finished Processing "+file)
else:
    print("ERROR: "+file+" not available.")