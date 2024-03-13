from urllib.parse import unquote, urlencode

from django import template
from django.apps import apps as django_apps
from django.conf import settings
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from edc_base.utils import age, get_utcnow
from edc_visit_schedule.models import SubjectScheduleHistory

from flourish_dashboard.utils import flourish_dashboard_utils

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_values_unique(dictionary):
    return set(list(dictionary.values()))


@register.filter
def get_keys(dictionary, value):
    return [k for k, v in dictionary.items() if v == value]


@register.filter
def readable_cohort(cohort):
    return cohort.replace('_', ' ')


@register.filter
def get_schedule_names(onschedules, child_subject_identifier):
    if child_subject_identifier:
        schedule_names = [model.schedule_name for model in onschedules if
                          model.child_subject_identifier == child_subject_identifier]
    else:
        schedule_names = [model.schedule_name for model in onschedules]
    return schedule_names


@register.simple_tag(takes_context=True)
def get_age(context, born=None):
    if born:
        reference_datetime = context.get('reference_datetime', get_utcnow())
        participant_age = age(born, reference_datetime)
        age_str = ''
        age_months = participant_age.months % 12
        if participant_age.years > 0:
            age_str += str(participant_age.years) + ' yrs '
        if age_months > 0:
            age_str += str(age_months) + ' months'
        return age_str


@register.inclusion_tag('flourish_dashboard/buttons/child_dashboard_button.html')
def child_dashboard_button(model_wrapper):
    child_dashboard_url = settings.DASHBOARD_URL_NAMES.get(
        'child_dashboard_url')
    return dict(
        child_dashboard_url=child_dashboard_url,
        subject_identifier=model_wrapper.subject_identifier)


@register.inclusion_tag('pre_flourish/buttons/heu_dashboard_button.html')
def huu_match_child_dashboard_button(subject_identifier):
    child_dashboard_url = settings.DASHBOARD_URL_NAMES.get(
        'pre_flourish_child_dashboard_url')
    return dict(
        child_dashboard_url=child_dashboard_url,
        subject_identifier=subject_identifier)


@register.inclusion_tag('flourish_dashboard/buttons/eligibility_button.html')
def eligibility_button(model_wrapper):
    comment = []
    eligible = []
    objs = model_wrapper.object.screeningpregwomeninline_set.all()
    tooltip = None
    for obj in objs:
        if not obj.is_eligible:
            comment = obj.ineligibility[1:-1].split(',')
            comment = list(set(comment))
            comment.sort()
        eligible.append(obj.is_eligible)
    return dict(eligible=any(eligible), comment=comment,
                tooltip=tooltip, obj=objs)


@register.inclusion_tag(
    'flourish_dashboard/buttons/child_eligibility_button.html')
def child_eligibility_button(children_ineligible):
    comments = []
    comment = []
    tooltip = None
    for child_ineligible in children_ineligible:
        if not child_ineligible.is_eligible:
            comment = child_ineligible.ineligibility[1:-1].split(',')
        comment = list(set(comment))
        comment.sort()
        comments.append(comment)
    consent_ineligible_pair = zip(children_ineligible, comments)
    return dict(
        comment=comment,
        tooltip=tooltip,
        consent_ineligible_pair=consent_ineligible_pair,
        children_ineligible=children_ineligible)


@register.inclusion_tag(
    'flourish_dashboard/buttons/child_ineligible_button.html')
def child_ineligible_button(model_wrapper):
    tooltip = 'See child screening for details.'
    url_name = 'flourish_dashboard:child_screening_listboard_url'
    options = {'screening_identifier': model_wrapper.screening_identifier}
    child_screening_url = reverse(url_name, kwargs=options)
    return dict(
        tooltip=tooltip,
        child_screening_url=child_screening_url,
        ineligible_children=model_wrapper.overall_ineligible)


@register.inclusion_tag('flourish_dashboard/buttons/edit_screening_button.html')
def edit_screening_button(model_wrapper):
    title = ['Edit Subject Screening form.']
    return dict(
        screening_identifier=model_wrapper.object.screening_identifier,
        href=model_wrapper.href,
        title=' '.join(title))


@register.inclusion_tag(
    'flourish_dashboard/buttons/edit_maternal_dataset_button.html')
def edit_maternal_dataset_button(model_wrapper):
    title = ['Edit Maternal Dataset form.']
    return dict(
        screening_identifier=model_wrapper.object.screening_identifier,
        href=model_wrapper.href,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/screening_button.html')
def screening_button(model_wrapper):
    options = {}
    if hasattr(model_wrapper, 'maternal_screening'):
        options = dict(
            add_screening_href=model_wrapper.maternal_screening.href,
            screening_identifier=model_wrapper.object.screening_identifier,
            maternal_screening_obj=model_wrapper.screening_model_obj,
            caregiver_locator_obj=model_wrapper.locator_model_obj)
    else:
        options = dict(
            add_screening_href=model_wrapper.href,
            screening_identifier=model_wrapper.object.screening_identifier,
            maternal_screening_obj=model_wrapper.object,
            caregiver_locator_obj=model_wrapper.locator_model_obj)

    return options


@register.inclusion_tag(
    'flourish_dashboard/buttons/bhp_prior_screening_button.html')
def bhp_prior_screening_button(model_wrapper):
    return dict(
        add_screening_href=model_wrapper.bhp_prior_screening.href,
        screening_identifier=model_wrapper.screening_identifier,
        prior_screening_obj=model_wrapper.bhp_prior_screening_model_obj,
        caregiver_locator_obj=model_wrapper.locator_model_obj)


@register.inclusion_tag(
    'flourish_dashboard/buttons/antenatal_enrollment_button.html')
def antenatal_enrollment_button(model_wrapper):
    title = ['Child Antenatal Enrollment(s)']
    unsaved = any(
        instance.id is None for instance in model_wrapper.antenatal_enrollments)
    return dict(
        wrapped_antenatal_enrollments=model_wrapper.antenatal_enrollments,
        unsaved=unsaved,
        title=' '.join(title), )


@register.inclusion_tag(
    'flourish_dashboard/buttons/maternal_delivery_button.html')
def maternal_delivery_button(model_wrapper):
    title = ['subject maternal deliveries.']
    unsaved = any(
        instance.id is None for instance in model_wrapper.maternal_deliveries)

    return dict(
        wrapped_maternal_deliveries=model_wrapper.maternal_deliveries,
        unsaved=unsaved,
        title=' '.join(title), )


@register.inclusion_tag('flourish_dashboard/buttons/locator_button.html')
def locator_button(model_wrapper):
    return dict(
        add_locator_href=model_wrapper.caregiver_locator.href,
        screening_identifier=model_wrapper.object.screening_identifier,
        caregiver_locator_obj=model_wrapper.locator_model_obj)


@register.inclusion_tag(
    'flourish_dashboard/buttons/caregiver_enrolment_info_button.html')
def caregiver_enrolment_info_button(model_wrapper):
    bhp_prior_screening = getattr(model_wrapper,
                                  'bhp_prior_screening_model_obj', None)
    return dict(
        add_caregiver_enrol_info_href=model_wrapper.caregiver_enrolment_info.href,
        subject_identifier=model_wrapper.object.subject_identifier,
        caregiver_enrolment_info_obj=model_wrapper.caregiver_enrolment_info_obj,
        bhp_prior_screening=bhp_prior_screening)


@register.inclusion_tag('flourish_dashboard/buttons/consent_button.html')
def consent_button(model_wrapper, antenatal=None):
    title = ['Consent subject to participate.']
    subject_screening_obj = model_wrapper.object
    screening_obj_inlines = getattr(
        subject_screening_obj, 'screeningpregwomeninline_set', None)
    non_complete_screening_objs = False
    if screening_obj_inlines:
        non_complete_screening_objs = screening_obj_inlines.filter(
            child_subject_identifier__isnull=True).exists()

    return dict(
        consent_model_obj=model_wrapper.consent_model_obj,
        subject_screening_obj=subject_screening_obj,
        add_consent_href=model_wrapper.consent.href,
        consent_version=model_wrapper.consent_version,
        non_complete_screening_objs=non_complete_screening_objs,
        antenatal=antenatal,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/assent_button.html')
def assent_button(model_wrapper):
    title = ['Assent child to participate.']
    return dict(
        consent_obj=model_wrapper.object,
        assent_age=model_wrapper.child_age >= 7,
        child_assent=model_wrapper.child_assent,
        title=' '.join(title))


@register.inclusion_tag(
    'flourish_dashboard/buttons/caregiverchildconsent_button.html')
def caregiverchildconsent_button(model_wrapper):
    title = ['Caregiver Child Consent']
    return dict(
        consent_obj=model_wrapper.object.subject_consent,
        caregiver_childconsent=model_wrapper.caregiverchildconsent_obj,
        add_caregiverchildconsent_href=model_wrapper.href,
        title=' '.join(title))


@register.inclusion_tag(
    'flourish_dashboard/buttons/caregiver_contact_button.html')
def caregiver_contact_button(model_wrapper):
    title = ['Caregiver Contact.']
    return dict(
        subject_identifier=model_wrapper.object.subject_identifier,
        add_caregiver_contact_href=model_wrapper.caregiver_contact.href,
        title=' '.join(title), )


@register.inclusion_tag(
    'flourish_dashboard/buttons/child_tb_referal_button.html')
def tb_adol_referal_button(model_wrapper):
    return dict(
        subject_identifier=model_wrapper.object.subject_identifier,
        href=model_wrapper.href, )


@register.inclusion_tag(
    'flourish_dashboard/buttons/childcontinuedconsent_button.html')
def childcontinuedconsent_button(model_wrapper):
    title = ['Child Continued Consent']
    return dict(
        child_age=model_wrapper.child_age,
        childcontinuedconsent=getattr(
            model_wrapper, 'child_continued_consent_model_obj', None),
        add_childcontinuedconsent_href=model_wrapper.child_continued_consent.href,
        title=' '.join(title))


@register.inclusion_tag(
    'flourish_dashboard/buttons/childcontinuedconsents_button.html')
def childcontinuedconsents_button(model_wrapper):
    title = 'Child Continued Consents(s)'
    child_continued_consents = list(model_wrapper.child_continued_consents)
    unsaved = any(instance.id is None for instance in child_continued_consents)

    return {
        'wrapped_continued_consents': child_continued_consents,
        'unsaved': unsaved,
        'title': title
    }


@register.inclusion_tag('flourish_dashboard/buttons/assents_button.html')
def assents_button(model_wrapper):
    title = ['Child Assent(s)']
    unsaved = any(
        instance.id is None for instance in model_wrapper.child_assents)
    return dict(
        wrapped_assents=model_wrapper.child_assents,
        unsaved=unsaved,
        title=' '.join(title), )


@register.inclusion_tag('flourish_dashboard/buttons/tb_adol_assents_button.html')
def tb_adol_assents_button(model_wrapper):
    title = ['TB Adol Assent(s)']
    unsaved = any(
        instance.id is None for instance in model_wrapper.tb_adol_assents)
    return dict(
        model_wrapper=model_wrapper,
        wrapped_assents=model_wrapper.tb_adol_assents,
        unsaved=unsaved,
        title=' '.join(title), )


@register.inclusion_tag('flourish_dashboard/buttons/tb_adol_assent_button.html')
def tb_adol_assent_button(model_wrapper):
    title = ['TB Adol. Assent to participate.']

    return dict(
        consent_obj=model_wrapper.object,
        assent_age=model_wrapper.child_age >= 10,
        tb_adol_assent=model_wrapper.tb_adol_assent,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/dashboard_button.html')
def dashboard_button(model_wrapper):
    subject_dashboard_url = settings.DASHBOARD_URL_NAMES.get(
        'subject_dashboard_url')
    return dict(
        subject_dashboard_url=subject_dashboard_url,
        subject_identifier=model_wrapper.consent.subject_identifier)


@register.inclusion_tag(
    'flourish_dashboard/buttons/caregiver_dashboard_button.html')
def caregiver_dashboard_button(model_wrapper):
    subject_dashboard_url = settings.DASHBOARD_URL_NAMES.get(
        'subject_dashboard_url')

    subject_identifier = model_wrapper.object \
        .subject_consent.subject_identifier

    return dict(
        subject_dashboard_url=subject_dashboard_url,
        subject_identifier=subject_identifier)


@register.inclusion_tag(
    'flourish_dashboard/buttons/maternal_dataset_button.html')
def maternal_dataset_button(model_wrapper):
    title = ['View Maternal Dataset form.']
    return dict(
        screening_identifier=model_wrapper.object.screening_identifier,
        href=model_wrapper.href,
        title=' '.join(title))


@register.inclusion_tag(
    'flourish_dashboard/maternal_subject/dashboard/infant_dashboard_links.html')
def infant_dash_link(subject_identifier):
    caregiver_child_consent = django_apps.get_model(
        'flourish_caregiver.caregiverchildconsent')

    try:
        child_obj = caregiver_child_consent.objects.get(
            subject_identifier=subject_identifier)
    except caregiver_child_consent.DoesNotExist:
        return None
    else:
        return dict(
            full_names=child_obj.first_name + " " + child_obj.last_name,
            first_name=child_obj.first_name,
            last_name=child_obj.last_name)


@register.inclusion_tag('edc_visit_schedule/subject_schedule_footer_row.html')
def subject_schedule_footer_row(subject_identifier, visit_schedule, schedule,
                                subject_dashboard_url):
    context = {}
    try:
        history_obj = SubjectScheduleHistory.objects.get(
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            subject_identifier=subject_identifier,
            offschedule_datetime__isnull=False)
    except SubjectScheduleHistory.DoesNotExist:
        onschedule_model_obj = schedule.onschedule_model_cls.objects.get(
            subject_identifier=subject_identifier,
            schedule_name=schedule.name, )
        options = dict(subject_identifier=subject_identifier)
        query = unquote(urlencode(options))
        href = (
            f'{visit_schedule.offstudy_model_cls().get_absolute_url()}?next='
            f'{subject_dashboard_url},subject_identifier')
        href = '&'.join([href, query])
        context = dict(
            offschedule_datetime=None,
            onschedule_datetime=onschedule_model_obj.onschedule_datetime,
            href=mark_safe(href))
    else:
        onschedule_model_obj = schedule.onschedule_model_cls.objects.get(
            subject_identifier=subject_identifier,
            schedule_name=schedule.name)
        options = dict(subject_identifier=subject_identifier)
        query = unquote(urlencode(options))
        offstudy_model_obj = None
        try:
            offstudy_model_obj = visit_schedule.offstudy_model_cls.objects.get(
                subject_identifier=subject_identifier)
        except visit_schedule.offstudy_model_cls.DoesNotExist:
            href = (f'{visit_schedule.offstudy_model_cls().get_absolute_url()}'
                    f'?next={subject_dashboard_url},subject_identifier')
        else:
            href = (f'{offstudy_model_obj.get_absolute_url()}?next='
                    f'{subject_dashboard_url},subject_identifier')

        href = '&'.join([href, query])

        context = dict(
            offschedule_datetime=history_obj.offschedule_datetime,
            onschedule_datetime=onschedule_model_obj.onschedule_datetime,
            href=mark_safe(href))
        if offstudy_model_obj:
            context.update(offstudy_date=offstudy_model_obj.offstudy_date)
    context.update(
        visit_schedule=visit_schedule,
        schedule=schedule,
        verbose_name=visit_schedule.offstudy_model_cls._meta.verbose_name)
    return context


@register.inclusion_tag('flourish_dashboard/buttons/child_dataset_button.html')
def child_dataset_button(model_wrapper):
    title = ['View Child Dataset form.']
    return dict(
        href=model_wrapper.href,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/child_birth_button.html')
def child_birth_button(child_birth_values):
    title = ['child birth.']
    return dict(
        subject_identifier=child_birth_values.subject_identifier,
        add_child_birth_href=child_birth_values.child_birth.href,
        child_birth_model_obj=child_birth_values.child_birth_obj,
        maternal_deliv_obj=child_birth_values.maternal_delivery_model_obj,
        title=' '.join(title), )


@register.inclusion_tag(
    'flourish_dashboard/buttons/caregiver_child_consent_button.html')
def caregiver_child_consent_button(model_wrapper):
    title = ['View Caregiver Consent on Behalf of Child form.']
    return dict(
        href=model_wrapper.href,
        title=' '.join(title))


@register.inclusion_tag(
    'flourish_dashboard/buttons/consent_version_button.html')
def consent_version_button(model_wrapper):
    title = ['Add Consent Version.']

    return dict(
        requires_child_version=flourish_dashboard_utils.requires_child_version(
            model_wrapper.object.subject_identifier,
            model_wrapper.object.screening_identifier),
        consent_versioned=model_wrapper.flourish_consent_version,
        screening_identifier=model_wrapper.object.screening_identifier,
        add_consent_version_href=model_wrapper.flourish_consent_version.href,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/child_off_study.html')
def child_off_study_button(model_wrapper):
    title = 'Child Subject Off Study'
    return dict(
        title=title,
        href=model_wrapper.child_offstudy.href,
        subject_identifier=model_wrapper.subject_identifier, )


@register.inclusion_tag('flourish_dashboard/buttons/missed_birth_visit_button.html')
def missed_birth_visit_button(model_wrapper):
    title = 'Missed Birth Visit'
    return dict(
        title=title,
        href=model_wrapper.missed_birth_visit.href,
        subject_identifier=model_wrapper.subject_identifier, )


@register.inclusion_tag('flourish_dashboard/buttons/caregiver_off_study.html')
def caregiver_off_study_button(model_wrapper):
    title = 'Caregiver Off Study'
    return dict(
        title=title,
        href=model_wrapper.caregiver_offstudy.href,
        subject_identifier=model_wrapper.subject_identifier
    )


@register.inclusion_tag(
    'flourish_dashboard/buttons/caregiver_death_report_button.html')
def caregiver_death_report_button(model_wrapper):
    title = 'Caregiver Death Report'
    return dict(
        title=title,
        href=model_wrapper.caregiver_death_report.href,
        subject_identifier=model_wrapper.subject_identifier
    )


@register.inclusion_tag('flourish_dashboard/buttons/child_death_report_button.html')
def child_death_report_button(model_wrapper):
    title = 'Child Death Report'
    return dict(
        title=title,
        href=model_wrapper.child_death_report.href,
        subject_identifier=model_wrapper.subject_identifier
    )


@register.inclusion_tag('flourish_dashboard/buttons/tb_consent_button.html')
def tb_consent_button(model_wrapper):
    title = ['TB Consent']
    consent_version = model_wrapper.tb_consent.version
    return dict(
        tb_consent=model_wrapper.tb_consent_model_obj,
        subject_identifier=model_wrapper.tb_consent.subject_identifier,
        add_consent_href=model_wrapper.tb_consent.href,
        consent_version=consent_version,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/young_adult_locator.html')
def young_adult_locator_button(model_wrapper):
    title = 'Young Adult Locator'
    return dict(
        wrapper=model_wrapper,
        title=title
    )


@register.inclusion_tag('flourish_dashboard/buttons/tb_adol_screening_button.html')
def tb_adol_screening_button(model_wrapper):
    title = ['TB Adol Screening']

    children_age = [age(consent.child_dob, get_utcnow()).years
                    for consent in model_wrapper.child_consents if consent.child_dob]
    age_adol_range = False
    for child_age in children_age:
        if child_age >= 10 and child_age <= 17:
            age_adol_range = True
            break

    return dict(
        tb_adol_screening=model_wrapper.tb_adol_screening_model_obj,
        subject_identifier=model_wrapper.tb_adol_screening.subject_identifier,
        add_adol_screening_href=model_wrapper.tb_adol_screening.href,
        age_adol_range=age_adol_range,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/tb_adol_consent_button.html')
def tb_adol_consent_button(model_wrapper):
    title = ['TB Adol Consent']
    consent_version = model_wrapper.tb_adol_consent_version

    return dict(
        tb_adol_consent=model_wrapper.tb_adol_consent_model_obj,
        subject_identifier=model_wrapper.tb_adol_consent.subject_identifier,
        add_adol_consent_href=model_wrapper.tb_adol_consent.href,
        consent_version=consent_version,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/tb_offstudy_button.html')
def tb_offstudy_button(model_wrapper):
    title = ['TB Off Study']
    return dict(
        tb_offstudy=model_wrapper.tb_offstudy_model_obj,
        subject_identifier=model_wrapper.tb_offstudy.subject_identifier,
        add_offstudy_href=model_wrapper.tb_offstudy.href,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/pre_flourish_birth_data_button.html')
def pre_flourish_birth_data_button(model_wrapper):
    title = ['Birth Data']
    return dict(
        pf_birth_data=model_wrapper.pf_birth_data_model_obj,
        subject_identifier=model_wrapper.pf_birth_data.subject_identifier,
        add_pf_birth_data_href=model_wrapper.pf_birth_data.href,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/facet_screening_button.html')
def facet_screening_button(model_wrapper):
    title = 'FACET Screening'
    status = 'btn-success' if model_wrapper.facet_screening_obj else 'btn-warning'

    return dict(
        facet_screening_obj=model_wrapper.facet_screening_obj,
        facet_screening_wrapper=model_wrapper.facet_screening_wrapper,
        title=title,
        status=status)


@register.inclusion_tag('flourish_dashboard/buttons/facet_consent_button.html')
def facet_consent_button(model_wrapper):
    title = 'FACET Consent'
    status = 'btn-success' if model_wrapper.facet_consent_obj else 'btn-warning'

    return dict(
        facet_consent_obj=model_wrapper.facet_consent_obj,
        facet_consent_wrapper=model_wrapper.facet_consent_wrapper,
        title=title,
        status=status)
