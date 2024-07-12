from summarization.audio_science_review.post import AsrPost
from tqdm import tqdm
# Docs: https://xenforo.com/community/pages/api-endpoints/#type_Thread
from datetime import datetime

class AsrThread(object):

    def __init__(self, json_data):
        self.id = json_data['thread']['thread_id']
        self.title = json_data['thread']['title']
        self.start_date = datetime.utcfromtimestamp(json_data['thread']['post_date'])
        self.last_post_date = datetime.utcfromtimestamp(json_data['thread']['last_post_date'])

        self.starter_user_id = json_data['thread']['user_id']
        self.starter_username = json_data['thread']['username']

        self.view_url = json_data['thread']['view_url']
        self.view_count = json_data['thread']['view_count']
        self.reply_count = json_data['thread']['reply_count']

        self.forum_title = json_data['thread']['Forum']['title']
        self.forum_parent_node_id = json_data['thread']['Forum']['parent_node_id']
        self.forum_desc = json_data['thread']['Forum']['description']
        self.forum_node_id = json_data['thread']['node_id']

        self.discussion_type = json_data['thread']['discussion_type']
        self.poll = json_data['thread'].get('Poll', None)

        self.posts = []
        for post_json in json_data['posts']:
            self.posts.append(AsrPost(post_json))

        self.count = len(self.posts)

    def count_post_tokens(self, tokenizer, bos=False, eos=False, force_recount=False):
        for post in tqdm(self.posts):
            if force_recount or not post.token_count:
                post.count_tokens(tokenizer, bos=bos, eos=eos)

    def get_total_sum_of_tokens(self):
        count = 0
        for post in self.posts:
            assert not isinstance(post.count_tokens, int), "run count_tokens() first"
            count += post.token_count
        return count

    def get_post_by_id(self, post_id):
        for post in self.posts:
            if str(post.id) == str(post_id):
                return post
        return None

    def __str__(self):
        return (f'ASR thread {self.id}\n'
                f'{self.starter_username}\n'
                f'{self.start_date}\n'
                f'{self.title}\n'
                f'{self.view_url}\n')
