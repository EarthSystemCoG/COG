'''
Main installation script for CoG application.
'''
from distutils.core import Command
import logging
logging.basicConfig(level=logging.INFO)

class CogSetupCommand(Command):
    '''Custom CoG install command to execute post-install configuration.'''
    
    description = "CoG configuration and installation command"
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
    
        # create/update cog_settings.cfg
        from config import CogConfig
        cogConfig = CogConfig()
        cogConfig.config()
        
        # use cog_settings.cfg to install/upgrade CoG database
        from install import CoGInstall
        cogInstall = CoGInstall()
        cogInstall.install()
    
    
if __name__ == '__main__':
    command = CogSetupCommand()
    command.run()