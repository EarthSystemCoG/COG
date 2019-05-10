'''
Main installation script for CoG application.
'''
from distutils.core import Command
import logging
import os

log = logging.getLogger(__name__)

class CogSetupCommand(Command):
    '''Custom CoG install command to execute post-install configuration.'''
    
    description = "CoG configuration and installation command"
    user_options = [ ('esgf=', None, 'Optional flag for ESGF configuration'), ]
    
    def initialize_options(self):
        self.esgf = 'False'
    
    def finalize_options(self):
        assert self.esgf in (None, 'True', 'true', 't', 'False', 'false', 'f'), "'esgf=' flag not specified"
        if self.esgf in ('True', 'true', 't'):
            self.esgf = True
        else:
            self.esgf = False
    
    def run(self):
        
        # 1) create/update cog_settings.cfg BEFORE Django is started
        log.debug('>>> 1) Executing CogConfig...')
        from config import CogConfig
        cogConfig = CogConfig(self.esgf)
        cogConfig.config()
        log.debug('<<< ...done with CogConfig')
        
        # 2) setup Django registry to initialize CoG application
        log.debug('>>> 2) Setting up Django applications registry')
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
        import django
        django.setup()
        log.debug('<<< ... done with django.setup()')
             
        # 3) use cog_settings.cfg to install/upgrade CoG database
        log.debug('>>> 3) Executing CoGInstall...')
        from install import CoGInstall
        cogInstall = CoGInstall()
        cogInstall.install()
        log.debug('<<< ...done with CoGInstall')
    
    
if __name__ == '__main__':
    command = CogSetupCommand()
    command.run()