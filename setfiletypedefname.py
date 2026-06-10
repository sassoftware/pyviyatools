#!/usr/bin/env python3

# setfiletypedefname.py June 2026

# This tool locates all files named "*.sas" that do not have a typeDefName of "programFile", and updates the typeDefName to "programFile".
# When this is set incorrectly, in SAS Environment Manager's Content page, the context menu item "Open SAS Program" is not available.
# For a single object, you could also use the "setobjectattribute.py" tool:
# ./setobjectattribute.py -u /files/files/file-id -a typeDefName -v programFile

import argparse
from sharedfunctions import callpagedrestapi, callrestapi
from datetime import datetime as dt

parser = argparse.ArgumentParser()
parser.add_argument("--filter", help="Set a custom filter for objects, for example eq(createdBy,sasdemo).")
parser.add_argument("--write", help="Make the specified changes.", action="store_true", default=False)
args = parser.parse_args()

# Set the request type
reqtype = 'get'

# Set the endpoint to call
if args.filter:
    reqval = "/files/files?filter=and(endsWith(name,'.sas'),not(contains(typeDefName,'programFile'))," + args.filter + ")"
else:
    reqval = "/files/files?filter=and(endsWith(name,'.sas'),not(contains(typeDefName,'programFile')))"

print('Calling REST endpoint:',reqval)

# Make the rest call using the callpagedrestapi function.
results=callpagedrestapi(reqval,reqtype)

# Capture the count attribute from the query and print it out.
if results is not None:
    if 'count' in results:
        count=results['count']
    else:
        count=len(results)
else:
    count=0

print('Found',count,'matching our query.')

if results is not None and count > 0:
    if args.write:
        for item in results:
            # I can use PATCH but my body needs to include the "name" and "searchable" fields as well, and I need to use the If-Match or If-Unmodified-Since header.
            # Get the URI, name, searchable, and modifiedTimeStamp attributes for the item.
            uri = item.get('links')[0].get('href')
            name = item.get('name')
            searchable = item.get('searchable')
            modified = item.get('modifiedTimeStamp')
            # Modified is in the form 2025-09-16T21:00:58.656Z, but for the header I need to convert it to something like Fri, 16 Sep 2025 21:00:58 GMT
            modified = modified.replace('T', ' ').replace('Z', '')
            modified = dt.strptime(modified, '%Y-%m-%d %H:%M:%S.%f')
            modified = modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
            currenttype = item.get('typeDefName')
            print('Updating typeDefName for file:',name,'from',currenttype,'to "programFile" with uri:',uri)
            patchbody = {
                "name": name,
                "searchable": searchable,
                "typeDefName": "programFile"
            }
            headers = {
                "If-Unmodified-Since": modified
            }
            reqtype = 'patch'
            callrestapi(uri,reqtype,data=patchbody,header=headers)
    else:
        print('No changes made. To update the typeDefName to "programFile" for the above files, re-run with the --write flag.')
        # Print a table of the names and URIs of the files that would be updated.
        print("{:<50} {:<100}".format('Name', 'URI'))
        for item in results:
            name = item.get('name')
            uri = item.get('links')[0].get('href')
            print("{:<50} {:<100}".format(name, uri))
else:
    print('No results returned from query.')
