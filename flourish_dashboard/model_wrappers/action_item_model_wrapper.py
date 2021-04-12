from django.conf import settings
from edc_action_item.model_wrappers import ActionItemModelWrapper as BaseActionItemModelWrapper


class ActionItemModelWrapper(BaseActionItemModelWrapper):

    next_url_name = settings.DASHBOARD_URL_NAMES.get('child_dashboard_url')
