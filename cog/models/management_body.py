from django.db import models
from cog.models.constants import (APPLICATION_LABEL, 
                                  MANAGEMENT_BODY_CATEGORY_STRATEGIC, MANAGEMENT_BODY_CATEGORY_OPERATIONAL,
                                  MANAGEMENT_BODY_CV, MANAGEMENT_BODY_CATEGORIES_CV, MANAGEMENT_BODY_CATEGORY_STRATEGIC,
                                  MANAGEMENT_BODY_CATEGORY_OPERATIONAL, STRATEGIC_MANAGEMENT_BODY_DICT,
                                  OPERATIONAL_MANAGEMENT_BODY_DICT, MANAGEMENT_BODY_DICT)
from cog.models.project import Project

import logging

log = logging.getLogger()

class ManagementBodyPurpose(models.Model):
    purpose = models.CharField(max_length=50, null=False, default='Other', choices=MANAGEMENT_BODY_CV,
                               verbose_name='Purpose/Role',
                               help_text='Type of organizational body (choose from controlled vocabulary).')
    order = models.IntegerField(blank=True, default=0)
    category = models.CharField(max_length=50, null=False, default=MANAGEMENT_BODY_CATEGORY_STRATEGIC,
                                choices=MANAGEMENT_BODY_CATEGORIES_CV, verbose_name='Category',
                                help_text='Strategic or Operational management body purpose.')

    def __unicode__(self):
        return "%s" % self.purpose
    
    class Meta:
        app_label = APPLICATION_LABEL


class ManagementBody(models.Model):
        
    title = models.CharField(max_length=200, blank=False, verbose_name='Title',
                             help_text='String used to succinctly describe an organizational body.')
    description = models.TextField(blank=False, verbose_name='Description',
                                   help_text='A short description providing extra information about organizational'
                                             ' body.')
    termsOfReference = models.TextField(blank=True, verbose_name='Terms of Reference',
                                        help_text='A description of the duties and responsibilities of the '
                                                  'organizational body.')
    purposes = models.ManyToManyField(ManagementBodyPurpose, blank=True)
    other = models.CharField(max_length=200, null=True, blank=True, verbose_name='Other Purpose',
                             help_text='Specify any other purpose(s) not included in the controlled vocabulary.')
    category = models.CharField(max_length=50, blank=True, null=False, default=MANAGEMENT_BODY_CATEGORY_STRATEGIC,
                                choices=MANAGEMENT_BODY_CATEGORIES_CV, verbose_name='Category',
                                help_text='Strategic or Operational management body purpose.')
    project = models.ForeignKey(Project)

    # sort list of members my last name and ignore case
    def members(self):
        member_list = self.managementbodymember_set.all()  # consists of a User object and ManagementBody object
        sorted_list = sorted(member_list, key=lambda _member: _member.user.last_name.lower())  # sort
        return sorted_list
    
    def get_all_purposes(self):
        """Merges the purposes from the controlled vocabulary with the other purposes."""
        purposes = list(self.purposes.all())
        if self.other is not None and len(self.other.strip()) > 0:
            purposes.append(self.other)
        #print purposes
        return purposes
    
    def set_category(self, dict={}):
        """Method to select the object category from the other fields. """
        
        for purpose in self.purposes.all():
            self.category = purpose.category

    def __unicode__(self):
        return "%s %s" % (self.project.short_name, self.title)
    
    class Meta:
        app_label = APPLICATION_LABEL


def getStrategicManagementBodies(project):
    """Returns the strategic management bodies for a given project."""
    return getManagementBodies(project, MANAGEMENT_BODY_CATEGORY_STRATEGIC)


def getOperationalManagementBodies(project):
    """Returns the operational management bodies for a given project."""
    return getManagementBodies(project, MANAGEMENT_BODY_CATEGORY_OPERATIONAL)


def getManagementBodies(project, category):
    """Returns a sorted list of a specific category of management bodies for a given project."""
    
    # transform QuerySet into list
    bodies = list(ManagementBody.objects.filter(project=project).filter(category=category))
    
    # sort by title
    return sorted(bodies, key=lambda body: body.title)


def initManagementBodyPurpose():
    """Function to populate the database with the necessary instances of ManagementBodyPurpose."""
    
    for purpose, order in STRATEGIC_MANAGEMENT_BODY_DICT.items():
        try:
            mbp = ManagementBodyPurpose.objects.get(purpose=purpose, category=MANAGEMENT_BODY_CATEGORY_STRATEGIC)
        except ManagementBodyPurpose.DoesNotExist:
            mbp = ManagementBodyPurpose(purpose=purpose, order=order, category=MANAGEMENT_BODY_CATEGORY_STRATEGIC)
            mbp.save()
            log.debug("Created management body purpose: %s" % mbp)
            
    for purpose, order in OPERATIONAL_MANAGEMENT_BODY_DICT.items():
        try:
            mbp = ManagementBodyPurpose.objects.get(purpose=purpose, category=MANAGEMENT_BODY_CATEGORY_OPERATIONAL)
        except ManagementBodyPurpose.DoesNotExist:
            mbp = ManagementBodyPurpose(purpose=purpose, order=order, category=MANAGEMENT_BODY_CATEGORY_OPERATIONAL)
            mbp.save()
            log.debug("Created management body purpose: %s" % mbp)