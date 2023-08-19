# I don't know who wrote this original code. I found it on Reddit. It's the basis for the GUI version by me.
# Thanks to the original author(s).

import praw
import json
import requests
import re
import os


class RedditMedia:
    def __init__(self, cred_path):
        with open(cred_path) as f:
            cred = json.load(f)
        self.reddit = praw.Reddit(client_id=cred['client_id'],
                                  client_secret=cred['client_secret'],
                                  password=cred['password'],
                                  redirect_uri=cred['redirect_uri'],
                                  user_agent=cred['user_agent'],
                                  username=cred['username'])

    def dl_sub_images(self, sub, sort='top', limit=300, when='all'):
        """
        download images from a subreddit
        :param sub: subreddit name 
        :param sort: how to sort the subreddit, 'top' is the default value
        :param limit: how many posts to scan. 300 is default
        :param when: choose time filter. 'all' is default
        :return: None
        """
        if not os.path.exists(sub):
            os.mkdir(sub)
        subreddit = self.reddit.subreddit(sub)
        gen = getattr(subreddit, sort)(when, limit=limit)
        url_pattern = re.compile(r'https://(external-)?preview\.redd\.it/(?P<name>.+\.(?:jpg|png))')
        for i in gen:
            if not i.is_self:
                att = dir(i)
                if 'is_gallery' in att:
                    image_ids = [x['media_id'] for x in i.gallery_data['items']]
                    for x in image_ids:
                        url = max(i.media_metadata[x]['p'], key=lambda y: y['y'])['u']
                        img = requests.get(url).content
                        name = url_pattern.search(url).group('name')
                        with open(sub+'/'+name, 'wb') as f:
                            f.write(img)
                elif 'preview' in att:
                    url = i.preview['images'][0]['source']['url']
                    img = requests.get(url).content
                    name = url_pattern.search(url).group('name')
                    with open(sub+'/'+name, 'wb') as f:
                        f.write(img)
