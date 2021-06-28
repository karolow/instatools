from instatools.preprocessing.preprocessing import (
    HashtagPosts,
    LocationPosts
)


class ExtractEdgesFromJsonTests:
    def test_for_hashtag_endpoint(self, hashtag_endpoint_data):
        raw_file, processed_json = hashtag_endpoint_data
        result = HashtagPosts._extract_edges_from_json(raw_file)
        assert result == processed_json

    def test_for_location_endpoint(self, location_endpoint_data):
        raw_file, processed_json = location_endpoint_data
        result = LocationPosts._extract_edges_from_json(raw_file)
        assert result == processed_json


class ExtractPostTests:

    def test_for_hashtag_endpoint(self, hashtag_endpoint_node):
        node, (id, record) = hashtag_endpoint_node
        result_id, result_record = HashtagPosts._extract_post(node)
        assert result_id == id and result_record == record

    def test_for_location_endpoint(self, location_endpoint_node):
        node, (id, record) = location_endpoint_node
        result_id, result_record = LocationPosts._extract_post(node)
        assert result_id == id and result_record == record


class ParseFromMultipleJsonFilesTests:

    def test_for_hashtag_endpoint(self, multiple_hashtag_json):
        path, posts = multiple_hashtag_json
        result = HashtagPosts.from_json_files(path)
        assert result.posts == posts

    def test_for_location_endpoint(self, multiple_location_json):
        path, posts = multiple_location_json
        result = LocationPosts.from_json_files(path)
        assert result.posts == posts


class RemovePostsTests:

    def test_for_hashtag_endpoint(self):

    def test_for_location_endpoint(self)
