import aiohttp
import logging
from decouple import config
from .trello_token_manager import TrelloTokenManager

class TrelloClient:
    """
    Async client for Trello API using aiohttp.
    """
    BASE_URL = 'https://api.trello.com/1'

    def __init__(self, board_id: str, client_id_env: str, client_secret_env: str, access_token_env: str, refresh_token_env: str):
        self.board_id = board_id
        self.token_manager = TrelloTokenManager(
            client_id_env=client_id_env,
            client_secret_env=client_secret_env,
            access_token_env=access_token_env,
            refresh_token_env=refresh_token_env
        )
        self.logger = logging.getLogger(__name__)

    async def _make_request(self, method: str, endpoint: str, params: dict = None, json: dict = None) -> dict:
        """
        Faz uma requisição à API do Trello com suporte a refresh token.
        """
        url = f'{self.BASE_URL}/{endpoint}'
        access_token = await self.token_manager.get_valid_access_token()

        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, params=params, json=json, headers=headers) as resp:
                    if resp.status == 401:
                        # Token expirado, tenta atualizar
                        await self.token_manager.refresh_access_token()
                        # Tenta novamente com o novo token
                        access_token = await self.token_manager.get_valid_access_token()
                        headers = {'Authorization': f'Bearer {access_token}'}
                        async with session.request(method, url, params=params, json=json, headers=headers) as retry_resp:
                            retry_resp.raise_for_status()
                            return await retry_resp.json()
                    else:
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
        data = {'text': text}
        return await self._make_request('POST', f'cards/{card_id}/actions/comments', json=data)

    async def get_attachments(self, card_id: str):
        """
        Obtém os anexos de um card.
        """
        return await self._make_request('GET', f'cards/{card_id}/attachments')
