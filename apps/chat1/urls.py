from django.conf.urls import url

from apps.chat1 import views

urlpatterns = [
    url(r'^message/$', views.MessangerList.as_view(), name='api_Messages'),
]
