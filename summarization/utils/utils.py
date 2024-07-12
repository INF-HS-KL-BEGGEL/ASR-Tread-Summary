import json
import os
from summarization.audio_science_review.api import AudioScienceReviewAPI
from summarization.audio_science_review.thread import AsrThread
from summarization.llama_tokenizer.tokenizer import Tokenizer


def write_json_to_file(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile, indent=4, default=vars)


def load_json_from_file(file_path):
    with open(file_path, 'r') as fobj:
        data = json.load(fobj)
    return data


def download_thread(thread_id, out_dir='../data/thread_samples/'):
    # fetch a full thread, save raw json to file
    # load file and populate object from json
    out_fp = os.path.join(out_dir, f'thread_{thread_id}.json')

    api = AudioScienceReviewAPI()
    raw_json = api.get_raw_full_thread_by_id(thread_id)
    write_json_to_file(raw_json, out_fp)

    thread_json = load_json_from_file(out_fp)
    thread = AsrThread(thread_json)
    return thread


def read_thread_from_file(thread_id, dir='../data/thread_samples', tokenizer=None):
    # read thread from json file for further use
    json_fp = os.path.join(dir, f'thread_{thread_id}.json')
    thread_from_json = load_json_from_file(json_fp)
    thread = AsrThread(thread_from_json)

    if isinstance(tokenizer, Tokenizer):
        thread.count_post_tokens(tokenizer=tokenizer)
    return thread


def get_updated_thread_ids(last_days):
    api = AudioScienceReviewAPI()
    thread_reply_counts = api.get_ids_and_reply_count_of_updated_threads(last_days=last_days)

    return thread_reply_counts


