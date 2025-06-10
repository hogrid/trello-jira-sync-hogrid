# Trello-Jira Sync

Uma solução escalável de sincronização bidirecional entre múltiplos boards do Trello e projetos do Jira, projetada para execução via GitHub Actions.

## Recursos

- **Múltiplos Boards**: Sincronize vários boards do Trello com diferentes projetos Jira simultaneamente
- **Configuração Flexível**: Defina quais campos sincronizar para cada conexão
- **Intervalos Personalizáveis**: Configure diferentes intervalos de sincronização por conexão
- **Sincronização Bidirecional**: Alterações em ambas as plataformas são propagadas
- **Mapeamentos Avançados**:
  - Checklists do Trello → Subtasks no Jira
  - Menções de usuários convertidas entre plataformas
  - Anexos (links)
  - Datas e etiquetas

## Arquitetura

```
trello-jira-sync/
├── src/
│   ├── core/
│   │   ├── trello_client.py  # Cliente assíncrono para API do Trello
│   │   ├── jira_client.py    # Cliente assíncrono para API do Jira
│   │   └── sync_engine.py    # Motor de sincronização bidirecional
│   ├── workers/
│   │   └── connection_worker.py # Worker CLI para rodar uma conexão
├── config/
│   ├── mappings.yaml  # Configuração de boards/projetos e campos
│   └── .env.template  # Template para credenciais
├── docker/
│   └── Dockerfile     # Container para deployment
├── .github/
│   ├── workflows/
│   │   └── sync.yml   # Workflow com matriz para múltiplas conexões
└── docs/
    └── SETUP.md       # Instruções detalhadas de configuração
```

## Configuração Rápida

1. Clone o repositório:
   ```bash
   git clone https://github.com/emersonnunes/trello-jira-sync.git
   cd trello-jira-sync
   ```

2. Copie o template de variáveis de ambiente:
   ```bash
   cp config/.env.template .env
   ```

3. Configure suas conexões em `config/mappings.yaml`:
   ```yaml
   connections:
     - trello:
         board_id: "seu-board-id-1"
         api_key: "TRELLO_KEY_1"
         token: "TRELLO_TOKEN_1"
       jira:
         project_key: "PROJ_1"
         host: "https://sua-empresa.atlassian.net"
         user: "JIRA_USER_1"
         api_token: "JIRA_TOKEN_1"
       sync:
         interval: "*/5 * * * *"
         fields:
           - title
           - description
           - checklists
   ```

4. Defina as credenciais no `.env` ou como secrets no GitHub.

## Execução

### Localmente
```bash
pip install -r requirements.txt
python src/workers/connection_worker.py --connection-index 0
```

### Via GitHub Actions
Configure secrets no repositório GitHub e use o workflow incluído.

### Com Docker
```bash
docker build -t trello-jira-sync -f docker/Dockerfile .
docker run --env-file .env trello-jira-sync
```

## Monitoramento e Logs

Os logs detalhados são gerados em cada execução, facilitando o diagnóstico de problemas e verificação de sincronizações.

## Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/sua-feature`)
3. Commit suas mudanças (`git commit -m "Adiciona recurso X"`)
4. Push para sua branch (`git push origin feature/sua-feature`)
5. Abra um Pull Request

---

Desenvolvido por Emerson Nunes
<emerson@hogrid.com>
