from django.apps import apps as django_apps
from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('flourish_dashboard/buttons/child_dashboard_button.html')
def child_dashboard_button(model_wrapper):
    child_dashboard_url = settings.DASHBOARD_URL_NAMES.get(
        'child_dashboard_url')
    return dict(
        child_dashboard_url=child_dashboard_url,
        subject_identifier=model_wrapper.object.subject_identifier,
        assent_obj=model_wrapper.assent_model_obj,
        consent_obj=model_wrapper.object)


@register.inclusion_tag('flourish_dashboard/buttons/eligibility_button.html')
def eligibility_button(screening_model_wrapper):
    comment = []
    obj = screening_model_wrapper.object
    tooltip = None
    if obj.ineligibility:
        comment = obj.ineligibility[1:-1].split(',')
        comment = list(set(comment))
        comment.sort()
    return dict(eligible=obj.is_eligible, comment=comment,
                tooltip=tooltip, obj=obj)


@register.inclusion_tag('flourish_dashboard/buttons/edit_screening_button.html')
def edit_screening_button(model_wrapper):
    title = ['Edit Subject Screening form.']
    return dict(
        screening_identifier=model_wrapper.object.screening_identifier,
        href=model_wrapper.href,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/edit_maternal_dataset_button.html')
def edit_maternal_dataset_button(model_wrapper):
    title = ['Edit Maternal Dataset form.']
    return dict(
        screening_identifier=model_wrapper.object.screening_identifier,
        href=model_wrapper.href,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/screening_button.html')
def screening_button(model_wrapper):
    return dict(
        add_screening_href=model_wrapper.maternal_screening.href,
        screening_identifier=model_wrapper.object.screening_identifier,
        maternal_screening_obj=model_wrapper.screening_model_obj,
        caregiver_locator_obj=model_wrapper.locator_model_obj)


@register.inclusion_tag('flourish_dashboard/buttons/bhp_prior_screening_button.html')
def bhp_prior_screening_button(model_wrapper):
    return dict(
        add_screening_href=model_wrapper.bhp_prior_screening.href,
        screening_identifier=model_wrapper.screening_identifier,
        prior_screening_obj=model_wrapper.bhp_prior_screening_model_obj,
        caregiver_locator_obj=model_wrapper.locator_model_obj)


@register.inclusion_tag('flourish_dashboard/buttons/antenatal_enrollment_button.html')
def antenatal_enrollment_button(model_wrapper):
    title = ['subject antenatal enrollment.']

    preg_screening_cls = django_apps.get_model('flourish_caregiver.screeningpregwomen')
    try:
        preg_screening_obj = preg_screening_cls.objects.get(
            screening_identifier=model_wrapper.consent.screening_identifier)
    except preg_screening_cls.DoesNotExist:
        preg_screening_obj = None

    return dict(
        subject_identifier=model_wrapper.consent.subject_identifier,
        add_anternatal_enrollment_href=model_wrapper.antenatal_enrollment.href,
        antenatal_enrollment_model_obj=model_wrapper.antenatal_enrollment_model_obj,
        screening_identifier=model_wrapper.object.screening_identifier,
        preg_screening_obj=preg_screening_obj,
        title=' '.join(title),)


@register.inclusion_tag('flourish_dashboard/buttons/locator_button.html')
def locator_button(model_wrapper):
    return dict(
        add_locator_href=model_wrapper.caregiver_locator.href,
        screening_identifier=model_wrapper.object.screening_identifier,
        caregiver_locator_obj=model_wrapper.locator_model_obj)


@register.inclusion_tag('flourish_dashboard/buttons/consent_button.html')
def consent_button(model_wrapper):
    title = ['Consent subject to participate.']
    return dict(
        subject_identifier=model_wrapper.consent.object.subject_identifier,
        subject_screening_obj=model_wrapper.object,
        add_consent_href=model_wrapper.consent.href,
        consent_version=model_wrapper.consent_version,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/assent_button.html')
def assent_button(model_wrapper):
    title = ['Assent child to participate.']
    return dict(
        consent_obj=model_wrapper.object,
        assent_age=model_wrapper.child_age > 7,
        child_assent=model_wrapper.child_assent,
        add_assent_href=model_wrapper.child_assent.href,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/assents_button.html')
def assents_button(model_wrapper):
    title = ['Child Assent(s)']
    return dict(
        wrapped_assents=model_wrapper.child_assents,
        title=' '.join(title),)


@register.inclusion_tag('flourish_dashboard/buttons/dashboard_button.html')
def dashboard_button(model_wrapper):
    subject_dashboard_url = settings.DASHBOARD_URL_NAMES.get(
        'subject_dashboard_url')
    return dict(
        subject_dashboard_url=subject_dashboard_url,
        subject_identifier=model_wrapper.consent_model_obj.subject_identifier,
        show_dashboard=model_wrapper.show_dashboard)
