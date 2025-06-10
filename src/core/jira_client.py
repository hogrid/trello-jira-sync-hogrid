import aiohttp
from decouple import config

class JiraClient:
    """
    Async client for Jira REST API using aiohttp.
    """
    def __init__(self, host_env: str, user_env: str, token_env: str):
        self.host = config(host_env)
        self.user = config(user_env)
        self.api_token = config(token_env)
        if not self.host or not self.user or not self.api_token:
            raise ValueError('Jira credentials not set')
        self.auth = aiohttp.BasicAuth(self.user, self.api_token)

    async def search_issues(self, jql: str):
        url = f'{self.host}/rest/api/2/search'
        params = {'jql': jql}
        async with aiohttp.ClientSession(auth=self.auth) as session:
            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data.get('issues', [])

    async def create_or_update_issue(self, issue_key: str, fields: dict):
        if issue_key:
            # update
            url = f'{self.host}/rest/api/2/issue/{issue_key}'
            method = 'PUT'
        else:
            # create
            url = f'{self.host}/rest/api/2/issue'
            method = 'POST'
        async with aiohttp.ClientSession(auth=self.auth) as session:
            if method == 'PUT':
                async with session.put(url, json={'fields': fields}) as resp:
                    resp.raise_for_status()
                    return await resp.json()
            else:
                async with session.post(url, json={'fields': fields}) as resp:
                    resp.raise_for_status()
                    return await resp.json()
