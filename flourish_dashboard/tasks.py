import pytz
import pandas as pd
from datetime import datetime
from io import StringIO
from django.apps import apps as django_apps
from django.core.mail import EmailMessage

from flourish_dashboard.model_wrappers import ChildDummyConsentModelWrapper


tz = pytz.timezone('Africa/Gaborone')


def format_export_data(model_cls, queryset):
    data = []
    export_fields = ['subject_identifier', 'child_age', 'assent_date',
                     'enrol_cohort', 'current_cohort']
    for _id in queryset:
        obj = model_cls.objects.filter(
            subject_identifier=_id).latest('consent_datetime')
        wrapped_obj = ChildDummyConsentModelWrapper(obj)

        if wrapped_obj.eligible_for_protocol_completion is not True:
            continue

        record = {}
        for field in export_fields:
            field_value = getattr(wrapped_obj, field, '')
            if field_value == '':
                field_value = getattr(
                    wrapped_obj.object, field, '')

            record.update({f'{field}': field_value})

        for key, value in record.items():
            if isinstance(value, datetime):
                record[key] = value.strftime('%d-%m-%Y %H:%M')
            if key in ['child_age', ] and value:
                record[key] = round(value, 2)
        data.append(record)
    return data


def generate_csv_file(data, filename_prefix):
    df = pd.DataFrame(data)
    filename = f'{filename_prefix}_{datetime.now(tz).strftime("%Y_%m_%d_%H%M%S")}.csv'

    buffer = StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return filename, buffer.read()


def send_export_email(filecontent, filename, emails):
    subject = 'Off-study Eligible Participants'
    message = ('Please find attached the CSV export for off-study '
               'eligible participants requested')
    email_msg = EmailMessage(subject, message, to=emails)
    email_msg.attach(filename, filecontent, 'text/csv')
    email_msg.send()


def generate_offstudy_csv(filename_prefix, emails, model_name):
    model_cls = django_apps.get_model(model_name)
    idx_qs = set(model_cls.objects.values_list(
        'subject_identifier', flat=True))

    export_data = format_export_data(model_cls, idx_qs)
    filename, csv_content = generate_csv_file(export_data, filename_prefix)
    send_export_email(csv_content, filename, emails)
