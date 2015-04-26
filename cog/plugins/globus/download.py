import sys
import getopt
import os

from uuid import uuid4

'''
To use this script, you must have added your SSH key your Gloubus profile.
For reference see https://support.globus.org/entries/20979751-How-do-I-add-an-SSH-key-to-my-Globus-account-

This script makes use of the Globus CLI 'transfer' command.  It will activate
the appropriate endpoints.  By default, the transfer command will:

 - verify the checksum of the transfer
 - encrypt the transfer
 - delete any fies at the user endpoint with the same name

User can call this script in the followin manner:

% python download.py -e <user endpoint> -u <username> -s <user SSH key file; optional>
'''

def activateEndpoints(gendpointDict, uendpoint, username, sshkey):
    endNames = gendpointDict.keys()
    for thisEndName in endNames:
        os.system("ssh " + sshkey + " " + username + "@cli.globusonline.org endpoint-activate " + thisEndName)

    uendpointBase = uendpoint.split('/')[0]
    os.system("ssh " + sshkey + " " + username + "@cli.globusonline.org endpoint-activate " + uendpointBase)

    return

def arguments(argv):
    uendpoint = ''
    username = ''
    sshkey = ''

    try:
        opts, args = getopt.getopt(argv,"he:u:s:")
    except getopt.GetoptError:
        print 'download.py -e <user endpoint> -u <username> -s <user SSH key file; optional>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -e <user endpoint> -u <username> -s <user SSH key file; optional>'
            sys.exit()
        elif opt in ("-e"):
            if '#' not in arg:
                print "Please supply a valid Globus enpoint"
                sys.exit()
            else:
                uendpoint = arg
        elif opt in ("-u"):
            username = arg
        elif opt in ("-s"):
            sshkey = arg

    return (uendpoint, username, sshkey)

def getFiles(gendpointDict, uendpoint, username, sshkey):
    label = str(uuid4())

    endNames = gendpointDict.keys()

    for thisEndName in endNames:

        fileList = gendpointDict[thisEndName]

        for thisFile in fileList:

            basename = os.path.basename(thisFile)

            if uendpoint[-1] != '/':
                basename = '/' + basename

            remote = thisEndName + thisFile
            local = uendpoint + basename
            os.system("echo '" + remote + " " + local + "' | ssh " + sshkey + "  " + username + "@cli.globusonline.org transfer --verify-checksum --encrypt --label=" + label + " --delete")

    return

if __name__ == '__main__':
    gendpointDict = ##GENDPOINTDICT##
    uendpoint, username, sshkey = arguments(sys.argv[1:])
    if sshkey != '':
        sshkey = '-i ' + sshkey
    activateEndpoints(gendpointDict, uendpoint, username, sshkey)
    getFiles(gendpointDict, uendpoint, username, sshkey)
