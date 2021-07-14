#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getruleid.py
# December 2017
#
# getruleid pass in a uri and identity and return the rule id
# for example
# getruleid.py -u /SASVisualAnalytics/** -p "authenticatedUsers"
#  or
# getruleid.py -c /folders/folders/dba5473d-afb4-44d4-866a-9671ed5878c2 -p "authenticatedusers"
#
# Change History
#
#  27JAN2017 Comments added
#  18JUN2018 Output JSON
#  20Feb2020 make identity a required parameter
#  14Jul2021 Support getting rules that target container URIs
#
# Copyright © 2018-2021, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
import sys

from sharedfunctions import callrestapi, printresult

debug=False

# Define exception handler so that we only output trace info from errors when in debug mode
def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print "%s: %s" % (exception_type.__name__, exception)

sys.excepthook = exception_handler


# setup command-line arguements
parser = argparse.ArgumentParser()

parser.add_argument("-u","--objecturi", help="objectURI. You must specify either -u objectURI or -c containerURI.")
parser.add_argument("-c","--containeruri", help="containerURI. You must specify either -u objectURI or -c containerURI.")
parser.add_argument("-p","--principal", help="Enter the identity name or authenticatedUsers, everyone or guest",required='True')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='json')

args = parser.parse_args()
objuri=args.objecturi
conturi=args.containeruri
ident=args.principal
output_style=args.output

if objuri and conturi:
  raise Exception('You must specify either -u objectURI or -c containerURI, but not both.')
if objuri is None and conturi is None:
  raise Exception('You must specify either -u objectURI or -c containerURI. You may not specify both.')

if ident.lower()=='authenticatedusers': ident='authenticatedUsers'

if ident=='guest' or ident=='everyone' or ident=='authenticatedUsers':
    if objuri:
        reqval= "/authorization/rules?filter=and(eq(principalType,'"+ident+"'),eq(objectUri,'"+objuri+"'))"
    else:
        reqval= "/authorization/rules?filter=and(eq(principalType,'"+ident+"'),eq(containerUri,'"+conturi+"'))"
else:
    if objuri:
        reqval= "/authorization/rules?filter=and(eq(principal,'"+ident+"'),eq(objectUri,'"+objuri+"'))"
    else:
        reqval= "/authorization/rules?filter=and(eq(principal,'"+ident+"'),eq(containerUri,'"+conturi+"'))"

reqtype='get'

result=callrestapi(reqval,reqtype)

# print rest call results
printresult(result,output_style)
