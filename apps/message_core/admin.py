from django.contrib import admin

from .models import News, PushToken, Message, PushSchedule


admin.site.register(PushToken)
admin.site.register(News)
admin.site.register(Message)
admin.site.register(PushSchedule)


# Register your models here.
