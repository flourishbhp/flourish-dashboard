from django.conf import settings
from edc_model_wrapper import ModelWrapper
from edc_odk.model_wrappers import NoteToFileModelWrapperMixin, \
    ClinicianNotesModelWrapperMixin, LabResultsModelWrapperMixin


class ChildBirthModelWrapper(NoteToFileModelWrapperMixin,
                             ClinicianNotesModelWrapperMixin,
                             LabResultsModelWrapperMixin,
                             ModelWrapper):
    model = 'flourish_child.childbirth'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'child_dashboard_url')
    next_url_attrs = ['subject_identifier']
    querystring_attrs = ['subject_identifier']
