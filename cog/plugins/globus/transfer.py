'''
Module to interact with Globus data transfer services.

@author: Luca Cinquini
'''

from datetime import datetime, timedelta
from cog.site_manager import siteManager
if siteManager.isGlobusEnabled():    
    from globusonline.transfer.api_client import Transfer
    from globusonline.transfer.api_client import TransferAPIClient
    from globusonline.transfer.api_client import TransferAPIError
    from globusonline.transfer.api_client import x509_proxy
import os
import urlparse

DOWNLOAD_SCRIPT = "download.py"

def generateGlobusDownloadScript(download_map):

    print "Generating script for downloading files: "
    print download_map

    # read script 'download.py' located in same directory as this module
    scriptFile = os.path.join(os.path.dirname(__file__), DOWNLOAD_SCRIPT)
    with open(scriptFile, 'r') as f:
        script = f.read().strip()
    script = script.replace('{}##GENDPOINTDICT##', str(download_map))

    return script


def activateEndpoint(api_client, endpoint, myproxy_server=None, username=None, password=None, cert=None, key=None):
    if (not myproxy_server or not password) and (not myproxy_server or not cert):
        # Try to autoactivate the endpoint
        code, reason, result = api_client.endpoint_autoactivate(endpoint, if_expires_in=2880)
        print "Endpoint Activation: %s. %s: %s" % (endpoint, result["code"], result["message"])
        if result["code"] == "AutoActivationFailed":
            return (False, "")
        return (True, "")

    code, reason, reqs = api_client.endpoint_activation_requirements(endpoint)

    # Activate the endpoint using an X.509 user credential stored by esgf-idp in /tmp/x509up_<idp_hostname>_<username>
    if cert and key:
        cred_file = "/tmp/x509up_%s_%s" % (myproxy_server, username)
        with open(cred_file, 'w') as cred:
            cred.write(cert)
            cred.write(key)
        public_key = reqs.get_requirement_value("delegate_proxy", "public_key")
        try:
            proxy = x509_proxy.create_proxy_from_file(cred_file, public_key, lifetime_hours=72)
        except Exception as e:
            print "Could not activate the endpoint: %s. Error: %s" % (endpoint, str(e))
            return False
        reqs.set_requirement_value("delegate_proxy", "proxy_chain", proxy)
    else:
        # Activate the endpoint using MyProxy server method
        reqs.set_requirement_value("myproxy", "hostname", myproxy_server)
        reqs.set_requirement_value("myproxy", "username", username)
        reqs.set_requirement_value("myproxy", "passphrase", password)
        reqs.set_requirement_value("myproxy", "lifetime_in_hours", "168")

    try:
        code, reason, result = api_client.endpoint_activate(endpoint, reqs)
    except Exception as e:
        print "Could not activate the endpoint: %s. Error: %s" % (endpoint, str(e))
        return (False, str(e))
    if code != 200:
        print "Could not aactivate the endpoint: %s. Error: %s - %s" % (endpoint, result["code"], result["message"])
        return (False, result["message"])

    print "Endpoint Activation: %s. %s: %s" % (endpoint, result["code"], result["message"])

    return (True, "")


def submitTransfer(api_client, source_endpoint, source_files, target_endpoint, target_directory):
    '''
    Method to submit a data transfer request to Globus.
    '''
    
    # obtain a submission id from Globus
    code, message, data = api_client.transfer_submission_id()
    submission_id = data["value"]
    print "Obtained transfer submission id: %s" % submission_id
    
    # maximum time for completing the transfer
    deadline = datetime.utcnow() + timedelta(days=10)
    
    # create a transfer request
    transfer_task = Transfer(submission_id, source_endpoint, target_endpoint, deadline)
    for source_file in source_files:
        source_directory, filename = os.path.split(source_file)
        target_file = os.path.join(target_directory, filename) 
        transfer_task.add_item(source_file, target_file)
    
    # submit the transfer request
    try:
        code, reason, data = api_client.transfer(transfer_task)
        task_id = data["task_id"]
        print "Submitted transfer task with id: %s" % task_id
    except Exception as e:
        print "Could not submit the transfer. Error: %s" % str(e)
        task_id = "Could not submit the transfer. Please contact the ESGF node admin to investigate the issue."
    
    return task_id
