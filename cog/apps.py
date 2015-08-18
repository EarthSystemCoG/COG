from django.apps import AppConfig

class CogConfig(AppConfig):

    name = 'cog'
    verbose_name = "CoG Scientific Projects Web Environment"

    def ready(self):
        # nothing to do for now
        pass