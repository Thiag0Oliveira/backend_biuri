from django.contrib import admin

import nested_admin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    Badge, EvaluationCustomer, EvaluationType, Executive, FavoriteProfessional, Professional,
    ProfessionalBadge, ProfessionalCategory, ProfessionalCity, ProfessionalEvaluation,
    ProfessionalSchedule, Schedule, ServiceProfessional, ServiceProfessionalPricingCriterion,
    ProfessionalScheduleDefault,ServiceProfessionalLog,
    DocumentType, ContractClause, Contract, ProfessionalDocument, ProfessionalPicture,
    Seller, ProfessionalCriterion, SaloonScheduleRemove)


class ServiceProfessionalPricingCriterionAdmin(nested_admin.NestedStackedInline):
    model = ServiceProfessionalPricingCriterion

class ServiceAdmin(nested_admin.NestedTabularInline):
    model = ServiceProfessional
    inlines = [ServiceProfessionalPricingCriterionAdmin,]

class ScheduleAdmin(nested_admin.NestedTabularInline):
    model = Schedule

class ProfessionalEvaluationAdmin(nested_admin.NestedTabularInline):
    model = ProfessionalEvaluation

class ProfessionalBadgeAdmin(nested_admin.NestedTabularInline):
    model = ProfessionalBadge

class ProfessionalAdmin(nested_admin.NestedModelAdmin):
    list_filter = ['professional_enabled',]
    search_fields = ['search_text',]
    list_display = ['id', 'search_text', 'avatar', 'celphone', 'professional_enabled']
    inlines = [ProfessionalBadgeAdmin,]

class ScheduleAdmin(admin.ModelAdmin):
    raw_id_fields =['attendance', 'professional']
    list_display = ['id', 'daily_date', 'daily_time_begin', 'daily_time_end', 'attendance', 'professional',]
    list_filter = ['daily_date']

class ProfessionalScheduleAdmin(admin.ModelAdmin):
    raw_id_fields =['professional']
    list_display = ['id', 'date_schedule', 'professional']
    list_filter = ['date_schedule']



class SaloonScheduleRemoveAdmin(admin.ModelAdmin):
    class Meta:
        model = SaloonScheduleRemove

admin.site.register(SaloonScheduleRemove,SaloonScheduleRemoveAdmin)
admin.site.register(Professional,ProfessionalAdmin)
admin.site.register(Schedule,ScheduleAdmin)
admin.site.register(FavoriteProfessional,SimpleHistoryAdmin)
admin.site.register(ServiceProfessional,SimpleHistoryAdmin)
admin.site.register(Badge, SimpleHistoryAdmin)
admin.site.register(EvaluationType)
admin.site.register(ProfessionalCategory)
admin.site.register(ProfessionalCity)
admin.site.register(Executive)
admin.site.register(ProfessionalSchedule, ProfessionalScheduleAdmin)
admin.site.register(EvaluationCustomer)
admin.site.register(ProfessionalScheduleDefault)
admin.site.register(ProfessionalEvaluation)
admin.site.register(DocumentType)
admin.site.register(Seller)
admin.site.register(ContractClause)
admin.site.register(Contract)
admin.site.register(ProfessionalDocument)
admin.site.register(ServiceProfessionalLog)
admin.site.register(ProfessionalPicture)
admin.site.register(ProfessionalCriterion)
