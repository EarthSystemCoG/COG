from django.db import models
from django.contrib.auth.models import User
from constants import APPLICATION_LABEL, RESEARCH_KEYWORDS_MAX_CHARS, RESEARCH_INTERESTS_MAX_CHARS

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from cog.plugins.esgf.security import esgfDatabaseManager

class UserProfile(models.Model):

    # user
    user = models.OneToOneField(User)

    # additional mandatory fields
    institution = models.CharField(max_length=100, blank=False, default='')
    city = models.CharField(max_length=100, blank=False, null=False, default='')
    country = models.CharField(max_length=100, blank=False, null=False, default='')

    # additional optional fields
    state = models.CharField(max_length=100, blank=True, null=True, default='')
    department = models.CharField(max_length=100, blank=True, null=True, default='')

    # opt-in mailing list (but defaults to true to migrate existing users)
    subscribed = models.BooleanField(verbose_name='Subscribe to COG mailing list ?', default=True, null=False)

    # opt-out privacy option
    private = models.BooleanField(verbose_name='Do NOT list me among project members', default=False, null=False)

    # optional picture
    image = models.ImageField(upload_to='photos/', blank=True, null=True)

    # optional research information
    researchInterests = models.CharField(max_length=RESEARCH_INTERESTS_MAX_CHARS, blank=True, null=True, default='')
    researchKeywords = models.CharField(max_length=RESEARCH_KEYWORDS_MAX_CHARS, blank=True, null=True, default='')

    # clear text password - this field is NOT persisted to the database, but it is needed to execute MD5 encoding on the user-supplied password
    clearTextPassword = ''

    class Meta:
        app_label= APPLICATION_LABEL

# NOTE: monkey-patch User __unicode__() method to show full name
User.__unicode__ = User.get_full_name

# callback receiver function for UserProfile post_save events
@receiver(post_save, sender=UserProfile, dispatch_uid="user_profile_post_save")
def account_created_receiver(sender, **kwargs):

    # retrieve arguments
    userp = kwargs['instance']
    created = kwargs['created']

    print 'Signal received: UserProfile post_save: user=%s created=%s' % (userp.user.get_full_name(), created)

    # create ESGF user - only when user profile is first created
    if settings.ESGF_CONFIG and created:
        print 'Inserting user into ESGF security database'
        esgfDatabaseManager.insertUser(userp)
