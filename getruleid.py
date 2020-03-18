#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getruleid.py
# December 2017
#
# getruleid pass in a uri and identity and return the rule id
# for example
# getruleid.py -u /SASVisualAnalytics/** -p "authenticatedUsers" 
#
# Change History
#
#  27JAN2017 Comments added 
#  18JUN2018 Output JSON  
#  20Feb2020 make identity a required parameter
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
parser = argparse.ArgumentParser()

parser.add_argument("-u","--objecturi", help="Enter the objecturi.",required='True')
parser.add_argument("-p","--principal", help="Enter the identity name or authenticatedUsers, everyone or guest",required='True')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='json')

args = parser.parse_args()
objuri=args.objecturi
ident=args.principal
output_style=args.output

if ident.lower()=='authenticatedusers': ident='authenticatedUsers'

if ident=='guest' or ident=='everyone' or ident=='authenticatedUsers':
    reqval= "/authorization/rules?filter=and(eq(principalType,'"+ident+"'),eq(objectUri,'"+objuri+"'))"
else:
    reqval= "/authorization/rules?filter=and(eq(principal,'"+ident+"'),eq(objectUri,'"+objuri+"'))"

reqtype='get'

result=callrestapi(reqval,reqtype)

# print rest call results
printresult(result,output_style)
