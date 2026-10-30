# Installing pyviyatools

- [Installing pyviyatools](#installing-pyviyatools)
- [Install](#install)
  - [Download and install](#download-and-install)
  - [Configure](#configure)
  - [Test](#test)

pyviyatools is a collection of command-line tools that call the SAS Viya REST APIs. The tools can make direct calls to REST endpoints or combine multiple calls to provide more complex functionality. Some tools also call the SAS Administration CLI.

## Install

Download the repository as a whole; individual tools depend on shared files in the repository.

The tools need access to a configured SAS Viya CLI profile and authentication token. For Viya 4, use the `sas-viya` CLI. If you are using Viya 3, use the `sas-admin` CLI instead. Install the repository on a machine that has access to the CLI, or configure the CLI profile and token for the account running the tools.

### Download and install

Clone the repository and install its Python dependencies:

```sh
git clone https://github.com/sassoftware/pyviyatools.git
cd pyviyatools
python3 -m pip install -r requirements.txt
```

Use Python 3 to run the tools. The repository does not currently declare a formal range of supported Python versions.

### Configure

Use the `sas-viya` CLI for Viya 4. If you are using Viya 3, use `sas-admin`.

The repository's `application.properties` file stores the CLI location and executable name. To configure the standard Viya 4 CLI, run `setup.py` with no arguments:

```sh
python3 setup.py
```

For Viya 3, configure the tools to use `sas-admin`:

```sh
python3 setup.py --clilocation /opt/sas/viya/home/bin/ --cliexecutable sas-admin
```

If the CLI is installed in a non-default location, pass its location and executable name. For example, for Viya 4:

```sh
python3 setup.py --clilocation /opt/bin --cliexecutable sas-viya
```

Create and authenticate a profile with the matching CLI (`sas-viya` for Viya 4 or `sas-admin` for Viya 3) before running the tools. See the [README profile instructions](README.md#creating-a-profile-and-logging-on).

### Test

1. Configure and authenticate the appropriate CLI profile: use `sas-viya` for Viya 4, or `sas-admin` for Viya 3. See the [README profile instructions](README.md#creating-a-profile-and-logging-on).

2. From the repository directory, make a test request. It should return JSON for folders in the Viya deployment:

```sh
python3 callrestapi.py -e /folders/folders -m get
```

3. To display the current setup and environment details, run:

```sh
python3 showsetup.py
```
