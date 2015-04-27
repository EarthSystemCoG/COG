'''
Module to interact with Globus Online ("GO") data transfer services.

@author: Luca Cinquini
'''

import time
from datetime import datetime, timedelta
from globusonline.transfer.api_client import Transfer
from globusonline.transfer.api_client import TransferAPIClient
import os
from os.path import expanduser, join

import logging

ACCESS_TOKEN_FILE = ".goauth-token.secret"
DOWNLOAD_SCRIPT = "download.py"

def generateGlobusDownloadScript(download_map):

    print "Generating script for downloading files: "
    print download_map

    # read script 'download.py' located in same directory
    scriptFile = os.path.join(os.path.dirname(__file__), DOWNLOAD_SCRIPT)
    with open(scriptFile, 'r') as f:
        script = f.read().strip()
    script = script.replace('{}##GENDPOINTDICT##', str(download_map))

    return script
    

# FIXME: use web workflow instead
def get_access_token():
    
    filepath = os.path.join(os.path.expanduser("~"), ACCESS_TOKEN_FILE)
    
    try:
        with open(filepath, 'r') as f:
            access_token = f.read().strip()
            return access_token
    except IOError:
        # file not found
        logging.warn("Access token file not found: %s" % filepath) 
        return None


def submiTransfer(username, access_token, source_endpoint, source_files, target_endpoint, target_directory):
    '''
    Method to submit a transfer request to Globus Online.
    '''
    
    # instantiate GO client
    goapi_client = TransferAPIClient(username, goauth=access_token)
    
    # activate source endpoint
    # currently this method does not work - source endpoint must be activated manually from web interface
    # TODO: ask Rachana how to programmatically activate the source endpoint and what credentials to use
    # NOTE: must use JPL MyProxy uder credentials
    #code, reason, result = goapi_client.endpoint_autoactivate(source_endpoint, if_expires_in=600)
    #print "Source Endpoint Activation:: %s (%s)" % (result["code"], result["message"])
    
    # target_endpoint endpoint can be automatically activated using cached credentials
    code, reason, result = goapi_client.endpoint_autoactivate(target_endpoint, if_expires_in=600)
    print "Target Endpoint Activation: : %s (%s)" % (result["code"], result["message"])
        
    # obtain a submission id from GO
    code, message, data = goapi_client.transfer_submission_id()
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
    code, reason, data = goapi_client.transfer(transfer_task)
    task_id = data["task_id"]
    print "Submitted transfer task with id: %s" % task_id
    
    return task_id

if __name__ == '__main__':

    # authentication parameters 
    username = "cinquiniluca"
    access_token = get_access_token()
    
    # files to transfer
    # these are obtained from the GridFTP URls by removing the "gsiftp://<hostname:port>" part, which is implicit in the "esg#jpl" source endpoint configuration
    sourceFiles = ["/esg_dataroot/obs4MIPs/observations/atmos/husNobs/mon/grid/NASA-JPL/AIRS/v20110608/husNobs_AIRS_L3_RetStd-v5_200209-201105.nc",
                   "/esg_dataroot/obs4MIPs/observations/atmos/taStderr/mon/grid/NASA-JPL/AIRS/v20110608/taStderr_AIRS_L3_RetStd-v5_200209-201105.nc"]

    # source endpoint - this is the JPL server
    source_endpoint = "esg#jpl"
    
    # target endpoint - this is the user own's laptop
    target_endpoint = "cinquiniluca#mymac"
    
    # target directory to store files
    target_directory = "/~" # is this a GO custom notation ?

    # submit transfer request
    task_id = submiTransfer(username, access_token, source_endpoint, sourceFiles, target_endpoint, target_directory)
    
    print "Task id=%s submitted, monitor your task at: https://www.globus.org/xfer/ViewActivity" % task_id