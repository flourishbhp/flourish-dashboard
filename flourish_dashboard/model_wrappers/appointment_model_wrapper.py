from edc_subject_dashboard import AppointmentModelWrapper as BaseAppointmentModelWrapper

from .maternal_visit_model_wrapper import MaternalVisitModelWrapper


class AppointmentModelWrapper(BaseAppointmentModelWrapper):

    visit_model_wrapper_cls = MaternalVisitModelWrapper
