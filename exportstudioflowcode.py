#!/usr/bin/python

# -*- coding: utf-8 -*-
#
# exportstudioflowcode.py
# Feb 2022
#
# create a code from SAS Studio flows
#
# Change History
#
#

import argparse, os, sys, json

from sharedfunctions import callrestapi, getfolderid

# write code function
def writecode():

    if debug: print(data)

    reqval="/studioDevelopment/code"
    reqtype="post"
    flow_json=callrestapi(reqval,reqtype,data=data,stoponerror=0,noprint=1)

    # if code is returned then output to file
    if flow_json !=None:

        code=flow_json['code']
    
        if os.path.exists(basedir):
            # remove / from path
            filename=flow_name.split('.')[0].replace("/","_")
            file=os.path.join(basedir,filename+'.sas')

            print("NOTE: SAS Code output to "+file)

            with open(file, "w") as outfile:
                    outfile.write(code)

        else: 
            print("ERROR: output directory does not exist.")
            sys.exit()
    
    else:
        print("WARNING: code cannot be generated for "+flow_name)

# get python version
version=int(str(sys.version_info[0]))

# get arguements
parser = argparse.ArgumentParser(description="Create code from a SAS Studio flow or from all flows in folder.")
parser.add_argument("-t","--type", help="Enter 'Flow' for a single flow or 'Folder' for all flows in a folder.",required=True,choices=['Flow','Folder'])
parser.add_argument("-n","--name", help="Name of Flow or Folder Path.",required=True)
parser.add_argument("-d","--directory", help="Directory to store generated code",required='True')

parser.add_argument("--includeinitcode", help="Include init code (default False)",action='store_true')
parser.add_argument("--includewrappercode", help="Include wrapper code (default False)",action='store_true')
parser.add_argument("--debug", help="Include wrapper code (default False)",action='store_true')

args = parser.parse_args()
basedir=args.directory
type=args.type
debug=args.debug

# user passed in a single flow
if type=="Flow":

    flow_name=args.name

    # build the json parameters
    data = {}
    reference={}
    data["reference"]=reference
    reference["type"]="content"
    reference['path']=flow_name
    reference['mediaType']="application/vnd.sas.dataflow"
    data['initCode'] = args.includeinitcode
    data['wrapperCode']= args.includewrappercode

    # run the request and get the code
    writecode()

else:

    # user passed in a folder, loop and output code for the flows in the folder
    folder_path=args.name
    print("NOTE: creating code for flows in folder "+folder_path) 
    targets=getfolderid(folder_path)

    # if the folder is found
    if targets[0] is not None: uri=targets[1]
    else:
        print("ERROR: Folder does not exist.")
        sys.exit()

    reqval=uri+"/members?&limit=100000"
    reqtype='get'

    folder_members=callrestapi(reqval,reqtype)

    items=folder_members["items"]

    if len(items)==0:
        print("NOTE: folder is empty.")
        sys.exit()
    
    count=0
    
    # loop folder members
    for itemlist in items:

        ctype=itemlist["contentType"]
        flow_name=folder_path+"/"+itemlist["name"]
       
        if ctype=="dataFlow":

            # write out code from each flow
            data = {}
            reference={}
            data["reference"]=reference
            reference["type"]="content"
            reference['path']=flow_name
            reference['mediaType']="application/vnd.sas.dataflow"
            data['initCode'] = args.includeinitcode
            data['wrapperCode']= args.includewrappercode
          
            writecode()
        
        else:
            count=count+1
        
    if count > 0: print("NOTE: No flows in folder.")









    





l