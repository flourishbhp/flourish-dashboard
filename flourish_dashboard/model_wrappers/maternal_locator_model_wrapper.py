from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from edc_model_wrapper import ModelWrapper 


class MaternalLocatorModelWrapperMixin:

    @property
    def screening_identifier(self):
        if self.maternal_model_obj:
            return self.maternal_model_obj.screening_identifier
        return None

    @property
    def maternal_model_obj(self):
        """Returns a maternal model instance or None.
        """
        try:
            return self.maternal_locator_cls.objects.get(
                **self.maternal_locator_options)
        except ObjectDoesNotExist:
            return None

    @property
    def maternal_locator_cls(self):
        return django_apps.get_model('flourish_maternal.maternallocator')

    @property
    def create_maternal_locator_options(self):
        """Returns a dictionary of options to create a new
        unpersisted maternal locator model instance.
        """
        options = dict(
            screening_identifier=self.object.screening_identifier)
        return options


class MaternalLocatorModelWrapper(MaternalLocatorModelWrapperMixin,
                                    ModelWrapper):

    model = 'flourish_maternal.maternallocator'
    querystring_attrs = ['screening_identifier']
    next_url_attrs = ['screening_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
                                'maternal_locator_listboard_url')

    @property
    def maternal_locator(self):
        """"Returns a wrapped saved or unsaved maternal locator
        """
        model_obj = self.maternal_model_obj or self.maternal_locator_cls(
            **self.maternal_locator_options)
        return self(model_obj=model_obj)
