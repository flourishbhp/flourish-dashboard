from django.apps import AppConfig as DjangoAppConfig



class AppConfig(DjangoAppConfig):
    name = 'flourish_dashboard'
    admin_site_name = 'flourish_caregiver_admin'

    def ready(self):
        from django.contrib.auth.models import Group
        try:
            Group.objects.get(name='locator users')
        except Group.DoesNotExist:
            Group.objects.create(name='locator users')
