from instatools.preprocessing.preprocessing import (
    Posts,
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

    def test_detect_junk_hashtags(self):
        hashtags = ['#foo', '#bar']
        assert Posts._detect_junk_hashtags(hashtags, ['#foo']) is True
        assert Posts._detect_junk_hashtags(hashtags, ['#baz']) is False

    def test_for_hashtag_endpoint(self, multiple_hashtag_json):
        path, posts = multiple_hashtag_json
        hp = HashtagPosts(posts)
        junk_hashtags = ['#medialabkatowice']
        hp_filtered = hp.remove_posts(junk_hashtags)
        assert any([any([hashtag in v['hashtags'] for hashtag in junk_hashtags])
                    for k, v in hp_filtered.posts.items() if v['hashtags']]) is False

    def test_for_location_endpoint(self, multiple_location_json):
        path, posts = multiple_location_json
        lp = LocationPosts(posts)
        junk_hashtags = ['#park', '#sunday']
        lp_filtered = lp.remove_posts(junk_hashtags)
        assert any([any([hashtag in v['hashtags'] for hashtag in junk_hashtags])
                    for k, v in lp_filtered.posts.items() if v['hashtags']]) is False
