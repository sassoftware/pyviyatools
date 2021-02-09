#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# exportfolder.py
# Feb 2021
#
# Pass in a folder and this tool will  export the folder to a apcakge
#
#
# Change History
#
#
# Copyright Â© 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
import argparse, sys, subprocess, uuid, time, os, glob

from sharedfunctions import getfolderid, callrestapi, getapplicationproperties, printresult

# get python version
version=int(str(sys.version_info[0]))

# get cli location from properties
propertylist=getapplicationproperties()

clidir=propertylist["sascli.location"]
cliexe=propertylist["sascli.executable"]

clicommand=os.path.join(clidir,cliexe)

# get input parameters
parser = argparse.ArgumentParser(description="Export a Viya Folder and its sub-folders")

parser.add_argument("-f","--folderpath", help="Folder path to export",required='True')
parser.add_argument("-d","--directory", help="Directory for Export",required='True')
parser.add_argument("--filename", help="File name without extension. Optional, default name is the folder path.",default="XNOFILENAMEX")



parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')
args= parser.parse_args()

folderpath=args.folderpath
basedir=args.directory
filename=args.filename

quietmode=args.quiet


# prompt if directory exists because existing json files are deleted
if os.path.exists(basedir):

        # if the quiet mode flag is not passed then prompt to continue
        if not quietmode:

                if version  > 2:
                        areyousure=input("The folder exists any existing json files pf the same naew will be overwritten. Continue? (Y)")
                else:
                        areyousure=raw_input("The folder exists any existing json files pf the same naew will be overwritten. Continue? (Y)")
        else:
                areyousure="Y"

else: areyousure="Y"

# prompt is Y if user selected Y, its a new directory, or user selected quiet mode
if areyousure.upper() =='Y':

        path=basedir

        # create directory if it doesn't exist
        if not os.path.exists(path): os.makedirs(path)

        folderinfo=getfolderid(folderpath)

        results=(folderinfo[3])

        printresult(results,'JSON')
        id=results["id"]

        package_name=str(uuid.uuid1())


        json_name=folderpath.replace("/","_")
        if filename !="XNOFILENAMEX" : json_name=filename

        command=clicommand+' transfer export -u /folders/folders/'+id+' --name "'+package_name+'"'
        print(command)
        subprocess.call(command, shell=True)

        reqtype='get'
        reqval='/transfer/packages?filter=eq(name,"'+package_name+'")'
        package_info=callrestapi(reqval,reqtype)
        package_id=package_info['items'][0]['id']
        completefile=os.path.join(path,json_name+'.json')
        command=clicommand+' transfer download --file '+completefile+' --id '+package_id
        print(command)
        subprocess.call(command, shell=True)


        print("NOTE: Viya folder "+folderpath+ "  exported to json file "+completefile)

else:
         print("NOTE: Operation cancelled")

