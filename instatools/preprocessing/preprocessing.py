from datetime import datetime
import json
from pathlib import Path
import re


def extract_edges_from_json(file_name):

    with open(file_name) as file:
        data = json.load(file)

    if 'location' in data['graphql'].keys():
        return data['graphql']['location']['edge_location_to_media']['edges']
    elif 'hashtag' in data['graphql'].keys():
        return data['graphql']['hashtag']['edge_hashtag_to_media']['edges']


def extract_post(node):

    id = node['node']['id']
    shortcode = node['node']['shortcode']
    timestamp = datetime.fromtimestamp(node['node']['taken_at_timestamp'])
    owner = node['node']['owner']['id']
    likes = node['node']['edge_liked_by']['count']
    comments = node['node']['edge_media_to_comment']['count']
    display_url = node['node']['display_url']
    caption = node['node'].get('accessibility_caption', '')

    if node['node']['edge_media_to_caption']['edges']:
        text = node['node']['edge_media_to_caption']['edges'][0]['node']['text']
    else:
        text = ''

    hashtags = [tag.lower() for tag in re.findall('#[^#\\s]+', text) if tag[1:].isalnum()]

    id = id
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


def json_files_to_dict(input_path):

    files = Path(input_path).glob('**/*.json')
    posts = dict()

    for file in files:
        edges = extract_edges_from_json(file)

        for node in edges:
            id, content = extract_post(node)
            posts.setdefault(id, content)

    return posts


def dict_to_hashes(dict, key_name='hashtags'):
    hashes = [v[key_name] for k, v in dict.items() if v[key_name]]
    return hashes
