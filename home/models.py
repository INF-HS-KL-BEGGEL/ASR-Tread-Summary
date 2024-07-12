from django.db import models
from django.utils.translation import gettext_lazy as _


class SummarizedThread(models.Model):
    thread_id = models.CharField()
    forum_title = models.CharField(blank=True, null=True)
    thread_type = models.CharField(blank=True, null=True)
    thread_name = models.CharField(blank=True, null=True)
    thread_creator_name = models.CharField(blank=True, null=True)
    thread_creator_id = models.IntegerField(blank=True, null=True)
    thread_last_post_date = models.DateTimeField(blank=True, null=True)
    thread_last_post_id = models.IntegerField(blank=True, null=True)
    thread_reply_count = models.IntegerField(blank=True, null=True)
    thread_summary = models.TextField(blank=True, default="")
    thread_url = models.URLField(blank=True, null=True)
    last_change = models.DateTimeField(auto_now_add=True, null=True)
    forum_api_requests = models.IntegerField(default=0)
    ollama_llm_runs = models.IntegerField(default=0)
    llm_runtime = models.IntegerField(default=0)
    llm_input_tokens = models.IntegerField(default=0)
    llm_output_tokens = models.IntegerField(default=0)
    download_runtime = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    is_summarized = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Summarized Thread")
        verbose_name_plural = _("Summarized Threads")

#
# class DailyRequest(models.Model):
#     number_of_api_calls = models.IntegerField()
#     number_of_failed_api_calls = models.IntegerField()
#
#
# class DailySummaryCounter(models.Model):
#     summaries_done_today = models.IntegerField()
#     summaries_todo = models.IntegerField()
