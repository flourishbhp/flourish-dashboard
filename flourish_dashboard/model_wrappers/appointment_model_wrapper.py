from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_subject_dashboard import AppointmentModelWrapper as BaseAppointmentModelWrapper

from .maternal_visit_model_wrapper import MaternalVisitModelWrapper


class AppointmentModelWrapper(BaseAppointmentModelWrapper):

    visit_model_wrapper_cls = MaternalVisitModelWrapper
    unscheduled_appointment_url_name = 'flourish_dashboard:unscheduled_appointment_url'

    @property
    def next_by_timepoint(self):
        """ Returns the previous appointment or None of all appointments
            for this subject for visit_code_sequence=0. Use this instead
            of attr defined on the base appointment model, to account for
            visit_schedule setup.
        """
        return self.model_cls.objects.filter(
            subject_identifier=self.subject_identifier,
            timepoint__gt=self.timepoint,
            visit_code_sequence=0,
            schedule_name=self.schedule_name
        ).order_by('timepoint').first()

    @property
    def next_visit_code_sequence(self):
        return getattr(self.object, 'next_visit_code_sequence', None)

    @property
    def appt_datetime(self):
        return getattr(self.object, 'appt_datetime', None)

    @property
    def timepoint_datetime(self):
        return getattr(self.object, 'timepoint_datetime', None)

    @property
    def wrapped_visit(self):
        """Returns a wrapped persistent or non-persistent visit instance.
        """
        try:
            model_obj = self.object.maternalvisit
        except ObjectDoesNotExist:
            visit_model = django_apps.get_model(
                self.visit_model_wrapper_cls.model)
            model_obj = visit_model(
                appointment=self.object,
                subject_identifier=self.subject_identifier,
                reason=self.object.appt_reason)
        return self.visit_model_wrapper_cls(model_obj=model_obj)
