from django.conf import settings
from edc_navbar import NavbarItem, site_navbars, Navbar


no_url_namespace = True if settings.APP_NAME == 'flourish_dashboard' else False

flourish_dashboard = Navbar(name='flourish_dashboard')

flourish_dashboard.append_item(
    NavbarItem(
        name='maternal_dataset',
        title='Maternal Dataset',
        label='maternal dataset',
        fa_icon='far fa-user-circle',
        url_name=settings.DASHBOARD_URL_NAMES[
            'maternal_dataset_listboard_url'],
        no_url_namespace=no_url_namespace))

flourish_dashboard.append_item(
    NavbarItem(
        name='anc_screening',
        title='ANC Screening',
        label='anc screening',
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

flourish_dashboard.append_item(
    NavbarItem(
        name='child_subject',
        title='Child Subjects',
        label='child subjects',
        fa_icon='far fa-user-circle',
        url_name=settings.DASHBOARD_URL_NAMES[
            'child_listboard_url'],
        no_url_namespace=no_url_namespace))


site_navbars.register(flourish_dashboard)
