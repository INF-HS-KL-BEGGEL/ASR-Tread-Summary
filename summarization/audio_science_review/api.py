import time
import requests
from tqdm import tqdm
import os

from summarization.audio_science_review.thread import AsrThread


# API Docs: https://xenforo.com/community/pages/api-endpoints/


class AudioScienceReviewAPI(object):

    def __init__(self):
        self.base_url = os.environ.get('ASR_FORUM_API_URL')
        self.user_agent = 'asr-thread-summary-ai-agent'
        self.api_key = os.environ.get('ASR_FORUM_API_KEY')
        self.timeout = float(os.environ.get('ASR_FORUM_TIMEOUT'))
        self.delay = float(os.environ.get('ASR_FORUM_DELAY'))

    def _api_get_request(self, path, params=None):
        headers = {
            'XF-Api-Key': self.api_key,
            'Accept': 'application/json',
            'User-Agent': self.user_agent,
        }
        req = requests.get(f"{self.base_url.rstrip('/')}/{path}",
                           params=params,
                           headers=headers,
                           timeout=self.timeout)
        req.raise_for_status()
        res = req.json()
        if 'errors' in res:
            raise Exception(res['errors'])

        return res

    def _paginated_api_get_request(self, path, params=None):
        params.update(page=1)
        res = self._api_get_request(path, params)
        total_pages = res['pagination']['last_page']
        paginated_keys = [k for k in res.keys() if isinstance(res[k], list)]

        collected_res = res
        for page in tqdm(range(2, total_pages + 1)):
            params.update(page=page)
            res = self._api_get_request(path, params)
            for key in paginated_keys:
                collected_res[key] += res[key]
            time.sleep(self.delay)

        collected_res['pagination'].pop('current_page', None)
        return collected_res, total_pages

    def get_full_thread_by_id(self, thread_id):
        path = f'threads/{thread_id}'
        params = {
            'with_posts': True,
        }
        res, n_req = self._paginated_api_get_request(path, params)
        thread = AsrThread(res)
        return thread

    def get_full_thread_by_url(self, thread_url):
        title = thread_url.rstrip('/').split('/')[-1]  # get last part of url
        thread_id = title.split('.')[-1]  # id is title suffix
        return self.get_full_thread_by_id(thread_id)

    def get_raw_full_thread_by_id(self, thread_id):
        path = f'threads/{thread_id}'
        params = {
            'with_posts': True,
        }
        res, n_req = self._paginated_api_get_request(path, params)
        return res, n_req

    def get_raw_full_thread_by_url(self, thread_url):
        title = thread_url.rstrip('/').split('/')[-1]  # get last part of url
        thread_id = title.split('.')[-1]  # id is title suffix
        return self.get_raw_full_thread_by_id(thread_id)

    def get_ids_and_reply_count_of_updated_threads(self, last_days=1):
        path = f'threads/'
        params = {
            'with_posts': False,
            'last_days': int(last_days),
            'order': 'last_post_date',
            'direction': 'desc',
        }
        res, n_req = self._paginated_api_get_request(path, params)
        thread_reply_counts = {}
        for thread in res['threads']:
            reply_count = thread['reply_count']
            thread_id = thread['thread_id']
            thread_reply_counts[thread_id] = reply_count

        return thread_reply_counts
