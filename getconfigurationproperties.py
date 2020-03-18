#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getconfigurationproperties.py
# December 2017
#
# pass in the coniguration definition and return the properties
#
# Change History
#
# 27JAN2017 Comments added
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


# Import Python modules
from __future__ import print_function
import argparse
import pprint
pp = pprint.PrettyPrinter(indent=4)

from sharedfunctions import callrestapi, printresult

    
parser = argparse.ArgumentParser(description="Return a set of configuration properties")
parser.add_argument("-c","--configuration", help="Enter the configuration definition.",required='True')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='json')

args = parser.parse_args()
configurationdef=args.configuration
output_style=args.output

reqval="/configuration/configurations?definitionName="+configurationdef

configvalues=callrestapi(reqval,'get')

printresult(configvalues,output_style)
   
