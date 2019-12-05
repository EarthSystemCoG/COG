'''
Module to interact with Globus data transfer services.

@author: Luca Cinquini
'''

from datetime import datetime, timedelta
from cog.site_manager import siteManager
if siteManager.isGlobusEnabled():    
    from globus_sdk import TransferData
import os
import urllib.parse

DOWNLOAD_SCRIPT = "download.py"

def generateGlobusDownloadScript(download_map):

    print("Generating script for downloading files: ")
    print(download_map)

    # read script 'download.py' located in same directory as this module
    scriptFile = os.path.join(os.path.dirname(__file__), DOWNLOAD_SCRIPT)
    with open(scriptFile, 'r') as f:
        script = f.read().strip()
    script = script.replace('{}##GENDPOINTDICT##', str(download_map))

    return script


def activateEndpoint(transfer_client, endpoint, myproxy_server=None, username=None, password=None):
    if not myproxy_server or not password:
        # Try to autoactivate the endpoint
        result = transfer_client.endpoint_autoactivate(endpoint, if_expires_in=2880)
        print("Endpoint Activation: %s. %s: %s" % (endpoint, result["code"], result["message"]))
        if result["code"] == "AutoActivationFailed":
            return (False, "")
        return (True, "")

    requirements = transfer_client.endpoint_get_activation_requirements(endpoint)
    requirements_json = requirements.data

    # Activate the endpoint using MyProxy server method
    for i, d in enumerate(requirements_json["DATA"]):
        if d["type"] == "myproxy":
            if d["name"] == "hostname":
                requirements_json["DATA"][i]["value"] = myproxy_server
            elif d["name"] == "username":
                requirements_json["DATA"][i]["value"] = username
            elif d["name"] == "passphrase":
                requirements_json["DATA"][i]["value"] = password
            elif d["name"] == "lifetime_in_hours":
                requirements_json["DATA"][i]["value"] = "168"

    try:
        result = transfer_client.endpoint_activate(endpoint, requirements_json)
    except Exception as e:
        print("Could not activate the endpoint: %s. Error: %s" % (endpoint, str(e)))
        return (False, str(e))
    if result["code"] != "Activated.MyProxyCredential":
        print("Could not aactivate the endpoint: %s. Error: %s - %s" % (endpoint, result["code"], result["message"]))
        return (False, result["message"])

    print("Endpoint Activation: %s. %s: %s" % (endpoint, result["code"], result["message"]))

    return (True, "")


def submitTransfer(transfer_client, source_endpoint, source_files, target_endpoint, target_directory):
    '''
    Method to submit a data transfer request to Globus.
    '''
    
    # maximum time for completing the transfer
    deadline = datetime.utcnow() + timedelta(days=10)
    
    # create a transfer request
    transfer_task = TransferData(transfer_client, source_endpoint, target_endpoint, deadline=deadline)
    print("Obtained transfer submission id: %s" % transfer_task["submission_id"])

    for source_file in source_files:
        source_directory, filename = os.path.split(source_file)
        target_file = os.path.join(target_directory, filename) 
        transfer_task.add_item(source_file, target_file)
    
    # submit the transfer request
    try:
        data = transfer_client.submit_transfer(transfer_task)
        task_id = data["task_id"]
        print("Submitted transfer task with id: %s" % task_id)
    except Exception as e:
        print("Could not submit the transfer. Error: %s" % str(e))
        task_id = "Could not submit the transfer. Please contact the ESGF node admin to investigate the issue."
    
    return task_id
