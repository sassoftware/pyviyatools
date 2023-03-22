#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#
# modifydomain.py
# December 2017
#
# modify a viya domain
#
# Change History
# March 2023, Add support for 'client' identity type

import argparse, sys, base64, json

from sharedfunctions import callrestapi

parent_parser = argparse.ArgumentParser(add_help=False)

parent_parser.add_argument("-n","--name", help="Domain name.",required=True)
parent_parser.add_argument("-it","--identitytype", help="User, Group or Client",required=True,choices=['user','group','client'])
parent_parser.add_argument("-i","--identity", help="List of users OR list of groups (comma seperated)",required=True)
parent_parser.add_argument("--debug", action='store_true', help="Debug")

parser = argparse.ArgumentParser(description="Modify a Domain")

subparsers = parser.add_subparsers(help='Type of Domain',dest="type")

# password domain
password_parser=subparsers.add_parser("password",description="Update credentials on password domain",parents=[parent_parser])
password_parser.add_argument("-uid","--userid", help="Name of credential account",required=True)
password_parser.add_argument("-pw","--password", help="Password of credential user",required=True)

# token domain
# nothing needed it will add the current token for the user
token_parser=subparsers.add_parser("oauth2.0",description="Update token on Token(oauth2.0) Domain",parents=[parent_parser])

# encryption domain
oauth_parser=subparsers.add_parser("cryptDomain",description="Update encryption key on  cryptDomain",parents=[parent_parser])
oauth_parser.add_argument("-k","--key", help="Encryption Key",required=True)

connection_parser=subparsers.add_parser("connection",description="Update account on connection domain",parents=[parent_parser])
connection_parser.add_argument("-uid","--userid", help="User Id",required=True)

args = parser.parse_args()
# get common paramaters
domain_name=args.name
type=args.type
identitytype=args.identitytype

if identitytype=='group': epointvar='groups'
elif identitytype=='user': epointvar='users'
elif identitytype=='client': epointvar='clients'

identitylist=args.identity.split(",")
debug=args.debug

# check if domain and type combo exists, if it doesn't print a message and exit
reqval="/credentials/domains/"+domain_name
reqtype="get"
result=callrestapi(reqval,reqtype)

if result['type']==type:
    print("NOTE: modifying domain with name "+domain_name+" and type "+type+".")
else:
    print("ERROR: domain with name "+domain_name+" and type "+type+" does not exist.")
    sys.exit()

# now we know domain exists
# build the dictionary for each type
data={}
data['domainId'] = domain_name
data['domainType'] = type

if type=='password':

    userid=args.userid
    pwval=args.password

    data['properties']={"userId": userid}
    cred=base64.b64encode(pwval.encode("utf-8")).decode("utf-8")
    data['secrets']={"password": cred}

#elif type=='oaauth2.0':


elif type=='cryptDomain':
    keyval=args.key
    cred=base64.b64encode(keyval.encode("utf-8")).decode("utf-8")
    data['secrets']={"encryptkey": cred}

elif type=='connection':

    userid=args.userid
    data['properties']={"userId": userid}

# loop the identity list and update the domain credentials

for identity in identitylist:

    print("NOTE: Updating "+identitytype+" "+identity+ " on "+type+" domain "+ domain_name)
    data['identityId'] = identity
    data['identityType'] =  identitytype

    if debug:
        print(json.dumps(data,indent=2))
        print(reqval)

    # do the magic
    reqval="/credentials/domains/"+domain_name+"/"+epointvar+"/"+identity
    reqtype="put"
    callrestapi(reqval,reqtype,data=data)

