#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# changeimportloc.py
# December 2024
#
# Transforms relevant objects and values of an exported json file to
# to enable the exported content to be imported (or promoted) into
# an specific Viya folder, (initially only /Public is an option).
#
# Change History
# 29NOV2024 Initial release
# 02DEC2024 Restructure of Stage 2 and 3 to plug scenario gaps
#
#
# Copyright © 2024, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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

## Defines colours
green='\033[1;32;40m'
white='\033[1;37;40m'
red='\033[1;31;40m'
cyan='\033[1;36;40m'
yellow='\033[1;33;40m'

## Import Python modules
import argparse, sys, json, os
import pip
from pathlib import Path


### Pre-req checks
## Numpy
try:
    import numpy as np
except ModuleNotFoundError:
    print(red,"ERROR: The 'numpy' module is not installed, please install this to your local system and try again.",white)
    exit()
 
## Python 3.4+
versionmajor=int(str(sys.version_info[0]))
versionminor=int(str(sys.version_info[1]))
sysvers=(sys.version)
if versionmajor < 3 or versionminor < 4:
    print(red,"\nERROR: Python version 3.4, or above, is required for this script to run.\n\nThe Python currently in use is:\n\n" 
          + cyan + sysvers + white)
    exit()


## Defines variables
cwd = Path.cwd() # Sets current working dir.
objArr=np.array([], dtype='int16') #used in Stage 1
objCount=0 #used in Stage 1
hrefobj=0 #used in Stage 3
uriobj=0 #used in Stage 3


## Presents input options/arguments    
parser = argparse.ArgumentParser(description="Modifies exported VA report json file to having /Public as it's source location")
parser.add_argument("-f","--file", help="Enter the path to the source file.",required='True')
parser.add_argument("-o","--outputdir", help="Enter the destination path for file/s output.",default=cwd)
args = parser.parse_args()

source=args.file
outdir=args.outputdir

## Defines Viya output location for report being transformed
## (could be made dynamic in the future, currently hardcoded for the values of /Public set on all Viya 4 environments)
ftarget=('/Public')
ftargeturi=('/folders/folders/751063da-3eea-4b1c-be09-dd55fd3c15c9')
ftargetid=('751063da-3eea-4b1c-be09-dd55fd3c15c9')
ftargetname=('Public')

## Formats the input json's file and resolves collapsed dirs
source=Path(source)
source=source.resolve()

## Validates that the input file has a .json file extension
if  Path(source).match('*.json', case_sensitive=None) == False:
    print(red,"ERROR: A valid json file is required for this script to function. Please check your input file and try again.",white)
    exit()

## Read in JSON file
with open(source, 'r') as f:  
    data = json.load(f)

## DEBUG: For reviewing json file content that's been parsed in
#print(json.dumps(data, indent = 4, sort_keys=False))

##########################
######  FUNCTIONS   ######
##########################
                                                                 
## +++ objectcount()                                                
## Counts objects directly underneath 'transferDetails' of a json   
## file read in to the variable "data". It should be run at the     
## start of every Stage, and after a 'del(data[...' command is run. 
def objectcount():
    global count
    count=0
    for obj in data['transferDetails']:
        count += 1

## +++ setitr()                                                      
## Sets the 'itr' variable to '0'.                                  
def setitr():
    global itr
    itr=0




##########################
######  Begin STAGE 1 ####
##########################
## Loops and scans through all 'transferObject' objects and removes all objects of
## "type": "folder", EXCEPT for one.
####
objectcount()
setitr()

for count in data['transferDetails']:
    try:
        
        if data['transferDetails'][itr]['transferObject']['summary']['type'] == "folder" and data['transferDetails'][itr]['connectors'][0]['type'] == "parentFolder":
            ## DEBUG
            #print('\niteration= ',s1itr)
            #print(data['transferDetails'][s1itr]['transferObject']['summary']['type'])
            #print(data['transferDetails'][s1itr]['connectors'][0]['type'])
            objArr=np.append(objArr,itr,axis=None)
            itr += 1
        else:
            itr += 1
    except IndexError:
        itr = itr+1
        pass

for obj in objArr:
    objCount += 1
    
for obj in objArr:
    try:
        objCount -= 1
        ## DEBUG
        #print('deleting iteration = ',objArr[objCount])
        del(data['transferDetails'][objArr[objCount]])        
    except IndexError:
        pass

print(cyan,"\nDELETED object(s):\n",white,objArr.size,"x \'transferObject(s)\' and \'connector(s)\'")
##########################
######  End STAGE 1 ######
##########################




##########################
######  Begin STAGE 2 ####
##########################
## Loops and scan the remaining 'transferObject' object that has a 'folder' value and makes updates.
##
## Updates 'name' to variable 'ftargetname'
## Updates 'id' to variable 'ftargetid'
####
objectcount()
setitr() 

for count in data['transferDetails']:
    try:
        if data['transferDetails'][itr]['transferObject']['summary']['type'] == "folder":
            origname = data['transferDetails'][itr]['transferObject']['summary']['name']
            origid1 = data['transferDetails'][itr]['transferObject']['summary']['id']
            changedname=(cyan+"\nCHANGED 'transferObject' --> 'summary' --> 'name' object: \n"+white+origname+ " --> "+ftargetname+"\n")
            changedid=(cyan+"\nCHANGED 'transferObject' --> 'summary' --> 'id' object: \n"+white+origid1+ " --> "+ftargetid)
            nochangedname=(yellow+"\nNO CHANGE required to 'transferObject' --> 'summary' --> 'name' ("+origname+")\n")
            nochangedid=(yellow+"\nNO CHANGE required to 'transferObject' --> 'summary' --> 'id' ("+origid1+")\n")
            if origname != ftargetname or origid1 != ftargetid:
                if origname != ftargetname and origid1 != ftargetid:
                    origid2 = origid1
                    origname = ftargetname
                    origid1 = ftargetid
                    print(changedname, changedid)
                    itr += 1
                elif origname != ftargetname and origid1 == ftargetid:
                    origid2 = origid1
                    origname = ftargetname
                    print(changedname, nochangedid)
                    itr += 1
                elif origname == ftargetname and origid1 != ftargetid:
                    origid2 = origid1
                    origid1 = ftargetid
                    print(nochangedname, changedid)
                    itr += 1
                else:
                    origid2 = origid1
                    print(nochangedname, nochangedid)                    
                    itr += 1
            else:
                origid2 = origid1
                print(nochangedname,'\n', nochangedid)
                itr += 1
        else:
            itr += 1  

    except IndexError:
        itr += 1
        pass            
##########################
######  End STAGE 2 ######
##########################




##########################
######  Begin STAGE 3 ####
##########################
## Searches for the sole 'transferObject' of type 'folder' (as per outcome of STAGE 1), and
## makes updates to nested objects within this object.
####

## Finds and replaces of the object's references to 'origid2', within the nested 'href' object, to 'ftargetid'
objectcount()
setitr()

if origid2 == ftargetid:
    print(yellow+"\nNO CHANGE required to 'connectors' --> 'links' --> 'href' objects"+white+"\n")
    print(yellow+"\nNO CHANGE required to 'connectors' --> 'links' --> 'uri' objects"+white+"\n")
else:  
    print(cyan,"\nCHANGED \"href\" value(s):",white)
    for count in data['transferDetails']:
        try:
            doesexist=data['transferDetails'][itr]['transferObject']['summary']['links'][hrefobj]
        except IndexError:
            pass

        if data['transferDetails'][itr]['transferObject']['summary']['type'] == "folder" and origid2 != ftargetid:
            try:
                if origid2 in data['transferDetails'][itr]['transferObject']['summary']['links'][hrefobj]['href']:
                    orighref=data['transferDetails'][itr]['transferObject']['summary']['links'][hrefobj]['href']
                    data['transferDetails'][itr]['transferObject']['summary']['links'][hrefobj]['href']=data['transferDetails'][itr]['transferObject']['summary']['links'][hrefobj]['href'].replace(origid2,ftargetid)
                    print(orighref,"-->",data['transferDetails'][itr]['transferObject']['summary']['links'][hrefobj]['href'])
                    hrefobj += 1
                else:
                    hrefobj = 0
                    itr += 1
            except IndexError:
                pass
        else:
            itr += 1

## Finds and replaces of the object's references to 'origid2', within the nested 'uri' object, to 'ftargetid'
    setitr() 

    print(cyan,"\nCHANGED \"uri\" value(s):",white)
    for count in data['transferDetails']:
        try:
            doesexist=data['transferDetails'][itr]['transferObject']['summary']['links'][uriobj]
        except IndexError:
            pass
        
        if data['transferDetails'][itr]['transferObject']['summary']['type'] == "folder":
            try:
                if origid2 in data['transferDetails'][itr]['transferObject']['summary']['links'][uriobj]['uri']:
                    origuri=data['transferDetails'][itr]['transferObject']['summary']['links'][uriobj]['uri']
                    data['transferDetails'][itr]['transferObject']['summary']['links'][uriobj]['uri']=data['transferDetails'][itr]['transferObject']['summary']['links'][uriobj]['uri'].replace(origid2,ftargetid)            
                    print(origuri,"-->",data['transferDetails'][itr]['transferObject']['summary']['links'][uriobj]['uri'])
                    uriobj += 1
                else:
                    uriobj = 0
                    itr += 1
            except IndexError:
                pass
        else:
            itr += 1        
##########################        
######  End STAGE 3 ######
##########################




##########################
######  Begin STAGE 4 ####
##########################        
## Loops and scans through all remaining (non 'folder') 'transferObject' objects making updates
####

##########################
####    Begin Part A  ####
##########################
## Updates 'contentSourceLocation' to variable 'ftarget'
####
objectcount()
setitr()

print(cyan,"\nCHANGED \"contentSourceLocation\" value(s):",white)
for count in data['transferDetails']:
    try:
        if 'contentSourceLocation' in data['transferDetails'][itr]['transferObject']:
            if data['transferDetails'][itr]['transferObject']['contentSourceLocation'] != ftarget:
                origcsl = data['transferDetails'][itr]['transferObject']['contentSourceLocation']
                data['transferDetails'][itr]['transferObject']['contentSourceLocation'] = ftarget
                print(origcsl+ " --> " + ftarget)
                itr += 1                
            else:
                print("\nNo change to 'contentSourceLocation' required.")
                itr += 1 
        else:
            itr += 1 
    except IndexError:
        pass
##########################
####    End Part A    ####
##########################

        
##########################
####    Begin Part B  ####
##########################
## Updates 'uri' to variable 'ftargeturi'
## Updates 'name' to variable 'ftargetname'
####
objectcount()
setitr()

print(cyan,"\nCHANGED \"connectors\" > \"uri\" & \"name\" value(s) of non-folder objects:",white)
for count in data['transferDetails']:
    try:        
        doesexist=data['transferDetails'][itr]['connectors'][0]['uri']
    except IndexError:
        itr += 1
    try:
        if data['transferDetails'][itr]['transferObject']['summary']['type'] != "folder":
            if data['transferDetails'][itr]['connectors'][0]['uri'] != ftargeturi:
                origuri = data['transferDetails'][itr]['connectors'][0]['uri']
                data['transferDetails'][itr]['connectors'][0]['uri'] = ftargeturi
                print(origuri+ " --> " + ftargeturi)
            else:
                print("No change to \"connectors\" -> \"uri\" required.")

            if data['transferDetails'][itr]['connectors'][0]['name'] != ftargetname:
                origname = data['transferDetails'][itr]['connectors'][0]['name']
                data['transferDetails'][itr]['connectors'][0]['name'] = ftargetname
                print(origname+ " --> " + ftargetname)
            else:
                print("No change to \"connectors\" -> \"name\" required.")
            itr += 1
                
        else:
            itr +=1
    except IndexError:
        pass
##########################
####    End Part B    ####
##########################

##########################        
######  End STAGE 4 ######
##########################




##########################
######  Begin STAGE 5 ####
########################## 
## Writes out transformed json content to a new json file
####
    
# Remove absolute location and file extension
source=source.stem

# Append filename to outdir location
jsonout=Path(outdir, source)

# Add custom suffix
jsonout=jsonout.with_suffix('.modified.json')

# Write out JSON file
with open(jsonout, 'w') as f:
    json.dump(data, f, indent = 2, sort_keys=False)

print(cyan,"\n\nJOB COMPLETE - new json file written to: \n\n",green,jsonout,white)
##########################        
######  End STAGE 5 ######
########################## 
