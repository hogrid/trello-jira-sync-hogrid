import aiohttp
import logging
from decouple import config

class TrelloClient:
    """
    Async client for Trello API using aiohttp.
    """
    BASE_URL = 'https://api.trello.com/1'

    def __init__(self, board_id: str, api_key_env: str, token_env: str):
        self.board_id = board_id
        self.api_key = config(api_key_env)
        self.token = config(token_env)

        if not self.api_key or not self.token:
            raise ValueError('Trello key/token não definidos nas variáveis de ambiente')

        self.logger = logging.getLogger(__name__)

    async def _make_request(self, method: str, endpoint: str, params: dict = None, json: dict = None) -> dict:
        """
        Faz uma requisição à API do Trello.
        """
        url = f'{self.BASE_URL}/{endpoint}'

        # Adiciona os parâmetros de autenticação
        if params is None:
            params = {}
        params.update({
            'key': self.api_key,
            'token': self.token
        })

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, params=params, json=json) as resp:
                        resp.raise_for_status()
                        return await resp.json()
        except Exception as e:
            self.logger.error(f"Erro na requisição ao Trello: {str(e)}")
            raise

    async def get_updates_since(self, since: str):
        """
        Obtém atualizações do board desde uma data específica.
        """
        params = {'since': since}
        return await self._make_request('GET', f'boards/{self.board_id}/cards', params=params)

    async def create_or_update_card(self, card_id: str, data: dict):
        """
        Cria ou atualiza um card.
        """
        if card_id:
            return await self._make_request('PUT', f'cards/{card_id}', json=data)
        else:
            return await self._make_request('POST', 'cards', json=data)

    async def get_checklists(self, card_id: str):
        """
        Obtém as checklists de um card.
        """
        return await self._make_request('GET', f'cards/{card_id}/checklists')

    async def get_comments(self, card_id: str):
        """
        Obtém os comentários de um card.
        """
        params = {'filter': 'commentCard'}
        return await self._make_request('GET', f'cards/{card_id}/actions', params=params)

    async def add_comment(self, card_id: str, text: str):
        """
        Adiciona um comentário a um card.
        """
        params = {'text': text}
        return await self._make_request('POST', f'cards/{card_id}/actions/comments', params=params)

    async def get_attachments(self, card_id: str):
        """
        Obtém os anexos de um card.
        """
        return await self._make_request('GET', f'cards/{card_id}/attachments')
