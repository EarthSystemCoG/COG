from cog.forms.forms_account import *
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from cog.models import *
from cog.util.thumbnails import *
from django.forms.models import modelformset_factory

from cog.notification import notify, sendEmail

# view to display the data cart for a given site, user
def datacart_display2(request, site_id, user_id):

    # load User object
    user = get_object_or_404(User, pk=user_id)

    # TODO:: check site, redirect in case
    datacart = DataCart.objects.get(user=user)

    return render_to_response('cog/account/datacart.html',
                              { 'datacart': datacart },
                              context_instance=RequestContext(request))


def notifyAdminsOfUserRegistration(user):

    subject = 'New User Registration'
    message = 'User %s has created a new account' % user.get_full_name()

    # user attributes
    message += "\nFirst Name: %s" % user.first_name
    message += "\nLast Name: %s" % user.last_name
    message += "\nUser Name: %s" % user.username
    message += "\nEmail: %s" % user.email

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

    # create URLs formset
    UserUrlFormsetFactory = modelformset_factory(UserUrl, form=UserUrlForm, exclude=('profile',), can_delete=True, extra=3 )

    if (request.method=='GET'):

        form = UserForm() # unbound form
        formset = UserUrlFormsetFactory(queryset=UserUrl.objects.none()) # empty formset

        return render_user_form(request, form, formset, title='Create User Profile')

    else:
        form = UserForm(request.POST, request.FILES,) # form with bounded data
        formset = UserUrlFormsetFactory(request.POST, queryset=UserUrl.objects.none())   # formset with bounded data


        if form.is_valid() and formset.is_valid():

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
                                image=form.cleaned_data['image'])

            userp.clearTextPassword = clearTextPassword # NOTE: this field is NOT persisted
            userp.save()

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
                    pass # image does not exist, ignore

            # notify site administrators
            notifyAdminsOfUserRegistration(user)

            # subscribe to mailing list ?
            if userp.subscribed==True:
                subscribeUserToMailingList(user, request)

            # redirect to login page with special message
            return HttpResponseRedirect(reverse('login')+"?message=user_add")

        else:
            if not form.is_valid():
                print "Form is invalid: %s" % form.errors
            elif not formset.is_valid():
                print "Formset is invalid: %s" % formset.errors
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
        print "Created empty profile for user=%s" % user

    # retrieve map of (project, groups) for this user
    projects = getProjectsForUser(user, True) # include pending projects

    return render_to_response('cog/account/user_detail.html',
                              { 'user_profile': user_profile, 'projects':projects },
                              context_instance=RequestContext(request))

@login_required
def user_update(request, user_id):

    # security check
    if str(request.user.id) != user_id:
        raise Exception("User not authorized to change profile data")

    # get user
    user = get_object_or_404(User, pk=user_id)
    profile = get_object_or_404(UserProfile, user=user)

    # create URLs formset
    UserUrlFormsetFactory = modelformset_factory(UserUrl, form=UserUrlForm, exclude=('profile',), can_delete=True, extra=3 )

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
                                                 'image':profile.image })

        # retrieve existing URLs associated to this user
        formset = UserUrlFormsetFactory(queryset=UserUrl.objects.filter(profile=profile))

        return render_user_form(request, form, formset, title='Update User Profile')

    else:
        form = UserForm(request.POST, request.FILES, instance=user) # form with bounded data
        formset = UserUrlFormsetFactory(request.POST, queryset=UserUrl.objects.filter(profile=profile))   # formset with bounded data

        if form.is_valid() and formset.is_valid():

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
            urls = formset.save(commit=False)
            for url in urls:
                print 'URL=%s name=%s' % (url.url, url.name)
                url.profile = profile
                url.save()


            # generate thumbnail - after picture has been saved
            if _generateThumbnail:
                generateThumbnail(user_profile.image.path, THUMBNAIL_SIZE_SMALL)

            # subscribe/unsubscribe user is mailing list selection changed
            if oldSubscribed==True and form.cleaned_data['subscribed']==False:
                unSubscribeUserToMailingList(user, request)
            elif oldSubscribed==False and form.cleaned_data['subscribed']==True:
                subscribeUserToMailingList(user, request)

            # redirect user profile page
            return HttpResponseRedirect(reverse('user_detail', kwargs={ 'user_id':user.id }))

        else:
            if not form.is_valid():
                print "Form is invalid: %s" % form.errors
            elif not formset.is_valid():
                print "Formset is invalid: %s" % formset.errors
            return render_user_form(request, form, formset, title='Update User Profile')

@login_required
def password_update(request, user_id):

    # security check
    if str(request.user.id) != user_id:
        raise Exception("User not authorized to change password")

    # load user object
    user = get_object_or_404(User, pk=user_id)

    if (request.method=='GET'):

        # create empty form
        form = PasswordChangeForm(user)
        return render_password_change_form(request, form)

    else:
        form = PasswordChangeForm(user, request.POST)

        if form.is_valid():

            # change password in database
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            # logout user
            logout(request)
            # redirect to login page with special message
            return HttpResponseRedirect(reverse('login')+"?message=password_update")

        else:
            print "Form is invalid: %s" % form.errors
            return render_password_change_form(request, form)

def username_reminder(request):

    if (request.method=='GET'):
        form = UsernameReminderForm()
        return render_username_reminder_form(request, form)

    else:
        form = UsernameReminderForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')

            # look up username
            users = User.objects.filter(email__iexact=email)

            if len(users)>0:

                # send email with username(s) to user
                subject = "Username Reminder"
                message = ""
                for user in users:
                    message +=  "Your username is: %s\n"  % user.username
                notify(user, subject, message)

                # redirect to login page with special message
                return HttpResponseRedirect(reverse('login')+"?message=username_reminder")

            # user not found
            else:
                return render_username_reminder_form(request, form, "This email address cannot be found")

        else:
            print "Form is invalid: %s" % form.errors
            return render_username_reminder_form(request, form)


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
                new_password = User.objects.make_random_password(length=10)

                # change password in database
                user.set_password(new_password)
                user.save()

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

def render_user_form(request, form, formset, title=''):
    return render_to_response('cog/account/user_form.html',
                              {'form': form, 'formset':formset, 'mytitle' : title },
                              context_instance=RequestContext(request))

def render_password_change_form(request, form):
    return render_to_response('cog/account/password_change.html',
                              {'form': form, 'mytitle' : 'Change User Password' },
                              context_instance=RequestContext(request))

def render_password_reset_form(request, form, message=""):
    return render_to_response('cog/account/password_reset.html',
                              {'form':form, 'mytitle':'Reset User Password', 'message':message },
                              context_instance=RequestContext(request))

def render_username_reminder_form(request, form, message=""):
    return render_to_response('cog/account/username_reminder.html',
                              {'form':form, 'mytitle':'Username Reminder', 'message':message },
                              context_instance=RequestContext(request))