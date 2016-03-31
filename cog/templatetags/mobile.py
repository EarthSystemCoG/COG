from django import template
import user_agents
from django.contrib.sites.models import Site
from cog.models import Project, Post
from django.shortcuts import get_object_or_404

register = template.Library()


@register.filter(name='detect_mobile')
def detect_mobile(ua_string):
    # function to determine if a user is on a mobile device
    # uses the python library user agents (this had to be added to cog)
    user_agent = user_agents.parse(ua_string)
    return user_agent.is_mobile

    # setting this to true to emulate mobile device while developing
    #return True


@register.filter(name='stay_desktop')
def stay_desktop(request):
    # function to determine if a key has been added to the session in mobile_middleware
    # this key is added if the user comes in on a mobile device but wants to stay on the desktop version

    if 'VERSION' in request.session.keys():
        return True
    else:
        return False


@register.filter(name='mobile_string_present')
def mobile_string_present(query_string):
    # function to determine if the ?mobile query string is on the url
    # this query string is added with each page load inside the mobile version
    # if the query string is present the user stays in mobile mode
    if query_string == "mobile":
        return True


@register.filter(name='desktop_string_present')
def desktop_string_present(query_string):
    # function to determine if the ?mobile query string is on the url
    # this query string is added with each page load inside the mobile version
    # if the query string is present the user stays in mobile mode
    if query_string == "desktop":
        return True


@register.assignment_tag(name='get_project_list')
def get_project_list():
    # function to get a simple list of project urls to present in the mobile version project pull down
    project_list = Project.objects.filter(site=Site.objects.get_current()).order_by('short_name')
    return project_list


@register.filter(name='get_page_list')
def get_page_list(project_short_name):
    # function to get a simple list of wiki pages to present in the mobile version page pull down
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    page_list = Post.objects.filter(project=project).distinct().order_by('title')
    return page_list






