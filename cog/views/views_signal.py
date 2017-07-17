from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from cog.models import Project
from cog.views.utils import paginate


def signal_list(request, project_short_name):
    
    project = get_object_or_404(Project, short_name__iexact=project_short_name)

    # template in /templates/cog/signal
    return render(request,
                  'cog/signal/signal_list.html', 
                  {'project': project, 
                   'title': '%s Activity' % project.full_name(),
                   'project_signals': paginate(project.signals(), request, max_counts_per_page=10)})
