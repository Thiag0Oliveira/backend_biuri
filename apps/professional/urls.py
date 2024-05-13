from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required

from . import views

from apps.company_sale import views as company_views





urlpatterns = [
    url('professional$', login_required(views.ProfessionalList.as_view()), name='professional-list'),
    url('professional/price_log$', login_required(views.ProfessionalPriceLogList.as_view()), name='professional-list-price-log'),
    url('professional/portfolio$', login_required(views.ProfessionalPortfolio.as_view()), name='professional-portfolio'),
    url('professional/concierge/$', login_required(views.ProfessionalConcierge.as_view()), name='professional-concierge'),
    url('professional/concierge/(?P<pk>[0-9]+)/$', login_required(views.ProfessionalConciergeCreate.as_view()), name='professional-concierge'),
    url('customer/add', login_required(views.PdfContract.as_view()), name='professional-contract'),
    url('professional/(?P<pk>[0-9]+)/category$', login_required(views.ProfessionalUpdateCategory.as_view()),
        name='professional-category'),
    url('professional/(?P<pk>[0-9]+)/service$', login_required(views.ProfessionalUpdateService.as_view()),
        name='professional-service'),
    url('professional/(?P<pk>[0-9]+)/picture_portfolio$', login_required(views.ProfessionalUpdatePortfolio.as_view()),
        name='professional-picture-portfolio'),
    url('professional/(?P<pk>[0-9]+)/service_pricing$', login_required(views.ProfessionalUpdatePricingCriterion.as_view()),
        name='professional-service-pricing'),
    url('professional/add$', login_required(views.ProfessionalCreate.as_view()), name='professional-add'),
    url('professional/(?P<pk>[0-9]+)/edit$', login_required(views.ProfessionalUpdate.as_view()), name='professional-update'),
    url('professional/(?P<pk>[0-9]+)/schedule$', login_required(views.ProfessionalScheduleDefaultUpdate.as_view()),
        name='professional-schedule'),
    url('professional/(?P<pk>[0-9]+)/reset_password$', login_required(views.ProfessionalResetPassword.as_view()),
        name='professional-reset-password'),
    url('professional/(?P<pk>[0-9]+)/test_service$', login_required(views.ProfessionalTestService.as_view()),
        name='professional-test-service'),
    url('professional/service_pricing$', views.ProfessionalUpdatePricingCriterion.as_view(),
        name='professional-service-pricing-edit'),
    url('professional/category$', views.ProfessionalUpdateCategory.as_view(),
        name='professional-category-edit'),
    url('professional/service$', views.ProfessionalUpdateService.as_view(),
        name='professional-service-edit'),
    url('professional/schedule$', views.ProfessionalScheduleDefaultUpdate.as_view(),
        name='professional-schedule-edit'),
    url('executive$', login_required(views.ExecutiveList.as_view()), name='executive-list'),
    url('executive/create$', login_required(views.ExecutiveCreate.as_view()), name='executive-create'),
    url('executive/(?P<pk>[0-9]+)/edit$', login_required(views.ExecutiveUpdate.as_view()),
        name='executive-update'),
    url('seller$', login_required(views.SellerList.as_view()), name='seller-list'),
    url('seller/create$', login_required(views.SellerCreate.as_view()), name='seller-create'),
    url('seller/(?P<pk>[0-9]+)/edit$', login_required(views.SellerUpdate.as_view()),
        name='seller-update'),
    url('professional/(?P<pk>[0-9]+)/terms', login_required(views.PdfTerms.as_view()), name='professional-terms'),
    url('professional/(?P<pk>[0-9]+)/contract', login_required(views.PdfContract.as_view()), name='professional-contract'),
    url('message/push$', login_required(views.MessagePushList.as_view()), name='message-push'),
    url('message/push/create$', login_required(views.MessageCreate.as_view()), name='message-push-create'),
    url('message/push/(?P<pk>[0-9]+)/update$', login_required(views.MessageUpdate.as_view()),
        name='message-push-update'),
    url('message/push/(?P<pk>[0-9]+)/update_region/$', login_required(views.MessageUpdateRegion.as_view()),
        name='message-push-update-region'),
    url('ajax/delete_picture/$', views.delete_picture, name='delete-picture'),
    url('ajax/newest_picture/$', views.newest_picture, name='newest-picture'),
    # url('company$', login_required(company_views.CompanyList.as_view()), name='company-list'),
    # url('company/create$', login_required(company_views.CompanyCreate.as_view()), name='company-create'),
    # url('company/(?P<pk>[0-9]+)/edit$', login_required(company_views.CompanyUpdate.as_view()),
    #     name='company-update'),
]
