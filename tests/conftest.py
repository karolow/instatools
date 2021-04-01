import json
from pytest import fixture


tags_json_path = 'tests/data/raw/api_response_tags_endpoint.json'
locations_json_path = 'tests/data/raw/api_reposnse_locations_endpoint.json'
multiple_json_path = 'tests/data/raw/'
all_posts_path = 'tests/data/processed/extracted_posts.json'

# HELPER FUNCTIONS


def load_data_from_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        api_response = json.load(file)
    return api_response


def parse_node(node):
    id = node['node']['id']
    shortcode = node['node']['shortcode']
    timestamp = node['node']['taken_at_timestamp']
    owner = node['node']['owner']['id']
    likes = node['node']['edge_liked_by']['count']
    comments = node['node']['edge_media_to_comment']['count']
    display_url = node['node']['display_url']
    caption = node['node'].get('accessibility_caption', '')

    if node['node']['edge_media_to_caption']['edges']:
        text = node['node']['edge_media_to_caption']['edges'][0]['node']['text']
    else:
        text = ''

    id = id
    record = {
        'shortcode': shortcode,
        'owner': owner,
        'timestamp': timestamp,
        'likes': likes,
        'comments': comments,
        'display_url': display_url,
        'caption': caption,
        'text': text
    }

    return id, record


# FIXTURES

@fixture
def tags_endpoint_json_data(path=tags_json_path):
    api_response = load_data_from_file(path)
    edges = api_response['graphql']['hashtag']['edge_hashtag_to_media']['edges']
    yield path, edges


@fixture
def locations_endpoint_json_data(path=locations_json_path):
    api_response = load_data_from_file(path)
    edges = api_response['graphql']['location']['edge_location_to_media']['edges']
    yield path, edges


@fixture(params=range(0, 10))
def tags_endpoint_node(request, path=tags_json_path):
    api_response = load_data_from_file(tags_json_path)
    node = api_response['graphql']['hashtag']['edge_hashtag_to_media']['edges'][request.param]
    id, record = parse_node(node)
    yield node, (id, record)


@fixture(params=range(0, 10))
def locations_endpoint_node(request, path=locations_json_path):
    api_response = load_data_from_file(locations_json_path)
    node = api_response['graphql']['location']['edge_location_to_media']['edges'][request.param]
    id, record = parse_node(node)
    yield node, (id, record)


@fixture
def multiple_json_path(path=multiple_json_path):
    posts = load_data_from_file(all_posts_path)
    yield path, posts
