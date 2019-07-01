from django.db import models
from .constants import APPLICATION_LABEL, PURPOSE_CV, COMMUNICATION_CV, MEMBERSHIP_CV
from .project import Project


class CommunicationMeans(models.Model):
        
    title = models.CharField(max_length=200, blank=False, verbose_name='Title',
                             help_text='String used to describe the name of the meeting.')
    frequency = models.CharField(max_length=50, blank=True, null='True', verbose_name='Frequency',
                                 help_text='String used to describe the frequency of the meeting '
                                           '(e.g. Weekly on Wednesdays, Monthly, Yearly, ...).')
    type = models.CharField(max_length=50, blank=False, choices=COMMUNICATION_CV, verbose_name='Type',
                            help_text='String used to describe the type of meeting (choose from controlled '
                                      'vocabulary).')
    purpose = models.CharField(max_length=50, blank=True, null=True, choices=PURPOSE_CV, verbose_name='Purpose',
                               help_text='Purpose of meeting (choose from controlled vocabulary).')
    #membership = models.BooleanField(blank=True, verbose_name='Open Membership', help_text='A boolean that indicates
    # whether the means is open or closed to non-members')
    membership = models.CharField(max_length=50, blank=True, null=True, choices=MEMBERSHIP_CV,
                                  verbose_name='Membership', help_text='A field that indicates whether the means is '
                                                                       'open or closed to non-members.')
    participationDetails = models.TextField(blank=True, null=True, verbose_name='Participation Details',
                                            help_text='Information about how a person would participate: phone number, '
                                                      'pass code, meeting venue, etc.')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    # opt-out privacy option
    internal = models.BooleanField(default=True, null=False)
    
    def members(self):
        return self.communicationmeansmember_set.all()
    
    def set_category(self, dict={}):
        """Method to select the object 'internal' field."""
        
        self.internal = dict['internal']

    def __unicode__(self):
        return "%s %s" % (self.project.short_name, self.title)
    
    class Meta:
        app_label = APPLICATION_LABEL
