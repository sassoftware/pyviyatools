#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# listrules.py
# May 2026
#
# Change History
# May 2026 - Initial release
#
# Copyright © 2026, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License);
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# Assisted-by: Microsoft Copilot

import argparse
import datetime
import json
import sys
from typing import List, Optional
from argparse import RawDescriptionHelpFormatter

from sharedfunctions import callrestapi, printresult, getbaseurl


# --- Configuration ---
DESIRED_OUTPUT_COLUMNS = ['objectUri','containerUri','principalType','principal','setting','permissions','description','reason','createdBy','creationTimeStamp','modifiedBy','modifiedTimeStamp','condition','matchParams','mediaType','enabled','version','id']
VALID_PERMISSIONS = ['read','update','delete','secure','add','remove','create']
PRINCIPAL_TYPES = {'guest','everyone','authenticatedUsers'}

# --- Helpers ---
# set results return limit
def set_limit(args, default: int = 10000) -> int:
    val = getattr(args, "limit", None)
    if val is None:
        return default
    try:
        return int(val)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid limit value: {val!r}; must be an integer")


def parse_bool(val: str) -> Optional[bool]:
    if val is None or val.lower() in ('none',''):
        return None
    v = val.lower()
    if v in ('true','t','1','yes','y','enabled'):
        return True
    if v in ('false','f','0','no','n','disabled'):
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {val}")

def parse_date(val: str) -> str:
    # Accept ISO 8601 date or datetime; raise on invalid
    try:
        # allow date-only or datetime
        if 'T' in val:
            datetime.datetime.fromisoformat(val.replace('Z','+00:00'))
        else:
            datetime.date.fromisoformat(val)
        return val
    except Exception:
        raise argparse.ArgumentTypeError(f"Invalid date/datetime: {val}. Use ISO 8601 format.")

def join_or(expressions: List[str]) -> str:
    expressions = [e for e in expressions if e]
    if not expressions:
        return ''
    if len(expressions) == 1:
        return expressions[0]
    return 'or(' + ','.join(expressions) + ')'

def join_and(expressions: List[str]) -> str:
    expressions = [e for e in expressions if e]
    if not expressions:
        return ''
    if len(expressions) == 1:
        return expressions[0]
    return 'and(' + ','.join(expressions) + ')'

def contains(field: str, value: str) -> str:
    return f"contains({field},'{value}')"

def cmp(field: str, value: str, operator: str = 'eq') -> str:
    op = operator.lower()
    if op not in ('eq','ne','contains'):
        raise ValueError("Unsupported operator: must be 'eq', 'ne' or 'contains")
    return f"{op}({field},'{value}')"

def cmpdefault(field: str, value: str, operator: str = 'eq') -> str:
    op = 'eq'
    return f"{op}({field},'{value}')"

def in_list(field: str, values: List[str], operator: str = 'eq') -> str:
    # build or(eq(field,val1),eq(field,val2),...) or or(ne(...))
    return join_or([cmp(field, v, operator) for v in values])

def get_rules_count(rules_result_json):
    """
    Return an integer count from the JSON. Falls back to len(items) if count missing or invalid.
    """
    try:
        count = rules_result_json.get("count", None)
        if count is None:
            return int(len(rules_result_json.get("items", [])))
        return int(count)
    except (TypeError, ValueError):
        return int(len(rules_result_json.get("items", [])))


# --- Build filter expression ---
def build_filter(args) -> str:
    clauses = []
    operator = args.operator.lower() if args.operator else 'eq'

    # objectUri (use cmp)
    if args.uri and args.uri.lower() != 'none':
        clauses.append(cmp('objectUri', args.uri, operator))

    # containerUri (use cmp)
    if args.container and args.container.lower() != 'none':
        clauses.append(cmp('containerUri', args.container, operator))

    # description contains (CASE SENSITIVE as original)
    if args.description and args.description != 'none':
        clauses.append(contains('description', args.description))

    # principal or principalType (use cmp for eq/ne)
    if args.principal and args.principal.lower() != 'none':
        p = args.principal
        if p.lower() == 'authenticatedusers':
            p = 'authenticatedUsers'
        if p in PRINCIPAL_TYPES:
            if operator in ['eq','ne']:
                clauses.append(cmp('principalType', p, operator))
            else:       
                clauses.append(cmpdefault('principalType', p, operator))
        else:
            clauses.append(cmp('principal', p, operator))

    # enabled boolean (use cmp if operator is 'eq' or 'ne')
    if args.enabled and args.enabled.lower() != 'none':
        b = parse_bool(args.enabled)
        if b is not None and operator in ['eq','ne']:
            clauses.append(cmp('enabled', 'true' if b else 'false', operator))
        else:
            clauses.append(cmpdefault('enabled', 'true' if b else 'false', operator))

    ''' YET TO BE DEVELOPED
    # permissions: ensure valid and build contains/any logic
    if args.permission:
        invalid = [p for p in args.permission if p not in VALID_PERMISSIONS]
        if invalid:
            raise SystemExit(f"Invalid permission(s): {invalid}. Valid: {sorted(VALID_PERMISSIONS)}")
        # permissions are matched with contains; operator doesn't apply to contains
        perm_clauses = [contains('permissions', p) for p in args.permission]
        clauses.append(join_or(perm_clauses))
    '''

    # created/modified ranges (these are range ops and unaffected by eq/ne)
    if args.created_after:
        clauses.append(f"gt(creationTimeStamp,'{args.created_after}')")
    if args.created_before:
        clauses.append(f"lt(creationTimeStamp,'{args.created_before}')")
    if args.modified_after:
        clauses.append(f"gt(modifiedTimeStamp,'{args.modified_after}')")
    if args.modified_before:
        clauses.append(f"lt(modifiedTimeStamp,'{args.modified_before}')")

    # created/modified by (use cmpdefault)
    if args.created_by and args.created_by.lower() != 'none':
        clauses.append(cmpdefault('createdBy', args.created_by, operator))
    if args.modified_by and args.modified_by.lower() != 'none':
        clauses.append(cmpdefault('modifiedBy', args.modified_by, operator))

    # mediaType exact match (use cmp)
    if args.media_type and args.media_type.lower() != 'none':
        clauses.append(cmp('mediaType', args.media_type, operator))

    # condition free text (use contains)
    if args.condition:
        clauses.append(contains('condition', args.condition))
#        print(clauses) 

    ''' YET TO BE DEVELOPED
    if args.match_params:
        clauses.append(contains('matchParams', args.match_params))
    '''
    
    # custom raw filter (allow advanced users to pass a full filter expression)
    if args.raw_filter:
        clauses.append(args.raw_filter)

    # combine all clauses with and
    return join_and(clauses)


# --- Argument parsing ---
parser = argparse.ArgumentParser(
    description='''
listrules.py\n
\033[4;34m\033[1mUSAGE NOTE\033[0m
All search filters use the \033[1;33m"eq"\033[0m filter unless otherwise stated.
When using the date/time based filters the format can be either:
\033[1;33m2026-01-01\033[0m
or
\033[1;33m2026-01-01T00:00:00Z\033[0m''',
    formatter_class=RawDescriptionHelpFormatter)

parser.add_argument("-u","--uri", help="objectUri search, can be used with operator", default="none")
parser.add_argument("-c","--container", help="containerUri search, can be used with operator", default="none")
parser.add_argument("-p","--principal", help="Principal/Group ID (CASE SENSITIVE), or 'authenticatedUsers', 'everyone' or 'guest'", default='none')
parser.add_argument("-d","--description", help="description search ('contains' only and CASE SENSITIVE)", default='none')
parser.add_argument("--condition", help="condition search ('contains' only and CASE SENSITIVE)")
parser.add_argument("--media-type", dest='media_type', help="mediaType search, can be used with operator")
parser.add_argument("-e","--enabled", help="Show rules enabled/true or disabled/false", default='none')
parser.add_argument("--operator", help="Filter operator", choices=['eq','ne','contains'], default='eq')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson'], default='json')
parser.add_argument("--header-off", dest='headeroff', action='store_true', help="(Optional) Disables header when Output Style is csv")
parser.add_argument("--print-filter", dest='printfilter', action='store_true', help="Returns the filter string without executing it")
#parser.add_argument("--perms", help="Sting of permissions to search for in the rules", default="none")
#parser.add_argument("--permission", action='append', help="Filter by permission. Can be repeated", metavar='PERM')
parser.add_argument("--created-after", dest='created_after', type=parse_date, help="Created after datetime (see usage note above)")
parser.add_argument("--created-before", dest='created_before', type=parse_date, help="Created before datetime (see usage note above)")
parser.add_argument("--modified-after", dest='modified_after', type=parse_date, help="Modified after datetime (see usage note above)")
parser.add_argument("--modified-before", dest='modified_before', type=parse_date, help="Modified before datetime (see usage note above)")
parser.add_argument("--created-by", dest="created_by", help="createdBy search (exact match only)")
parser.add_argument("--modified-by", dest="modified_by", help="modifiedBy search (exact match only)")
#parser.add_argument("--match-params", dest='match_params', help="Filter by matchParams contains text")
parser.add_argument("--count-only", dest='countonly', action='store_true', help="Displays the number of rules found only")
parser.add_argument("--limit", type=int, help="(Optional) Overrides the default 10000 return limit with a custom value")
parser.add_argument("--sort-by", help="(Optional) Sorts results (single sortBy item ONLY)")
parser.add_argument("--sort-order", help="(Optional) Order of sorted results", choices=['ascending','descending'], default='ascending')
parser.add_argument("--raw-filter", help="Raw filter expression to append (advanced users)")

args = parser.parse_args()

# --- Build request path ---
try:
    filter_expr = build_filter(args)
except SystemExit as e:
    print(str(e), file=sys.stderr)
    sys.exit(2)
except ValueError as e:
    print(str(e), file=sys.stderr)
    sys.exit(2)


LIMITVAL = set_limit(args)
base = "/authorization/rules"
if filter_expr:
    reqval = f"{base}?filter={filter_expr}&limit={LIMITVAL}"
else:
    reqval = f"{base}?limit={LIMITVAL}"

if args.sort_by == None:
    pass
elif args.sort_by != None and args.sort_by in DESIRED_OUTPUT_COLUMNS:
    reqval = reqval + f"&sortBy=" + args.sort_by + ":" + args.sort_order
else:
    print('\n\033[1;31mINVALID SORT OPTION\n\n'+
          '\033[1;33mUpdate your sort to use one of the following options and try again.\033[0m\n\n'+
           str(DESIRED_OUTPUT_COLUMNS) +'\n')
    sys.exit(0)


reqtype = 'get'

# prints the filter and REST call without executing, then exists
if args.printfilter:
    print('\nFull filter:\n\033[1;32m'+reqval+'\033[0m\n')
    print('Full call:\n\033[1;32m'+getbaseurl()+reqval+'\033[0m\n')
    sys.exit(0)

# make the rest call
rules_result_json = callrestapi(reqval, reqtype)
rulesfound = get_rules_count(rules_result_json)
#print(rulesfound)

if rulesfound == 0:
  print('\n\033[1;31mNO RULES FOUND. Check your filter and try again.\n\n\033[1;33m'+reqval+'\033[0m\n')
  sys.exit(0)
elif args.countonly:
  print('\n\033[1;32m'+str(rulesfound)+' RULES FOUND\033[0m\n')
  sys.exit(0)
else:
  pass

# print the result if output style is json or simple
if args.output in ['json','simple']:
  printresult(rules_result_json,args.output)
elif args.output=='csv':

  # option to disable header row
  if args.headeroff:
      pass
  else:
      print(','.join(map(str,DESIRED_OUTPUT_COLUMNS)))
      
  if 'items' in rules_result_json:
    for item in rules_result_json['items']:
      outstr=''
      for column in DESIRED_OUTPUT_COLUMNS:
        # Add a comma to the output string, even if we will not output anything else, unless this is the very first desired output column
        if column is not DESIRED_OUTPUT_COLUMNS[0]: outstr=outstr+','
        if column=='setting':
          # The setting value is derived from two columns: type and condition.
          if 'condition' in item:
            #print("Condition found")
            outstr=outstr+'conditional '+item['type']
          else:
            outstr=outstr+item['type']
        elif column in item:
          # This column is in the results item for this rule
          # Most columns are straight strings, but a few need special handling
          if column in ['condition','description','reason']:
            # The these strings can have values whcih contain commas, need we to quote them to avoid the commas being interpreted as column separators in the CSV
            outstr=outstr+'"'+item[column]+'"'
          elif column=='permissions':
            # Construct a string listing each permission in the correct order, separated by spaces and surrounded by square brackets
            outstr=outstr+'['
            permstr=''
            # Output permissions in the order we choose, not the order they appear in the result item
            for permission in VALID_PERMISSIONS:
              for result_permission in item['permissions']:
                if permission == result_permission:
                  # Add a space to separate permissions if this isn't the first permission
                  if not permstr=='': permstr=permstr+' '
                  permstr=permstr+result_permission
            outstr=outstr+permstr+']'
          else:
            # Normal column
            # Some columns contain non-string values: matchParams and enabled are boolean, version is integer. Convert everything to a string.
            outstr=outstr+str(item[column])
      print(outstr)
else:
  print ("output_style can be json, simple or csv. You specified " + args.output + " which is invalid.")
