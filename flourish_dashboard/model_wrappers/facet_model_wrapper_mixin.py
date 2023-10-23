from edc_base.utils import relativedelta
from django.apps import apps as django_apps
from edc_constants.constants import YES
from edc_base.utils import get_utcnow, age
from .facet_consent_model_wrapper import FacetConsentModelWrapper
from .facet_screening_model_wrapper import FacetScreeningModelWrapper
from ..utils import flourish_dashboard_utils


class FacetModelWrapperMixin:

    facet_screening_model = 'flourish_facet.facetsubjectscreening'

    facet_consent_model = 'flourish_facet.facetconsent'

    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'

    antenatal_screening_model = 'flourish_caregiver.screeningpregwomen'

    @property
    def caregiver_child_consent_model_cls(self):
        return django_apps.get_model(self.caregiver_child_consent_model)

    @property
    def antenatal_screening_model_cls(self):
        return django_apps.get_model(self.antenatal_screening_model)

    @property
    def facet_screening_cls(self):
        return django_apps.get_model(self.facet_screening_model)

    @property
    def facet_consent_cls(self):
        return django_apps.get_model(self.facet_consent_model)

    @property
    def facet_screening_obj(self):
        try:
            screen_obj = self.facet_screening_cls.objects.get(
                subject_identifier=self.subject_identifier)

        except self.facet_screening_cls.DoesNotExist:
            pass
        else:
            return screen_obj

    @property
    def facet_consent_obj(self):
        try:
            screen_obj = self.facet_consent_cls.objects.get(
                subject_identifier=self.subject_identifier)

        except self.facet_consent_cls.DoesNotExist:
            pass
        else:
            return screen_obj

    @property
    def caregiver_child_consent_objs(self):
        return self.caregiver_child_consent_model_cls.objects.filter(
            subject_consent__subject_identifier=self.subject_identifier,
            preg_enroll=True)

    @property
    def antenatal_screening_obj(self):
        try:
            antenatal_screening_obj = self.antenatal_screening_model_cls.objects.get(
                screening_identifier=self.screening_identifier)
        except self.antenatal_screening_model_cls.DoesNotExist:
            pass
        else:
            return antenatal_screening_obj

    @property
    def facet_consent_wrapper(self):
        consent_obj = self.facet_consent_obj or self.facet_consent_cls(
            subject_identifier=self.subject_identifier)

        return FacetConsentModelWrapper(model_obj=consent_obj)

    @property
    def facet_screening_wrapper(self):
        screening_obj = self.facet_screening_obj or self.facet_screening_cls(
            subject_identifier=self.subject_identifier)

        return FacetScreeningModelWrapper(model_obj=screening_obj)

    @property
    def show_facet_consent(self):
        return self.facet_screening_obj and self.facet_screening_obj.is_eligible

    @property
    def show_facet_screening(self):
        """
        Condition for showing screening
        """
        for child_consent in self.caregiver_child_consent_objs:
            child_age = relativedelta(years=0, months=0, days=0)

            if child_consent.child_dob:
                child_age = age(child_consent.child_dob, get_utcnow().date())

            age_is_within = False

            if child_age.years == 0:
                if child_age.months < 6:
                    age_is_within = True
                elif child_age.months == 6 and child_age.days <= 10:
                    age_is_within = True
            if self.antenatal_screening_obj and age_is_within:
                return child_consent.subject_consent.future_contact == YES
