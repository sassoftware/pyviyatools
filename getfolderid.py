#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getfolder.py
# December 2017
#
# getfolderid is a wrapper which sets up the command line arguements and then calls the getfolderid function
# the function returns a folderid and uri when passed the path to the folder in Viya
#
# Change History
#
# 27JAN2017 Comments added  
# 08FEB2020 Added the option to return full json     
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

import argparse

from sharedfunctions import getfolderid, printresult

# setup command-line arguements    
parser = argparse.ArgumentParser()
parser.add_argument("-f","--folderpath", help="Enter the path to the viya folder.",required='True')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='csv')

args = parser.parse_args()
path_to_folder=args.folderpath
output_style=args.output

# call the get folderid function and pass it the entered path
targets=getfolderid(path_to_folder)

# default simple output style prints with original print method
# but can also choose json or csv
if output_style=='simple':

    #print results if any are returned
    if targets[0] is not None:
        print("Id  = "+targets[0])
        print("URI = "+targets[1])
        print("Path = "+targets[2])
else: printresult(targets[3],output_style)