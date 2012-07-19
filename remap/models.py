from django.db import models
from django.forms import ModelForm
from os import listdir, path

from django.conf import settings

SRCGRID_DIR = getattr(settings, "SRCGRID_DIR", "/tmp")
DSTGRID_DIR = getattr(settings, "DSTGRID_DIR", "/tmp")
WEIGHTS_DIR = getattr(settings, "WEIGHTS_DIR", "/tmp")

METHOD_CHOICES = ( ("bilinear", "Bilinear"),
                   ("patch", "Patch"),
                   ("conserve", "Conservative")
                 );

def grids(grid_dir):
    choices = []
    try :
        filenames = listdir(grid_dir)
        for filename in filenames:
            filepath = path.join(grid_dir, filename)
            if (path.isfile(filepath) and filename[0] != '.'):
                #choices.append( (filepath, filename) )
                choices.append( (filename, filename) )
    except OSError:
        pass
    return choices

# object representing a remapping request
class RemapJob(models.Model):
    
    srcgrid = models.CharField('Input Source Grid', max_length=200, choices=grids(SRCGRID_DIR), null=False, blank=False )
    dstgrid = models.CharField('Input Destination Grid', max_length=200, choices=grids(DSTGRID_DIR), null=False, blank=False )
    weights = models.CharField('Output Weights', max_length=200, null=False)
    method  = models.CharField('Interpolation Method', max_length=50, null=False, blank=False, choices=METHOD_CHOICES, default=METHOD_CHOICES[0])
    
# form backed up by a RemapJob model
class RemapForm(ModelForm):
    class Meta:
        model = RemapJob
        # exclude weights so it is not validated when form is submitted
        exclude = ('weights')
