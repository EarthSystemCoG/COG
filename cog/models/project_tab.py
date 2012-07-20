from django.db import models
from constants import APPLICATION_LABEL, PROJECT_PAGES
from project import Project
from django.core.urlresolvers import reverse

# Tab displayed in project top navigation menu
class ProjectTab(models.Model):
        
    project = models.ForeignKey(Project, blank=False, null=False, related_name="tabs")
    # the URL of a corresponding project page
    url = models.CharField(max_length=200, verbose_name='URL', blank=True, unique=True, default='')
    # the label displayed in the menu
    label =  models.CharField(max_length=40, blank=False, null=False)
    # whether or not the tab will be displayed
    active = models.BooleanField(default=True, null=False, blank=False)
    # optional parent tab (null for top-level tabs)
    parent = models.ForeignKey('self', blank=True, null=True)
    
    def __unicode__(self):
        return "Project Tab label='%s', url='%s', active=%s" % (self.label, self.url, self.active)
    
    class Meta:
        app_label= APPLICATION_LABEL
        
# function to retrieve the project tabs in the display order
# the tabs can be optionally created if not existing already
# each item in the list is itself a list, containing the top-level tab, 
# followed by all sub-tabs
def get_or_create_project_tabs(project, save=True):
            
    tabs = []
    for pagelist in PROJECT_PAGES:
        tablist = []
        for i, page in enumerate(pagelist):
            # default values for label, url
            label = page[0]
            url = project.home_page_url() + page[1]
            if page[0]=="Home":
                # NESII Home
                label = "%s Home" % project.short_name                
            if page[0]=="Bookmarks" and len(project.short_name)>0:
                # use reverse lookup to obtain bookmarks/list/nesii/
                url = reverse('bookmark_list', args=[project.short_name.lower()])
            try:
                # try loading the project tab by its unique URL
                tab = ProjectTab.objects.get(url=url)
            except ProjectTab.DoesNotExist:
                # create the project tab if not existing already. 
                # select initial active state of tabs
                if page[0]=='Home' or page[0]=='About Us' or page[0]=='Contact Us':
                    active = True
                else:
                    active = False
                tab = ProjectTab(project=project, label=label, url=url, active=active)
                if save:
                    tab.save()      
                    print "Created %s" % tab
                    # assign parent tab
                    if i>0:
                        tab.parent = tablist[0]
                        tab.save()
                        print "Assigned parent tab=%s to child tab=%s" % (tablist[0], tab)

            tablist.append(tab)
        tabs.append(tablist)
    return tabs           