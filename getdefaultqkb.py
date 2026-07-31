# !/usr/bin/python
# -*- coding: utf-8 -*-
#
# getdefaultqkb.py
# February 2026
#
# Get current default QKB settings as defined in Environment Manager.  
# Optional choose which engine to return (CAS or compute) defaults to both
#
# Change History
#
# 02FEB2026 Initial version
# 30JUL2026 Code review

# Import Python modules
from __future__ import print_function
import argparse
import pprint
import sys
pp = pprint.PrettyPrinter(indent=4)

from sharedfunctions import printresult, getconfigurationproperty

# Get current state for cas or compute depending on value in --engine
def parse_cas_qkb(contents):
    """
    Parse the CAS QKB settings from the sas.cas.instance.config contents.

    Expects:
        cas.DQLOCALE="ENUSA" --LOCALE
        cas.DQSETUPLOC="QKB CI 33" --QKB NAME
    """
    locale = None
    qkb = None

    if not contents:
        return {"locale": locale, "qkb": qkb}

    for line in contents.splitlines():

        # Parse DQLOCALE: anything inside double quotes
        if "cas.DQLOCALE" in line:
            first = line.find('"')
            last = line.rfind('"')
            if first != -1 and last != -1 and last > first:
                locale = line[first + 1:last]
        
         # Parse DQSETUPLOC: anything inside double quotes
        if "cas.DQSETUPLOC" in line:
            first = line.find('"')
            last = line.rfind('"')
            if first != -1 and last != -1 and last > first:
                qkb = line[first + 1:last]

    return {"locale": locale, "qkb": qkb}


def parse_compute_qkb(contents):
    """
    Parse the Compute QKB settings from the sas.compute.server contents.

    Expects:
        -DQLOCALE (ENUSA) --LOCALE
        -DQSETUPLOC 'QKB CI 33' --QKB NAME
    """
    locale = None
    qkb = None

    if not contents:
        return {"locale": locale, "qkb": qkb}

    for line in contents.splitlines():
        line = line.strip()

        # Parse DQLOCALE: anything inside parentheses
        if "-DQLOCALE" in line:
            first = line.find("(")
            last = line.rfind(")")
            if first != -1 and last != -1 and last > first:
                locale = line[first + 1:last]
        
         # Parse DQSETUPLOC: anything inside single quotes
        if "-DQSETUPLOC" in line:
            first = line.find("'")
            last = line.rfind("'")
            if first != -1 and last != -1 and last > first:
                qkb = line[first + 1:last]

    return {"locale": locale, "qkb": qkb}


def get_cas_qkb():
    """Get CAS QKB info."""
    configurationdef_cas = "sas.cas.instance.config"
    cas_info = {"locale": None, "qkb": None}

    configurationproperty_cas = getconfigurationproperty(configurationdef_cas)
    if not configurationproperty_cas or "items" not in configurationproperty_cas:
            return cas_info
    
    # Find item where config name == "config"
    cas_contents = ""
    for item in configurationproperty_cas["items"]:
        config_name = item.get("name", "")
        if config_name == "config":
            cas_contents = item.get("contents", "")
            break    

    parsed = parse_cas_qkb(cas_contents)
    cas_info.update(parsed)

    if cas_info["locale"] is None and cas_info["qkb"] is None:
        print("\n❌ No CAS QKB information found in configuration contents",file=sys.stderr)
        return cas_info
    
    return cas_info


def get_compute_qkb():
    """Get Compute QKB info."""
    configurationdef_compute = "sas.compute.server"
    compute_info = {"locale": None, "qkb": None}

    configurationproperty_compute = getconfigurationproperty(configurationdef_compute)
    if not configurationproperty_compute or "items" not in configurationproperty_compute:
        return compute_info

    # Find item where config name == "configuration_options"
    compute_contents = ""
    for item in configurationproperty_compute["items"]:
        config_name = item.get("name", "")
        if config_name == "configuration_options":
            compute_contents = item.get("contents", "")
            break

    parsed = parse_compute_qkb(compute_contents)
    compute_info.update(parsed)

    if compute_info["locale"] is None and compute_info["qkb"] is None:
        print("\n❌ No Compute QKB information found in configuration contents", file=sys.stderr)
        return compute_info
    
    return compute_info


def main():
    # Set input parameters
    parser = argparse.ArgumentParser(
        description="Get default QKB setting for SAS CAS and Compute engines"
    )
    parser.add_argument(
        "--engine",
        nargs="*",
        choices=["cas", "compute"],
        help=(
            "Engine(s) to query: cas, compute. "
            "If omitted, both are returned."
        ),
    )

    parser.add_argument(
        "-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'],default='json'
    )

    args = parser.parse_args()
    output_style=args.output

    # If no engine specified, default to both
    engines = args.engine if args.engine else ["cas", "compute"]

    results = {}

    if "cas" in engines:
        results["cas"] = get_cas_qkb()

    if "compute" in engines:
        results["compute"] = get_compute_qkb()

    printresult(results, output_style)

if __name__ == "__main__":
    main()