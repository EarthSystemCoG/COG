from cog.forms.forms_account import *
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from cog.models import *
from cog.util.thumbnails import *

from cog.notification import notify, sendEmail
from django.conf import settings

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
    
    if (request.method=='GET'):
        
        form = UserForm() # unbound form     
                
        return render_user_form(request, form, title='Create User Profile')

    else:
        form = UserForm(request.POST) # form with bounded data
        
        if form.is_valid():
            
            # create a user from the form but don't save it to the database yet because the password is not encoded yet
            user = form.save(commit=False)
            # must reset the password through the special method that encodes it correctly
            user.set_password(form.cleaned_data['password'])
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
                                subscribed=form.cleaned_data['subscribed'],
                                private=form.cleaned_data['private'])
            userp.save()
            print 'Created profile for user=%s' % user.get_full_name()
            
            # notify site administrators
            notifyAdminsOfUserRegistration(user)
            
            # subscribe to mailing list ?
            if userp.subscribed==True:
                subscribeUserToMailingList(user, request)
            
            # redirect to login page with special message
            message = 'Thank you for creating an account. You can now login.'
            return HttpResponseRedirect(reverse('login')+"?message=%s" % message)
             
        else: 
            print "Form is invalid: %s" % form.errors
            return render_user_form(request, form, title='Create User Profile')
        
# view to display user data
# require login to limit exposure of user information
@login_required 
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
    if not request.user.id != user_id:
        raise Exception("User not authorized to change profile data")
    
    # get user
    user = get_object_or_404(User, pk=user_id)
    
    if (request.method=='GET'):
        
        # pre-populate form, including value of extra field 'confirm_password'
        profile = get_object_or_404(UserProfile, user=user)
        form = UserForm(instance=user, initial={ 'confirm_password':user.password,
                                                 'institution':profile.institution, 
                                                 'city':profile.city, 
                                                 'state':profile.state,
                                                 'country':profile.country, 
                                                 'department':profile.department,
                                                 'subscribed':profile.subscribed,
                                                 'private':profile.private,
                                                 'photo':profile.photo })
                
        return render_user_form(request, form, title='Update User Profile')

    else:
        form = UserForm(request.POST, request.FILES, instance=user) # form with bounded data
        
        if form.is_valid():
            
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
            user_profile.subscribed=form.cleaned_data['subscribed']
            user_profile.private=form.cleaned_data['private']
            
            # photo management
            _generateThumbnail = False
            if form.cleaned_data.get('delete_photo')==True:
                deletePhotoAndThumbnail(user_profile)
                
            elif form.cleaned_data['photo'] is not None:
                # delete previous photo
                try:
                   deletePhotoAndThumbnail(user_profile) 
                except ValueError:
                    # photo not existing, ignore
                    pass
                   
                user_profile.photo=form.cleaned_data['photo']
                _generateThumbnail = True
            
            # persist changes
            user_profile.save()
            
            # generate thumbnail - after picture has been saved
            if _generateThumbnail:
                generateThumbnail(user_profile.photo.path)
                        
            # subscribe/unsubscribe user is mailing list selection changed
            if oldSubscribed==True and form.cleaned_data['subscribed']==False:
                unSubscribeUserToMailingList(user, request)
            elif oldSubscribed==False and form.cleaned_data['subscribed']==True:
                subscribeUserToMailingList(user, request)

            # redirect user profile page
            return HttpResponseRedirect(reverse('user_detail', kwargs={ 'user_id':user.id }))
             
        else: 
            print "Form is invalid: %s" % form.errors
            return render_user_form(request, form, title='Update User Profile')
            
@login_required
def password_update(request, user_id):
    
    # security check
    if not request.user.id != user_id:
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
            message = 'Your password has been changed. Please login again.'
            return HttpResponseRedirect(reverse('login')+"?message=%s" % message)

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
                message = 'Your username has been emailed to the address you provided. Please check your email box.'
                return HttpResponseRedirect(reverse('login')+"?message=%s" % message)

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
            
            # look for user with given username, password
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
                message = 'A new password has been e-mailed to you. Please use the new password to login and change it as soon as possible.'
                return HttpResponseRedirect(reverse('login')+"?message=%s" % message)
              
            # user not found
            except User.DoesNotExist:            
                return render_password_reset_form(request, form, "Invalid username/email combination")

        else:
            print "Form is invalid: %s" % form.errors
            return render_password_reset_form(request, form)
            
def render_user_form(request, form, title=''):
    return render_to_response('cog/account/user_form.html', 
                              {'form': form, 'mytitle' : title }, 
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