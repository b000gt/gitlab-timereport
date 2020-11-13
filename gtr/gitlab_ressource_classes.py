import requests
import json
import pandas as pd
from gitlab_url_builder import Ressource
from time_string_helper import parse_time, parse_week


class ContributorList():
    """
    Gitlab Contributor list as a Pandas DataFrame
    """

    def __init__(self):
        self.contributors = pd.DataFrame(
            columns=['id', 'name', 'username']).set_index('id')

    def __str__(self):
        return str(self.contributors)

    def add(self, id, name, username):
        self.contributors.loc[id] = {'name': name, 'username': username}

    def load(self, url_builder):
        for member in requests.get(url_builder.build(Ressource.MEMBERS)).json():
            self.add(member['id'], member['name'], member['username'])


class IssueList():
    """
    Gitlab Issue List as a Pandas DataFrame
    """

    def __init__(self, get_notes=False):
        self.issues = pd.DataFrame(columns=[
                                   'id', 'title', 'milestone_id', 'labels', 'time_estimate', 'time_spent']).set_index('id')
        self.note_list = None
        if get_notes:
            self.note_list = NoteList()

    def __str__(self):
        return str(self.issues)

    def add(self, id, title, milestone_id, labels, time_estimate, time_spent):
        self.issues.loc[id] = {'title': title, 'milestone_id': milestone_id,
                               'labels': labels, 'time_estimate': time_estimate, 'time_spent': time_spent}

    def load(self, url_builder):
        page = 1
        has_more = True
        while has_more:
            new_issues = requests.get(url_builder.build(
                Ressource.ISSUES) + '&page=' + str(page)).json()
            if len(new_issues) == 0:
                has_more = False
            for issue in new_issues:
                milestone_id = 0 if issue['milestone'] == None else issue['milestone']['id']
                self.add(issue['id'], issue['title'], milestone_id, issue['labels'],
                         issue['time_stats']['time_estimate'], issue['time_stats']['total_time_spent'])
                if self.note_list:
                    self.note_list.load(url_builder, issue['iid'])
            page += 1


class NoteList():
    """
    Gitlab Issue List as a Pandas DataFrame
    """

    def __init__(self):
        self.notes = pd.DataFrame(
            columns=['id', 'member_id', 'time', 'date']).set_index('id')

    def __str__(self):
        return str(self.notes)

    def add(self, id, member_id, time, date):
        self.notes.loc[id] = {
            'member_id': member_id, 'time': time, 'date': date}

    def load(self, url_builder, issue_id):
        for note in requests.get(url_builder.build(Ressource.NOTES).replace(':issue_id', str(issue_id))).json():
            self.add(note['id'], note['author']['id'],
                     parse_time(note['body']), parse_week(note['updated_at']))
