#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# showsetup.py
# 
# output some system settings to help with debugging issues
#
# October 2018
#
#
# Change History
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

import sys
import requests
import os

from sharedfunctions import getprofileinfo

# software versions
print("Python Version is: "+str(sys.version_info[0])+'.'+str(sys.version_info[1]))
print("Requests Version is: "+requests.__version__)

# profile

cur_profile=os.environ.get("SAS_CLI_PROFILE","NOTSET")

if cur_profile=="NOTSET": 
    print("SAS_CLI_PROFILE environment variable not set, using Default profile")
    cur_profile='Default'
else:
    print("SAS_CLI_PROFILE environment variable set to profile "+ cur_profile)


ssl_file=os.environ.get("SSL_CERT_FILE","NOTSET")

if ssl_file=="NOTSET": 
    print("SSL_CERT_FILE environment variable not set.")
else:
    print("SSL_CERT_FILE environment variable set to profile "+ ssl_file)


r_ssl_file=os.environ.get("REQUESTS_CA_BUNDLE","NOTSET")

if r_ssl_file=="NOTSET": 
    print("REQUESTS_CA_BUNDLE environment variable not set.")
else:
    print("REQUESTS_CA_BUNDLE environment variable set to profile "+ r_ssl_file)

getprofileinfo(cur_profile)
