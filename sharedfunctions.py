#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# sharedfunctions.py
# December 2017
#
# A set of shared functions used by the piviyatool which makes REST calls to supplement the VIYA CLI
#
# callrestapi is the core function it will accept a method endpoint and optionally a python dictionary as input
# getfolderid returns a folder id if it is passed the path to the viya folder
# getebaseuri returns the base url for the service from the default profile
# getauthtoken returns the authentication token created by the CLI call sas-admin auth login
# getinputjson converts the input json to a python dictionary
#
# Change History
#
#  27JAN2018 Comments added 
#  29JAN2018 Added simpleresults function  
#  31JAN2018 Added the ability to pass contenttype to call_rest_api (now callrestapi)   
#  31JAN2018 Improved error handling of call_rest_api (now callrestapi)
#  31JAN2018 Deal with situation where json is not returned   
#  31JAN2018 Fix a bug when neither json or text is returned
#  02FEB2018 Fix a bug when text is returned 
#  12MAR2018 Made simple result print generic   
#  20MAR2018 Added some comments 
#  20MAR2018 Handle errors when profile and authentication token do not exist 
#  20May2018 Fixed bug in authentication check
#  01jun2018 Deal with empty profile error
#  23oct2018 Added print result function
#  23oct2018 Added print csv
#  28oct2018 Added stop on error to be able to override stopping processing when an error occurs
#  20nov2018 Updated so that multiple profiles can be used
#  20dec2018 Fixed standard csv output
#  14JAN2019 Added getpath
#  20SEP2019 Added getidsanduris
#
# Copyright © 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


# Import Python modules
from __future__ import print_function
import requests
import sys
import json
import pprint
import os
import collections

pp = pprint.PrettyPrinter(indent=4)

# validate rest api is not used at this time
# not used
    
def validaterestapi(baseurl, reqval, reqtype, data={}):
    
    global result

    print("The request is a "+reqtype+" request: ",baseurl+reqval)
       
    json_data=json.dumps(data, ensure_ascii=False)
    
    print("Data for Request:")
    print(json_data)
    
    if (reqtype !="get" or reqtype !="post" or reqtype!="delete" or reqtype!="put"): 
        print("NOTE: Invalid method")
        
    return;
        
# callrestapi
# this is the main function called many other programs and by the callrestapi program to make the REST calls
# change history
#   01dec2017 initial development
#   28oct2018 Added stop on error to be able to override stopping processing when an error occurs

def callrestapi(reqval, reqtype, acceptType='application/json', contentType='application/json',data={},stoponerror=1):
   
    
    # get the url from the default profile
    baseurl=getbaseurl()

    # get the auth token
    oaval=getauthtoken(baseurl)
        
    # build the authorization header
    head= {'Content-type':contentType,'Accept':acceptType}
    head.update({"Authorization" : oaval})
    
    # maybe this can be removed    
    global result

    # sereliaze the data string for the request to json format
    json_data=json.dumps(data, ensure_ascii=False)
    
    # call the rest api using the parameters passed in and the requests python library 
       
    if reqtype=="get":
        ret = requests.get(baseurl+reqval,headers=head,data=json_data)
    elif reqtype=="post":
        ret = requests.post(baseurl+reqval,headers=head,data=json_data)
    elif reqtype=="delete":
        ret = requests.delete(baseurl+reqval,headers=head,data=json_data)
    elif reqtype=="put":
        ret = requests.put(baseurl+reqval,headers=head,data=json_data)
    else:
        result=None
        print("NOTE: Invalid method")
        sys.exit()        
    
  
    # response error if status code between these numbers   
    if (400 <= ret.status_code <=599):
    
       print(ret.text)    
       result=None            
       if stoponerror: sys.exit()  
    
    # return the result    
    else:
         # is it json   
         try:            
             result=ret.json()
         except:
            # is it text
            try:
                result=ret.text
            except:
                result=None
                print("NOTE: No result to print")
       
                  
            
    return result;
        
# getfolderid
# when a Viya content path is passed in return the id, path and uri
# change history
#   01dec2017 initial development
#   08Feb2020 return full json as 4 item in list that is returned

def getfolderid(path):
    
    # build the request parameters  
    reqval="/folders/folders/@item?path="+path
    reqtype='get'
          
    callrestapi(reqval,reqtype)

    if result==None:
        print("NOTE: Folder'"+path+"' not found.")
        targetid=None
        targetname=None
        targeturi=None
    else:
        targetid=result['id']
        targetname=result['name']
        targeturi="/folders/folders/"+targetid
                
    return [targetid,targeturi,targetname,result]
  
    
# getbaseurl
# from the default profile return the baseurl of the Viya server
# change history
#   01dec2017 initial development
#   01jun2018 Deal with empty profile error
#   20nov2018 Use the SAS_CLI_PROFILE env variable

    
def getbaseurl():

    # check that profile file is available and can be read

    # note the path to the profile is hard-coded right now
    endpointfile=os.path.join(os.path.expanduser('~'),'.sas','config.json')
    access_file=file_accessible(endpointfile,'r')

    #profile does not exist
    if access_file==False:
        print("ERROR: Cannot read CLI profile at:",endpointfile,". Recreate profile with sas-admin profile init.")
        sys.exit()

    #profile is empty file
    if os.stat(endpointfile).st_size==0:
         print("ERROR: Cannot read CLI profile empty file at:",endpointfile,". Recreate profile with sas-admin profile init.")
         sys.exit()

    # get json from profile
    with open(endpointfile) as json_file:
        data = json.load(json_file)
        
    # get the profile environment variable to use it
    # if it is not set default to the default profile
    
    cur_profile=os.environ.get("SAS_CLI_PROFILE","Default")
    #print("URL: ",cur_profile )
    
    # check that information is in profile
    if cur_profile in data:
        baseurl=data[cur_profile]['sas-endpoint']
    else:

        baseurl=None
        print("ERROR: profile "+cur_profile+" does not exist. Recreate profile with sas-admin profile init.")
        sys.exit()


    return baseurl


# getauthtoken
# from the stored auth file get the authentication token for the request header 
# change history
#   01dec2017 initial development
# return oaval=None when no authtoken retrieved
#   20nov2018 Use the SAS_CLI_PROFILE env variable

def getauthtoken(baseurl):
    
          
    #get authentication information for the header
    credential_file=os.path.join(os.path.expanduser('~'),'.sas','credentials.json')
    
    # check that credential file is available and can be read
    access_file=file_accessible(credential_file,'r')
    
    if access_file==False:
        oaval=None
        print("ERROR: Cannot read authentication credentials at: ", credential_file)
        print("ERROR: Try refreshing your token with sas-admin auth login")
        sys.exit()
    
    with open(credential_file) as json_file:  
        data = json.load(json_file)
    type(data)
   
    # the sas-admin profile init creates an empty credential file
    # check that credential is in file, if it is add it to the header, if not exit
    
     # get the profile environment variable to use it
    # if it is not set default to the default profile
    
    cur_profile=os.environ.get("SAS_CLI_PROFILE","Default")
    
    #print("LOGON: ", cur_profile )
    
    if cur_profile in data:
    
        oauthToken=data[cur_profile]['access-token']
               
        oauthTokenType="bearer"
    
        oaval=oauthTokenType + ' ' + oauthToken
    
        head= {'Content-type':'application/json','Accept':'application/json' }
        head.update({"Authorization" : oaval})
    
        # test a connection to rest api if it fails exit
        r = requests.get(baseurl,headers=head)
                
        if (400 <= r.status_code <=599):
 
            oaval=None
            print(r.text)
            print("ERROR: cannot connect to "+baseurl+" is your token expired?")
            print("ERROR: Try refreshing your token with sas-admin auth login")
            sys.exit()
    else:

        oaval=None
        print("ERROR: access token not in file: ", credential_file)
        print("ERROR: Try refreshing your token with sas-admin auth login")
        sys.exit()
        
    return oaval
    
# getinputjson
# load the returned json to a python dictionary
# change history
#   01dec2017 initial development
    
def getinputjson(input_file):

    with open(input_file) as json_file:
        inputdata = json.load(json_file)

    return inputdata    
    
# simpleresults
# take the complex json and create a simple print of the results
# change history
#   01dec2017 initial development
#   20dec2018 simple output now alphibetical order by key
    
def simpleresults(resultdata):

    # print a simplification of the json results
    
    
    # list of items returned by rest call
    if 'items' in resultdata:
    
        total_items=resultdata['count']
        
        returned_items=len(resultdata['items'])
        
        if total_items == 0: print("Note: No items returned.")
            
        for i in range(0,returned_items):    
        
            print ("=====Item ",i,"=======")
            
            origpairs=resultdata['items'][i]
            
            test=origpairs.get('description') 
            if test==None: origpairs['description']='None'
            
            pairs=collections.OrderedDict(sorted(origpairs.items()))
                                        
                                      
            for key,val in pairs.items():
        
               if key != 'links': 
                   print(key,end="")
                   print(" = ", val)
        
        print("Result Summary: Total items available: ",total_items ,"Total items returned: ", returned_items)
    
    elif 'id' in resultdata:  #one item returned by rest call
              
        for key,val in resultdata.items():
        
               if key != 'links': 
                   print(key,end="")
                   print(" = ", val)
    
    else:
        print("NOTE: No JSON Results Found")



# tableresults
# take the complex json and create a simple table of the results
# change history
#   01aug2018  initial development
#   19dece2018 print  csv in column orderwith only common columns  

def csvresults(resultdata,columns=[]):

      
    if 'items' in resultdata:
    
        total_items=resultdata['count']
        
        returned_items=len(resultdata['items'])
        
        if total_items == 0: print("Note: No items returned.")
            
        for i in range(0,returned_items):  
        
               
            origpairs=resultdata['items'][i]
            
            # create an ordered dictionary
            pairs=collections.OrderedDict()
            
            # loop thru the column list and insert to a new dictionary in that order
            # this ensures that colums appear in this order in the csv
            for keylabel in columns:
                
                # get the value for the current column
                curval=origpairs.get(keylabel)
                
                if curval != None:
                   pairs[keylabel] = curval
                else:
                   pairs[keylabel] = 'None' 
                                                                
            numvals=len(columns)
            z=0
            
            # print header row of column names
            for key,val in pairs.items():
                            
                z=z+1            
                
                # seperate with comma except last item
                if z==numvals: sep=''
                else: sep=','
    
                if i==0 and key in columns: print(key,sep,end="")
                
            print("\n",end="")
            
            z=0
            
            # print rows
            for key,val in pairs.items():
             
                # seperate with comma except last item
                z=z+1
                if z==numvals: sep=''
                else: sep=','
        
                if key !=  'links' and key in columns: print('"'+str(val)+'"'+sep, end="")
         
        
        print("\n",end="")
        
            
    elif 'id' in resultdata:  #one item returned by rest call
        
        numvals=len(resultdata.items())
        z=0
        
        for key,val in resultdata.items():
        
            # seperate with comma except last item
            z=z+1
            if z==numvals: sep=''
            else: sep=','
        
            if key != 'links': print(key,sep,end="")
                   
        print("\n",end="")
        
        
        z=0
        
        for key,val in resultdata.items():
        
            # seperate with comma except last item
            z=z+1
            if z==numvals: sep=''
            else: sep=','
            
            if key != 'links': print('"'+str(val)+'"'+sep,end="")
                   
        print("\n",end="")
            
    else:
        print("NOTE: No JSON Results Found")


# file_accessible
# Check if a file exists and is accessible. 
# change history
#   01dec2017 initial development
      
def file_accessible(filepath, mode):
    
    try:
        f = open(filepath, mode)
        f.close()
    except IOError as e:
        return False
 
    return True


# printresult
# prints the results in the style requested 
# change history
#   28oct2018 initial development
#   22dec2018 add csv columns only relevent for csv output, defaults provided but can be overriden when called
#   20feb2020 add simplejson output style

def printresult(result,output_style,colsforcsv=["id","name","type","description","creationTimeStamp","modifiedTimeStamp"]):

    
    # print rest call results
    if type(result) is dict:
        
        if output_style=='simple':
            simpleresults(result)
        elif output_style=='simplejson':
            simplejsonresults(result)
        elif output_style=='csv':
            csvresults(result,columns=colsforcsv)
        else:
            print(json.dumps(result,indent=2))
    else: print(result) 
    


# getprofileinfo
# prints the token expiration, endpoint and current user
# change history
#   20nov2018 initial development
    

def getprofileinfo(myprofile):
    
       
          
    #get authentication information for the header
    credential_file=os.path.join(os.path.expanduser('~'),'.sas','credentials.json')
    
    # check that credential file is available and can be read
    access_file=file_accessible(credential_file,'r')
    
    if access_file==False:
        print("ERROR: Cannot read authentication credentials at: ", credential_file)
        print("ERROR: Try refreshing your token with sas-admin auth login")
        sys.exit()
    
    with open(credential_file) as json_file:  
        data = json.load(json_file)
    type(data)
   
    # the sas-admin profile init creates an empty credential file
    # check that credential is in file, if it is add it to the header, if not exit
    
     # get the profile environment variable to use it
    # if it is not set default to the default profile
    
          
    if myprofile in data:
    
        expiry=data[myprofile]['expiry']
        print("Note your authentication token expires at: "+expiry)
                
    else:
        
        print("ERROR: access token not in file: ", credential_file)
        print("ERROR: Try refreshing your token with sas-admin auth login")
        sys.exit()
      
        
    # note the path to the profile is hard-coded right now
    endpointfile=os.path.join(os.path.expanduser('~'),'.sas','config.json')
    access_file=file_accessible(endpointfile,'r')

    #profile does not exist
    if access_file==False:
        print("ERROR: Cannot read CLI profile at:",endpointfile,". Recreate profile with sas-admin profile init.")
        sys.exit()

    #profile is empty file
    if os.stat(endpointfile).st_size==0:
         print("ERROR: Cannot read CLI profile empty file at:",endpointfile,". Recreate profile with sas-admin profile init.")
         sys.exit()

    # get json from profile
    with open(endpointfile) as json_file:
        data = json.load(json_file)
        
        
    # check that information is in profile
    if myprofile in data:
        baseurl=data[myprofile]['sas-endpoint']
        print("Endpoint is: "+baseurl)
    else:
        print("ERROR: profile "+myprofile+" does not exist. Recreate profile with sas-admin profile init.")
       
    # build the request parameters  
    reqval="/identities/users/@currentUser"
    reqtype='get'
          
    result=callrestapi(reqval,reqtype)
        
    if result==None:
        print("NOTE: Not logged in.")
        
    else:
        print("Logged on as id: "+ result['id'])
        print("Logged on as name: "+result['name'])
        
        
    
# getpath
# when a Viya objectURI is passed in return the path
# change history
#   14JAN2019 initial development

def getpath(objecturi):

    # build the request parameters
    reqval='/folders/ancestors?childUri='+objecturi
    reqtype='get'
    accept='application/vnd.sas.content.folder.ancestor+json'

    ancestors_result_json=callrestapi(reqval,reqtype,accept)
    #print(ancestors_result_json)

    if not 'ancestors' in ancestors_result_json:
        print("NOTE: Could not get ancestor folders of ObjectURI '"+objecturi+"'.")
        path=None
    else:
        ancestors = ancestors_result_json['ancestors']

        path=''

        #For each principle's section in the explanations section of the data returned from the REST API call...
        for ancestor in ancestors:
            path=ancestor['name']+'/'+path
        path='/'+path

    return path

# getidsanduris
# given a result json structure, return a dictionary with a list of id's and uri's 
# change history
#   01dec2017 initial development

def getidsanduris(resultdata):

    resultdict={}
    resultdict['ids']=[]
    resultdict['uris']=[]
    
    # loop the result and add a list of ids and uris to the returned dictionary
    if 'items' in resultdata:
    
        total_items=resultdata['count']
        returned_items=len(resultdata['items'])
        if total_items == 0: print("Note: No items returned.")
         
        for i in range(0,returned_items): 
                                
           resultdict['ids'].append(resultdata['items'][i]['id'])
           resultdict['uris'].append(resultdata['items'][i]['uri'])
                             
    return resultdict


# simplejsonresults
# given a result json structure, remove all the "links" items
# this will return a more readable json output 
# change history
#   20feb2020 initial development
      
def simplejsonresults(resultdata):

      
    if 'items' in resultdata:   # list of items returned by rest call
    
        for key in list(resultdata): 
            if key == 'links':  del resultdata[key] 

        total_items=resultdata['count']
        returned_items=len(resultdata['items'])
        
        if total_items == 0: print("Note: No items returned.")
            
        for i in range(0,returned_items):  
                       
            for key in list(resultdata['items'][i]):
                if key=='links':                   
                     del resultdata['items'][i][key]
            
        print(json.dumps(resultdata,indent=2))

    elif 'id' in resultdata:  #one item returned by rest call

        del resultdata['links'] 
        print(json.dumps(resultdata,indent=2))
