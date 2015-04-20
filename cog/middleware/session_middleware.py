'''
Session-related middleware
'''

from datetime import datetime
from django.conf import settings
from cog.models import update_user_projects, update_user_tags, isUserRemote
from cog.views.utils import set_openid_cookie
from django.core.exceptions import ObjectDoesNotExist

class SessionMiddleware(object):
    
    def process_request(self, request):
        '''
        Method called before processing of the view.
        Used to periodically update the user's projects.
        '''
        
        # must not use shared anonymous session
        try:
            if request.user.is_authenticated() and request.user.profile.openid() is not None:
            
                s = request.session
                last_accessed_seconds = s.get('LAST_ACCESSED', 0) # defaults to Unix Epoch
                now_seconds = int(datetime.now().strftime("%s"))
                
                if now_seconds - last_accessed_seconds > settings.MY_PROJECTS_REFRESH_SECONDS:
                    
                    # update session stamp BEFORE querying remote sites
                    s['LAST_ACCESSED'] = now_seconds
                    s.save()
                                        
                    # update the user tags from their home site
                    if isUserRemote(request.user):
                        update_user_tags(request.user)
                        
                    # update the user's projects across the federation                
                    update_user_projects(request.user)

                    
        except ObjectDoesNotExist:
            pass # no profile
                
        # keep on processing this request
        return None