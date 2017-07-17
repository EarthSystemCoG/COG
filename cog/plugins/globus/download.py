import sys
import argparse
import os

from random import SystemRandom
from uuid import uuid4

def activateEndpoints(gendpointDict, uendpoint, username, sshkey):

    endNames = gendpointDict.keys()
    for thisEndName in endNames:
        os.system("ssh " + sshkey + " " + username + "@cli.globusonline.org endpoint-activate " + thisEndName)

    uendpointBase = uendpoint.split('/')[0]
    os.system("ssh " + sshkey + " " + username + "@cli.globusonline.org endpoint-activate " + uendpointBase)

    return

def arguments(argv):

    parser = argparse.ArgumentParser(description = '''To use this script, you must have added your SSH key your Gloubus profile.'''
            '''For reference see https://support.globus.org/entries/20979751-How-do-I-add-an-SSH-key-to-my-Globus-account-'''
            '''This script makes use of the Globus CLI 'transfer' command.  It will activate'''
            '''the appropriate endpoints.  By default, the transfer command will:'''
            '''verify the checksum of the transfer, encrypt the transfer, and delete any fies at the user endpoint with the same name.'''
            )
    parser.add_argument('-e', '--user-endpoint', type=str, help='endpoint you wish to download files to', required=True)
    parser.add_argument('-u', '--username', type=str, help='your Globus username', required=True)
    parser.add_argument('-p', '--path', type=str, help='the path on your endpoint where you want files to be downloaded to', default='/~/')
    parser.add_argument('-s', '--ssh-key', type=str, help='your SSH key file', default=' ')
    parser._optionals.title = 'required and optional arguments'
    args = parser.parse_args()

    username = args.username
    uendpoint = args.user_endpoint
    sshkey = args.ssh_key
    upath = args.path

    if '#' not in uendpoint:
        print "Please supply a valid Globus endpoint"
        sys.exit()
    if '/' in uendpoint:
        print "Do not include the download path in the endpoint name, please use the -p option"
        sys.exit()
    if '#' in upath:
        print "The '#' character is invalid in your path, please re-enter"
        sys.exit()
    if upath[0] != '/' and upath != '/~/':
        upath = '/' + upath
    if sshkey != ' ':
        sshkey = '-i ' + sshkey

    return (uendpoint, username, upath, sshkey)

def getFiles(gendpointDict, uendpoint, username, upath, sshkey):

    cryptogen = SystemRandom()
    transferFile = '/tmp/transferList' + str(cryptogen.randint(1,9999)) + '.txt'
    file = open(transferFile, 'w')

    label = str(uuid4())

    endNames = gendpointDict.keys()

    for thisEndName in endNames:

        fileList = gendpointDict[thisEndName]

        for thisFile in fileList:

            basename = os.path.basename(thisFile)

            if upath[-1] != '/':
                basename = '/' + basename

            remote = thisEndName + thisFile
            local = uendpoint + upath + basename

            file.write(remote + ' ' + local + '\n')

    file.close()

    os.system("cat '" + transferFile  + "' | ssh " + sshkey + "  " + username + "@cli.globusonline.org transfer --verify-checksum --encrypt --label=" + label + " --delete")

    os.remove(transferFile)

    return

if __name__ == '__main__':

    gendpointDict = {}##GENDPOINTDICT##
    uendpoint, username, upath, sshkey = arguments(sys.argv)
    #activateEndpoints(gendpointDict, uendpoint, username, sshkey)
    getFiles(gendpointDict, uendpoint, username, upath, sshkey)
