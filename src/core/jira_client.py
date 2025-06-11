import aiohttp
import logging

class JiraClient:
    """
    Async client for Jira REST API using aiohttp.
    """
    def __init__(self, host: str, user: str, api_token: str):
        self.host = host
        self.user = user
        self.api_token = api_token

        if not self.host or not self.user or not self.api_token:
            raise ValueError('Credenciais do Jira não configuradas corretamente')

        self.auth = aiohttp.BasicAuth(self.user, self.api_token)
        self.logger = logging.getLogger(__name__)

    async def _make_request(self, method: str, endpoint: str, params: dict = None, json: dict = None) -> dict:
        """
        Faz uma requisição à API do Jira.
        """
        url = f'{self.host}/rest/api/2/{endpoint}'

        try:
            async with aiohttp.ClientSession(auth=self.auth) as session:
                async with session.request(method, url, params=params, json=json) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except aiohttp.ClientError as e:
            self.logger.error(f"Erro na requisição ao Jira: {str(e)}")
            raise

    async def search_issues(self, jql: str):
        """
        Busca issues usando JQL.
        """
        self.logger.info(f"Buscando issues com JQL: {jql}")
        params = {'jql': jql}
        data = await self._make_request('GET', 'search', params=params)
        return data.get('issues', [])

    async def create_or_update_issue(self, issue_key: str, fields: dict):
        """
        Cria ou atualiza uma issue.
        """
        if issue_key:
            self.logger.info(f"Atualizando issue {issue_key}")
            url = f'issue/{issue_key}'
            method = 'PUT'
        else:
            self.logger.info("Criando nova issue")
            url = 'issue'
            method = 'POST'

        return await self._make_request(method, url, json={'fields': fields})

    async def add_comment(self, issue_key: str, body: str):
        """
        Adiciona um comentário a uma issue.
        """
        self.logger.info(f"Adicionando comentário à issue {issue_key}")
        url = f'issue/{issue_key}/comment'
        return await self._make_request('POST', url, json={'body': body})

    async def get_comments(self, issue_key: str):
        """
        Obtém os comentários de uma issue.
        """
        self.logger.info(f"Obtendo comentários da issue {issue_key}")
        url = f'issue/{issue_key}/comment'
        data = await self._make_request('GET', url)
        return data.get('comments', [])
