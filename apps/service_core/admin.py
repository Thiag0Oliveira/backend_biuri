from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from .models import (
    Attendance, AttendanceService, Category, PricingCriterion, PricingCriterionOptions, Service,
	AttendanceProfessionalConfirmation, CancelationReason, AttendanceCancelation
)

from apps.payment.models import Transaction


class ServiceAdmin(admin.TabularInline):
	model = Service
	Extra = 0

class TransactionAdmin(admin.TabularInline):
	model = Transaction
	raw_id_fields = ['transfer',]
	Extra = 0

class CategoryAdmin(admin.ModelAdmin):
	inlines = (ServiceAdmin,)

class PricingCriterionOptionAdmin(admin.TabularInline):
	model = PricingCriterionOptions
	Extra = 0

class PricingCriterionAdmin(admin.ModelAdmin):
	inlines = (PricingCriterionOptionAdmin,)

class AttendanceServiceAdmin(admin.TabularInline):
	model = AttendanceService
	raw_id_fields = ['service']
	Extra = 0

class AttendanceAdmin(admin.ModelAdmin):
	raw_id_fields = ['customer', 'professional', 'address', 'neighborhood', 'initial_service', 'credit_card', 'voucher']
	list_display = ['id','initial_service','status','professional', 'customer', 'scheduling_date',]
	search_fields = ['pk', 'customer__user__first_name', 'professional__user__first_name', 'professional__user__username']
	list_filter = ['scheduling_date','status']
	inlines = (AttendanceServiceAdmin,TransactionAdmin,)

admin.site.register(Service,SimpleHistoryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Attendance,AttendanceAdmin)
admin.site.register(AttendanceService,SimpleHistoryAdmin)
admin.site.register(PricingCriterion,PricingCriterionAdmin)
admin.site.register(AttendanceProfessionalConfirmation)
admin.site.register(CancelationReason)
admin.site.register(AttendanceCancelation)