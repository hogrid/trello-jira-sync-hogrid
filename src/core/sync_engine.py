import asyncio
from typing import Dict
from trello_client import TrelloClient
from jira_client import JiraClient

async def sync_changes(connection: Dict, last_sync: str):
    """
    Perform bidirectional sync for a single connection.
    """
    trello_conf = connection['trello']
    jira_conf = connection['jira']
    sync_conf = connection['sync']

    trello = TrelloClient(
        board_id=trello_conf['board_id'],
        api_key_env=trello_conf['api_key'],
        token_env=trello_conf['token']
    )
    jira = JiraClient(
        host_env=jira_conf['host'],
        user_env=jira_conf['user'],
        token_env=jira_conf['api_token']
    )

    # Trello -> Jira
    updates = await trello.get_updates_since(last_sync)
    for card in updates:
        # convert and sync to Jira
        fields = convert_to_jira_fields(card, sync_conf)
        issue_key = find_existing_issue(jira, card, connection)
        result = await jira.create_or_update_issue(issue_key, fields)

    # Jira -> Trello
    jql = f"project={jira_conf['project_key']} AND updated > \"{last_sync}\""
    issues = await jira.search_issues(jql)
    for issue in issues:
        data = convert_to_trello_fields(issue, sync_conf)
        card_id = issue['fields'].get(connection['jira']['customfield_trello_id'])
        await trello.create_or_update_card(card_id, data)

async def run_sync(connection: Dict, last_sync: str):
    await sync_changes(connection, last_sync)

# Placeholder functions

def convert_to_jira_fields(card, sync_conf):
    # TODO: map Trello card to Jira fields based on sync_conf['fields']
    return {}

def convert_to_trello_fields(issue, sync_conf):
    # TODO: map Jira issue to Trello card fields based on sync_conf['fields']
    return {}

def find_existing_issue(jira: JiraClient, card, connection):
    # TODO: implement lookup using customfield mapping
    return None
