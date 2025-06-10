# Trello-Jira Sync

A Python-based bidirectional synchronization between Trello and Jira, designed to run on GitHub Actions.

## Features

- Configurable sync interval
- Synchronize card titles and descriptions
- Convert Trello checklists into Jira subtasks
- Support due dates, comments, and attachment links
- Detect changes on both platforms using timestamps
- Convert mentions (e.g., `@trello_user` → `@jira_user`)
- Open source and open to contributions

## Prerequisites

- Python 3.6 or higher
- GitHub repository with Actions enabled

## Installation

```bash
git clone https://github.com/yourusername/trello-jira-sync.git
cd trello-jira-sync
pip install -r requirements.txt
```

## Configuration

Copy the provided `config.yaml` and update with your IDs and mappings:

```yaml
trello:
  board_id: '<TRELLO_BOARD_ID>'
  list_ids:
    - '<LIST_ID_1>'
    - '<LIST_ID_2>'

jira:
  project_key: '<JIRA_PROJECT_KEY>'
  customfield_trello_id: 'customfield_10000'
  user_mapping:
    trello_user1: jira_user1
    trello_user2: jira_user2

sync:
  state_file: 'state.json'
  sync_interval_minutes: 1
```

Set the following environment variables (locally or in GitHub Actions secrets):

- `TRELLO_KEY`
- `TRELLO_TOKEN`
- `JIRA_URL`
- `JIRA_USER`
- `JIRA_API_TOKEN`

## Usage

Run the synchronization script locally:

```bash
python sync_logic.py
```

To customize the sync interval, modify `sync_interval_minutes` in `config.yaml`.

## GitHub Actions Workflow

The workflow file `.github/workflows/sync.yml` is configured to run on a cron schedule (default every minute) and on demand via `workflow_dispatch`. Secrets are used to securely store API keys.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add feature"`)
4. Push to your branch (`git push origin feature/your-feature`)
5. Open a Pull Request and describe your changes

Please ensure code follows Python style guidelines and includes tests where applicable.

## License

This project is licensed under the MIT License.

---

Developed by Emerson Nunes
<emerson@hogrid.com>
