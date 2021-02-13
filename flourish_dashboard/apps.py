from django.apps import AppConfig as DjangoAppConfig



class AppConfig(DjangoAppConfig):
    name = 'flourish_dashboard'
    admin_site_name = 'flourish_caregiver_admin'

    def ready(self):
        from django.contrib.auth.models import Group
        Group.objects.create(name='locator users')
