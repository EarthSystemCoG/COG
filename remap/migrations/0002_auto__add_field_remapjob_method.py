# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'RemapJob.method'
        db.add_column('remap_remapjob', 'method', self.gf('django.db.models.fields.CharField')(default=('Bilinear', 'bilinear'), max_length=50), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'RemapJob.method'
        db.delete_column('remap_remapjob', 'method')


    models = {
        'remap.remapjob': {
            'Meta': {'object_name': 'RemapJob'},
            'dstgrid': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'default': "('Bilinear', 'bilinear')", 'max_length': '50'}),
            'srcgrid': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'weights': ('django.db.models.fields.CharField', [], {'default': "'/Users/cinquini/junk/weights'", 'max_length': '200'})
        }
    }

    complete_apps = ['remap']
