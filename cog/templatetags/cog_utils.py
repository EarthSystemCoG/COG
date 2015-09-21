from cog.models import *
from cog.models.auth import userHasUserPermission, userHasContributorPermission, userHasAdminPermission, userHasProjectRole
from cog.models.utils import site_index, listPeople
from cog.views import encodeMembershipPar, NEW_MEMBERSHIP, OLD_MEMBERSHIP, NO_MEMBERSHIP
from cog.views import userCanPost, userCanView
from django import template
from django.core.urlresolvers import reverse
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
import re
from cog.utils import smart_truncate, INVALID_CHARS
from cog.models.utils import get_project_communication_means
from django.conf import settings
from cog.models.constants import DEFAULT_LOGO, FOOTER_LOGO, ROLES
from cog.models.navbar import NAVMAP, INVNAVMAP, TABS, TAB_LABELS
from cog.models.constants import DEFAULT_IMAGES
from cog.util.thumbnails import getThumbnailPath
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
import urlparse
import string
from cog.views.utils import getKnownIdentityProviders

register = template.Library()


@register.filter
def knownIdentityProviders(request):
    return getKnownIdentityProviders().items()


@register.filter
def concat(astring, bstring):
    return str(astring) + str(bstring)


@register.filter
def sortdict(the_dict):
    tuples = []
    for key, value in the_dict.iteritems():
        tuples.append((key, value))
    return sorted(tuples, key=lambda tuple: tuple[0])


@register.filter
def dictKeyLookup(the_dict, key):
    # Try to fetch from the dict, and if it's not found return an empty string.
    return the_dict.get(key, '')


# Utility function to set the "escape" function to be conditional_escape, or the identity function
# depending on the auto-escape context currently in effect in the template.
# conditional_escape does not escape instances of SafeData
def get_escape_function(autoescape):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    return esc


@register.filter
def index(project):
    return site_index(project)


@register.filter
def settings_value(key):
    """
    Custom filter to access a settings value in a template.
    :param key:
    :return:
    """
    return getattr(settings, key, '')


# filter to list the bookmarks folders for a user, project combination
@register.filter
def list_bookmarks(project, user, autoescape=None):

    folder = getTopFolder(project)

    esc = get_escape_function(autoescape)
    treeId = project.short_name + "_folderTree"

    html = "<div id='folder_tree' class='yui-skin-sam'>"
    html += "<div id='%s'>" % treeId

    # start recursion from this folder
    html += "<ul>"
    html += _folder_tree(folder, user, esc, expanded=True, icon='folder')  # expand this folder and its children
    html += "</ul>"

    html += "</div>"
    html += "</div>"

    # fire java-script event to initialize the tree object
    html += "<script>YAHOO.util.Event.onContentReady('%s', bookmarkTreeInit, this);</script>" % treeId

    # mark the result as safe from further escaping
    return mark_safe(html)

list_bookmarks.needs_autoescape = True


# recursive function to build the folder hierarchy tree for the current project and the project network (rollup)
def _folder_tree(folder, user, esc, expanded=False, icon='folder'):

    html = ""
    static_url = getattr(settings, "STATIC_URL", "static/")

    # always show the top-level folder and active folders
    if folder.name == TOP_FOLDER or folder.active:

        # this folder
        if expanded:
            html += "<li class='expanded'>"
        else:
            html += "<li>"
        html += "<div class='%s'>%s" % (icon, folder.name)  # changed to a div, better behaved than span

        # add edit/delete links, but not for pre-defined folders
        if not folder.isPredefined():
            deleteurl = reverse('folder_delete', args=[folder.project.short_name.lower(), folder.id])
            updateurl = reverse('folder_update', args=[folder.project.short_name.lower(), folder.id])
            if hasContributorPermission(user, folder.project):
                html += "&nbsp;&nbsp;[ <a href='" + updateurl + "' class='changelink'>Edit</a> | "
                html += "<a href='" + deleteurl + \
                        "' class='deletelink' onclick=\"return urlConfirmationDialog('Delete Folder Confirmation'," \
                        + "'Are you sure you want to delete this folder (including all the bookmarks and folders it " \
                          "contains)?', this)\">Delete</a> ]"
        html += "</div> "

        # this folder's children
        html += "<ul>"

        # display bookmarks
        project = folder.project
        bookmarks = folder.bookmark_set.all()

        # ensure that the bookmarks are returned in descending order of creation (or id).
        bookmarks_sorted = sorted(bookmarks, key=lambda _bookmark: _bookmark.id, reverse=True)
        for bookmark in bookmarks_sorted:
            deleteurl = reverse('bookmark_delete', args=[project.short_name.lower(), bookmark.id])
            updateurl = reverse('bookmark_update', args=[project.short_name.lower(), bookmark.id])
            html += "<li><span class='bookmark'>"
            html += "<a href='%s'>%s</a>" % (bookmark.url, bookmark.name)
            # display [Edit|Delete] links
            if hasContributorPermission(user, folder.project):
                html += "&nbsp;&nbsp;[ <a href='" + updateurl + "' class='changelink'>Edit</a> | "
                html += "<a href='" + deleteurl + \
                        "' class='deletelink' onclick=\"return urlConfirmationDialog('Delete Bookmark Confirmation'," \
                        "'Are you sure you want to delete this bookmark ?', this)\">Delete</a> ]"
            # display "Notes" link
            if bookmark.notes:
                html += "&nbsp;&nbsp;[ <img src='%scog/img/notes_16x16.png' style='vertical-align:bottom;' />" \
                        "<a href='%s'> Notes</a> ]" % (static_url, reverse('post_detail', args=[bookmark.notes.id]))
            if bookmark.description:
                html += "<br/>%s<br/>" % bookmark.description
            html += "</span></li>"

        # display sub-folders
        # predefined folders differently. If any child folders are digital (e.g. years), we want to sort
        #   its child folders in reverse order to keep the most recent folder on top.
        # closing upper-level child folders by default (e.g. folders under Presentations)

        years = reversed(range(2000, 2025))  # create list of reversed integers representing years
        years_str = [str(_year) for _year in years]  # convert that list to a list of strings

        if folder.name == "Bookmarks":
            # all first level folders, pre-defined or not are open by default and listed alphabetically
            # does not check for years. Folders with year names will be first in the list
            for child in folder.children().order_by('name'):  # sort folders alphabetically
                html += _folder_tree(child, user, esc, expanded=True)  # upper-level pre-defined folders open
        else:
            # loop thru all children of upper-level folders to check if any of them are years, if so set is_year to True
            is_year = False
            for child in folder.children():
                name = child.name.encode("utf-8")  # convert folder name fm unicode to string so it can be compared
                if any(_name == name for _name in years_str):
                    is_year = True
                # if any of the child folders are years, then reverse order them.
            if is_year:
                for child in folder.children().order_by('-name'):  # sort folders reverse alphabetically
                    html += _folder_tree(child, user, esc, expanded=False)  # child folder closed by default
            else:
                for child in folder.children().order_by('name'):
                    html += _folder_tree(child, user, esc, expanded=False)  # child folder closed by default

        html += "</ul>"
        html += "</li>"

    return html


# Filter to return a simple list of bookmark folders for a project, user combination
# The filter is composed of tuples of the form (folder object, folder hierarchy label)
@register.filter
def listFolders(project, user):
    #get the list of folders associated with a project
    folders = []
    _listSubfolders(getTopFolder(project), '', folders)

    #sort the folders alphabetically
    folders_sorted = sorted(folders, key=lambda folder_tuple: folder_tuple[0].name, reverse=True)
    return folders_sorted


def _listSubfolders(folder, hierarchy_label, folders):
    # add parent folder, append its name to hierarchy label
    hierarchy_label = "%s %s" % (hierarchy_label, folder.name)
    # truncate the folder hierarchy names to 100 characters
    folders.append((folder, smart_truncate(hierarchy_label, 100)))
    #folders.append( folder )
    # recursion over children
    for subFolder in folder.children():
        _listSubfolders(subFolder, "%s >" % hierarchy_label, folders)


# Filter that returns the top-level folder for a given project.
@register.filter
def getTopFolderForProject(project):
    return getTopFolder(project)


# recursive function to build the project hierarchy tree
def _project_tree(user, project, esc, expanded=False, dopeers=False, dochildren=False, icon='child'):

    if project.isNotVisible(user):
        return ""

    # this project
    #if icon=='this':
    #     html = "<li class='expanded' yuiConfig='{\"checked\":\"yes\"}'>"
    if expanded:
        html = "<li class='expanded'>"
    else:
        html = "<li>"
    html += "<span class='%s'><a href='%s'>%s</a></span>" % (icon, reverse('project_home',
                                                                           args=[project.short_name.lower()]),
                                                             esc(project.short_name))

    # this project's children
    if project.children and dochildren:
        html += "<ul>"
        for child in project.children():
                # recursion (do not expand children, do not retrieve their peers, do not retrieve their children)
                html += _project_tree(user, child, esc)
        html += "</ul>"
    html += "</li>"

    # this project's peers
    if dopeers and project.peers.all():
        for peer in project.peers.all():
                html += _project_tree(user, peer, esc, icon='peer')

    return html


# filter to determine whether a user is enrolled in a group
@register.filter
def isEnrolled(user, group):
    if group in user.groups.all():
        return True
    else:
        return False


# filter to determine whether a user belongs to a project
@register.filter
def hasUser(project, user):
    return project.hasUser(user)


# filter to determine whether a user is pending approval in a project
@register.filter
def hasUserPending(project, user):
    return project.hasUserPending(user)


# filters to encode a membership HTTP parameter
@register.filter
def newMembership(group, user):
    return encodeMembershipPar(NEW_MEMBERSHIP, group.name, user.id)


@register.filter
def oldMembership(group, user):
    return encodeMembershipPar(OLD_MEMBERSHIP, group.name, user.id)


@register.filter
def noMembership(group, user):
    return encodeMembershipPar(NO_MEMBERSHIP, group.name, user.id)


@register.filter
def hasUserPermission(user, project):
    return userHasUserPermission(user, project)

@register.filter
def hasContributorPermission(user, project):
    return userHasContributorPermission(user, project)

@register.filter
def hasAdminPermission(user, project):
    return userHasAdminPermission(user, project)


@register.filter
def canPost(user, post):
    return userCanPost(user, post)


@register.filter
def relatedPostCount(post, related_posts):
    count = len(related_posts)
    if post.parent:
        count += 1
    return count


@register.filter
# function to sort Child Pages alphabetically by title
def relatedPostSorted(post, related_posts):
    sorted_posts = sorted(related_posts, key=lambda x: x.title, reverse=False)
    return sorted_posts


@register.filter
def numberOptions(lastNumber, selectedNumber):
    lastNumberPlusOne = int(lastNumber)
    selectedNumber = int(selectedNumber)
    html = ""
    for n in range(1, lastNumber + 1):
        html += "<option value='%d'" % n
        if n == selectedNumber:
            html += "selected='selected'"
        html += ">%d</option>" % n
    # mark the result as safe from further escaping
    return mark_safe(html)


def getTopTabUrl(project, request):
    """
    Returns the full URL of the top tab for the current request.
    Example: request.path = "/projects/cog/aboutus/mission/" --> "/projects/cog/aboutus/".
    """

    # "/projects/cog/"
    homeurl = project.home_page_url()

    # requested URL start with project base URL
    if homeurl in request.path:
        # request.path = "/projects/cog/aboutus/mission/" or "/projects/cog/nav/aboutus/update/"
        # subtaburl = "aboutus/mission/"
        subtaburl = request.path[len(homeurl):]
        # disregard everything after the first '/'
        subtaburl = subtaburl[0:subtaburl.find('/')+1]
        # taburl = "/projects/cog/" + "aboutus/"
        if subtaburl in INVNAVMAP:
            taburl = homeurl + INVNAVMAP[subtaburl]
            #print "subtaburl=%s" % subtaburl
            #print "taburl=%s" % taburl
            return taburl
    # default: no tab selected
    return None


# Utility method to return a list of ACTIVE project tabs (top-tabs and sub-tabs).
# Returns a list of list: [ [(tab1,False)], [(tab2,False)], [(tab3,True), (sub-tab3a,False), (subtab3b,True), (
# subtab3c,False),...], [(tab4,True)], [(tab5,True)], ...] where sub-tabs are returned only for the currently selected
# top-tab, and each 3-tuple has the form: (tab label, tab url, selected)
@register.filter
def getTopNav(project, request):

    taburl = getTopTabUrl(project, request)

    tabs = []
    ptabs = get_or_create_project_tabs(project, save=True)
    # project tabs have full URLs:
    # (u'Contact Us', u'/projects/cog/contactus/')
    # (u'Mission', u'/projects/cog/aboutus/mission/')
    # .....
    for ptablist in ptabs:
        tablist = []
        selected = False
        for idx, ptab in enumerate(ptablist):
            label = ptab.label
            # top-tab
            if idx == 0:
                # change label name
                if 'Home' in label:    # remove project short name from 'Home' tab
                    label = 'Home'
                if ptab.active:
                    if str(ptab.url) == taburl:
                        selected = True
                    tablist.append((label, ptab.url, selected))
            # sub-tab
            else:
                if selected and ptab.active:
                    _selected = False
                    if request.path == ptab.url:
                        _selected = True
                    tablist.append((label, ptab.url, _selected))

        tabs.append(tablist)
    return tabs


@register.filter
def getTopTabStyle(tablist, selected):
    """Method to return the top-tab CSS style, depending on whether it is selected, and it has sub-tabs."""

    if selected:
        if len(tablist) > 1:
            return mark_safe("style='color:#358C92; background-color: #B9E0E3'")
        else:
            return mark_safe("style='color:#358C92; background-color: #FFFFFF'")
    else:
        return ""


@register.filter
def getSubTabStyle(tablist, tab):
    """ Method to return the sub-tab CSS style depending on whether it is selected.
        tablist: full list of tuples (label, url, selected) for current top tab
        tab: current subtab
    """
    toptab = tablist[0]
    # top-tab selected
    if toptab[2]:
        # sub-tab selected
        if tab[2]:
            #return mark_safe("style='color:#358C92; background-color: #FFFFFF''")
            #return mark_safe("style='color:#358C92; text-decoration: underline;'")
            return mark_safe("style='color:#358C92;'")
        # sub-tab not selected
        else:
            return mark_safe("style='color:#358C92;'")
    else:
        return ""


# Utility method to return the list of invalid characters
@register.filter
def getInvalidCharacters(project):
    return "!@#$%^&*[]/{}|\"\\<>"
    # remove leading [ and trailing \]
    #return INVALID_CHARS[1:len(INVALID_CHARS)-1]


# filter that inserts a lock icon if the user can not view the URL
@register.filter
def is_locked(post, request, autoescape=None):

    # show lock depending on user authentication status and permissions
    #if userCanView(request.user, post):
    #    html = ""
    #else:
    #    html = "&nbsp;<span class='privatelink'>&nbsp;</span>"

    # show lock depending on page properties
    html = ""
    if post.is_private:
        html += "&nbsp;<span class='privatelink'>&nbsp;</span>"
    #if post.is_restricted:
    #    html += "&nbsp;<span class='restrictedlink'>&nbsp;</span>"

    # mark the result as safe from further escaping
    return mark_safe(html)


@register.filter
def get_form_global_errors(form):
    errors = dict(form.errors)
    return list(errors.get("__all__", []))


@register.filter
def get_organizational_roles(project, category):

    return getOrganizationalRoles(project, category)


@register.filter
def get_management_bodies(project, category):

    return getManagementBodies(project, category)


@register.filter
def is_home_page(request, project):

    if project.home_page_url() == request.path:
        return True
    else:
        return False


@register.filter
def get_external_urls(project, external_url_type):
    return project.get_external_urls(external_url_type)


@register.filter
def roles(user, project):
    """
    Lists the roles of a user in a project.
    """

    roles = []
    for role in ROLES:
        if userHasProjectRole(user, project, role):
            roles.append(role)

    return roles


@register.filter
def getUserAttribute(user, attribute):
    """
    Utility to look for a named attribute in the User/Collaborator object first,
    or in the UserProfile object if not found.
    """
    try:
        return getattr(user, attribute)
    except AttributeError:
        profile = UserProfile.objects.get(user=user)
        return getattr(profile, attribute)


@register.filter
def tabs(label):
    return TABS[label]


@register.filter
def getTabLabel(tabkey):
    """
    Transforms "download/" into "tab_Download
    :param tabkey:
    :return:
    """
    tabkey = tabkey[0:-1]
    return "tab_%s" % TAB_LABELS[tabkey]


def parseBoolString(theString):
    return theString[0].upper() == 'T'


@register.filter
def getCommunicationMeans(project, internal):
    return get_project_communication_means(project, parseBoolString(internal))


@register.filter
def getPeople(project):
    return listPeople(project)


@register.filter
def getImage(obj):

    try:
        # AnonymousUser
        if isinstance(obj, AnonymousUser):
            return getattr(settings, "STATIC_URL") + DEFAULT_IMAGES['User']

        # User
        elif isinstance(obj, User):
            profile = UserProfile.objects.get(user=obj)
            return profile.image.url

        # Collaborator
        elif isinstance(obj, Collaborator):
            return obj.image.url

        elif isinstance(obj, Organization) or isinstance(obj, FundingSource):
            return obj.image.url

    except (ValueError, ObjectDoesNotExist) as e:
        # if the image field has no associated file -> return default (no image found)
        return getattr(settings, "STATIC_URL") + DEFAULT_IMAGES['%s' % obj.__class__.__name__]


@register.filter
def getThumbnailById(id, type):

    if id is not None:
        if type == 'Collaborator':
            obj = Collaborator.objects.get(pk=id)
        elif type == 'Organization':
            obj = Organization.objects.get(pk=id)
        elif type == 'FundingSource':
            obj = FundingSource.objects.get(pk=id)
        return getThumbnail(obj)

    else:
        imagepath = getattr(settings, "STATIC_URL") + DEFAULT_IMAGES[type]
        return getThumbnailPath(imagepath)


@register.filter
def getThumbnail(user):

    imagePath = getImage(user)
    thumbnailPath = getThumbnailPath(imagePath)
    print thumbnailPath
    return thumbnailPath


@register.filter
def doc_redirect(doc):

    if len(doc.post_set.all()) > 0:
        for doc in doc.post_set.all():
            redirect = reverse('post_detail', kwargs={'post_id': doc.id})
    else:
        redirect = reverse('project_home', kwargs={'project_short_name': doc.project.short_name.lower()})
    return redirect


@register.filter
def partners(project):
    organizations = list(project.organization_set.all())
    return sorted(organizations, key=lambda org: org.name)


@register.filter
def sponsors(project):
    fundingsources = list(project.fundingsource_set.all())
    return sorted(fundingsources, key=lambda fs: fs.name)


@register.filter
# filter that builds the content for the Javascript projectTags array
# This is tags across ALL projects. Used in the tag pulldown in the Project Browser
def projectTags(project):

    tags = ProjectTag.objects.all()
    tagstring = ''
    for tag in tags:
        tagstring += '\"'+tag.name+'\",'
    return mark_safe(tagstring[0:-1])  # important: no escaping!


@register.filter
# filter to list projects below the Project Browser in alphabetical order regardless of case
def list_project_tags(project):

    tags_sorted = sorted(project.tags.all(), key=lambda _tag: _tag.name.lower())
    return tags_sorted


@register.filter
def projectNews(project):
    return news(project)


@register.filter
def dataCartContains(user, item_identifier):

    (datacart, _) = DataCart.objects.get_or_create(user=user)
    return datacart.contains(item_identifier)


@register.filter
def showMessage(message):
    """
    Utility filter to translate message code into message strings.
    """

    if message == 'password_reset':
        return 'A new password has been e-mailed to you. ' \
               'Please use the new password to login and change it as soon as possible.'

    elif message == 'user_add':
        return 'Thank you for creating an account. You can now login.'

    elif message == 'password_update':
        return 'Your password has been changed. Please login again.'
    
    elif message == 'password_updated_by_admin':
        return 'The user password has been updated.'

    elif message == 'user_reminder':
        return 'Your UserName and OpenID have been emailed to the address you provided.' \
               '<br/>Please check your email box.'

    elif message == 'incomplete_profile':
        return 'Please update your profile to contain at least the mandatory information required by COG ' \
               '(the fields in bold).'

    elif message == 'invalid_idp':
        return 'Invalid Identity Provider (not trusted).'

    elif message == 'invalid_openid':
        return "Invalid OpenID (does it start with 'https' ?)"

    elif message == 'openid_discovery_error':
        return "OpenID Discovery Error: unrecognized by the Identity Provider."

    elif message == "login_failed":
        return "Error entering username and/or password."

    elif message == "password_expired":
        return "Your password has expired. Please choose a new password conforming to the requirements below."

    else:
        raise Exception("Invalid message")


@register.filter
def is_error_msg(message):
    words = ["Invalid", "Error"]
    for word in words:
        if word in message:
            return True


@register.filter
def isValidUser(user):
    return isUserValid(user)


@register.filter
def isLocal(user):
    return isUserLocal(user)


@register.filter
def isRemote(user):
    return isUserRemote(user)


@register.filter
def get_domain(url):
    """
    Returns the domain part of a URL
    """
    
    return urlparse.urlparse(url)[1]

@register.filter
def get_target_url_with_next_url(request, target_url_name):
    '''Returns a named target URL with the 'next' parameter set to the current page URL.'''
    
    # <a href="{% url 'login' %}?next={{ request.build_absolute_uri }}"> Login</a>
    target_url = reverse(target_url_name)
    
    # current page full URL
    current_url =  request.build_absolute_uri()
    
    # keep the same 'next' URL, don't keep adding
    if '?next=' in current_url:
        next_url = current_url.split("?next=")[1]
    # return to current page, with optional query parameters
    else:
        next_url = current_url
    
    return "%s?next=%s" % (target_url, next_url)

@register.filter
def get_openid(request):
    """
    Retrieves the user openid from either the request query string,
    or the request cookies.
    """
    
    if request.REQUEST.get('openid', None):
        return request.REQUEST['openid']
    elif request.COOKIES.get('openid', None):
        return request.COOKIES['openid']
    else:
        return ''


@register.filter
def delete_from_session(session, key):
    """
    Deletes a named key from the user HTTP session.
    """
    
    if session.get(key, None):
        del session[key]
        session.save()
        
@register.filter
def get_peer_sites(project):
    """
    Returns a list of ENABLED peer sites, ordered alphabetically by name.
    """
    
    return getPeerSites()