import asyncio
import logging
import os
from typing import Dict
from .trello_client import TrelloClient
from .jira_client import JiraClient

logger = logging.getLogger(__name__)

async def sync_changes(connection: Dict, last_sync: str):
    """
    Perform bidirectional sync for a single connection.
    """
    trello_conf = connection['trello']
    jira_conf = connection['jira']
    sync_conf = connection['sync']

    # Lê as variáveis de ambiente usando os nomes definidos no arquivo de configuração
    board_id = os.getenv(trello_conf['board_id'])
    api_key = os.getenv(trello_conf['api_key'])
    token = os.getenv(trello_conf['token'])
    jira_host = os.getenv(jira_conf['host'])
    jira_user = os.getenv(jira_conf['user'])
    jira_token = os.getenv(jira_conf['api_token'])
    project_key = os.getenv(jira_conf['project_key'])

    trello = TrelloClient(
        board_id=board_id,
        api_key=api_key,
        token=token
    )
    jira = JiraClient(
        host=jira_host,
        user=jira_user,
        api_token=jira_token
    )

    try:
        # Trello -> Jira
        logger.info(f"Iniciando sincronização Trello -> Jira desde {last_sync}")
        updates = await trello.get_updates_since(last_sync)
        for card in updates:
            # convert and sync to Jira
            fields = convert_to_jira_fields(card, sync_conf)
            issue_key = find_existing_issue(jira, card, connection)
            result = await jira.create_or_update_issue(issue_key, fields)
            logger.info(f"Card {card['id']} sincronizado com issue {result.get('key', 'nova')}")

        # Jira -> Trello
        logger.info(f"Iniciando sincronização Jira -> Trello desde {last_sync}")
        jql = f"project={project_key} AND updated > \"{last_sync}\""
        issues = await jira.search_issues(jql)
        for issue in issues:
            data = convert_to_trello_fields(issue, sync_conf)
            card_id = issue['fields'].get(connection['jira']['customfield_trello_id'])
            result = await trello.create_or_update_card(card_id, data)
            logger.info(f"Issue {issue['key']} sincronizada com card {result.get('id', 'novo')}")

    except Exception as e:
        logger.error(f"Erro durante a sincronização: {str(e)}")
        raise

async def run_sync(connection: Dict, last_sync: str):
    """
    Executa a sincronização com tratamento de erros.
    """
    try:
        await sync_changes(connection, last_sync)
    except Exception as e:
        logger.error(f"Falha na sincronização: {str(e)}")
        raise

def convert_to_jira_fields(card, sync_conf):
    """
    Converte campos do Trello para o formato do Jira.
    """
    fields = {}
    if 'title' in sync_conf['fields']:
        fields['summary'] = card.get('name', '')
    if 'description' in sync_conf['fields']:
        fields['description'] = card.get('desc', '')
    if 'due_date' in sync_conf['fields'] and card.get('due'):
        fields['duedate'] = card['due']
    return fields

def convert_to_trello_fields(issue, sync_conf):
    """
    Converte campos do Jira para o formato do Trello.
    """
    fields = {}
    if 'title' in sync_conf['fields']:
        fields['name'] = issue['fields'].get('summary', '')
    if 'description' in sync_conf['fields']:
        fields['desc'] = issue['fields'].get('description', '')
    if 'due_date' in sync_conf['fields'] and issue['fields'].get('duedate'):
        fields['due'] = issue['fields']['duedate']
    return fields

def find_existing_issue(jira: JiraClient, card, connection):
    """
    Procura uma issue existente baseada no ID do card do Trello.
    """
    customfield = connection['jira']['customfield_trello_id']
    # Lê project_key da variável de ambiente
    project_key = os.getenv('JIRA_PROJECT_KEY')
    jql = f"project={project_key} AND \"{customfield}\" = \"{card['id']}\""
    issues = asyncio.run(jira.search_issues(jql))
    return issues[0]['key'] if issues else None
