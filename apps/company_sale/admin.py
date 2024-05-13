from django.contrib import admin
from .models import Company, Sale, BundleService, Bundle, SaleVoucherGenerator, VoucherSale

# Register your models here.

admin.site.register(Company)
admin.site.register(Sale)
admin.site.register(BundleService)
admin.site.register(Bundle)
admin.site.register(SaleVoucherGenerator)
admin.site.register(VoucherSale)