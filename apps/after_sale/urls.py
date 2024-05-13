from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    url('attendance/list$', views.AttendanceList.as_view(),
        name='attendance_list'),
    url('transaction/list$', views.TransactionList.as_view(),
        name='transaction_list'),
    url('attendance/(?P<pk>[0-9]+)/edit$', login_required(views.AttendanceDetail.as_view()),
        name='attendance-detail'),
    url('attendance/(?P<pk>[0-9]+)/update$', login_required(views.AttendanceUpdate.as_view()),
        name='attendance-update'),
    url('ajax/get_voucher/$', views.get_voucher, name='get_voucher'),
    url('ajax/update_price/$', views.update_price, name='update_price'),
    url('ajax/attendance_service_delete/$', views.attendance_service_delete, name='attendance_service_delete'),
    url('ajax/attendance_service_edit/$', views.attendance_service_edit, name='attendance_service_edit'),
    url('ajax/get_attendance_service/$', views.get_attendance_service, name='get_attendance_service'),
    url('ajax/get_services/$', views.get_services, name='get_services'),
    url('ajax/create_attendance_service/$', views.create_attendance_service, name='create_attendance_service')

]
