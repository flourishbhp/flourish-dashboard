from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from .missed_birth_visit_model_wrapper import MissedBirthVisitModelWrapper


class MissedBirthVisitModelWrapperMixin:

    missed_birth_visit_model_wrapper_cls = MissedBirthVisitModelWrapper

    @property
    def missed_birth_visit_model_obj(self):
        """Returns a missed birth visit model instance or None
        """
        try:
            return self.missed_birth_visit_cls.objects.get(
                **self.missed_birth_visit_options)
        except ObjectDoesNotExist:
            return None

    @property
    def missed_birth_visit(self):
        """"Returns a wrapped saved or unsaved missed birth visit
         """
        model_obj = self.missed_birth_visit_model_obj or \
            self.missed_birth_visit_cls(
                **self.create_missed_birth_visit_options)
        return self.missed_birth_visit_model_wrapper_cls(model_obj=model_obj)

    @property
    def missed_birth_visit_cls(self):
        return django_apps.get_model('flourish_prn.missedbirthvisit')

    @property
    def create_missed_birth_visit_options(self):
        """Returns a dictionary of options to create a new
        unpersisted missed birth visit model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier)
        return options

    @property
    def missed_birth_visit_options(self):
        """Returns a dictionary of options to get an existing
         missed birth visit model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier, )
        return options
