'''
Main installation script for CoG application.
'''

import logging
logging.basicConfig(level=logging.INFO)
    
def main():
    
    # create/update cog_settings.cfg
    from config import CogConfig
    cogConfig = CogConfig()
    cogConfig.config()
    
    # use cog_settings.cfg to install/upgrade CoG database
    from install import CoGInstall
    cogInstall = CoGInstall()
    cogInstall.install()
    
    
if __name__ == '__main__':
    main()