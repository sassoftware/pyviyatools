#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# listcaslibs.py December 2017
#
# listcaslibs an example of how easy it is to build a new tool. This tool is not really needed as you can do this easily with the CLI
# it is here for demo purposes. It lists the caslibs and their details accepting the cas server as a parameter
#
#
# Change History
#
# 27JAN2017 Comments added
# 15OCT2019 Changed endpoint to /dataSources/providers/
#
#
# Copyright © 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either 
#  express or implied. See the License for the specific language governing permissions and limitations under the License.
# 

import argparse 
from sharedfunctions import callrestapi,printresult

# setup command-line arguements. In this block which is common to all the tools you setup what parameters
# are passed to the tool
# the --output parameter is a common one which supports the three styles of output json, simple or csv

parser = argparse.ArgumentParser() 
parser.add_argument("-s","--server", help="The CAS SERVER.",required='True',default="cas-shared-default")
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='csv')
args = parser.parse_args()
casserver=args.server
output_style=args.output

# set the request type
reqtype='get'

# set the endpoint to call
reqval='/dataSources/providers/cas/sources/'+casserver+'/children?&limit=100000'

#make the rest call using the callrestapi function. You can have one or many calls
caslib_result_json=callrestapi(reqval,reqtype)

# example of overriding the columns for csv output
cols=['name','type','path','scope','attributes','description']

# print result accepts
# the json returned
# the output style
# optionally the columns for csv outtput, if you don't pass in columns you get defaults

# You can just print results r post process the results as you need to

printresult(caslib_result_json,output_style,cols)

