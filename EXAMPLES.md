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

**createpublishdest.py**

```bash
# List all existing publishing destinations
 ./callrestapi.py -m get -e /modelPublish/destinations -o simple

# Create new publishing destinations - one example each for CAS, Hadoop and Teradata
./createpublishdest.py cas -n newcasdest -s cas-shared-default -c mycaslib -t thetable
./createpublishdest.py hadoop -n newhadoopdest -s cas-shared-default -c myhadoop -hd /mydir
./createpublishdest.py teradata -n newtddest -s cas-shared-default -c mycaslib  -dt teratable -db tera2
```

**deletepublishdest.py**

```bash
# Delete publishing destination
./deletepublishdest.py -n newcasdest
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
**snapshotreports.py**

```bash
#his tool will export all the reports in your viya system to there own
# individual json file in a directory
# optionally you can pass in folder path and only export reports that
# are located under that folder

./snapshotreports.py -c 10 -d ~/snapshot
./snapshotreports.py -c 10 -d ~/snapshot/salesreports -f /gelcontent/sales

```

**creategroups.py**

```bash
# create custom groups and add members using a csv file as input
# you can also add members to existing groups
#
# if the group already exists it will not be added and the http response is printed
# if the user does not exist it will not be added to the group and the http response is printed
# if the user is already a member of the group it will not be added to the group and the http response is printed
#
# none of the above conditions will prevent the processing of additional items in the csv

./creategroups.py -f /tmp/newgroups.csv

Format of csv file is four columns
Column 1 group id
Column 2 group name
Column 3 is a description
Column 4 member id

For example:
group2,"Group 2","My Group 2"
group3,"Group 3","My Group3",geladm
group1,"Group 1","group 1"
```

**applyfolderauthorization.py**

```bash
# create folder authorization rules using a csv file as input
#
# if the rule already exists it will not be added and the response (from the CLI command) is printed
#

./applyfolderauthorization.py -f /tmp/folderauths.csv

Format of input csv file is 6 columns
Column 1 is the full path to the folder
Column 2 is the principal type
Column 3 is the principal name
Column 4 is the access setting (grant or prohibit)
Column 5 is the permissions on the folder
Column 6 is the conveyed permissions on the folder's contents

For example:
/gelcontent/GELCorp/Marketing/Reports,group,Marketing,grant,"read,add,remove","read,update,delete,add,remove"
/gelcontent/GELCorp/Marketing/Reports,user,Douglas,grant,"read,update,add,remove,delete,secure","read,update,add,remove,delete,secure"
/gelcontent/GELCorp/Marketing/Analyses,group,Marketing,grant,"read,add,remove","read,update,delete,add,remove"
/gelcontent/GELCorp/Marketing/Work in Progress,group,Marketing,grant,"read,update,add,remove,delete,secure","read,update,add,remove,delete,secure"
```

**submit_jobdef.py**
```bash
./submit_jobdef.py -id {jobDefinitionId}
./submit_jobdef.py -id {jobDefinitionId} -v
./submit_jobdef.py -id {jobDefinitionId} -context "SAS Studio compute context"
./submit_jobdef.py -id {jobDefinitionId} -context "SAS Studio compute context" -v

```

**submit_jobreq.py**
```bash
./submit_jobreq.py -id {jobRequestId}
./submit_jobreq.py -id {jobRequestId} -v
```

**getcomputecontextattributes.py**

```bash
./getcomputecontextattributes.py -n "Data Mining compute context"
```

**setcomputecontextattributes.py**

```bash
./setcomputecontextattributes.py -n "Data Mining compute context" -a runAsUser -v sastest1
./setcomputecontextattributes.py -n "Data Mining compute context" -r runAsUser
```