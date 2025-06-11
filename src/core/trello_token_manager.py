import os
import aiohttp
import logging
from typing import Dict, Optional
from decouple import config

class TrelloTokenManager:
    """
    Gerencia tokens de acesso do Trello com suporte a refresh token.
    """
    def __init__(self, client_id_env: str, client_secret_env: str, access_token_env: str, refresh_token_env: str):
        self.client_id = config(client_id_env)
        self.client_secret = config(client_secret_env)
        self.access_token = config(access_token_env)
        self.refresh_token = config(refresh_token_env)

        if not all([self.client_id, self.client_secret, self.access_token, self.refresh_token]):
            raise ValueError('Credenciais do Trello não configuradas corretamente')

        self.logger = logging.getLogger(__name__)

    async def refresh_access_token(self) -> Dict[str, str]:
        """
        Atualiza o token de acesso usando o refresh token.
        Retorna um dicionário com os novos tokens.
        """
        url = "https://trello.com/oauth2/token"
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        tokens = await response.json()
                        self.access_token = tokens['access_token']
                        self.refresh_token = tokens.get('refresh_token', self.refresh_token)

                        # Atualiza as variáveis de ambiente
                        os.environ[access_token_env] = self.access_token
                        os.environ[refresh_token_env] = self.refresh_token

                        self.logger.info("Tokens do Trello atualizados com sucesso")
                        return tokens
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Erro ao atualizar token: {error_text}")
                        raise Exception(f"Falha ao atualizar token: {response.status}")
        except Exception as e:
            self.logger.error(f"Erro ao atualizar token: {str(e)}")
            raise

    async def get_valid_access_token(self) -> str:
        """
        Retorna um token de acesso válido, atualizando se necessário.
        """
        return self.access_token

    def get_current_tokens(self) -> Dict[str, str]:
        """
        Retorna os tokens atuais.
        """
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token
        }
