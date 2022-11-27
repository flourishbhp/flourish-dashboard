from django.apps import apps as django_apps
from django.contrib import messages
from edc_constants.constants import YES


class TBStudyViewMixin:
    tb_consent_model = 'flourish_caregiver.tbinformedconsent'

    @property
    def tb_consent_model_cls(self):
        return django_apps.get_model(self.tb_consent_model)

    @property
    def tb_eligibility(self):
        tb_study_eligibility_cls = django_apps.get_model(
            'flourish_caregiver.tbstudyeligibility')
        subject_identifier = self.kwargs.get('subject_identifier')
        try:
            tb_study_screening_obj = tb_study_eligibility_cls.objects.get(
                maternal_visit__subject_identifier=subject_identifier)
        except tb_study_eligibility_cls.DoesNotExist:
            pass
        else:
            if tb_study_screening_obj.tb_participation == YES:
                if not self.is_tb_enroll:
                    messages.warning(
                        self.request,
                        'Complete the TB informed consent under special forms')
                return True
        return False

    # @property
    # def tb_adol_eligibility(self):
    #     tb_adol_eligibility_cls = django_apps.get_model(
    #         'flourish_caregiver.tbadoleligibility')
    #     subject_identifier = self.kwargs.get('subject_identifier')
    #     try:
    #         tb_adol_screening_obj = tb_adol_eligibility_cls.objects.get(
    #             maternal_visit__subject_identifier=subject_identifier)
    #     except tb_adol_eligibility_cls.DoesNotExist:
    #         pass
    #     else:
    #         if tb_adol_screening_obj.tb_participation == YES:
    #             if not self.is_tb_enroll:
    #                 messages.warning(
    #                     self.request,
    #                     'Complete the TB informed consent under special forms')
    #             return True
    #     return False

    def get_tb_enroll_msg(self):
        if self.is_tb_enroll and not self.tb_take_off_study:
            messages.success(self.request, 'Participant enrolled on the TB Maternal Study')

    @property
    def tb_take_off_study(self):
        tb_take_off_study_cls = django_apps.get_model(
            'flourish_caregiver.tboffstudy')
        subject_identifier = self.kwargs.get('subject_identifier')
        try:
            tb_take_off_study_cls.objects.get(
                subject_identifier=subject_identifier)
        except tb_take_off_study_cls.DoesNotExist:
            return False
        else:
            return True

    @property
    def is_tb_enroll(self):
        subject_identifier = self.kwargs.get('subject_identifier')
        try:
            self.tb_consent_model_cls.objects.get(
                subject_identifier=subject_identifier)
        except self.tb_consent_model_cls.DoesNotExist:
            return False
        else:
            return True
