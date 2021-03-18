from dateutil.relativedelta import relativedelta
from django.conf import settings
from edc_base.utils import get_utcnow
from edc_model_wrapper import ModelWrapper

from .child_assent_model_wrapper_mixin import ChildAssentModelWrapperMixin
from .consent_model_wrapper_mixin import ConsentModelWrapperMixin


class ChildDummyConsentModelWrapper(ChildAssentModelWrapperMixin,
                                    ConsentModelWrapperMixin,
                                    ModelWrapper):

    model = 'flourish_child.childdummysubjectconsent'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'child_listboard_url')
    next_url_attrs = ['subject_identifier', 'screening_identifier']
    querystring_attrs = ['subject_identifier', 'screening_identifier']

    @property
    def screening_identifier(self):
        subject_consent = self.subject_consent_cls.objects.get(
            subject_identifier=self.subject_identifier)
        return subject_consent.screening_identifier

    @property
    def assent_options(self):
        """Returns a dictionary of options to get an existing
         child assent model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
            version=self.version)
        return options

    @property
    def consent_options(self):
        """Returns a dictionary of options to get an existing
        consent model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier,
            version=self.consent_version)
        return options

    @property
    def subject_identifier(self):
        subject_identifier = self.object.subject_identifier.split('-')
        subject_identifier.pop()
        caregiver_subject_identifier = '-'.join(subject_identifier)
        return caregiver_subject_identifier

    @property
    def child_age(self):
        if getattr(self, 'assent_model_obj'):
            birth_date = self.assent_model_obj.dob
            difference = relativedelta(get_utcnow().date(), birth_date)
            months = 0
            if difference.years > 0:
                months = difference.years * 12
            years = round((months + difference.months) / 12, 2)
            return years
        return 0
