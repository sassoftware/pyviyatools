# ValidateViya User Guide

ValidateViya is one of the many tools found in pyviyatools. ValidateViya runs a swath of tests on a Viya environment, validating that it is running as expected. ValidateViya is designed to be heavily modular, allowing for the creation of custom tests, the alteration of existing tests, and the removal of unneeded tests.

## Usage

ValidateViya is run in the command line like any other tool in pyviyatools:

```Bash
./validateViya.py
```

## Optional Arguments

| Argument              	| Description                             	|
|-----------------------	|-----------------------------------------	|
| -v/--verbose          	| Provides additional output              	|
| -s/--silent           	| Limits output to results only           	|
| -o/--output           	| Returns results in one of eight styles  	|
| -g/--generate-tests   	| Creates a custom tests file for editing 	|
| -c/--custom-tests     	| Uses a custom tests file for testing    	|
| -d/--output-directory 	| Selects the directory to output files   	|


## -v/--verbose

Provides additional output throughout the test processes, as well as formatted output for each output type.

## -s/--silent

Limits output to only test results, excluding any progess-related output, output formatting, etc.

## -o/--output

Provides different options for output, including:
- Json: raw json output for each test
- Simplejson: the json output type sans all of the "links" items
- Simple: a more readable format of simplejson
- Csv: csv output of test results, limiting columns to those specified with "cols" parameter
- Passfail: "PASS" if tests are passing, "FAIL" otherwise
- Passfail-full: Provides a json object specifying whether each test passed or failed
- Report: generates an HTML report containing all of the tests ran, their results, and the number of returned elements with the test
- Report-full: generates an HTML report containing everything in report output, as well as the individual items returned (for the list users test, it lists all of the users, etc.)

Test results are not labeled by default for all test types -> use --verbose to provide labels

The report and report-full output types both create an html file, which, by default, will be saved at the same directory as ValidateViya. Use --output-directory to specify a different output location if desired.

## -g/--generate-tests

Creates the default test suite as a JSON file, which can be edited. By default, the JSON is saved to the current directory as testPreferences.json, but the optional filename parameter can alter the name of the file and --output-directory can alter the output location.

## -c/--custom-tests

Loads in a custom test suite created off of the template provided with --generate-tests.

## -d/--output-directory

Selects the output directory for ValidateViya actions that save a file (--output report/report-full and --generate-tests). The directory must first exist before it is specified with --output-directory.

## Creating Custom Tests

Each test should contain the following fields:
- Id: a unique numerical id for the test -> these should appear in ascending order starting with 0
- Name: a unique test name
- Active: a boolean value determining whether or not to run the test
- Req: the API request used
  - This should be in the format of an array, as some tests require variables to be passed into the request. If the variable is X and the req array is ['a', 'b'], the request passed should then be aXb. Essentially, the request variables are slotted in between the indices of the req array.
- Cols: the columns to print from the request result for csv output
- Type: either data collection (uses REST GET) or Computation (running SAS code)

Tests that require a variable to be passed in its request must contain the following fields:
- reqVariable: the name of the variable used inside of the API request
- Servers/caslibs/etc: the reqVariable, different test-by-test
  - This should be in the format of a 2d array, allowing for different values (multiple servers) and multiple variables per request (caslibs lists ['server', 'caslib'] for each caslib)

The JSON also has a "count" parameter, which should be equal to the total number of tests (active and inactive)

## Custom Test Examples

1. Deactivating an existing test, meaning it will not run:

```JSON
{
  "count": 8,
  "tests": [
    {
      "name": "Logged in User",
      "req": [
        "/identities/users/@currentUser"
      ],
      "cols": [
        "name",
        "id"
      ],
      "active": "True",
      "type": "Data Collection",
      "id": "0"
    },
    {
      "name": "List Users",
      "req": [
        "/identities/users?limit=10000"
      ],
      "cols": [
        "name",
        "id"
      ],
      "active": "False",
      "type": "Data Collection",
      "id": "1"
    }
  ]
}
```

The "active" field for test 1 (List Users) has been set to false. When running this custom test plan, test 1 will not be run. _NOTE: Tests 2-7 are not shown_

2. Altering the cols values to change the variables of interest for CSV output:

```JSON
{
  "name": "List CAS Servers",
  "req": [
    "/casManagement/servers?limit=10000"
  ],
  "cols": [
    "version",
    "name",
    "host",
    "port",
    "description",
    "restProtocol"
  ],
  "active": "True",
  "type": "Data Collection",
  "id": "3"
},
```

The additional columns "restProtocol" and "version" were added to the test. When running this test with the output type of CSV, these new columns will be returned.

3. Adding additional reqVariable values:

```JSON
{
  "reqVariable": "caslibs",
  "name": "List CASLib Tables",
  "active": "True",
  "type": "Data Collection",
  "req": [
    "/casManagement/servers/",
    "/caslibs/",
    "/tables?limit=10000"
  ],
  "caslibs": [
    [
      "cas-shared-default",
      "systemData"
    ],
	[
	  "cas-shared-default",
	  "samples"
	]
  ],
  "id": "6",
  "cols": [
    "serverName",
    "caslibName",
    "name"
  ]
}
```

In this example, the reqVariable "caslibs" gained an additional value (['cas-shared-default', 'samples']). This value will be tested when running this custom test.

```JSON
{
  "reqVariable": "servers",
  "name": "List CAS Server Metrics",
  "active": "True",
  "type": "Data Collection",
  "req": [
    "/casManagement/servers/",
    "/metrics"
  ],
  "cols": [
    "serverName",
    "systemNodes",
    "systemCores",
    "cpuSystemTime",
    "memory"
  ],
  "id": "4",
  "servers": [
    [
      "cas-shared-default",
	  "cas-server-2"
    ]
  ]
}
```

In this example, the reqVariable "servers" was given an additional value "cas-server-2". This value will be tested when the tests are run.

4. Creating a custom test

```JSON
{
  "name": "List Reports",
  "req": [
    "/reports/reports"
  ],
  "cols": [
    "id",
    "name",
    "createdBy"
  ],
  "active": "True",
  "type": "Data Collection",
  "id": "8"
}
```

In this example, a custom data collection test was created without any reqVaraibles. This test contains each of the required parameters for a non-variable test.

```JSON
{
  "reqVariable": "CASservers",
  "name": "List CAS Server Sessions",
  "active": "True",
  "type": "Data Collection",
  "req": [
    "/casManagement/servers/",
    "/sessions"
  ],
  "cols": [
    "name",
    "state",
    "id",
    "owner",
  ],
  "id": "9",
  "CASservers": [
    [
      "cas-shared-default"
    ]
  ]
}
```

In this example, a custom test with a variable inside was created. Not how the value for reqVariable is set to the key for the array containing the variables (CASservers).