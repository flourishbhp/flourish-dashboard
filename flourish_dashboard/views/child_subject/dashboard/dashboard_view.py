# from flourish_dashboard.model_wrappers.infant_death_report_model_wrapper
# import InfantDeathReportModelWrapper # from flourish_prn.action_items
# import CHILD_DEATH_REPORT_ACTION
from dateutil import relativedelta
from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.safestring import mark_safe
from django.views.generic.base import ContextMixin
from edc_base.utils import age
from edc_base.utils import get_utcnow
from edc_base.view_mixins import EdcBaseViewMixin
from edc_constants.constants import POS, YES
from edc_dashboard.views import DashboardView as BaseDashboardView
from edc_data_manager.model_wrappers import DataActionItemModelWrapper
from edc_navbar import NavbarViewMixin
from edc_registration.models import RegisteredSubject
from edc_subject_dashboard.view_mixins import SubjectDashboardViewMixin
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from flourish_caregiver.helper_classes import MaternalStatusHelper
from flourish_child.helper_classes.child_fu_onschedule_helper import \
    ChildFollowUpEnrolmentHelper
from flourish_child.helper_classes.child_onschedule_helper import ChildOnScheduleHelper
from flourish_prn.action_items import CHILDOFF_STUDY_ACTION
from ...view_mixin import DashboardViewMixin
from ....model_wrappers import (ActionItemModelWrapper, CaregiverChildConsentModelWrapper,
                                CaregiverLocatorModelWrapper,
                                ChildAppointmentModelWrapper, ChildCrfModelWrapper,
                                ChildDatasetModelWrapper, ChildDummyConsentModelWrapper,
                                ChildOffstudyModelWrapper, ChildRequisitionModelWrapper,
                                ChildVisitModelWrapper,
                                MaternalRegisteredSubjectModelWrapper,
                                TbAdolReferralModelWrapper)
from ....model_wrappers import YoungAdultLocatorModelWrapper


class ChildBirthValues(object):
    subject_consent_cls = django_apps.get_model(
        'flourish_caregiver.subjectconsent')
    maternal_delivery_cls = django_apps.get_model(
        'flourish_caregiver.maternaldelivery')
    child_consent_cls = django_apps.get_model(
        'flourish_caregiver.caregiverchildconsent')

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
    def consent_version_cls(self):
        return django_apps.get_model(
            'flourish_caregiver.flourishconsentversion')

    @property
    def caregiver_subject_identifier(self):
        try:
            registered_subject = RegisteredSubject.objects.get(
                subject_identifier=self.subject_identifier)
        except RegisteredSubject.DoesNotExist:
            raise
        else:
            return registered_subject.relative_identifier

    @property
    def latest_consent_version(self):
        version = None
        try:
            consent = self.subject_consent_cls.objects.filter(
                subject_identifier=self.caregiver_subject_identifier, ).latest(
                'consent_datetime')
        except ObjectDoesNotExist:
            return None
        else:
            screening_identifier = consent.screening_identifier
            try:
                consent_version_obj = self.consent_version_cls.objects.get(
                    screening_identifier=screening_identifier)
            except self.consent_version_cls.DoesNotExist:
                version = '1'
            else:
                version = consent_version_obj.version
            return version

    @property
    def subject_consent_obj(self):
        """Returns a child birth model instance or None.
        """
        try:
            return self.subject_consent_cls.objects.get(
                subject_identifier=self.caregiver_subject_identifier,
                version=self.latest_consent_version)
        except ObjectDoesNotExist:
            return None

    @property
    def caregiver_child_consent_obj(self):
        """Returns a caregiver consent on behalf of child model instance or None.
        """
        try:
            return self.child_consent_cls.objects.get(
                subject_identifier=self.subject_identifier,
                version=self.latest_consent_version)
        except ObjectDoesNotExist:
            return None

    @property
    def maternal_delivery_obj(self):
        """Returns a child birth model instance or None.
        """
        try:

            return self.maternal_delivery_cls.objects.get(
                subject_identifier=self.caregiver_subject_identifier)
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
    def child_initials(self):
        pass

    @property
    def child_offstudy_cls(self):
        return django_apps.get_model('flourish_prn.childoffstudy')

    @property
    def child_offstudy_model_obj(self):
        """Returns a child offstudy model instance or None.
        """
        try:
            return self.child_offstudy_cls.objects.get(
                **self.child_offstudy_options)
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
            infant_birth_values=infant_birth_values, )
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
        subject_identifier = self.kwargs.get('subject_identifier')
        birth_values = ChildBirthValues(subject_identifier=subject_identifier)
        return getattr(birth_values, 'caregiver_subject_identifier', None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            caregiver_registered_subject=self.caregiver_registered_subject)
        return context


class DashboardView(DashboardViewMixin, EdcBaseViewMixin, SubjectDashboardViewMixin,
                    NavbarViewMixin, BaseDashboardView, ChildBirthButtonCls,
                    CaregiverRegisteredSubjectCls):
    dashboard_url = 'child_dashboard_url'
    dashboard_template = 'child_subject_dashboard_template'
    appointment_model = 'flourish_child.appointment'
    appointment_model_wrapper_cls = ChildAppointmentModelWrapper
    crf_model_wrapper_cls = ChildCrfModelWrapper
    requisition_model_wrapper_cls = ChildRequisitionModelWrapper
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
    special_forms_include_value = \
        'flourish_dashboard/child_subject/dashboard/special_forms.html'
    maternal_dashboard_include_value = \
        "flourish_dashboard/child_subject/dashboard/caregiver_dashboard_links.html"
    data_action_item_template = \
        "flourish_dashboard/child_subject/dashboard/data_manager.html"
    odk_archive_forms_include_value = \
        'flourish_dashboard/child_subject/dashboard/odk_archives.html'

    subject_consent_cls = django_apps.get_model(
        'flourish_caregiver.subjectconsent')

    tb_adol_referal_cls = django_apps.get_model(
        'flourish_prn.tbreferaladol')

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
    def consent_version_cls(self):
        return django_apps.get_model(
            'flourish_caregiver.flourishconsentversion')

    @property
    def latest_consent_version(self):
        return ChildBirthValues(
            subject_identifier=self.subject_identifier).latest_consent_version

    @property
    def caregiver_child_consent(self):
        child_consent_cls = django_apps.get_model(
            'flourish_caregiver.caregiverchildconsent')

        child_consent = child_consent_cls.objects.filter(
            subject_identifier=self.subject_identifier).latest('consent_datetime')

        if child_consent:
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
                study_child_identifier=self.caregiver_child_consent
                .study_child_identifier)
        except child_dataset_cls.DoesNotExist:
            return None
        else:
            return ChildDatasetModelWrapper(child_dataset)

    @property
    def young_adult_locator_obj(self):
        try:

            obj = self.young_adult_locator_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except self.young_adult_locator_cls.DoesNotExist:
            pass
        else:
            return obj

    @property
    def young_adult_locator_wrapper(self):
        if self.young_adult_locator_obj:
            return YoungAdultLocatorModelWrapper(model_obj=self.young_adult_locator_obj)

    def check_ageing_out(self):
        ageing_out = ChildOnScheduleHelper().aging_out(
            subject_identifier=self.subject_identifier)

        if ageing_out:
            msg = mark_safe(
                f'Please note, this child is aging out of cohort in {(ageing_out * 12)} '
                f'months.')
            messages.add_message(self.request, messages.INFO, msg)

    def get_context_data(self, **kwargs):
        # Put on schedule before getting the context, so schedule shows onreload.
        if 'fu_enrollment' in self.request.path:
            self.enrol_subject()

        context = super().get_context_data(**kwargs)

        child_offstudy_cls = django_apps.get_model(
            'flourish_prn.childoffstudy')
        child_visit_cls = django_apps.get_model('flourish_child.childvisit')

        self.get_consent_version_object_or_message(
            screening_identifier=self.caregiver_child_consent.subject_consent
            .screening_identifier)

        self.get_offstudy_or_message(visit_cls=child_visit_cls,
                                     offstudy_cls=child_offstudy_cls,
                                     offstudy_action=CHILDOFF_STUDY_ACTION)
        child_age = ChildBirthValues(
            subject_identifier=self.subject_identifier).child_age

        self.check_ageing_out()

        self.caregiver_hiv_status_aware()

        self.get_continued_consent_object_or_message(
            subject_identifier=self.subject_identifier, child_age=child_age)
        self.get_assent_object_or_message(
            subject_identifier=self.subject_identifier, child_age=child_age,
            version=self.latest_consent_version)

        facet_schedule = self.visit_schedules.get(
            'f_child_visit_schedule', None)

        if facet_schedule:
            del self.visit_schedules['f_child_visit_schedule']

        context.update(
            in_person_visits=['2000D', '2100A', '3000'],
            caregiver_child_consent=self.caregiver_child_consent,
            gender=self.caregiver_child_consent.gender,
            child_dataset=self.child_dataset,
            schedule_names=[model.schedule_name for model in
                            self.onschedule_models],
            child_offstudy=self.consent_wrapped.child_offstudy,
            cohort=self.consent_wrapped.get_cohort,
            child_version=self.consent_wrapped.child_consent_version,
            fu_participant_note=self.fu_participant_note,
            is_tb_off_study=self.is_tb_off_study,
            tb_adol_referal=self.tb_adol_referal,
            is_pf_enrolled=self.is_pf_enrolled,
            young_adult_locator_wrapper=self.young_adult_locator_wrapper)

        context = self.add_url_to_context(
            new_key='dashboard_url_name',
            existing_key=self.dashboard_url,
            context=context
        )
        return context

    @property
    def tb_adol_referal(self):
        try:
            tb_referal = self.tb_adol_referal_cls.objects.filter(
                subject_identifier=self.subject_identifier
            ).latest('report_datetime')
        except self.tb_adol_referal_cls.DoesNotExist:
            pass
        else:
            return TbAdolReferralModelWrapper(model_obj=tb_referal)

    def enrol_subject(self):
        subject_identifier = self.kwargs.get('subject_identifier')
        schedule_enrol_helper = ChildFollowUpEnrolmentHelper(
            subject_identifier=subject_identifier)
        schedule_enrol_helper.activate_child_fu_schedule()

    @property
    def fu_participant_note(self):

        schedule_history_cls = django_apps.get_model(
            'edc_visit_schedule.subjectschedulehistory')

        fu_schedule = schedule_history_cls.objects.filter(
            subject_identifier=self.subject_identifier,
            schedule_name__contains='_fu')
        if not fu_schedule:
            flourish_calendar_cls = django_apps.get_model(
                'flourish_calendar.participantnote')

            return flourish_calendar_cls.objects.filter(
                subject_identifier=self.subject_identifier,
                title='Follow Up Schedule', )

    @property
    def maternal_hiv_status(self):
        """Returns mother's current hiv status.
        """
        subject_identifier = self.kwargs.get('subject_identifier')
        caregiver_sid = ChildBirthValues(
            subject_identifier=subject_identifier).caregiver_subject_identifier
        maternal_visit_cls = django_apps.get_model(
            'flourish_caregiver.maternalvisit')
        latest_visit = maternal_visit_cls.objects.filter(
            subject_identifier=caregiver_sid, ).order_by(
            '-report_datetime').first()

        if latest_visit:
            maternal_status_helper = MaternalStatusHelper(
                maternal_visit=latest_visit)
        else:
            maternal_status_helper = MaternalStatusHelper(
                subject_identifier=caregiver_sid)
        return maternal_status_helper.hiv_status

    def hiv_disclosed_or_offstudy(self):

        child_age = ChildBirthValues(
            subject_identifier=self.subject_identifier).child_age

        child_offstudy_cls = django_apps.get_model(
            'flourish_prn.childoffstudy')
        child_visit_cls = django_apps.get_model('flourish_child.childvisit')

        try:
            child_registered_subject = RegisteredSubject.objects.get(
                subject_identifier=self.subject_identifier)
        except RegisteredSubject.DoesNotExist:
            raise ValidationError(
                "Registered subject for the mother is expected to exist.")
        else:
            reg_age = age(child_registered_subject.dob,
                          child_registered_subject.consent_datetime)

            child_age = float(f'{reg_age.years}.{reg_age.months}')

        if self.maternal_hiv_status == POS and child_age and child_age >= 16:
            trigger = self.caregiver_hiv_status_aware()

            self.get_offstudy_or_message(
                visit_cls=child_visit_cls,
                offstudy_cls=child_offstudy_cls,
                offstudy_action=CHILDOFF_STUDY_ACTION,
                trigger=trigger)

    def set_current_schedule(self, onschedule_model_obj=None,
                             schedule=None, visit_schedule=None,
                             is_onschedule=True):

        if onschedule_model_obj:
            if is_onschedule:
                self.current_schedule = schedule
                self.current_visit_schedule = visit_schedule
                self.current_onschedule_model = onschedule_model_obj
            else:
                model_name = f'flourish_child.{onschedule_model_obj._meta.model_name}'
                visit_schedule, schedule = (
                    site_visit_schedules.get_by_onschedule_model_schedule_name(
                        model_name, onschedule_model_obj.schedule_name))
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

    @property
    def is_tb_off_study(self):
        tb_take_off_study_cls = django_apps.get_model(
            'flourish_prn.tbadoloffstudy')
        subject_identifier = self.kwargs.get('subject_identifier')
        try:
            tb_take_off_study_cls.objects.get(
                subject_identifier=subject_identifier)
        except tb_take_off_study_cls.DoesNotExist:
            return False
        else:
            return True

    @property
    def is_pf_enrolled(self):
        if self.child_dataset and self.child_dataset.study_child_identifier:
            return 'P' in self.child_dataset.study_child_identifier

    def caregiver_hiv_status_aware(self):
        """Returns mother's current hiv status.
        """
        trigger = None
        for disclosure_cls in ['hivdisclosurestatusa', 'hivdisclosurestatusb',
                               'hivdisclosurestatusc']:

            hiv_disclosure_cls = django_apps.get_model(
                f'flourish_caregiver.{disclosure_cls}')
            try:
                hiv_disclosure_cls.objects.get(
                    associated_child_identifier=self.subject_identifier,
                    disclosed_status=YES)
            except hiv_disclosure_cls.DoesNotExist:
                trigger = True
            else:
                messages.info(
                    self.request,
                    'Please note, this child is aware of the Mother\'s HIV '
                    'status.')
                trigger = False
                break
        return trigger
