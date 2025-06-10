import os
import yaml
import json
import logging
from datetime import datetime
from trello_jira_sync import TrelloClient, JiraClient

logging.basicConfig(level=logging.INFO)

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def load_state(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
        return data.get('last_run')
    return '1970-01-01T00:00:00Z'

def save_state(path, timestamp):
    with open(path, 'w') as f:
        json.dump({'last_run': timestamp}, f)

def convert_mentions(text, mapping):
    for src, dst in mapping.items():
        text = text.replace(f'@{src}', f'@{dst}')
    return text

def sync():
    config = load_config()
    state_file = config['sync'].get('state_file', 'state.json')
    last_run = load_state(state_file)
    now = datetime.utcnow().isoformat() + 'Z'
    logging.info(f'Iniciando sincronização (última execução: {last_run})')

    trello_conf = config['trello']
    jira_conf = config['jira']
    trello = TrelloClient()
    jira = JiraClient()

    # Trello -> Jira
    cards = trello.get_cards(trello_conf['board_id'], since=last_run)
    for card in cards:
        if 'list_ids' in trello_conf and card.get('idList') not in trello_conf['list_ids']:
            continue

        cf_id = jira_conf['customfield_trello_id']
        jql = f"project={jira_conf['project_key']} AND \"{cf_id}\" = \"{card['id']}\""
        issues = jira.search_issues(jql)

        summary = card.get('name', '')
        desc = convert_mentions(card.get('desc', ''), jira_conf.get('user_mapping', {}))

        # Attachments
        attachments = trello.get_attachments(card['id'])
        for att in attachments:
            desc += f"\nAttachment: {att.get('url')}"

        # Due date
        fields = {}
        if card.get('due'):
            fields['duedate'] = card.get('due')

        if issues:
            key = issues[0]['key']
            logging.info(f'Atualizando issue {key} para o card {card["id"]}')
            jira.update_issue(key, {'summary': summary, 'description': desc, **fields})

            # Comments
            comments = trello.get_comments(card['id'])
            for c in comments:
                text = convert_mentions(c['data']['text'], jira_conf.get('user_mapping', {}))
                jira.add_comment(key, text)
        else:
            logging.info(f'Criando issue para card {card["id"]}')
            new = jira.create_issue(
                jira_conf['project_key'],
                summary,
                desc,
                duedate=card.get('due'),
                custom_fields={cf_id: card['id']}
            )
            key = new.get('key')

            # Subtasks
            checklists = trello.get_checklists(card['id'])
            for cl in checklists:
                for item in cl.get('checkItems', []):
                    jira.create_subtask(key, item.get('name'), duedate=card.get('due'))

    # Jira -> Trello
    jql2 = f"project={jira_conf['project_key']} AND updated > \"{last_run}\""
    issues = jira.search_issues(jql2)
    inv_mapping = {v: k for k, v in jira_conf.get('user_mapping', {}).items()}

    for issue in issues:
        t_id = issue['fields'].get(jira_conf['customfield_trello_id'])
        if not t_id:
            continue

        logging.info(f'Atualizando card {t_id} para issue {issue["key"]}')
        data = {}
        fields = issue['fields']

        if fields.get('summary'):
            data['name'] = fields['summary']
        if fields.get('description'):
            data['desc'] = fields['description']
        if fields.get('duedate'):
            data['due'] = fields['duedate']

        trello.update_card(t_id, data)

        # Comments
        j_comments = jira.get_comments(issue['key'])
        for jc in j_comments:
            text = convert_mentions(jc.get('body', ''), inv_mapping)
            trello.add_comment(t_id, text)

    save_state(state_file, now)
    logging.info('Sincronização finalizada')

if __name__ == '__main__':
    sync()
