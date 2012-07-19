import os

def remap(srcgrid, dstgrid, weights, method=""):
    command = 'cat %s %s > %s' % (srcgrid, dstgrid, weights)
    print 'command= %s ' % command
    status = os.system(command)
    return status