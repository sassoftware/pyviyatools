#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getloglevels.py June 2026
#
# Tool to check and set logging levels
#
#
# Change History
#
# 26JUN2026 Initial commit
#
#
# Copyright © 2026, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either 
#  express or implied. See the License for the specific language governing permissions and limitations under the License.
# 

# Import required packages

import os
import argparse 
from sharedfunctions import callrestapi
from collections import Counter
import subprocess
import json
import re
import xml.etree.ElementTree as ET

# Setup command-line arguements.

parser = argparse.ArgumentParser()
parser.add_argument("--notrace", help="Set any loggers set to trace down to debug.",action="store_true",default=False)
parser.add_argument("--nodebug", help="Set any loggers set to debug down to info.",action="store_true",default=False)

# Add option to make kubectl execution optional in case the user does not have kubectl installed or does not have access to the cluster
parser.add_argument("--kubectl", help="Enable checking for logging levels set in consul using kubectl exec.",action="store_true",default=False)

# Add option to supply a kubernetes namespace if the user has specified the kubectl option, default to "viya"
parser.add_argument("--namespace", help="The kubernetes namespace to use for kubectl commands, default is viya.",default="viya")

# Add option to supply a kubeconfig file for kubectl commands.
parser.add_argument("--kubeconfig", help="The kubeconfig file to use for kubectl commands, default is ~/.kube/config.")

# Add verbose option to include all loggers rather than just debug and tracegers
parser.add_argument("--verbose", help="Include all loggers in the output, not just those set to debug or trace.",action="store_true",default=False)

# Read arguments into variables.
args = parser.parse_args()
notrace=args.notrace
nodebug=args.nodebug
kubectl_enabled=args.kubectl
namespace=args.namespace
verbose=args.verbose

# If a kubeconfig file is specified, set the KUBECONFIG environment variable to that file so the kubectl command uses it.
if args.kubeconfig:
    os.environ['KUBECONFIG'] = args.kubeconfig

# If the environment variable REQUESTS_CA_BUNDLE is unset:
# If /opt/sas/viya/config/etc/SASSecurityCertificateFramework/cacerts/trustedcerts.pem file exists, use it, otherwise set it to /etc/ssl/certs/ca-certificates.crt
if 'REQUESTS_CA_BUNDLE' not in os.environ:
    if os.path.exists('/opt/sas/viya/config/etc/SASSecurityCertificateFramework/cacerts/trustedcerts.pem'):
        os.environ['REQUESTS_CA_BUNDLE'] = '/opt/sas/viya/config/etc/SASSecurityCertificateFramework/cacerts/trustedcerts.pem'
    else:
        os.environ['REQUESTS_CA_BUNDLE'] = '/etc/ssl/certs/ca-certificates.crt'

### Configuration Service -- logging.level definition configurations ###

# Query the current logging.level configurations from the configuration service.
# by default this API isn't paginated, so we should get all of the configurations in one call.
reqtype='get'
reqval = '/configuration/configurations?definitionName=logging.level'
print("Calling REST endpoint: ",reqval)
results = callrestapi(reqval,reqtype)

# Produce a report of the number of logging.level configurations, the levels they are set to, and details on any loggers set to debug or trace.
all_configs = results.get('items', [])
count_all = len(all_configs)
print("Found %s logging.level configurations in total." % count_all)

# Build a table organized by service.
services_table = {}

# For each configuration, get the logger name and level, and add it to the services table. 
# If the verbose option is not set, only include loggers set to debug or trace.
for item in all_configs:
    logger_name = item.get("name", "UNKNOWN")
    logger_level = item.get("level", "UNKNOWN")
    if not verbose and logger_level not in ["DEBUG", "TRACE"]:
        continue
    services = item['metadata'].get('services', [])
    for service in services:
        if service not in services_table:
            services_table[service] = []
        services_table[service].append((logger_name, logger_level))

# Print the services table, showing the service name, the number of loggers for that service, and the logger names and levels.
for service, loggers in services_table.items():
    print("Service: %s Count: %s" % (service, len(loggers)))
    for logger_name, logger_level in loggers:
        print("  Logger: %s, Level: %s" % (logger_name, logger_level))
level_counts_all = Counter(obj.get("level", "UNKNOWN") for obj in all_configs)

# Iterate through each level and print the number of configurations with that level
for level, count in level_counts_all.items():
    print("Found %s logging.level configurations with level %s." % (count, level))

# Only evaluate non-default configurations for notrace and nodebug options.
nonDefault_configs = [item for item in results.get('items', []) if not item.get('metadata', {}).get('isDefault', True)]

# Count the number of logging.level configurations
count = len(nonDefault_configs)
print("Checking %s non-default logging.level configurations for any set to debug or trace..." % count)

# Count the number of logging.level configurations by level
level_counts = Counter(obj.get("level", "UNKNOWN") for obj in nonDefault_configs)

# Iterate through each level and print the number of configurations with that level
for level, count in level_counts.items():
    print("Found %s logging.level configurations with level %s." % (count, level))

# If we found any debug or trace level loggers
    if level in ["DEBUG", "TRACE"]:
        for item in nonDefault_configs:
            if item.get("level") == level:
                # Output details on the logger configuration
                services = item['metadata'].get('services', [])
                created_by = item['metadata'].get('createdBy', "UNKNOWN")
                modified_by = item['metadata'].get('modifiedBy', "UNKNOWN")
                creationTimeStamp = item['metadata'].get('creationTimeStamp', "UNKNOWN")
                modifiedTimeStamp = item['metadata'].get('modifiedTimeStamp', "UNKNOWN")
                print("id: %s level: %s" % (item.get("id"), item.get("level")))
                print("logger: %s, services %s" % (item.get("name"), services))
                print("created by: %s on %s" % (created_by, creationTimeStamp))
                print("modified by: %s on %s " % (modified_by, modifiedTimeStamp))

                # If we've set the notrace or nodebug options, change the logging level as needed

                # For TRACE -- If notrace and nodebug are set, change the logging level to info.
                if item.get("level") == "TRACE" and notrace and nodebug:
                    print("Logging level is Trace and notrace and nodebug are set. Changing to INFO.")
                    item["level"] = "INFO"
                    reqval='/configuration/configurations/'+item.get("id")
                    reqtype='put'
                    results=callrestapi(reqval,reqtype,contentType='application/vnd.sas.configuration.config.logging.level+json;version=1',data=item)
                # For TRACE -- If just notrace is set, change the logging level to debug.
                elif item.get("level") == "TRACE" and notrace:
                    print("Logging level is Trace and notrace is set. Changing to DEBUG.")
                    item["level"] = "DEBUG"
                    reqval='/configuration/configurations/'+item.get("id")
                    reqtype='put'
                    results=callrestapi(reqval,reqtype,contentType='application/vnd.sas.configuration.config.logging.level+json;version=1',data=item)
                # For DEBUG -- If nodebug is set, change the logging level to info.
                elif item.get("level") == "DEBUG" and nodebug:
                    print("Logging level is Debug and nodebug is set. Changing to INFO.")
                    item["level"] = "INFO"
                    reqval='/configuration/configurations/'+item.get("id")
                    reqtype='put'
                    results=callrestapi(reqval,reqtype,contentType='application/vnd.sas.configuration.config.logging.level+json;version=1',data=item)

# Query the configuration service for the logconfig files and evaluate them for any loggers set to debug or trace. 
# The logconfig files are stored in the configuration service with a definitionName of the server (e.g. sas.compute.server) and a name of "logconfig" or "sessionlogconfig".

print("Checking logconfig files in configuration service for any loggers set to debug or trace...")

# Pull the configurations for each of the servers.
for server in ["sas.compute.server", "sas.cas.instance.config", "sas.batch.server", "sas.connect.spawner", "sas.connect.server"]:
    reqtype='get'
    reqval = f'/configuration/configurations?definitionName={server}'
    print("Calling REST endpoint: ",reqval)
    results = callrestapi(reqval,reqtype)

    # Check for a configuration with a name of "logconfig" or "sessionlogconfig" in those results.
    all_configs = [item for item in results.get('items', []) if item.get("name") in ["logconfig", "sessionlogconfig"]]

    # If we found any...
    for item in all_configs:
            
        # The content of the logconfig is in the "contents" field and is a string representation of the logconfig.xml file. 
        # We need to parse this XML to check for any loggers set to debug or trace.
        
        # The header of the XML file differs depending on the server, for example:

        # Compute Server: 
        # <?xml version='1.0' encoding='utf-8'?>
        # <log4sas:configuration xmlns:log4sas="http://www.sas.com/rnd/Log4SAS/">

        # CAS Server:
        # <?xml version="1.0" encoding="UTF-8"?>
        # <logging:configuration xmlns:logging="http://www.sas.com/xml/logging/1.0/">

        # As we might need to replace this XML content, preserve the original XML declaration if it exists, so we can put it back when we update the logconfig.

        # Extract the namespace from the XML declaration if it exists
        logconfig_xml = item.get("contents", "")
        root_tag = logconfig_xml.lstrip().split()[0] if logconfig_xml.lstrip() else ""
        namespace_match = re.search(r'xmlns(?::(\w+))?="([^"]+)"', logconfig_xml)
        if namespace_match:
            namespace_prefix = namespace_match.group(1) or ''
            namespace_uri = namespace_match.group(2)
            ET.register_namespace(namespace_prefix, namespace_uri)
        else:
            # Default fallback namespaces
            ET.register_namespace('logging', 'http://www.sas.com/xml/logging/1.0/')
        
        try:
            # Grab the full declaration line if it exists, so we can put it back when we update the logconfig.
            declaration_match = re.match(r'^\s*(<\?xml[^>]*\?>)', logconfig_xml)
            original_xml_declaration = declaration_match.group(1) if declaration_match else None
            # Read in the XML file.
            root = ET.fromstring(logconfig_xml)
            logconfig_changed = False
            print(f"Checking logconfig named {item.get('name')} for server {server}...")
            # For each logger element in the logconfig, get the name and level and print it out if it's set to debug or trace.
            for logger in root.iter('logger'):
                logger_name = logger.get('name')
                # level is a child element of logger, so we need to find the level element and get the value of the level attribute
                level_element = logger.find('level')
                logger_level = level_element.get('value') if level_element is not None else "UNKNOWN"
                # Upcase the level to make it easier to compare
                logger_level = logger_level.upper()
                # If we aren't verbose and the logger level isn't debug or trace, skip it.
                if not verbose and logger_level not in ["DEBUG", "TRACE"]:
                    continue
                # If we are verbose, we'll print out the logger name and level even if it isn't trace or debug.
                print(f"Found logger {logger_name} with level {logger_level} in {item.get('name')} for server {server}.")

                if logger_level in ["DEBUG", "TRACE"]:
                    # print(f"Logger {logger_name} in {item.get('name')} is set to {logger_level}.")
                    # If we've set the notrace or nodebug options and the configuration is not default, change the logging level as needed
                    if logger_level == "TRACE" and notrace and nodebug and not item.get('metadata', {}).get('isDefault', True):
                        print(f"Logging level for {logger_name} is Trace and notrace and nodebug are set. Changing to INFO.")
                        level_element.set('value', 'INFO')
                        logconfig_changed = True
                    elif logger_level == "TRACE" and notrace and not item.get('metadata', {}).get('isDefault', True):
                        print(f"Logging level for {logger_name} is Trace and notrace is set. Changing to DEBUG.")
                        level_element.set('value', 'DEBUG')
                        logconfig_changed = True
                    elif logger_level == "DEBUG" and nodebug and not item.get('metadata', {}).get('isDefault', True):
                        print(f"Logging level for {logger_name} is Debug and nodebug is set. Changing to INFO.")
                        level_element.set('value', 'INFO')
                        logconfig_changed = True
            # There is also a "root" object with a level that applies to all loggers that do not have a level explicitly set. We need to check this as well.
            root_level_element = root.find('root/level')
            if root_level_element is not None:
                root_logger_level = root_level_element.get('value', "UNKNOWN").upper()
                if not verbose and root_logger_level not in ["DEBUG", "TRACE"]:
                    continue
                print(f"Found root logger with level {root_logger_level} in {item.get('name')} for server {server}.")
                if root_logger_level in ["DEBUG", "TRACE"]:
                    if root_logger_level == "TRACE" and notrace and nodebug and not item.get('metadata', {}).get('isDefault', True):
                        print(f"Root logging level is Trace and notrace and nodebug are set. Changing to INFO.")
                        root_level_element.set('value', 'INFO')
                        logconfig_changed = True
                    elif root_logger_level == "TRACE" and notrace and not item.get('metadata', {}).get('isDefault', True):
                        print(f"Root logging level is Trace and notrace is set. Changing to DEBUG.")
                        root_level_element.set('value', 'DEBUG')
                        logconfig_changed = True
                    elif root_logger_level == "DEBUG" and nodebug and not item.get('metadata', {}).get('isDefault', True):
                        print(f"Root logging level is Debug and nodebug is set. Changing to INFO.")
                        root_level_element.set('value', 'INFO')
                        logconfig_changed = True
            # If we made any changes to the logconfig, we need to update the configuration service with the new logconfig content
            if logconfig_changed:
                new_logconfig_xml = ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')
                if original_xml_declaration:
                    new_logconfig_xml = re.sub(r'^\s*<\?xml[^>]*\?>', original_xml_declaration, new_logconfig_xml, count=1)
                print(f"Updating logconfig for {item.get('name')} in server {server}...")
                item["contents"] = new_logconfig_xml
                # Pull the reqtype and reqval for updating the configuration the items "update" relation link
                # Find the link of type "update" in the item links
                update_link = next((link for link in item.get('links', []) if link.get('rel') == 'update'), None)
                if update_link:
                    contentType = update_link.get('type')
                    reqval = update_link.get('href')
                    reqtype = update_link.get('method', 'put').lower()
                    print(f"Updating logconfig using {reqtype.upper()} on {reqval} ...")
                    results = callrestapi(reqval, reqtype, contentType=contentType, data=item)
                else:
                    print(f"No update link found for {item.get('name')} in server {server}. Cannot update logconfig.")
        except ET.ParseError as e:
            print(f"Error parsing logconfig XML for {item.get('name')}: {e}")
    

# If kubectl execution is enabled, we will also check for any loggers set to debug or trace directly in consul. 
# This is because some loggers may be set directly in consul and not through the configuration service, and these loggers would not be captured by the previous steps.
if kubectl_enabled:

### Consul keys -- Check for logging.level definitions set directly in consul, bypassing the configuration service. ###

    # Now we need to check for any loggers set to debug or trace directly in consul. The consul server does not have an ingress defined,
    #  so we need to use the sas-bootstrap-config command run in the rabbitmq pod to check for any keys /config/*/logging.level.
    #  We need to run this command in the rabbitmq pod, so we will use the kubectl exec command to do this.
    # The namespace is set using argparser, defaulting to "viya", the pod is "sas-rabbitmq-server-0", and the container "sas-rabbitmq-server".
    # The command we need to run is /opt/sas/viya/home/bin/sas-bootstrap-config kv read --recurse config/ | grep logging.level.
    # This will provide output like the following:
    # For a single service:
    # config/compute/logging.level/logger.name=DEBUG
    # For a global logger:
    # config/application/logging.level/logger.name2=trace

    # We will use the subprocess module to run this command and capture the output.
    # Define the command to run in the rabbitmq pod
    command = [
        'kubectl', 'exec', '-n', namespace, 'sas-rabbitmq-server-0', '-c', 'sas-rabbitmq-server',
        '--', '/opt/sas/viya/home/bin/sas-bootstrap-config', 'kv', 'read', '--recurse', 'config/'
    ]
    print("Checking logging.level entries in consul...")
    # Run the command and capture the output
    try:
        output = subprocess.check_output(command, universal_newlines=True)
    
        lines = output.splitlines()
        
        # Iterate through each line and check for logging.level entries
        for line in lines:
            
            # Some lines may be a continuation of the previous line, so we need to check if the line starts with "config/".
            if not line.startswith('config/'):
                continue

            # Get the key name (value before the equals sign) and value (value after the equals sign) for each line.
            key, value = line.split('=', 1)

            if 'logging.level' in key:
                # Extract the application name from the key
                # The key is in the format config/<application>/logging.level/<logger_name>
                # We will split the key by '/' and take the second last element as the application name            
                service_name = key.split('/')[1]
                # Extract the logger name from the key
                logger_name = key.split('/')[-1]

                if not verbose and value.strip().upper() not in ["DEBUG", "TRACE"]:
                    continue
                print(f"Service: {service_name} Logger: {logger_name} Level: {value.strip()}.")
                
                # Check if the value is DEBUG or TRACE, tolerating case differences
                if value.strip().upper() in ['DEBUG', 'TRACE']:
                    print(f"Logger {logger_name} is set to {value.strip()}.")
                    
                    # If we've set the notrace or nodebug options, change the logging level as needed
                    if value.strip().upper() == "TRACE" and notrace and nodebug:
                        print(f"Logging level for {logger_name} is Trace and notrace and nodebug are set. Changing to INFO.")
                        new_value = "INFO"
                    elif value.strip().upper() == "TRACE" and notrace:
                        print(f"Logging level for {logger_name} is Trace and notrace is set. Changing to DEBUG.")
                        new_value = "DEBUG"
                    elif value.strip().upper() == "DEBUG" and nodebug:
                        print(f"Logging level for {logger_name} is Debug and nodebug is set. Changing to INFO.")
                        new_value = "INFO"
                    else:
                        continue

                    # Define a command to update the logging level if needed
                    update_command = [
                        'kubectl', 'exec', '-n', namespace, 'sas-rabbitmq-server-0', '-c', 'sas-rabbitmq-server',
                        '--', '/opt/sas/viya/home/bin/sas-bootstrap-config', 'kv', 'write', '--force', key, new_value
                    ]
                    
                    # Run the update command
                    try:
                        subprocess.run(update_command, check=True)
                        print(f"Updated {logger_name} logging level to {new_value}.")

                    except subprocess.CalledProcessError as e:
                        print(f"Error updating {logger_name} logging level: {e}")
        
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)

### Kubernetes environment variables -- Check for logging levels set by environment variables in deployments, daemonsets and statefulsets ###

    # Now we need to check for any logging levels set by setting an environment variable starting with SAS_LOG_LEVEL or LOGGING_LEVEL
    # in the deployment, daemonset or statefulset objects
    print("Checking for environment variables starting with SAS_LOG_LEVEL or LOGGING_LEVEL in deployments, daemonsets and statefulsets...")
    # Define the command to get all deployments, daemonsets and statefulsets in the viya namespace
    command = [
        'kubectl', 'get', 'deployments,daemonsets,statefulsets', '-n', namespace, '-o', 'json'
    ]
    # Run the command and capture the output
    try:
        output = subprocess.check_output(command, universal_newlines=True)
        # Convert the JSON string to a Python dictionary
        resources = json.loads(output)
        # Check if the resources contain items
        if 'items' not in resources or not resources['items']:
            print(f"No deployments, daemonsets or statefulsets found in the {namespace} namespace.")
        else:
            print(f"Found {len(resources['items'])} deployments, daemonsets or statefulsets in the {namespace} namespace.")
        
        # Iterate through each resource type
        for resource_type in resources['items']:
            # Check if the resource has environment variables
            if 'spec' in resource_type and 'template' in resource_type['spec'] and 'spec' in resource_type['spec']['template']:
                containers = resource_type['spec']['template']['spec'].get('containers', [])
                for container in containers:
                    env_vars = container.get('env', [])
                    for env_var in env_vars:
                        if env_var.get('name', '').startswith(('SAS_LOG_LEVEL', 'LOGGING_LEVEL')):
                            if not verbose and env_var.get('value', '').strip().upper() not in ["DEBUG", "TRACE"]:
                                continue
                            print(f"Resource: {resource_type['metadata']['name']}, Container: {container['name']}, Environment Variable: {env_var['name']}, Value: {env_var['value']}")
                            # Check if the value is DEBUG or TRACE, tolerating case differences
                            if env_var['value'].strip().upper() in ['DEBUG', 'TRACE']:
                                # print(f"Environment variable {env_var['name']} in {resource_type['kind'].lower()} {resource_type['metadata']['name']} is set to {env_var['value']}.")
                                # We'll need to update this environment variable if the notrace or nodebug options are set
                                # this means we'll need to know the container index and the environment variable index where we found the value
                                # so we can patch the deployment, daemonset or statefulset object.

                                # Get the index number of the container and environment variable
                                container_index = containers.index(container)
                                env_var_index = env_vars.index(env_var)
                                # print(f"Container index: {container_index}, Environment variable index: {env_var_index}")
                                
                                # If we've set the notrace or nodebug options, change the logging level as needed
                                if env_var['value'].strip().upper() == "TRACE" and notrace and nodebug:
                                    print(f"Logging level for {env_var['name']} is Trace and notrace and nodebug are set. Changing to INFO.")
                                    new_value = "INFO"
                                elif env_var['value'].strip().upper() == "TRACE" and notrace:
                                    print(f"Logging level for {env_var['name']} is Trace and notrace is set. Changing to DEBUG.")
                                    new_value = "DEBUG"
                                elif env_var['value'].strip().upper() == "DEBUG" and nodebug:
                                    print(f"Logging level for {env_var['name']} is Debug and nodebug is set. Changing to INFO.")
                                    new_value = "INFO"
                                else:
                                    continue

                                # Define a command to update the environment variable if needed, using the indexes found and the kubectl patch command
                                update_command = [
                                    'kubectl', 'patch', resource_type['kind'].lower(), resource_type['metadata']['name'],
                                    '-n', namespace,
                                    '--type=json',
                                    '-p', f'[{{"op": "replace", "path": "/spec/template/spec/containers/{container_index}/env/{env_var_index}/value", "value": "{new_value}"}}]'
                                ]
                                
                                # Run the update command
                                try:
                                    subprocess.run(update_command, check=True)
                                    print(f"Updated {env_var['name']} logging level to {new_value} in {resource_type['metadata']['name']}.")

                                except subprocess.CalledProcessError as e:
                                    print(f"Error updating {env_var['name']} logging level: {e}")

    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)

### Kubernetes envFrom -- Check for logging levels set by environment variables in configMaps ###

# Check configMaps that could be setting this using envFrom.
    print("Checking for environment variables starting with SAS_LOG_LEVEL or LOGGING_LEVEL in configMaps...")
    # Define the command to get all configmaps in the namespace
    command = [
        'kubectl', 'get', 'configmaps', '-n', namespace, '-o', 'json'
    ]
    # Run the command and capture the output
    try:
        output = subprocess.check_output(command, universal_newlines=True)
        # Convert the JSON string to a Python dictionary
        configmaps = json.loads(output)
        # Check if the configmaps contain items
        if 'items' not in configmaps or not configmaps['items']:
            print(f"No configmaps found in the {namespace} namespace.")
        else:
            print(f"Found {len(configmaps['items'])} configmaps in the {namespace} namespace.")
        
        for configmap in configmaps['items']:
            data = configmap.get('data', {})
            for key, value in data.items():
                if key.startswith(('SAS_LOG_LEVEL', 'LOGGING_LEVEL')):
                    if not verbose and value.strip().upper() not in ["DEBUG", "TRACE"]:
                        continue
                    print(f"ConfigMap: {configmap['metadata']['name']}, Key: {key}, Value: {value}")
                    # Check if the value is DEBUG or TRACE, tolerating case differences
                    if value.strip().upper() in ['DEBUG', 'TRACE']:
                        print(f"ConfigMap {configmap['metadata']['name']} has key {key} set to {value}.")
                        # If we've set the notrace or nodebug options, change the logging level as needed
                        if value.strip().upper() == "TRACE" and notrace and nodebug:
                            print(f"Logging level for {key} in ConfigMap {configmap['metadata']['name']} is Trace and notrace and nodebug are set. Changing to INFO.")
                            new_value = "INFO"
                        elif value.strip().upper() == "TRACE" and notrace:
                            print(f"Logging level for {key} in ConfigMap {configmap['metadata']['name']} is Trace and notrace is set. Changing to DEBUG.")
                            new_value = "DEBUG"
                        elif value.strip().upper() == "DEBUG" and nodebug:
                            print(f"Logging level for {key} in ConfigMap {configmap['metadata']['name']} is Debug and nodebug is set. Changing to INFO.")
                            new_value = "INFO"
                        else:
                            continue

                        # Define a command to update the configmap key if needed, using the kubectl patch command
                        update_command = [
                            'kubectl', 'patch', 'configmap', configmap['metadata']['name'],
                            '-n', namespace,
                            '--type=json',
                            '-p', f'[{{"op": "replace", "path": "/data/{key}", "value": "{new_value}"}}]'
                        ]
                        # Run the update command
                        try:
                            subprocess.run(update_command, check=True)
                            print(f"Updated {key} logging level to {new_value} in ConfigMap {configmap['metadata']['name']}.")
                        except subprocess.CalledProcessError as e:
                            print(f"Failed to update {key} logging level in ConfigMap {configmap['metadata']['name']}: {e}")
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)

### Kubernetes podTemplates -- Check for logging levels set by environment variables in podTemplates ###

# Need to check podTemplate objects for any environment variables starting with SAS_LOG_LEVEL or LOGGING_LEVEL as well, as these could be used to set logging levels too.
# PodTemplates start with /template rather than /spec/template like the other objects, so we need to check these separately.
    print("Checking for environment variables starting with SAS_LOG_LEVEL or LOGGING_LEVEL in podTemplates...")
    # Define the command to get all podTemplates in the namespace
    command = [
        'kubectl', 'get', 'podtemplates', '-n', namespace, '-o', 'json'
    ]
    # Run the command and capture the output
    try:
        output = subprocess.check_output(command, universal_newlines=True)
        # Convert the JSON string to a Python dictionary
        podtemplates = json.loads(output)
        # Check if the podtemplates contain items
        if 'items' not in podtemplates or not podtemplates['items']:
            print(f"No podTemplates found in the {namespace} namespace.")
        else:
            print(f"Found {len(podtemplates['items'])} podTemplates in the {namespace} namespace.")
        
        for podtemplate in podtemplates['items']:
            template = podtemplate.get('template', {})
            spec = template.get('spec', {})
            containers = spec.get('containers', [])
            for container in containers:
                env_vars = container.get('env', [])
                for env_var in env_vars:
                    if env_var.get('name', '').startswith(('SAS_LOG_LEVEL', 'LOGGING_LEVEL')):
                        if not verbose and env_var.get('value', '').strip().upper() not in ["DEBUG", "TRACE"]:
                            continue
                        print(f"PodTemplate: {podtemplate['metadata']['name']}, Container: {container['name']}, Environment Variable: {env_var['name']}, Value: {env_var['value']}")
                        # Check if the value is DEBUG or TRACE, tolerating case differences
                        if env_var['value'].strip().upper() in ['DEBUG', 'TRACE']:
                            print(f"Environment variable {env_var['name']} in PodTemplate {podtemplate['metadata']['name']} is set to {env_var['value']}.")
                            # If we've set the notrace or nodebug options, change the logging level as needed
                            if env_var['value'].strip().upper() == "TRACE" and notrace and nodebug:
                                print(f"Logging level for {env_var['name']} in PodTemplate {podtemplate['metadata']['name']} is Trace and notrace and nodebug are set. Changing to INFO.")
                                new_value = "INFO"
                            elif env_var['value'].strip().upper() == "TRACE" and notrace:
                                print(f"Logging level for {env_var['name']} in PodTemplate {podtemplate['metadata']['name']} is Trace and notrace is set. Changing to DEBUG.")
                                new_value = "DEBUG"
                            elif env_var['value'].strip().upper() == "DEBUG" and nodebug:
                                print(f"Logging level for {env_var['name']} in PodTemplate {podtemplate['metadata']['name']} is Debug and nodebug is set. Changing to INFO.")
                                new_value = "INFO"
                            else:
                                continue
                            # Define a command to update the podtemplate key if needed, using the kubectl patch command
                            container_index = containers.index(container)
                            env_var_index = env_vars.index(env_var)
                            update_command = [
                                'kubectl', 'patch', 'podtemplate', podtemplate['metadata']['name'],
                                '-n', namespace,
                                '--type=json',
                                '-p', f'[{{"op": "replace", "path": "/template/spec/containers/{container_index}/env/{env_var_index}/value", "value": "{new_value}"}}]'
                            ]
                            # Run the update command
                            try:
                                subprocess.run(update_command, check=True)
                                print(f"Updated {env_var['name']} logging level to {new_value} in PodTemplate {podtemplate['metadata']['name']}.")
                            except subprocess.CalledProcessError as e:
                                print(f"Failed to update {env_var['name']} logging level in PodTemplate {podtemplate['metadata']['name']}: {e}")
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)

### CAS servers -- Check for logging levels set in CAS servers ###

# Get a list of all CAS servers
reqtype='get'
reqval='/casManagement/servers'
print('Calling REST endpoint:',reqval)
results=callrestapi(reqval,reqtype)
servers = results['items']

print(f"Found {len(servers)} CAS servers.")

# Iterate through each server
for server in servers:

    # Get the name of the server
    servername=server['name']
    print(f"Checking loggers for CAS server: {servername}...")
    
    # Get a CAS session and assume superuser role just in case we need to update any loggers.
    # Get CAS Session
    reqtype='post'
    reqval='/casManagement/servers/'+servername+'/sessions'
    print('Calling REST endpoint:',reqval)
    results=callrestapi(reqval,reqtype)
    session = results['id']
    print('Created session on server:',servername,'Session ID:',session)

    # Assume the superuser role
    reqtype='put'
    reqval='/casAccessManagement/servers/'+servername+'/admUser/assumeRole/superUser?sessionId='+session
    print('Calling REST endpoint:',reqval)
    results=callrestapi(reqval,reqtype)
    print('Assumed superuser role on server:',servername)

    # Pull the list of loggers and levels
    reqval='/casManagement/servers/'+servername+'/loggers?limit=10000&sessionId='+session
    reqtype='get'
    print('Calling REST endpoint:',reqval)
    results=callrestapi(reqval,reqtype)
    loggers = results['items']
    print(f"Found {len(loggers)} loggers for CAS server: {servername}.")

    # Iterate through each logger
    for logger in loggers:
        loggername=logger['name']
        loggerlevel=logger['level']
        if not verbose and loggerlevel.upper() not in ["DEBUG", "TRACE"]:
            continue
        print(f"Logger: {loggername} Level: {loggerlevel}.")

        # If the log level is set to debug or trace, output the logger details
        if loggerlevel.upper() in ["DEBUG", "TRACE"]:
            #print('Server:',servername,'Logger:',loggername,'Level:',loggerlevel)

            #If we've set the notrace or nodebug options, change the logging level as needed
            if loggerlevel.upper() == "TRACE" and notrace and nodebug:
                print("Logging level is Trace and notrace and nodebug are set. Changing to info.")
                logger['level'] = "info"
                logger['applyToController'] = True
                reqval='/casManagement/servers/'+servername+'/loggers/'+loggername+'?sessionId='+session
                reqtype='put'
                print('Calling REST endpoint:',reqval)
                results=callrestapi(reqval,reqtype,contentType='application/vnd.sas.cas.server.logger+json',data=logger)
            elif loggerlevel.upper() == "TRACE" and notrace:
                print("Logging level is Trace and notrace is set. Changing to debug.")
                logger['level'] = "debug"
                logger['applyToController'] = True
                reqval='/casManagement/servers/'+servername+'/loggers/'+loggername+'?sessionId='+session
                reqtype='put'
                print('Calling REST endpoint:',reqval)
                results=callrestapi(reqval,reqtype,contentType='application/vnd.sas.cas.server.logger+json',data=logger)
            elif loggerlevel.upper() == "DEBUG" and nodebug:
                print("Logging level is Debug and nodebug is set. Changing to info.")
                logger['level'] = "info"
                logger['applyToController'] = True
                reqval='/casManagement/servers/'+servername+'/loggers/'+loggername+'?sessionId='+session
                reqtype='put'
                print('Calling REST endpoint:',reqval)
                results=callrestapi(reqval,reqtype,contentType='application/vnd.sas.cas.server.logger+json',data=logger)

    # We're finished, so terminate the CAS session
    reqtype='delete'
    reqval='/casManagement/servers/'+servername+'/sessions/'+session
    print('Calling REST endpoint:',reqval)
    results=callrestapi(reqval,reqtype)
    print('Terminated session on server:',servername)
