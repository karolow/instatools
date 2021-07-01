from collections import Counter
import csv
from datetime import datetime
from dateutil import tz
import json
from pathlib import Path
import re
import pandas as pd


class Posts:
    """
    Parse from JSON and preprocess Instagram posts.

    Args:
        posts (dict): Collection of posts obtained from Instagram API.

    Attributes:
        posts (dict): Collection of posts obtained from Instagram API.
        df (Pandas dataframe): Collection of posts converted to dataframe.
        hashes (list): A list of lists with all existing hashtags.

    Methods:
        to_hashes: Generate a list of lists with all existing hashtags.
        to_df: Convert posts to Pandas dataframe.
        from_json_files: Create a class from multiple JSON files.
        set_custom_categories: Assign posts to categories based on
            existing hashtags.
        popular_categories: Check the popularity of categories.
        popular_hashtags: Find the most popular hashtags.

    """

    def __init__(self, posts):
        self.posts = posts
        self.df = None
        self.hashes = None

    def __repr__(self):
        return f'{len(self.posts)} Instagram posts'

    def __add__(self, other):
        """Add an object to another one of the same base class.

        They can also be added using the "+" operator.

        Args:
            other: Another object containg Instagram posts.

        Returns:
            A new instance of Posts class containg the posts
            from two other objects.

        """
        return Posts({**self.posts, **other.posts})

    def to_hashes(self):
        """Generate a list of lists with all existing hashtags."""
        self.hashes = [v['hashtags'] for k, v in self.posts.items() if v['hashtags']]
        return self

    def to_df(self):
        """Convert posts to Pandas dataframe."""
        self.df = pd.DataFrame.from_dict(self.posts, orient='index')
        return self

    @classmethod
    def from_json_files(cls, path):
        """
        Create a class from multiple JSON files.

        Args:
            path (str): A path to directory with JSON files obtained from API.

        """
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
        """
        Helper method to parse edges from a JSON file.

        Args:
            file_name (str): A JSON file to parse.

        Returns:
            list: Edges parsed from a JSON file.

        """
        with open(file_name, 'r') as file:
            content = json.load(file)

        all_edges = []

        for edges in content[cls.JSON_FIELD]['recent']['sections']:
            for edge in edges['layout_content']['medias']:
                all_edges.append(edge)

        return all_edges

    @classmethod
    def _extract_post(cls, node):
        """
        Helper method to extract posts from JSON files.

        Args:
            node (dict): Contains post content as extracted from API.

        Returns:
            tuple of str and dict: Post id and post content.

        """
        id = str(node['media']['pk'])
        url = f"https://www.instagram.com/p/{node['media']['code']}"
        timestamp = datetime.utcfromtimestamp(node['media']['taken_at']).isoformat()
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

    @staticmethod
    def _detect_junk_hashtags(hashtags, to_detect):
        """
        Helper method to search for unwanted hashtags.

        Args:
            hashtags (list): Existing hashtags.
            to_detect (list): Unwanted hashtags to search for.

        Returns:
            bool: True if any unwanted hashtag found, False otherwise.

        """
        return any([tag in hashtags for tag in to_detect if hashtags])

    @staticmethod
    def _load_junk_hashtags(file_path):
        """
        Helper method to load a list of unwanted hashtags from a txt file.

        Args:
            file_path (str): A path to a text file.

        Returns:
            list: Unwanted hashtags.

        """
        with open(file_path, 'r') as file:
            junk_hashtags = file.read().replace(' ', '').strip('\n').split(',')
        return junk_hashtags

    def remove_posts(self, junk_hashtags=None, file_path=None):
        """Remove posts based on the predefined list of unwanted hashtags.

        If a file is provided, its content will be used. Otherwise it needs to
        be passed as a junk_hashtags argument. Please note that it returns
        the new Posts object.

        Args:
            junk_hashtags (list): Unwanted hashtags.
            file_path (str): A path to a file containing unwanted hashtags.
                Defaults to None.

        Returns:
            A new filtered Posts object.

        """
        if file_path:
            junk_hashtags = self._load_junk_hashtags(file_path)
        posts = {id: post for id, post in self.posts.items(
        ) if not self._detect_junk_hashtags(post['hashtags'], junk_hashtags)}
        return Posts(posts)

    def set_custom_categories(self, file_path, name='categories'):
        """Assign posts to categories based on existing hashtags.

        Category to hashtags mapping is provided via the CSV file.

        Note:
            If the df attribute exists, it will be updated with
            new values automatically.

        Args:
            file_path (str): A path to a CSV file including custom categories.
            name (str): A new variable name. Defaults to 'categories'.

        """
        categories_mapping = self._load_custom_categories(file_path)
        for post in self.posts:
            hashtags = self.posts[post].get('hashtags')
            self.posts[post][name] = self._hashtags_to_categories(
                categories_mapping, hashtags) if hashtags else None

        if self.df is not None:
            self.to_df()

    @classmethod
    def _load_custom_categories(cls, file_path):
        """Helper function to laod custom categories from a CSV file.

        Args:
            file_path (str): A CSV file with custom categories.

        Returns:
            dict: Mapping of categories to hashtags.

        """
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            categories = {rows[0]: rows[1].replace(' ', '').split(',') for rows in reader}
            return categories

    @classmethod
    def _hashtags_to_categories(cls, custom_categories, hashtags):
        """Helper method to assign post to categories based on hashtags.

        Args:
            custom_categories (dict): Mapping of categories to hashtags.
            hashtags (list): Existing hashtags for each post.

        Returns:
            list or None: Assigned categories if relevant.

        """
        categories = []
        if custom_categories and hashtags:
            for name, categories_lst in custom_categories.items():
                for tag in hashtags:
                    if tag in categories_lst:
                        categories.append(name)
                        break
        return categories if categories else None

    def popular_categories(self, category='categories', pct=True):
        """Check the popularity of categories.

        Args:
            category (str): Variable name. Defaults to 'categories'.
            pct (bool): Percent for categories if True, otherwise the number
                of posts within categories.

        Returns:
            list of tuples: Results for each category.

        """
        categories = [
            v['categories'] for k, v in self.posts.items() if v['categories']]
        categories_list = [item for sublist in categories for item in sublist]
        most_common = Counter(categories_list).most_common()
        if pct:
            return [(value, round((count / len(self.posts)) * 100, 2))
                    for value, count in most_common]
        return most_common

    def popular_hashtags(self, n=10, pct=False):
        """Find the most popular hashtags.

        Args:
            n (int): Number of hashtags to show.
            pct (bool): Percent of all posts if True, otherwise the number
                    of posts with relevant hashtags.

        Returns:
            list of tuples: Results for each category.

        """
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
