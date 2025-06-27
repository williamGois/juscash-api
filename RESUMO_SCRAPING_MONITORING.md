# 📊 Como Analisar se o Web Scraping está Funcionando - RESUMO EXECUTIVO

## 🎯 **Status Atual - IMPLEMENTADO**

✅ **Chrome instalado** - Usamos Dockerfile.alternative com Google Chrome  
✅ **Selenium funcionando** - Dependências instaladas e configuradas  
✅ **Celery configurado** - Worker rodando com filas de scraping  
✅ **Flower funcionando** - Monitor principal em https://flower.juscash.app  
✅ **API endpoints** - `/api/scraping/extract` para executar scraping  
✅ **Scripts de análise** - Ferramentas automatizadas de verificação  

## 🚀 **Formas de Verificar se o Scraping está Funcionando**

### **1. 🌸 Flower - MÉTODO PRINCIPAL (Recomendado)**

**URL**: https://flower.juscash.app  
**Login**: admin / juscash2024

**O que verificar:**
- Aba "Tasks" → Procurar tarefas `extract_publicacoes_task`
- Status SUCCESS = Scraping funcionou ✅
- Status FAILURE = Problema no scraping ❌
- Tempo de execução normal: 2-30 minutos

### **2. 📋 Logs Docker - VERIFICAÇÃO TÉCNICA**

```bash
# SSH na VPS
ssh root@77.37.68.178

# Ver logs do worker (onde roda o scraping)
docker logs juscash_worker_prod --tail 50 | grep -i extract

# Logs de sucesso esperados:
# "✅ Driver inicializado com webdriver-manager"
# "Raspagem diária concluída: X publicações extraídas"
# "✅ Driver do Selenium finalizado com sucesso"
```

### **3. 🧪 Teste Manual via API**

```bash
# Executar scraping de teste
curl -X POST 'https://cron.juscash.app/api/scraping/extract' \
  -H 'Content-Type: application/json' \
  -d '{
    "data_inicio": "2024-12-25T00:00:00",
    "data_fim": "2024-12-25T23:59:59"
  }'

# Resposta esperada:
# {"task_id": "...", "status": "Em processamento (async)"}

# Verificar status da tarefa:
curl 'https://cron.juscash.app/api/cron/tasks/TASK_ID'
```

### **4. 📊 Verificar Dados Extraídos**

```bash
# Ver publicações no banco
curl 'https://cron.juscash.app/api/publicacoes/?limit=10'

# Se retornar dados = scraping já funcionou antes
# Se retornar vazio = scraping nunca funcionou ou problema
```

### **5. 🤖 Script Automatizado**

```bash
# Na máquina local (dentro do projeto)
./scripts/check-scraping.sh

# Faz análise completa automaticamente
```

## 📈 **Indicadores de Saúde do Scraping**

### **✅ FUNCIONANDO BEM:**
- Tarefas SUCCESS no Flower nas últimas 24h
- Logs sem erros críticos de Chrome/Selenium
- Publicações novas sendo salvas no banco
- Tempo de execução < 30 minutos por execução
- Campos preenchidos em > 80% das publicações

### **🚨 PROBLEMAS CRÍTICOS:**
- 0 publicações extraídas por > 2 dias
- Erros "Chrome not found" ou "Selenium failed"
- Timeout em > 50% das execuções
- Campos vazios em > 80% dos dados
- Container worker reiniciando constantemente

## 🛠️ **Solução de Problemas Comuns**

### **Problema: Chrome não encontrado**
```bash
# Verificar se está usando Dockerfile correto
grep "dockerfile:" docker-compose.prod.yml
# Deve mostrar: dockerfile: Dockerfile.alternative

# Se não, corrigir e fazer rebuild
docker-compose -f docker-compose.prod.yml up --build -d
```

### **Problema: Selenium falha**
```bash
# Testar Selenium no container
docker exec juscash_worker_prod python -c "from selenium import webdriver; print('OK')"

# Se falhar, verificar dependências
docker exec juscash_worker_prod google-chrome --version
```

### **Problema: Site DJE inacessível**
```bash
# Testar conectividade
docker exec juscash_worker_prod curl -I https://dje.tjsp.jus.br/cdje/index.do

# Deve retornar "200 OK"
```

### **Problema: Worker não processa tarefas**
```bash
# Restart do worker
docker-compose -f docker-compose.prod.yml restart worker

# Verificar logs
docker logs juscash_worker_prod --tail 20
```

## 📅 **Monitoramento Diário Recomendado**

### **⚡ Verificação Rápida (2 minutos)**
1. Acessar https://flower.juscash.app
2. Verificar se há tarefas SUCCESS nas últimas 24h
3. Se não houver, executar teste manual

### **🔍 Verificação Semanal (10 minutos)**
1. Executar `./scripts/check-scraping.sh`
2. Analisar qualidade dos dados extraídos
3. Verificar performance dos containers
4. Revisar logs de erro da semana

## 🎯 **URLs Importantes**

| Ferramenta | URL | Descrição |
|------------|-----|-----------|
| 🌸 **Flower** | https://flower.juscash.app | Monitor principal (admin:juscash2024) |
| 📊 **cAdvisor** | https://cadvisor.juscash.app | Métricas de containers |
| 🐳 **Portainer** | https://portainer.juscash.app | Gerenciamento Docker |
| 📚 **API Docs** | https://cron.juscash.app/docs/ | Documentação Swagger |

## 📋 **Checklist de Funcionamento**

- [ ] Container `juscash_worker_prod` está UP
- [ ] Chrome instalado: `google-chrome --version` funciona
- [ ] Selenium funciona: `from selenium import webdriver` sem erro
- [ ] Site DJE acessível: curl retorna 200 OK
- [ ] Flower mostra tarefas SUCCESS recentes
- [ ] Banco tem publicações recentes
- [ ] Logs sem erros críticos

## 🚀 **Próximos Passos**

1. **Configurar cron jobs** para execução automática diária
2. **Monitorar via Flower** diariamente
3. **Executar script de análise** semanalmente
4. **Otimizar performance** se necessário

---

## 📞 **Em Caso de Problemas**

1. **Verificar Flower primeiro**: https://flower.juscash.app
2. **Executar script de análise**: `./scripts/check-scraping.sh`
3. **Verificar logs**: `docker logs juscash_worker_prod`
4. **Testar manualmente**: API `/api/scraping/extract`
5. **Restart se necessário**: `docker-compose restart worker`

**Status atual**: ✅ Scraping configurado e funcionando com Chrome + Selenium 