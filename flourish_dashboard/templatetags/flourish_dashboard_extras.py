from django import template


register = template.Library()


@register.inclusion_tag('flourish_dashboard/buttons/edit_screening_button.html')
def edit_screening_button(model_wrapper):
    title = ['Edit Subject Screening form.']
    return dict(
        screening_identifier=model_wrapper.object.screening_identifier,
        href=model_wrapper.href,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/edit_locator_button.html')
def edit_locator_button(model_wrapper):
    title = ['Edit Subject Locator form.']
    return dict(
        screening_identifier=model_wrapper.object.screening_identifier,
        href=model_wrapper.href,
        title=' '.join(title))


@register.inclusion_tag('flourish_dashboard/buttons/screening_button.html')
def screening_button(model_wrapper):
    return dict(
        add_screening_href=model_wrapper.maternal_screening.href,
        screening_identifier=model_wrapper.object.screening_identifier,
        maternal_screening_obj=model_wrapper.screening_model_obj)


@register.inclusion_tag('flourish_dashboard/buttons/locator_button.html')
def locator_button(model_wrapper):
    return dict(
        add_locator_href=model_wrapper.maternal_locator.href,
        screening_identifier=model_wrapper.object.screening_identifier,
        maternal_locator_obj=model_wrapper.locator_model_obj)


@register.inclusion_tag('flourish_dashboard/buttons/consent_button.html')
def consent_button(model_wrapper):
    title = ['Consent subject to participate.']
    return dict(
        screening_identifier=model_wrapper.object.screening_identifier,
        subject_identifier=model_wrapper.subject_identifier,
        subject_screening_obj=model_wrapper.object,
        add_consent_href=model_wrapper.subject_consent.href,
#         consent_version=model_wrapper.consent_version,
        title=' '.join(title))
