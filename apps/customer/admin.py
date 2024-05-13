from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from .models import Customer, PricingCriterionCustomer


class CustomerAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name','user__username', 'user__email']


admin.site.register(Customer,CustomerAdmin)
admin.site.register(PricingCriterionCustomer)
