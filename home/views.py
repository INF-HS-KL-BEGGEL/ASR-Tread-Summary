from datetime import datetime

from django.shortcuts import render

from .models import *
from summarization.audio_science_review import api
from django.db.models import Sum
import re
from datetime import timedelta
import os
from background_task.models import Task


def index(request):
    summarized_threads = SummarizedThread.objects.filter(is_summarized=True).order_by('-last_change')
    summarized_threads_count = summarized_threads.count()
    open_summary_tasks = Task.objects.all().count()


    daily_llm_runs = SummarizedThread.objects.aggregate(sum=Sum('ollama_llm_runs'))['sum']
    daily_forum_api_req = SummarizedThread.objects.aggregate(sum=Sum('forum_api_requests'))['sum']
    daily_llm_token_in = SummarizedThread.objects.aggregate(sum=Sum('llm_input_tokens'))['sum']
    daily_llm_token_out = SummarizedThread.objects.aggregate(sum=Sum('llm_output_tokens'))['sum']
    daily_llm_runtime = SummarizedThread.objects.aggregate(sum=Sum('llm_runtime'))['sum']
    daily_download_runtime = SummarizedThread.objects.aggregate(sum=Sum('download_runtime'))['sum']

    context = {
        'segment': 'index',
        'summarized_threads_count': summarized_threads_count if summarized_threads_count else 0,
        'open_summary_tasks': open_summary_tasks if open_summary_tasks else 0,
        'daily_llm_runs': daily_llm_runs if daily_llm_runs else 0,
        'daily_forum_api_req': daily_forum_api_req if daily_forum_api_req else 0,
        'daily_llm_token_in': daily_llm_token_in if daily_llm_token_in else 0,
        'daily_llm_token_out': daily_llm_token_out if daily_llm_token_out else 0,
        'daily_llm_runtime': str(timedelta(seconds=int(daily_llm_runtime))) if daily_llm_runtime else 0,
        'daily_download_runtime': str(timedelta(seconds=int(daily_download_runtime))) if daily_download_runtime else 0,

        'dailyRequestsApiCalls': int(daily_forum_api_req if daily_forum_api_req else 0),
        'dailySummariesInRun': open_summary_tasks if open_summary_tasks else 0,
        'dailySummariesToDo': open_summary_tasks if open_summary_tasks else 0,
        'dailyLlmRuns': int(daily_llm_runs if daily_llm_runs else 0),

        # data access for the complete tables
        'summarizedThreads': summarized_threads if summarized_threads else [],
        'dailySummaryCounter': summarized_threads_count if False else [],

        # table meta information for all tables
        'summarizedThreadTableInfo': SummarizedThread._meta._get_fields(),
        'dailySummaryCounterTableInfo': [],
        'dailyRequestsTableInfo': [],
    }
    return render(request, "pages/index.html", context)


def tables(request, thread_id=""):
    summarized_threads = SummarizedThread.objects.filter(thread_id=thread_id).order_by('+last_change')

    thread_summary = "Not available"
    thread_name = "Not available"
    if summarized_threads:
        thread_summary = summarized_threads.get().thread_summary
        thread_name = summarized_threads.get().thread_name

    context = {
        'segment': 'tables',
        'summarizedThreads': thread_summary,
        'threadName': thread_name,
    }

    return render(request, "pages/dynamic-tables.html", context)



def inject_reference_link(thread_summary, thread_view_url):
    pattern = r"<<\{\[(\d+)_(\d+)_(\d+)_(\d+)\]\}>>"
    reference_html = (r'<div style="margin-left: auto; margin-right: 0; text-align: right;">'
                      r'<a href="' + str(thread_view_url) + r'post-\1" type="button" '
                      r'class="btn btn-link" data-toggle="tooltip" data-original-title="Show in Forum" '
                      r'style="padding: 0 0 0 0; margin: 0 0 0 0;" '
                      r'target="_blank" rel="noopener noreferrer">'
                      r'Post #\3 to #\4</a></div>')

    thread_summary_referenced = re.sub(pattern, reference_html, str(thread_summary))
    return thread_summary_referenced


def group_references_in_summary(summary, prefix='<<{['):
    res = []
    current_group = []

    for element in summary:
        if element.startswith(prefix):
            if not current_group:
                current_group.append(element)
            else:
                current_group.append(element)
        else:
            if current_group:
                res.append(current_group)
                current_group = []
            res.append([element])

    if current_group:
        res.append(current_group)
    return res


def aggregate_embedded_references(thread_summary):
    if '\r\n' in thread_summary:
        summary_split = str(thread_summary).split('\r\n\r\n')
    else:
        summary_split = str(thread_summary).split('\n\n')
    summary_aggregated = []
    # aggregate references
    refined_summary_with_references_grouped = group_references_in_summary(summary_split)
    pattern = r"<<\{\[(\d+)_(\d+)_(\d+)_(\d+)\]\}>>"
    for group in refined_summary_with_references_grouped:
        if len(group) > 1 and group[0].startswith('<<{[') and group[-1].startswith('<<{['):
            match_head = re.search(pattern, group[0])
            match_tail = re.search(pattern, group[-1])
            first_id, _, thread_pos_first, _ = match_head.groups()
            _, last_id, _, thread_pos_last = match_tail.groups()

            ref_tag_new = "<<{[" + "_".join([str(first_id),
                                             str(last_id),
                                             str(thread_pos_first),
                                             str(thread_pos_last)]) + "]}>>"
            summary_aggregated.append(ref_tag_new)

        else:
            summary_aggregated.append(group[0])

    return '\n\n'.join(summary_aggregated)


def summary(request, thread_id=""):
    try:
        summarized_thread = SummarizedThread.objects.filter(
            is_summarized=True
        ).filter(
            thread_id=int(thread_id)
        ).latest('last_change')

        thread_summary = summarized_thread.thread_summary
        thread_id = summarized_thread.thread_id
        thread_name = summarized_thread.thread_name
        thread_view_url = summarized_thread.thread_url
        thread_creator_username = summarized_thread.thread_creator_name
        #thread_date = summarized_thread.start_date
        thread_date = summarized_thread.last_change
        thread_reply_count = summarized_thread.thread_reply_count
        thread_forum_title = summarized_thread.forum_title
        thread_last_change = summarized_thread.last_change
        thread_forum_api_requests = summarized_thread.forum_api_requests
        thread_ollama_llm_runs = summarized_thread.ollama_llm_runs
        thread_llm_runtime = summarized_thread.llm_runtime
        thread_llm_input_tokens = summarized_thread.llm_input_tokens
        thread_llm_output_tokens = summarized_thread.llm_output_tokens
        thread_download_runtime = summarized_thread.download_runtime

        thread_summary_aggregated = aggregate_embedded_references(str(thread_summary))
        thread_summary_referenced = inject_reference_link(thread_summary_aggregated, thread_view_url)
        thread_summary_referenced = thread_summary_referenced.replace('*', '')

        llm_model = os.environ.get('OLLAMA_LARGE_LANGUAGE_MODEL')

    except Exception as e:
        thread_summary_referenced = str(e) #"Not available"
        thread_id = "No ID"
        thread_name = "Not available"
        thread_view_url = "#"
        thread_creator_username = "No Name"
        thread_date = datetime.now()
        thread_reply_count = "No Posts"
        thread_forum_title = "No Thread"
        thread_last_change = datetime.now()
        thread_forum_api_requests = "No Thread"
        thread_ollama_llm_runs = "No Thread"
        thread_llm_runtime = "No Thread"
        thread_llm_input_tokens = "No Thread"
        thread_llm_output_tokens = "No Thread"
        thread_download_runtime = "No Thread"
        llm_model = "None"

    context = {
        'segment': 'tables',
        'summary': thread_summary_referenced,
        'thread_name': thread_name,
        'thread_id': thread_id,
        'thread_view_url': thread_view_url,
        'thread_creator_username': thread_creator_username,
        'thread_date': thread_date,
        'thread_reply_count': thread_reply_count,
        'thread_forum_title': thread_forum_title,
        'thread_last_change':  thread_last_change,
        'thread_forum_api_requests':  thread_forum_api_requests,
        'thread_ollama_llm_runs':  thread_ollama_llm_runs,
        'thread_llm_runtime':  thread_llm_runtime,
        'thread_llm_input_tokens':  thread_llm_input_tokens,
        'thread_llm_output_tokens':  thread_llm_output_tokens,
        'thread_download_runtime':  thread_download_runtime,
        'llm_model': llm_model,
    }

    return render(request, "pages/summary_detail.html", context)

