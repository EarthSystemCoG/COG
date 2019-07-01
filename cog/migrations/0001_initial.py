# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import cog.models.doc


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(max_length=1000, verbose_name=b'URL')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(max_length=200, null=True, blank=True)),
                ('order', models.IntegerField(default=0, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Collaborator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(default=b'', max_length=100)),
                ('last_name', models.CharField(default=b'', max_length=100)),
                ('institution', models.CharField(default=b'', max_length=100)),
                ('researchKeywords', models.CharField(default=b'', max_length=60, null=True, blank=True)),
                ('image', models.ImageField(null=True, upload_to=b'photos/', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CommunicationMeans',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text=b'String used to describe the name of the meeting.', max_length=200, verbose_name=b'Title')),
                ('frequency', models.CharField(help_text=b'String used to describe the frequency of the meeting (e.g. Weekly on Wednesdays, Monthly, Yearly, ...).', max_length=50, null=b'True', verbose_name=b'Frequency', blank=True)),
                ('type', models.CharField(help_text=b'String used to describe the type of meeting (choose from controlled vocabulary).', max_length=50, verbose_name=b'Type', choices=[(b'Telco', b'Telco'), (b'Face-to-face', b'Face-to-face'), (b'Webinar', b'Webinar'), (b'Video Conference', b'Video Conference'), (b'Internet Chat', b'Internet Chat'), (b'Wiki', b'Wiki'), (b'Mailing List', b'Mailing List')])),
                ('purpose', models.CharField(choices=[(b'Overall Project Coordination', b'Overall Project Coordination'), (b'Steering Committee', b'Steering Committee'), (b'Design', b'Design'), (b'Design and Implementation Review', b'Design and Implementation Review'), (b'Task Prioritization', b'Task Prioritization'), (b'Requirements Identification', b'Requirements Identification'), (b'Strategic Direction', b'Strategic Direction'), (b'External Review', b'External Review'), (b'Implementation', b'Implementation'), (b'Meeting Planning', b'Meeting Planning'), (b'Testing', b'Testing'), (b'Knowledge Transfer', b'Knowledge Transfer'), (b'Grant Writing', b'Grant Writing'), (b'Other', b'Other')], max_length=50, blank=True, help_text=b'Purpose of meeting (choose from controlled vocabulary).', null=True, verbose_name=b'Purpose')),
                ('membership', models.CharField(choices=[(b'Open', b'Open'), (b'Closed', b'Closed'), (b'By Invitation', b'By Invitation')], max_length=50, blank=True, help_text=b'A field that indicates whether the means is open or closed to non-members.', null=True, verbose_name=b'Membership')),
                ('participationDetails', models.TextField(help_text=b'Information about how a person would participate: phone number, pass code, meeting venue, etc.', null=True, verbose_name=b'Participation Details', blank=True)),
                ('internal', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='CommunicationMeansMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('communicationMeans', models.ForeignKey(to='cog.CommunicationMeans', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='DataCart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(related_name='datacart', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='DataCartItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(max_length=200)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Time')),
                ('cart', models.ForeignKey(related_name='items', to='cog.DataCart', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='DataCartItemMetadataKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=200)),
                ('item', models.ForeignKey(related_name='keys', to='cog.DataCartItem', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='DataCartItemMetadataValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=1000, null=True, blank=True)),
                ('key', models.ForeignKey(related_name='values', to='cog.DataCartItemMetadataKey', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Doc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, blank=True)),
                ('path', models.CharField(max_length=400, blank=True)),
                ('description', models.TextField(blank=True)),
                ('file', models.FileField(storage=cog.models.doc.OverridingFileStorage(), max_length=400, upload_to=cog.models.doc.get_upload_path)),
                ('publication_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Published')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name=b'Date Updated')),
                ('is_private', models.BooleanField(default=False, verbose_name=b'Private?')),
                ('author', models.ForeignKey(related_name='documents', on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'Publisher', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExternalUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name=b'Title')),
                ('description', models.CharField(max_length=1000, blank=True)),
                ('url', models.URLField(max_length=1000, verbose_name=b'URL')),
                ('type', models.CharField(max_length=20, verbose_name=b'URL Type', choices=[(b'blog', b'Blog'), (b'repository', b'Repositories'), (b'homepage', b'Home Page'), (b'reference', b'Reference'), (b'tracker', b'Trackers'), (b'usecase', b'Use Cases'), (b'policy', b' Policies'), (b'roadmaps', b'Roadmaps'), (b'download', b'Download / Releases'), (b'admin_docs', b'Install / Admin Docs'), (b'user_docs', b'User Docs'), (b'faq', b'FAQ'), (b'code_example', b'Code Examples'), (b'dev_docs', b'Dev Docs'), (b'testing', b'Testing'), (b'checklist', b'Checklists'), (b'prioritization', b'Prioritization'), (b'metric', b'Metrics'), (b'release_schedule', b'Release Schedules')])),
            ],
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('active', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0, blank=True)),
                ('parent', models.ForeignKey(related_name='parent_folder', blank=True, to='cog.Folder', null=True, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='ForumThread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name=b'SubTitle')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Created')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name=b'Date Updated')),
                ('author', models.ForeignKey(related_name='threads', on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'Author', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ForumTopic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name=b'Title')),
                ('description', models.TextField(verbose_name=b'Description', blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Created')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name=b'Date Updated')),
                ('is_private', models.BooleanField(default=False, verbose_name=b'Private?')),
                ('order', models.IntegerField(default=0, blank=True)),
                ('author', models.ForeignKey(related_name='forum_topics', on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'Author', to=settings.AUTH_USER_MODEL, null=True)),
                ('forum', models.ForeignKey(related_name='topics', to='cog.Forum', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='FundingSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Organization or agency that financially supports the project', max_length=200)),
                ('url', models.URLField(help_text=b'Funding Source URL', null=True, blank=True)),
                ('image', models.ImageField(null=True, upload_to=b'logos/', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Lock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_type', models.CharField(max_length=100, verbose_name=b'Object Type')),
                ('object_id', models.IntegerField(verbose_name=b'Object Identifier')),
                ('timestamp', models.DateTimeField(auto_now=True, verbose_name=b'Last Update Date')),
                ('owner', models.ForeignKey(verbose_name=b'Owner', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='LoggedEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('url', models.URLField(blank=True)),
                ('update_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Time')),
                ('sender', models.CharField(max_length=200, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ManagementBody',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text=b'String used to succinctly describe an organizational body.', max_length=200, verbose_name=b'Title')),
                ('description', models.TextField(help_text=b'A short description providing extra information about organizational body.', verbose_name=b'Description')),
                ('termsOfReference', models.TextField(help_text=b'A description of the duties and responsibilities of the organizational body.', verbose_name=b'Terms of Reference', blank=True)),
                ('other', models.CharField(help_text=b'Specify any other purpose(s) not included in the controlled vocabulary.', max_length=200, null=True, verbose_name=b'Other Purpose', blank=True)),
                ('category', models.CharField(default=b'Strategic', choices=[(b'Strategic', b'Strategic'), (b'Operational', b'Operational')], max_length=50, blank=True, help_text=b'Strategic or Operational management body purpose.', verbose_name=b'Category')),
            ],
        ),
        migrations.CreateModel(
            name='ManagementBodyMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('managementBody', models.ForeignKey(to='cog.ManagementBody', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='ManagementBodyPurpose',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('purpose', models.CharField(default=b'Other', help_text=b'Type of organizational body (choose from controlled vocabulary).', max_length=50, verbose_name=b'Purpose/Role', choices=[(b'Strategic Direction', b' Strategic Direction (Strategic)'), (b'Advice or Guidance', b' Advice or Guidance (Strategic)'), (b'Program Direction', b' Program Direction (Strategic)'), (b'Review', b' Review (Strategic)'), (b'Research', b' Research (Operational)'), (b'Development', b' Development (Operational)'), (b'Requirements Identification', b' Requirements Identification (Operational)'), (b'Task Prioritization', b' Task Prioritization (Operational)'), (b'Testing', b' Testing (Operational)'), (b'Review', b' Review (Operational)'), (b'Meeting and Event Planning', b' Meeting and Event Planning (Operational)'), (b'Administration', b' Administration (Operational)')])),
                ('order', models.IntegerField(default=0, blank=True)),
                ('category', models.CharField(default=b'Strategic', help_text=b'Strategic or Operational management body purpose.', max_length=50, verbose_name=b'Category', choices=[(b'Strategic', b'Strategic'), (b'Operational', b'Operational')])),
            ],
        ),
        migrations.CreateModel(
            name='MembershipRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now=True, verbose_name=b'Request Date')),
                ('group', models.ForeignKey(to='auth.Group', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('text', models.TextField()),
                ('publication_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Published')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name=b'Date Updated')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Project or organization that collaborates on this project', max_length=200)),
                ('url', models.URLField(help_text=b'Organization URL', null=True, blank=True)),
                ('image', models.ImageField(null=True, upload_to=b'logos/', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationalRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default=b'', help_text=b'Type of organizational role (choose from controlled vocabulary).', max_length=50, verbose_name=b'Type', choices=[(b'Principal Investigator', b' Principal Investigator (Lead Role)'), (b'Co-Investigator', b' Co-Investigator (Lead Role)'), (b'Program Manager', b' Program Manager (Lead Role)'), (b'Project Manager', b' Project Manager (Lead Role)'), (b'Software Architect', b' Software Architect (Lead Role)'), (b'Lead', b' Lead (Lead Role)'), (b'Other Lead', b' Other Lead (Lead Role)'), (b'', b'--------------'), (b'Administrative Assistant', b' Administrative Assistant (Member Role)'), (b'Data Manager', b' Data Manager (Member Role)'), (b'Outreach Coordinator', b' Outreach Coordinator (Member Role)'), (b'Researcher', b' Researcher (Member Role)'), (b'Software Developer', b' Software Developer (Member Role)'), (b'Webmaster', b' Webmaster (Member Role)'), (b'Other Member', b' Other Member (Member Role)')])),
                ('title', models.CharField(help_text=b'Optional string used to succinctly describe an organizational role.', max_length=200, null=True, verbose_name=b'Title', blank=True)),
                ('description', models.TextField(help_text=b'Long description providing extra information about an organizational role.', null=True, verbose_name=b'Description', blank=True)),
                ('category', models.CharField(default=b'Member', choices=[(b'Lead', b'Lead'), (b'Member', b'Member')], max_length=50, blank=True, help_text=b'Lead or Member role.', verbose_name=b'Category')),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationalRoleMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('organizationalRole', models.ForeignKey(to='cog.OrganizationalRole', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='PeerSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enabled', models.BooleanField(default=False)),
                ('site', models.OneToOneField(related_name='peersite', to='sites.Site', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name=b'Title')),
                ('label', models.CharField(help_text=b'Short index label', max_length=25, null=True, verbose_name=b'Label', blank=True)),
                ('body', models.TextField(default=b'', verbose_name=b'Content', blank=True)),
                ('publication_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Published')),
                ('update_date', models.DateTimeField(verbose_name=b'Date Updated')),
                ('order', models.IntegerField(default=0, blank=True)),
                ('type', models.CharField(max_length=10, verbose_name=b'Type', choices=[(b'blog', b'Blog'), (b'page', b'Page'), (b'notes', b'Notes')])),
                ('url', models.CharField(default=b'', unique=True, max_length=200, verbose_name=b'URL', blank=True)),
                ('template', models.CharField(max_length=200, verbose_name=b'Template', blank=True)),
                ('is_home', models.BooleanField(default=False, verbose_name=b'Is Home Page?')),
                ('is_private', models.BooleanField(default=False, verbose_name=b'Private?')),
                ('is_restricted', models.BooleanField(default=False, verbose_name=b'Restricted?')),
                ('version', models.IntegerField(default=1)),
                ('author', models.ForeignKey(related_name='posts', on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'Author', to=settings.AUTH_USER_MODEL, null=True)),
                ('docs', models.ManyToManyField(to='cog.Doc', verbose_name=b'Attachments', blank=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'Parent Post', blank=True, to='cog.Post', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', models.CharField(help_text=b"Short project acronym, 20 characters maximum, use only letters, numbers and '_', '-', no spaces.", unique=True, max_length=20)),
                ('long_name', models.CharField(help_text=b'Fully spelled project name.', unique=True, max_length=120)),
                ('description', models.TextField(help_text=b'A short paragraph that describes the project.', null=True)),
                ('mission', models.TextField(help_text=b'Succinctly describes why the project exists and what it does.', blank=True)),
                ('vision', models.TextField(help_text=b'Outlines what a project wants to be, or how it wants the world in which it operates to be. It is a long-term view.', blank=True)),
                ('values', models.TextField(help_text=b'Beliefs that are shared among the members of a project. Values influence culture and priorities and provide a framework for informing decisions.', blank=True)),
                ('history', models.TextField(help_text=b'A narrative describing the origination and evolution of the project.', blank=True)),
                ('external_homepage', models.URLField(help_text=b'External Home Page', null=True, blank=True)),
                ('governanceOverview', models.TextField(help_text=b'One or more paragraphs providing a general overview of the governance structure for the project.', null=True, verbose_name=b'Governance Overview', blank=True)),
                ('developmentOverview', models.TextField(help_text=b'One or more paragraphs providing a general overview of the development processes for the project.', null=True, verbose_name=b'Development Overview', blank=True)),
                ('taskPrioritizationStrategy', models.TextField(help_text=b'A paragraph describing how tasks are prioritized. This description may include who participates, how often they meet, how they meet, and whether the results are public.', null=True, verbose_name=b'Task Prioritization Strategy.', blank=True)),
                ('requirementsIdentificationProcess', models.TextField(help_text=b'A paragraph describing how requirements are identified. This description may include who participates, what system is used to track requirements, and whether the results are public.', null=True, verbose_name=b'Requirements Identification Process', blank=True)),
                ('software_features', models.TextField(help_text=None, null=True, verbose_name=b'Software Features', blank=True)),
                ('system_requirements', models.TextField(help_text=None, null=True, verbose_name=b'Software System Requirements', blank=True)),
                ('license', models.TextField(help_text=b'Name of license used for the software, if any.', null=True, verbose_name=b'License', blank=True)),
                ('implementationLanguage', models.TextField(help_text=b'The implementation language(s) of the software code.', null=True, verbose_name=b'Implementation Language', blank=True)),
                ('bindingLanguage', models.TextField(help_text=b'The binding language(s) of the software code.', null=True, verbose_name=b'Binding Language', blank=True)),
                ('supportedPlatforms', models.TextField(help_text=b'The computing platforms that the software can run on.', null=True, verbose_name=b'Supported Platforms', blank=True)),
                ('externalDependencies', models.TextField(help_text=b'The major libraries and packages the software depends on.', null=True, verbose_name=b'External Dependencies', blank=True)),
                ('getting_started', models.TextField(help_text=b'Describe how users can get started with this project.', null=True, verbose_name=b'Getting Started', blank=True)),
                ('projectContacts', models.TextField(default=b'', help_text=b'Describe how to contact the project.', null=True, verbose_name=b'Project Contacts', blank=True)),
                ('technicalSupport', models.TextField(help_text=b'Email address for technical questions.', null=True, verbose_name=b'Technical Support', blank=True)),
                ('meetingSupport', models.TextField(help_text=b'Describe how to setup meetings.', null=True, verbose_name=b'Meeting Support', blank=True)),
                ('getInvolved', models.TextField(help_text=b'Describe how to participate in the project.', null=True, verbose_name=b'Get Involved', blank=True)),
                ('active', models.BooleanField(default=False)),
                ('private', models.BooleanField(default=False)),
                ('logo', models.ImageField(null=True, upload_to=b'logos/', blank=True)),
                ('logo_url', models.CharField(help_text=b'Optional logo hyperlink URL.', max_length=200, null=True, blank=True)),
                ('dataSearchEnabled', models.BooleanField(default=False, help_text=b'Enable data search?')),
                ('forumNotificationEnabled', models.BooleanField(default=False, help_text=b'Enable forum notifications to project administrators ?')),
                ('maxUploadSize', models.IntegerField(default=52428800, help_text=b'Maximum upload size in bytes', blank=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('parents', models.ManyToManyField(related_name='parent_projects', to='cog.Project', blank=True)),
                ('peers', models.ManyToManyField(related_name='peer_projects', to='cog.Project', blank=True)),
                ('site', models.ForeignKey(default=1, to='sites.Site', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectImpact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', help_text=b'Title for this impact.', max_length=200)),
                ('description', models.TextField(help_text=b'Describe a major impact of this project in its field.', verbose_name=b'Project Impact')),
                ('order', models.IntegerField(blank=True)),
                ('project', models.ForeignKey(related_name='impacts', to='cog.Project', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectTab',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(default=b'', unique=True, max_length=200, verbose_name=b'URL', blank=True)),
                ('label', models.CharField(max_length=40)),
                ('active', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(blank=True, to='cog.ProjectTab', null=True, on_delete=models.CASCADE)),
                ('project', models.ForeignKey(related_name='tabs', to='cog.Project', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=20, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectTopic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0)),
                ('project', models.ForeignKey(to='cog.Project', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='SearchFacet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=40)),
                ('label', models.CharField(max_length=40)),
                ('order', models.IntegerField(default=0, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SearchGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'default', max_length=40)),
                ('order', models.IntegerField(default=0, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SearchProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('constraints', models.CharField(default=b'', max_length=500, null=True, blank=True)),
                ('modelMetadataFlag', models.BooleanField(default=False)),
                ('replicaSearchFlag', models.BooleanField(default=False)),
                ('latestSearchFlag', models.BooleanField(default=False)),
                ('localSearchFlag', models.BooleanField(default=False)),
                ('description', models.TextField(help_text=b'Optional description of this project search capabilities.', null=True, verbose_name=b'Search Help', blank=True)),
                ('project', models.OneToOneField(to='cog.Project', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'Name')),
                ('description', models.TextField(verbose_name=b'Description', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('institution', models.CharField(default=b'', max_length=100)),
                ('city', models.CharField(default=b'', max_length=100)),
                ('country', models.CharField(default=b'', max_length=100)),
                ('state', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('department', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('subscribed', models.BooleanField(default=True, verbose_name=b'Subscribe to COG mailing list?')),
                ('private', models.BooleanField(default=False, verbose_name=b'Do NOT list me among project members')),
                ('image', models.ImageField(null=True, upload_to=b'photos/', blank=True)),
                ('researchInterests', models.CharField(default=b'', max_length=1000, null=True, blank=True)),
                ('researchKeywords', models.CharField(default=b'', max_length=60, null=True, blank=True)),
                ('type', models.IntegerField(default=1)),
                ('last_password_update', models.DateTimeField(null=True, verbose_name=b'Date and Time when Password was Last Updated', blank=True)),
                ('site', models.ForeignKey(default=1, to='sites.Site', on_delete=models.CASCADE)),
                ('tags', models.ManyToManyField(related_name='users', to='cog.ProjectTag', blank=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='UserUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(max_length=1000, verbose_name=b'URL')),
                ('name', models.CharField(max_length=200)),
                ('profile', models.ForeignKey(to='cog.UserProfile', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='searchgroup',
            name='profile',
            field=models.ForeignKey(related_name='groups', to='cog.SearchProfile', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='searchfacet',
            name='group',
            field=models.ForeignKey(related_name='facets', to='cog.SearchGroup', null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='projecttopic',
            name='topic',
            field=models.ForeignKey(to='cog.Topic', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='project',
            name='tags',
            field=models.ManyToManyField(related_name='projects', to='cog.ProjectTag', blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='topics',
            field=models.ManyToManyField(to='cog.Topic', through='cog.ProjectTopic', blank=True),
        ),
        migrations.AddField(
            model_name='post',
            name='project',
            field=models.ForeignKey(to='cog.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='post',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='cog.Topic', null=True),
        ),
        migrations.AddField(
            model_name='organizationalrole',
            name='project',
            field=models.ForeignKey(to='cog.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='organization',
            name='project',
            field=models.ForeignKey(to='cog.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='news',
            name='other_projects',
            field=models.ManyToManyField(related_name='other_news', verbose_name=b'Projects Notified', to='cog.Project', blank=True),
        ),
        migrations.AddField(
            model_name='news',
            name='project',
            field=models.ForeignKey(verbose_name=b'About Project', to='cog.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='managementbody',
            name='project',
            field=models.ForeignKey(to='cog.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='managementbody',
            name='purposes',
            field=models.ManyToManyField(to='cog.ManagementBodyPurpose', blank=True),
        ),
        migrations.AddField(
            model_name='loggedevent',
            name='project',
            field=models.ForeignKey(to='cog.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='loggedevent',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='fundingsource',
            name='project',
            field=models.ForeignKey(to='cog.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='forumthread',
            name='topic',
            field=models.ForeignKey(related_name='threads', to='cog.ForumTopic', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='forum',
            name='project',
            field=models.OneToOneField(related_name='forum', to='cog.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='folder',
            name='project',
            field=models.ForeignKey(to='cog.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='externalurl',
            name='project',
            field=models.ForeignKey(to='cog.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='doc',
            name='project',
            field=models.ForeignKey(to='cog.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='communicationmeans',
            name='project',
            field=models.ForeignKey(to='cog.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='collaborator',
            name='project',
            field=models.ForeignKey(to='cog.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='bookmark',
            name='folder',
            field=models.ForeignKey(to='cog.Folder', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='bookmark',
            name='notes',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='cog.Post', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='organizationalrolemember',
            unique_together=set([('user', 'organizationalRole')]),
        ),
        migrations.AlterUniqueTogether(
            name='membershiprequest',
            unique_together=set([('user', 'group')]),
        ),
        migrations.AlterUniqueTogether(
            name='managementbodymember',
            unique_together=set([('user', 'managementBody')]),
        ),
        migrations.AlterUniqueTogether(
            name='lock',
            unique_together=set([('object_type', 'object_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='folder',
            unique_together=set([('project', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='communicationmeansmember',
            unique_together=set([('user', 'communicationMeans')]),
        ),
    ]
