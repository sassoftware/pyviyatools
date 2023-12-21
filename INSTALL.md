# pyviyatools Install Intructions

- [pyviyatools Install Intructions](#pyviyatools-install-intructions)
- [Install](#install)
  - [Viya 3.x](#viya-3x)
  - [Viya 4](#viya-4)
  - [Configure](#configure)
  - [Install Required Python Packages](#install-required-python-packages)
  - [Test](#test)

The  pyviyatools are a set of command-line tools that call the SAS Viya REST API's from python. The tools can be used to make direct calls to any rest-endpoint (like a CURL command) or to build additional tools that make multiple rest calls to provide more complex functionality. A subset of the tools also call the SAS Administration CLI

# Install

The tools are a package of files and should be downloaded as such. The individual files are not useable without the package.

The tools should be installed on the same machine that hosts the Viya command-line interfaces(CLI). The following commands will install a copy of the tools in a sub-directory (pyviyatools) of the current directory.

## Viya 3.x

For Viya 3.x follow these steps.

```sh
cd $install-dir
*git clone https://github.com/sassoftware/pyviyatools.git*
```

## Viya 4

For Viya 4 follow these steps.

```sh
cd $install-dir
*git clone https://github.com/sassoftware/pyviyatools.git*
cd pyviyatools
./setup.py
```

## Configure

What does .setup.py do?

**NOTE. You do not need to run setup.py if you are using Viya 3.x and the tools are installed in the default location.**

Viya 3.5 the SAS Administration cli executable is `sas-admin` and the Viya 4 cli is `sas-viya`.

The project contains an application.properties file that documents the name and location of the SAS Administation cli. The default application properties in the repository stores the values for Viya 3.x

```log
sascli.location=/opt/sas/viya/home/bin/
sascli.executable=sas-admin
```

To configure the tools for Viya 4, or if you have your cli installed in a non-default location use ./setup.py. For example:

```sh
./setup.py --clilocation /opt/bin/mycli --cliexecutable sas-viya
```

If you pass no parameters the defaults for the function are the Viya 4 default values.

```log
sascli.location=/opt/sas/viya/home/bin/
sascli.executable=sas-viya
```

## Install Required Python Packages

The required python packages are listed in the `requirements.txt` file and may be installed using the following command.

```sh
pip install -r requirements.txt
```

## Test

1. Follow the steps to authenticate to Viya.

1. Execute a test call. Change directory to your install directory and run the command below. The call should return the JSON for the folders in the viya deployment. Be patient it might take a few seconds the first time.

```sh
./callrestapi.py -e /folders/folders -m get*
```

2. To see the current setup, including python and package versions, environment variable settings, profile information and current user. Run

```sh
./showsetup.py
```
```log
Python Version is: 2.7
Requests Version is: 2.6.0
SAS_CLI_PROFILE environment variable set to profile gelcorp
SSL_CERT_FILE environment variable set to profile /home/cloud-user/.certs/gelcorp_trustedcerts.pem
REQUESTS_CA_BUNDLE environment variable set to profile /home/cloud-user/.certs/gelcorp_trustedcerts.pem
Note your authentication token expires at: 2023-12-21T18:13:39Z
Endpoint is: https://gelcorp.pdcesx03191.race.sas.com
Logged on as id: geladm
Logged on as name: geladm
{u'sascli.location': u'/opt/sas/viya/home/bin/', u'sascli.executable': u'sas-viya'}
```
