from django.db import models
from constants import APPLICATION_LABEL, ORGANIZATIONAL_ROLE_CV, ORGANIZATIONAL_ROLE_CATEGORIES_CV
from project import Project
from django.contrib.auth.models import User
from cog.models.constants import ROLE_CATEGORY_LEAD, ROLE_CATEGORY_MEMBER, ORGANIZATIONAL_ROLES_DICT, LEAD_ORGANIZATIONAL_ROLES_DICT


class OrganizationalRole(models.Model):

    title = models.CharField(max_length=200, blank=False, verbose_name='Title',  help_text='String used to succinctly describe an organizational role.')
    description = models.TextField(blank=True, null=True, verbose_name='Description', help_text='Long description providing extra information about an organizational role.')
    type = models.CharField(max_length=50, blank=False, null=False, choices=ORGANIZATIONAL_ROLE_CV, verbose_name='Type', help_text='Type of organizational role (choose from controlled vocabulary).')
    category = models.CharField(max_length=50, blank=True, null=False, default='Member', choices=ORGANIZATIONAL_ROLE_CATEGORIES_CV, verbose_name='Category', help_text='Lead or Member role.')
    project = models.ForeignKey(Project)

    def set_category(self, dict={}):
        """Method to select the object category from the other fields. """

        if self.type in LEAD_ORGANIZATIONAL_ROLES_DICT:
            self.category = ROLE_CATEGORY_LEAD
        else:
            self.category = ROLE_CATEGORY_MEMBER

    def members(self):
        return self.organizationalrolemember_set.all()

    def __unicode__(self):
        return "%s %s" % (self.project.short_name, self.title)

    class Meta:
        app_label= APPLICATION_LABEL

def getLeadOrganizationalRoles(project):
    '''Returns the lead organizational roles for a given project.'''
    return getOrganizationalRoles(project, ROLE_CATEGORY_LEAD)

def getMemberOrganizationalRoles(project):
    '''Returns the member organizational roles for a given project.'''
    return getOrganizationalRoles(project, ROLE_CATEGORY_MEMBER)

def getOrganizationalRoles(project, category):
    '''Returns a sorted list of a specific category of organizational roles for a given project.'''

    # transform QuerySet into list
    roles = list(OrganizationalRole.objects.filter(project=project).filter(category=category))

    # sort by display number
    return sorted(roles, key=lambda role: ORGANIZATIONAL_ROLES_DICT.get(role.type,0))