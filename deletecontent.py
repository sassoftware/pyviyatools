#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# deletecontent.py
# july 2021
#
# Pass in a folder path and delete the folder and content
# use -i to also delete the folder
# Replaces deletefolderandcontent.py
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

# Import Python modules

import argparse, sys, json

from sharedfunctions import getfolderid, callrestapi

# get python version
version=int(str(sys.version_info[0]))

# get input parameters
parser = argparse.ArgumentParser(description="Delete a folders content")
parser.add_argument("-f","--folderpath", help="Enter the path to the viya folder.",required='True')
parser.add_argument("-i","--includefolder", action='store_true', help="Include folder in delete.")
parser.add_argument("-d","--debug", action='store_true', help="Debug")

parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')

args = parser.parse_args()

path_to_folder=args.folderpath
quietmode=args.quiet
debug=args.debug
includefolder=args.includefolder

# call getfolderid to get the folder id
targets=getfolderid(path_to_folder)

# if the folder is found
if targets[0] is not None:

    uri=targets[1]

    # if quiet do not prompt
    if quietmode:
        areyousure="Y"
    else:

        if version  > 2:
            areyousure=input("Are you sure you want to delete the folder and its contents? (Y)")
        else:
            areyousure=raw_input("Are you sure you want to delete the folder and its contents? (Y)")

    if areyousure.upper() == 'Y':

        #delete folder content, recursive call returns all children
        reqval=uri+"/members?recursive=true&limit=1000000"

        reqtype='get'
        allchildren=callrestapi(reqval,reqtype)

        # get all child items
        if 'items' in allchildren:

            itemlist=allchildren['items']

            folderlist=[]
            contentlist=[]

            #delete child items and if its a folder delete the folder and its content
            for children in itemlist:

                #print(json.dumps(children,indent=2))
                contenttype=children['contentType']

                linklist=children['links']

                for linkval in linklist:
                    #build a list of folders
                    if contenttype=="folder":

                        if linkval['rel']=='deleteResource':
                            deleteUri=(linkval['uri'])
                            folderlist.append(deleteUri)
                    else:

                        if linkval['rel']=='deleteResource':
                            deleteUri=(linkval['uri'])
                            contentlist.append(deleteUri)
                            print("NOTE: Deleting "+children['name']+" of type "+children['contentType']+".")

            # do all non-folders first
            for itemuri in contentlist:
                reqtype='delete'
                callrestapi(itemuri,reqtype)

        #with content gone recusively delete sub-folders of the folder
        reqtype='get'
        reqval=uri+"/members?limit=1000000"
        subfolders=callrestapi(reqval,reqtype)

        if 'items' in subfolders:

           itemlist=subfolders['items']
           #delete child items and if its a folder delete the folder and its content
           for children in itemlist:

               furi=children['uri']
               reqtype='delete'
               reqval=furi+"?recursive=true"
               callrestapi(reqval,reqtype)

        # with content gone recursively delete top folder
        if includefolder:

           print("NOTE: Deleted "+ path_to_folder+" and all sub-folders and content.")
           reqtype='delete'
           reqval=uri+"?recursive=true"
           callrestapi(reqval,reqtype)

        else: print("NOTE: Deleted all content and all sub-folders from "+ path_to_folder)

    else: print("Good thing I asked!")
