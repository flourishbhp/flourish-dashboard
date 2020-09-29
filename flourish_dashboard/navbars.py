from django.conf import settings
from edc_navbar import NavbarItem, site_navbars, Navbar


no_url_namespace = True if settings.APP_NAME == 'flourish_dashboard' else False

flourish_dashboard = Navbar(name='flourish_dashboard')

flourish_dashboard.append_item(
    NavbarItem(
        name='maternal_datasett',
        title='Maternal Dataset',
        label='maternal dataset',
        fa_icon='far fa-user-circle',
        url_name=settings.DASHBOARD_URL_NAMES[
            'maternal_dataset_listboard_url'],
        no_url_namespace=no_url_namespace))

flourish_dashboard.append_item(
    NavbarItem(
        name='maternal_screening',
        title='Maternal Screening',
        label='maternal screening',
        fa_icon='far fa-user-circle',
        url_name=settings.DASHBOARD_URL_NAMES[
            'maternal_screening_listboard_url'],
        no_url_namespace=no_url_namespace))

flourish_dashboard.append_item(
    NavbarItem(
        name='consented_subject',
        title='Maternal Subjects',
        label='maternal subjects',
        fa_icon='far fa-user-circle',
        url_name=settings.DASHBOARD_URL_NAMES[
            'subject_listboard_url'],
        no_url_namespace=no_url_namespace))

site_navbars.register(flourish_dashboard)
