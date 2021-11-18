# from flourish_dashboard.model_wrappers.infant_death_report_model_wrapper import InfantDeathReportModelWrapper
# # from flourish_prn.action_items import CHILD_DEATH_REPORT_ACTION

from dateutil import relativedelta
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.generic.base import ContextMixin
from edc_base.utils import get_utcnow
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from edc_dashboard.views import DashboardView as BaseDashboardView
from edc_data_manager.model_wrappers import DataActionItemModelWrapper
from edc_subject_dashboard.view_mixins import SubjectDashboardViewMixin
from edc_registration.models import RegisteredSubject
from flourish_prn.action_items import CHILDOFF_STUDY_ACTION

from ...view_mixin import DashboardViewMixin
from ....model_wrappers import (
    ChildAppointmentModelWrapper, ChildDummyConsentModelWrapper,
    ChildCrfModelWrapper, ChildOffstudyModelWrapper,
    ChildVisitModelWrapper, CaregiverLocatorModelWrapper,
    ActionItemModelWrapper, CaregiverChildConsentModelWrapper,
    ChildDatasetModelWrapper, MaternalRegisteredSubjectModelWrapper)


class ChildBirthValues(object):

    subject_consent_cls = django_apps.get_model('flourish_caregiver.subjectconsent')
    maternal_delivery_cls = django_apps.get_model('flourish_caregiver.maternaldelivery')
    child_consent_cls = django_apps.get_model('flourish_caregiver.caregiverchildconsent')

    def __init__(self, subject_identifier=None):
        self.subject_identifier = subject_identifier

    def get_difference(self, birth_date=None):
        difference = relativedelta.relativedelta(
            get_utcnow().date(), birth_date)
        months = 0
        if difference.years > 0:
            months = difference.years * 12
        return months + difference.months

    @property
    def subject_consent_obj(self):
        """Returns a child birth model instance or None.
        """
        subject_identifier = self.subject_identifier.split('-')
        subject_identifier.pop()
        caregiver_subject_identifier = '-'.join(subject_identifier)
        try:
            return self.subject_consent_cls.objects.get(
                subject_identifier=caregiver_subject_identifier)
        except ObjectDoesNotExist:
            return None

    @property
    def caregiver_child_consent_obj(self):
        """Returns a caregiver consent on behalf of child model instance or None.
        """
        try:
            return self.child_consent_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            return None

    @property
    def maternal_delivery_obj(self):
        """Returns a child birth model instance or None.
        """
        subject_identifier = self.subject_identifier.split('-')
        subject_identifier.pop()
        caregiver_subject_identifier = '-'.join(subject_identifier)
        try:
            return self.maternal_delivery_cls.objects.get(
                subject_identifier=caregiver_subject_identifier)
        except ObjectDoesNotExist:
            return None

    @property
    def child_age(self):
        if self.caregiver_child_consent_obj:
            birth_date = self.caregiver_child_consent_obj.child_dob
            return self.get_difference(birth_date)

        elif self.maternal_delivery_obj:
            birth_date_time = self.maternal_delivery_obj.delivery_datetime
            birth_date = birth_date_time.date()
            return self.get_difference(birth_date)

        return None

    @property
    def child_offstudy_cls(self):
        return django_apps.get_model('flourish_prn.childoffstudy')

    @property
    def child_offstudy_model_obj(self):
        """Returns a child offstudy model instance or None.
        """
        try:
            return self.child_offstudy_cls.objects.get(**self.child_offstudy_options)
        except ObjectDoesNotExist:
            return None

    @property
    def child_offstudy(self):
        """Returns a wrapped saved or unsaved infant offstudy.
        """
        model_obj = self.child_offstudy_model_obj or self.child_offstudy_cls(
            **self.child_offstudy_options)
        return ChildOffstudyModelWrapper(model_obj=model_obj)

    @property
    def child_offstudy_options(self):
        """Returns a dictionary of options to get an existing
        infant offstudy model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier)
        return options


class ChildBirthButtonCls(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        infant_birth_values = ChildBirthValues(
            subject_identifier=self.subject_identifier)
        context.update(
            infant_birth_values=infant_birth_values,)
        return context


class CaregiverRegisteredSubjectCls(ContextMixin):

    @property
    def caregiver_registered_subject(self):
        try:
            caregiver_registered_subject = RegisteredSubject.objects.get(
                subject_identifier=self.caregiver_subject_identifier)
        except RegisteredSubject.DoesNotExist:
            raise ValidationError(
                "Registered subject for the mother is expected to exist.")
        else:
            return MaternalRegisteredSubjectModelWrapper(
                caregiver_registered_subject)

    @property
    def caregiver_subject_identifier(self):
        subject_identifier = self.kwargs.get('subject_identifier').split('-')
        subject_identifier.pop()
        caregiver_subject_identifier = '-'.join(subject_identifier)
        return caregiver_subject_identifier

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            caregiver_registered_subject=self.caregiver_registered_subject)
        return context


class DashboardView(
        DashboardViewMixin, EdcBaseViewMixin, SubjectDashboardViewMixin,
        NavbarViewMixin, BaseDashboardView, ChildBirthButtonCls,
        CaregiverRegisteredSubjectCls):

    dashboard_url = 'child_dashboard_url'
    dashboard_template = 'child_subject_dashboard_template'
    appointment_model = 'flourish_child.appointment'
    appointment_model_wrapper_cls = ChildAppointmentModelWrapper
    crf_model_wrapper_cls = ChildCrfModelWrapper
    # requisition_model_wrapper_cls = None
    consent_model = 'flourish_child.childdummysubjectconsent'
    consent_model_wrapper_cls = ChildDummyConsentModelWrapper
    action_item_model_wrapper_cls = ActionItemModelWrapper
    navbar_name = 'flourish_dashboard'
    visit_attr = 'childvisit'
    navbar_selected_item = 'child_subject'
    visit_model_wrapper_cls = ChildVisitModelWrapper
    subject_locator_model = 'flourish_caregiver.caregiverlocator'
    subject_locator_model_wrapper_cls = CaregiverLocatorModelWrapper
    mother_infant_study = True
    infant_links = False
    maternal_links = True
    special_forms_include_value = 'flourish_dashboard/child_subject/dashboard/special_forms.html'
    maternal_dashboard_include_value = "flourish_dashboard/child_subject/dashboard/caregiver_dashboard_links.html"
    data_action_item_template = "flourish_dashboard/child_subject/dashboard/data_manager.html"

    @property
    def data_action_item(self):
        """Returns a wrapped saved or unsaved consent version.
        """
        model_cls = django_apps.get_model('edc_data_manager.dataactionitem')
        model_obj = model_cls(subject_identifier=self.subject_identifier)
        next_url = settings.DASHBOARD_URL_NAMES.get(
            'child_dashboard_url')
        model_wrapper = DataActionItemModelWrapper(model_obj=model_obj,
                                                   next_url_name=next_url)
        return model_wrapper

    @property
    def caregiver_child_consent(self):
        child_consent_cls = django_apps.get_model(
            'flourish_caregiver.caregiverchildconsent')
        try:
            child_consent = child_consent_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except child_consent_cls.DoesNotExist:
            return None
        else:
            return CaregiverChildConsentModelWrapper(child_consent)

    @property
    def prior_screening(self):
        bhp_prior_screening_cls = django_apps.get_model(
            'flourish_caregiver.screeningpriorbhpparticipants')
        try:
            bhp_prior = bhp_prior_screening_cls.objects.get(
                screening_identifier=self.consent_wrapped.screening_identifier)
        except bhp_prior_screening_cls.DoesNotExist:
            return None
        else:
            return bhp_prior

    @property
    def child_dataset(self):
        """Returns a wrapped child dataset obj
        """
        child_dataset_cls = django_apps.get_model(
            'flourish_child.childdataset')
        try:
            child_dataset = child_dataset_cls.objects.get(
                study_child_identifier=self.caregiver_child_consent.study_child_identifier)
        except child_dataset_cls.DoesNotExist:
            return None
        else:
            return ChildDatasetModelWrapper(child_dataset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        child_offstudy_cls = django_apps.get_model('flourish_prn.childoffstudy')
        child_visit_cls = django_apps.get_model('flourish_child.childvisit')
        # child_death_cls = None
        # infant_death_cls = django_apps.get_model('flourish_prn.childdeathreport')

        # self.update_messages(offstudy_cls=child_offstudy_cls)
        # self.get_death_or_message(visit_cls=child_visit_cls,
        #                           death_cls=child_death_cls)
        self.get_offstudy_or_message(visit_cls=child_visit_cls,
                                     offstudy_cls=child_offstudy_cls,
                                     offstudy_action=CHILDOFF_STUDY_ACTION)
        child_age = ChildBirthValues(
            subject_identifier=self.subject_identifier).child_age
        self.get_continued_consent_object_or_message(
            subject_identifier=self.subject_identifier, child_age=child_age)
        self.get_assent_object_or_message(
            subject_identifier=self.subject_identifier, child_age=child_age)
        context.update(
            caregiver_child_consent=self.caregiver_child_consent,
            gender=self.caregiver_child_consent.gender,
            child_dataset=self.child_dataset,
            schedule_names=[model.schedule_name for model in self.onschedule_models],

        )
        context = self.add_url_to_context(
            new_key='dashboard_url_name',
            existing_key=self.dashboard_url,
            context=context)
        return context

    def set_current_schedule(self, onschedule_model_obj=None,
                             schedule=None, visit_schedule=None,
                             is_onschedule=True):

        if onschedule_model_obj:
            if is_onschedule:
                self.current_schedule = schedule
                self.current_visit_schedule = visit_schedule
                self.current_onschedule_model = onschedule_model_obj
            self.onschedule_models.append(onschedule_model_obj)
            self.visit_schedules.update(
                {visit_schedule.name: visit_schedule})

    def get_onschedule_model_obj(self, schedule):
        try:
            return schedule.onschedule_model_cls.objects.get(
                subject_identifier=self.subject_identifier,
                schedule_name=schedule.name)
        except ObjectDoesNotExist:
            return None

    def get_subject_locator_or_message(self):
        """
        Overridden to stop system from generating subject locator
        action items for child.
        """
        pass
