import json


class JsonParse(object):
    def __init__(self, json_file):
        # TODO add file path to json
        # TODO Check if file exists
        # json must be in curr folder
        self.missionjson = None
        with open(json_file, 'r') as file:
            self.missionjson = json.load(file)

    def get(self, parent_tag: str, sub_tag=None):
        # TODO Check if labels exists
        if sub_tag is None:
            return self.missionjson[parent_tag]
        else:
            return self.missionjson[parent_tag][sub_tag]
