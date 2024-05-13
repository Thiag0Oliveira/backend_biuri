from django import template
from django.template.defaultfilters import stringfilter

from apps.core.models import City
from apps.service_core.models import Category, PricingCriterionOptions, Service, ServiceProfessional
from apps.professional.models import DAYS_OF_WEEK, GENDER_ATTENDANCE

register = template.Library()

@register.filter
def category_name(value):
    """Removes all values of arg from the given string"""
    return str(Category.objects.get(pk=value).name)

@register.filter
def service_name(value):
    """Removes all values of arg from the given string"""
    return str(Service.objects.get(pk=value).name)

@register.filter
def service_professional_name(value):
    """Removes all values of arg from the given string"""
    return str(ServiceProfessional.objects.get(pk=value).service.name)

@register.filter
def city_name(value):
    """Removes all values of arg from the given string"""
    return str(City.objects.get(pk=value).name)

@register.filter
def pricing_criterion_options(value):
    """Removes all values of arg from the given string"""
    pricing_criterion_option = PricingCriterionOptions.objects.get(pk=value)
    return str(str(pricing_criterion_option.pricing_criterion.description) + ' - ' + str(pricing_criterion_option.description))

@register.filter
def day_of_week(value):
    return DAYS_OF_WEEK[int(value)][1]

@register.filter
def gender_attendance(value):
    return GENDER_ATTENDANCE[value]

register.filter('category_name', category_name)
register.filter('service_name', service_name)
register.filter('service_professional_name', service_professional_name)
register.filter('pricing_criterion_options', pricing_criterion_options)
register.filter('city_name', city_name)
register.filter('day_of_week', day_of_week)
