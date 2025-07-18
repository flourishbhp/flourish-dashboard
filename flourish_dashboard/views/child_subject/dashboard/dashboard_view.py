from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist, \
    ValidationError
from django.utils.safestring import mark_safe
from django.views.generic.base import ContextMixin
from edc_base.utils import get_utcnow
from edc_base.view_mixins import EdcBaseViewMixin
from edc_constants.constants import YES
from edc_dashboard.views import DashboardView as BaseDashboardView
from edc_data_manager.model_wrappers import DataActionItemModelWrapper
from edc_navbar import NavbarViewMixin
from edc_registration.models import RegisteredSubject
from edc_subject_dashboard.view_mixins import SubjectDashboardViewMixin
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from flourish_caregiver.helper_classes import MaternalStatusHelper
from flourish_child.helper_classes.brain_ultrasound_helper import BrainUltrasoundHelper
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
        difference = relativedelta(
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
    def get_consent_version_obj(self):
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
                return None
            else:
                return consent_version_obj

    @property
    def latest_consent_version(self):
        version = getattr(self.get_consent_version_obj, 'version', '1')
        return version

    @property
    def latest_child_consent_version(self):
        version = getattr(
            self.get_consent_version_obj, 'child_version', '1')
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
        version = (self.latest_child_consent_version or
                   self.latest_consent_version)
        try:
            return self.child_consent_cls.objects.get(
                subject_identifier=self.subject_identifier,
                version=version)
        except ObjectDoesNotExist:
            return None

    @property
    def maternal_delivery_obj(self):
        """Returns a child birth model instance or None.
        """
        try:

            return self.maternal_delivery_cls.objects.get(
                child_subject_identifier=self.subject_identifier)
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

    birth_data_cls = django_apps.get_model(
        'flourish_child.preflourishbirthdata')

    @property
    def brain_ultrasound_helper(self):
        """Returns a brain ultrasound helper."""
        subject_identifier = self.kwargs.get('subject_identifier')
        return BrainUltrasoundHelper(
            child_subject_identifier=subject_identifier,
            caregiver_subject_identifier=self.caregiver_subject_identifier)

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

        if 'brain_ultrasound' in self.request.path:
            if self.brain_ultrasound_helper.is_enrolled_brain_ultrasound():
                self.brain_ultrasound_helper.brain_ultrasound_enrolment()
            else:
                msg = mark_safe(
                    f'Please enrol this participant in the Redcap brainultrasound.')
                messages.add_message(self.request, messages.INFO, msg)

        context = super().get_context_data(**kwargs)

        child_offstudy = self.consent_wrapped.child_offstudy

        child_age = ChildBirthValues(
            subject_identifier=self.subject_identifier).child_age

        disclosure_offstudy = False

        requires_continued_consent = False

        if not child_offstudy and not self.check_anc_offschedule:
            disclosure_offstudy = self.caregiver_hiv_status_aware()

            self.get_consent_version_object_or_message(
                screening_identifier=self.caregiver_child_consent.subject_consent.screening_identifier)

            self.get_continued_consent_object_or_message(
                subject_identifier=self.subject_identifier,
                child_age=child_age)

            requires_continued_consent = (child_age/12) >= 18 if child_age else False

            self.get_assent_object_or_message(
                subject_identifier=self.subject_identifier,
                child_age=child_age,
                version=self.latest_consent_version)

            self.check_ageing_out()

            offstudy_eligible = self.consent_wrapped.eligible_for_protocol_completion
            if offstudy_eligible:
                messages.info(
                    self.request,
                    'Please note, this child is eligible for '
                    'off-study/protocol completion.')

        child_visit_cls = django_apps.get_model('flourish_child.childvisit')

        self.get_offstudy_or_message(visit_cls=child_visit_cls,
                                     offstudy_cls=self.child_offstudy_cls,
                                     offstudy_action=CHILDOFF_STUDY_ACTION,
                                     trigger=disclosure_offstudy)

        facet_schedule = self.visit_schedules.get(
            'f_child_visit_schedule', None)

        group_names = self.request.user.groups.values_list('name', flat=True)

        if facet_schedule:
            del self.visit_schedules['f_child_visit_schedule']

        context.update(
            in_person_visits=['2000D', '2100A', '3000'],
            caregiver_child_consent=self.caregiver_child_consent,
            gender=self.caregiver_child_consent.gender,
            group_names=group_names,
            child_dataset=self.child_dataset,
            schedule_names=[model.schedule_name for model in
                            self.onschedule_models],
            child_offstudy=child_offstudy,
            cohort=self.consent_wrapped.get_cohort,
            child_version=self.consent_wrapped.child_consent_version,
            fu_participant_note=self.fu_participant_note,
            is_tb_off_study=self.is_tb_off_study,
            tb_adol_referal=self.tb_adol_referal,
            is_pf_enrolled=self.is_pf_enrolled,
            is_brain_ultrasound_enrolled=self.is_brain_ultrasound_enrolled,
            show_brain_ultrasound_button=self.brain_ultrasound_helper.show_brain_ultrasound_button(),
            young_adult_locator_wrapper=self.young_adult_locator_wrapper,
            is_pf_birth_data=self.is_pf_birth_data(),
            requires_continued_consent=requires_continued_consent)

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

        not_sq_enrol = (self.consent_wrapped.current_cohort ==
                        self.consent_wrapped.enrol_cohort)

        schedules = schedule_history_cls.objects.filter(
            subject_identifier=self.subject_identifier, )
        fu_schedule = schedules.filter(schedule_name__contains='_fu').exists()
        primary_cohort = True
        try:
            latest_schedule = schedules.latest(
                'onschedule_datetime', 'created')
        except schedule_history_cls.DoesNotExist:
            pass
        else:
            primary_cohort = not ('sec' in latest_schedule.schedule_name)

        if not fu_schedule and primary_cohort and not_sq_enrol:
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

    @property
    def check_anc_offschedule(self):
        subject_identifier = self.kwargs.get('subject_identifier')
        ssh_model_cls = django_apps.get_model(
            'edc_visit_schedule.subjectschedulehistory')

        child_schedules = ssh_model_cls.objects.filter(
            subject_identifier=subject_identifier).exists()
        if child_schedules:
            return False

        anc_schedule_model_cls = django_apps.get_model(
            'flourish_caregiver.onschedulecohortaantenatal')
        onschedule = anc_schedule_model_cls.objects.filter(
            child_subject_identifier=subject_identifier).values(
                'subject_identifier', 'schedule_name').first()

        is_offschedule = ssh_model_cls.objects.filter(
                subject_identifier=onschedule.get('subject_identifier', None),
                schedule_name=onschedule.get('schedule_name', None),
                schedule_status='offschedule').exists()
        if is_offschedule:
            messages.warning(
                self.request,
                mark_safe('<b>PLEASE NOTE: This child is off-study.</b'))
            return is_offschedule

    def set_current_schedule(self, onschedule_model_obj=None,
                             schedule=None, visit_schedule=None,
                             is_onschedule=True):

        if onschedule_model_obj:
            if is_onschedule:
                self.current_schedule = schedule
                self.current_visit_schedule = visit_schedule
                self.current_onschedule_model = onschedule_model_obj
            else:
                model_name = onschedule_model_obj._meta.label_lower
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

    def is_pf_birth_data(self):
        subject_identifier = self.kwargs.get('subject_identifier')
        try:
            self.birth_data_cls.objects.get(
                subject_identifier=subject_identifier)
        except self.birth_data_cls.DoesNotExist:
            return False
        else:
            return True

    def caregiver_hiv_status_aware(self):
        """ Checks if child has been disclosed to and if not disclosed to at
            10 years or older, take off-study
        """
        _disclosed = False
        for disclosure_cls in ['hivdisclosurestatusa', 'hivdisclosurestatusb',
                               'hivdisclosurestatusc']:

            hiv_disclosure_cls = django_apps.get_model(
                f'flourish_caregiver.{disclosure_cls}')
            try:
                hiv_disclosure_cls.objects.get(
                    associated_child_identifier=self.subject_identifier,
                    disclosed_status=YES)
            except hiv_disclosure_cls.DoesNotExist:
                continue
            except MultipleObjectsReturned:
                _disclosed = True
                messages.info(
                    self.request,
                    'Please note, this child is aware of the Mother\'s HIV '
                    'status.')
                break
            else:
                _disclosed = True
                messages.info(
                    self.request,
                    'Please note, this child is aware of the Mother\'s HIV '
                    'status.')
                break

        if not _disclosed:
            # Show notification if HEU not disclosed to, at 10 years or older
            child_age_yrs = self.consent_wrapped.child_age
            current_cohort = self.consent_wrapped.cohort_model_obj({
                'subject_identifier': self.subject_identifier,
                'current_cohort': True, })

            if current_cohort and child_age_yrs:
                if (current_cohort.exposure_status == 'EXPOSED' and
                        child_age_yrs >= 10):
                    messages.warning(
                        self.request,
                        'This child is 10 years or older and is NOT aware '
                        'of the Mother\'s HIV status. Please complete CRF.')
                if child_age_yrs >= 18:
                    # Return true to take child off-study for HEU undisclosed
                    # 18 years or older.
                    return True

    @property
    def is_brain_ultrasound_enrolled(self):
        """Returns True if the child is enrolled on the brain ultrasound schedule."""
        return (self.brain_ultrasound_helper.is_enrolled_brain_ultrasound() and
                not self.brain_ultrasound_helper.is_onschedule)
