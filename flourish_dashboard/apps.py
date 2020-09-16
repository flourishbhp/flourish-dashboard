from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'flourish_dashboard'
    admin_site_name = 'flourish_maternal_admin'
