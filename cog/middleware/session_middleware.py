'''
Session-related middleware
'''

import threading
from datetime import datetime
from django.conf import settings
from cog.models import update_user_projects, update_user_tags, isUserRemote
from cog.views.utils import set_openid_cookie
from django.core.exceptions import ObjectDoesNotExist

class SessionMiddleware(object):
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_request(self, request):
        '''
        Method called before processing of the view.
        Used to periodically update the user's projects.
        '''
        
        # must not use shared anonymous session
        try:
            if request.user.is_authenticated and request.user.profile.openid() is not None:
            
                s = request.session
                last_accessed_seconds = s.get('LAST_ACCESSED', 0) # defaults to Unix Epoch
                now_seconds = int(datetime.now().strftime("%s"))
                
                if now_seconds - last_accessed_seconds > settings.MY_PROJECTS_REFRESH_SECONDS:
                    
                    # update session stamp BEFORE querying remote sites
                    s['LAST_ACCESSED'] = now_seconds
                    s.save()
                                        
                    # update the user status in a separate thread
                    t = threading.Thread(target=update_user, args=(request.user,))
                    t.start()
                    # don't wait for completion
                    
        except ObjectDoesNotExist:
            pass # no profile
                
        # keep on processing this request
        return None
    
def update_user(user):
    '''Function that updates the user status on the local site by querying all remote sites.
       This function is meant to be run as the target of a separate thread.'''
    
    # update the user tags from their home site
    if isUserRemote(user):
        update_user_tags(user)
        
    # update the user's projects across the federation                
    update_user_projects(user)

    
    