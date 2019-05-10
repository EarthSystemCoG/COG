'''
Tests for ESGF openID authentication

@author: cinquini
'''
import os
import sys
import unittest
import urllib2

# list of openids from different ESGF IdPs
OPENIDS = ['https://pcmdi9.llnl.gov/esgf-idp/openid/lucacinquini',
           'https://esgf-node.ipsl.fr/esgf-idp/openid/luca4test',
           'https://esg-datanode.jpl.nasa.gov/esgf-idp/openid/lucacinquini',
           'https://hydra.fsl.noaa.gov/esgf-idp/openid/lucacinquini',
           'https://ceda.ac.uk/openid/Luca.Cinquini1',
           'https://esgf-data.dkrz.de/esgf-idp/openid/luca4test']

def importPycurl():
    import pycurl

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass

    def testEnv(self):
        '''Tests that the SSL_CERT_DIR environment is set.'''
        
        ssl_cert_dir = os.getenv('SSL_CERT_DIR', None)
        self.assertEqual(ssl_cert_dir, '/etc/grid-security/certificates', 'Must set environment SSL_CERT_DIR to /etc/grid-security/certificates')
        
    def testPythonVersion(self):
        '''Tests that the python installed version is 2.7.13.'''
        
        self.assertTrue('2.7.13' in sys.version, 'Must use Python version 2.7.13')
        
        
    def testNoPyCurl(self):
        '''Tests that pycurl is NOT installed.'''
        
        self.assertRaises(ImportError, importPycurl)

    def testValidOpenids(self):
        '''
        Tests that each openid is valid:
        - the IdP uses a trusted SSL certificate
        - the openid is registered at the IdP
        '''
        
        for openid in OPENIDS:
            try:
                response = urllib2.urlopen(openid)
                self.assertEqual(response.getcode(), 200, 'Invalid openid: %s' % openid)
            except Exception as e:
                raise e


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
