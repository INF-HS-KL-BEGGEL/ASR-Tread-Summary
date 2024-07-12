from bs4 import BeautifulSoup
from datetime import datetime

from summarization.audio_science_review.attachment import AsrPostAttachment

# Docs: https://xenforo.com/community/pages/api-endpoints/#type_Post


class AsrPost(object):

    def __init__(self, json_data):
        self.id = json_data['post_id']
        self.post_date = datetime.utcfromtimestamp(json_data['post_date'])
        self.user_id = json_data['user_id']
        self.user_name = json_data['username']

        self.message = json_data['message']  # raw
        self.message_parsed = json_data['message_parsed']  # html
        self.message_cleaned = AsrPost.clean_post_message(self.message_parsed)  # cleaned text

        self.thread_id = json_data['thread_id']
        self.position_in_thread = json_data['position']
        self.is_first_post = json_data['is_first_post']
        self.is_last_post = json_data['is_last_post']
        self.reaction_score = json_data['reaction_score']

        self.attach_count = json_data['attach_count']
        self.attachments = []
        if self.attach_count > 0:
            for attach_json in json_data['Attachments']:
                self.attachments.append(AsrPostAttachment(attach_json))

        self.token_count = None

    @staticmethod
    def clean_post_message(html_message, remove_blockquotes=True):
        soup = BeautifulSoup(html_message, 'html.parser')  # html to txt without tags

        if remove_blockquotes:
            removals = soup.find_all('blockquote', {'class': 'xfBb-quote'})
            for match in removals:
                match.decompose()

        clean_msg = soup.get_text()
        clean_msg = " ".join(clean_msg.split())  # remove duplicate spaces
        return clean_msg

    def count_tokens(self, tokenizer, bos=False, eos=False):
        token = tokenizer.encode(str(self), bos=False, eos=False)
        self.token_count = len(token)

    def __str__(self):
        return (f"Post from User {self.user_name}:\n"
                f"'''{self.message_cleaned}'''")
