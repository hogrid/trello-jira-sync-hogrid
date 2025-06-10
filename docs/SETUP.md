# Setup Instructions

This document guides you through preparing and running the multi-board Trello–Jira sync solution.

## Prerequisites

- Docker (optional) or Python 3.12
- Git
- GitHub repository with secrets configured

## Configuration

1. Copy `.env.template` to `.env` and fill in your credentials:
   ```bash
   cp config/.env.template .env
   # Edit .env with your API keys and tokens
   ```

2. Update `config/mappings.yaml` with your board-project pairs and desired sync fields.

## Running Locally

Install dependencies:
```bash
pip install -r requirements.txt
```
Run a specific connection (index 0 for first connection):
```bash
python src/workers/connection_worker.py --connection-index 0
```

## Running with Docker

Build the container:
```bash
docker build -t trello-jira-sync -f docker/Dockerfile .
```
Run the default worker (connection 0):
```bash
docker run --env-file .env trello-jira-sync
```

## GitHub Actions

The workflow in `.github/workflows/sync.yml` parses `config/mappings.yaml` and runs a job per connection:

```yaml
name: Multi-Board Sync
on:
  workflow_dispatch:
  schedule:
    - cron: '*/1 * * * *'
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      connections: ${{ steps.parse.outputs.connections }}
    steps:
      - uses: actions/checkout@v3
      - name: Parse mappings
        id: parse
        run: |
          pip install pyyaml jq
          python - <<EOF
import yaml, json
m=yaml.safe_load(open('config/mappings.yaml'))['connections']
print('::set-output name=connections::'+json.dumps(m))
EOF

  sync:
    needs: setup
    runs-on: ubuntu-latest
    strategy:
      matrix:
        connection: ${{ fromJson(needs.setup.outputs.connections) }}
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run sync
        run: |
          python src/workers/connection_worker.py --config config/mappings.yaml --connection-index ${{ matrix.connection_index }}
        env:
          TRELLO_KEY: ${{ secrets[matrix.connection.trello.api_key] }}
          TRELLO_TOKEN: ${{ secrets[matrix.connection.trello.token] }}
          JIRA_URL: ${{ matrix.connection.jira.host }}
          JIRA_USER: ${{ secrets[matrix.connection.jira.user] }}
          JIRA_API_TOKEN: ${{ secrets[matrix.connection.jira.api_token] }}
```
