from summarization.audio_science_review.thread import AsrThread
from summarization.utils.utils import load_json_from_file
from summarization.llama_tokenizer.tokenizer import Tokenizer
import os


def chunk_summaries_by_number_of_tokens(list_of_summaries, max_size, tokenizer):
    chunks = []
    current_chunk = []
    current_size = 0
    list_of_summaries_token_count = [len(tokenizer.encode(s, bos=False, eos=False)) for s in list_of_summaries]
    for summary, token_count in zip(list_of_summaries, list_of_summaries_token_count):
        if current_size + token_count > max_size:
            chunks.append(current_chunk)
            current_chunk = []
            current_size = 0

        current_chunk.append(summary)
        current_size += token_count

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def chunk_asr_thread_by_number_of_tokens(asr_thread, max_size):
    chunks = []
    current_chunk = []
    current_size = 0
    first_and_last_post_ids = []
    for post in asr_thread.posts:
        if current_size + post.token_count > max_size:
            chunks.append(current_chunk)
            first_and_last_post_ids.append([current_chunk[0].id, current_chunk[-1].id])
            current_chunk = []
            current_size = 0

        current_chunk.append(post)
        current_size += post.token_count

    if current_chunk:
        chunks.append(current_chunk)
        first_and_last_post_ids.append([current_chunk[0].id, current_chunk[-1].id])

    return chunks, first_and_last_post_ids

