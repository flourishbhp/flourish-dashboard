from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .child_death_report_model_wrapper import ChildDeathReportModelWrapper


class ChildDeathReportModelWrapperMixin:
    child_death_report_model_wrapper_cls = ChildDeathReportModelWrapper

    @property
    def child_death_report_model_obj(self):
        """Returns a child death report model instance or None.
        """
        try:
            return self.child_death_report_cls.objects.get(
                **self.child_death_report_options)
        except ObjectDoesNotExist:
            return None

    @property
    def child_death_report(self):
        """"Returns a wrapped saved or unsaved child death report
        """
        model_obj = self.child_death_report_model_obj or \
                    self.child_death_report_cls(
                        **self.create_child_death_report_options
                    )
        return self.child_death_report_model_wrapper_cls(model_obj=model_obj)

    @property
    def child_death_report_cls(self):
        return django_apps.get_model('flourish_prn.childdeathreport')

    @property
    def create_child_death_report_options(self):
        """Returns a dictionary of options to create a new
        unpersisted death report model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier)
        return options

    @property
    def child_death_report_options(self):
        """Returns a dictionary of options to get an existing
         child death report model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier, )
        return options
