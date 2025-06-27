# 🕷️ Guia Completo de Monitoramento do Web Scraping - JusCash DJE

## 🎯 Como Analisar se o Web Scraping está Funcionando Corretamente

### 📊 **1. Flower - Monitor Principal para Scraping**

**URL**: https://flower.juscash.app  
**Login**: admin / juscash2024

**O que verificar no Flower:**

#### 🔍 **Aba "Tasks"**
- Procure por tarefas com nomes:
  - `extract_publicacoes_task`
  - `extract_daily_publicacoes`
  - `extract_full_period_publicacoes`
  - `extract_custom_period_publicacoes`

#### 📈 **Estados das Tarefas de Scraping**
- **SUCCESS** ✅: Scraping concluído com sucesso
- **PROGRESS** 🔄: Scraping em execução
- **FAILURE** ❌: Erro no scraping
- **PENDING** ⏳: Aguardando execução

#### 🕐 **Tempo de Execução**
- Scraping normal: 2-10 minutos
- Scraping de período longo: 10-60 minutos
- Se passar de 60 minutos: possível problema

### 📋 **2. Logs Detalhados do Scraping**

```bash
# Logs específicos do worker (onde roda o scraping)
ssh root@77.37.68.178 "cd /var/www/juscash && docker logs juscash_worker_prod --tail 100 | grep -i 'scraping\|publicacao\|extract\|selenium\|chrome'"

# Logs em tempo real
ssh root@77.37.68.178 "cd /var/www/juscash && docker logs juscash_worker_prod -f | grep -E '(scraping|publicacao|extract|selenium|chrome|DJE)'"

# Filtrar apenas sucessos
ssh root@77.37.68.178 "cd /var/www/juscash && docker logs juscash_worker_prod --tail 50 | grep -i 'concluída\|success\|extraídas'"

# Filtrar apenas erros
ssh root@77.37.68.178 "cd /var/www/juscash && docker logs juscash_worker_prod --tail 50 | grep -i 'error\|erro\|failed\|falha'"
```

**Logs de Sucesso Esperados:**
```
✅ Driver inicializado com webdriver-manager
Iniciando extração de 01/12/2024 a 01/12/2024
Processando página de resultados 1...
Raspagem diária concluída: 5 publicações extraídas do dia 2024-12-01
✅ Driver do Selenium finalizado com sucesso
```

**Logs de Erro a Investigar:**
```
❌ Falha crítica ao inicializar Chrome após 3 tentativas
Driver não está operacional. Abortando extração.
Erro fatal durante a extração: ...
connection to server at "db" failed
```

### 🧪 **3. Testes Manuais via API**

#### **Teste Rápido de Scraping**
```bash
# Testar scraping de 1 dia (ontem)
curl -X POST 'https://cron.juscash.app/api/scraping/extract' \
  -H 'Content-Type: application/json' \
  -d '{
    "data_inicio": "2024-12-25T00:00:00",
    "data_fim": "2024-12-25T23:59:59"
  }'
```

**Resposta de Sucesso:**
```json
{
  "task_id": "a6102a28-85b0-4e22-9fdd-f00da25918d3",
  "status": "Em processamento (async)",
  "message": "Extração de publicações iniciada em background via Celery"
}
```

#### **Verificar Status da Tarefa**
```bash
# Usar o task_id da resposta anterior
curl -X GET 'https://cron.juscash.app/api/cron/tasks/a6102a28-85b0-4e22-9fdd-f00da25918d3'
```

**Resposta de Sucesso:**
```json
{
  "state": "SUCCESS",
  "result": {
    "total_extraidas": 8,
    "data_inicio": "2024-12-25T00:00:00",
    "data_fim": "2024-12-25T23:59:59",
    "status": "concluido"
  }
}
```

### 📊 **4. Verificação do Banco de Dados**

#### **Contar Publicações Extraídas**
```bash
# Verificar quantas publicações foram salvas
curl -X GET 'https://cron.juscash.app/api/publicacoes/?limit=1000' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total de publicações: {len(data)}')
print('Últimas 5 publicações:')
for pub in data[:5]:
    print(f'- {pub[\"numero_processo\"]} - {pub[\"data_disponibilizacao\"]}')
"
```

#### **Verificar Publicações por Data**
```bash
# Publicações de hoje
curl -X GET 'https://cron.juscash.app/api/publicacoes/?search=2024-12-26'

# Publicações recentes
curl -X GET 'https://cron.juscash.app/api/publicacoes/?limit=10'
```

### 🔍 **5. Análise de Qualidade dos Dados**

#### **Script Python para Análise Detalhada**
```python
import requests
import json
from datetime import datetime, timedelta

API_BASE = "https://cron.juscash.app/api"

def analisar_qualidade_scraping():
    """Analisa a qualidade dos dados extraídos"""
    
    # Buscar publicações recentes
    response = requests.get(f"{API_BASE}/publicacoes/?limit=100")
    publicacoes = response.json()
    
    print(f"📊 ANÁLISE DE QUALIDADE DO SCRAPING")
    print(f"=" * 50)
    print(f"Total de publicações: {len(publicacoes)}")
    
    if not publicacoes:
        print("❌ Nenhuma publicação encontrada!")
        return
    
    # Análise de campos obrigatórios
    campos_vazios = {
        'numero_processo': 0,
        'autores': 0,
        'advogados': 0,
        'conteudo_completo': 0
    }
    
    publicacoes_com_valores = 0
    datas_extraidas = set()
    
    for pub in publicacoes:
        # Verificar campos vazios
        for campo in campos_vazios:
            if not pub.get(campo) or pub[campo].strip() == '':
                campos_vazios[campo] += 1
        
        # Contar publicações com valores monetários
        if any([
            pub.get('valor_principal_bruto'),
            pub.get('valor_principal_liquido'),
            pub.get('valor_juros_moratorios'),
            pub.get('honorarios_advocaticios')
        ]):
            publicacoes_com_valores += 1
        
        # Coletar datas
        if pub.get('data_disponibilizacao'):
            data = pub['data_disponibilizacao'][:10]  # YYYY-MM-DD
            datas_extraidas.add(data)
    
    print(f"\n🔍 QUALIDADE DOS DADOS:")
    print(f"Publicações com valores monetários: {publicacoes_com_valores} ({publicacoes_com_valores/len(publicacoes)*100:.1f}%)")
    print(f"Datas diferentes encontradas: {len(datas_extraidas)}")
    print(f"Período coberto: {min(datas_extraidas) if datas_extraidas else 'N/A'} a {max(datas_extraidas) if datas_extraidas else 'N/A'}")
    
    print(f"\n❌ CAMPOS VAZIOS:")
    for campo, count in campos_vazios.items():
        porcentagem = count/len(publicacoes)*100
        status = "✅" if porcentagem < 10 else "⚠️" if porcentagem < 50 else "❌"
        print(f"{status} {campo}: {count} vazios ({porcentagem:.1f}%)")
    
    # Últimas extrações
    print(f"\n📅 ÚLTIMAS EXTRAÇÕES:")
    for data in sorted(datas_extraidas, reverse=True)[:5]:
        count = sum(1 for pub in publicacoes if pub.get('data_disponibilizacao', '').startswith(data))
        print(f"- {data}: {count} publicações")

# Executar análise
analisar_qualidade_scraping()
```

### 🚨 **6. Indicadores de Problemas no Scraping**

#### **Problemas Críticos:**
- ❌ **0 publicações extraídas**: Scraper não conseguiu acessar o site
- ❌ **Timeout constante**: Problemas de conectividade ou site lento
- ❌ **Erro de Chrome/Selenium**: Driver não inicializa
- ❌ **Erro de banco**: Não consegue salvar os dados

#### **Problemas de Qualidade:**
- ⚠️ **Muitos campos vazios**: Parsing dos dados falhou
- ⚠️ **Números de processo inválidos**: Regex não funcionou
- ⚠️ **Datas inconsistentes**: Problema na extração de datas
- ⚠️ **Conteúdo duplicado**: Lógica de deduplicação falhou

#### **Sinais de Sucesso:**
- ✅ **Publicações extraídas > 0**: Scraping funcionando
- ✅ **Campos preenchidos > 80%**: Parsing funcionando bem
- ✅ **Valores monetários extraídos**: Regex de valores funcionando
- ✅ **Tempo de execução consistente**: Performance estável

### 🛠️ **7. Comandos de Diagnóstico Específicos**

#### **Verificar Chrome/Selenium**
```bash
# Testar se Chrome está funcionando no container
ssh root@77.37.68.178 "cd /var/www/juscash && docker exec juscash_worker_prod google-chrome --version"

# Testar Selenium
ssh root@77.37.68.178 "cd /var/www/juscash && docker exec juscash_worker_prod python -c 'from selenium import webdriver; print(\"Selenium OK\")'"
```

#### **Testar Conectividade com DJE**
```bash
# Testar acesso ao site do DJE
ssh root@77.37.68.178 "cd /var/www/juscash && docker exec juscash_worker_prod curl -I https://dje.tjsp.jus.br/cdje/index.do"
```

#### **Verificar Recursos do Container**
```bash
# Memória e CPU do worker
ssh root@77.37.68.178 "cd /var/www/juscash && docker stats juscash_worker_prod --no-stream"
```

### 📈 **8. Métricas de Performance**

#### **Benchmarks Esperados:**
- **Velocidade**: 10-50 publicações por minuto
- **Uso de memória**: 200-800 MB durante scraping
- **Uso de CPU**: 20-60% durante scraping
- **Taxa de sucesso**: > 95% das execuções

#### **Script de Monitoramento Contínuo**
```python
import requests
import time
from datetime import datetime

def monitorar_scraping_continuo():
    """Monitora o scraping continuamente"""
    
    while True:
        try:
            # Executar scraping de teste (1 dia)
            ontem = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            response = requests.post('https://cron.juscash.app/api/scraping/extract', json={
                'data_inicio': f'{ontem}T00:00:00',
                'data_fim': f'{ontem}T23:59:59'
            })
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get('task_id')
                
                print(f"🚀 [{datetime.now()}] Scraping iniciado: {task_id}")
                
                # Aguardar conclusão
                while True:
                    status_response = requests.get(f'https://cron.juscash.app/api/cron/tasks/{task_id}')
                    status_data = status_response.json()
                    
                    if status_data['state'] == 'SUCCESS':
                        result = status_data.get('result', {})
                        total = result.get('total_extraidas', 0)
                        print(f"✅ [{datetime.now()}] Sucesso: {total} publicações extraídas")
                        break
                    elif status_data['state'] == 'FAILURE':
                        print(f"❌ [{datetime.now()}] Falha no scraping")
                        break
                    
                    time.sleep(30)
            else:
                print(f"❌ [{datetime.now()}] Erro na API: {response.status_code}")
                
        except Exception as e:
            print(f"❌ [{datetime.now()}] Erro: {e}")
        
        # Aguardar 1 hora antes do próximo teste
        time.sleep(3600)

# Para executar monitoramento contínuo
# monitorar_scraping_continuo()
```

### 🎯 **9. Checklist de Verificação Rápida**

#### **✅ Verificação Diária (2 minutos)**
1. Acessar Flower: https://flower.juscash.app
2. Verificar se há tarefas `extract_` com status SUCCESS nas últimas 24h
3. Verificar logs: `docker logs juscash_worker_prod --tail 20`
4. Contar publicações: `curl https://cron.juscash.app/api/publicacoes/?limit=1 | wc -l`

#### **🔍 Verificação Semanal (10 minutos)**
1. Executar teste manual de scraping
2. Analisar qualidade dos dados com script Python
3. Verificar performance dos containers
4. Revisar logs de erro da semana

#### **🛠️ Verificação Mensal (30 minutos)**
1. Análise completa de qualidade dos dados
2. Otimização de performance se necessário
3. Atualização de dependências (Chrome, Selenium)
4. Backup e análise de tendências

### 🚨 **10. Troubleshooting Comum**

#### **Problema: Chrome não inicializa**
```bash
# Solução 1: Restart do worker
ssh root@77.37.68.178 "cd /var/www/juscash && docker-compose -f docker-compose.prod.yml restart worker"

# Solução 2: Rebuild do container
ssh root@77.37.68.178 "cd /var/www/juscash && docker-compose -f docker-compose.prod.yml up --build worker -d"
```

#### **Problema: Site DJE mudou layout**
```bash
# Verificar se o site está acessível
curl -I https://dje.tjsp.jus.br/cdje/index.do

# Logs específicos de parsing
ssh root@77.37.68.178 "cd /var/www/juscash && docker logs juscash_worker_prod | grep -i 'parsing\|element\|selector'"
```

#### **Problema: Muitos dados vazios**
1. Verificar logs de parsing
2. Testar regex patterns manualmente
3. Verificar se estrutura HTML mudou
4. Atualizar seletores se necessário

#### **Problema: Performance lenta**
```bash
# Verificar recursos
ssh root@77.37.68.178 "cd /var/www/juscash && docker stats --no-stream"

# Otimizar Chrome options se necessário
# Reduzir período de scraping
# Adicionar delays entre requisições
```

---

## 📊 **Resumo Executivo**

### **🎯 Para verificar rapidamente se o scraping está funcionando:**

1. **🌸 Flower**: https://flower.juscash.app → Verificar tarefas SUCCESS
2. **📋 Logs**: `docker logs juscash_worker_prod --tail 20 | grep extract`
3. **🧪 Teste**: POST para `/api/scraping/extract` com data de ontem
4. **📊 Dados**: GET `/api/publicacoes/` para ver publicações recentes

### **✅ Indicadores de Saúde:**
- Tarefas SUCCESS no Flower nas últimas 24h
- Logs sem erros críticos
- Publicações novas sendo salvas
- Tempo de execução < 30 minutos por dia

### **🚨 Alertas Críticos:**
- 0 publicações extraídas por > 2 dias
- Erros de Chrome/Selenium constantes
- Timeout em > 50% das execuções
- Campos vazios em > 80% dos dados