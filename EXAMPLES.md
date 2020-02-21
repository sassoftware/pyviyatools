## Examples

The example calls assume you are in the directory where you installed the tools. If you are not you can prepemd the directory to the filename, for example /opt/pyviyatools/callrestapi.py
If you are using the tool on windows the syntax is:

python toolname.py

The following examples are Linux.

**loginviauathinfo.py**

```bash
# Login to Viya using default authinfo file ~/.authinfo  
./loginviauthinfo.py

# Login to Viya using an authinfo file  
./loginviauthinfo.py -f ~/.authinfo_geladm
```

**callrestapi.py**

```bash
#return all the rest calls that can be made to the folders endpoint  
./callrestapi.py -e /folders -m get  

#return the json for all the folders/folders  
./callrestapi.py -e /folders/folders -m get  

#return simple text for all the folders/folders  
./callrestapi.py -e /folders/folders -m get -o simple 

#rest calls often limit the results returned the text output will tell you returned and total available items   
#in this call set a limit above the total items to see everything  
./callrestapi.py -e /folders/folders?limit=500 -m get -o simple  


#return the json for all the identities  
./callrestapi.py -e /identities/identities -m get    

#return the json for all the identities output to a file  
./callrestapi.py -e /identities/identities -m get > identities.json    

#refresh the identities cache  
./callrestapi.py -e /identities/userCount -m get    
./callrestapi.py -e /identities/cache/refreshes -m post

#return basic content using accept response type    
./callrestapi.py -m get -e /identities/users/sasadm -a "application/vnd.sas.identity.basic+json"
```    

**getfolderid.py**

```bash
# pass the folder path and return the folder id and uri  
./getfolderid.py -f /gelcontent  
```

**getruleid.py**

```bash
getruleid.py -u /SASVisualAnalytics/** -p "authenticatedUsers" 
```

**deletefolder.py**

```bash
# delete a folder based on its path   
./deletefolder.py -f /gelcontent  
```

**getconfigurationproperties.py**

```bash
#return a set of configuration properties  
./getconfigurationproperties.py -c sas.identities.providers.ldap.user -o simple  
```

**createdomain.py and updatedomain.py**

```bash
#create a domain using createdomain  
./createdomain.py -t password -d test -u sasadm -p lnxsas -g "SASAdministrators,HR ,Sales" 

#Update an existing domain to add credentials from a csv file   
./updatedomain.py -d LASRAuth -f /tmp/myusers.csv 

csv file format  
no header row  
column1 is userid  
column2 is password  
column3 is identity    
column4 is identity type (user or group)  

For example:  
myuserid,mypass,Sales,group   
acct1,pw1,sasadm,user  

#create a domain using callrestapi. Last part of endpoint is domain name
./callrestapi.py -e /credentials/domains/<newdomain> -m post -i domain.json  

INPUT JSON must be formatted as the endpoint expects. Example:  

{   
  "id": "<newdomain>",  
  "type": "password"  
}  
```

**testfolderaccess.py**

```bash
#test folder access  
./root/admin/pyviyatools/testfolderaccess.py -f '/gelcontent' -p Sales -m read -s grant -q  
```

**listrules.py**

```bash
# Display all sasadministrator rules  
./listrules.py --p SASadministrators -o simple

# Display all rules that contain SASVisual in the URI  
./listrules.py -u SASVisual -o simple
```

**createfolders.py**

```bash
# Create folders from a CSV file  
./createfolders.py" -f /tmp/newfolders.csv

FORMAT OF CSV file folder path (parents must exist), description  
/RnD, Folder under root for R&D  
/RnD/reports, reports  
/RnD/analysis, analysis  
/RnD/data plans, data plans  
/temp,My temporary folder  
/temp/mystuff, sub-folder
```  

**updatepreferences.py**

```bash
# Update the theme for the user sasadm  
./updatepreferences.py -t user -tn sasadm -pi  OpenUI.Theme.Default -pv sas_hcb
```  

**explainaccess.py**

```bash
#Explain direct and indirect permissions on the folder /folderA/folderB, no header row. For folders, conveyed permissions are shown by default.  
./explainaccess.py -f /folderA/folderB

#As above but for a specific user named Heather  
./explainaccess.py -f /folderA/folderB -n Heather -t user

#As above with a header row  
./explainaccess.py -f /folderA/folderB --header

#As above with a header row and the folder path, which is useful if you concatenate sets of results in one file  
./explainaccess.py -f /folderA/folderB -p --header

#As above showing only rows which include a direct grant or prohibit  
./explainaccess.py -f /folderA/folderB --direct_only

#Explain direct and indirect permissions on a service endpoint. Note in the results that there are no conveyed permissions. By default they are not shown for URIs.  
./explainaccess.py -u /SASEnvironmentManager/dashboard

#As above but including a header row and the create permission, which is relevant for services but not for folders and other objects   
./explainaccess.py -u /SASEnvironmentManager/dashboard --header -l read update delete secure add remove create

#Explain direct and indirect permissions on a report, reducing the permissions reported to just read, update, delete and secure, since none of add, remove or create are applicable to a report.   
./explainaccess.py -u /reports/reports/id --header -l read update delete secure

#Explain direct and indirect permissions on a folder expressed as a URI. Keep the default permissions list, but for completeness we must also specify -c true to request conveyed permissions be displayed, as they are not displayed by default for URIs.   
./explainaccess.py -u /folders/folders/id --header -p -c true
``` 

**getpath.py**

```bash
# Get folder path for an object (can be a folder, report or any other object which has a folder path)  
./getpath.py -u /folders/folders/id  
./getpath.py -u /reports/reports/id  
``` 

**listmemberswithpath.py**

```bash
# Return list of members of a folder identified by objectURI  
./listmemberswithpath.py -u /folders/folders/id  

# Return list of all members of a folder identified by objectURI, recursively searching subfolders  
./listmemberswithpath.py -u /folders/folders/id -r
``` 

**listcaslibs.py and listtables.py**

```bash
# Return list of all CAS libraries on all servers  
./listcaslibs.py
# Return list of all CAS tables in all CAS libraries on all servers  
./listcastables.py
``` 

**listcaslibsandeffectiveaccess.py**
```bash
# Return list of all effective access on all CAS libraries on all servers  
./listcaslibsandeffectiveaccess.py

# Return list of all effective access on all CAS tables in all CAS libraries on all servers  
./listcastablesandeffectiveaccess.py
``` 

**listgroupsandmembers.py**
```bash
# Return list of all groups and all their members  
./listgroupsandmembers.py
``` 
**importpackages.py**

```bash
# import all viya packages located in the os directory
importpackages.py -d /tmp/mypackage -q
```

**exportfoldertree.py**

```bash
# export all viya root folders and their sub-folders and content
# directory will contain an export package for folders under the Viya root folder
./exportfoldertree.py -d /tmp/viyafolders -q
```

**listfiles.py**

```bash
# list log files, created by the /jobexecution service older than 6 days old.
./listfiles.py -n log -p /jobExecution -d 6 -o csv 
```

**archivefiles.py**

```bash
# read log files from job execution and add archive them to an os directory
./archivefiles.py -n log -d 6 -p /job -fp /tmp 
```
**archivefiles.py**

```bash
#his tool will export all the reports in your viya system to there own
# individual json file in a directory

./snapshotreports.py -c 10 -d ~/snapshot 
```
