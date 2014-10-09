'''
Session-related middleware
'''

from datetime import datetime
from django.conf import settings
from cog.models import update_user_projects
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
                    
                    # update the user's projects across the federation                
                    update_user_projects(request.user)
                    
                    # refresh session stamp
                    s['LAST_ACCESSED'] = now_seconds
                    s.save()
        except ObjectDoesNotExist:
            pass # no profile
                
        # keep on processing this request
        return None


    '''
    def process_response(self, request, response):
        Method called before response is returned to the browser.
        Used to set the openid cookie if not set already.
        
        try:
            if request.user.is_authenticated() and request.user.profile.openid() is not None:
            
                # set openid cookie if not found already
                if request.COOKIES.get('openid', None) is None or len(request.COOKIES['openid'])==0:
                    set_openid_cookie(response, request.user.profile.openid())
                    
        except AttributeError:
            pass
                
        return response
    '''
