from django.contrib import admin

from django.apps import apps
from django.contrib import admin
from home.models import SummarizedThread
from django.utils.translation import gettext_lazy as _


class SummarizedThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread_id', 'thread_name', 'thread_reply_count', 'is_summarized', 'last_change')


app_models = apps.get_app_config('home').get_models()
for model in app_models:
    try:
        if model == SummarizedThread:
            admin.site.register(SummarizedThread, SummarizedThreadAdmin)
        else:
            admin.site.register(model)

    except Exception:
        pass
