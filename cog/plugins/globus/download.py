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

def activateEndpoints(gendpoint, uendpoint, username, sshkey):
	gendpointBase = gendpoint.split('/')[0]
	uendpointBase = uendpoint.split('/')[0]

	os.system("ssh " + sshkey + " " + username + "@cli.globusonline.org endpoint-activate " + gendpointBase)
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

def getFiles(gendpoint, uendpoint, username, sshkey):
	label = str(uuid4())

	basename = os.path.basename(gendpoint)
	if uendpoint[-1] != '/':
		uendpoint = uendpoint + '/' + basename
	else:
		uendpoint = uendpoint + basename

	os.system("echo '" + gendpoint + " " + uendpoint + "' | ssh " + sshkey + "  " + username + "@cli.globusonline.org transfer --verify-checksum --encrypt --label=" + label + " --delete") 

	return

if __name__ == '__main__':
	gendpointList = ["esg#jpl/esg_dataroot/obs4MIPs/observations/atmos/cltStddev/mon/grid/NASA-GSFC/MODIS/v20111130/cltStddev_MODIS_L3_C5_200003-201109.nc","esg#jpl/esg_dataroot/obs4MIPs/observations/atmos/taStderr/mon/grid/NASA-JPL/AIRS/v20110608/taStderr_AIRS_L3_RetStd-v5_200209-201105.nc"]
	uendpoint, username, sshkey = arguments(sys.argv[1:])
	os.system("ssh-add " + sshkey)
	if sshkey != '':
		sshkey = '-i ' + sshkey
	activateEndpoints(gendpointList[0], uendpoint, username, sshkey)
	for gendpoint in gendpointList:
		getFiles(gendpoint, uendpoint, username, sshkey)
