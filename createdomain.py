#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# createdomain.py
# December 2017
#
# create a viya domain
#
# Change History
#
#  27JAN2017 Comments added    
#  27JAN2017 Added the ability to create connection domains
#  29JAN2017 Added choices to validate type of domain  
#  29SEP2018 make group list comma seperated 
#

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

# Create a domain

import base64
import argparse

from sharedfunctions import callrestapi
    
parser = argparse.ArgumentParser(description="Create a Viya Domain")
parser.add_argument("-d","--domain", help="Enter the domain name.",required=True)
parser.add_argument("-u","--user", help="User ID for the domain.",required=True)
parser.add_argument("-p","--password", help="Password for the userid.",required=False)
parser.add_argument("-g","--groups", help="A list of groups to add to the domain. Groupid comma seperated",required=True)
parser.add_argument("-c","--desc", help="Description of the domain.",required=False)
parser.add_argument("-t","--type", help="Type of the domain: password or connection (passwordless).",required=True, choices=['password','connection'])

args = parser.parse_args()

domain_name=args.domain
userid=args.user
pwval=args.password
groups=args.groups
desc=args.desc
type=args.type

# create a python list with the groups
grouplist=groups.split(",")

# encode the password
if pwval:
  cred=base64.b64encode(pwval.encode("utf-8")).decode("utf-8")

# build the rest call
reqval="/credentials/domains/"+domain_name
reqtype="put"

# build the json parameters
data = {}
data['id'] = domain_name
data['description'] = desc
data['type'] = type

# create the domain
callrestapi(reqval,reqtype,data=data)

# for each group passed in add their credentials to the domain
for group_id in grouplist:
    print("Adding "+ group_id + " to domain " + domain_name)

    reqval="/credentials/domains/"+domain_name+"/groups/"+group_id
    reqtype="put"

    data = {}
    data['domainId'] = domain_name
    data['domainType'] = type
    data['identityId'] = group_id
    data['identityType'] = 'group'
    data['properties']={"userId": userid}
    if pwval:
      data['secrets']={"password": cred}

    print(data)

    callrestapi(reqval,reqtype,data=data)


