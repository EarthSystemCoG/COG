'''
Password-related middleware.
'''

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

EXEMPT_URLS = ['/password/update/', 'site_media', 'logout']

class PasswordMiddleware(object):
    
    def process_request(self, request):
        '''
        Method called before processing of the view.
        Used to check that the user password has not expired.
        '''
        
        if not any(url in request.path for url in EXEMPT_URLS):
            if request.user.is_authenticated() and request.user.profile.type==1 and request.user.profile.hasPasswordExpired():
                print 'Password for user %s has expired, forcing mandatory change.' % request.user
                
                return HttpResponseRedirect(reverse('password_update')+"?message=password_expired&next=%s" % request.path)
            
        # keep on processing this request
        return None

