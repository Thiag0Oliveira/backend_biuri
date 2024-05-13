from django.contrib import admin

from .models import Lead


# Register your models here.

class LeadAdmin(admin.ModelAdmin):
    list_display = ['name','email','telephone','status', 'get_categorys','created']
    list_filter = ['category', 'type', 'status']
    search_fields = ['name','cpf','rg','celphone']

    def get_categorys(self, obj):
        return "\n".join([p.name for p in obj.category.all()])

admin.site.register(Lead,LeadAdmin)
