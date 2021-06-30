from datetime import datetime
import json
import re
from pytest import fixture


api_response_hashtag_path = 'tests/data/raw/api_response_hashtag_endpoint.json'
api_response_location_path = 'tests/data/raw/api_response_location_endpoint.json'
raw_multiple_files_hashtag_path = 'tests/data/raw_multiple/hashtag'
raw_multiple_files_loacation_path = 'tests/data/raw_multiple/location'
processed_hashtag_posts_path = 'tests/data/processed/extracted_posts_hashtag.json'
processed_location_posts_path = 'tests/data/processed/extracted_posts_location.json'

# HELPER FUNCTIONS


def load_data_from_json_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def parse_node(node):
    id = str(node['media']['pk'])
    url = f"https://www.instagram.com/p/{node['media']['code']}"
    timestamp = datetime.fromtimestamp(node['media']['taken_at']).replace(
        tzinfo=tz.gettz("Europe/Warsaw")).isoformat()
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


# FIXTURES

@fixture
def hashtag_endpoint_data(path=api_response_hashtag_path):
    api_response = load_data_from_json_file(path)

    all_edges = []
    for edges in api_response['data']['recent']['sections']:
        for edge in edges['layout_content']['medias']:
            all_edges.append(edge)

    yield path, all_edges


@fixture
def location_endpoint_data(path=api_response_location_path):
    api_response = load_data_from_json_file(path)

    all_edges = []
    for edges in api_response['native_location_data']['recent']['sections']:
        for edge in edges['layout_content']['medias']:
            all_edges.append(edge)

    yield path, all_edges


@fixture(params=range(0, 2))
def hashtag_endpoint_node(request, path=api_response_hashtag_path):
    api_response = load_data_from_json_file(path)
    node = api_response['data']['recent']['sections'][0]['layout_content']['medias'][request.param]
    id, record = parse_node(node)
    yield node, (id, record)


@fixture(params=range(0, 2))
def location_endpoint_node(request, path=api_response_location_path):
    api_response = load_data_from_json_file(path)
    node = api_response['native_location_data']['recent']['sections'][0]['layout_content']['medias'][request.param]
    id, record = parse_node(node)
    yield node, (id, record)


@fixture
def multiple_hashtag_json(
        path_raw=raw_multiple_files_hashtag_path,
        path_processed=processed_hashtag_posts_path):
    posts = load_data_from_json_file(path_processed)
    yield path_raw, posts


@fixture
def multiple_location_json(
        path_raw=raw_multiple_files_loacation_path,
        path_processed=processed_location_posts_path):
    posts = load_data_from_json_file(path_processed)
    yield path_raw, posts
