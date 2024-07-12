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
import os
from summarization.thread_handling.generate_chunks import chunk_asr_thread_by_number_of_tokens
from .prompts import PROMPT_SUMMARY_OF_POST_CHUNKS, PROMPT_SUMMARY_REFINE, PROMPT_SYSTEM
import pathlib
import re

def llm_inference(ollama_client, model, prompt, system_prompt, params, context=None):
    print(prompt)
    if context:
        res = ollama_client.generate(model=model, prompt=prompt, system=system_prompt,
                                     options=params, context=context)
    else:
        res = ollama_client.generate(model=model, prompt=prompt, system=system_prompt,
                                     options=params)
    return res



def thread_summary_iterative_refine_with_references(asr_thread):
    model = os.environ.get('OLLAMA_LARGE_LANGUAGE_MODEL')
    ollama_host = os.environ.get('OLLAMA_SERVER_URL')
    max_tokens = 4000
    hyper_params = {'temperature': 0.0,
                    'num_predict': 4096,
                    'num_ctx': 4096,
                    }

    ollama_client = ollama.Client(host=ollama_host)
    n_llm_runs = 0
    llm_input_tokens = 0
    llm_output_tokens = 0

    tokenizer_model = os.path.join(pathlib.Path(__file__).parent.resolve(),
                                   "../tokenizer_models/Meta-Llama-3-8B/tokenizer.model")
    tokenizer = Tokenizer(tokenizer_model)
    asr_thread.count_post_tokens(tokenizer, force_recount=False)

    post_chunks, chunk_first_and_last_post_ids = chunk_asr_thread_by_number_of_tokens(asr_thread, max_tokens)

    # summary of chunks, starting with second chunk
    chunk_summaries = []
    for n, chunk in enumerate(post_chunks):
        print("llm inference, summarize chunk", n+1, "of", len(post_chunks))

        chunk_content = "\n\n".join([str(c) for c in chunk])
        prompt = Template(PROMPT_SUMMARY_OF_POST_CHUNKS).safe_substitute(chunk_content=chunk_content)

        model_inference = llm_inference(ollama_client, model, prompt, PROMPT_SYSTEM, hyper_params)
        n_llm_runs += 1
        summary = model_inference.get('response')
        chunk_summaries.append(summary)

        llm_input_tokens += len(tokenizer.encode(PROMPT_SYSTEM, bos=False, eos=False))
        llm_input_tokens += len(tokenizer.encode(prompt, bos=True, eos=True))
        llm_output_tokens += len(tokenizer.encode(summary, bos=False, eos=False))


    refined_summary = chunk_summaries[0]
    intermediate_summaries = [refined_summary]
    ref_positions = []
    for n, (chunk_summary, (first_id, last_id)) in enumerate(zip(chunk_summaries, chunk_first_and_last_post_ids)):
        if n == 0:
            ref_positions.append((0,
                                  first_id,
                                  last_id,
                                  asr_thread.get_post_by_id(first_id).position_in_thread,
                                  asr_thread.get_post_by_id(last_id).position_in_thread))
            continue

        print("llm inference, refine summary on chunk summaries", n+1, "of", len(chunk_summaries))
        prompt = Template(PROMPT_SUMMARY_REFINE).safe_substitute(refined_summary=refined_summary,
                                                                 initial_summary=chunk_summaries[0],
                                                                 chunk_summary=chunk_summary)

        model_inference = llm_inference(ollama_client, model, prompt, PROMPT_SYSTEM, hyper_params)
        n_llm_runs += 1

        ref_positions.append((len(refined_summary.split("\n\n")),
                              first_id,
                              last_id,
                              asr_thread.get_post_by_id(first_id).position_in_thread,
                              asr_thread.get_post_by_id(last_id).position_in_thread))

        refined_summary = model_inference.get('response')
        intermediate_summaries.append(refined_summary)

        llm_input_tokens += len(tokenizer.encode(PROMPT_SYSTEM, bos=False, eos=False))
        llm_input_tokens += len(tokenizer.encode(prompt, bos=True, eos=True))
        llm_output_tokens += len(tokenizer.encode(refined_summary, bos=False, eos=False))

    # add references
    refined_summary_with_references = []
    for n, par in enumerate(refined_summary.split("\n\n")):
        for pos_ref, first_id, last_id, thread_pos_first, thread_pos_last in ref_positions:
            if n == pos_ref:
                ref_tag = "<<{[" + "_".join([str(first_id),
                                             str(last_id),
                                             str(int(thread_pos_first + 1)),
                                             str(int(thread_pos_last + 1))]) + "]}>>"
                refined_summary_with_references.append(ref_tag)
        refined_summary_with_references.append(par)

    # combine summary paragraphs and references to text
    refined_summary_with_references = "\n\n".join(refined_summary_with_references)

    # clean summary
    noise_prefixes = ["Here is the extended summary:",
                      "Here is the final summary:",
                      "Here is the refined summary:"]
    for noise in noise_prefixes:
        refined_summary_with_references = refined_summary_with_references.replace(noise, "")

    refined_summary_with_references = refined_summary_with_references.lstrip()

    print(refined_summary_with_references)

    return (refined_summary_with_references, intermediate_summaries, post_chunks, n_llm_runs,
            llm_input_tokens, llm_output_tokens)

