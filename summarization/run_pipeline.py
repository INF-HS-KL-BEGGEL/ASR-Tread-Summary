#from langchain_community.llms import Ollama
from summarization.utils import ollama_utils
from summarization.llama_tokenizer.tokenizer import Tokenizer
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import ollama
import pprint
from string import Template
from summarization.audio_science_review.api import AudioScienceReviewAPI
from summarization.audio_science_review.thread import AsrThread
from summarization.iterative_summarization.summarize import thread_summary_iterative_refine_with_references

from summarization.utils.utils import write_json_to_file
from home.models import SummarizedThread
import time


def download_thread(asr_thread_id):
    # fetch a full thread, return AsrThread-Object
    api = AudioScienceReviewAPI()
    raw_json, n_api_requests = api.get_raw_full_thread_by_id(asr_thread_id)
    asr_thread = AsrThread(raw_json)
    return asr_thread, n_api_requests


def run_pipeline_download_and_summarize(summary_id, asr_thread_id):
    start_time = time.time()
    asr_thread, n_api_requests = download_thread(asr_thread_id)
    download_runtime = time.time() - start_time

    thread_summary_obj = SummarizedThread.objects.get(id=summary_id)
    thread_summary_obj.thread_id = asr_thread.id
    thread_summary_obj.forum_title = asr_thread.forum_title
    thread_summary_obj.thread_type = "thread"
    thread_summary_obj.thread_name = asr_thread.title
    thread_summary_obj.thread_creator_name = asr_thread.starter_username
    thread_summary_obj.thread_creator_id = asr_thread.starter_user_id
    thread_summary_obj.thread_last_post_date = asr_thread.posts[-1].post_date
    thread_summary_obj.thread_last_post_id = asr_thread.posts[-1].id
    thread_summary_obj.thread_reply_count = asr_thread.reply_count
    thread_summary_obj.thread_url = asr_thread.view_url
    thread_summary_obj.is_summarized = False
    thread_summary_obj.save()

    start_time = time.time()
    refined_summary, _, _, n_llm_runs, input_tokens, output_tokens\
        = thread_summary_iterative_refine_with_references(asr_thread)
    llm_runtime = time.time() - start_time

    thread_summary_obj.thread_summary = refined_summary
    thread_summary_obj.is_summarized = True
    thread_summary_obj.forum_api_requests = int(n_api_requests)
    thread_summary_obj.download_runtime = int(download_runtime)
    thread_summary_obj.ollama_llm_runs = n_llm_runs
    thread_summary_obj.llm_runtime = int(llm_runtime)
    thread_summary_obj.llm_input_tokens = int(input_tokens)
    thread_summary_obj.llm_output_tokens = int(output_tokens)
    thread_summary_obj.save()


if __name__ == '__main__':
    run_pipeline_download_and_summarize(0, "16822")
    #run_pipeline_download_and_summarize(0, "47362")
