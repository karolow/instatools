import csv
from datetime import datetime
import json
from pathlib import Path
import re
import numpy as np
import pandas as pd


class Posts:
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
        if self.df is None:
            self.to_df()

        df_raw = self.df
        df_exploded = df_raw.explode(category)
        df_exploded['_helper'] = 1
        df_exploded = df_exploded.loc[:, [category, '_helper']]
        df_wide = df_exploded.pivot(columns=category, values='_helper')
        df_wide.drop(np.nan, axis=1, inplace=True)
        if pct:
            return round(df_wide.count(0) / len(self.df) * 100, 1).sort_values(ascending=False)
        else:
            return df_wide.count(0), len(self.df)


class HashtagPosts(Posts):

    @classmethod
    def _extract_edges_from_json(cls, file_name):
        with open(file_name, 'r') as file:
            content = json.load(file)

        all_edges = []

        for edges in content['data']['recent']['sections']:
            for edge in edges['layout_content']['medias']:
                all_edges.append(edge)

        return all_edges

    @classmethod
    def _extract_post(cls, node):

        id = node['media']['pk']
        shortcode = node['media']['code']
        timestamp = datetime.fromtimestamp(node['media']['taken_at'])
        owner = node['media']['user']['pk']
        likes = node['media']['like_count']
        comments = node['media']['comment_count']

        try:
            display_url = node['media']['image_versions2']['candidates'][0]['url']
        except KeyError:
            display_url = node['media']['carousel_media'][0]['image_versions2']['candidates'][0]['url']

        caption = None
        text = node['media']['caption'].get('text')

        hashtags = [tag.lower() for tag in re.findall('#[^#\\s]+', text) if tag[1:].isalnum()]
        hashtags = hashtags if hashtags else None

        record = {
            'shortcode': shortcode,
            'owner': owner,
            'timestamp': timestamp,
            'likes': likes,
            'comments': comments,
            'display_url': display_url,
            'caption': caption,
            'text': text,
            'hashtags': hashtags
        }

        return id, record


class LocationPosts(Posts):

    @classmethod
    def _extract_edges_from_json(cls, file_name):
        with open(file_name, 'r') as file:
            content = json.load(file)

        return content['graphql']['location']['edge_location_to_media']['edges']

    @classmethod
    def _extract_post(cls, node):

        id = node['node']['id']
        shortcode = node['node']['shortcode']
        timestamp = datetime.fromtimestamp(node['node']['taken_at_timestamp'])
        owner = node['node']['owner']['id']
        likes = node['node']['edge_liked_by']['count']
        comments = node['node']['edge_media_to_comment']['count']
        display_url = node['node']['display_url']
        caption = node['node'].get('accessibility_caption')

        if node['node']['edge_media_to_caption']['edges']:
            text = node['node']['edge_media_to_caption']['edges'][0]['node']['text']
        else:
            text = ''

        hashtags = [tag.lower() for tag in re.findall('#[^#\\s]+', text) if tag[1:].isalnum()]
        hashtags = hashtags if hashtags else None

        record = {
            'shortcode': shortcode,
            'owner': owner,
            'timestamp': timestamp,
            'likes': likes,
            'comments': comments,
            'display_url': display_url,
            'caption': caption,
            'text': text,
            'hashtags': hashtags
        }

        return id, record
