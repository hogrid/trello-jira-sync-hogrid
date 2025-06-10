import os
import requests
import logging


class TrelloClient:
    def __init__(self, key=None, token=None):
        self.key = key or os.getenv('TRELLO_KEY')
        self.token = token or os.getenv('TRELLO_TOKEN')
        self.base_url = 'https://api.trello.com/1'
        if not self.key or not self.token:
            raise ValueError('Trello key/token não definidos nas variáveis de ambiente')

    def get_cards(self, board_id, since=None):
        params = {'key': self.key, 'token': self.token}
        if since:
            params['since'] = since
        resp = requests.get(f'{self.base_url}/boards/{board_id}/cards', params=params)
        resp.raise_for_status()
        return resp.json()

    def update_card(self, card_id, data):
        params = {'key': self.key, 'token': self.token}
        resp = requests.put(f'{self.base_url}/cards/{card_id}', params=params, json=data)
        resp.raise_for_status()
        return resp.json()

    def get_checklists(self, card_id):
        params = {'key': self.key, 'token': self.token}
        resp = requests.get(f'{self.base_url}/cards/{card_id}/checklists', params=params)
        resp.raise_for_status()
        return resp.json()

    def get_comments(self, card_id):
        params = {'key': self.key, 'token': self.token, 'filter': 'commentCard'}
        resp = requests.get(f'{self.base_url}/cards/{card_id}/actions', params=params)
        resp.raise_for_status()
        return resp.json()

    def add_comment(self, card_id, text):
        params = {'key': self.key, 'token': self.token, 'text': text}
        resp = requests.post(f'{self.base_url}/cards/{card_id}/actions/comments', params=params)
        resp.raise_for_status()
        return resp.json()

    def get_attachments(self, card_id):
        params = {'key': self.key, 'token': self.token}
        resp = requests.get(f'{self.base_url}/cards/{card_id}/attachments', params=params)
        resp.raise_for_status()
        return resp.json()


class JiraClient:
    def __init__(self, url=None, user=None, api_token=None):
        self.url = url or os.getenv('JIRA_URL')
        self.user = user or os.getenv('JIRA_USER')
        self.api_token = api_token or os.getenv('JIRA_API_TOKEN')
        if not self.url or not self.user or not self.api_token:
            raise ValueError('JIRA_URL, JIRA_USER ou JIRA_API_TOKEN não definidos nas variáveis de ambiente')
        self.session = requests.Session()
        self.session.auth = (self.user, self.api_token)
        self.headers = {'Content-Type': 'application/json'}

    def search_issues(self, jql):
        resp = self.session.get(f'{self.url}/rest/api/2/search', params={'jql': jql})
        resp.raise_for_status()
        return resp.json().get('issues', [])

    def create_issue(self, project_key, summary, description, issue_type='Task', duedate=None, custom_fields=None):
        payload = {'fields': {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
        }}
        if duedate:
            payload['fields']['duedate'] = duedate
        if custom_fields:
            payload['fields'].update(custom_fields)
        resp = self.session.post(f'{self.url}/rest/api/2/issue', json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def update_issue(self, issue_key, fields):
        payload = {'fields': fields}
        resp = self.session.put(f'{self.url}/rest/api/2/issue/{issue_key}', json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def add_comment(self, issue_key, body):
        resp = self.session.post(f'{self.url}/rest/api/2/issue/{issue_key}/comment', json={'body': body}, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_comments(self, issue_key):
        resp = self.session.get(f'{self.url}/rest/api/2/issue/{issue_key}/comment')
        resp.raise_for_status()
        return resp.json().get('comments', [])

    def create_subtask(self, parent_key, summary, description='', duedate=None, issue_type='Sub-task'):
        payload = {'fields': {
            'project': {'key': parent_key.split('-')[0]},
            'parent': {'key': parent_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
        }}
        if duedate:
            payload['fields']['duedate'] = duedate
        resp = self.session.post(f'{self.url}/rest/api/2/issue', json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()
