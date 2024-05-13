from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from apps.company_sale.views import Pdf, PdfSale
from . import views


urlpatterns = [
    url('pdf_voucher/(?P<voucher>[0-9]+)$', login_required(Pdf.as_view()), name='pdf-voucher'),
    url('pdf_voucher_sale/(?P<sale>[0-9]+)$', login_required(PdfSale.as_view()), name='pdf-sale'),
    url('voucher$', login_required(views.VoucherList.as_view()), name='voucher-list'),
    url('voucher/create$', login_required(views.VoucherCreate.as_view()), name='voucher-create'),
    url('voucher/(?P<pk>[0-9]+)/edit$', login_required(views.VoucherUpdate.as_view()), name='voucher-update')
]
