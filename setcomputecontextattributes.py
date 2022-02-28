#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# setcomputecontextattributes.py
# February 2022
#
# Set compute context attributes, adding, changing and removing as required.
#
#
# Change History
#
# Copyright © 2022, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
#  OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
#
#
# Import Python modules
import argparse, sys, os, json
from sharedfunctions import callrestapi #, getbaseurl, getauthtoken
#import requests

debug=True

# Define exception handler so that we only output trace info from errors when in debug mode
def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print "%s: %s" % (exception_type.__name__, exception)

sys.excepthook = exception_handler



# ###########################################################
# def callrestapiwithetag(reqval, reqtype, acceptType='application/json', contentType='application/json',data={},stoponerror=1,returnEtag=False,etagIn=''):

#     # get the url from the default profile
#     baseurl=getbaseurl()

#     # get the auth token
#     oaval=getauthtoken(baseurl)

#     # build the authorization header
#     head= {'Content-type':contentType,'Accept':acceptType}
#     head.update({"Authorization" : oaval})
#     # If an etag was passed in, add an If-Match header with that etag as the value
#     if etagIn!='':
#          head.update({"If-Match" : etagIn})

#     # maybe this can be removed
#     global result

#     # sereliaze the data string for the request to json format
#     json_data=json.dumps(data, ensure_ascii=False)

#     # call the rest api using the parameters passed in and the requests python library

#     if reqtype=="get":
#         ret = requests.get(baseurl+reqval,headers=head,data=json_data)
#     elif reqtype=="post":
#         ret = requests.post(baseurl+reqval,headers=head,data=json_data)
#     elif reqtype=="delete":
#         ret = requests.delete(baseurl+reqval,headers=head,data=json_data)
#     elif reqtype=="put":
#         ret = requests.put(baseurl+reqval,headers=head,data=json_data)
#     else:
#         result=None
#         print("NOTE: Invalid method")
#         sys.exit()


#     # response error if status code between these numbers
#     if (400 <= ret.status_code <=599):

#        print(ret.text)
#        result=None
#        if stoponerror: sys.exit()

#     # return the result
#     else:
#          # is it json
#          try:
#              result=ret.json()
#          except:
#             # is it text
#             try:
#                 result=ret.text
#             except:
#                 result=None
#                 print("NOTE: No result to print")

#     # Capture the value of any etag returned in the headers
#     etagOut=None
#     if 'etag' in ret.headers:
#         etagOut=ret.headers['etag']

#     # ONLY if the user specifically asked for an etag to be returned, return one
#     if returnEtag:
#         return result,etagOut;
#     else:
#         # Otherwise, return only the result as normal
#         return result;

# ###########################################################

# get input parameters
parser = argparse.ArgumentParser(description="Add attributes to an existing compute context.")
parser.add_argument("-n","--name", help="Compute context name",required='True')
parser.add_argument("-a","--add", help="Single attribute to add or update.", nargs="?",const="")
parser.add_argument("-v","--value", help="Value to set attribute to. Only has any effect if you also specify an attribute to add.", nargs="?",const="")
parser.add_argument("-r","--remove", help="Single attribute to remove. If the compute context does not have this attribute, nothing happens.", nargs="?",const="")
args= parser.parse_args()
contextname=args.name
attrToAdd=str(args.add)
attrValue=str(args.value)
attrToRemove=str(args.remove)

if attrToAdd != "None":
    if attrValue == "None":
        raise Exception('If you specify an attribute to add or update, you must also specify a value using -v or --value.')
    if attrToRemove != "None":
        raise Exception('If you specify an attribute to add or update, do not also specify an attribute to remove in the same command. Add and remove attributes with separate calls to this utility.')
else:
    if attrToRemove == "None":
        raise Exception('You must specify either:\n    - an attribute to add or update with -a and a value to set it to with -v, or\n    - an attribute to remove with -r.')

if attrToRemove != "None":
    if attrValue != "None":
        print('Note: You specified an attribute to remove, but also specified a value. The value will be ignored; the specified attribute will be removed whatever value it has.')

# get python version
#version=int(str(sys.version_info[0]))
#print("Python version: " + str(version))

# Get compute contexts
reqtype="get"
reqval="/compute/contexts/?filter=eq(name, '"+contextname+"')"
resultdata=callrestapi(reqval,reqtype)
#json_formatted_str = json.dumps(resultdata, indent=2)
#print(json_formatted_str)


if 'items' in resultdata:
    #print(resultdata['items'])
    if resultdata['items']==[]:
        id=None
        raise Exception("Compute context '"+contextname+"' not found.")
    elif len(resultdata['items'])>1:
        id=None
        raise Exception("More than one matching compute context named '"+contextname+"'.!")
    # If we make it this far, we found exactly one compute context
    for i in resultdata['items']:
        id=i['id']
        #print("Compute context: "+contextname+" ["+id+"]")
else:
    id=None
    # Handle the error! Compute context not found...
    raise Exception('Compute context not found.')

if id!=None:

    boolUpdateRequired=False

    # Get the details of this compute context
    reqtype="get"
    reqval="/compute/contexts/"+id
    # reqaccept="application/vnd.sas.compute.context.summary+json"
    # reccontent="application/vnd.sas.collection+json"
    resultdata,etag=callrestapi(reqval,reqtype,returnEtag=True)
    print("etag: "+etag)
    # Get rid of parts of the context we don't need
    # resultdata.pop("links",None)
    # resultdata.pop("creationTimeStamp",None)
    # resultdata.pop("modifiedTimeStamp",None)
    # resultdata.pop("version",None)
    json_formatted_str = json.dumps(resultdata, indent=2)
    print(json_formatted_str)

    # The following set of logic expects and assumes that EITHER:
    #   attrToAdd has a value, indicating that we are adding/updating a value, and attrToRemove has a value of None, or
    #   attrToRemove has a value, indicating that we are removing a value, and attrToAdd has a value of None.
    # They should not BOTH be None.
    # They should not BOTH have values that are not None.
    # To put it another way, one of them should have a value of None, the other must not.

    boolFoundAttribute=False
    if 'attributes' in resultdata:
        # numattributes=len(resultdata['attributes'])
        # print('numattributes='+str(numattributes))
        # print(resultdata['attributes'])
        # print(type(resultdata['attributes']))

        for attributeKey, attributeValue in resultdata['attributes'].items():
            print("Attribute: "+attributeKey+" : "+attributeValue)

            if attrToAdd != "None":
                # We are adding or updating a value
                if attrToAdd == attributeKey:
                    # We found the value - we are being asked to update the value of an existing attribute
                    boolFoundAttribute=True
                    if attrValue == attributeValue:
                        # No change to value for existing attribute
                        print("Attribute: "+attributeKey+" already has value: "+attributeValue+", it will not be updated")
                    else:
                        # Update value for existing attribute
                        print("Attribute: "+attributeKey+" : "+attributeValue+" to be updated to "+attrValue)
                        resultdata['attributes'][attributeKey]=attrValue
                        boolUpdateRequired=True
            if attrToRemove != "None":
                # Instead, we are removing a value
                if attrToRemove == attributeKey:
                    # We found the value to remove
                    boolFoundAttribute=True
                    print("Attribute: "+attributeKey+" : "+attributeValue+" to be removed")
                    if len(resultdata['attributes'].items())==1:
                        # We are about to remove the only attribute
                        # Remove the whole attributes dictionary
                        resultdata.pop("attributes",None)
                    else:
                        # We are about to remove an attribute, but it is not the last one
                        # Remove this specific attribute from the 'attributes' dictionary
                        resultdata['attributes'].pop(attrToRemove,None)
                    boolUpdateRequired=True
        if not boolFoundAttribute:
            if attrToAdd != "None":
                # We are adding an attribute, and we did not find an existing attribute with this name
                print("Attribute: "+attrToAdd+" to be added, with value "+attrValue)
                resultdata['attributes'][attrToAdd]=attrValue
                boolUpdateRequired=True
            if attrToRemove != "None":
                # We are being asked to remove an attribute, but we did not find it among the compute context's existing attributes
                print("Attribute: "+attrToRemove+" was not found and cannot be removed")
    else:
        # No attributes section in results data at all
        if attrToAdd != "None":
            # We are adding an attribute, and this compute context currently does not have any attributes
            print("Attribute: "+attrToAdd+" to be added as first attribute, with value "+attrValue)
            attrValueDict={attrToAdd: attrValue}
            resultdata['attributes']=attrValueDict
            boolUpdateRequired=True
        if attrToRemove != "None":
            # We are being asked to remove an attribute, but the compute context has no attributes
            print("Attribute: "+attrToRemove+" was not found and cannot be removed")

    # Let's see what we got
    #json_formatted_str = json.dumps(resultdata, indent=2)
    #print(json_formatted_str)

    if boolUpdateRequired:
        #print("Update required")
        # Update compute contexts
        # See http://swagger.na.sas.com/swagger-ui/?url=/apis/compute/v10/openapi-all.json#/Contexts/updateContext
        ##########################################################################
        # Updates a context definition. Changing a context does not affect any
        # sessions that are currently running on the server that is instantiated
        # by that context. Servers that are created after updating the context
        # use the current definition. If the contextId matches the ID of an
        # existing context, that context is updated. Otherwise, an error is
        # returned. The request must include the current ETag of the context as
        # the value of the If-Match request header to prevent concurrent updates.
        # The current ETag of the context is provided in the value of the ETag
        # response header of any endpoint that produces
        # application/vnd.sas.compute.context.
        ##########################################################################
        reqtype="put"
        reqval="/compute/contexts/"+id
        reqaccept="application/vnd.sas.compute.context+json"
        #reccontent="application/vnd.sas.collection+json"
        reccontent="application/vnd.sas.compute.context+json"
        resultdata_after_update=callrestapi(reqval,reqtype,reqaccept,reccontent,data=resultdata,etagIn=etag)
        json_formatted_str = json.dumps(resultdata_after_update, indent=2)
        #print(json_formatted_str)
    #else:
        #print("Update not required")


sys.exit()
