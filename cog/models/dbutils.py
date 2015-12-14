from django.db import models

# utility class to allow creation of foreign key to instances that are NOT yet saved to the database
# this allow backward compatibility after changes made in django 1.8
class UnsavedForeignKey(models.ForeignKey):
   
    # a ForeignKey which can point to an unsaved object
    allow_unsaved_instance_assignment = True

