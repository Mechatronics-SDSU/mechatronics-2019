class MissionTask(object):
    def __init__(self, json_file):
        self.type = json_file["type"]
        self.estimated_position = dict(json_file["estimated_position"])
        self.timeout = json_file["timeout"]
