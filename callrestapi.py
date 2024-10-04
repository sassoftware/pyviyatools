#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# callrestapi.py
# December 2017
#
# Based on the items passed in the utility calls the rest api and return results
#
# Change History
#
# 27JAN2017 Comments added
# 29JAN2017 Added choices to validate method input
# 31JAN2017 Added contenttype parameters
# 02FEB2018 Added  simple text print flag
# 01JUN2018 Renamed from call_rest_api.py to callrestapi.py
# 08JUN2018 Print json instead of pprint of easier result parsing
# 01JUN2018 Renamed from call_rest_api.py to callrestapi.py
# 08JUN2018 Print json instead of pprint of easier result parsing
# 08OCT2018 make printed json pretty
# 26OCT2018 call print function
# 20FEB2020 support simplejson
# 16Jul2021 Support for updating the header. (Issue #83)
# 20Feb2022 Support patch

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

from sharedfunctions import callrestapi,getinputjson,printresult

# get command line parameters

parser = argparse.ArgumentParser(description="Call the Viya REST API")
parser.add_argument("-e","--endpoint", help="Enter the REST endpoint e.g. /folders/folders ",required='True')
parser.add_argument("-m","--method", help="Enter the REST method.",default="get",required='True',choices=['get','put','post','delete','patch','head'])
parser.add_argument("-i","--inputfile",help="Enter the full path to an input json file",default=None)
parser.add_argument("-a","--accepttype",help="Enter REST Content Type you want returned e.g application/vnd.sas.identity.basic+json",default="application/json")
parser.add_argument("-c","--contenttype",help="Enter REST Content Type for POST e.g application/vnd.sas.identity.basic+json",default="application/json")
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='json')
parser.add_argument("-t","--text", help="Display Simple Text Results.", action='store_true')
parser.add_argument("-hf","--headerfile",help="Enter the full path to a header json file",default=None)

args = parser.parse_args()

reqval=args.endpoint
reqtype=args.method
reqfile=args.inputfile
reqcontent=args.contenttype
reqaccept=args.accepttype
simpletext=args.text
output_style=args.output
headfile=args.headerfile

# keep for backward compatibility
if simpletext: output_style='simple'

# use the callrestapi function to make a call to the endpoint
# call passing json or not
if reqfile != None and headfile != None:
    inputdata=getinputjson(reqfile)
    headerdata=getinputjson(headfile)
    result = callrestapi(reqval, reqtype, reqaccept, reqcontent, data=inputdata,header=headerdata)
elif reqfile != None:
    inputdata=getinputjson(reqfile)
    result=callrestapi(reqval,reqtype,reqaccept,reqcontent,data=inputdata)
elif headfile != None:
    headerdata=getinputjson(headfile)
    result=callrestapi(reqval,reqtype,reqaccept,reqcontent,header=headerdata)
elif reqtype == 'head':
    result,httpcode=callrestapi(reqval,reqtype,reqaccept,reqcontent)
    print('Response Code:',httpcode)
else:
    result=callrestapi(reqval,reqtype,reqaccept,reqcontent)

#print the result
printresult(result,output_style)
