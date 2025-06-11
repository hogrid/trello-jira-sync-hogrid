import argparse
import asyncio
import logging
import os
import yaml
from core.sync_engine import run_sync

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Run Trello-Jira sync for a connection')
    parser.add_argument('--config', default='config/mappings.yaml', help='Path to mappings YAML')
    parser.add_argument('--connection-index', type=int, required=True, help='Index of connection to run')
    parser.add_argument('--last-sync', default=None, help='Timestamp of last sync')
    args = parser.parse_args()

    try:
        logger.info(f"Carregando configuração de {args.config}")
        data = yaml.safe_load(open(args.config))
        connections = data.get('connections', [])

        if args.connection_index < 0 or args.connection_index >= len(connections):
            raise IndexError(f'connection-index {args.connection_index} fora do intervalo (0-{len(connections)-1})')

        connection = connections[args.connection_index]
        last_sync = args.last_sync or '1970-01-01T00:00:00Z'

        logger.info(f"Iniciando sincronização para conexão {args.connection_index}")
        logger.info(f"Board Trello: {os.getenv(connection['trello']['board_id'], 'NOT_SET')}")
        logger.info(f"Projeto Jira: {os.getenv(connection['jira']['project_key'], 'NOT_SET')}")

        asyncio.run(run_sync(connection, last_sync))
        logger.info("Sincronização concluída com sucesso")

    except FileNotFoundError:
        logger.error(f"Arquivo de configuração não encontrado: {args.config}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Erro ao processar arquivo YAML: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Erro durante a sincronização: {str(e)}")
        raise

if __name__ == '__main__':
    main()
