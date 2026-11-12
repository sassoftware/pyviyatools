# pyviyatools Tool Reference

This reference is generated from the tools' `argparse` definitions. Regenerate it after changing a tool's arguments.

## applyauthmodel.py

[Source](../applyauthmodel.py)

Applies the CSV files output by the ViyaAuthModel project (https://gitlab.sas.com/snztst/viyaauthmodel) and applies them to a Viya environment.

```text
usage: applyauthmodel.py [-h] -e ENV -d DIRECTORY [--dryrun] [--replacerules]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-e, --env ENV` | Name of environment that is to be extracted. | Required; Default: `None` |
| `-d, --directory DIRECTORY` | Directory that contains CSV auth files to be implemented. | Required; Default: `None` |
| `--dryrun` | Compiles commands for review without running them. | Default: `False` |
| `--replacerules` | Changes the function of toggleviyarules call from 'disable' to 'replace'                     - creating replacement rules for the Viya service account 'sasapp'. | Default: `False` |

## applyfolderauthorization.py

[Source](../applyfolderauthorization.py)

Apply bulk auths from a CSV file to folders and contents

```text
usage: applyfolderauthorization.py [-h] -f FILE
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --file FILE` | Full path to CSV file. Format of csv: 'folderpath,principaltype,principalid,grant_or_prohibit,perms_on_folder,perms_on_contents | Required; Default: `None` |

## applyviyarules.py

[Source](../applyviyarules.py)

Apply bulk auths from a CSV file to folders and contents

```text
usage: applyviyarules.py [-h] -f FILE
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --file FILE` | Full path to CSV file. Format of csv: 'objecturi,principaltype,principalid,grant_or_prohibit,perms,enabled,condition | Required; Default: `None` |

## archivefiles.py

[Source](../archivefiles.py)

DETAILS: Archive and optionally delete files stored in the Viya infrastructure data server.<br>NOTE: By default files in folders are not processed. You must use -pf to process files stored in folders.

```text
usage: archivefiles.py [-h] [-n NAME] [-c TYPE] [-p PARENT] [-pf PARENTFOLDER]
                       [-d DAYS] [-m MODIFIEDBY] [-fp PATH] [-x] [-xx]
                       [--debug]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Name contains | Default: `None` |
| `-c, --type TYPE` | Content Type in. | Default: `None` |
| `-p, --parent PARENT` | ParentURI starts with. | Default: `None` |
| `-pf, --parentfolder PARENTFOLDER` | Parent Folder Name. | Default: `None` |
| `-d, --days DAYS` | List files older than this number of days | Default: `'-1'` |
| `-m, --modifiedby MODIFIEDBY` | Last modified id equals | Default: `None` |
| `-fp, --path PATH` | Path of directory to store files | Default: `'/tmp'` |
| `-x, --delete` | Delete Files after archiving from Viya | Default: `False` |
| `-xx, --deletenoarch` | Delete Files without Archiving from Viya | Default: `False` |
| `--debug` | Debug | Default: `False` |

## callrestapi.py

[Source](../callrestapi.py)

Call the Viya REST API

```text
usage: callrestapi.py [-h] -e ENDPOINT -m {get,put,post,delete,patch,head}
                      [-i INPUTFILE] [-a ACCEPTTYPE] [-c CONTENTTYPE]
                      [-o {csv,json,simple,simplejson}] [-t] [-hf HEADERFILE]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-e, --endpoint ENDPOINT` | Enter the REST endpoint e.g. /folders/folders  | Required; Default: `None` |
| `-m, --method METHOD` | Enter the REST method. | Required; Choices: `get, put, post, delete, patch, head`; Default: `'get'` |
| `-i, --inputfile INPUTFILE` | Enter the full path to an input json file | Default: `None` |
| `-a, --accepttype ACCEPTTYPE` | Enter REST Content Type you want returned e.g application/vnd.sas.identity.basic+json | Default: `'application/json'` |
| `-c, --contenttype CONTENTTYPE` | Enter REST Content Type for POST e.g application/vnd.sas.identity.basic+json | Default: `'application/json'` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson`; Default: `'json'` |
| `-t, --text` | Display Simple Text Results. | Default: `False` |
| `-hf, --headerfile HEADERFILE` | Enter the full path to a header json file | Default: `None` |

## changeimportloc.py

[Source](../changeimportloc.py)

Modifies exported VA report json file to having /Public as it's source location

```text
usage: changeimportloc.py [-h] -f FILE [-o OUTPUTDIR]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --file FILE` | Enter the path to the source file. | Required; Default: `None` |
| `-o, --outputdir OUTPUTDIR` | Enter the destination path for file/s output. | Default: `current working directory` |

## comparecontent.py

[Source](../comparecontent.py)

Compare two content lists.

```text
usage: comparecontent.py [-h] -f1 FILE1 -f2 FILE2 [-f1l FILE1LABEL]
                         [-fl2 FILE2LABEL] [-d] [--ignore-dates]
                         [--ignore-ownership] [--ignore-id]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f1, --file1 FILE1` | Full path to the first content file. | Required; Default: `None` |
| `-f2, --file2 FILE2` | Full path to the second content file. | Required; Default: `None` |
| `-f1l, --file1label FILE1LABEL` | Optional label for file1. | Default: `'First file.'` |
| `-fl2, --file2label FILE2LABEL` | Optional label for file2. | Default: `'Second file.'` |
| `-d, --debug` | Debug output | Default: `False` |
| `--ignore-dates` | Ignore creationTimeStamp and modifiedTimeStamp columns when comparing | Default: `False` |
| `--ignore-ownership` | Ignore createdByand modifiedBy columns when comparing | Default: `False` |
| `--ignore-id` | Ignore id columns when comparing, some content gets a new id on import | Default: `False` |

## compareviyarules.py

[Source](../compareviyarules.py)

Receives bulk auths from a CSV file and compares to what exists

```text
usage: compareviyarules.py [-h] -f FILE
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --file FILE` | Full path to CSV file. Format of csv: 'objecturi,principaltype,principalid,grant_or_prohibit,perms,enabled,condition | Required; Default: `None` |

## createbinarybackup.py

[Source](../createbinarybackup.py)

```text
usage: createbinarybackup.py [-h] [-q] [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-q, --quiet` |  | Default: `False` |
| `-d, --debug` |  | Default: `False` |

## createcaslibjson.py

[Source](../createcaslibjson.py)

Create basic CASLIBs from a CSV file

```text
usage: createcaslibjson.py [-h] -f FILE
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --file FILE` | Full path to CSV file. Format of csv: 'name,path,casserver,type,subdirs | Required; Default: `None` |

## createcaslibjsonauth.py

[Source](../createcaslibjsonauth.py)

Create CASLIBs Authorization files from a CSV file

```text
usage: createcaslibjsonauth.py [-h] -f FILE
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --file FILE` | Full path to CSV file. Format of csv: 'CASLIB,ID,permissions | Required; Default: `None` |

## createcryptdomain.py

[Source](../createcryptdomain.py)

Create a Viya Encryption Domain. Please see createdomain.py to create other types of domain.

```text
usage: createcryptdomain.py [-h] -d DOMAIN -k KEY -g GROUPS [-c DESC]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --domain DOMAIN` | Enter the domain name. | Required; Default: `None` |
| `-k, --key KEY` | Encryption Key. | Required; Default: `None` |
| `-g, --groups GROUPS` | A list of groups to add to the domain. Groupid comma seperated | Required; Default: `None` |
| `-c, --desc DESC` | Description of the domain. | Default: `None` |

## createdomain.py

[Source](../createdomain.py)

Create a Viya Domain (password, token, connection) : Please see createcryptdomain.py to create encryption domains.

```text
usage: createdomain.py [-h] -d DOMAIN [-u USER] [-p PASSWORD] -g GROUPS
                       [-c DESC] -t {password,connection,oauth2.0} [-s]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --domain DOMAIN` | Enter the domain name. | Required; Default: `None` |
| `-u, --user USER` | User ID for the domain. | Default: `None` |
| `-p, --password PASSWORD` | Password for the userid. | Default: `None` |
| `-g, --groups GROUPS` | A list of groups to add to the domain. Groupid comma seperated | Required; Default: `None` |
| `-c, --desc DESC` | Description of the domain. | Default: `None` |
| `-t, --type TYPE` | Type of the domain: password, oauth2.0 (token) or connection (passwordless). | Required; Choices: `password, connection, oauth2.0`; Default: `None` |
| `-s, --store` | Store Credential in existing domain. (Domain Creation is skipped) | Default: `False` |

## createfolders.py

[Source](../createfolders.py)

Create folders that are read from a csv file

```text
usage: createfolders.py [-h] -f FILE [--debug] [--skipfirstrow]
                        [--encoding ENCODING]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --file FILE` | Full path to csv file containing folders, format of csv: 'folderpath,description' | Required; Default: `None` |
| `--debug` | Debug | Default: `False` |
| `--skipfirstrow` | Skip the first row if it is a header | Default: `False` |
| `--encoding ENCODING` | default is utf-8 for python3 | Default: `'utf-8'` |

## creategroups.py

[Source](../creategroups.py)

Create custom groups and establish membership from csv: File Format: column1=groupid,column2=group name,column3=description,optional column4=memberid

```text
usage: creategroups.py [-h] -f FILE [--debug] [--skipfirstrow]
                       [--encoding ENCODING]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --file FILE` | Full path to csv file containing groups  | Required; Default: `None` |
| `--debug` | Debug | Default: `False` |
| `--skipfirstrow` | Skip the first row if it is a header | Default: `False` |
| `--encoding ENCODING` | default is utf-8 for python3 | Default: `'utf-8'` |

## createpublishdest.py

[Source](../createpublishdest.py)

Create a Publishing Destinations

```text
usage: createpublishdest.py [-h] {cas,hadoop,teradata} ...
```

### Subcommands

#### `cas`

CAS destination

```text
usage: createpublishdest.py cas [-h] [-d DESC] -n NAME -s SERVER -c CASLIB -t
                                TABLE
```

##### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --desc DESC` | Description | Default: `'Created by pyviya'` |
| `-n, --name NAME` | Enter the destination name. | Required; Default: `None` |
| `-s, --server SERVER` | CAS Server. | Required; Default: `'cas-shared-default'` |
| `-c, --caslib CASLIB` | CASLIB. | Required; Default: `None` |
| `-t, --table TABLE` | Table | Required; Default: `None` |

#### `hadoop`

Hadoop destination

```text
usage: createpublishdest.py hadoop [-h] [-d DESC] -n NAME -s SERVER -c CASLIB
                                   -hd HDFSDIR
```

##### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --desc DESC` | Description | Default: `'Created by pyviya'` |
| `-n, --name NAME` | Enter the destination name. | Required; Default: `None` |
| `-s, --server SERVER` | CAS Server. | Required; Default: `'cas-shared-default'` |
| `-c, --caslib CASLIB` | CASLIB. | Required; Default: `None` |
| `-hd, --hdfsdir HDFSDIR` | HDFS Directory | Required; Default: `None` |

#### `teradata`

Teradata Destination

```text
usage: createpublishdest.py teradata [-h] [-d DESC] -n NAME -s SERVER -c
                                     CASLIB -db DBCASLIB -dt TABLE
```

##### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --desc DESC` | Description | Default: `'Created by pyviya'` |
| `-n, --name NAME` | Enter the destination name. | Required; Default: `None` |
| `-s, --server SERVER` | CAS Server. | Required; Default: `'cas-shared-default'` |
| `-c, --caslib CASLIB` | CASLIB. | Required; Default: `None` |
| `-db, --dbcaslib DBCASLIB` | Database Caslib | Required; Default: `None` |
| `-dt, --table TABLE` | Destination Table | Required; Default: `None` |

## createreportimage.py

[Source](../createreportimage.py)

Generate a Visual Analytics Report Image

```text
usage: createreportimage.py [-h] -d DIRECTORY -f FILE -r REPORTID [-s SIZE]
                            [-o REPORTOBJECTID] [-q]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --directory DIRECTORY` | Directory to store output file | Required; Default: `None` |
| `-f, --file FILE` | Name of the output file | Required; Default: `None` |
| `-r, --reportId REPORTID` | ID of the report to export | Required; Default: `None` |
| `-s, --size SIZE` | Size of the output image as a string (ex: '1024px,768px') | Default: `'1024px,768px'` |
| `-o, --reportObjectId REPORTOBJECTID` | ID of the report object to export (ex: ve123) | Default: `None` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |

## createreportpdf.py

[Source](../createreportpdf.py)

Generate a pdf from a Visual Analytics Report

```text
usage: createreportpdf.py [-h] -r REPORTID [-f FOLDERID] -n FILENAME
                          [-c {replace,rename}] [-w WAIT] [-q]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-r, --reportId REPORTID` | ID of the report to export | Required; Default: `None` |
| `-f, --folderid FOLDERID` | Enter the viya folder id for the output to be placed in. | Default: `'@myFolder'` |
| `-n, --filename FILENAME` | Name the path of the Viya Folder. | Required; Default: `None` |
| `-c, --nameConflict NAMECONFLICT` | The strategy for handling name collision when saving the result file: replace or rename | Choices: `replace, rename`; Default: `'replace'` |
| `-w, --wait WAIT` | Specify the number of seconds to wait for the job to complete. Default is 30. | Default: `30`; Type: `int` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |

## deletecontent.py

[Source](../deletecontent.py)

Delete a folders content

```text
usage: deletecontent.py [-h] -f FOLDERPATH [-i] [-d] [-q]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --folderpath FOLDERPATH` | Enter the path to the viya folder. | Required; Default: `None` |
| `-i, --includefolder` | Include folder in delete. | Default: `False` |
| `-d, --debug` | Debug | Default: `False` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |

## deletedomain.py

[Source](../deletedomain.py)

Delete a Viya Domain

```text
usage: deletedomain.py [-h] -d DOMAIN -t
                       {password,connection,oauth2.0,cryptDomain}
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --domain DOMAIN` | Enter the domain name. | Required; Default: `None` |
| `-t, --type TYPE` | Type of the domain: password, oauth2.0 (token), connection (passwordless) or encryption. | Required; Choices: `password, connection, oauth2.0, cryptDomain`; Default: `None` |

## deletefolder.py

[Source](../deletefolder.py)

Delete a folder and its sub-folders

```text
usage: deletefolder.py [-h] -f FOLDERPATH [-q]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --folderpath FOLDERPATH` | Enter the path to the viya folder. | Required; Default: `None` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |

## deletefolderandcontent.py

[Source](../deletefolderandcontent.py)

Delete a folder and its sub-folders and contents

```text
usage: deletefolderandcontent.py [-h] -f FOLDERPATH [-q]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --folderpath FOLDERPATH` | Enter the path to the viya folder. | Required; Default: `None` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |

## deletejobhistory.py

[Source](../deletejobhistory.py)

```text
usage: deletejobhistory.py [-h] [-e] [-f FILTER] [-w] [-l LIMIT]
                           [-p PAGELIMIT]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-e, --empty` | Filter on objects without an expiration set. | Default: `False` |
| `-f, --filter FILTER` | Set a custom filter for objects, for example eq(createdBy,sasdemo). | Default: `None` |
| `-w, --write` | Make the specified changes. | Default: `False` |
| `-l, --limit LIMIT` | Specify the number of records to pull in each REST API call. Default is 10. | Default: `10`; Type: `int` |
| `-p, --pagelimit PAGELIMIT` | Specify the number of pages to pull before stopping. Default is 10. | Default: `10`; Type: `int` |

## deleteorphanedfiles.py

[Source](../deleteorphanedfiles.py)

```text
usage: deleteorphanedfiles.py [-h] [-f FILTER] [-w] [-l LIMIT] [-p PAGELIMIT]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --filter FILTER` | Set a custom filter for objects, for example eq(createdBy,sasdemo). | Default: `None` |
| `-w, --write` | Make the specified changes. | Default: `False` |
| `-l, --limit LIMIT` | Specify the number of records to pull in each REST API call. Default is 10. | Default: `10`; Type: `int` |
| `-p, --pagelimit PAGELIMIT` | Specify the number of pages to pull before stopping. Default is 10. | Default: `10`; Type: `int` |

## deleteorphanedfoldermembers.py

[Source](../deleteorphanedfoldermembers.py)

```text
usage: deleteorphanedfoldermembers.py [-h] -f FOLDER [-d] [-l LIMIT]
                                      [-p PAGELIMIT]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --folder FOLDER` | Specify the folder to search for orphaned memberships. | Required; Default: `None` |
| `-d, --delete` | Delete the members found. | Default: `False` |
| `-l, --limit LIMIT` | Specify the number of records to pull in each REST API call. Default is 10. | Default: `10`; Type: `int` |
| `-p, --pagelimit PAGELIMIT` | Specify the number of pages to pull before stopping. Default is 10. | Default: `10`; Type: `int` |

## deleteorphanedschedulerjobs.py

[Source](../deleteorphanedschedulerjobs.py)

```text
usage: deleteorphanedschedulerjobs.py [-h] [-f FILTER] [-w] [-l LIMIT]
                                      [-p PAGELIMIT]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --filter FILTER` | Set a custom filter for objects, for example eq(createdBy,sasdemo). | Default: `None` |
| `-w, --write` | Make the specified changes. | Default: `False` |
| `-l, --limit LIMIT` | Specify the number of records to pull in each REST API call. Default is 10. | Default: `10`; Type: `int` |
| `-p, --pagelimit PAGELIMIT` | Specify the number of pages to pull before stopping. Default is 10. | Default: `10`; Type: `int` |

## deletepublishdest.py

[Source](../deletepublishdest.py)

Delete a publishing destination

```text
usage: deletepublishdest.py [-h] -n NAME [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Enter the name of the publishing destination to be deleted. | Required; Default: `None` |
| `-d, --debug` | Debug | Default: `False` |

## deletetransferpackages.py

[Source](../deletetransferpackages.py)

Query and list files stored in the infrastructure data server.

```text
usage: deletetransferpackages.py [-h] [-n NAME] [-m MODIFIEDBY] [-c CREATEDBY]
                                 [-d DAYS] [-do {older,younger}] [-q]
                                 [--debug]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Name contains | Default: `None` |
| `-m, --modifiedby MODIFIEDBY` | Last modified id equals | Default: `None` |
| `-c, --createdby CREATEDBY` | Created id equals | Default: `None` |
| `-d, --days DAYS` | List files older than this number of days | Default: `'-1'` |
| `-do, --olderoryounger OLDERORYOUNGER` | For the date subsetting specify older or younger | Choices: `older, younger`; Default: `'older'` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |
| `--debug` | Debug | Default: `False` |

## explainaccess.py

[Source](../explainaccess.py)

```text
usage: explainaccess.py [-h] [-f FOLDERPATH] [-u OBJECTURI] [-n NAME]
                        [-t {user,group}] [-p] [--header] [--direct_only]
                        [-l PERMISSIONS_LIST [PERMISSIONS_LIST ...]]
                        [-c {true,false}] [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --folderpath FOLDERPATH` | Path to a Viya folder. You must specify either -f folderpath or -u objectURI. | Default: `None` |
| `-u, --objecturi OBJECTURI` | Object URI. You must specify either -f folderpath or -u objectURI. | Default: `None` |
| `-n, --name NAME` | Enter the name of the user or group to test. | Default: `None` |
| `-t, --principaltype PRINCIPALTYPE` | Enter the type of principal to test: user or group. | Choices: `user, group`; Default: `None` |
| `-p, --printpath` | Print the folder path in each row | Default: `False` |
| `--header` | Print a header row | Default: `False` |
| `--direct_only` | Show only explanations which include a direct grant or prohibit | Default: `False` |
| `-l, --permissions_list PERMISSIONS_LIST` | List of permissions, to include instead of all seven by default | Default: `['read', 'update', 'delete', 'secure', 'add', 'remove']`; Arguments: `+` |
| `-c, --convey CONVEY` | Show conveyed permissions in results. True by default when folder path is specified. False by dfefault if Object URI is specified. | Choices: `true, false`; Default: `None` |
| `-d, --debug` | Debug | Default: `False` |

## exportcaslibs.py

[Source](../exportcaslibs.py)

```text
usage: exportcaslibs.py [-h] [-s SERVER] [-i] -d DIRECTORY [-nc NAMECONTAINS]
                        [-dc DESCRIPTIONCONTAINS] [-q] [--debug]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-s, --server SERVER` | CAS Server (default is cas-shared-default) | Default: `'cas-shared-default'` |
| `-i, --includeauthorization` | Also export caslib authorization | Default: `False` |
| `-d, --directory DIRECTORY` | Directory where packages are written. | Required; Default: `None` |
| `-nc, --namecontains NAMECONTAINS` | Name contains | Default: `None` |
| `-dc, --descriptioncontains DESCRIPTIONCONTAINS` | Name contains | Default: `None` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |
| `--debug` | Debug | Default: `False` |

## exportcustomgroups.py

[Source](../exportcustomgroups.py)

Export Custom Groups to a Package

```text
usage: exportcustomgroups.py [-h] [-f FILENAME] [--id ID] [-n NAME] [-t]
                             [-l LIMIT] [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --filename FILENAME` | Full path to file. (No extension) | Default: `'/tmp/customgroups'` |
| `--id ID` | Subset based on group id containing a string | Default: `None` |
| `-n, --name NAME` | Subset based on name containing a string | Default: `None` |
| `-t, --transferremove` | Remove transfer file after download? | Default: `False` |
| `-l, --limit LIMIT` | Specify the number of records to pull. Default is 1000. | Default: `1000`; Type: `int` |
| `-d, --debug` | Debug | Default: `False` |

## exportfolder.py

[Source](../exportfolder.py)

Export a Viya Folder and its sub-folders

```text
usage: exportfolder.py [-h] -f FOLDERPATH -d DIRECTORY [--filename FILENAME]
                       [-t] [-q]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --folderpath FOLDERPATH` | Folder path to export | Required; Default: `None` |
| `-d, --directory DIRECTORY` | Directory for Export | Required; Default: `None` |
| `--filename FILENAME` | File name without extension. Optional, default name is the folder path. | Default: `'XNOFILENAMEX'` |
| `-t, --tranferremove` | Remove transfer package from SAS Viya after download to JSON file | Default: `False` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |

## exportfoldertree.py

[Source](../exportfoldertree.py)

Export the complete Viya folder tree or the members of a folder to a set of Viya Packages.

```text
usage: exportfoldertree.py [-h] -d DIRECTORY [-f FOLDER] [-q] [-t] [-n]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --directory DIRECTORY` | Directory to store Export Packages | Required; Default: `None` |
| `-f, --folder FOLDER` | Folder to start export at (root is default) | Default: `'NONE'` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |
| `-t, --tranferremove` | Remove transfer package from SAS Viya after download to JSON file | Default: `False` |
| `-n, --nonincrament` | Do not add an incremental number at the end of the downloaded JSON file  | Default: `False` |

## exportgeoproviders.py

[Source](../exportgeoproviders.py)

Export each geo providers to it's own unique transfer package

```text
usage: exportgeoproviders.py [-h] -d DIRECTORY [-q] [-l LIMIT]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --directory DIRECTORY` | Directory to store report packages | Required; Default: `None` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |
| `-l, --limit LIMIT` | Specify the number of records to pull. Default is 1000. | Default: `1000`; Type: `int` |

## exportjobflow.py

[Source](../exportjobflow.py)

Export a Viya Job Flow or Flows to packages.

```text
usage: exportjobflow.py [-h] (-fn FLOWNAME | -ff FLOWFILE) -d DIRECTORY [-t]
                        [--debug]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-fn, --flowname FLOWNAME` | Flow name to export (Viya Job Flow object name). Choose this or pass a flowfile. | Default: `None` |
| `-ff, --flowfile FLOWFILE` | Path to an existing flow definition file to export. Choose this or pass a flowname. | Default: `None` |
| `-d, --directory DIRECTORY` | Directory to store Export Packages | Required; Default: `'TEMP'` |
| `-t, --transferremove` | Remove transfer package from SAS Viya after download to JSON file | Default: `False` |
| `--debug` | Debug: shows the requests file created | Default: `False` |

## exportstudioflowcode.py

[Source](../exportstudioflowcode.py)

Create code from a SAS Studio flow or from all flows in folder.

```text
usage: exportstudioflowcode.py [-h] -t {Flow,Folder} -n NAME -d DIRECTORY
                               [--includeinitcode] [--includewrappercode]
                               [--debug]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-t, --type TYPE` | Enter 'Flow' for a single flow or 'Folder' for all flows in a folder. | Required; Choices: `Flow, Folder`; Default: `None` |
| `-n, --name NAME` | Name of Flow or Folder Path. | Required; Default: `None` |
| `-d, --directory DIRECTORY` | Directory to store generated code | Required; Default: `None` |
| `--includeinitcode` | Include init code (default False) | Default: `False` |
| `--includewrappercode` | Include wrapper code (default False) | Default: `False` |
| `--debug` | Include wrapper code (default False) | Default: `False` |

## getactivityrecords.py

[Source](../getactivityrecords.py)

```text
usage: getactivityrecords.py [-h] [-l LIMIT] [-t TYPE] [-a APPLICATION]
                             [-c ACTION] [-d ADMIN_ACTION] [-s STATE]
                             [-u USER] [-A AFTER] [-B BEFORE] [-S SORTBY]
                             [-o {csv,json,simple,simplejson}]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-l, --limit LIMIT` | Maximum number of records to display | Default: `'1000'` |
| `-t, --type TYPE` | Filter by entry Type | Default: `None` |
| `-a, --application APPLICATION` | Filter by entry Application | Default: `None` |
| `-c, --action ACTION` | Filter by entry Action | Default: `None` |
| `-d, --admin-action ADMIN_ACTION` | Filter by Administrative Action | Default: `None` |
| `-s, --state STATE` | Filter by entry State | Default: `None` |
| `-u, --user USER` | Filter by Username | Default: `None` |
| `-A, --after AFTER` | Filter entries that are created after the specified timestamp. For example: 2020-01-03 or 2020-01-03T18:15Z | Default: `None` |
| `-B, --before BEFORE` | Filter entries that are created before the specified timestamp. For example: 2020-01-03 or 2020-01-03T18:15Z | Default: `None` |
| `-S, --sortby SORTBY` | Sort the output ascending by this field | Default: `'timeStamp'` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson`; Default: `'csv'` |

## getauditrecords.py

[Source](../getauditrecords.py)

```text
usage: getauditrecords.py [-h] [-a APPLICATION] [-l LIMIT] [-t TYPE]
                          [-c ACTION] [-s STATE] [-u USER] [-A AFTER]
                          [-B BEFORE] [-S SORTBY]
                          [-o {csv,json,simple,simplejson}]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-a, --application APPLICATION` | Filter by Application or Service name | Default: `None` |
| `-l, --limit LIMIT` | Maximum number of records to display | Default: `'1000'` |
| `-t, --type TYPE` | Filter by entry Type | Default: `None` |
| `-c, --action ACTION` | Filter by entry Action | Default: `None` |
| `-s, --state STATE` | Filter by entry State | Default: `None` |
| `-u, --user USER` | Filter by Username | Default: `None` |
| `-A, --after AFTER` | Filter entries that are created after the specified timestamp. For example: 2020-01-03 or 2020-01-03T18:15Z | Default: `None` |
| `-B, --before BEFORE` | Filter entries that are created before the specified timestamp. For example: 2020-01-03 or 2020-01-03T18:15Z | Default: `None` |
| `-S, --sortby SORTBY` | Sort the output ascending by this field | Default: `'timeStamp'` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson`; Default: `'csv'` |

## getcomputecontextattributes.py

[Source](../getcomputecontextattributes.py)

List attributes in an existing compute context. If you want to add, remove or update a compute context, use setcomputecontextattributes.py.

```text
usage: getcomputecontextattributes.py [-h] -n NAME
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Compute context name | Required; Default: `None` |

## getconfigurationproperties.py

[Source](../getconfigurationproperties.py)

Return a set of configuration properties

```text
usage: getconfigurationproperties.py [-h] -c CONFIGURATION
                                     [-o {csv,json,simple,simplejson}]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-c, --configuration CONFIGURATION` | Enter the configuration definition. | Required; Default: `None` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson`; Default: `'json'` |

## getdefaultqkb.py

[Source](../getdefaultqkb.py)

Get default QKB setting for SAS CAS and Compute engines

```text
usage: getdefaultqkb.py [-h] [--engine [{cas,compute} ...]]
                        [-o {csv,json,simple,simplejson}]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `--engine ENGINE` | Engine(s) to query: cas, compute. If omitted, both are returned. | Choices: `cas, compute`; Default: `None`; Arguments: `*` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson`; Default: `'json'` |

## getfolderid.py

[Source](../getfolderid.py)

```text
usage: getfolderid.py [-h] -f FOLDERPATH [-o {csv,json,simple,simplejson}]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --folderpath FOLDERPATH` | Enter the path to the viya folder. | Required; Default: `None` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson`; Default: `'csv'` |

## getimportresults.py

[Source](../getimportresults.py)

```text
usage: getimportresults.py [-h] [-i ID] [-f FILTER] [-l LIMIT] [-p PAGELIMIT]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-i, --id ID` | Specify the package ID being imported. | Default: `None` |
| `-f, --filter FILTER` | Set a custom filter for objects, for example eq(createdBy,sasdemo). | Default: `None` |
| `-l, --limit LIMIT` | Specify the number of records to pull in each REST API call. Default is 10. | Default: `10`; Type: `int` |
| `-p, --pagelimit PAGELIMIT` | Specify the number of pages to pull before stopping. Default is 10. | Default: `10`; Type: `int` |

## getloglevels.py

[Source](../getloglevels.py)

```text
usage: getloglevels.py [-h] [--notrace] [--nodebug] [--kubectl]
                       [--namespace NAMESPACE] [--kubeconfig KUBECONFIG]
                       [--verbose]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `--notrace` | Set any loggers set to trace down to debug. | Default: `False` |
| `--nodebug` | Set any loggers set to debug down to info. | Default: `False` |
| `--kubectl` | Enable checking for logging levels set in consul using kubectl exec. | Default: `False` |
| `--namespace NAMESPACE` | The kubernetes namespace to use for kubectl commands, default is viya. | Default: `'viya'` |
| `--kubeconfig KUBECONFIG` | The kubeconfig file to use for kubectl commands, default is ~/.kube/config. | Default: `None` |
| `--verbose` | Include all loggers in the output, not just those set to debug or trace. | Default: `False` |

## getpath.py

[Source](../getpath.py)

```text
usage: getpath.py [-h] -u OBJECTURI [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-u, --objecturi OBJECTURI` | Object URI of folder or other object that can be contained within a folder. | Required; Default: `None` |
| `-d, --debug` | Debug | Default: `False` |

## getpathsplus.py

[Source](../getpathsplus.py)

```text
usage: getpathsplus.py [-h] [-m [{all,name,createdby}]] [-o] -u [URILIST ...]
                       [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-m, --more MORE` | Returns additional details for each Object (default: all) | Choices: `all, name, createdby`; Default: `None`; Arguments: `?` |
| `-o` | Prepends ObjectURIs to each row output | Default: `None` |
| `-u, --objecturi URILIST` | Object URI of folder or other object contained within a folder. Lists should be used WITHOUT quotes and delimited with a space. E.g. getpathsplus.py -u /files/files/1234 /files/files/abcd  | Required; Default: `['objecturi1', 'objecturi2', 'objecturi3']`; Arguments: `*`; Type: `str` |
| `-d, --debug` | Debug | Default: `False` |

## getposixgroups.py

[Source](../getposixgroups.py)

Display POSIX attributes for group or all groups of no groups specified

```text
usage: getposixgroups.py [-h] [-g GROUP] [-c] [-l LIMIT] [-d]
                         [-o {csv,json,simple,simplejson}]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-g, --group GROUP` | Enter the group id | Default: `'all'` |
| `-c, --custom` | Display local (custom) groups as well | Default: `False` |
| `-l, --limit LIMIT` | Specify the number of records to pull. Default is 1000. | Default: `1000`; Type: `int` |
| `-d, --debug` | Debug | Default: `False` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson`; Default: `'simplejson'` |

## getposixidentity.py

[Source](../getposixidentity.py)

Display POSIX attributes for User or ALL users(default)

```text
usage: getposixidentity.py [-h] [-u USER] [-q QUERY] [-c] [-l LIMIT] [-d]
                           [-o {csv,json,simple,simplejson}]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-u, --user USER` | Enter the user id or leave blank for all users. | Default: `'all'` |
| `-q, --query QUERY` | Enter a valid rest query of usernames. | Default: `'not(blank(id))'` |
| `-c, --custom` | Display local (custom) users as well | Default: `False` |
| `-l, --limit LIMIT` | Specify the number of records to pull. Default is 1000. | Default: `1000`; Type: `int` |
| `-d, --debug` | Debug | Default: `False` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson`; Default: `'json'` |

## getreportdatasources.py

[Source](../getreportdatasources.py)

List a Visual Analytics report's datasources

```text
usage: getreportdatasources.py [-h] (-r REPORTID | -p REPORTPATH)
                               [-o {simple,simplejson,csv}] [-i]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-r, --reportId REPORTID` | ID of the report to export | Default: `None` |
| `-p, --reportPath REPORTPATH` | The full path to the report | Default: `None` |
| `-o, --output OUTPUT` | The type of output to receive (default: simple) | Choices: `simple, simplejson, csv`; Default: `'simple'` |
| `-i, --info` | Print report info to console | Default: `False` |

## getruleid.py

[Source](../getruleid.py)

```text
usage: getruleid.py [-h] [-u OBJECTURI] [-c CONTAINERURI] -p PRINCIPAL
                    [-o {csv,json,simple,simplejson}]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-u, --objecturi OBJECTURI` | objectURI. You must specify either -u objectURI or -c containerURI. | Default: `None` |
| `-c, --containeruri CONTAINERURI` | containerURI. You must specify either -u objectURI or -c containerURI. | Default: `None` |
| `-p, --principal PRINCIPAL` | Enter the identity name or authenticatedUsers, everyone or guest | Required; Default: `None` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson`; Default: `'json'` |

## getschedulehistory.py

[Source](../getschedulehistory.py)

```text
usage: getschedulehistory.py [-h] [-f FILTER] [-l LIMIT] [-p PAGELIMIT]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --filter FILTER` | Set a custom filter for objects, for example eq(createdBy,sasdemo). | Default: `None` |
| `-l, --limit LIMIT` | Specify the number of records to pull in each REST API call. Default is 10. | Default: `10`; Type: `int` |
| `-p, --pagelimit PAGELIMIT` | Specify the number of pages to pull before stopping. Default is 10. | Default: `10`; Type: `int` |

## gettransfermapping.py

[Source](../gettransfermapping.py)

Create a JSON Mapping File from a Viya Mapping Set.

```text
usage: gettransfermapping.py [-h] [-n NAME] -d DIRECTORY [--debug] [-q]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Name of the Mapping Set (also the name of the output file). | Default: `'@systemMap'` |
| `-d, --directory DIRECTORY` | Directory where mapping files are written. | Required; Default: `None` |
| `--debug` | Debug | Default: `False` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |

## importcaslibs.py

[Source](../importcaslibs.py)

Import JSON files that define path-based CASLIBS from directory. All json files in directory will be imported.

```text
usage: importcaslibs.py [-h] -d DIRECTORY [-q] [-su] [-v]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --directory DIRECTORY` | Directory that contains JSON caslib definition files to import | Required; Default: `None` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |
| `-su, --superuser` | Runs the CASLIB create process with superuser permissions. | Default: `False` |
| `-v, --verbose` | Show merged stdout/stderr for successful commands and pass --verbose to CLI. | Default: `False` |

## importconfiguration.py

[Source](../importconfiguration.py)

Import JSON files that update Viya configuration. All json files in directory will be imported.

```text
usage: importconfiguration.py [-h] -d DIRECTORY [-q]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --directory DIRECTORY` | Directory that contains JSON configuration definition files to import | Required; Default: `None` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |

## importpackages.py

[Source](../importpackages.py)

Import JSON files from directory. All json files in directory will be imported.

```text
usage: importpackages.py [-h] -d DIRECTORY [-m MAPPING] [-ea] [-q]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --directory DIRECTORY` | Directory that contains JSON files to import | Required; Default: `None` |
| `-m, --mapping MAPPING` | A mapping file to use with the import. | Default: `None` |
| `-ea, --excludeauthorization` | Exclude the import of authorization rules. | Default: `False` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |

## importtemplates.py

[Source](../importtemplates.py)

Upload templates

```text
usage: importtemplates.py [-h] -d DIRECTORY [-q]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --directory DIRECTORY` | Directory that contains JSON files to import | Required; Default: `None` |
| `-q, --quiet` | Suppress the confirmation prompt. | Default: `False` |

## listallcasservercachestatus.py

[Source](../listallcasservercachestatus.py)

```text
usage: listallcasservercachestatus.py [-h] [--noheader] [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `--noheader` | Do not print the header row | Default: `False` |
| `-d, --debug` | Debug | Default: `False` |

## listcaslibs.py

[Source](../listcaslibs.py)

```text
usage: listcaslibs.py [-h] [-n NAME] [--noheader] [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Caslib name contains | Default: `None` |
| `--noheader` | Do not print the header row | Default: `False` |
| `-d, --debug` | Debug | Default: `False` |

## listcaslibs_example.py

[Source](../listcaslibs_example.py)

```text
usage: listcaslibs_example.py [-h] -s SERVER [-o {csv,json,simple,simplejson}]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-s, --server SERVER` | The CAS SERVER. | Required; Default: `'cas-shared-default'` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson`; Default: `'csv'` |

## listcaslibsandeffectiveaccess.py

[Source](../listcaslibsandeffectiveaccess.py)

```text
usage: listcaslibsandeffectiveaccess.py [-h] [-n NAME] [--noheader] [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Caslib name contains | Default: `None` |
| `--noheader` | Do not print the header row | Default: `False` |
| `-d, --debug` | Debug | Default: `False` |

## listcastables.py

[Source](../listcastables.py)

```text
usage: listcastables.py [-h] [-n NAME] [--noheader] [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Table name contains | Default: `None` |
| `--noheader` | Do not print the header row | Default: `False` |
| `-d, --debug` | Debug | Default: `False` |

## listcastablesandeffectiveaccess.py

[Source](../listcastablesandeffectiveaccess.py)

```text
usage: listcastablesandeffectiveaccess.py [-h] [-n NAME] [--noheader]
                                          [--rowlevelsecurity]
                                          [--sourcetables] [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Table name contains | Default: `None` |
| `--noheader` | Do not print the header row | Default: `False` |
| `--rowlevelsecurity` | Get row level security (i.e. table filters on the select permission) | Default: `False` |
| `--sourcetables` | Get effective permissions for source tables, rather than in-memory tables which is the default | Default: `False` |
| `-d, --debug` | Debug | Default: `False` |

## listcontent.py

[Source](../listcontent.py)

List folder and its sub-folders and content.

```text
usage: listcontent.py [-h] -f FOLDERPATH [-v]
                      [-o {csv,json,simple,simplejson}] [--debug]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --folderpath FOLDERPATH` | Enter the path to the viya folder to start the listing. | Required; Default: `None` |
| `-v, --verbosecsv` | Verbose CSV(only used with -o=csv)  | Default: `False` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson`; Default: `'json'` |
| `--debug` | Debug | Default: `False` |

## listfiles.py

[Source](../listfiles.py)

Query and list files stored in the Viya Infrastructure Data sSrver.

```text
usage: listfiles.py [-h] [-n NAME] [-c TYPE] [-p PARENT] [-pf PARENTFOLDER]
                    [-d DAYS] [-do {older,younger}] [-m MODIFIEDBY]
                    [-s SORTBY] [-so {ascending,descending}] [-v]
                    [-o {csv,json,simple,simplejson}] [--debug]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Name contains | Default: `None` |
| `-c, --type TYPE` | Content Type in. | Default: `None` |
| `-p, --parent PARENT` | ParentURI starts with. | Default: `None` |
| `-pf, --parentfolder PARENTFOLDER` | Parent Folder Name. | Default: `None` |
| `-d, --days DAYS` | List files older or younger than this number of days | Default: `'-1'` |
| `-do, --olderoryounger OLDERORYOUNGER` | For the date subsetting specify older or younger | Choices: `older, younger`; Default: `'older'` |
| `-m, --modifiedby MODIFIEDBY` | Last modified id equals | Default: `None` |
| `-s, --sortby SORTBY` | Sort the output by this field | Default: `'modifiedTimeStamp'` |
| `-so, --sortorder SORTORDER` | Sort order | Choices: `ascending, descending`; Default: `'descending'` |
| `-v, --verbosecsv` | Verbose CSV(only used with -o=csv)  | Default: `True` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson`; Default: `'json'` |
| `--debug` | Debug | Default: `False` |

## listgroupsandmembers.py

[Source](../listgroupsandmembers.py)

```text
usage: listgroupsandmembers.py [-h] [--id ID] [--name NAME]
                               [--type {user,group}]
                               [--source {local,scim,ldap}] [--noheader] [-e]
                               [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `--id ID` | Subset based on group id containing a string | Default: `None` |
| `--name NAME` | Subset based on name containing a string | Default: `None` |
| `--type TYPE` | Subset based on type containing a string | Choices: `user, group`; Default: `None` |
| `--source SOURCE` | Subset based on providerId containing a string | Choices: `local, scim, ldap`; Default: `None` |
| `--noheader` | Do not print the header row | Default: `False` |
| `-e, --email` | Show email addresses for users | Default: `False` |
| `-d, --debug` | Debug | Default: `False` |

## listmemberswithpath.py

[Source](../listmemberswithpath.py)

```text
usage: listmemberswithpath.py [-h] -u OBJECTURI [-r] [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-u, --objecturi OBJECTURI` | Object URI of folder or other object that can be contained within a folder. | Required; Default: `None` |
| `-r, --recursive` | Debug | Default: `False` |
| `-d, --debug` | Debug | Default: `False` |

## listmodelobjects.py

[Source](../listmodelobjects.py)

```text
usage: listmodelobjects.py [-h] [-n NAME] [-c TYPE] [-d DAYS] [-m MODIFIEDBY]
                           [-s SORTBY] [-o {csv,json,simple}] [--debug]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Name contains | Default: `None` |
| `-c, --type TYPE` | Content Type (model, project or repository) | Default: `'model'` |
| `-d, --days DAYS` | List files older than this number of days | Default: `'-1'` |
| `-m, --modifiedby MODIFIEDBY` | Last modified id equals | Default: `None` |
| `-s, --sortby SORTBY` | Sort the output descending by this field | Default: `'name'` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple`; Default: `'csv'` |
| `--debug` | Debug | Default: `False` |

## listreports.py

[Source](../listreports.py)

List Viya Reports and their folder path.

```text
usage: listreports.py [-h] [-n NAME] [-f FOLDERPATH] [-c CHANGEDDAYS]
                      [-m MODIFIEDBY] [-o {csv,json,simple}]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Name contains? | Default: `None` |
| `-f, --folderpath FOLDERPATH` | Folder Path starts with? | Default: `'/'` |
| `-c, --changeddays CHANGEDDAYS` | Reports changed in the how many days (defaults to 15 years)? | Default: `'5475'` |
| `-m, --modifiedby MODIFIEDBY` | Last modified id equals? | Default: `None` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple`; Default: `'csv'` |

## listrules.py

[Source](../listrules.py)

List rules for a principal and/or an endpoint

```text
usage: listrules.py [-h] [-u URI] [-p PRINCIPAL]
                    [-o {csv,json,simple,simplejson}]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-u, --uri URI` | Enter a string that the objecturi contains. | Default: `'none'` |
| `-p, --principal PRINCIPAL` | Enter the identity name or authenticatedUsers, everyone or guest | Default: `'none'` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson`; Default: `'json'` |

## listtransferpackages.py

[Source](../listtransferpackages.py)

Query and list transfer packages stored in the infrastructure data server.

```text
usage: listtransferpackages.py [-h] [-n NAME] [-m MODIFIEDBY] [-c CREATEDBY]
                               [-d DAYS] [-do {older,younger}] [-s SORTBY]
                               [-so {ascending,descending}]
                               [-o {csv,json,simple,simplejson}] [--debug]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Name contains | Default: `None` |
| `-m, --modifiedby MODIFIEDBY` | Last modified id equals | Default: `None` |
| `-c, --createdby CREATEDBY` | Created id equals | Default: `None` |
| `-d, --days DAYS` | List files older than this number of days | Default: `'-1'` |
| `-do, --olderoryounger OLDERORYOUNGER` | For the date subsetting specify older or younger | Choices: `older, younger`; Default: `'older'` |
| `-s, --sortby SORTBY` | Sort the output descending by this field | Default: `'modifiedTimeStamp'` |
| `-so, --sortorder SORTORDER` | Sort order | Choices: `ascending, descending`; Default: `'descending'` |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson`; Default: `'json'` |
| `--debug` | Debug | Default: `False` |

## loadcasdata.py

[Source](../loadcasdata.py)

Load CAS data: File Format: column1=caslib,column2=tablename,column3=casserver

```text
usage: loadcasdata.py [-h] -f FILE [--debug] [--skipfirstrow]
                      [--encoding ENCODING]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --file FILE` | Full path to csv file containing data to load  | Required; Default: `None` |
| `--debug` | Debug | Default: `False` |
| `--skipfirstrow` | Skip the first row if it is a header. | Default: `False` |
| `--encoding ENCODING` | default is utf-8 for python3 | Default: `'utf-8'` |

## loadcasformats.py

[Source](../loadcasformats.py)

Load CAS data: File Format: column1=format library,column2=full path to file ,colum3=cas library,column4=casserver

```text
usage: loadcasformats.py [-h] -f FILE [--debug] [--skipfirstrow]
                         [--encoding ENCODING]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --file FILE` | Full path to csv file containing formatso load  | Required; Default: `None` |
| `--debug` | Debug | Default: `False` |
| `--skipfirstrow` | Skip the first row if it is a header. | Default: `False` |
| `--encoding ENCODING` | default is utf-8 for python3 | Default: `'utf-8'` |

## loginviauthinfo.py

[Source](../loginviauthinfo.py)

Authinfo File

```text
usage: loginviauthinfo.py [-h] [-f FILE]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --file FILE` | Enter the path to the authinfo file. | Default: `'.authinfo'` |

## mergeuserfolders.py

[Source](../mergeuserfolders.py)

Merge user folders in SAS Viya Platform based on account ID changes.

```text
usage: mergeuserfolders.py [-h] [--csv CSV] [--commit] [--old-id OLD_ID]
                           [--new-id NEW_ID] [--merge] [--debug]
                           [--skip-identity-validation]
                           [--original-root-folder-id ORIGINAL_ROOT_FOLDER_ID]
                           [--new-root-folder-id NEW_ROOT_FOLDER_ID]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `--csv CSV` | Path to the CSV file containing old and new user IDs. | Default: `None` |
| `--commit` | Commit changes (default is dry run). | Default: `False` |
| `--old-id OLD_ID` | Old user account ID. | Default: `None` |
| `--new-id NEW_ID` | New user account ID. | Default: `None` |
| `--merge` | Merge content from old user folder to new user folder. | Default: `False` |
| `--debug` | Enable debug logging. | Default: `False` |
| `--skip-identity-validation` | Skip validation of user IDs in the Viya identities service. | Default: `False` |
| `--original-root-folder-id ORIGINAL_ROOT_FOLDER_ID` | Folder ID for the /Users folder to move content from. | Default: `None` |
| `--new-root-folder-id NEW_ROOT_FOLDER_ID` | Folder ID for the /Users folder to move content to. | Default: `None` |

## modifydomain.py

[Source](../modifydomain.py)

Modify a Domain

```text
usage: modifydomain.py [-h] {password,oauth2.0,cryptDomain,connection} ...
```

### Subcommands

#### `password`

Update credentials on password domain

```text
usage: modifydomain.py password [-h] -n NAME -it {user,group,client} -i
                                IDENTITY [--debug] -uid USERID -pw PASSWORD
```

##### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Domain name. | Required; Default: `None` |
| `-it, --identitytype IDENTITYTYPE` | User, Group or Client | Required; Choices: `user, group, client`; Default: `None` |
| `-i, --identity IDENTITY` | List of users OR list of groups (comma seperated) | Required; Default: `None` |
| `--debug` | Debug | Default: `False` |
| `-uid, --userid USERID` | Name of credential account | Required; Default: `None` |
| `-pw, --password PASSWORD` | Password of credential user | Required; Default: `None` |

#### `oauth2.0`

Update token on Token(oauth2.0) Domain

```text
usage: modifydomain.py oauth2.0 [-h] -n NAME -it {user,group,client} -i
                                IDENTITY [--debug]
```

##### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Domain name. | Required; Default: `None` |
| `-it, --identitytype IDENTITYTYPE` | User, Group or Client | Required; Choices: `user, group, client`; Default: `None` |
| `-i, --identity IDENTITY` | List of users OR list of groups (comma seperated) | Required; Default: `None` |
| `--debug` | Debug | Default: `False` |

#### `cryptDomain`

Update encryption key on  cryptDomain

```text
usage: modifydomain.py cryptDomain [-h] -n NAME -it {user,group,client} -i
                                   IDENTITY [--debug] -k KEY
```

##### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Domain name. | Required; Default: `None` |
| `-it, --identitytype IDENTITYTYPE` | User, Group or Client | Required; Choices: `user, group, client`; Default: `None` |
| `-i, --identity IDENTITY` | List of users OR list of groups (comma seperated) | Required; Default: `None` |
| `--debug` | Debug | Default: `False` |
| `-k, --key KEY` | Encryption Key | Required; Default: `None` |

#### `connection`

Update account on connection domain

```text
usage: modifydomain.py connection [-h] -n NAME -it {user,group,client} -i
                                  IDENTITY [--debug] -uid USERID
```

##### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Domain name. | Required; Default: `None` |
| `-it, --identitytype IDENTITYTYPE` | User, Group or Client | Required; Choices: `user, group, client`; Default: `None` |
| `-i, --identity IDENTITY` | List of users OR list of groups (comma seperated) | Required; Default: `None` |
| `--debug` | Debug | Default: `False` |
| `-uid, --userid USERID` | User Id | Required; Default: `None` |

## modifyglobalcaslib.py

[Source](../modifyglobalcaslib.py)

Import JSON files that update Viya configuration. All json files in directory will be imported.

```text
usage: modifyglobalcaslib.py [-h] -o {list,grant,revoke} [-i ID]
                             [-t {user,group}] [--cas CAS]
                             [--scope {global,session}]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-o, --operator OPERATOR` | Option to list, grant or revoke access to special CASLIBs | Required; Choices: `list, grant, revoke`; Default: `None` |
| `-i, --id ID` | A user or group ID | Default: `None` |
| `-t, --idtype IDTYPE` | 'user' or 'group' | Choices: `user, group`; Default: `None` |
| `--cas CAS` | Sets a non-default CAS Server. | Default: `'cas-shared-default'` |
| `--scope SCOPE` | 'global' (default) or 'session' | Choices: `global, session`; Default: `'global'` |

## movecontent.py

[Source](../movecontent.py)

Move content from a source to a target folder

```text
usage: movecontent.py [-h] -s SOURCEFOLDER -t TARGETFOLDER [-q]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-s, --sourcefolder SOURCEFOLDER` | Enter the path to the source folder. | Required; Default: `None` |
| `-t, --targetfolder TARGETFOLDER` | Enter the path to the source folder. | Required; Default: `None` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |

## removecaslibs.py

[Source](../removecaslibs.py)

Delete CASLIBs defined in JSON files in a directory.

```text
usage: removecaslibs.py [-h] -d DIRECTORY [-q] [-su] [-v]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --directory DIRECTORY` | Directory containing JSON caslib definition files | Required; Default: `None` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |
| `-su, --superuser` | Run commands with superuser permissions. | Default: `False` |
| `-v, --verbose` | Show merged stdout/stderr for successful commands and pass --verbose to CLI. | Default: `False` |

## setcomputecontextattributes.py

[Source](../setcomputecontextattributes.py)

Add attributes to an existing compute context.

```text
usage: setcomputecontextattributes.py [-h] -n NAME [-a [ADD]] [-v [VALUE]]
                                      [-r [REMOVE]]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Compute context name | Required; Default: `None` |
| `-a, --add ADD` | Single attribute to add or update. | Default: `None`; Arguments: `?` |
| `-v, --value VALUE` | Value to set attribute to. Only has any effect if the arguments also specify an attribute to add or update with -a. | Default: `None`; Arguments: `?` |
| `-r, --remove REMOVE` | Single attribute to remove. If the compute context does not have this attribute, nothing happens. | Default: `None`; Arguments: `?` |

## setconfigurationproperties.py

[Source](../setconfigurationproperties.py)

Import JSON files that update Viya configuration. Read JSON from a file (-f) or from STDIN (pipe) using -f - or by piping without -f.

```text
usage: setconfigurationproperties.py [-h] [-o {csv,json,simple,simplejson}]
                                     [-f FILE]
                                     [--ignore-items-keys [IGNORE_ITEMS_KEYS ...]]
                                     [--ignore-metadata-keys [IGNORE_METADATA_KEYS ...]]
                                     [--include-keys [INCLUDE_KEYS ...]]
                                     [--dryrun]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-o, --output OUTPUT` |  | Choices: `csv, json, simple, simplejson`; Default: `'json'` |
| `-f, --file FILE` | The JSON configuration definition to import | Default: `None` |
| `--ignore-items-keys IGNORE_ITEMS_KEYS` |  | Default: `['id', 'links']`; Arguments: `*` |
| `--ignore-metadata-keys IGNORE_METADATA_KEYS` |  | Default: `['createdBy', 'creationTimeStamp', 'modifiedBy', 'modifiedTimeStamp']`; Arguments: `*` |
| `--include-keys INCLUDE_KEYS` |  | Default: `['version', 'accept', 'name', 'items']`; Arguments: `*` |
| `--dryrun` | Simulate the operation without applying changes | Default: `False` |

## setdefaultqkb.py

[Source](../setdefaultqkb.py)

Set the default QKB locale and QKB name for SAS Viya CAS and Compute engines.

```text
usage: setdefaultqkb.py [-h] --engine [{cas,compute} ...] --locale LOCALE
                        --qkb QKB [--output-file OUTPUT_FILE]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `--engine ENGINE` | Engine(s) to update: cas, compute, or both. | Required; Choices: `cas, compute`; Default: `None`; Arguments: `*` |
| `--locale LOCALE` | Locale to set, e.g. ENUSA. | Required; Default: `None` |
| `--qkb QKB` | QKB name to set, e.g. 'QKB CI 33'. | Required; Default: `None` |
| `--output-file OUTPUT_FILE` | Path for the temporary JSON payload file. Default: /tmp/qkb_update.json | Default: `'/tmp/qkb_update.json'` |

## setfiletypedefname.py

[Source](../setfiletypedefname.py)

```text
usage: setfiletypedefname.py [-h] [--filter FILTER] [--write]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `--filter FILTER` | Set a custom filter for objects, for example eq(createdBy,sasdemo). | Default: `None` |
| `--write` | Make the specified changes. | Default: `False` |

## setjobrequestexpire.py

[Source](../setjobrequestexpire.py)

```text
usage: setjobrequestexpire.py [-h] [-e] [-f FILTER] [-d DURATION] [-w]
                              [-l LIMIT] [-p PAGELIMIT]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-e, --empty` | Filter on objects without an expiration set. | Default: `False` |
| `-f, --filter FILTER` | Set a custom filter for objects, for example eq(createdBy,sasdemo). | Default: `None` |
| `-d, --duration DURATION` | Specify the expiration period in W3C XML duration format. Default is PT72H (72 hours) | Default: `'PT72H'` |
| `-w, --write` | Make the specified changes. | Default: `False` |
| `-l, --limit LIMIT` | Specify the number of records to pull in each REST API call. Default is 10. | Default: `10`; Type: `int` |
| `-p, --pagelimit PAGELIMIT` | Specify the number of pages to pull before stopping. Default is 10. | Default: `10`; Type: `int` |

## setjobrequestfolder.py

[Source](../setjobrequestfolder.py)

```text
usage: setjobrequestfolder.py [-h] [-f FILTER] [-w] -t TARGET [-l LIMIT]
                              [-p PAGELIMIT]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --filter FILTER` | Set a custom filter for objects, for example eq(createdBy,sasdemo). | Default: `None` |
| `-w, --write` | Make the specified changes. | Default: `False` |
| `-t, --target TARGET` | Set the target SAS Content path for the jobRequest. | Required; Default: `None` |
| `-l, --limit LIMIT` | Specify the number of records to pull in each REST API call. Default is 10. | Default: `10`; Type: `int` |
| `-p, --pagelimit PAGELIMIT` | Specify the number of pages to pull before stopping. Default is 10. | Default: `10`; Type: `int` |

## setobjectattribute.py

[Source](../setobjectattribute.py)

```text
usage: setobjectattribute.py [-h] -u URI -a ATTRIBUTE -v VALUE
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-u, --uri URI` | Specify the URI to update. | Required; Default: `None` |
| `-a, --attribute ATTRIBUTE` | Specify the attribute to update. | Required; Default: `None` |
| `-v, --value VALUE` | Specify the new value of the attribute. | Required; Default: `None` |

## setposixattributes.py

[Source](../setposixattributes.py)

Set POSIX attributes for User and Group (uid and gid) file format: principal type,principal,id of user or group, primary gid for users

```text
usage: setposixattributes.py [-h] -f FILE [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --file FILE` | Full path to csv containing posix attributes. | Required; Default: `None` |
| `-d, --debug` | Debug | Default: `False` |

## setup.py

[Source](../setup.py)

Setup pyviyatools

```text
usage: setup.py [-h] [--clilocation CLILOCATION]
                [--cliexecutable CLIEXECUTABLE]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `--clilocation CLILOCATION` | Enter the full path to the viya cli. | Default: `'/opt/sas/viya/home/bin/'` |
| `--cliexecutable CLIEXECUTABLE` | Enter the name of the viya cli executable. | Default: `'sas-viya'` |

## setupcopilotcredentials.py

[Source](../setupcopilotcredentials.py)

Set up SAS Viya Copilot Orders API credentials

```text
usage: setupcopilotcredentials.py [-h] [--client-id CLIENT_ID]
                                  [--client-secret CLIENT_SECRET]
                                  [--input-file INPUT_FILE] [--force]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `--client-id CLIENT_ID` | Orders API Client ID | Default: `None` |
| `--client-secret CLIENT_SECRET` | Orders API Client Secret | Default: `None` |
| `--input-file INPUT_FILE` | KEY=VALUE file containing Orders API credentials | Default: `None` |
| `--force` | Attempt to overwrite existing credential if it exists | Default: `False` |

## snapshotcontent.py

[Source](../snapshotcontent.py)

Export Viya content each piece of content to its own unique transfer package.

```text
usage: snapshotcontent.py [-h] -d DIRECTORY [-q] -f FOLDERPATH
                          [-c CHANGEDDAYS] [-t] [-l LIMIT]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --directory DIRECTORY` | Directory to store report packages. | Required; Default: `None` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |
| `-f, --folderpath FOLDERPATH` | Folder Path starts with. | Required; Default: `None` |
| `-c, --changeddays CHANGEDDAYS` | Content changed in the how many days (defaults to 1 day)? | Default: `'1'` |
| `-t, --transferremove` | Remove transfer file from Infrastructure Data Server after download. | Default: `False` |
| `-l, --limit LIMIT` | Specify the number of records to pull. Default is 1000. | Default: `1000`; Type: `int` |

## snapshotreports.py

[Source](../snapshotreports.py)

Export Viya Reports each to its own unique transfer package

```text
usage: snapshotreports.py [-h] -d DIRECTORY [-q] [-c CHANGEDDAYS]
                          [-m MODIFIEDBY] [-n NAME] [-f FOLDERPATH] [-t] [-i]
                          [-l LIMIT]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --directory DIRECTORY` | Directory to store report packages | Required; Default: `None` |
| `-q, --quiet` | Suppress the are you sure prompt. | Default: `False` |
| `-c, --changeddays CHANGEDDAYS` | Reports changed in the how many days (defaults to 1 day)? | Default: `'1'` |
| `-m, --modifiedby MODIFIEDBY` | Last modified id equals? | Default: `None` |
| `-n, --name NAME` | Name contains? | Default: `None` |
| `-f, --folderpath FOLDERPATH` | Folder Path starts with? | Default: `'/'` |
| `-t, --tranferremove` | Remove transfer file after download? | Default: `False` |
| `-i, --includeDependencies` | Specifies if dependencies want to be included for each of the reports being exported. | Default: `False` |
| `-l, --limit LIMIT` | Specify the number of records to pull. Default is 1000. | Default: `1000`; Type: `int` |

## submit_jobdef.py

[Source](../submit_jobdef.py)

Submit Job using job definition

```text
usage: submit_jobdef.py [-h] -id ID [-c CONTEXT] [-v]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-id ID` | Provide Job Definition ID | Required; Default: `None` |
| `-c, --context CONTEXT` | Provide Context Name. Default ['SAS Job Execution compute context'] | Default: `'SAS Job Execution compute context'` |
| `-v, --verbose` | Print Verbosity | Default: `False` |

## submit_jobreq.py

[Source](../submit_jobreq.py)

Submit Job using job definition

```text
usage: submit_jobreq.py [-h] -id ID [-v]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-id ID` | Provide Job Definition ID | Required; Default: `None` |
| `-v, --verbose` | Print Verbosity | Default: `False` |

## testfolderaccess.py

[Source](../testfolderaccess.py)

```text
usage: testfolderaccess.py [-h] -f FOLDERPATH -n NAME -t {user,group} -s
                           {grant,prohibit} -m
                           {read,update,delete,add,secure,remove} [-q] [-d]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --folderpath FOLDERPATH` | Enter the path to the viya folder. | Required; Default: `None` |
| `-n, --name NAME` | Enter the name of the user or group to test. | Required; Default: `None` |
| `-t, --principaltype PRINCIPALTYPE` | Enter the type of principal to test: user or group. | Required; Choices: `user, group`; Default: `None` |
| `-s, --setting SETTING` | Enter grant or prohibit as the expected setting for the permission being tested. | Required; Choices: `grant, prohibit`; Default: `None` |
| `-m, --permission PERMISSION` | Enter the permission to test. | Required; Choices: `read, update, delete, add, secure, remove`; Default: `None` |
| `-q, --quiet` |  | Default: `False` |
| `-d, --debug` |  | Default: `False` |

## toggleviyarules.py

[Source](../toggleviyarules.py)

Enables or Disables Viya rules in bulk.

```text
usage: toggleviyarules.py [-h] -f FILE -o {enable,disable,replace}
                          [--skipfirstrow] [-p PRINC]
                          [-ptype {group,user,guest,authenticated-users,everyone}]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --file FILE` | Full path to CSV file. Format of csv: 'objecturi,principal | Required; Default: `None` |
| `-o, --operator OPERATOR` | Option to enable, disable or replace rules | Required; Choices: `enable, disable, replace`; Default: `None` |
| `--skipfirstrow` | Skip first row/header of the input csv file | Default: `False` |
| `-p, --princ PRINC` | Requires operator option 'replace'. Sets the principal (account/group) name to be used for the replacement copies of the rules being applied. | Default: `None` |
| `-ptype, --princtype PRINCTYPE` | Requires operator option 'replace'. Sets the principal TYPE to be used for the replacement copies of the rules being created and applied. | Choices: `group, user, guest, authenticated-users, everyone`; Default: `None` |

## updatecomputecontext.py

[Source](../updatecomputecontext.py)

Update an existing compute context from a JSON file.

```text
usage: updatecomputecontext.py [-h] -n NAME -f FILE
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-n, --name NAME` | Compute context name | Required; Default: `None` |
| `-f, --file FILE` | JSON file containing updated definition of existing compute context. | Required; Default: `None` |

## updatedomain.py

[Source](../updatedomain.py)

Update a Viya Domain to add credentials from a csv file.

```text
usage: updatedomain.py [-h] -d DOMAIN -f FILE
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-d, --domain DOMAIN` | Existing Domain. | Required; Default: `None` |
| `-f, --file FILE` | A csv file containing groups and userids. | Required; Default: `None` |

## updatepreferences.py

[Source](../updatepreferences.py)

Update user preferences for a user or a group of users

```text
usage: updatepreferences.py [-h] -t {user,group,all} [-tn TARGETNAME] -pi
                            PREFERENCEID -pv PREFERENCEVALUE
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-t, --target TARGET` | Type the target of the update: user or group | Required; Choices: `user, group, all`; Default: `None` |
| `-tn, --targetname TARGETNAME` | ID of the user or group to which the update applies. | Default: `None` |
| `-pi, --preferenceid PREFERENCEID` | ID of the preference to be updated | Required; Default: `None` |
| `-pv, --preferencevalue PREFERENCEVALUE` | Value to be set for the preference | Required; Default: `None` |

## uploadfiles.py

[Source](../uploadfiles.py)

```text
usage: uploadfiles.py [-h] [-f FILE] [--folder FOLDER] [-w] -c CONTENT_PATH
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-f, --file FILE` | Specify one or more files to upload. | Default: `None` |
| `--folder FOLDER` | Specify a folder containing files to upload. | Default: `None` |
| `-w, --overwrite` | Overwrite existing files with the same name in the destination folder. | Default: `False` |
| `-c, --content-path CONTENT_PATH` | Specify the destination path in SAS Content where the files will be uploaded to. | Required; Default: `None` |

## validateviya.py

[Source](../validateviya.py)

```text
usage: validateviya.py [-h]
                       [-o {csv,json,simple,simplejson,passfail,passfail-full,report,report-full}]
                       [-g [filename]] [-c filename] [-v] [-s] [-d directory]
                       [-p PROGRAM]
```

### optional arguments

| Option | Description | Details |
| --- | --- | --- |
| `-o, --output OUTPUT` | Output Style | Choices: `csv, json, simple, simplejson, passfail, passfail-full, report, report-full`; Default: `'csv'` |
| `-g, --generate-tests filename` | Generate JSON Test Preferences File | Default: `None`; Arguments: `?` |
| `-c, --custom-tests filename` | Use a Custom Test Preferences File | Default: `None`; Arguments: `1`; Type: `FileType('r')` |
| `-v, --verbose` | Add Output Verbosity | Default: `False` |
| `-s, --silent` | Limit Output to Results Only | Default: `False` |
| `-d, --output-directory directory` | Output Directory for Generated Files | Default: `None` |
| `-p, --program PROGRAM` | Full Path to an External Program for Computation Tests | Default: `None` |
