# Detailed Configuration Guide

This document provides detailed examples for configuring multiple Trello board to Jira project connections.

## Configuration Structure

The entire synchronization configuration is defined in `config/mappings.yaml`. Each connection requires:

1. Trello board information
2. Jira project information
3. Sync settings (interval, fields)

## Multiple Board-Project Pairs Example

Here's a complete example with three different connections:

```yaml
# config/mappings.yaml
connections:
  # Connection 1: Development board to CORE project
  - trello:
      board_id: ${{ secrets.TRELLO_BOARD_DEV_ID }}
      client_id: ${{ secrets.TRELLO_CLIENT_ID_DEV }}
      client_secret: ${{ secrets.TRELLO_CLIENT_SECRET_DEV }}
      access_token: ${{ secrets.TRELLO_ACCESS_TOKEN_DEV }}
      refresh_token: ${{ secrets.TRELLO_REFRESH_TOKEN_DEV }}
    jira:
      project_key: ${{ secrets.JIRA_KEY_DEV }}
      host: ${{ secrets.JIRA_HOST_DEV }}
      user: ${{ secrets.JIRA_USER_DEV }}
      api_token: ${{ secrets.JIRA_TOKEN_DEV }}
    sync:
      interval: "*/15 * * * *"    # Every 15 minutes
      fields:
        - title
        - description
        - checklists
        - comments
        - attachments
        - due_date

  # Connection 2: Marketing board to MKT project
  - trello:
      board_id: ${{ secrets.TRELLO_BOARD_MKT_ID }}
      client_id: ${{ secrets.TRELLO_CLIENT_ID_MKT }}
      client_secret: ${{ secrets.TRELLO_CLIENT_SECRET_MKT }}
      access_token: ${{ secrets.TRELLO_ACCESS_TOKEN_MKT }}
      refresh_token: ${{ secrets.TRELLO_REFRESH_TOKEN_MKT }}
    jira:
      project_key: ${{ secrets.JIRA_KEY_MKT }}
      host: ${{ secrets.JIRA_HOST_MKT }}
      user: ${{ secrets.JIRA_USER_MKT }}
      api_token: ${{ secrets.JIRA_TOKEN_MKT }}
    sync:
      interval: "0 * * * *"       # Hourly
      fields:
        - title
        - description
        - labels

```

## Environment Variables Setup

For each connection, you need to set up environment variables for the API credentials. Using the example above:

### Local Development

Create a `.env` file based on the `.env.template`:

```
# Development team credentials
TRELLO_CLIENT_ID_DEV=your_client_id...
TRELLO_CLIENT_SECRET_DEV=your_client_secret...
TRELLO_ACCESS_TOKEN_DEV=your_access_token...
TRELLO_REFRESH_TOKEN_DEV=your_refresh_token...
JIRA_USER_DEV=dev.team@company.com
JIRA_TOKEN_DEV=your_jira_token...

# Marketing team credentials
TRELLO_CLIENT_ID_MKT=your_client_id...
TRELLO_CLIENT_SECRET_MKT=your_client_secret...
TRELLO_ACCESS_TOKEN_MKT=your_access_token...
TRELLO_REFRESH_TOKEN_MKT=your_refresh_token...
JIRA_USER_MKT=marketing@company.com
JIRA_TOKEN_MKT=your_jira_token...
```

### GitHub Actions

Set up GitHub Secrets with the same names:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add each environment variable as a secret:
   - TRELLO_CLIENT_ID_DEV
   - TRELLO_CLIENT_SECRET_DEV
   - TRELLO_ACCESS_TOKEN_DEV
   - TRELLO_REFRESH_TOKEN_DEV
   - JIRA_USER_DEV
   - JIRA_TOKEN_DEV
   - (and so on for all teams)

## How Environment Variables Are Used

1. Inside `src/core/trello_token_manager.py`, credentials are loaded:
   ```python
   self.client_id = config(client_id_env)
   self.client_secret = config(client_secret_env)
   self.access_token = config(access_token_env)
   self.refresh_token = config(refresh_token_env)
   ```

2. Inside `src/core/jira_client.py`, credentials are loaded:
   ```python
   self.host = config(host_env)
   self.user = config(user_env)
   self.api_token = config(token_env)
   ```

3. The GitHub Actions workflow uses these environment variables:
   ```yaml
   env:
     TRELLO_CLIENT_ID: ${{ secrets[matrix.connection.trello.client_id] }}
     TRELLO_CLIENT_SECRET: ${{ secrets[matrix.connection.trello.client_secret] }}
     TRELLO_ACCESS_TOKEN: ${{ secrets[matrix.connection.trello.access_token] }}
     TRELLO_REFRESH_TOKEN: ${{ secrets[matrix.connection.trello.refresh_token] }}
     JIRA_URL: ${{ matrix.connection.jira.host }}
     JIRA_USER: ${{ secrets[matrix.connection.jira.user] }}
     JIRA_API_TOKEN: ${{ secrets[matrix.connection.jira.api_token] }}
   ```

## Running Multiple Connections

### Locally (Testing)

Run individual connections by specifying the index:

```bash
# Run first connection (Development board → CORE project)
python src/workers/connection_worker.py --connection-index 0

# Run second connection (Marketing board → MKT project)
python src/workers/connection_worker.py --connection-index 1

# Run third connection (Support board → HELP project)
python src/workers/connection_worker.py --connection-index 2
```

### Via GitHub Actions

The GitHub Actions workflow uses a matrix strategy to run all connections in parallel:

```yaml
strategy:
  matrix:
    connection: ${{ fromJson(needs.setup.outputs.connections) }}
```

### With Docker

To run a specific connection:

```bash
# Run first connection
docker run --env-file .env trello-jira-sync python src/workers/connection_worker.py --connection-index 0

# Run second connection
docker run --env-file .env trello-jira-sync python src/workers/connection_worker.py --connection-index 1
```

Create a docker-compose.yml to run all connections:

```yaml
version: '3'
services:
  dev-sync:
    build: .
    env_file: .env
    command: python src/workers/connection_worker.py --connection-index 0
    restart: always

  mkt-sync:
    build: .
    env_file: .env
    command: python src/workers/connection_worker.py --connection-index 1
    restart: always

  support-sync:
    build: .
    env_file: .env
    command: python src/workers/connection_worker.py --connection-index 2
    restart: always
```

Run with:
```bash
docker-compose up -d
```

## Finding Your Trello Board ID

1. Open your Trello board in browser
2. Add `.json` to the URL: `https://trello.com/b/abcdef12/board-name.json`
3. Look for the `"id"` field at the top level of the JSON response

## Getting Jira Project Key

1. Open your Jira project
2. The project key is shown in the URL: `https://company.atlassian.net/browse/CORE`
3. In this example, `CORE` is the project key

## Obtaining API Credentials

### Trello

1. Go to https://trello.com/app-key to get your API Key
2. Generate a Token by following the instructions on that page
3. For OAuth 2.0 credentials:
   - Go to https://trello.com/app-key
   - Click on "OAuth 2.0" tab
   - Create a new OAuth 2.0 application
   - Get your Client ID and Client Secret
   - Use the OAuth 2.0 flow to get Access Token and Refresh Token

### Jira

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Create an API token and copy it
3. Use your email address as the username
