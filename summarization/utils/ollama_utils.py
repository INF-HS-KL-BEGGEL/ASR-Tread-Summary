import ollama
import re


def get_ollama_model_stop_tags(model_name):
    stop_tags = []
    params = ollama.show(model_name)['parameters'].split('\n')
    for p in params:
        if 'stop' in p:
            stop_tags += re.findall(r'"(.*?)"', p)
    return stop_tags
