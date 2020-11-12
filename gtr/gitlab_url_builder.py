from enum import Enum, EnumMeta

class Ressource(Enum):
    MEMBERS = 'members/all?'
    ISSUES = 'issues?scope=all&'
    EVENTS = 'events?'
    NOTES = 'issues/:issue_id/notes?'

class UrlBuilder():
    def __init__(self, base_url, project_id, access_token):
        self.base_url = base_url
        self.project_id = project_id
        self.access_token = access_token

    def build(self, ressource):
        if type(ressource) != type(Ressource.MEMBERS):
            raise Exception('ressource was not of Ressource type')
        return f'{self.base_url}/projects/{self.project_id}/{ressource.value}private_token={self.access_token}'