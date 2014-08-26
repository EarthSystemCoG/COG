from cog.forms.forms_account import *
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from cog.models import *
from cog.util.thumbnails import *
from django.forms.models import modelformset_factory

from cog.notification import notify, sendEmail
from django.contrib.auth.views import login
from django_openid_auth.views import login_complete
from django.contrib.auth.hashers import is_password_usable
from django.core.exceptions import ObjectDoesNotExist
from django_openid_auth.models import UserOpenID
from django.contrib.sites.models import Site
from cog.plugins.esgf.security import esgfDatabaseManager
import datetime
from cog.views.utils import set_openid_cookie

def custom_login(request, **kwargs):
    '''Overriden standard login view that checks whether the authenticated user has any missing information.'''
    
    # authenticate user via standard login
    response = login(request, **kwargs)

    # check if user is valid
    return _custom_login(request, response)

def custom_login_complete(request, **kwargs):
    '''Method invoked after successful OpenID login.
       Overridden to create user profile after first successful OpenID login.
    '''

    # authenticate user
    response = login_complete(request, **kwargs)

    # create a stub profile with blank mandatory fields
    if not request.user.is_anonymous():
        openid = request.GET.get('openid.claimed_id', None)
        try:
            request.user.profile
            
        except ObjectDoesNotExist:

            # retrieve user home site            
            site = discoverSiteForUser( openid )
            if site is None: 
                # set user home site to current site
                site = Site.objects.get_current()
                
            # create new ESGF/OpenID login
            UserProfile.objects.create(user=request.user, institution='', city='', country='', type=2, site=site) # type=2: ESGF

            # create user datacart
            DataCart.objects.create(user=request.user)
            
            # set openid cookie
            set_openid_cookie(response, openid)

    # check if user is valid
    return _custom_login(request, response)


def _custom_login(request, response):

    # succesfull login
    if not request.user.is_anonymous():
        
        # FIXME
        print 'USER TYPE=%s' % request.user.profile.type
        print 'isUserLocal=%s' % isUserLocal(request.user)
        print 'isUserValid=%s' % isUserValid(request.user)
        
        # missing information
        if isUserLocal(request.user) and not isUserValid(request.user):
            return HttpResponseRedirect(reverse('user_update', kwargs={ 'user_id':request.user.id })+"?message=incomplete_profile")
        
    return response


def notifyAdminsOfUserRegistration(user):

    subject = 'New User Registration'
    message = 'User %s has created a new account' % user.get_full_name()

    # user attributes
    message += "\nFirst Name: %s" % user.first_name
    message += "\nLast Name: %s" % user.last_name
    message += "\nUser Name: %s" % user.username
    message += "\nEmail: %s" % user.email
    
    # openid
    message += "\nOpenID is: %s" % user.profile.localOpenid()

    # user profile attributes
    profile = UserProfile.objects.get(user=user)
    message += "\nInstitution: %s" % profile.institution
    message += "\nDepartment: %s" % profile.department
    message += "\nCity: %s" % profile.city
    message += "\nState: %s" % profile.state
    message += "\nCountry: %s" % profile.country
    message += "\nSubscribe to COG email list? %s" % profile.subscribed

    for admin in getSiteAdministrators():
        notify(admin, subject, message)
        
def notifyUserOfRegistration(user):
    
    subject = "CoG Account Creation"
    message = "Thank you for creating a new CoG account."
    message += "\n"
    message += "\nYour User Name is: %s" % user.username
    message += "\nYour OpenID is: %s" % user.profile.localOpenid()
    message += "\n"
    message += "\nPlease note that you will need your OpenID to login"
    notify(user, subject, message)

def subscribeUserToMailingList(user, request):
    """Method to notify administrators of user subscription request."""

    notifyAdminsOfUserSubscription(user, request, 'join')

def unSubscribeUserToMailingList(user, request):
    """Method to notify administrators of user un-subscription."""

    notifyAdminsOfUserSubscription(user, request, 'leave')

def notifyAdminsOfUserSubscription(user, request, action):

    subject = 'User request to %s the email list %s' % (action, settings.COG_MAILING_LIST)
    message = 'User: %s has requested to %s the email list: %s' % (user.get_full_name(), action, settings.COG_MAILING_LIST)

    url = reverse('user_detail', kwargs={ 'user_id':user.id })
    url = request.build_absolute_uri(url)
    message += '\nUser profile: %s\n' % url
    for admin in getSiteAdministrators():
        notify(admin, subject, message)


# view to create a user account
def user_add(request):
    
    # redirect to another site if necessary
    if settings.IDP_REDIRECT is not None:
        return HttpResponseRedirect( settings.IDP_REDIRECT + request.path )

    # create URLs formset
    UserUrlFormsetFactory = modelformset_factory(UserUrl, form=UserUrlForm, exclude=('profile',), can_delete=True, extra=2)
    UserOpenidFormsetFactory = modelformset_factory(UserOpenID, form=UserOpenidForm, can_delete=True, extra=2)

    if (request.method=='GET'):

        form = UserForm() # unbound form
        formset1 = UserUrlFormsetFactory(queryset=UserUrl.objects.none(), prefix='url')          # empty formset
        # NOTE: currently openid formset is not really used when first creating COG users
        formset2 = UserOpenidFormsetFactory(queryset=UserOpenID.objects.none(), prefix='openid') # empty formset

        return render_user_form(request, form, formset1, formset2, title='Create User Profile')

    else:
        form = UserForm(request.POST, request.FILES,) # form with bounded data
        formset1 = UserUrlFormsetFactory(request.POST, queryset=UserUrl.objects.none(), prefix='url')         # formset with bounded data
        formset2 = UserOpenidFormsetFactory(request.POST, queryset=UserOpenID.objects.none(), prefix='openid') # formset with bounded data


        if form.is_valid() and formset1.is_valid() and formset2.is_valid():

            # create a user from the form but don't save it to the database yet because the password is not encoded yet
            user = form.save(commit=False)
            # must reset the password through the special method that encodes it correctly
            clearTextPassword = form.cleaned_data['password']
            user.set_password( clearTextPassword )

            # save user to database
            user.save()
            print 'Created user=%s' % user.get_full_name()

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

            userp.clearTextPassword = clearTextPassword # NOTE: this field is NOT persisted
            
            # save user profile --> will trigger userProfile post_save and consequent creation of openid
            userp.save()

            # create user data cart
            datacart = DataCart(user=user)
            datacart.save()

            # must assign URL to this user
            urls = formset1.save(commit=False)
            for url in urls:
                url.profile = userp
                url.save()

            # generate thumbnail image
            if userp.image is not None:
                try:
                    generateThumbnail(userp.image.path, THUMBNAIL_SIZE_SMALL)
                except ValueError:
                    pass # image does not exist, ignore

            # notify user, site administrators of new registration
            notifyUserOfRegistration(user)
            notifyAdminsOfUserRegistration(user)

            # subscribe to mailing list ?
            if userp.subscribed==True:
                subscribeUserToMailingList(user, request)

            # redirect to login page with special message
            response = HttpResponseRedirect(reverse('login')+"?messageuser_add")
            
            # set openid cookie
            set_openid_cookie(response, userp.localOpenid())

            return response

        else:
            if not form.is_valid():
                print "Form is invalid: %s" % form.errors
            elif not formset1.is_valid():
                print "URL formset is invalid: %s" % formset1.errors
            elif not formset2.is_valid():
                print "OpenID formset is invalid: %s" % formset1.errors
            return render_user_form(request, form, formset1, formset2, title='Create User Profile')

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
        print "Created empty profile for user=%s" % user

    # retrieve map of (project, groups) for this user
    projects = getProjectsForUser(user, True) # include pending projects

    return render_to_response('cog/account/user_detail.html',
                              { 'user_profile': user_profile, 'projects':projects },
                              context_instance=RequestContext(request))
    
# view to redirect to the user profile on the local or remote site
# this view is always invoked with the *local* user 'id'
def user_profile_redirect(request, user_id):
    
    if (request.method=='GET'):
        
        # load User object
        user = get_object_or_404(User, pk=user_id)
        
        if isUserRemote(user):
            return HttpResponseRedirect( user.profile.getAbsoluteUrl() )
                                         
        else:
            return HttpResponseRedirect(reverse('user_detail', kwargs={ 'user_id': user.id }))

        
    else:
        return HttpResponseNotAllowed(['GET'])
    
# view to look up a *local* user by OpenID
# this view does NOT redirect to other peer sites
# (user_profile_redirect does that)
def user_byopenid(request):
    
    if (request.method=='GET'):
    
        openid = request.GET['openid']
        
        # load User object
        userOpenid = get_object_or_404(UserOpenID, claimed_id=openid)
        
        # redirect to user profile page on local site
        return HttpResponseRedirect(reverse('user_detail', kwargs={ 'user_id': userOpenid.user.id }))
            
    else:
        return HttpResponseNotAllowed(['GET'])
    
    

@login_required
def user_update(request, user_id):

    # security check
    if str(request.user.id) != user_id and not request.user.is_staff:
        raise Exception("User not authorized to change profile data")

    # get user
    user = get_object_or_404(User, pk=user_id)
    profile = get_object_or_404(UserProfile, user=user)

    # create URLs formset
    UserUrlFormsetFactory = modelformset_factory(UserUrl, form=UserUrlForm, exclude=('profile',), can_delete=True, extra=2)
    UserOpenidFormsetFactory = modelformset_factory(UserOpenID, form=UserOpenidForm, can_delete=True, extra=2)

    if (request.method=='GET'):

        # pre-populate form, including value of extra field 'confirm_password'
        form = UserForm(instance=user, initial={ 'confirm_password':user.password,
                                                 'institution':profile.institution,
                                                 'city':profile.city,
                                                 'state':profile.state,
                                                 'country':profile.country,
                                                 'department':profile.department,
                                                 'researchKeywords':profile.researchKeywords,
                                                 'researchInterests':profile.researchInterests,
                                                 'subscribed':profile.subscribed,
                                                 'private':profile.private,
                                                 'image':profile.image,
                                                 'type':profile.type })

        # retrieve existing URLs and OpenIDs associated to this user
        formset1 = UserUrlFormsetFactory(queryset=UserUrl.objects.filter(profile=profile), prefix='url')
        formset2 = UserOpenidFormsetFactory(queryset=UserOpenID.objects.filter(user=profile.user), prefix='openid')

        return render_user_form(request, form, formset1, formset2, title='Update User Profile')

    else:
        form = UserForm(request.POST, request.FILES, instance=user) # form with bounded data
        formset1 = UserUrlFormsetFactory(request.POST, queryset=UserUrl.objects.filter(profile=profile), prefix='url')            # formset with bounded data
        formset2 = UserOpenidFormsetFactory(request.POST, queryset=UserOpenID.objects.filter(user=profile.user), prefix='openid') # formset with bounded data

        if form.is_valid() and formset1.is_valid() and formset2.is_valid():

            # update user
            user = form.save()

            # update user profile
            user_profile = get_object_or_404(UserProfile, user=user)
            oldSubscribed = user_profile.subscribed
            user_profile.institution = form.cleaned_data['institution']
            user_profile.city=form.cleaned_data['city']
            user_profile.state=form.cleaned_data['state']
            user_profile.country=form.cleaned_data['country']
            user_profile.department=form.cleaned_data['department']
            user_profile.researchKeywords=form.cleaned_data['researchKeywords']
            user_profile.researchInterests=form.cleaned_data['researchInterests']
            user_profile.subscribed=form.cleaned_data['subscribed']
            user_profile.private=form.cleaned_data['private']

            # check if the password is encoded already
            # if not, encode the password that the user provided in clear text
            if not is_password_usable(user.password):
                user.set_password( form.cleaned_data['password'] )
                user.save()
                print 'Reset password for user=%s' % user

            # image management
            _generateThumbnail = False
            if form.cleaned_data.get('delete_image')==True:
                deleteImageAndThumbnail(user_profile)

            elif form.cleaned_data['image'] is not None:
                # delete previous image
                try:
                    deleteImageAndThumbnail(user_profile)
                except ValueError:
                    # image not existing, ignore
                    pass

                user_profile.image=form.cleaned_data['image']
                _generateThumbnail = True

            # persist changes
            user_profile.save()

            # must assign URL to this user
            urls = formset1.save(commit=False)
            for url in urls:
                url.profile = profile
                url.save()

            # must assign OpenIDs to this user
            openids = formset2.save(commit=False)
            for openid in openids:
                openid.user = profile.user
                openid.save()
                

            # generate thumbnail - after picture has been saved
            if _generateThumbnail:
                generateThumbnail(user_profile.image.path, THUMBNAIL_SIZE_SMALL)

            # subscribe/unsubscribe user is mailing list selection changed
            if oldSubscribed==True and form.cleaned_data['subscribed']==False:
                unSubscribeUserToMailingList(user, request)
            elif oldSubscribed==False and form.cleaned_data['subscribed']==True:
                subscribeUserToMailingList(user, request)

            # redirect user profile page
            response = HttpResponseRedirect(reverse('user_detail', kwargs={ 'user_id':user.id }))
            
            # set openid cookie to first available openid
            set_openid_cookie(response, user.profile.openid())

            return response

        else:
            if not form.is_valid():
                print "Form is invalid: %s" % form.errors
            elif not formset1.is_valid():
                print "URL formset is invalid: %s" % formset1.errors
            elif not formset2.is_valid():
                print "OpenID formset is invalid: %s" % formset2.errors

            return render_user_form(request, form, formset1, formset2, title='Update User Profile')

#@login_required
def password_update(request):


    if (request.method=='GET'):

        # create form
        if request.user.is_anonymous():
            initial = {}
        else: # pre-fill username
            initial={ 'username': request.user.username }
        form = PasswordChangeForm(initial=initial)
        return render_password_change_form(request, form)

    else:
        form = PasswordChangeForm(request.POST)

        if form.is_valid():
            
            user = User.objects.get(username=form.cleaned_data.get('username'))

            # change password in database
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            user.profile.last_password_update = datetime.datetime.now()
            user.profile.save()
            
            # update ESGF user object
            if settings.ESGF_CONFIG:
                esgfDatabaseManager.updatePassword(user, form.cleaned_data.get('password') )
            
            # logout user
            logout(request)
                        
            # redirect to login page with special message
            response = HttpResponseRedirect(reverse('login')+"?message=password_update")
            openid = user.profile.localOpenid()
            if openid is not None:
                set_openid_cookie(response, openid)        
            return response

        else:
            print "Form is invalid: %s" % form.errors
            return render_password_change_form(request, form)
        
def user_reminder(request):

    if (request.method=='GET'):
        form = UsernameReminderForm()
        return render_user_reminder_form(request, form)

    else:
        form = UsernameReminderForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')

            # look up username
            users = User.objects.filter(email__iexact=email)

            if len(users)>0:

                # send email with username(s) to user
                subject = "Username/OpenID Reminder"
                message = ""
                for user in users:
                    message +=  "Your username is: %s\n"  % user.username

                    for openid in user.profile.openids():
                        message += "Your OpenID is: %s\n" % openid

                notify(user, subject, message)

                # redirect to login page with special message
                return HttpResponseRedirect(reverse('login')+"?message=user_reminder")

            # user not found
            else:
                return render_user_reminder_form(request, form, "This email address cannot be found")

        else:
            print "Form is invalid: %s" % form.errors
            return render_user_reminder_form(request, form)


def password_reset(request):

    if (request.method=='GET'):
        form = PasswordResetForm()
        return render_password_reset_form(request, form)

    else:
        form = PasswordResetForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            # look for user with given username, email
            try:
                # retrieve user for given username and email
                user = User.objects.filter(username=username).get(email__iexact=email)
                
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
                url = reverse('user_detail', kwargs={ 'user_id': user.id })
                url = request.build_absolute_uri(url)

                # send email to user
                subject = "Password Reset"
                message =  "Your new password has been set to: %s .\nFor security reasons, please change this password as soon as you log in."  % new_password
                message += "\nTo change your password, click on the 'My Profile' link on the top-right of each page, " \
                         + "\nor visit the following URL: %s" % url
                notify(user, subject, message)

                # redirect to login page with special message
                return HttpResponseRedirect(reverse('login')+"?message=password_reset")

            # user not found
            except User.DoesNotExist:
                return render_password_reset_form(request, form, "Invalid username/email combination")

        else:
            print "Form is invalid: %s" % form.errors
            return render_password_reset_form(request, form)

def render_user_form(request, form, formset1, formset2, title=''):
    return render_to_response('cog/account/user_form.html',
                              {'form': form, 'formset1':formset1, 'formset2':formset2, 'mytitle' : title },
                              context_instance=RequestContext(request))

def render_password_change_form(request, form):
    return render_to_response('cog/account/password_change.html',
                              {'form': form, 'mytitle' : 'Change User Password' },
                              context_instance=RequestContext(request))

def render_password_reset_form(request, form, message=""):
    return render_to_response('cog/account/password_reset.html',
                              {'form':form, 'mytitle':'Reset User Password', 'message':message },
                              context_instance=RequestContext(request))

def render_user_reminder_form(request, form, message=""):
    return render_to_response('cog/account/user_reminder.html',
                              {'form':form, 'mytitle':'UserName and OpenID Reminder', 'message':message },
                              context_instance=RequestContext(request))
    
def render_site_change_form(request, form):
    return render_to_response('cog/account/site_change.html',
                              {'form': form, 'mytitle' : 'Change User Home Site' },
                              context_instance=RequestContext(request))