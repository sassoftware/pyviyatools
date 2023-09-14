#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# listrules.py
# August 2018
#
# listrules  
#
# Change History
# December 2018 - Added custom CSV output code, which writes out consistent columns in a specific order for the result rules JSON
# January 2019 - Added 'id' to list of desired output columns
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

from sharedfunctions import callrestapi, printresult

# setup command-line arguements    
parser = argparse.ArgumentParser(description="List rules for a principal and/or an endpoint")

parser.add_argument("-u","--uri", help="Enter a string that the objecturi contains.",default="none")
parser.add_argument("-p","--principal", help="Enter the identity name or authenticatedUsers, everyone or guest",default='none')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='json')

args = parser.parse_args()
objuri=args.uri
ident=args.principal
output_style=args.output

# set the limit high so that all data is returned
limitval=10000

# Define columns we want to output for each rule item (whether the item has a value for that column or not)
desired_output_columns=['objectUri','containerUri','principalType','principal','setting','permissions','description','reason','createdBy','createdTimestamp','modifiedBy','modifiedTimestamp','condition','matchParams','mediaType','enabled','version','id']
valid_permissions=['read','update','delete','secure','add','remove','create']

# build the request depending on what options were passed in
if ident.lower()=='authenticatedusers': ident='authenticatedUsers'

if ident=='none' and objuri=='none': reqval= "/authorization/rules"
elif ident=='none' and objuri != 'none': reqval= "/authorization/rules?filter=contains(objectUri,'"+objuri+"')"
elif ident!='none' and objuri == 'none':
    if ident=='guest' or ident=='everyone' or ident=='authenticatedUsers':
        reqval= "/authorization/rules?filter=eq(principalType,'"+ident+"')"
    else:
        reqval= "/authorization/rules?filter=eq(principal,'"+ident+"')"
elif ident!='none' and objuri != 'none':
    
    if ident=='guest' or ident=='everyone' or ident=='authenticatedUsers':
        reqval= "/authorization/rules?filter=and(eq(principalType,'"+ident+"'),contains(objectUri,'"+objuri+"'))"
    else:
        reqval= "/authorization/rules?filter=and(eq(principal,'"+ident+"'),contains(objectUri,'"+objuri+"'))"

if ident=='none' and objuri=='none': reqval=reqval+'?limit='+str(limitval)
else: reqval=reqval+'&limit='+str(limitval)

reqtype='get'

#make the rest call
rules_result_json=callrestapi(reqval,reqtype)

#print(rules_result_json)
#print('rules_result_json is a '+type(rules_result_json).__name__+' object') #rules_result_json is a dict object

#print the result if output style is json or simple
if output_style in ['json','simple']:
  printresult(rules_result_json,output_style)
elif output_style=='csv':
  # Print a header row
  print(','.join(map(str,desired_output_columns)))
  if 'items' in rules_result_json:
    #print "There are " + str(rules_result_json['count']) + " rules"
    for item in rules_result_json['items']:
      outstr=''
      #print(item)
      for column in desired_output_columns:
        # Add a comma to the output string, even if we will not output anything else, unless this is the very first desired output column
        if column is not desired_output_columns[0]: outstr=outstr+','
        if column=='setting':
          # The setting value is derived from two columns: type and condition.
          if 'condition' in item:
            #print("Condition found")
            outstr=outstr+'conditional '+item['type']
          else:
            outstr=outstr+item['type']
        elif column in item:
          # This column is in the results item for this rule
          # Most columns are straight strings, but a few need special handling
          if column in ['condition','description','reason']:
            # The these strings can have values whcih contain commas, need we to quote them to avoid the commas being interpreted as column separators in the CSV
            outstr=outstr+'"'+item[column]+'"'
          elif column=='permissions':
            # Construct a string listing each permission in the correct order, separated by spaces and surrounded by square brackets
            outstr=outstr+'['
            permstr=''
            # Output permissions in the order we choose, not the order they appear in the result item
            for permission in valid_permissions:
              for result_permission in item['permissions']:
                if permission == result_permission:
                  # Add a space to separate permissions if this isn't the first permission
                  if not permstr=='': permstr=permstr+' '
                  permstr=permstr+result_permission
            outstr=outstr+permstr+']'
          else:
            # Normal column
            # Some columns contain non-string values: matchParams and enabled are boolean, version is integer. Convert everything to a string.
            outstr=outstr+str(item[column])
      print(outstr)
else:
  print ("output_style can be json, simple or csv. You specified " + output_style + " which is invalid.")

