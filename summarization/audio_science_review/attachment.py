
# Docs: https://xenforo.com/community/pages/api-endpoints/#type_Attachment

class AsrPostAttachment(object):

    def __init__(self, json_data):
        self.attachment_id = json_data['attachment_id']
        self.content_id = json_data['content_id']
        self.content_type = json_data['content_type']

        self.filename = json_data['filename']
        self.file_size = json_data['file_size']
        self.view_count = json_data['view_count']
        self.is_audio = json_data['is_audio']
        self.is_video = json_data['is_video']
        self.height = json_data['height']
        self.width = json_data['width']

        self.direct_url = json_data['direct_url']
        self.thumbnail_url = json_data.get('thumbnail_url', None)
