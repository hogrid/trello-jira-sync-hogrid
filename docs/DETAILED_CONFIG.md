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
      board_id: "5f8a421c72b6c32141a1e45a"
      api_key: "TRELLO_KEY_DEV"   # Env variable name
      token: "TRELLO_TOKEN_DEV"   # Env variable name
    jira:
      project_key: "CORE"
      host: "https://company.atlassian.net"
      user: "JIRA_USER_DEV"       # Env variable name
      api_token: "JIRA_TOKEN_DEV" # Env variable name
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
      board_id: "6e2b531d83c7d43252b2f56b"
      api_key: "TRELLO_KEY_MKT"
      token: "TRELLO_TOKEN_MKT"
    jira:
      project_key: "MKT"
      host: "https://company.atlassian.net"
      user: "JIRA_USER_MKT"
      api_token: "JIRA_TOKEN_MKT"
    sync:
      interval: "0 * * * *"       # Hourly
      fields:
        - title
        - description
        - labels

  # Connection 3: Support board to HELP project
  - trello:
      board_id: "7f1c642e94d8e54363c3g67c"
      api_key: "TRELLO_KEY_SUPPORT"
      token: "TRELLO_TOKEN_SUPPORT"
    jira:
      project_key: "HELP"
      host: "https://support.atlassian.net"  # Different Jira instance
      user: "JIRA_USER_SUPPORT"
      api_token: "JIRA_TOKEN_SUPPORT"
    sync:
      interval: "*/5 * * * *"     # Every 5 minutes
      fields:
        - title
        - comments
```

## Environment Variables Setup

For each connection, you need to set up environment variables for the API credentials. Using the example above:

### Local Development

Create a `.env` file based on the `.env.template`:

```
# Development team credentials
TRELLO_KEY_DEV=a1b2c3d4e5f6g7h8i9j0...
TRELLO_TOKEN_DEV=a1b2c3d4e5f6g7h8i9j0...
JIRA_USER_DEV=dev.team@company.com
JIRA_TOKEN_DEV=a1b2c3d4e5f6g7h8i9j0...

# Marketing team credentials
TRELLO_KEY_MKT=k1l2m3n4o5p6q7r8s9t0...
TRELLO_TOKEN_MKT=k1l2m3n4o5p6q7r8s9t0...
JIRA_USER_MKT=marketing@company.com
JIRA_TOKEN_MKT=k1l2m3n4o5p6q7r8s9t0...

# Support team credentials
TRELLO_KEY_SUPPORT=u1v2w3x4y5z6a7b8c9d0...
TRELLO_TOKEN_SUPPORT=u1v2w3x4y5z6a7b8c9d0...
JIRA_USER_SUPPORT=support@company.com
JIRA_TOKEN_SUPPORT=u1v2w3x4y5z6a7b8c9d0...
```

### GitHub Actions

Set up GitHub Secrets with the same names:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add each environment variable as a secret:
   - TRELLO_KEY_DEV
   - TRELLO_TOKEN_DEV
   - JIRA_USER_DEV
   - JIRA_TOKEN_DEV
   - (and so on for all teams)

## How Environment Variables Are Used

1. Inside `src/core/trello_client.py`, credentials are loaded:
   ```python
   self.api_key = config(api_key_env)  # Uses python-decouple
   self.token = config(token_env)
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
     TRELLO_KEY: ${{ secrets[matrix.connection.trello.api_key] }}
     TRELLO_TOKEN: ${{ secrets[matrix.connection.trello.token] }}
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

### Jira

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Create an API token and copy it
3. Use your email address as the username
