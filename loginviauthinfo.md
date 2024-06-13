## Usage

loginviauthinfo.py is used to read the credentials from a secure location and authenticate. The secure location is a authinfo file stored in the users home directory. Authinfo files are currently used in Viya to authenticate from any of the programming interfaces (Python,Java, Lua, Base SAS).  The use of the Authinfo file makes the code far easier to share and means the credentials are stored in one secure file rather than hundreds of unsecured code files."

SAS Documents creating authinfo files:

In the documnettation it says 

"The format of an authinfo file is based on the .netrc file specification that is used for FTP login. In addition to the .netrc file standards, the authinfo specification allows for putting commands in the file, as well as using quoted strings for passwords. The quoted strings allow for spaces within passwords and user IDs. "

https://go.documentation.sas.com/?cdcId=pgmsascdc&cdcVersion=9.4_3.4&docsetId=authinfo&docsetTarget=n0xo6z7e98y63dn1fj0g9l2j7oyq.htm&locale=en

Note the **pyviyatools use the .netrc format** not the updated .authinfo format. An addtional difference is that .netrc uses "machine" to identify the target environment rather than "host" for .authinfo.

The .netrc format is documented here https://www.ibm.com/support/knowledgecenter/en/ssw_aix_71/filesreference/netrc.html


Related post: https://communities.sas.com/t5/SAS-Communities-Library/Automating-post-deployment-SAS-Viya-tasks-with-REST-and-the/ta-p/603304

Example of file. 

First line specifies the default userid and password if no machine is specified. 

Second line specifies a machine and the userid and password for that machine.

```bash

default user sasadm1 password mypass
machine sasviya01.gelcorp.com user sasadm2 password mpass2

```

It is very similair to the .authinfo format, but not exactly the same.