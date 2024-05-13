"""{{project_name}} URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views import defaults as default_views

from rest_framework_swagger.views import get_swagger_view


admin.site.site_header = settings.ADMIN_SITE_HEADER
schema_view = get_swagger_view(title='BIURI API')

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('apps.core.urls')),
    url(r'^api/', include('apps.api.urls', namespace='api')),
    url(r'^dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    url(r'^', include('apps.lead_captation.urls', namespace='lead')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^nested_admin/', include('nested_admin.urls')),
    url(r'^dashboard/', include('apps.professional.urls', namespace='professional')),
    url(r'^payment/', include('apps.payment.urls', namespace='payment')),
    url(r'^after_sale/', include('apps.after_sale.urls', namespace='after_sale')),
    url(r'^dashboard/company/', include('apps.company_sale.urls', namespace='company')),
    url(r'^chat/', include('apps.chat1.urls', namespace = 'message')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    url(r'^swagger$', schema_view)
]

# urlpatterns += [
#     url(r'^silk/', include('silk.urls', namespace='silk'))
# ]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
