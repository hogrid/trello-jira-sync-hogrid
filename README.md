# Trello-Jira Sync

A scalable bidirectional synchronization solution between multiple Trello boards and Jira projects, designed to run via GitHub Actions.

## Features

- **Multiple Boards**: Synchronize various Trello boards with different Jira projects simultaneously
- **Flexible Configuration**: Define which fields to sync for each connection
- **Customizable Intervals**: Configure different synchronization intervals per connection
- **Bidirectional Sync**: Changes on both platforms are propagated
- **Advanced Mappings**:
  - Trello checklists → Jira subtasks
  - User mentions converted between platforms
  - Attachments (links)
  - Due dates and labels

## Architecture

```
trello-jira-sync/
├── src/
│   ├── core/
│   │   ├── trello_client.py  # Async client for Trello API
│   │   ├── jira_client.py    # Async client for Jira API
│   │   └── sync_engine.py    # Bidirectional sync engine
│   ├── workers/
│   │   └── connection_worker.py # CLI worker to run a connection
├── config/
│   ├── mappings.yaml  # Board/project and field configuration
│   └── .env.template  # Credentials template
├── docker/
│   └── Dockerfile     # Container for deployment
├── .github/
│   ├── workflows/
│   │   └── sync.yml   # Workflow with matrix for multiple connections
└── docs/
    └── SETUP.md       # Detailed configuration instructions
```

## Quick Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/emernuness/trello-jira-sync.git
   cd trello-jira-sync
   ```

2. Copy the environment variables template:
   ```bash
   cp config/.env.template .env
   ```

3. Configure your connections in `config/mappings.yaml`:
   ```yaml
   connections:
     - trello:
        board_id: ${{ secrets.TRELLO_BOARD_DEV_ID }}
        api_key: ${{ secrets.TRELLO_API_KEY_DEV }}
        token: ${{ secrets.TRELLO_TOKEN_DEV }}
    jira:
        project_key: ${{ secrets.JIRA_KEY_DEV }}
        host: ${{ secrets.JIRA_HOST_DEV }}
        user: ${{ secrets.JIRA_USER_DEV }}       
        api_token: ${{ secrets.JIRA_TOKEN_DEV }} 
       sync:
         interval: "*/5 * * * *"
         fields:
           - title
           - description
           - checklists
   ```

4. Set credentials in `.env` or as GitHub secrets.

For detailed configuration of multiple board-project pairs, environment variables, and examples, see the [Detailed Configuration Guide](docs/DETAILED_CONFIG.md).

## Execution

### Locally
```bash
pip install -r requirements.txt
python src/workers/connection_worker.py --connection-index 0
```

### Via GitHub Actions
Configure secrets in your GitHub repository and use the included workflow.

### With Docker
```bash
docker build -t trello-jira-sync -f docker/Dockerfile .
docker run --env-file .env trello-jira-sync
```

## Monitoring and Logs

Detailed logs are generated during each execution, facilitating problem diagnosis and sync verification.

## Contributing

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add feature X"`)
4. Push to your branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

Developed by Emerson Nunes
<emerson@hogrid.com>
