from django.core.exceptions import ObjectDoesNotExist
import user_agents
from django.contrib.sessions.backends.file import SessionStore
from uuid import uuid4

class MobileMiddleware(object):

    def process_request(self, request):
        """
        Method called before processing of the view.
        Used to check if a user on a mobile device want to stay mobile
        """
        ua_string = request.META['HTTP_USER_AGENT']
        user_agent = user_agents.parse(ua_string)
        mobile = user_agent.is_mobile
        mobile = True
        print '****************** in MobileMiddleware ********************'

        #request.session['VERSION'] = 'desktop'  # add only adds if it does not exist already

        if mobile:
            try:
                if request.META['QUERY_STRING'] == "desktop":
                    request.session['VERSION'] = 'desktop'    # FIXME: we want to only do this once
                    request.session.save()

            except ObjectDoesNotExist:
                pass

        else:
            pass

        # keep on processing this request

        return None