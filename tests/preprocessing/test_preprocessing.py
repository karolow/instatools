from instatools.preprocessing.preprocessing import (
    extract_edges_from_json,
    extract_post,
    json_files_to_dict,
)


class ExtractEdgesFromJsonTests:

    def test_for_tags_endpoint(self, tags_endpoint_json_data):
        raw_file, processed_json = tags_endpoint_json_data
        result = extract_edges_from_json(raw_file)
        assert result == processed_json

    def test_for_locations_endpoint(self, locations_endpoint_json_data):
        raw_file, processed_json = locations_endpoint_json_data
        result = extract_edges_from_json(raw_file)
        assert result == processed_json


class ExtractPostTests:

    def test_for_tags_endpoint(self, tags_endpoint_node):
        node, (id, record) = tags_endpoint_node
        result_id, result_record = extract_post(node)
        assert result_id == id and result_record == record

    def test_for_locations_endpoint(self, locations_endpoint_node):
        node, (id, record) = locations_endpoint_node
        result_id, result_record = extract_post(node)
        assert result_id == id and result_record == record


class JsonFilesToDictTests:

    def test_multiple_files_to_dict(self, multiple_json_path):
        path, posts = multiple_json_path
        result = json_files_to_dict(path)
        assert result == posts
