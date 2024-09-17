from edc_appointment.views import UnscheduledAppointmentView as BaseUnscheduledAppointmentView
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ....model_wrappers import AppointmentModelWrapper


class UnscheduledAppointmentView(BaseUnscheduledAppointmentView):

    def get(self, request, *args, **kwargs):
        """ Update to pass wrapped parent appointment to the
            unscheduled appointment defining `next_by_timepoint`
            attribute that accounts for flourish visit_schedule setup.
        """
        parent_appointment = self.get_parent_appointment(**kwargs)
        kwargs.update(parent_appointment=parent_appointment)
        return super().get(request, *args, **kwargs)

    def get_parent_appointment(self, **kwargs):
        visit_schedule_name = kwargs.get('visit_schedule_name', None)
        schedule_name = kwargs.get('schedule_name', None)
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name)
        schedule = visit_schedule.schedules.get(schedule_name)
        appointment_model_cls = schedule.appointment_model_cls
        try:
            appointment = appointment_model_cls.objects.get(
                subject_identifier=kwargs.get('subject_identifier', None),
                visit_schedule_name=visit_schedule_name,
                schedule_name=schedule_name,
                visit_code=kwargs.get('visit_code', None),
                visit_code_sequence=0)
        except appointment_model_cls.DoesNotExist:
            return None
        else:
            return AppointmentModelWrapper(model_obj=appointment)
