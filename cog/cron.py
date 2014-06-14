'''
Module containing COG cron tasks.
'''

import kronos
import datetime
from cog.project_manager import projectManager
import logging
from django.conf import settings

    
@kronos.register(settings.TASK_SYNC_PROJECTS)
def syncProjects():
    
    sites = projectManager.sync()
    logging.debug('Kronos syncProjects: time=%s synchronized projects from sites=%s' % (datetime.datetime.now(), sites))
    
    
