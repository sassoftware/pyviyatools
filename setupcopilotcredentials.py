 #!/usr/bin/python
#
# setupcopilotcredentials.py
#
# Create or update the OrdersAPIAuth credential required
# for setup of SAS Viya Copilot. 

# Prior to running, generate required key and secret at 
# https://developer.sas.com/rest-apis/mysas/applications.
# Optionally specify these in an input file with the format:
# ```
# SAS_ORDERS_API_CLIENT_ID=xxxxxxxxxxxx
# SAS_ORDERS_API_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxx # base64 (no special characters)
# ````

#
# More information: https://go.documentation.sas.com/doc/en/sasadmincdc/default/callicense/p1ii465hpdnkoan1fx3ybdin9q5s.htm

import argparse, sys
import sharedfunctions

debug = False

DOMAIN_ID = "OrdersAPIAuth"
IDENTITY_TYPE = "client"
CLIENT = "sas.genAiGateway"

CLIENT_ID_KEY = "SAS_ORDERS_API_CLIENT_ID"
CLIENT_SECRET_KEY = "SAS_ORDERS_API_CLIENT_SECRET"

# Define exception handler so that we only output trace info from errors when in debug mode
def exception_handler(exception_type, exception, traceback,
                      debug_hook=sys.excepthook):
    if debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print(f"{exception_type.__name__}: {exception}")

sys.excepthook = exception_handler



# Read input file (KEY=VALUE)
def read_values_from_file(path):
    values = {}

    try:
        with open(path) as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue

                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()

    except Exception as e:
        raise Exception(f"Unable to read input file '{path}': {e}")

    for k in (CLIENT_ID_KEY, CLIENT_SECRET_KEY):
        if k not in values or not values[k]:
            raise Exception(f"Missing required value '{k}' in input file")

    return values


# get input parameters
parser = argparse.ArgumentParser(
    description="Set up SAS Viya Copilot Orders API credentials"
)

parser.add_argument("--client-id", help="Orders API Client ID")
parser.add_argument("--client-secret", help="Orders API Client Secret")
parser.add_argument(
    "--input-file",
    help="KEY=VALUE file containing Orders API credentials"
)
parser.add_argument(
    "--force",
    action="store_true",
    help="Attempt to overwrite existing credential if it exists"
)

args = parser.parse_args()


# Input resolution
if args.input_file:
    values = read_values_from_file(args.input_file)
else:
    if not args.client_id or not args.client_secret:
        raise Exception(
            "You must supply --client-id and --client-secret, "
            "or use --input-file"
        )

    values = {
        CLIENT_ID_KEY: args.client_id,
        CLIENT_SECRET_KEY: args.client_secret
    }


# Check for existing client credentials
list_endpoint = f"/credentials/domains/{DOMAIN_ID}/credentials"

result = sharedfunctions.callrestapi(list_endpoint, "get")

credential_exists = False

for item in result.get("items", []):
    if item.get("identityType") == "client":
        credential_exists = True
        break


if credential_exists and not args.force:
    print(
        f"Credential '{CLIENT}' already exists in domain '{DOMAIN_ID}'.\n"
        "No changes made. Use --force to attempt overwrite."
    )
    sys.exit(0)


# Create required client credential
endpoint = f"/credentials/domains/{DOMAIN_ID}/clients/{CLIENT}"

payload = {
    "domainId": DOMAIN_ID,
    "identityType": IDENTITY_TYPE,
    "identityId": CLIENT,
    "domainType": "token",
    "properties": {
        CLIENT_ID_KEY: values[CLIENT_ID_KEY]
    },
    "secrets": {
        CLIENT_SECRET_KEY: values[CLIENT_SECRET_KEY]
    }
}

if debug:
    print("DEBUG: PUT", endpoint)
    print("DEBUG: payload =", payload)

sharedfunctions.callrestapi(
    endpoint,
    "put",
    data=payload
)

print(
    f"SAS Viya Copilot Orders API credential '{CLIENT}' configured in domain '{DOMAIN_ID}'."
)

sys.exit()
