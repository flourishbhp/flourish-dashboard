from edc_base.utils import age, get_utcnow


class FlourishDashboardUtils:

    def child_age(self, infant_dob):
        years = None
        if infant_dob:
            birth_date = infant_dob
            child_age = age(birth_date, get_utcnow())
            years = round(child_age.years + (child_age.months / 12), 2)
        return years if years else 0


flourish_dashboard_utils = FlourishDashboardUtils()
