from django.contrib import admin

from .models import Address, UserAddress


admin.site.register(Address)
admin.site.register(UserAddress)
