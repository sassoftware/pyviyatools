#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# updatedomain.py
# November 2018
#
# update a viya domain to add credentials from a csv
# the domain must exist
#
# Change History
#
# 27JAN2017 Comments added   
# 03DEC2018 Strip spaces from the end of users and groups    
#
# csv file format
# no header row
# column1 is userid
# column2 is password
# column3 is identity
# column4 is identity type (user or group)
# For example:
# myuserid,mypass,Sales,group 
# acct1,pw1,Admin,user
# etc
#
# Copyright © 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


# Update a domain

import csv
import base64
import argparse

from sharedfunctions import callrestapi, file_accessible
    
parser = argparse.ArgumentParser(description="Update a Viya Domain to add credentials from a csv file.")
parser.add_argument("-d","--domain", help="Existing Domain.",required=True)
parser.add_argument("-f","--file", help="A csv file containing groups and userids.",required=True)

args = parser.parse_args()

domain_name=args.domain
file=args.file

# check that domain exists
reqval="/credentials/domains/"+domain_name
reqtype="get"

#if domain does not exist call restapi will exit and no additional code is run
domainexist=callrestapi(reqval,reqtype)

type=domainexist['type']

# read the csv file to create json
check=file_accessible(file,'r')

# file can be read
if check:

    with open(file, 'rt') as f:
        filecontents = csv.reader(f)
        for row in filecontents:
            
            #print(row)
            
            userid=row[0]
            pwval=row[1]
            ident=row[2].rstrip()
            identtype=row[3].rstrip()
            
            
            if pwval: cred=base64.b64encode(pwval.encode("utf-8")).decode("utf-8")
            
            if identtype=="group": end_ident="groups"
            if identtype=="user": end_ident="users"
            
            reqval="/credentials/domains/"+domain_name+"/"+end_ident+"/"+ident
            reqtype="put"
    
            data = {}
            data['domainId'] = domain_name
            data['domainType'] = type
            data['identityId'] = ident
            data['identityType'] = identtype
            data['properties']={"userId": userid}
            if pwval:
                data['secrets']={"password": cred}
    
            #print(reqval)
            #print(data)
            
            # make the rest call
            callrestapi(reqval,reqtype,data=data)
else:
    print("ERROR: cannot read "+file)
