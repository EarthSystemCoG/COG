#!/usr/bin/env python
#===============================================================================
#                            remap.py
# 
# This is a driver python script for the RegridWeightGen application in ESMF
#===============================================================================

def remap(srcgrid, dstgrid, weights, method='bilinear'):

	import os
	import re
	import sys

        print 'remap: srcgrid=%s dstgrid=%s weights=%s method=%s' % (srcgrid, dstgrid, weights, method)

	# current running executable directory
	RUNDIR = os.getcwd()

	#TODO is this in the esmf.mk?
	# find out how many procs to use on this machine
	if os.environ.get('ESMF_NUM_PROCS'):
		NUM_PROCS = os.environ.get('ESMF_NUM_PROCS')
	else:
		print "ESMF_NUM_PROCS not defined in user environment, using default ESMF_NUM_PROCS=1"
		NUM_PROCS = "1"

	# read the esmf.mk and get the location of the executable and the OS for this system
	if os.environ.get('ESMFMKFILE'):
		esmfmkfile = open(os.environ.get('ESMFMKFILE'))
	else:
		print "ESMFMKFILE is not defined!"
		sys.exit

	for line in esmfmkfile:
		if re.search(".*ESMF_APPSDIR.*", line) != None:
			ap_match = line 

	esmfmkfile.close()

	# clean up the executable name string for proper usage
	ap_match = ap_match.split("=")[1]
	APP = ap_match.strip()+"/ESMF_RegridWeightGen"

	options = ''
	file = ''
	# methods
	if method == 'bilinear':
		options = ''
		file = 'b'
	elif method == 'patch':
		options = '-m patch'
		file = 'p'
	elif method == 'conserve':
		options = '-m conserve'
		file = 'c'
	else:
		print 'Method: '+method+' is not supported!'
		sys.exit

	#weights = weights.split('.')[0]
	#weights = weights+"_"+file+".nc"
#srcgrid = "/export/shared/grids/ll1deg_grid.nc"
#dstgrid = "/export/shared/grids/ll2.5deg_grid.nc"
#options = ""
#weights = "srcgrid_to_dstgrid_b.nc"

	return os.system("mpirun -np "+NUM_PROCS+" "+APP+" "+options+" -s "+srcgrid+" -d "+dstgrid+" -w "+weights+" > RegridWeightGen.out")
