import click
import requests
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gitlab_url_builder import UrlBuilder, Ressource
from time_string_helper import parse_time
import datetime
from dateutil.parser import parse

class ContributorList():
    """
    Gitlab Contributor list as a Pandas DataFrame
    """
    def __init__(self):
        self.contributors = pd.DataFrame(columns=['id', 'name', 'username']).set_index('id')
    
    def __str__(self):
        return str(self.contributors)

    def add(self, id, name, username):
        self.contributors.loc[id] = { 'name': name, 'username': username }

    def load(self, url_builder):
        for member in requests.get(url_builder.build(Ressource.MEMBERS)).json():
            self.add(member['id'], member['name'], member['username'])

class IssueList():
    """
    Gitlab Issue List as a Pandas DataFrame
    """
    def __init__(self, get_notes=False):
        self.issues = pd.DataFrame(columns=['id', 'title', 'milestone_id', 'labels', 'time_estimate', 'time_spent']).set_index('id')
        self.note_list = None
        if get_notes:
            self.note_list = NoteList()

    def __str__(self):
        return str(self.issues)

    def add(self, id, title, milestone_id, labels, time_estimate, time_spent):
        self.issues.loc[id] = { 'title': title, 'milestone_id': milestone_id, 'labels': labels, 'time_estimate': time_estimate, 'time_spent': time_spent }

    def load(self, url_builder):
        page = 1
        has_more = True
        while has_more:
            new_issues = requests.get(url_builder.build(Ressource.ISSUES) + '&page=' + str(page)).json()
            if len(new_issues) == 0 or True:
                has_more = False
            for issue in new_issues:
                milestone_id = 0 if issue['milestone'] == None else issue['milestone']['id']
                self.add(issue['id'], issue['title'], milestone_id, issue['labels'], issue['time_stats']['time_estimate'], issue['time_stats']['total_time_spent'])
                if self.note_list:
                    self.note_list.load(url_builder, issue['iid'])
            page += 1

class NoteList():
    """
    Gitlab Issue List as a Pandas DataFrame
    """
    def __init__(self):
        self.notes = pd.DataFrame(columns=['id', 'member_id', 'time', 'date']).set_index('id')

    def __str__(self):
        return str(self.notes)

    def add(self, id, member_id, time, date):
        self.notes.loc[id] = { 'member_id': member_id, 'time': time, 'date': date }

    def load(self, url_builder, issue_id):
        for note in requests.get(url_builder.build(Ressource.NOTES).replace(':issue_id', str(issue_id))).json():
            self.add(note['id'], note['author']['id'], parse_time(note['body']), parse(note['updated_at']).date())


    
@click.command()
@click.option('-a', '--access-token', help='Personal Access Token.')
@click.option('-p', '--project', help='The Project ID.', type=int)
@click.option('-b', '--base-url', default='https://gitlab.dev.ifs.hsr.ch/api/v4', help='Base URL of the GitLab API.')
def report(base_url, project, access_token):
    url_builder = UrlBuilder(base_url, project, access_token)

    all_contributors = ContributorList()
    all_contributors.load(url_builder)
    print('CONTRIBUTORS')
    print(60*'-')
    print(all_contributors)

    all_issues = IssueList(get_notes=True)
    all_issues.load(url_builder)
    print('ISSUES')
    print(60*'-')
    print(all_issues)
    
    all_notes = all_issues.note_list
    print('NOTES')
    print(60*'-')
    print(all_notes)

    print('SUM OF NOTES')
    print(60*'-')
    notes_aggregate = all_notes.notes.groupby(['member_id', 'date']).sum()
    print(notes_aggregate)
    notes_aggregate.plot(x='date')
    plt.show()

def old():
    project_json = requests.get(project_api_string).json()
    labels_dict = requests.get(get_gitlab_url(base_url, project, 'labels', access_token, ['with_counts=yes'])).json()
    members_dict = requests.get(get_gitlab_url(base_url, project, 'members/all', access_token)).json()
    issues_dict = get_all_from_pages(get_gitlab_url(base_url, project, 'issues', access_token, ['scope=all']))
    project = {}
    for key in project_json['_links']:
        page = 0
        more_objects = True
        while more_objects:
            current_objects = requests.get(
                project_json['_links'][key] 
                + '?scope=all&per_page=100&page='
                + str(page)
                + '&private_token='
                + access_token).json()
            if page == 0:
                project[key] = current_objects
            else:
                project[key].append(current_objects)
            page += 1
            more_objects = len(current_objects) > 0 and not (current_objects == project[key])


    labels = pd.DataFrame(labels_dict, columns=['id', 'name', 'color'])
    labels['total_time'] = 0
    members = pd.DataFrame(members_dict)
    issues = pd.DataFrame(issues_dict)

    for issue in issues_dict:
        if 'labels' in issue:
            for label in issue['labels']:
                labels.loc[labels['name'] == label, 'total_time'] += issue['time_stats']['total_time_spent']
    
    labels.plot.pie(y='total_time', labels=labels['name'], legend=None, colors=labels['color'])
    plt.show()
    click.echo(labels)
    click.echo(issues)


def get_gitlab_url(base_url, project_nr, resource, access_token, additional_parameters=[]):
    url = f'{base_url}/projects/{project_nr}/{resource}/'
    url += f'?private_token={access_token}'
    for param in additional_parameters:
        url += f'&{param}'
    return url

def get_all_from_pages(url):
    objects = {}
    page = 0
    more_objects = True
    while more_objects:
        current_objects = requests.get(url + '&per_page=100&page=' + str(page)).json()
        more_objects = len(current_objects) > 0 and not (current_objects == objects)
        if page == 0:
            objects = current_objects
        else:
            objects.append(current_objects)
        page += 1
    return objects


if __name__ == '__main__':
    report()
