from collections import Counter
import csv
from datetime import datetime
import json
from pathlib import Path
import re
import pandas as pd


class Posts:
    """Parse from JSON and preprocess Instagram posts.

    Attributes:
        posts (dict): Collection of posts obtained from Instagram API.

    """

    def __init__(self, posts):
        self.posts = posts
        self.df = None
        self.hashes = None

    def __repr__(self):
        return f'{len(self.posts)} Instagram posts'

    def __add__(self, other):
        return Posts({**self.posts, **other.posts})

    def to_hashes(self):
        self.hashes = [v['hashtags'] for k, v in self.posts.items() if v['hashtags']]
        return self

    def to_df(self):
        self.df = pd.DataFrame.from_dict(self.posts, orient='index')
        return self

    @classmethod
    def from_json_files(cls, path):

        files = Path(path).glob('**/*.json')
        posts = dict()

        for file in files:
            edges = cls._extract_edges_from_json(file)
            for node in edges:
                id, content = cls._extract_post(node)
                posts.setdefault(id, content)

        return cls(posts)

    @classmethod
    def _extract_edges_from_json(cls, file_name):
        with open(file_name, 'r') as file:
            content = json.load(file)

        all_edges = []

        for edges in content[cls.JSON_FIELD]['recent']['sections']:
            for edge in edges['layout_content']['medias']:
                all_edges.append(edge)

        return all_edges

    @classmethod
    def _extract_post(cls, node):

        id = str(node['media']['pk'])
        url = f"https://www.instagram.com/p/{node['media']['code']}"
        timestamp = datetime.fromtimestamp(node['media']['taken_at']).isoformat()
        user_id = node['media']['user']['pk']
        user_name = node['media']['user']['username']
        user_full_name = node['media']['user']['full_name']
        likes = node['media']['like_count']
        comments = node['media']['comment_count']

        try:
            display_url = node['media']['image_versions2']['candidates'][0]['url']
        except KeyError:
            display_url = node['media']['carousel_media'][0]['image_versions2']['candidates'][0]['url']
        try:
            text = node['media']['caption']['text']
        except TypeError:
            text = None
        try:
            hashtags = [tag.lower() for tag in re.findall('#[^#\\s]+', text) if tag[1:].isalnum()]
        except TypeError:
            hashtags = None

        record = {
            'url': url,
            'user_id': user_id,
            'user_name': user_name,
            'user_full_name': user_full_name,
            'timestamp': timestamp,
            'likes': likes,
            'comments': comments,
            'display_url': display_url,
            'text': text,
            'hashtags': hashtags
        }

        return id, record

    def _detect_junk_tags(self, hashtags, to_detect):
        return any([tag in hashtags for tag in to_detect if hashtags])

    def remove_posts(self, file_path):
        with open(file_path, 'r') as file:
            junk_hashtags = file.read().replace(' ', '').strip('\n').split(',')
        posts = {id: post for id, post in self.posts.items(
        ) if not self._detect_junk_tags(post['hashtags'], junk_hashtags)}
        return Posts(posts)

    def set_custom_categories(self, file_path, name='categories'):
        categories_mapping = self._load_custom_categories(file_path)
        for post in self.posts:
            hashtags = self.posts[post].get('hashtags')
            self.posts[post][name] = self._hashtags_to_categories(
                categories_mapping, hashtags) if hashtags else None

        if self.df is not None:
            self.to_df()

    @classmethod
    def _load_custom_categories(cls, file_path):
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            categories = {rows[0]: rows[1].replace(' ', '').split(',') for rows in reader}
            return categories

    @classmethod
    def _hashtags_to_categories(cls, custom_categories, hashtags):
        categories = []
        if custom_categories and hashtags:
            for name, categories_lst in custom_categories.items():
                for tag in hashtags:
                    if tag in categories_lst:
                        categories.append(name)
                        break
        return categories if categories else None

    def popular_categories(self, category='categories', pct=True):
        categories = [
            v['categories'] for k, v in self.posts.items() if v['categories']]
        categories_list = [item for sublist in categories for item in sublist]
        most_common = Counter(categories_list).most_common()
        if pct:
            return [(value, round((count / len(self.posts)) * 100, 2))
                    for value, count in most_common]
        return most_common

    def popular_hashtags(self, n=10, pct=False):
        if not self.hashes:
            self.to_hashes()
        hash_list = [item for sublist in self.hashes for item in sublist]

        most_common = Counter(hash_list).most_common(n)
        if pct:
            return [(value, round((count / len(self.posts)) * 100, 2))
                    for value, count in most_common]
        return most_common


class HashtagPosts(Posts):
    """Parse from JSON and preprocess Instagram posts
    obtained via the hashtag API endpoint.

    Attributes:
        posts (dict): Collection of posts obtained from Instagram API.
    """

    JSON_FIELD = 'data'


class LocationPosts(Posts):
    """Parse from JSON and preprocess Instagram posts
    obtained via the location API endpoint.

    Attributes:
        posts (dict): Collection of posts obtained from Instagram API.
    """

    JSON_FIELD = 'native_location_data'
