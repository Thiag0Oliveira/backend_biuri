from django.contrib import admin

from .models import Address, City, Neighborhood, Place, State

class CityAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'state']
    list_filter = ['is_covered', 'state']

class NeighborhoodAdmin(admin.ModelAdmin):
    raw_id_fields = ['city', 'father']
    list_filter = ['city']

admin.site.register(Address)
admin.site.register(City, CityAdmin)
admin.site.register(Neighborhood, NeighborhoodAdmin)
admin.site.register(State)
admin.site.register(Place)

