from django.conf import settings
from edc_model_wrapper import ModelWrapper

from .child_assent_model_wrapper_mixin import ChildAssentModelWrapperMixin
from .consent_model_wrapper_mixin import ConsentModelWrapperMixin


class FacetScreeningModelWrapper(ConsentModelWrapperMixin,
                                 ChildAssentModelWrapperMixin,
                                 ModelWrapper):

    model = 'flourish_facet.facetsubjectscreening'
    querystring_attrs = ['subject_identifier']
    next_url_attrs = ['subject_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_dashboard_url')
