from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from edc_action_item.site_action_items import site_action_items
from edc_base.utils import get_utcnow
from edc_constants.constants import NEW, OFF_STUDY, POS, OPEN

from flourish_dashboard.utils import flourish_dashboard_utils


class DashboardViewMixin:
    data_action_item_model = 'edc_data_manager.dataactionitem'

    young_adult_locator_model = 'flourish_child.youngadultlocator'

    child_offstudy_model = 'flourish_prn.childoffstudy'

    @property
    def child_offstudy_cls(self):
        return django_apps.get_model(self.child_offstudy_model)

    @property
    def young_adult_locator_cls(self):
        return django_apps.get_model(self.young_adult_locator_model)

    @property
    def data_action_item_cls(self):
        return django_apps.get_model(self.data_action_item_model)

    def get_offstudy_or_message(self, visit_cls=None, offstudy_cls=None,
                                offstudy_action=None, trigger=False):

        subject_identifier = self.kwargs.get('subject_identifier')

        sub_study_visit_codes = ['2100T', '2200T',
                                 '2100A', '2200A', '2600F']

        offstudy_visit_obj = visit_cls.objects.filter(
            appointment__subject_identifier=subject_identifier,
            study_status=OFF_STUDY).exclude(
            visit_code__in=sub_study_visit_codes).order_by(
            'report_datetime').last()

        trigger = self.require_offstudy(
            offstudy_visit_obj, subject_identifier) or trigger

        self.action_cls_item_creator(
            subject_identifier=subject_identifier,
            action_cls=offstudy_cls,
            action_type=offstudy_action,
            trigger=trigger)

    def require_offstudy(self, offstudy_visit_obj, subject_identifier):

        hiv_cls = django_apps.get_model(
            'flourish_child.childhivrapidtestcounseling')

        hiv_obj = hiv_cls.objects.filter(
            child_visit__subject_identifier=subject_identifier,
            result=POS)

        preg_test_cls = django_apps.get_model(
            'flourish_child.childpregtesting')

        preg_test_obj = preg_test_cls.objects.filter(
            child_visit__subject_identifier=subject_identifier,
            child_visit__visit_code='2000',
            preg_test_result=POS)

        child_continued_consent_cls = django_apps.get_model(
            'flourish_child.childcontinuedconsent')

        child_continued_consent_obj = child_continued_consent_cls.objects.filter(
            subject_identifier=subject_identifier,
            is_eligible=False)

        infant_hiv_test_cls = django_apps.get_model(
            'flourish_child.infanthivtesting')

        infant_hiv_test_obj = infant_hiv_test_cls.objects.filter(
            child_visit__subject_identifier=subject_identifier,
            hiv_test_result=POS)

        return (hiv_obj or preg_test_obj or offstudy_visit_obj or
                child_continued_consent_obj or infant_hiv_test_obj)

    def get_offstudy_message(self, offstudy_cls=None, msg=None):

        action_item_obj = self.get_action_item_obj(offstudy_cls)
        msg = msg or mark_safe(
            f'Please complete the off-study form to take subject off-study.')

        if action_item_obj:
            messages.add_message(self.request, messages.ERROR, msg)

    def action_cls_item_creator(self, subject_identifier=None, action_cls=None,
                                action_type=None, trigger=None):

        action_item_cls = site_action_items.get(
            action_cls.action_name)
        action_item_model_cls = action_item_cls.action_item_model_cls()

        if trigger:
            try:
                action_item_model_cls.objects.get(
                    subject_identifier=subject_identifier,
                    action_type__name=action_type,
                    status=NEW)
            except ObjectDoesNotExist:
                action_item_cls(
                    subject_identifier=subject_identifier)
        else:
            self.delete_action_item_if_new(action_cls)

    def data_action_item_creator(self, subject_identifier=None, subject=None,
                                 message=None, assigned=None, priority='Normal'):
        defaults = {'assigned': assigned,
                    'comment': message,
                    'action_priority': priority}
        self.data_action_item_cls.objects.update_or_create(
            subject=subject,
            subject_identifier=subject_identifier,
            defaults=defaults)

    def delete_action_item_if_new(self, action_model_cls):
        action_item_obj = self.get_action_item_obj(action_model_cls, [NEW, OPEN])
        if action_item_obj:
            action_item_obj.delete()

    def get_action_item_obj(self, model_cls, action_status=[NEW, ]):
        subject_identifier = self.kwargs.get('subject_identifier')
        action_cls = site_action_items.get(
            model_cls.action_name)
        action_item_model_cls = action_cls.action_item_model_cls()

        try:
            action_item_obj = action_item_model_cls.objects.get(
                subject_identifier=subject_identifier,
                action_type__name=model_cls.action_name,
                status__in=action_status)
        except action_item_model_cls.DoesNotExist:
            return None
        return action_item_obj

    def get_assent_object_or_message(
            self, child_age=None, subject_identifier=None, version=None):
        obj = None
        assent_cls = django_apps.get_model('flourish_child.childassent')
        if child_age and ((child_age / 12) >= 7 and (child_age / 12 < 18)):
            try:
                obj = assent_cls.objects.get(
                    subject_identifier=subject_identifier,
                    version=version)
            except assent_cls.DoesNotExist:
                if version:
                    msg = mark_safe(
                        f'Please complete the v{version} assent fo'
                        f'r child {subject_identifier}')
                else:
                    msg = mark_safe(
                        f'Please complete assent for child {subject_identifier}')
                self.data_action_item_creator(
                    subject_identifier=subject_identifier,
                    subject=f'Complete v{version} assent',
                    message=msg,
                    assigned='clinic', )
                messages.add_message(self.request, messages.WARNING, msg)
            return obj

    def get_consent_version_object_or_message(self, screening_identifier=None):
        consent_version_cls = django_apps.get_model(
            'flourish_caregiver.flourishconsentversion')

        try:
            consent_version_cls.objects.get(
                screening_identifier=screening_identifier)
        except consent_version_cls.DoesNotExist:
            msg = mark_safe(
                'Please complete the consent version form before proceeding.')
            messages.add_message(self.request, messages.WARNING, msg)

    def get_continued_consent_object_or_message(self, child_age=None,
                                                subject_identifier=None):
        obj = None
        child_continued_consent_cls = django_apps.get_model(
            'flourish_child.childcontinuedconsent')
        if child_age and (child_age / 12) >= 18:
            try:
                obj = child_continued_consent_cls.objects.filter(
                    subject_identifier=subject_identifier).latest('consent_datetime')
            except child_continued_consent_cls.DoesNotExist:
                msg = mark_safe(
                    f'Please complete the continued consent for child '
                    f'{subject_identifier}.')
                messages.add_message(self.request, messages.WARNING, msg)
            return obj

    def get_consent_from_version_form_or_message(self, subject_identifier,
                                                 screening_identifier):
        """ Updated to consider continued child consent for adolescents >= 18
        """
        today_dt = get_utcnow().date()
        eighteen_years_dt = today_dt - relativedelta(years=18)
        caregiver_child_consent_cls = django_apps.get_model(
            'flourish_caregiver.caregiverchildconsent')

        consent_version_obj = flourish_dashboard_utils.consent_version_obj(
            screening_identifier)
        if getattr(consent_version_obj, 'child_version', None):

            consents_lt_18 = caregiver_child_consent_cls.objects.filter(
                subject_consent__subject_identifier=subject_identifier,
                child_dob__gt=eighteen_years_dt)

            caregiver_child_consent_objs = consents_lt_18.filter(
                version=consent_version_obj.child_version)

            if consents_lt_18 and not caregiver_child_consent_objs:
                msg = mark_safe(
                    f'Please complete the v{consent_version_obj.child_version} '
                    f'consent '
                    f'on behalf of child {subject_identifier}.')
                messages.add_message(self.request, messages.WARNING, msg)
        if (flourish_dashboard_utils.is_delivery_window(subject_identifier)
                and not getattr(consent_version_obj, 'child_version', None)):
            msg = mark_safe(
                'Please complete the consent version for consent on behalf of child'
                f' {subject_identifier}.')
            messages.add_message(self.request, messages.WARNING, msg)
