'''
Module to interact with Globus data transfer services.

@author: Luca Cinquini
'''

from datetime import datetime, timedelta
from cog.site_manager import siteManager
if siteManager.isGlobusEnabled():    
    from globus_sdk.transfer import TransferData
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


def activateEndpoint(transfer_client, endpoint, openid=None, password=None):

    if not openid or not password:
        # Try to autoactivate the endpoint
        code, reason, result = transfer_client.endpoint_autoactivate(endpoint, if_expires_in=2880)
        print("Endpoint Activation: %s. %s: %s" % (endpoint, result["code"], result["message"]))
        if result["code"] == "AutoActivationFailed":
            return (False, "")
        return (True, "")

    openid_parsed = urllib.parse.urlparse(openid)
    hostname = openid_parsed.hostname
    username = os.path.basename(openid_parsed.path)
    code, reason, reqs = transfer_client.endpoint_get_activation_requirements(endpoint)

    # Activate the endpoint using an X.509 user credential stored by esgf-idp in /tmp/x509up_<idp_hostname>_<username>
    #cred_file = "/tmp/x509up_%s_%s" % (hostname, username)
    #public_key = reqs.get_requirement_value("delegate_proxy", "public_key")
    #try:
    #    proxy = x509_proxy.create_proxy_from_file(cred_file, public_key, lifetime_hours=72)
    #except Exception as e:
    #    print "Could not activate the endpoint: %s. Error: %s" % (endpoint, str(e))
    #    return False
    #reqs.set_requirement_value("delegate_proxy", "proxy_chain", proxy)

    # Activate the endpoint using MyProxy server method
    for i, d in enumerate(req["DATA"]):
        if d["type"] == "myproxy":
            if d["name"] == "hostname":
                req["DATA"][i]["value"] = hostname
            elif d["name"] == "username":
                req["DATA"][i]["value"] = username
            elif d["name"] == "passphrase":
                req["DATA"][i]["value"] = password
            elif d["name"] == "lifetime_in_hours":
                req["DATA"][i]["value"] = "168"

    try:
        code, reason, result = transfer_client.endpoint_activate(endpoint, reqs)
    except Exception as e:
        print("Could not activate the endpoint: %s. Error: %s" % (endpoint, str(e)))
        return (False, str(e))
    if code != 200:
        print("Could not aactivate the endpoint: %s. Error: %s - %s" % (endpoint, result["code"], result["message"]))
        return (False, result["message"])

    print("Endpoint Activation: %s. %s: %s" % (endpoint, result["code"], result["message"]))

    return (True, "")


def submitTransfer(transfer_client, source_endpoint, source_files, target_endpoint, target_directory):
    '''
    Method to submit a data transfer request to Globus.
    '''
    
    # obtain a submission id from Globus
    # code, message, data = transfer_client.transfer_submission_id()
    # submission_id = data["value"]
    # print "Obtained transfer submission id: %s" % submission_id
    
    # maximum time for completing the transfer
    deadline = datetime.utcnow() + timedelta(days=10)
    
    # create a transfer request
    transfer_task = Transfer(transfer_client, source_endpoint, target_endpoint, deadline=deadline)
    print("Obtained transfer submission id: %s" % transfer_task["submission_id"])
    for source_file in source_files:
        source_directory, filename = os.path.split(source_file)
        target_file = os.path.join(target_directory, filename) 
        transfer_task.add_item(source_file, target_file)
    
    # submit the transfer request
    try:
        code, reason, data = transfer_client.submit_transfer(transfer_task)
        task_id = data["task_id"]
        print("Submitted transfer task with id: %s" % task_id)
    except Exception as e:
        print("Could not submit the transfer. Error: %s" % str(e))
        task_id = "Could not submit the transfer. Please contact the ESGF node admin to investigate the issue."
    
    return task_id
