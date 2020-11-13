import click
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gitlab_url_builder import UrlBuilder
from gitlab_ressource_classes import ContributorList, IssueList


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
    notes_group = all_notes.notes.groupby(
        by=['member_id', 'date'], squeeze=True).sum().unstack(fill_value=0)
    notes_group.columns = notes_group.columns.droplevel()
    notes_group['name'] = all_contributors.contributors.loc[
        notes_group.index.values.astype(int), 'name']
    notes_group = notes_group.set_index('name').transpose()
    ax = notes_group.plot.bar()
    for p in ax.patches:
        ax.annotate('{:.1f}'.format(p.get_height()),
                    (p.get_x() * 1.005, p.get_height() * 1.005))
    plt.axhline(y=17.5, color='r', linestyle='dashed')
    plt.savefig('./images/time_weeks.png')

if __name__ == '__main__':
    report()
