# 📁 Scripts do Projeto JusCash

Esta pasta contém todos os scripts auxiliares organizados por categoria.

## 📋 Estrutura

```
scripts/
├── deploy/          # Scripts de deploy
├── setup/           # Scripts de configuração inicial
├── maintenance/     # Scripts de manutenção
└── debug/          # Scripts de debug e monitoramento
```

## 🚀 Scripts Principais

### Deploy
- `deploy.sh` - Deploy principal via CI/CD
- `rollback.sh` - Reverter para versão anterior

### Setup
- `setup-vps.sh` - Configuração inicial da VPS
- `setup-local.sh` - Configuração ambiente local

### Manutenção
- `backup.sh` - Backup do banco de dados
- `cleanup.sh` - Limpeza de arquivos temporários

### Debug
- `monitor.sh` - Monitorar aplicação
- `logs.sh` - Ver logs em tempo real 