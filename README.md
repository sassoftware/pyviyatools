# Python Tools for SAS Viya

The pyviyatools are a set of command-line tools that call the SAS Viya REST API's from python. The tools can be used to make direct calls to any rest-endpoint (like a CURL command) or to build additional tools that make multiple rest calls to provide more complex functionality. The tools are designed to be used in conjunction with the SAS Administration command line interfaces(CLI). A subset of the tools also make calls to the cli.

- [Python Tools for SAS Viya](#python-tools-for-sas-viya)
  - [Getting Started](#getting-started)
  - [Documentation](#documentation)
    - [Installing](#installing)
  - [Running](#running)
    - [Creating a Profile and Logging on](#creating-a-profile-and-logging-on)
    - [Certificates](#certificates)
    - [Using the tools](#using-the-tools)
  - [Available Tools](#available-tools)
  - [Troubleshooting](#troubleshooting)
  - [Developing with the existing functions](#developing-with-the-existing-functions)
  - [Contributing](#contributing)
  - [License](#license)
## Getting Started

You can find an inventory of pyviyatools at [inventory.md](inventory.md)

## Documentation

* SAS Open API's documented : https://developer.sas.com/apis/rest/
* Sample REST API calls : https://github.com/sassoftware/devsascom-rest-api-samples

Some other useful links

* https://developer.sas.com/apis/rest/#filters
* https://developer.sas.com/apis/rest/#pagination
* https://developer.sas.com/apis/rest/#sorting


### Installing

Please use the installation intructions in the file [INSTALL.md](INSTALL.md)

## Running

The pyviyatools use the SAS Administration CLI to authenticate to Viya. To use the tool you must create a profile and authenticate. The SAS Administration CLI is named sas-admin in Viya 3.x and sas-viya in Viya 4. 

This process is documented in the SAS Viya Administration guide here:

* Viya 3.3: http://documentation.sas.com/?cdcId=calcdc&cdcVersion=3.3&docsetId=calcli&docsetTarget=n1e2dehluji7jon1gk69yggc6i28.htm&locale=en
* Viya 3.4: http://documentation.sas.com/?cdcId=calcdc&cdcVersion=3.4&docsetId=calcli&docsetTarget=n1e2dehluji7jon1gk69yggc6i28.htm&locale=en
* Viya 3.5: https://documentation.sas.com/?cdcId=calcdc&cdcVersion=3.5&docsetId=calcli&docsetTarget=n1e2dehluji7jon1gk69yggc6i28.htm&locale=en
* Viya 4: https://documentation.sas.com/doc/en/sasadmincdc/default/calcli/titlepage.htm


### Creating a Profile and Logging on

> NOTE: on Viya 4 use sas-viya instead of sasasdm.

The tool will automatically use the default profile.

1. To create a profile as a SAS Administrator logon to the machine that contains the Viya CLI's
2. Run `/opt/sas/viya/home/bin/sas-admin profile init` and when prompted enter the base endpoint of your Viya server for example: http://myviyaserver.blah.com. You may enter your personal preference at the other prompts.
3. After you create the profile there are two options to authenticate
 * Run `/opt/sas/viya/home/bin/sas-admin auth login` to authenticate to Viya enter the userid and password of the SAS Administrator when prompted.
 *  Create an `.authinfo` file in your home directory with your userid and password and use **loginviauthinfo.py** to authenticate with the credentials in the file (you can use different authinfo files with the -f option)

The CLI allows for multiple profiles. To use a profile other than the default profile, for example newprofile

1. Create a named profile `sas-admin --profile newprofile profile init`
2. 3. Logon with the named profile `sas-admin --profile newprofile auth login`
4. Set the SAS_CLI_PROFILE environment variable to the name of the profile
* LINUX: `export SAS_CLI_PROFILE=newprofile`
* WINDOWS: `set SAS_CLI_PROFILE=newprofile`

1. When the  SAS_CLI_PROFILE is set the tool will use the profile stored in the variable
2. To revert to using the default variable reset the environment variable

* LINUX: `unset SAS_CLI_PROFILE`
* WINDOWS: `set SAS_CLI_PROFILE=`

### Certificates

The documentation https://documentation.sas.com/doc/en/sasadmincdc/default/calcli/titlepage.htm covers setting the certificate environment variables. You may need to set the following three variables.

```sh
export SSL_CERT_FILE="/opt/sas/spre/config/etc/SASSecurityCertificateFramework/cacerts/trustedcerts.pem"    
# else loginviauthinfo complains "Login failed due to an error with the security certificate. The certificate is signed by an unknown authority"

export REQUESTS_CA_BUNDLE=/opt/sas/viya/config/etc/SASSecurityCertificateFramework/cacerts/trustedcerts.pem
# else loginviauthinfo complains "ConnectionError: HTTPSConnectionPool(host='intviya01.race.sas.com', port=443): Max retries exceeded with url: / (Caused by SSLError(SSLError(1, u'[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:579)'),))"

export CAS_CLIENT_SSL_CA_LIST=/opt/sas/viya/config/etc/SASSecurityCertificateFramework/cacerts/vault-ca.crt
# else swat complains "ERROR: SSL Error: Missing CA trust list"
```

### Using the tools

The tools are self-documenting, for help on any tool call the tool passing `-h` or `--help`.

```sh
python *\<pathtotool\>\<toolname.py\>* -h
```

For example:

```sh
python3 importpackages.py -h
```
Will output:
```log
usage: importpackages.py [-h] -d DIRECTORY [-m MAPPING] [-ea] [-q]

Import JSON files from directory. All json files in directory will be
imported.

optional arguments:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Directory that contains JSON files to import
  -m MAPPING, --mapping MAPPING
                        A mapping file to use with the import.
  -ea, --excludeauthorization
                        Exclude the import of authorization rules.
  -q, --quiet           Suppress the are you sure prompt.

```

If you do not preface a tool with `python` the tools will automatically look for python im `/usr/bin/python` If your python is in a different path just call the tools using the `python` or `python3` command. For example.

```
python3 getfolderid.py -f /Public
```

## Available Tools

**callrestapi**

callrestapi is a general tool, and the building block for all the other tools.

callrestapi  will call the Viya REST API and return json or optionally a simplified output. It can call any viya REST method. (Like a curl command).

```sh
usage: callrestapi.py [-h] -e ENDPOINT -m {get,put,post,delete,patch}
                      [-i INPUTFILE] [-a ACCEPTTYPE] [-c CONTENTTYPE]
                      [-o {csv,json,simple,simplejson}] [-t] [-hf HEADERFILE]

Call the Viya REST API

optional arguments:
  -h, --help            show this help message and exit
  -e ENDPOINT, --endpoint ENDPOINT
                        Enter the REST endpoint e.g. /folders/folders
  -m {get,put,post,delete,patch}, --method {get,put,post,delete,patch}
                        Enter the REST method.
  -i INPUTFILE, --inputfile INPUTFILE
                        Enter the full path to an input json file
  -a ACCEPTTYPE, --accepttype ACCEPTTYPE
                        Enter REST Content Type you want returned e.g
                        application/vnd.sas.identity.basic+json
  -c CONTENTTYPE, --contenttype CONTENTTYPE
                        Enter REST Content Type for POST e.g
                        application/vnd.sas.identity.basic+json
  -o {csv,json,simple,simplejson}, --output {csv,json,simple,simplejson}
                        Output Style
  -t, --text            Display Simple Text Results.
  -hf HEADERFILE, --headerfile HEADERFILE
                        Enter the full path to a header json file
```


You must pass a method and endpoint. You can optionally pass json, content type headers or the -t flag to change output from json to basic text.

**List of some of the Additional Tools Available**

Additional tools provide more complex functionality by combining multiple calls to the callrestapi function, and post-processing the output that is returned.

* **getfolderid** returns the id of the folder based on the full folder path
* **deletefolder** deletes a folder based on the full folder path
* **deletefolderandcontent** deletes a folder and any reports that are stored in the folder
* **movecontent** moves the content from a source to a target folder
* **getconfigurationproperties** lists the name/value pairs of a configuration
* **testfolderaccess** tests if a user or group has access to a folder
* **createbinarybackup.py** creates a binary backup job
* **createdomain.py** creates an authentication domain
* **createpublishdest.py** creates CAS, Teradata or Hadoop publishing destinations
* **detetepublishdest.py** deletes publishing destinations
* **listrules.py** list authorization rules subset on a principal and/or a uri
* **loginviauthinfo.py** use an authinfo file to authenticate to the CLI
* **updateprefences.py** update preferences for a user or group of users
* **updatedomain.py** load a set of userids and passwords to a Viya domain from a csv file
* **createfolders.py** create a set of Viya folders from a csv file
* **explainaccess.py** explains access for a folder, object or service endpoint
* **getpath.py** return path of folder, report, or other object in folder
* **listmemberswithpath.py** lists members of a folder, recursively if desired
* **listcaslibs.py** list all CAS libraries on all servers
* **listcastables.py** list all CAS tables in all CAS libraries on all servers
* **listcaslibsandeffectiveaccess.py** list all effective access on all CAS libraries on all servers
* **listcastablesandeffectiveaccess.py** list all effective access on all CAS tables in all CAS libraries on all servers
* **listgroupsandmembers.py** list all groups and all their members
* **getauditrecords.py** lists audit records from SAS Infrastructure Data Server in CSV or JSON format using REST calls.
* **listmodelobjects.py** lists basic information about model content (models, projects and repositories).
* **applyfolderauthorization.py** apply authorization rules to folders in bulk from a source CSV file.
* **submit_jd_job.py** This file calls various functions from jobmodule.py. It will submit a job based on job definition id. Based on other arguments, it will either provide the sasout and saslog information if available in the location provided or it will display more information based on if verbose was selected. It will also display more information if needed based on log level selected.
* **submit_jr_job.py** This file calls various functions from jobmodule.py. It will submit a job based on job request id. Based on other arguments, it will either provide the sasout and saslog information if available in the location provided or it will display more information based on if verbose was selected. It will also display more information if needed based on log level selected.


Check back for additional tools and if you build a tool feel free to contribute it to the collection.

**Examples**

Many of the tools have examples of usage documented in  [EXAMPLES.md](EXAMPLES.md)

## Troubleshooting

The most common problem is an expired access token. You may see a message like:

    {"errorCode":0,"message":"Cannot convert access token to JSON","details":["traceId: 6bca23b2b3a2cfda","path: /folders/folders"],"remediation":null,"links":[ ],"version":2,"httpStatusCode":401}

To fix the problem generate a new access token: `/opt/sas/viya/home/bin/sas-admin auth login`

To see the current setup, including python and package versions, environment variable settings, profile information and current user. Run

`python showsetup.py`

If you get this error : Login failed. Error with security certificate.

Set the environment variable for the SSL certificate file. For example:

`export SSL_CERT_FILE=/opt/sas/viya/config/etc/SASSecurityCertificateFramework/cacerts/trustedcerts.pem`


If you get this error:

```log
Raise SSLError(e, request=request)
requests.exceptions.SSLError: HTTPSConnectionPool(host='intviya01.race.sas.com', port=443): Max retries exceeded with url: / (Caused by SSLError(SSLError(1, u'[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:579)'),))
```

Set the environment variable for the SSL certificate file. For example:

`export REQUESTS_CA_BUNDLE=/opt/sas/viya/config/etc/SASSecurityCertificateFramework/cacerts/trustedcerts.pem`

Encoding has been a problem. If you run into any encoding issues try using python3 the experience there is much better than python2.


## Developing with the existing functions

The file sharedfunctions.py contains a set of generic functions that make it easy to build additional tools.

*callrestapi* is the main function, called by many other programs and by the callrestapi program to make the REST calls. It accepts as parameters:

* reqval: the request value which is the rest endpoint for the request
* reqtype: the type of REST request, get,put, post, delete
* acceptType: optinal accept type content header
* contentType: optional content type content header
* data: optionally a python dictionary created from the json for the rest request
* stoponerror: whether the function will stop all further processing if an error occurs (default 0 to not stop)

We suggest you use [listcaslibs_example.py](listcaslibs_example.py) as a simple example to copy from if you wish to develop your own python scripts, and are new to Python or some of the concepts we have used. If one of the other existing tools is similar to what you want, of course you could use that as the basis for a new tool too.

## Contributing

We welcome your contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to submit contributions to this project.

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

