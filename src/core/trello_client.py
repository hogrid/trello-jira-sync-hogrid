import aiohttp
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
            raise ValueError('Trello credentials not set')

    async def get_updates_since(self, since: str):
        params = {'key': self.api_key, 'token': self.token, 'since': since}
        url = f'{self.BASE_URL}/boards/{self.board_id}/cards'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def create_or_update_card(self, card_id: str, data: dict):
        params = {'key': self.api_key, 'token': self.token}
        url = f'{self.BASE_URL}/cards/{card_id}'
        async with aiohttp.ClientSession() as session:
            async with session.put(url, params=params, json=data) as resp:
                resp.raise_for_status()
                return await resp.json()
