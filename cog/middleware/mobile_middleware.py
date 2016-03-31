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
        #mobile = True

        print user_agent.is_mobile
        print ua_string

        if mobile:
            try:
                # when a user says "No Thanks" on the mobile question, a ?desktop query string is added to the url,
                # we then want to set something on the session that persists so the user is not asked the question
                # again until they start a new session
                if request.META['QUERY_STRING'] == "desktop":
                    request.session['VERSION'] = 'desktop'    # FIXME: we want to only do this once
                    request.session.save()
                else:
                    print 'No Query string', request.session.keys()

            except ObjectDoesNotExist:
                pass

            try:
                if request.META['QUERY_STRING'] == "mobile":
                    if 'VERSION' in request.session.keys():
                        del request.session['VERSION']

            except ObjectDoesNotExist:
                pass

        else:
            pass

        # keep on processing this request

        return None