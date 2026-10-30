# Python Tools for SAS Viya <!-- omit in toc --> 

pyviyatools is a collection of command-line tools that call the SAS Viya REST APIs. The tools can make direct calls to REST endpoints or combine multiple calls to provide more complex functionality. They are designed to be used with the SAS Administration CLI; some tools also invoke the CLI directly.

- [Getting Started](#getting-started)
- [Documentation](#documentation)
- [Installing](#installing)
- [Running](#running)
  - [Creating a Profile and Logging on](#creating-a-profile-and-logging-on)
  - [Certificates](#certificates)
  - [Running in insecure mode](#running-in-insecure-mode)
  - [Using the tools](#using-the-tools)
- [Available Tools](#available-tools)
- [Troubleshooting](#troubleshooting)
- [Developing with the existing functions](#developing-with-the-existing-functions)
- [Contributing](#contributing)
- [License](#license)
## Getting Started

You can find an inventory of pyviyatools at [INVENTORY.md](INVENTORY.md)

## Documentation

* SAS Open API's documented : https://developer.sas.com/apis/rest/
* Sample REST API calls : https://github.com/sassoftware/devsascom-rest-api-samples

Some other useful links

* https://developer.sas.com/apis/rest/#filters
* https://developer.sas.com/apis/rest/#pagination
* https://developer.sas.com/apis/rest/#sorting


## Installing

Please use the installation instructions in the file [INSTALL.md](INSTALL.md)

## Running

The pyviyatools use the SAS Administration CLI profile and authentication token to access Viya. Create a profile and authenticate before running the tools. The CLI executable is named `sas-admin` in Viya 3.x and `sas-viya` in Viya 4.

This process is documented in the SAS Viya Administration guide here:

* Viya 3.3: http://documentation.sas.com/?cdcId=calcdc&cdcVersion=3.3&docsetId=calcli&docsetTarget=n1e2dehluji7jon1gk69yggc6i28.htm&locale=en
* Viya 3.4: http://documentation.sas.com/?cdcId=calcdc&cdcVersion=3.4&docsetId=calcli&docsetTarget=n1e2dehluji7jon1gk69yggc6i28.htm&locale=en
* Viya 3.5: https://documentation.sas.com/?cdcId=calcdc&cdcVersion=3.5&docsetId=calcli&docsetTarget=n1e2dehluji7jon1gk69yggc6i28.htm&locale=en
* Viya 4: https://documentation.sas.com/doc/en/sasadmincdc/default/calcli/titlepage.htm


### Creating a Profile and Logging on

> NOTE: on Viya 4 use sas-viya executable instead of sas-admin.

The tool will automatically use the default profile.

1. To create a profile as a SAS Administrator logon to the machine that contains the Viya CLI's
2. Run `/opt/sas/viya/home/bin/sas-admin profile init` and when prompted enter the base endpoint of your Viya server for example: http://myviyaserver.blah.com. You may enter your personal preference at the other prompts.
3. After you create a profile, authenticate in one of two ways:
   * Run `/opt/sas/viya/home/bin/sas-admin auth login` and follow the prompts.
   * Create an `.authinfo` file in your home directory and run `python3 loginviauthinfo.py` to authenticate with it. Use its `-f` option to specify a different file.

The CLI allows for multiple profiles. To use a profile other than the default profile, for example newprofile

1. Create a named profile: `sas-admin --profile newprofile profile init`
2. Log on with that profile: `sas-admin --profile newprofile auth login`
3. Set `SAS_CLI_PROFILE` to `newprofile`:
   * Linux/macOS: `export SAS_CLI_PROFILE=newprofile`
   * Windows Command Prompt: `set SAS_CLI_PROFILE=newprofile`

The tools use the profile named by `SAS_CLI_PROFILE` when it is set. To return to the default profile, unset the variable on Linux/macOS (`unset SAS_CLI_PROFILE`) or clear it in Windows Command Prompt (`set SAS_CLI_PROFILE=`).

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

### Running in insecure mode

If you have problems with certificates, pyviyatools can run in insecure mode, like the CLI. This is not recommended for production use. To run in insecure mode, set the `PYVIYA_INSECURE` environment variable.

```sh
export PYVIYA_INSECURE=True
```

Set it to `False` or unset it to verify certificates.

### Using the tools

Use Python 3 to run the tools. Each tool provides command-line help with `-h` or `--help`.

```sh
python3 <toolname.py> -h
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

Run a tool from the repository directory, or provide its path. For example:

```
python3 getfolderid.py -f /Public
```

## Available Tools

**callrestapi**

callrestapi is a general tool, and the building block for all the other tools.

callrestapi  will call the Viya REST API and return json or optionally a simplified output. It can call any viya REST method. (Like a curl command).

```sh
usage: callrestapi.py [-h] -e ENDPOINT -m {get,put,post,delete,patch,head}
                      [-i INPUTFILE] [-a ACCEPTTYPE] [-c CONTENTTYPE]
                      [-o {csv,json,simple,simplejson}] [-t] [-hf HEADERFILE]

Call the Viya REST API

optional arguments:
  -h, --help            show this help message and exit
  -e ENDPOINT, --endpoint ENDPOINT
                        Enter the REST endpoint e.g. /folders/folders
  -m {get,put,post,delete,patch,head}, --method {get,put,post,delete,patch,head}
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

For the current tool list and descriptions, see the [tool inventory](INVENTORY.md). Run any tool with `-h` for its current options.

**Examples**

Many of the tools have examples of usage documented in  [EXAMPLES.md](EXAMPLES.md)

## Troubleshooting

The most common problem is an expired access token. You may see a message like:

    {"errorCode":0,"message":"Cannot convert access token to JSON","details":["traceId: 6bca23b2b3a2cfda","path: /folders/folders"],"remediation":null,"links":[ ],"version":2,"httpStatusCode":401}

To fix the problem generate a new access token: `/opt/sas/viya/home/bin/sas-admin auth login`

To see the current setup, including python and package versions, environment variable settings, profile information and current user. Run

`python3 showsetup.py`

If you get this error : Login failed. Error with security certificate.

Set the environment variable for the SSL certificate file. For example:

`export SSL_CERT_FILE=/opt/sas/viya/config/etc/SASSecurityCertificateFramework/cacerts/trustedcerts.pem`


If you get this error:

```log
Raise SSLError(e, request=request)
requests.exceptions.SSLError: HTTPSConnectionPool(host='intviya01.gelcorp.com', port=443): Max retries exceeded with url: / (Caused by SSLError(SSLError(1, u'[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:579)'),))
```

Set the environment variable for the SSL certificate file. For example:

`export REQUESTS_CA_BUNDLE=/opt/sas/viya/config/etc/SASSecurityCertificateFramework/cacerts/trustedcerts.pem`

## Developing with the existing functions

The file sharedfunctions.py contains a set of generic functions that make it easy to build additional tools.

*callrestapi* is the main function, called by many other programs and by the callrestapi program to make the REST calls. It accepts as parameters:

* reqval: the request value which is the rest endpoint for the request
* reqtype: the type of REST request: `get`, `put`, `post`, `delete`, `patch`, or `head`
* acceptType: optional Accept content type
* contentType: optional content type content header
* data: optionally a python dictionary created from the json for the rest request
* params: optional dictionary of query parameters to pass to the rest request
* stoponerror: whether the function will stop all further processing if an error occurs (default 0 to not stop)

We suggest you use [listcaslibs_example.py](listcaslibs_example.py) as a simple example to copy from if you wish to develop your own python scripts, and are new to Python or some of the concepts we have used. If one of the other existing tools is similar to what you want, of course you could use that as the basis for a new tool too.

## Contributing

We welcome your contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to submit contributions to this project.

### Generating tool reference documentation

Use [scripts/generate_tool_docs.py](scripts/generate_tool_docs.py) to generate
the Markdown reference at [docs/TOOLS.md](docs/TOOLS.md):

```sh
python3 scripts/generate_tool_docs.py
```

The Markdown file is intended to be committed with documentation changes.
Regenerate it after changing a tool's arguments, then review and commit the
result with the source change.

To also build an optional HTML version, install the documentation-only
dependencies and use `--html`:

```sh
python3 -m pip install -r requirements-docs.txt
python3 scripts/generate_tool_docs.py --html
```

Open `docs/tools/html/index.html` to view the HTML output. Generated HTML files
under `docs/tools/` are ignored by Git; the tools' runtime dependencies are
unchanged.

Exclude particular tools by listing their exact filenames:

```sh
python3 scripts/generate_tool_docs.py \
  --exclude call_rest_api.py listcaslibs_example.py \
  --exclude setup.py
```

Use `--source-dir PATH` to scan another directory (not recursively),
`--markdown-file PATH` to change the Markdown destination, and `--output-dir PATH`
to change the optional HTML destination. Exclusion names must exist in the
source directory; files without argparse parsers are reported and skipped.

The generator reads Python syntax without importing tools, parsing their command
lines, loading credentials, or making Viya calls. It supports the repository's
literal argparse definitions, parent parsers, subcommands, argument groups, and
Python-version-specific encoding options. Current-directory defaults reflect the
directory where documentation is built; the command-line branch of
`changeimportloc.py` is documented rather than its SAS Studio integration.
Unsupported dynamic argument values and conditional declarations fail explicitly
instead of executing code. This is a static extractor for the patterns above,
not a general-purpose Python interpreter; new parser-building patterns may need
extractor support. Existing tools are not modified.

## License

This project is licensed under the [Apache 2.0 License](LICENSE).
