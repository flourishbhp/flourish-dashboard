from edc_dashboard.listboard_filter import ListboardFilter, ListboardViewFilters


class ListboardViewFilters(ListboardViewFilters):

    all = ListboardFilter(
        name='all',
        label='All',
        lookup={})

    on_worklist = ListboardFilter(
        label='On Worklist',
        position=10,
        lookup={'on_worklist': True})
