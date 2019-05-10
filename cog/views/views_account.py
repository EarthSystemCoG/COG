import urllib
from urlparse import urlparse

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import is_password_usable
from django.contrib.auth.views import login
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseServerError
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django_openid_auth.models import UserOpenID
from django_openid_auth.views import login_complete

from cog.forms.forms_account import *
from cog.models import *
from cog.notification import notify, sendEmail
from cog.plugins.esgf.security import esgfDatabaseManager
from cog.util.thumbnails import *
from cog.views.utils import set_openid_cookie, get_all_shared_user_info
from django.http.response import HttpResponseForbidden

#FIXME:  note: must import this module last otherwise it conflicts with previous import datetime.datetime
import datetime

import logging

log = logging.getLogger()

def redirectToIdp():
    if settings.IDP_REDIRECT is not None and len(settings.IDP_REDIRECT.strip()) > 0:
        return True
    else:
        return False


def custom_login(request, **kwargs):
    """
    Overrides standard login view that checks whether the authenticated user has any missing information.
    :param request:
    :param kwargs:
    :return:
    """
    
    # authenticate user via standard login
    response = login(request, **kwargs)

    # check if user is valid
    return _custom_login(request, response)


def custom_login_complete(request, **kwargs):
    """
    Method invoked after successful OpenID login.
    Overridden to create user profile after first successful OpenID login.
    """
    
    # authenticate user
    response = login_complete(request, **kwargs)

    # create a stub profile with blank mandatory fields
    if not request.user.is_anonymous():
        openid = request.GET.get('openid.claimed_id', None)
        try:
            request.user.profile
            
        except ObjectDoesNotExist:

            log.debug('Discovering site for user with openid=%s' % openid)
            
            # retrieve user home node
            site = discoverSiteForUser(openid)
            if site is None: 
                # set user home node to current node
                site = Site.objects.get_current()
                
            log.debug('User site=%s... creating user profile...' % site)
                
            # create new ESGF/OpenID login, type=2: ESGF
            UserProfile.objects.create(user=request.user, institution='', city='', country='', type=2, site=site)
            
            # create user datacart
            DataCart.objects.create(user=request.user)
            
            # set openid cookie
            set_openid_cookie(response, openid)

    # check if user is valid
    return _custom_login(request, response)


def _custom_login(request, response):
    
    # successful login
    if not request.user.is_anonymous():
                
        # missing information
        if isUserLocal(request.user) and not isUserValid(request.user):
            log.debug('User is local but some information is missing, redirecting to user update page')
            return HttpResponseRedirect(reverse('user_update', kwargs={'user_id': request.user.id}) +
                                        "?message=incomplete_profile")
        
    return response


def notifyAdminsOfUserRegistration(user,request):

    subject = "New User Registration"

    profile_url = reverse('user_profile_redirect', kwargs={'user_id': user.id})  # go to the right node
    profile_url = request.build_absolute_uri(profile_url)

    message = "User %s has created a new account." % user.get_full_name()
    message += "\nView home node profile at: %s" % profile_url

    # openid
    message += "\n\nOpenID is: %s" % user.profile.openid()

    # user attributes
    message += "\n\nFirst Name: %s" % user.first_name
    message += "\nLast Name: %s" % user.last_name
    message += "\nUser Name: %s" % user.username
    message += "\nEmail: %s" % user.email

    # user profile attributes
    profile = UserProfile.objects.get(user=user)
    message += "\n\nInstitution: %s" % profile.institution
    message += "\nDepartment: %s" % profile.department
    message += "\nCity: %s" % profile.city
    message += "\nState: %s" % profile.state
    message += "\nCountry: %s" % profile.country
    message += "\nSubscribe to COG email list? %s" % profile.subscribed
    message += "\nResearch Interests: %s" % profile.researchInterests
    message += "\nResearch Keywords: %s" % profile.researchKeywords

    for admin in getSiteAdministrators():
        notify(admin, subject, message)


def notifyUserOfRegistration(user):
    
    subject = "CoG Account Creation"
    message = "Thank you for creating a new ESGF-CoG account."
    message += "\n"
    message += "\nYour User Name is: %s" % user.username
    message += "\nYour OpenID is: %s" % user.profile.openid()
    message += "\n"
    message += "\nPlease note that you will need your OpenID to login."
    message += "\n"
    message += "\nCoG Tutorials: https://www.earthsystemcog.org/projects/cog/tutorials_web"
    message += "\n"
    message += "\nCoG Support: cog_support@list.woc.noaa.gov"

    notify(user, subject, message)


def subscribeUserToMailingList(user, request):
    """
    Method to subscribe a user to the CoG mailing list.
    User will receive a confirmation email.
    """

    _sendSubsriptionEmail(user, 'subscribe')

def unSubscribeUserToMailingList(user, request):
    """
    Method to unsubscribe a user to the CoG mailing list.
    User will receive a confirmation email.
    """

    _sendSubsriptionEmail(user, 'unsubscribe')

def _sendSubsriptionEmail(user, action):
    '''Common functionality to send email to the CoG mailing list.'''
    
    # cog-info-request@list.woc.noaa.gov
    toAddress = settings.COG_MAILING_LIST.replace('@','-request@')
    # subscribe address=<email address>
    subject = '%s address=%s' % (action, user.email)
    # body
    message = ''
    
    log.debug('Sending subscription email: To=%s Subject=%s' % (toAddress, subject))
    sendEmail(toAddress, subject, message, fromAddress=user.email)


# view to create a user account
def user_add(request):
    
    # redirection URL
    _next = request.GET.get('next', None) or request.POST.get('next', None)
    
    # redirect to another node if necessary
    if redirectToIdp():
        redirect_url = settings.IDP_REDIRECT + request.path
        if _next is not None:
            redirect_url += ("?next=%s" % urllib.quote_plus(_next))
        log.debug('Redirecting account creation to: %s' % redirect_url)
        return HttpResponseRedirect(redirect_url)

    # create URLs formset
    UserUrlFormsetFactory = modelformset_factory(UserUrl, form=UserUrlForm, exclude=('profile',), 
                                                 can_delete=True, extra=2)
            
    if request.method == 'GET':

        form = UserForm(initial={'next': _next})  # initialize form with redirect URL
        formset = UserUrlFormsetFactory(queryset=UserUrl.objects.none(), prefix='url')           # empty formset

        return render_user_form(request, form, formset, title='Create User Profile')

    else:
        # form with bounded data
        form = UserForm(request.POST, request.FILES,)
        # formset with bounded data
        formset = UserUrlFormsetFactory(request.POST, queryset=UserUrl.objects.none(), prefix='url')

        if form.is_valid() and formset.is_valid():

            # create a user from the form but don't save it to the database yet because the password is not encoded yet
            user = form.save(commit=False)
            
            # must reset the password through the special method that encodes it correctly
            clearTextPwd = form.cleaned_data['password']
            user.set_password(clearTextPwd)
                        
            # save user to database
            user.save()
            log.debug('Created user=%s' % user.username)
            
            # create openid
            if settings.ESGF_CONFIG:
                openid = form.cleaned_data['openid']
                log.debug('Creating openid=%s' % openid)
                userOpenID = UserOpenID.objects.create(user=user, claimed_id=openid, display_id=openid)
                log.debug('Added openid=%s for user=%s into COG database' % (openid, user.username))

            # use additional form fields to create user profile
            userp = UserProfile(user=user,
                                institution=form.cleaned_data['institution'],
                                city=form.cleaned_data['city'],
                                state=form.cleaned_data['state'],
                                country=form.cleaned_data['country'],
                                department=form.cleaned_data['department'],
                                researchKeywords=form.cleaned_data['researchKeywords'],
                                researchInterests=form.cleaned_data['researchInterests'],
                                subscribed=form.cleaned_data['subscribed'],
                                private=form.cleaned_data['private'],
                                image=form.cleaned_data['image'],
                                last_password_update=datetime.datetime.now())

            
            # save user profile --> will trigger userProfile post_save
            userp.save()
            
            # NOTE: this field is NOT persisted in the CoG database but it is used by insertEsgfUser() below
            userp.clearTextPwd = clearTextPwd  
            # insert into ESGF database
            if settings.ESGF_CONFIG:
                esgfDatabaseManager.insertEsgfUser(userp)

            # create user data cart
            datacart = DataCart(user=user)
            datacart.save()

            # must assign URL to this user
            urls = formset.save(commit=False)
            for url in urls:
                url.profile = userp
                url.save()

            # generate thumbnail image
            if userp.image is not None:
                try:
                    generateThumbnail(userp.image.path, THUMBNAIL_SIZE_SMALL)
                except ValueError:
                    pass  # image does not exist, ignore

            # notify user, node administrators of new registration
            notifyUserOfRegistration(user)
            notifyAdminsOfUserRegistration(user,request)

            # subscribe to mailing list ?
            if userp.subscribed:
                subscribeUserToMailingList(user, request)

            # redirect to login page with special message
            login_url = reverse('login')+"?message=user_add"
            if _next is not None and len(_next.strip()) > 0:
                login_url += ("&next=%s" % urllib.quote_plus(_next))
                # redirect to absolute URL (possibly at an another node)
                if 'http' in _next:
                    url = urlparse(_next)
                    login_url = '%s://%s%s' % (url.scheme, url.netloc, login_url)
            # append openid to initial login_url
            if userp.openid() is not None:
                login_url += "&openid=%s" % urllib.quote_plus(userp.openid())
            login_url += "&username=%s" % urllib.quote_plus(userp.user.username)
            
            response = HttpResponseRedirect(login_url)
            
            # set openid cookie on this host
            set_openid_cookie(response, userp.openid())

            log.debug('New user account created: redirecting to login url: %s' % login_url)
            return response

        else:
            if not form.is_valid():
                log.debug("Form is invalid: %s" % form.errors)
            elif not formset.is_valid():
                log.debug("URL formset is invalid: %s" % formset.errors)
            return render_user_form(request, form, formset, title='Create User Profile')


# view to display user data
# require login to limit exposure of user information
#@login_required
def user_detail(request, user_id):

    # load User object
    user = get_object_or_404(User, pk=user_id)
    # try loading user profile
    try:
        user_profile = UserProfile.objects.get(user=user)
    # create user profile if not existing already
    except:
        user_profile = UserProfile(user=user)
        user_profile.save()
        log.debug("Created empty profile for user=%s" % user)
        
    # retrieve map of (project, roles) for this user
    (projTuples, groupTuples) = get_all_shared_user_info(user)
    log.debug("projTuples=%s" % str(projTuples))
        
    # sort projects, groups alphabetically
    projects = sorted(projTuples, key=lambda x: x[0].short_name)
    groups = sorted(groupTuples, key=lambda x: x[0])
            
    return render(request, 'cog/account/user_detail.html',
                  {'user_profile': user_profile, 'projects': projects, 'groups':groups, 'title': 'User Profile'})


# view to redirect to the user profile on the local or remote node
# this view is always invoked with the *local* user 'id'
def user_profile_redirect(request, user_id):
    
    if request.method == 'GET':
        
        # load User object
        user = get_object_or_404(User, pk=user_id)
        
        if isUserRemote(user):
            return HttpResponseRedirect(user.profile.getAbsoluteUrl())
                                         
        else:
            return HttpResponseRedirect(reverse('user_detail', kwargs={'user_id': user.id}))

    else:
        return HttpResponseNotAllowed(['GET'])


# view to look up a *local* user by OpenID
# this view does NOT redirect to other peer nodes
# (user_profile_redirect does that)
def user_byopenid(request):
    
    if request.method == 'GET':
    
        openid = request.GET['openid']
        
        # load User object
        userOpenid = get_object_or_404(UserOpenID, claimed_id=openid)
        
        # redirect to user profile page on local node
        return HttpResponseRedirect(reverse('user_detail', kwargs={'user_id': userOpenid.user.id}))
            
    else:
        return HttpResponseNotAllowed(['GET'])
    
# view to retrieve the image of a local user, identified by openid
# optionally, the image thumbnail can be retrieved instead
def user_image(request):
    
    if request.method == 'GET':
    
        openid = request.GET['openid']
        thumbnail = request.GET.get('thumbnail', False)
        
        # default image
        imagePath = getattr(settings, "STATIC_URL") + DEFAULT_IMAGES['User']
        
        # load User object
        try:
            userOpenid = UserOpenID.objects.get(claimed_id=openid)
            
            # load user image
            userProfile = UserProfile.objects.get(user=userOpenid.user)
            imagePath = userProfile.image.url
                    
        except (ValueError, ObjectDoesNotExist) as e:
            pass # use default image
            
        # return thumbnail
        if thumbnail:
            
            thumbnailPath = getThumbnailPath(imagePath, mustExist=True)
            return HttpResponseRedirect( thumbnailPath )
        
        # return full image
        else:
            return HttpResponseRedirect( imagePath )        

    else:
        return HttpResponseNotAllowed(['GET'])

@user_passes_test(lambda u: u.is_staff)
def user_delete(request, user_id):
    
    # get user
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'GET':
        return render(request, 
                      'cog/account/user_delete.html', 
                      {'user': user, 'title': 'Delete User'} )
    else:
        
        # delete ESGF user and all related objects
        if settings.ESGF_CONFIG:
            esgfDatabaseManager.deleteUser(user)

        # delete CoG user and all related objects
        user.delete()
                
        # redirect to user listings
        return HttpResponseRedirect(reverse('admin_users'))


@login_required
def user_update(request, user_id):

    # security check
    if str(request.user.id) != user_id and not request.user.is_staff:
        raise Exception("User not authorized to change profile data")

    # get user
    user = get_object_or_404(User, pk=user_id)
    profile = get_object_or_404(UserProfile, user=user)

    # create URLs formset
    UserUrlFormsetFactory = modelformset_factory(UserUrl, form=UserUrlForm, exclude=('profile',), 
                                                 can_delete=True, extra=2)

    if request.method == 'GET':

        # pre-populate form, including value of extra field 'confirm_password'
        form = UserForm(instance=user, initial={'confirm_password': user.password,
                                                'institution': profile.institution,
                                                'city': profile.city,
                                                'state': profile.state,
                                                'country': profile.country,
                                                'department': profile.department,
                                                'researchKeywords': profile.researchKeywords,
                                                'researchInterests': profile.researchInterests,
                                                'subscribed': profile.subscribed,
                                                'private': profile.private,
                                                'image': profile.image,
                                                'type': profile.type})

        # retrieve existing URLs and OpenIDs associated to this user
        formset = UserUrlFormsetFactory(queryset=UserUrl.objects.filter(profile=profile), prefix='url')

        return render_user_form(request, form, formset, title='Update User Profile')

    else:
        # form with bounded data
        form = UserForm(request.POST, request.FILES, instance=user)
        
        # formset with bounded data
        formset = UserUrlFormsetFactory(request.POST, queryset=UserUrl.objects.filter(profile=profile), prefix='url')

        if form.is_valid():
            
            # delete UserUrls if found
            urls = UserUrl.objects.filter(profile=profile)
            for url in urls:
                log.debug('Deleting user URL: %s' % url.url)
                url.delete()

            # update user
            user = form.save()

            # old user profile
            user_profile = get_object_or_404(UserProfile, user=user)
            
            # capture user profile status before it is updated
            oldValidFlag = isUserValid(user)
            oldSubscribed = user_profile.subscribed
            
            # new user profile
            user_profile.institution = form.cleaned_data['institution']
            user_profile.city = form.cleaned_data['city']
            user_profile.state = form.cleaned_data['state']
            user_profile.country = form.cleaned_data['country']
            user_profile.department = form.cleaned_data['department']
            user_profile.researchKeywords = form.cleaned_data['researchKeywords']
            user_profile.researchInterests = form.cleaned_data['researchInterests']
            user_profile.subscribed = form.cleaned_data['subscribed']
            user_profile.private = form.cleaned_data['private']

            # check if the password is encoded already
            # if not, encode the password that the user provided in clear text
            if not is_password_usable(user.password):
                user.set_password(form.cleaned_data['password'])
                user.save()
                log.debug('Reset password for user=%s' % user)

            # image management
            _generateThumbnail = False
            if form.cleaned_data.get('delete_image'):
                deleteImageAndThumbnail(user_profile)

            elif form.cleaned_data['image'] is not None:
                # delete previous image
                try:
                    deleteImageAndThumbnail(user_profile)
                except ValueError:
                    # image not existing, ignore
                    pass

                user_profile.image = form.cleaned_data['image']
                _generateThumbnail = True

            # persist changes
            user_profile.save()

            # must assign URL to this user
            #urls = formset.save(commit=False)
            #for url in urls:
            #    url.profile = profile
            #    url.save()

            #for obj in formset.deleted_objects:
            #    obj.delete()

            # generate thumbnail - after picture has been saved
            if _generateThumbnail:
                generateThumbnail(user_profile.image.path, THUMBNAIL_SIZE_SMALL)

            # subscribe/unsubscribe user if mailing list selection changed
            if oldSubscribed and form.cleaned_data['subscribed'] == False:
                if oldValidFlag:  # send email only for non-new users
                    unSubscribeUserToMailingList(user, request)
                    
            elif oldSubscribed == False and form.cleaned_data['subscribed']:
                subscribeUserToMailingList(user, request)

            # update ESGF user object in ESGF database
            if settings.ESGF_CONFIG:
                esgfDatabaseManager.updateUser(user_profile)

            # redirect user profile page
            response = HttpResponseRedirect(reverse('user_detail', kwargs={'user_id': user.id}))
            
            # set openid cookie to first available openid
            set_openid_cookie(response, user.profile.openid())

            return response

        else:
            if not form.is_valid():
                log.debug("Form is invalid: %s" % form.errors)
            elif not formset.is_valid():
                log.debug("URL formset is invalid: %s" % formset.errors)
                
            return render_user_form(request, form, formset, title='Update User Profile')


@login_required
def password_update(request, user_id):
    """
    View used by the user (or by a node administrator) to change their password.
    """

    # redirect to another node if necessary
    if redirectToIdp():
        return HttpResponseRedirect(settings.IDP_REDIRECT + request.path)

    # check permission: user that owns the account, or a node administrator
    user = get_object_or_404(User, id=user_id)
    if user != request.user and not request.user.is_staff:
        return HttpResponseServerError("You don't have permission to change the password for this user.")

    # check use has OpenID issued by this node
    if user.profile.localOpenid() is None:
        return HttpResponseForbidden("Non local user: password must be changed at the node that issued the OpenID.")

    if request.method == 'GET':
                
        # create form (pre-fill username)
        initial = {'username': user.username,            # the target user
                   'requestor': request.user.username}  # the user requesting the change
        form = PasswordChangeForm(initial=initial)
        return render_password_change_form(request, form, user.username)

    else:
        form = PasswordChangeForm(request.POST)

        if form.is_valid():
            
            #user = User.objects.get(username=form.cleaned_data.get('username'))

            # change password in database
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            user.profile.last_password_update = datetime.datetime.now()
            user.profile.save()
            
            # update ESGF user object
            if settings.ESGF_CONFIG:
                esgfDatabaseManager.updatePassword(user, form.cleaned_data.get('password'))
            
            # standard user: logout
            if user == request.user:
                logout(request)
                        
                # redirect to login page with special message
                response = HttpResponseRedirect(reverse('login')+"?message=password_update")
                openid = user.profile.openid()
                if openid is not None:
                    set_openid_cookie(response, openid)        
                return response
            
            # administrator: back to user profile
            else:
                return HttpResponseRedirect(reverse('user_detail',
                                                    kwargs={'user_id': user.id})+"?message=password_updated_by_admin")

        else:
            log.debug("Form is invalid: %s" % form.errors)
            return render_password_change_form(request, form, user.username)


def user_reminder(request):
    
    # redirect to another node if necessary
    if redirectToIdp():
        return HttpResponseRedirect(settings.IDP_REDIRECT + request.path)

    if request.method == 'GET':
        form = UsernameReminderForm()
        return render_user_reminder_form(request, form)

    else:
        form = UsernameReminderForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')

            # look up username
            users = User.objects.filter(email__iexact=email)

            # user in this context is an account. There can be more than one account associated with an email
            if len(users) > 0:

                # send email with username(s) to the requester
                subject = "Username/OpenID Reminder"
                message = ""
                for user in users:
                    message += "\nYour username is: %s\n" % user.username

                    for openid in user.profile.openids():
                        message += "Your OpenID is: %s\n" % openid

                sendEmail(email, subject, message)

                # redirect to login page with special message
                return HttpResponseRedirect(reverse('login')+"?message=user_reminder")

            # user not found
            else:
                return render_user_reminder_form(request, form, "This email address cannot be found.")

        else:
            log.debug("Form is invalid: %s" % form.errors)
            return render_user_reminder_form(request, form)


def password_reset(request):
    
    # redirect to another node if necessary
    if redirectToIdp():
        return HttpResponseRedirect(settings.IDP_REDIRECT + request.path)
    
    if request.method == 'GET':
        
        # optional GET parameters to pre-populate the form
        initial = {'openid': request.GET.get('openid', ''),
                   'email': request.GET.get('email', '')}
        
        form = PasswordResetForm(initial=initial)       
        return render_password_reset_form(request, form)

    else:
        form = PasswordResetForm(request.POST)

        # check form is valid first
        if not form.is_valid():
            log.debug("Form is invalid: %s" % form.errors)
            return render_password_reset_form(request, form)

        openid = form.cleaned_data.get('openid')
        email = form.cleaned_data.get('email')
        
        # the openid entered by the user MUST be found in the local database
        # otherwise we can neither change the password, nor we can redirect to a known node
        try:
            userOpenid = UserOpenID.objects.get(claimed_id=openid)
            user = userOpenid.user
            
            # 1) local user (i.e. user home node == this node)
            if isUserLocal(user):
            
                # 1a) this node issued this openid
                if isOpenidLocal(openid):
    
                    if user.email == email:
                                            
                        # generate new random password
                        # prepend "AB1-" to satisfy mandatory requirements
                        new_password = "Ab1-"+User.objects.make_random_password(length=8)
        
                        # change password in database
                        user.set_password(new_password)
                        user.save()
                        user.profile.last_password_update = datetime.datetime.now()
                        user.profile.save()
                        
                        # update ESGF user object
                        if settings.ESGF_CONFIG:
                            esgfDatabaseManager.updatePassword(user, new_password)
        
                        # logout user (if logged in)
                        logout(request)
        
                        # user profile url
                        url = reverse('user_detail', kwargs={'user_id': user.id})
                        url = request.build_absolute_uri(url)
        
                        # send email to user
                        subject = "Password Reset"
                        message = "Your new password has been set to: %s\n" % new_password
                        message += "Your openid is: %s\n" % user.profile.openid()
                        message += "For security reasons, please change this password as soon as you log in.\n"  
                        message += "To change your password, first log in with your openid and new password,\n"
                        message += "then click on the 'My Profile' link on the top-right of each page,\n"
                        message += "or visit the following URL: %s" % url
                        notify(user, subject, message)
        
                        # redirect to login page with special message
                        return HttpResponseRedirect(reverse('login')+"?message=password_reset")
                    
                    else:
                        return render_password_reset_form(request, form, "Invalid OpenID/email combination")

                # 1b) user used an external ESGF openid (for example, http://dkrz...) to login onto this node
                # (for example, http://www.earthsystemcog.org/...)
                else:
                    idpurl = urlparse(openid)
                    idpurl = "%s://%s/" % (idpurl.scheme, idpurl.netloc)
                    message = "This OpenID was issued by another node."
                    message += "<br/>Please reset your password at <a href='%s'>that node</a>." % idpurl
                    return render_password_reset_form(request, form, message)
                
            #  2) non-local user: redirect request to peer node, post automatically
            else:
                site = user.profile.site
                redirect_url = 'http://%s%s?openid=%s&email=%s' % (site.domain, reverse('password_reset'),
                                                                   openid, email)
                
                # 2a) automatically redirect to peer node
                #redirect_url += "&post=true" # submit form automatically at that node
                #return HttpResponseRedirect(redirect_url)
                
                # 2b) show message on this node with link to peer node
                message = "This OpenID was issued by another ESG-CoG node."
                message += "<br/>Please use the <a href='%s'>Reset Password</a> page at that node." % redirect_url
                return render_password_reset_form(request, form, message)
                
        # openid not found
        except UserOpenID.DoesNotExist:
            message = "OpenID not found."
            message += "<br/>If your OpenID was issued by '%s'," % settings.ESGF_HOSTNAME
            message += "<br/>then please use the 'Forgot OpenID?' link below to retrieve the correct OpenID." 
            message += "<br/>Otherwise, please reset your password on the ESGF-CoG node that issued your OpenID."
            return render_password_reset_form(request, form, message)


def render_user_form(request, form, formset, title=''):
    return render(request, 'cog/account/user_form.html',
                  {'form': form, 'formset': formset, 'mytitle': title})


def render_password_change_form(request, form, username):
    return render(request, 'cog/account/password_change.html',
                  {'form': form, 'mytitle': 'Change Password for User: %s' % username})


def render_password_reset_form(request, form, message=""):
    return render(request, 'cog/account/password_reset.html',
                  {'form': form, 'mytitle': 'Reset User Password', 'message': message})


def render_user_reminder_form(request, form, message=""):
    return render(request, 'cog/account/user_reminder.html',
                  {'form': form, 'mytitle': 'UserName and OpenID Reminder', 'message': message})


def render_site_change_form(request, form):
    return render(request, 'cog/account/site_change.html',
                              {'form': form, 'mytitle' : 'Change User Home Node' })