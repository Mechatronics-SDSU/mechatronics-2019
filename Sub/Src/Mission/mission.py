from missionTask import MissionTask
from jsonParse import JsonParse


class Mission(object):

    def __init__(self, json_file):
        self.json = JsonParse(json_file).missionjson
        self.tasks = []
        self.task_count = len(self.json)
        self.create_tasks()

    def create_tasks(self):
        for task in self.json:
            self.tasks.append(MissionTask(self.json[task]))
