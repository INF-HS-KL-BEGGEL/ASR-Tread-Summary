from background_task import background
from background_task.tasks import Task
from django.dispatch import receiver
from django.db.models.signals import post_save

from summarization.run_pipeline import run_pipeline_download_and_summarize
from home.models import SummarizedThread
from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=SummarizedThread)
def notify_users(sender, instance, created, **kwargs):
    if created:
        asr_thread_id = instance.thread_id
        summary_id = instance.id
        if instance.active and len(instance.thread_summary) == 0:
            # register background task
            thread_summarization_background_worker(summary_id, asr_thread_id, verbose_name=f"Summarize {asr_thread_id}")



# https://django-background-tasks.readthedocs.io/en/latest/
# python manage.py process_tasks

@background(queue='thread_summarization')
def thread_summarization_background_worker(summary_id, asr_thread_id):
    run_pipeline_download_and_summarize(summary_id, asr_thread_id)


