from django.apps import apps as django_apps
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from edc_base.view_mixins import EdcBaseViewMixin
from edc_consent.exceptions import NotConsentedError
from edc_constants.constants import NO, YES
from edc_dashboard.views import DashboardView as BaseDashboardView
from edc_navbar import NavbarViewMixin
from edc_registration.models import RegisteredSubject
from edc_subject_dashboard.view_mixins import SubjectDashboardViewMixin

from flourish_caregiver.helper_classes import MaternalStatusHelper
from flourish_dashboard.model_wrappers.antenatal_enrollment_model_wrapper import \
    AntenatalEnrollmentModelWrapper
from flourish_prn.action_items import CAREGIVEROFF_STUDY_ACTION
from ...child_subject.dashboard.dashboard_view import ChildBirthValues
from ...view_mixin import DashboardViewMixin
from ....model_wrappers import AppointmentModelWrapper, \
    SubjectConsentModelWrapper
from ....model_wrappers import CaregiverChildConsentModelWrapper
from ....model_wrappers import CaregiverLocatorModelWrapper, \
    MaternalVisitModelWrapper
from ....model_wrappers import MaternalCrfModelWrapper, \
    MaternalScreeningModelWrapper
from ....model_wrappers import MaternalDatasetModelWrapper, \
    CaregiverRequisitionModelWrapper


class DashboardView(DashboardViewMixin, EdcBaseViewMixin,
                    SubjectDashboardViewMixin,
                    NavbarViewMixin, BaseDashboardView):
    dashboard_url = 'subject_dashboard_url'
    dashboard_template = 'subject_dashboard_template'
    appointment_model = 'edc_appointment.appointment'
    appointment_model_wrapper_cls = AppointmentModelWrapper
    crf_model_wrapper_cls = MaternalCrfModelWrapper
    consent_model = 'flourish_caregiver.subjectconsent'
    consent_model_wrapper_cls = SubjectConsentModelWrapper
    requisition_model_wrapper_cls = CaregiverRequisitionModelWrapper
    navbar_name = 'flourish_dashboard'
    visit_attr = 'maternalvisit'
    navbar_selected_item = 'consented_subject'
    subject_locator_model = 'flourish_caregiver.caregiverlocator'
    subject_locator_model_wrapper_cls = CaregiverLocatorModelWrapper
    visit_model_wrapper_cls = MaternalVisitModelWrapper
    mother_infant_study = True
    infant_links = True
    maternal_links = False
    special_forms_include_value = 'flourish_dashboard/maternal_subject/dashboard/special_forms.html'
    data_action_item_template = 'flourish_dashboard/maternal_subject/dashboard/data_manager.html'
    infant_dashboard_include_value = 'flourish_dashboard/maternal_subject/dashboard/infant_dashboard_links.html'
    infant_subject_dashboard_url = 'child_dashboard_url'
    tb_consent_model = 'flourish_caregiver.tbinformedconsent'
    antenatal_enrolment_model = 'flourish_caregiver.antenatalenrollment'
    odk_archive_forms_include_value = 'flourish_dashboard/maternal_subject/dashboard/odk_archives.html'

    @property
    def antenatal_enrolment_cls(self):
        return django_apps.get_model(self.antenatal_enrolment_model)

    @property
    def tb_consent_model_cls(self):
        return django_apps.get_model(self.tb_consent_model)

    @property
    def antenatal_enrolment(self):
        try:
            antenatal_enrolment_obj = self.antenatal_enrolment_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except self.antenatal_enrolment_cls.DoesNotExist:
            return None
        else:
            return AntenatalEnrollmentModelWrapper(model_obj=antenatal_enrolment_obj)

    @property
    def appointments(self):
        """Returns a Queryset of all appointments for this subject.
        """
        if not self._appointments:
            self._appointments = self.appointment_model_cls.objects.filter(
                subject_identifier=self.subject_identifier).order_by(
                'visit_code')
        return self._appointments

    @property
    def screening_pregnant_women(self):
        """Return a wrapped screening for preg women obj.
        """
        screening_cls = django_apps.get_model(
            'flourish_caregiver.screeningpregwomen')
        try:
            subject_screening = screening_cls.objects.get(
                subject_identifier=self.kwargs.get('subject_identifier'))
        except screening_cls.DoesNotExist:
            return None
        else:
            return MaternalScreeningModelWrapper(subject_screening)

    @property
    def maternal_dataset(self):
        """Returns a wrapped maternal dataset obj
        """
        maternal_dataset_cls = django_apps.get_model(
            'flourish_caregiver.maternaldataset')

        try:
            maternal_dataset = maternal_dataset_cls.objects.get(
                subject_identifier=self.kwargs.get('subject_identifier'))
        except maternal_dataset_cls.DoesNotExist:
            return None
        else:
            return MaternalDatasetModelWrapper(maternal_dataset)

    @property
    def caregiver_child_consents(self):
        wrapped_consents = []
        child_consent_cls = django_apps.get_model(
            'flourish_caregiver.caregiverchildconsent')
        child_consents = child_consent_cls.objects.filter(
            subject_identifier__startswith=self.subject_identifier)
        for child_consent in child_consents:
            wrapped_consents.append(
                CaregiverChildConsentModelWrapper(child_consent))
        return wrapped_consents

    @property
    def subject_consent_wrapper(self):

        subject_consent_cls = django_apps.get_model(
            'flourish_caregiver.subjectconsent')

        subject_identifier = self.kwargs.get('subject_identifier')
        if len(subject_identifier.split('-')) == 4:
            subject_identifier = subject_identifier[:-3]

        subject_consents = subject_consent_cls.objects.filter(
            subject_identifier=subject_identifier)

        if subject_consents:
            return SubjectConsentModelWrapper(
                model_obj=subject_consents.latest('consent_datetime'))
        else:
            raise NotConsentedError(
                'No consent object found for participant with subject '
                f'identifier {self.subject_identifier}')

    def get_context_data(self, offstudy_model_wrapper_cls=None, **kwargs):
        global offstudy_cls_model_obj
        context = super().get_context_data(**kwargs)

        caregiver_offstudy_cls = django_apps.get_model(
            'flourish_prn.caregiveroffstudy')
        caregiver_visit_cls = django_apps.get_model(
            'flourish_caregiver.maternalvisit')
        self.get_offstudy_or_message(
            visit_cls=caregiver_visit_cls,
            offstudy_cls=caregiver_offstudy_cls,
            offstudy_action=CAREGIVEROFF_STUDY_ACTION)

        self.get_consent_version_object_or_message(
            self.subject_consent_wrapper.screening_identifier)

        self.get_offstudy_message(offstudy_cls=caregiver_offstudy_cls)

        self.get_assent_continued_consent_obj_or_msg()
        self.get_assent_object_or_message()

        locator_obj = self.get_locator_info()

        offstudy_cls_model = self.consent_wrapped.caregiver_offstudy

        tb_eligibility = self.tb_eligibility

        context.update(
            locator_obj=locator_obj,
            schedule_names=[model.schedule_name for model in
                            self.onschedule_models],
            cohorts=self.get_cohorts,
            subject_consent=self.subject_consent_wrapper,
            gender=self.consent_wrapped.gender,
            screening_preg_women=self.screening_pregnant_women,
            maternal_dataset=self.maternal_dataset,
            hiv_status=self.hiv_status,
            child_names=self.child_names_schedule_dict,
            caregiver_child_consents=self.caregiver_child_consents,
            infant_registered_subjects=self.infant_registered_subjects,
            is_pregnant=self.is_pregnant,
            caregiver_offstudy=offstudy_cls_model,
            version=self.subject_consent_wrapper.consent_version,
            caregiver_death_report=self.consent_wrapped.caregiver_death_report,
            tb_eligibility=tb_eligibility,
            antenatal_enrolment=self.antenatal_enrolment)
        return context

    @property
    def child_names_schedule_dict(self):
        """ Return a key value pair of mother's visit schedule's corresponding
        child names for dashboard display"""

        child_consent_cls = django_apps.get_model(
            'flourish_caregiver.caregiverchildconsent')
        all_child_consents = child_consent_cls.objects.filter(
            subject_identifier__icontains=self.subject_identifier).exclude(
            Q(subject_identifier__icontains='-35') | Q(
                subject_identifier__icontains='-46') | Q(
                subject_identifier__icontains='-56')).order_by('created')

        if all_child_consents.count() > 1:

            appt_cls = django_apps.get_model('edc_appointment.appointment')
            cohorts = []
            for child in all_child_consents:
                cohorts.append(child.cohort)

            appointments = appt_cls.objects.filter(
                subject_identifier=self.subject_identifier,
                visit_code__endswith='000M')

            schedule_child_dict = {}

            for onschedule_model in self.onschedule_models:

                if (('sec' in onschedule_model.schedule_name
                     and 'quart' not in onschedule_model.schedule_name)
                        or 'enrol' in onschedule_model.schedule_name
                        or 'antenatal' in onschedule_model.schedule_name):
                    child_consents = all_child_consents.filter(
                        subject_identifier=onschedule_model.child_subject_identifier)

                    if child_consents:
                        child = child_consents.latest('consent_datetime')

                        appt = appointments.get(
                            schedule_name=onschedule_model.schedule_name)

                        full_names = None

                        if child.first_name:
                            full_names = child.first_name + ' ' + child.last_name
                        else:
                            full_names = 'ANC SCHEDULE'

                        schedule_child_dict[appt.visit_schedule_name] = full_names

            return schedule_child_dict

    @property
    def get_cohorts(self):
        subject_consent = self.subject_consent_wrapper.object
        child_consent = subject_consent.caregiverchildconsent_set.all()
        cohorts_query = child_consent.values_list('cohort',
                                                  flat=True).distinct()
        cohorts = ''
        for a in self.onschedule_models:
            if a.schedule_name == 'a_antenatal1_schedule1':
                cohorts = 'COHORT_A'

        for cohort in cohorts_query:
            if cohort:
                cohorts += ' ' + cohort.upper()

        cohorts = cohorts.strip().replace(' ', '| ')

        return cohorts.replace('_', ' ')

    def set_current_schedule(self, onschedule_model_obj=None, schedule=None,
            visit_schedule=None, is_onschedule=True):
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

    @property
    def get_offschedule_model_obj(self, schedule):
        try:
            return schedule.offschedule_model_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            return None

    @property
    def hiv_status(self):
        """Returns mother's current hiv status.
        """
        maternal_visit_cls = django_apps.get_model(
            MaternalVisitModelWrapper.model)
        subject_identifier = self.kwargs.get('subject_identifier')
        latest_visit = maternal_visit_cls.objects.filter(
            subject_identifier=subject_identifier, ).order_by(
            '-report_datetime').first()

        if latest_visit:
            maternal_status_helper = MaternalStatusHelper(
                maternal_visit=latest_visit)
        else:
            maternal_status_helper = MaternalStatusHelper(
                subject_identifier=self.kwargs.get('subject_identifier'))
        return maternal_status_helper.hiv_status

    @property
    def infant_registered_subjects(self):
        """Returns an infant registered subjects.
        """
        subject_identifier = self.kwargs.get('subject_identifier')
        try:
            registered_subject = RegisteredSubject.objects.filter(
                relative_identifier=subject_identifier)
        except RegisteredSubject.DoesNotExist:
            return None
        else:
            return registered_subject

    def get_locator_info(self):

        subject_identifier = self.kwargs.get('subject_identifier')
        try:
            obj = self.subject_locator_model_cls.objects.get(
                subject_identifier=subject_identifier)
        except ObjectDoesNotExist:
            return None
        return obj

    @property
    def is_pregnant(self):
        screening_preg_cls = django_apps.get_model(
            'flourish_caregiver.screeningpregwomen')

        if self.consent_wrapped:
            try:
                screening_preg_cls.objects.get(
                    screening_identifier=self.consent_wrapped.screening_identifier)
            except screening_preg_cls.DoesNotExist:
                return False
            else:
                delivery_cls = django_apps.get_model(
                    'flourish_caregiver.maternaldelivery')
                try:
                    delivery_cls.objects.get(
                        subject_identifier=self.consent_wrapped.subject_identifier)
                except delivery_cls.DoesNotExist:
                    return True
                else:
                    return False
            return True

    def get_assent_continued_consent_obj_or_msg(self):
        child_consents = self.caregiver_child_consents
        for consent in child_consents:
            subject_identifier = consent.subject_identifier
            child_age = ChildBirthValues(
                subject_identifier=subject_identifier).child_age
            self.get_continued_consent_object_or_message(
                subject_identifier=subject_identifier, child_age=child_age)
            self.get_assent_object_or_message(
                subject_identifier=subject_identifier, child_age=child_age)

    @property
    def tb_eligibility(self):
        tb_study_eligibility_cls = django_apps.get_model(
            'flourish_caregiver.tbstudyeligibility')
        subject_identifier = self.kwargs.get('subject_identifier')
        try:
            tb_study_screening_obj = tb_study_eligibility_cls.objects.get(
                maternal_visit__subject_identifier=subject_identifier
            )
        except tb_study_eligibility_cls.DoesNotExist:
            pass
        else:
            if tb_study_screening_obj.tb_participation == YES:
                try:
                    self.tb_consent_model_cls.objects.get(
                        subject_identifier=subject_identifier)
                except self.tb_consent_model_cls.DoesNotExist:
                    messages.warning(self.request,
                                     'Complete the TB informed consent under special form')
                return True
        return False
