#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getpath.py
# January 2019
#
# Usage:
# getpath.py -u objectURI [-d]
#
# Examples:
#
# 1. Return path of folder identified by objectURI
#        ./getpath.py -u /folders/folders/060c0ea4-07ee-43ea-aa79-a1696b7f8f52
#
# 2. Return path of report identified by objectURI
#        ./getpath.py -u /reports/reports/43de1f98-d7ef-4490-bb46-cc177f995052
#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
import argparse
import sys
import os
from sharedfunctions import getpath, getapplicationproperties

# get python version
version=int(str(sys.version_info[0]))
debug=False

# Define exception handler so that we only output trace info from errors when in debug mode
def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print (exception_type.__name__, exception)

sys.excepthook = exception_handler

parser = argparse.ArgumentParser()
parser.add_argument("-u","--objecturi", help="Object URI of folder or other object that can be contained within a folder.", required=True)
parser.add_argument("-d","--debug", action='store_true', help="Debug")
args = parser.parse_args()
objecturi=args.objecturi
debug=args.debug

path=getpath(objecturi)

if path is not None:
    print (path)
