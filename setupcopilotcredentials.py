#!/usr/bin/env python3

#
# setupcopilotcredentials.py
#
# Create or update the OrdersAPIAuth credential required
# for SAS Viya Copilot.
#
# This automates the following manual steps:
#   SAS Environment Manager
#     -> Domains
#     -> OrdersAPIAuth
#     -> New Credential
#

import argparse
import sharedfunctions
import callrestapi


DOMAIN_ID = "OrdersAPIAuth"
IDENTITY_TYPE = "application"
IDENTITY = "sas.genAiGateway"

CLIENT_ID_KEY = "SAS_ORDERS_API_CLIENT_ID"
CLIENT_SECRET_KEY = "SAS_ORDERS_API_CLIENT_SECRET"


def read_values_from_file(path):
    """
    Read key=value pairs from a text file.
    Expected keys:
      - SAS_ORDERS_API_CLIENT_ID
      - SAS_ORDERS_API_CLIENT_SECRET
    """
    values = {}

    try:
        with open(path) as f:
            for line in f:
                line = line.strip()

                # Skip blanks and comments
                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    continue

                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()

    except Exception as e:
        sharedfunctions.fail(
            f"Unable to read input file '{path}': {e}"
        )

    for required_key in (CLIENT_ID_KEY, CLIENT_SECRET_KEY):
        if required_key not in values or not values[required_key]:
            sharedfunctions.fail(
                f"Missing required value '{required_key}' in input file"
            )

    return values


def main():
    parser = argparse.ArgumentParser(
        description="Set up SAS Viya Copilot Orders API credentials"
    )

    parser.add_argument(
        "--client-id",
        help="Orders API Client ID"
    )
    parser.add_argument(
        "--client-secret",
        help="Orders API Client Secret"
    )
    parser.add_argument(
        "--input-file",
        help="Input file containing SAS_ORDERS_API_CLIENT_ID and "
             "SAS_ORDERS_API_CLIENT_SECRET (KEY=VALUE format)"
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace existing credential for sas.genAiGateway"
    )

    args = parser.parse_args()

    # Validate input method
    if args.input_file:
        values = read_values_from_file(args.input_file)
    else:
        if not args.client_id or not args.client_secret:
            sharedfunctions.fail(
                "You must supply --client-id and --client-secret, "
                "or use --input-file"
            )

        values = {
            CLIENT_ID_KEY: args.client_id,
            CLIENT_SECRET_KEY: args.client_secret
        }

    # Authenticate using standard pyviyatools mechanism
    baseurl, headers, _ = sharedfunctions.setupSession()

    credentials_endpoint = (
        f"/credentials/domains/{DOMAIN_ID}/credentials"
    )

    # Optionally delete existing credential for this identity
    if args.replace:
        rc, existing = callrestapi.callRestApi(
            "GET",
            baseurl + credentials_endpoint,
            headers=headers
        )

        if rc != 0:
            sharedfunctions.fail(
                "Failed to query existing credentials"
            )

        for item in existing.get("items", []):
            if (
                item.get("identityType") == IDENTITY_TYPE and
                item.get("identity") == IDENTITY
            ):
                delete_endpoint = (
                    f"{credentials_endpoint}/{item['id']}"
                )

                callrestapi.callRestApi(
                    "DELETE",
                    baseurl + delete_endpoint,
                    headers=headers
                )

    # Create the new credential
    payload = {
        "identityType": IDENTITY_TYPE,
        "identity": IDENTITY,
        "properties": {
            CLIENT_ID_KEY: values[CLIENT_ID_KEY]
        },
        "secrets": {
            CLIENT_SECRET_KEY: values[CLIENT_SECRET_KEY]
        }
    }

    rc, _ = callrestapi.callRestApi(
        "POST",
        baseurl + credentials_endpoint,
        headers=headers,
        payload=payload
    )

    if rc != 0:
        sharedfunctions.fail(
            "Failed to create Orders API credential"
        )

    print(
        "Copilot Orders API credential successfully configured "
        f"in domain '{DOMAIN_ID}'."
    )

