from math import modf
from datetime import date
from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django.conf import settings
from edc_base.utils import get_utcnow
from edc_model_wrapper import ModelWrapper

from flourish_caregiver.helper_classes.utils import cohort_assigned

from .child_assent_model_wrapper_mixin import ChildAssentModelWrapperMixin
from .child_birth_model_wrapper_mixin import ChildBirthModelWrapperMixin
from .child_death_report_model_wrapper_mixin import \
    ChildDeathReportModelWrapperMixin
from .child_dummy_consent_model_wrapper_mixin import \
    ChildDummyConsentModelWrapperMixin
from .child_offstudy_model_wrapper_mixin import ChildOffstudyModelWrapperMixin
from .consent_model_wrapper_mixin import ConsentModelWrapperMixin


class ChildDummyConsentModelWrapper(ChildDummyConsentModelWrapperMixin,
                                    ChildAssentModelWrapperMixin,
                                    ConsentModelWrapperMixin,
                                    ChildBirthModelWrapperMixin,
                                    ChildOffstudyModelWrapperMixin,
                                    ChildDeathReportModelWrapperMixin,
                                    ModelWrapper):
    model = 'flourish_child.childdummysubjectconsent'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'child_listboard_url')
    next_url_attrs = ['subject_identifier', 'screening_identifier']
    querystring_attrs = ['subject_identifier', 'screening_identifier']

    def has_fu_visit(self, cohort_name):
        cs_model_cls = django_apps.get_model(
            'flourish_caregiver.cohortschedules')

        schedule_names = cs_model_cls.objects.filter(
            cohort_name=cohort_name,
            schedule_type__in=['followup', 'sq_followup'],
            child_count__isnull=True).values_list('schedule_name', flat=True)

        visit_model_cls = django_apps.get_model(
            f'flourish_child.childvisit')

        return visit_model_cls.objects.filter(
            subject_identifier=self.object.subject_identifier,
            schedule_name__in=schedule_names).exists()

    @property
    def eligible_for_protocol_completion(self):
        is_eligible = True
        cohort_upper = {
            'cohort_a': 5.0833,
            'cohort_a_sec': 5.0833,
            'cohort_b': 10.0833,
            'cohort_b_sec': 10.0833}

        current_cohort = self.cohort_model_obj({
            'subject_identifier': self.object.subject_identifier,
            'current_cohort': True, })
        cohort_name = current_cohort.name
        study_child_id = self.child_consent.study_child_identifier
        child_dob = self.child_consent.child_dob

        today = get_utcnow().date()
        cutoff_date = date(2025, 6, 20)

        _cohort = cohort_assigned(study_child_id, child_dob, today)
        if _cohort and _cohort != cohort_name:
            cohort_name = _cohort

        age_now = current_cohort.child_age
        cohort_age = cohort_upper.get(current_cohort.name, None)
        if cohort_age and age_now < cohort_age:
            age_diff = cohort_age - age_now

            fractional_year, whole_years = modf(age_diff)
            whole_years = int(whole_years)
            months = int(round(fractional_year * 12))

            projected_date = today + relativedelta(years=whole_years, months=months)
            projected_cohort = None
            if projected_date > today and projected_date < cutoff_date:
                projected_cohort = cohort_assigned(
                    study_child_id, child_dob, projected_date)

            if projected_cohort and projected_cohort != cohort_name:
                cohort_name = projected_cohort

        if 'sec' not in cohort_name and not self.has_fu_visit(cohort_name):
            is_eligible = False
            if cohort_name == 'cohort_a':
                age_at_cutoff = current_cohort.child_age_at_date(cutoff_date)
                is_eligible = (age_at_cutoff * 12) < 18

        return is_eligible
