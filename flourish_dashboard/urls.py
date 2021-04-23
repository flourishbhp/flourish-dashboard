"""flourish_dashboard URL Configuration
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from edc_dashboard import UrlConfig

from .patterns import subject_identifier, screening_identifier, study_maternal_identifier
from .views import (
    ChildListboardView, ChildDashboardView, ChildScreeningListboardView,
    MaternalScreeningListBoardView, MaternalSubjectListboardView,
    MaternalDatasetListBoardView, MaternalDashboardView, LocatorLogReportView)

app_name = 'flourish_dashboard'

child_dashboard_url_config = UrlConfig(
    url_name='child_dashboard_url',
    view_class=ChildDashboardView,
    label='child_dashboard',
    identifier_label='subject_identifier',
    identifier_pattern=subject_identifier)

child_listboard_url_config = UrlConfig(
    url_name='child_listboard_url',
    view_class=ChildListboardView,
    label='child_subject_listboard',
    identifier_label='subject_identifier',
    identifier_pattern=subject_identifier)

child_screening_listboard_url_config = UrlConfig(
    url_name='child_screening_listboard_url',
    view_class=ChildScreeningListboardView,
    label='child_screening_listboard',
    identifier_label='screening_identifier',
    identifier_pattern=screening_identifier)

maternal_screening_listboard_url_config = UrlConfig(
    url_name='maternal_screening_listboard_url',
    view_class=MaternalScreeningListBoardView,
    label='maternal_screening_listboard',
    identifier_label='screening_identifier',
    identifier_pattern=screening_identifier)

subject_dashboard_url_config = UrlConfig(
    url_name='subject_dashboard_url',
    view_class=MaternalDashboardView,
    label='subject_dashboard',
    identifier_label='subject_identifier',
    identifier_pattern=subject_identifier)

maternal_dataset_listboard_url_config = UrlConfig(
    url_name='maternal_dataset_listboard_url',
    view_class=MaternalDatasetListBoardView,
    label='maternal_dataset_listboard',
    identifier_label='study_maternal_identifier',
    identifier_pattern=study_maternal_identifier)

subject_listboard_url_config = UrlConfig(
    url_name='subject_listboard_url',
    view_class=MaternalSubjectListboardView,
    label='maternal_subject_listboard',
    identifier_label='subject_identifier',
    identifier_pattern=subject_identifier)

urlpatterns = [
    path('locator_logs_report', LocatorLogReportView.as_view(),
         name='locator_report_url'),
]

urlpatterns += child_dashboard_url_config.dashboard_urls
urlpatterns += child_listboard_url_config.listboard_urls
urlpatterns += child_screening_listboard_url_config.listboard_urls
urlpatterns += subject_listboard_url_config.listboard_urls
urlpatterns += maternal_dataset_listboard_url_config.listboard_urls
urlpatterns += maternal_screening_listboard_url_config.listboard_urls
urlpatterns += subject_dashboard_url_config.dashboard_urls
