import argparse
import asyncio
import yaml
from core.sync_engine import run_sync


def main():
    parser = argparse.ArgumentParser(description='Run Trello-Jira sync for a connection')
    parser.add_argument('--config', default='config/mappings.yaml', help='Path to mappings YAML')
    parser.add_argument('--connection-index', type=int, required=True, help='Index of connection to run')
    parser.add_argument('--last-sync', default=None, help='Timestamp of last sync')
    args = parser.parse_args()

    data = yaml.safe_load(open(args.config))
    connections = data.get('connections', [])
    if args.connection_index < 0 or args.connection_index >= len(connections):
        raise IndexError('connection-index out of range')
    connection = connections[args.connection_index]
    last_sync = args.last_sync or '1970-01-01T00:00:00Z'

    asyncio.run(run_sync(connection, last_sync))


if __name__ == '__main__':
    main()
