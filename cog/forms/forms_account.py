from django.db import models
from django.contrib.auth.models import User
from django.forms import Form, ModelForm, CharField, PasswordInput, TextInput, BooleanField, ImageField, FileInput, Textarea
from cog.models import *
from django.core.exceptions import ObjectDoesNotExist
import re
from django.contrib.auth.models import check_password
from os.path import exists
from cog.models.constants import UPLOAD_DIR_PHOTOS
from cog.forms.forms_image import ImageForm
from cog.models.constants import RESEARCH_KEYWORDS_MAX_CHARS, RESEARCH_INTERESTS_MAX_CHARS
import os.path
from django_openid_auth.models import UserOpenID

# list of invalid characters in text fields
#INVALID_CHARS = "[^a-zA-Z0-9_\-\+\@\.\s,()\.;-]"
INVALID_CHARS = "[<>&#%{}\[\]\$]"
INVALID_USERNAME_CHARS = "[^a-zA-Z0-9_\-\+\@\.]"

class UserUrlForm(ModelForm):

    url = CharField(required=True, widget=TextInput(attrs={'size':'35'}))
    name = CharField(required=True, widget=TextInput(attrs={'size':'15'}))

    # validate data against bad characters
    def clean(self):

        url = self.cleaned_data.get('url')
        validate_field(self, 'url', url)

        name = self.cleaned_data.get('name')
        validate_field(self, 'name', name)

        return self.cleaned_data

class UserOpenidForm(ModelForm):

    claimed_id =  CharField(required=True, widget=TextInput(attrs={'size':'90'}))

    class Meta:
        model = UserOpenID
        fields = ('claimed_id',)

class PasswordResetForm(Form):

    username = CharField(required=True, widget=TextInput(attrs={'size':'50'}))
    email = CharField(required=True, widget=TextInput(attrs={'size':'50'}))

    # validate data against bad characters
    def clean(self):

        username = self.cleaned_data.get('username')
        validate_field(self, 'username', username)

        email = self.cleaned_data.get('email')
        validate_field(self, 'email', email)

        return self.cleaned_data

class UsernameReminderForm(Form):

    email = CharField(required=True, widget=TextInput(attrs={'size':'50'}))

    # validate data against bad characters
    def clean(self):

        email = self.cleaned_data.get('email')
        validate_field(self, 'email', email)

        return self.cleaned_data


class PasswordChangeForm(Form):

    old_password = CharField(required=True, widget=PasswordInput())
    password = CharField(required=True, widget=PasswordInput())
    confirm_password = CharField(required=True, widget=PasswordInput())

    # override __init__ method to store the user object
    def __init__(self, user, *args,**kwargs):

        super(PasswordChangeForm, self ).__init__(*args,**kwargs) # populates the post
        self.user = user

    def clean(self):

        # check current password
        old_password = self.cleaned_data.get('old_password')
        if not check_password(old_password, self.user.password):
            self._errors["old_password"] = self.error_class(["Wrong old password."])

        # validate 'password', 'confirm_password' fields
        validate_password(self)

        return self.cleaned_data

class UserForm(ImageForm):

    # override User form fields to make them required
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    username = CharField(required=True)
    email = CharField(required=True)
    password = CharField(required=True, widget=PasswordInput())

    # additional fields not in User
    confirm_password = CharField(required=True, widget=PasswordInput())
    institution = CharField(required=True)
    department = CharField(required=False)
    city = CharField(required=True)
    state = CharField(required=False)
    country = CharField(required=True)
    subscribed = BooleanField(required=False)
    private = BooleanField(required=False)
    researchInterests = CharField(required=False, widget=Textarea(attrs={'rows': 6}), max_length=RESEARCH_INTERESTS_MAX_CHARS)
    researchKeywords = CharField(required=False, max_length=RESEARCH_KEYWORDS_MAX_CHARS)

    # do NOT use default widget 'ClearableFileInput' as it doesn't work well with forms.ImageField
    image = ImageField(required=False, widget=FileInput)

    # extra field not present in model, used for deletion of previously uploaded image
    # inherited from ImageForm
    #delete_image = BooleanField(required=False)


    class Meta:
        # note: use User model, not UserProfile
        model = User
        # define fields to be used, so to exclude last_login and date_joined
        fields = ('first_name', 'last_name', 'username', 'password', 'email',
                  'institution','city','state','country','department',
                  'subscribed','private',
                  'image', 'delete_image', 'researchInterests', 'researchKeywords')

    # override form clean() method to execute custom validation on fields,
    # including combined validation on multiple fields
    def clean(self):

        # invoke superclass cleaning method
        super(UserForm, self).clean()

        # flags an existing user
        user_id = self.instance.id

        cleaned_data = self.cleaned_data

        # new user only: validate 'password', 'confirm_password' fields
        #if not user_id:
        validate_password(self)

        # validate 'username' field
        validate_username(self, user_id)

        # additional validation on 'image' field
        validate_image(self)

        # validate all other fields against injection attacks
        for field in ['first_name','last_name', 'username', 'email', 'institution', 'department', 'city', 'state', 'country',
                      'researchInterests', 'researchKeywords']:
            try:
                validate_field(self, field, cleaned_data[field])
            except KeyError: # field not set (validation occurs later)
                pass

        return cleaned_data

def validate_image(form):

    cleaned_data = form.cleaned_data
    image = cleaned_data.get("image", None)
    if image is not None:
        print 'image name=%s' % image.name
        extension = (os.path.splitext(image.name)[1]).lower()
        if extension != '.jpg' and extension != '.png' and extension != '.gif' and extension != '.jpeg' :
            form._errors["image"] = form.error_class(["Invalid image format: %s"%extension])


# method to validate the fields 'password" and 'confirm_password'
def validate_password(form):

        cleaned_data = form.cleaned_data

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password:
            if len(password) < 6:
                form._errors["password"] = form.error_class(["'Password' must contain at least 6 characters."])
            if password != confirm_password:
                form._errors["confirm_password"] = form.error_class(["'Password' and 'Confirm Password' must match."])

# method to validate the field 'username'
def validate_username(form, user_id):

        cleaned_data = form.cleaned_data

        username = cleaned_data.get("username")
        if username:
            if len(username) < 5:
                form._errors["username"] = form.error_class(["'Username' must contain at least 5 characters."])
            elif len(username) >30:
                form._errors["username"] = form.error_class(["'Username' must not exceed 30 characters."])
            elif re.search(INVALID_USERNAME_CHARS, username):
                form._errors["username"] = form.error_class(["'Username' can only contain letters, digits and @/./+/-/_"])
            try:
                # perform case-insensitive lookup of username, compare with id from form instance
                user =  User.objects.all().get(username__iexact=username)
                if user!=None and user.id != user_id:
                    form._errors["username"] = form.error_class(["Username already taken in database"])
            except ObjectDoesNotExist:
                pass

# method to validate a generic field against bad characters
def validate_field(form, field_name, field_value):
    if field_value:
        if re.search(INVALID_CHARS, field_value):
            form._errors[field_name] = form.error_class(["'%s' contains invalid characters." % field_name])