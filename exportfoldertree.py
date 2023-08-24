#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# exportfoldertree.py
# March 2018
#
# Pass in a directory and this tool will export the complete viya folder
# structure to a sub-directory named for the current date and time
# There will be a json file for each viya folder at the root level.
#
#
# Change History
#
# SEP2022 Added option to specify the root folder to start at
# MAR2023 Option to remove transfer objects and some general cleanup
# AUG2023 Option to suppress the incremental number suffix on downloaded file names 
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
import argparse, sys, subprocess, uuid, time, os, glob, json

from sharedfunctions import getfolderid, callrestapi,getapplicationproperties

# get python version
version=int(str(sys.version_info[0]))

# get cli location from properties
propertylist=getapplicationproperties()

clidir=propertylist["sascli.location"]
cliexe=propertylist["sascli.executable"]

clicommand=os.path.join(clidir,cliexe)

# get input parameters
parser = argparse.ArgumentParser(description="Export the complete Viya folder tree or the members of a folder to a set of Viya Packages.")
parser.add_argument("-d","--directory", help="Directory to store Export Packages",required='True')
parser.add_argument("-f","--folder", help="Folder to start export at (root is default)",default="NONE")
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')
parser.add_argument("-t","--tranferremove", help="Remove transfer package from SAS Viya after download to JSON file", action='store_true')
parser.add_argument("-n","--nonincrament", help="Do not add an incremental number at the end of the downloaded JSON file ", action='store_true')
args= parser.parse_args()

basedir=args.directory
folder=args.folder
quietmode=args.quiet
autotranferremove=args.tranferremove
nonincrament=args.nonincrament


# prompt if directory exists because existing json files are deleted
if os.path.exists(basedir):

    # if the quiet mode flag is not passed then prompt to continue
    if not quietmode:

        if version  > 2:
            areyousure=input("The folder exists any existing json files in it will be deleted. Continue? (Y)")
        else:
            areyousure=raw_input("The folder already exists any existing json files in it will be deleted. Continue? (Y)")
    else:
        areyousure="Y"

else: areyousure="Y"

# prompt is Y if user selected Y, its a new directory, or user selected quiet mode
if areyousure.upper() =='Y':

    path=basedir

    # create directory if it doesn't exist
    if not os.path.exists(path): os.makedirs(path)
    else:
        filelist=glob.glob(path+"/*.json")
        for file in filelist:
            os.remove(file)
    
    reqtype='get'

    # folder = NONE means the root folder
    # also if user passes in root
    if folder !='NONE' and folder !='/':

        # get members of folder passed in
        folderinfo=getfolderid(folder)
        results=(folderinfo[3])
        folderid=results["id"]
        reqval='/folders/folders/'+folderid+'/members'
    
    else:
       # retrieve root folders
       reqval='/folders/rootFolders'
    
    resultdata=callrestapi(reqval,reqtype)

    print(json.dumps(resultdata,indent=2))

    # loop root folders
    if 'items' in resultdata:

        total_items=resultdata['count']
        allitems=resultdata['items']
        
        if total_items == 0: print("Note: No items returned.")
        else:
            # export each folder and download the package file to the directory
            i=0
            for theitem in allitems:

                i=i+1
                
                if folder=='NONE' or folder=='/':

                   # get id for root folders and build URI	
                   id=theitem["id"]
                   folderuri='/folders/folders/'+id
                else:
                   
                   #get uri if not root folders
                   folderuri=theitem["uri"]

                # generate a unique name for the package in the Infrastructure Data Server
                package_name=str(uuid.uuid1())
                if nonincrament:
                    json_name=theitem["name"].replace(" ","")
                else:
                    json_name=theitem["name"].replace(" ","")+'_'+str(i)

                # export
                command=clicommand+' transfer export -u '+folderuri+' --name "'+package_name+'"'
                print(command)
                subprocess.call(command, shell=True)

                # use the unique name to get the package and download it to a JSON file
                reqval='/transfer/packages?filter=eq(name,"'+package_name+'")'
                package_info=callrestapi(reqval,reqtype)
                package_id=package_info['items'][0]['id']
                
                # download exported package
                completefile=os.path.join(path,json_name+'.json')
                command=clicommand+' transfer download --file '+completefile+' --id '+package_id
                print(command)
                subprocess.call(command, shell=True)

                # if -t set then remove transfer package from infrastructure data server after download
                if autotranferremove:
                    print(clicommand+' transfer delete --id '+package_id+"\n")
                    remTransferObject = subprocess.Popen(clicommand+' transfer delete --id '+package_id, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
                    remTransferObjectOutput = remTransferObject.communicate(b'Y\n')
                    remTransferObject.wait()

    print("NOTE: Viya folders exported to json files in "+path)

else:
     print("NOTE: Operation cancelled")

