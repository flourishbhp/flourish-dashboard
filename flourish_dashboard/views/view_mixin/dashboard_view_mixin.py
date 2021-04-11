from django.core.exceptions import ObjectDoesNotExist
from edc_action_item.site_action_items import site_action_items
from edc_constants.constants import OFF_STUDY, NEW


class DashboardViewMixin:

    def get_offstudy_or_message(self, visit_cls=None, offstudy_cls=None,
                                offstudy_action=None):

        subject_identifier = self.kwargs.get('subject_identifier')
        obj = visit_cls.objects.filter(
            appointment__subject_identifier=subject_identifier,
            study_status=OFF_STUDY).order_by('report_datetime').last()
        if not obj:
            self.delete_action_item_if_new(offstudy_cls)
        else:
            self.action_cls_item_creator(
                subject_identifier=subject_identifier,
                action_cls=offstudy_cls,
                action_type=offstudy_action)
        return obj

    def action_cls_item_creator(
            self, subject_identifier=None, action_cls=None, action_type=None):
        action_cls = site_action_items.get(
            action_cls.action_name)
        action_item_model_cls = action_cls.action_item_model_cls()
        try:
            action_item_model_cls.objects.get(
                subject_identifier=subject_identifier,
                action_type__name=action_type)
        except ObjectDoesNotExist:
            action_cls(
                subject_identifier=subject_identifier)

    def delete_action_item_if_new(self, action_model_cls):
        action_item_obj = self.get_action_item_obj(action_model_cls)
        if action_item_obj:
            action_item_obj.delete()

    def get_action_item_obj(self, model_cls):
        subject_identifier = self.kwargs.get('subject_identifier')
        action_cls = site_action_items.get(
            model_cls.action_name)
        action_item_model_cls = action_cls.action_item_model_cls()

        try:
            action_item_obj = action_item_model_cls.objects.get(
                subject_identifier=subject_identifier,
                action_type__name=model_cls.action_name,
                status=NEW)
        except action_item_model_cls.DoesNotExist:
            return None
        return action_item_obj
