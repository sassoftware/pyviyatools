# pyviyatools Install Intructions

* [Install](#install)
  * [Viya 3.x](#viya-3x)
  * [Viya 4](#viya-4)
  * [Configure](#configure)
* [Authentication](#authentication)

The  pyviyatools are a set of command-line tools that call the SAS Viya REST API's from python. The tools can be used to make direct calls to any rest-endpoint (like a CURL command) or to build additional tools that make multiple rest calls to provide more complex functionality. A subset of the tools also call the SAS Administration CLI

## Install

The tools are a package of files and should be downloaded as such. The individual files are not useable without the package.

The tools should be installed on the same machine that hosts the Viya command-line interfaces(CLI). The following commands will install a copy of the tools in a sub-directory(pyviyatools) of the current directory.

### Viya 3.x

*git clone https://github.com/sassoftware/pyviyatools.git*

### Viya 4

*git clone https://github.com/sassoftware/pyviyatools.git*

cd $install-dir

./setup.py

### Configure

What does .setup.py do?

Viya 3.5 the SAS Administration cli executable is sas-admin and the Viya 4 cli is sas-viya.

The application.properties file contains the name and location of the SAS Administation cli.


The default application properties in the repository stores the values for Viya 3.x

* sascli.location=/opt/sas/viya/home/bin/
* sascli.executable=sas-admin

To configure the tools for Viya 4, or if you have your cli installed in a non-default location use ./setup.py. For example:

**./setup.py --clilocation /opt/bin --cliexecutable sas-viya**

If you pass no parameters the defaults for the function are the Viya 4 default values.

* sascli.location=/opt/sas/viya/home/bin/
* sascli.executable=sas-viya

## Authentication

The pyviya tools use the sas-admin auth CLI to authenticate to Viya. To use the tool you must create a profile and authenticate. This process is documented in the SAS Viya Administration guide here.

http://documentation.sas.com/?cdcId=calcdc&cdcVersion=3.3&docsetId=calcli&docsetTarget=n1e2dehluji7jon1gk69yggc6i28.htm&locale=en


If your environment is enabled for Transport Layer Security (TLS), you must set the SSL_CERT_FILE environment variable to the path location of the trustedcerts.pem file (if using the SAS default truststore)
or the path location of your site-signed certificate (if using an internal truststore).

In addition you may need to set REQUESTS_CA_BUNDLE to the certificate location so that the requests library can find the certificates.

The tool will automatically use the default profile.

1. To create a profile as a SAS Administrator logon to the machine that contains the Viya CLI's
2. Run */opt/sas/viya/home/bin/sas-admin profile init* and when prompter enter the base endpoint of your Viya server for example: http://myviyaserver.blah.com. You may enter your personal preference at the other prompts.
3. After you create the profile there are two options to authenticate
 * Run */opt/sas/viya/home/bin/sas-admin auth login* to authenticate to Viya enter the userid and password of the SAS Administrator when prompted.
 *  Create an .authinfo file in your home directory with your userid and password and use **loginviauthinfo.py** to authenticate with the credentials in the file (you can use different authinfo files with the -f option)

The CLI allows for multiple profiles. To use a profile other than the default profile, for example newprofile

1. Create a named profile *sas-admin --profile newprofile profile init*
2. Logon with the named profile *sas-admin --profile newprofile auth login*
3. Set the SAS_CLI_PROFILE environment variable to the name of the profile
* LINUX: *export SAS_CLI_PROFILE=newprofile*
* WINDOWS: *set SAS_CLI_PROFILE=newprofile*

4. To revert to using the default variable reset the environment variable

* LINUX: *unset SAS_CLI_PROFILE*
* WINDOWS: *set SAS_CLI_PROFILE=*

The tools are self-documenting, for help on any tool call the tool passing -h or --help.


**TEST**

1. Execute a test call. Change directory to your install directory and run:

    *callrestapi.py -e /folders/folders -m get*

The call should return the JSON for the folders in the viya deployment. Be patient it might take a few seconds the first time.

2. To see the current setup, including python and package versions, environment variable settings, profile information and current user. Run

    *showsetup.py*
