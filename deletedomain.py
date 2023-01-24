#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# deletedomain.py
# January 2023
#
# delete a domain
#
# Change History
#
#  20JAN2023 Initial Build   

#
# Copyright Â© 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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

# Delete a domain

import base64, argparse, sys

from sharedfunctions import callrestapi

# get python version
version=int(str(sys.version_info[0]))
    
parser = argparse.ArgumentParser(description="Delete a Viya Domain")
parser.add_argument("-d","--domain", help="Enter the domain name.",required=True)
parser.add_argument("-t","--type", help="Type of the domain: password, oauth2.0 (token), connection (passwordless) or encryption.",required=True, choices=['password','connection','oauth2.0','cryptDomain'])
args = parser.parse_args()

domain_name=args.domain
type=args.type

if domain_name.isalnum()==False:
  print("ERROR: Domain name must be alpha-numeric.")
  quit()

# check the type matches the existing domain
reqval="/credentials/domains/"+domain_name
reqtype="get"
test_result_json=callrestapi(reqval,reqtype)

resp_id=test_result_json["id"]

if 'description' in test_result_json:
   resp_desc=test_result_json["description"]
else: resp_desc=''

resp_type=test_result_json["type"]

print('Found the domain with ID:' +resp_id+ ', description:' +resp_desc+ ', and type:' +resp_type)
print("")

if resp_type != type:
  print ('ERROR: The returned domain does not match the type you specified.')
  quit()

else:
  
  if resp_type == 'cryptDomain':
    
    print ('##########################################################')
    print ('CAUTION: YOU ARE ATTEMPTING TO DELETE AN ENCRYPTION DOMAIN')
    print ('##########################################################')
    print ('Libraries associated with this domain will need to be recreated if the domain is deleted.')
    print ("")
    
    
    if version  > 2:
      check_delete = input('Are you sure you want to delete the encryption domain? (Yes/No):')
    else:
      check_delete = raw_input('Are you sure you want to delete the encryption domain? (Yes/No):') 
    
    if check_delete == 'Yes':
      
      print ('NOTE: Deleting encryption domain: '+resp_id)
      reqval="/credentials/domains/"+domain_name+"?includeCredentials=true"
      reqtype="delete"
      
      callrestapi(reqval,reqtype)
    
    else:
      print ('NOTE: NOT Deleting encryption domain: '+resp_id)
  
  else:
    
    if version  > 2:
      check_delete = input('Are you sure you want to delete the domain? (Yes/No):')
    else:
      check_delete = raw_input('Are you sure you want to delete the domain? (Yes/No):') 
    
    if check_delete == 'Yes':
      
      print ('NOTE: Deleting Domain: '+resp_id)
      reqval="/credentials/domains/"+domain_name+"?includeCredentials=true"
      reqtype="delete"
      
      callrestapi(reqval,reqtype)
    else:
      print ('NOTE: NOT Deleting domain: '+resp_id)





