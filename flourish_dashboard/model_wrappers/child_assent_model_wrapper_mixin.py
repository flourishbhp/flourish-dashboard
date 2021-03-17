from dateutil import relativedelta
from edc_base.utils import get_utcnow

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .child_assent_model_wrapper import ChildAssentModelWrapper


class ChildAssentModelWrapperMixin:

    assent_model_wrapper_cls = ChildAssentModelWrapper


    @property
    def assent_model_cls(self):
        return django_apps.get_model('flourish_child.childassent')

    @property
    def assent_version(self):
        return '1'

    @property
    def assent_model_obj(self):
        """Returns a child assent model instance or None.
        """
        try:
            return self.assent_model_cls.objects.get(
                **self.assent_options)
        except ObjectDoesNotExist:
            return None

    @property
    def child_name_initial(self):
        if getattr(self, 'assent_model_obj'):
            name = self.assent_model_obj.first_name
            initials = self.assent_model_obj.initials
            return f'{name} {initials}'
        return None

    @property
    def assent_date(self):
        if getattr(self, 'assent_model_obj'):
            return self.assent_model_obj.consent_datetime.date()
        return None

    @property
    def child_age(self):
        if getattr(self, 'assent_model_obj'):
            birth_date = self.assent_model_obj.dob
            difference = relativedelta.relativedelta(
                get_utcnow().date(), birth_date)
            months = 0
            if difference.years > 0:
                months = difference.years * 12
            years = round((months + difference.months) / 12, 2)
            return years
        return None

    @property
    def child_assent(self):
        """"Returns a wrapped saved or unsaved child assent
        """
        model_obj = self.assent_model_obj or self.assent_model_cls(
            **self.create_assent_options)
        return ChildAssentModelWrapper(model_obj=model_obj)

    @property
    def create_assent_options(self):
        """Returns a dictionary of options to create a new
        unpersisted child assent model instance.
        """

        options = dict(
            screening_identifier=self.screening_identifier,
            version=self.assent_version)
        if getattr(self, 'consent_model_obj'):
            # import pdb; pdb.set_trace()
            options.update(
                {'dob': self.consent_model_obj.child_dob})
        return options

    # @property
    # def screening_identifier(self):
    #     if self.assent_model_obj:
    #         return self.assent_model_obj.screening_identifier
    #     return None

    @property
    def assent_options(self):
        """Returns a dictionary of options to get an existing
         child assent model instance.
        """
        options = dict(
            screening_identifier=self.screening_identifier,
            version=self.assent_version)
        return options
