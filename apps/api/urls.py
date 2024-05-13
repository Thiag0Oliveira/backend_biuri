from django.conf.urls import url, include
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter

from apps.api import views

router = DefaultRouter()
router.register(r'schedule-remove', views.ScheduleRemoveViewSet, base_name="scheduleremoveviewset")


urlpatterns = [
    url(r'', include(router.urls)),
    url(r'^executiveslead/$', views.ExecutiveLeadList.as_view(), name='api_executiveslead'),
    url(r'^professionallead/$', views.LeadProfessionalApi.as_view(), name='api_professionallead'),
    url(r'^executiveslead/(?P<pk>[0-9]+)$', views.ExecutiveLeadDetail.as_view(), name='api_executivesleaddetail'),
    url(r'^accounts/password/reset/$', views.ResetPassword.as_view(), name='api_account_reset_password'),
    url(r'^accounts/signup/$', views.SignUp.as_view(), name='api_account_signup'),
    url(r'^accounts/login/$', views.Login.as_view(), name='api_account_login'),
    url(r'^accounts/login/facebook/$', views.FacebookLogin.as_view(), name='api_account_login_fb'),
    url(r'^accounts/login/convert_token/$', views.ConvertToken.as_view(), name='api_account_login_convert_token'),
    url(r'^accounts/refresh/token/$', views.RefreshToken.as_view(), name='api_refresh_token'),
    url(r'^accounts/profile/$', views.Profile.as_view(), name='api_profile'),
    url(r'^accounts/pushtoken/$', views.AppRegistrationAPI.as_view(), name='api_token'),
    url(r'^accounts/celphone/$', views.CelphoneAPI.as_view(), name='api_celphone'),
    url(r'^accounts/address/(?P<pk>[0-9]+)$', views.UserAddressApiDetail.as_view(), name='api_address_detail'),
    url(r'^accounts/address/$', views.UserAddressApiList.as_view(), name='api_address_list'),
    url(r'^accounts/initialstatus/$', views.InitialStatus.as_view(), name='api_initial_status'),
    url(r'^accounts/favorite_professional/$', views.FavoriteProfessionalApi.as_view(), name='favorite_professional'),

    url(r'^accounts/pushtoken/$', views.AppRegistrationAPI.as_view(), name='api_token'),
    url(r'^accounts/email-exists/$', views.ExistingEmailAPI.as_view(), name='email_exists'),
    
    url(r'^category/$', cache_page(60)(views.CategoryList.as_view()),  name='api_category'),

    url(r'^service/$', cache_page(60)(views.ServiceList.as_view()), name='api_service'),


    url(r'^attendance/$', views.AttendanceList.as_view(), name='api_attendance'),
    url(r'^attendance/(?P<pk>[0-9]+)$', views.AttendanceDetail.as_view(), name='api_attendance_detail'),
    url(r'^update-flex-attendance/(?P<pk>[0-9]+)$', views.UpdateFlexAttendance.as_view(), name='api_update-flex-attendance'),
    url(r'^attendance/(?P<pk>[0-9]+)/customer$', views.AttendanceUpdateAnonymous.as_view(), name='api_attendance_detail_customer'),
    url(r'^attendance/(?P<pk>[0-9]+)/professional$', views.AttendanceProfessional.as_view(),
        name='api_attendance_professional'),
    url(r'^attendance/(?P<pk>[0-9]+)/accepted$', views.AttendanceProfessionalAccepted.as_view(),
        name='api_attendance_professional_accepted'),
    url(r'^attendance/(?P<pk>[0-9]+)/address$', views.AttendanceAddress.as_view(),
        name='api_attendance_address'),
    url(r'^attendance/(?P<pk>[0-9]+)/credit_card$', views.AttendanceCreditCard.as_view(),
        name='api_attendance_creditcard'),
    url(r'^attendance/(?P<pk>[0-9]+)/split$', views.AttendanceSplitApi.as_view(),
        name='api_attendance_split'),
    url(r'^attendance/(?P<pk>[0-9]+)/schedule$', views.AttendanceSchedule.as_view(),
        name='api_attendance_schedule'),
    url(r'^attendance/(?P<pk>[0-9]+)/evaluation$', views.ProfessionalEvaluationPostApi.as_view(),
        name='api_attendance_evaluation'),
    url(r'^attendance/(?P<pk>[0-9]+)/professionalevaluation$', views.EvaluationFinalProfessional.as_view(),
        name='api_professional_evaluation'),
    url(r'^attendance/(?P<pk>[0-9]+)/extra$', views.ServiceProfessionalPricingCriterionAPI.as_view(),
        name='api_attendance_extra'),
    url(r'^attendance/(?P<pk>[0-9]+)/extra_delete$', views.ServiceProfessionalPricingCriterionAPIDelete.as_view(),
        name='api_attendance_extra_delete'),
    url(r'^attendance/(?P<pk>[0-9]+)/observation$', views.AttendancePricingCriterionOptions.as_view(),
        name='api_attendance_observation'),
    url(r'^attendance/(?P<pk>[0-9]+)/voucher$', views.AttendanceVoucher.as_view(),
        name='api_attendance_evaluation'),
    url(r'^attendance/(?P<pk>[0-9]+)/cancelation$', views.CancelationAttendanceApi.as_view(),
        name='api_attendance_cancelation'),
    url(r'^attendance/(?P<pk>[0-9]+)/new$', views.NewAttendance.as_view(),
        name='api_attendance_new'),
    url(r'^attendance/historic/$', views.LastServices.as_view(),
        name='api_last_services'),

    url(r'^professional/(?P<pk>[0-9]+)$', views.ProfessionalDetail.as_view(), name='api_professional_profile'),
    url(r'^professional/(?P<pk>[0-9]+)/services$', views.ServiceProfessionalAttendanceAPI.as_view(),
        name='api_professional_services'),
    url(r'^professional/services-professional-api$', views.ServiceProfessionalAPI.as_view(),
        name='api_professional_services'),
    url(r'^professional/$', views.ProfessionalListApi.as_view(), name='api_professional_search'),
    url(r'^professional/home/$', views.ProfessionalHome.as_view(), name='api_professional_home'),
    url(r'^professional/evaluation/$', views.ProfessionalEvaluationApi.as_view(), name='api_professional_evaluation'),
    url(r'^professional/schedule/$', views.ProfessionalSheddule.as_view(), name='api_professional_schedule'),
    url(r'^professional/schedule_calendar/$', views.ProfessionalShedduleUpdate.as_view(),
        name='api_professional_schedule_update'),
    url(r'^professional/bank/$', views.ProfessionalBankAccount.as_view(),
        name='api_professional_bank'),
    url(r'^professional/transaction/$', views.TransactionListApi.as_view(),
        name='api_professional_transaction'),
    url(r'^professional/services/$', views.ServiceProfessionalListApi.as_view(),
        name='api_professional_services'),
    url(r'^professional/services/(?P<pk>[0-9]+)$', views.ServiceProfessionalDetailApi.as_view(),
        name='api_professional_service_detail'),
    url(r'^professional/transaction/(?P<pk>[0-9]+)$', views.TransactionDetailApi.as_view(),
        name='api_professional_transaction_detail'),

    url(r'^notification/send/$', views.SendPushNotification.as_view(), name='api_notification_send_push_notification'),
    url(r'^creditcard/$', views.CreditCard.as_view(), name='api_credit_card'),
    url(r'^creditcard/(?P<pk>[0-9]+)$', views.CreditCardDetail.as_view(), name='api_credit_card_detail'),
    url(r'^cep/(?P<cep>\w+)$', views.AddressAPI.as_view(), name='api_address'),
    url(r'^state/$', views.StateAPI.as_view(), name='api_state'),
    url(r'^city/$', views.CityAPI.as_view(), name='api_city'),
    url(r'^neighborhood/$', views.NeighborhoodAPI.as_view(), name='api_neighborhood'),
    url(r'^iugu/webhook/$', views.IuguWebhookApi.as_view(), name='api_iugu'),
    url(r'^edit-saloon/(?P<pk>[0-9]+)$', views.ToggleServices.as_view(), name='toggle_services'),
]