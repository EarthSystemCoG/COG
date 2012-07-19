# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'RemapJob'
        db.create_table('remap_remapjob', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('srcgrid', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('dstgrid', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('weights', self.gf('django.db.models.fields.CharField')(default='/Users/cinquini/junk/weights', max_length=200)),
        ))
        db.send_create_signal('remap', ['RemapJob'])


    def backwards(self, orm):
        
        # Deleting model 'RemapJob'
        db.delete_table('remap_remapjob')


    models = {
        'remap.remapjob': {
            'Meta': {'object_name': 'RemapJob'},
            'dstgrid': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'srcgrid': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'weights': ('django.db.models.fields.CharField', [], {'default': "'/Users/cinquini/junk/weights'", 'max_length': '200'})
        }
    }

    complete_apps = ['remap']
