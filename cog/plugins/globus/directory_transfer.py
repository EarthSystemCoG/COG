import sys
import argparse
import os

from uuid import uuid4

'''
Example invocation:
python directory_transfer.py -r jplesgnode#public -p /obs4MIPs/observations/ocean/zos/mon/grid/CNES/AVISO -l <local endpoint>  -u <globus username>
'''

def activateEndpoints(gendpoint, uendpoint, username, sshkey):

	os.system("ssh " + sshkey + " " + username + "@cli.globusonline.org endpoint-activate " + gendpoint)
	os.system("ssh " + sshkey + " " + username + "@cli.globusonline.org endpoint-activate " + uendpoint)

	return

def arguments(argv):

	parser = argparse.ArgumentParser(description = '''To use this script, you must have added your SSH key your Gloubus profile.'''
		'''For reference see https://support.globus.org/entries/20979751-How-do-I-add-an-SSH-key-to-my-Globus-account-'''
		'''This script makes use of the Globus CLI 'transfer' command to move an entire directory from one endpoint to another.'''  
		'''It will activate the appropriate endpoints.  By default, the transfer command will:'''
		'''verify the checksum of the transfer, encrypt the transfer, syncronize the directoriesand delete any fies''' 
		'''at the user endpoint with the same name.'''
		)
	parser.add_argument('-r', '--remote-endpoint', type=str, help='remote endpoint', required=True)
	parser.add_argument('-l', '--local-endpoint', type=str, help='local', required=True)
	parser.add_argument('-u', '--username', type=str, help='your Globus username', required=True)
	parser.add_argument('-p', '--path', type=str, help='path with files you want to download', required=True)
	parser.add_argument('-d', '--download-location', type=str, help='locatio you wish to download files to on the local machine, /~/ by default', default='/~/')
	parser.add_argument('-s', '--ssh-key', type=str, help='your SSH key file', default=' ')
	parser._optionals.title = 'required and optional arguments'
	args = parser.parse_args()

	username = args.username
	gendpoint = args.remote_endpoint
	uendpoint = args.local_endpoint
	sshkey = args.ssh_key
	path = args.path
	dlocation = args.download_location

	if '#' not in uendpoint:
		print "Please supply a valid Globus endpoint (local host)"
		sys.exit()
	if '#' not in gendpoint:
		print "Please supply a valid Globus endpoint (remote host)"
	if '/' in uendpoint:
		print "Do not include the download path in the local endpoint name, please use the -p option"
		sys.exit()
	if '/' in gendpoint:
		print "Do not include the download path in the remote endpoint name, please use the -p option"
	if '#' in path:
		print "The '#' character is invalid in your path, please re-enter"
		sys.exit()
	if '#' in dlocation:
		print "The '#' character is invalid in your download location, please re-enter"
	if path[-1] != '/':
		path = path + '/'
	if path[0] != '/':
		path = '/' + path 
	if dlocation[-1] != '/':
		dlocation = dlocation + '/'
	if dlocation[0] != '/':
		dlocation = '/' + dlocation
	if sshkey != ' ':
		sshkey = '-i ' + sshkey

	return (gendpoint, uendpoint, username, path, dlocation, sshkey)

def getFiles(gendpoint, uendpoint, username, path, dlocation, sshkey):

	label = str(uuid4())	

	remote = gendpoint + path
	local = uendpoint + dlocation[:-1] + path

	os.system("echo '" + remote + " " + local + " -r' | ssh " + sshkey + "  " + username + "@cli.globusonline.org transfer --verify-checksum --encrypt --label=" + label + " --delete -s 3") 

	return

if __name__ == '__main__':

	gendpoint, uendpoint, username, path, dlocation, sshkey = arguments(sys.argv)
	activateEndpoints(gendpoint, uendpoint, username, sshkey)
	getFiles(gendpoint, uendpoint, username, path, dlocation, sshkey)
