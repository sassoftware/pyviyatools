#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# listrules.py
# August 2018
#
# listrulesforidentity  
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

import argparse

from sharedfunctions import callrestapi, printresult

# setup command-line arguements    
parser = argparse.ArgumentParser(description="List rules for a principal and/or an endpoint")

parser.add_argument("-u","--uri", help="Enter a string that the objecturi contains.",default="none")
parser.add_argument("-p","--principal", help="Enter the identity name or authenticatedUsers, everyone or guest",default='none')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple'],default='json')

args = parser.parse_args()
objuri=args.uri
ident=args.principal
output_style=args.output

# set the limit high so that all data is returned
limitval=10000

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
result=callrestapi(reqval,reqtype)

#print the result
printresult(result,output_style)

