from django.conf import settings
from django.apps import apps as django_apps

from edc_model_wrapper import ModelWrapper


class CaregiverContactModelWrapper(ModelWrapper):

    model = 'flourish_caregiver.caregivercontact'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_dashboard_url')
    next_url_attrs = ['subject_identifier']
    querystring_attrs = ['subject_identifier', 'study_name']

    @staticmethod
    def contact_details_exist(subject_identifier):
        """
        Helper method, to check if any contact details exist since one
        participant can have more than one contact details
        """
        contact_details_cls = django_apps.get_model(
            'flourish_caregiver.caregivercontact')

        return contact_details_cls.objects.filter(
            subject_identifier=subject_identifier).exists()
