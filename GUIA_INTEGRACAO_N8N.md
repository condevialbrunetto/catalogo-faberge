# Guia de Integração N8N - Sistema de Análise de Punções Fabergé

## Visão Geral

Este guia explica como integrar o Sistema de Análise de Punções Fabergé com automações N8N rodando em um VPS com EasyPanel.

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                         N8N Workflow                         │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Trigger   │→ │ Process Data │→ │ Python Analysis  │   │
│  │ (Webhook/  │  │   (JSON)     │  │   (faberge_     │   │
│  │  Schedule) │  │              │  │    analyzer)     │   │
│  └────────────┘  └──────────────┘  └──────────────────┘   │
│                                              ↓               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Output Processing & Storage                  │  │
│  │  - Database Insert                                    │  │
│  │  - API Webhook                                        │  │
│  │  - Email Report                                       │  │
│  │  - File Storage                                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Configuração Inicial

### 1. Preparação do Ambiente VPS

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3 (se necessário)
sudo apt install python3 python3-pip -y

# Verificar instalação
python3 --version

# Clonar repositório
cd /opt
git clone https://github.com/condevialbrunetto/catalogo-faberge.git
cd catalogo-faberge

# Testar scripts
python3 faberge_hallmark_analyzer.py
```

### 2. Configuração no EasyPanel

1. Acesse o painel EasyPanel
2. Configure a aplicação N8N
3. Adicione variáveis de ambiente:
   - `FABERGE_ANALYZER_PATH=/opt/catalogo-faberge`
   - `PYTHON_BIN=/usr/bin/python3`

## Workflows N8N

### Workflow 1: Análise Individual de Peça

**Propósito**: Analisar marcas de uma única peça Fabergé

```json
{
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "faberge-analyze",
        "method": "POST"
      }
    },
    {
      "name": "Prepare Data",
      "type": "n8n-nodes-base.set",
      "parameters": {
        "values": {
          "string": [
            {
              "name": "piece_name",
              "value": "={{$json[\"piece_name\"]}}"
            },
            {
              "name": "marks",
              "value": "={{$json[\"marks\"]}}"
            }
          ]
        }
      }
    },
    {
      "name": "Execute Python Analysis",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "python3 /opt/catalogo-faberge/analyze_single.py '{{$json[\"piece_name\"]}}' '{{$json[\"marks\"]}}'"
      }
    },
    {
      "name": "Parse JSON Result",
      "type": "n8n-nodes-base.set",
      "parameters": {
        "keepOnlySet": false,
        "values": {
          "string": [
            {
              "name": "result",
              "value": "={{JSON.parse($json[\"stdout\"])}}"
            }
          ]
        }
      }
    },
    {
      "name": "Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "parameters": {
        "options": {}
      }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Prepare Data"}]]
    },
    "Prepare Data": {
      "main": [[{"node": "Execute Python Analysis"}]]
    },
    "Execute Python Analysis": {
      "main": [[{"node": "Parse JSON Result"}]]
    },
    "Parse JSON Result": {
      "main": [[{"node": "Response"}]]
    }
  }
}
```

### Workflow 2: Análise em Lote de Coleção

**Propósito**: Processar coleção completa de peças

```json
{
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "hours",
              "hoursInterval": 24
            }
          ]
        }
      }
    },
    {
      "name": "Read Collection File",
      "type": "n8n-nodes-base.readBinaryFile",
      "parameters": {
        "filePath": "/opt/catalogo-faberge/ovos_extraidos.json"
      }
    },
    {
      "name": "Execute Batch Analysis",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "cd /opt/catalogo-faberge && python3 processar_puncoes_colecao.py"
      }
    },
    {
      "name": "Read Results",
      "type": "n8n-nodes-base.readBinaryFile",
      "parameters": {
        "filePath": "/opt/catalogo-faberge/analise_puncoes_colecao_completa.json"
      }
    },
    {
      "name": "Parse Results",
      "type": "n8n-nodes-base.set",
      "parameters": {
        "keepOnlySet": false,
        "values": {
          "string": [
            {
              "name": "analysis_results",
              "value": "={{JSON.parse($binary.data.toString())}}"
            }
          ]
        }
      }
    },
    {
      "name": "Store in Database",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO faberge_analysis ..."
      }
    }
  ]
}
```

## Scripts Helper para N8N

### Script 1: analyze_single.py

Criar arquivo `/opt/catalogo-faberge/analyze_single.py`:

```python
#!/usr/bin/env python3
"""
Script para análise individual - Integração N8N
"""
import sys
import json
from faberge_hallmark_analyzer import FabergeHallmarkAnalyzer

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    piece_name = sys.argv[1]
    marks = sys.argv[2]
    
    analyzer = FabergeHallmarkAnalyzer()
    result = analyzer.analyze_marks(marks, piece_name)
    
    # Output JSON para stdout (N8N captura)
    print(json.dumps(result.to_dict(), ensure_ascii=False))

if __name__ == "__main__":
    main()
```

Tornar executável:
```bash
chmod +x /opt/catalogo-faberge/analyze_single.py
```

### Script 2: analyze_api.py

API Flask para integração avançada:

```python
#!/usr/bin/env python3
"""
API REST para análise de punções Fabergé
"""
from flask import Flask, request, jsonify
from faberge_hallmark_analyzer import FabergeHallmarkAnalyzer

app = Flask(__name__)
analyzer = FabergeHallmarkAnalyzer()

@app.route('/api/analyze', methods=['POST'])
def analyze_single():
    """Analisa uma peça individual"""
    data = request.json
    piece_name = data.get('piece_name', 'Unknown')
    marks = data.get('marks', '')
    
    result = analyzer.analyze_marks(marks, piece_name)
    return jsonify(result.to_dict())

@app.route('/api/analyze/batch', methods=['POST'])
def analyze_batch():
    """Analisa múltiplas peças"""
    data = request.json
    collection = data.get('collection', [])
    
    results = analyzer.analyze_collection(collection)
    return jsonify({
        'total': len(results),
        'results': results
    })

@app.route('/api/statistics', methods=['POST'])
def get_statistics():
    """Retorna estatísticas da análise"""
    data = request.json
    results = data.get('results', [])
    
    summary = analyzer.generate_summary_report(results)
    return jsonify(summary)

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Instalar dependências:
```bash
pip3 install flask
```

Criar serviço systemd `/etc/systemd/system/faberge-api.service`:

```ini
[Unit]
Description=Faberge Analysis API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/catalogo-faberge
ExecStart=/usr/bin/python3 /opt/catalogo-faberge/analyze_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Ativar serviço:
```bash
sudo systemctl enable faberge-api
sudo systemctl start faberge-api
```

## Exemplos de Uso via Webhook

### Exemplo 1: Análise Individual

**Request:**
```bash
curl -X POST https://seu-n8n.com/webhook/faberge-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "piece_name": "Renaissance Egg",
    "marks": "Fabergé, M. P. in Cyrillic, 56, crossed anchors and scepter"
  }'
```

**Response:**
```json
{
  "piece_name": "Renaissance Egg",
  "confidence_score": 0.9,
  "metal_standard": {
    "mark": "56",
    "purity": 0.583,
    "description": "583/1000 gold - 14kt"
  },
  "assayer_mark": {
    "type": "crossed_anchors_scepter",
    "period": "pre-1899"
  },
  "faberge_mark": {
    "variant": "FABERGE",
    "script": "Latin"
  },
  "workmaster_mark": {
    "name": "Mikhail Perkhin",
    "initials": "M.P."
  }
}
```

### Exemplo 2: Via API Flask

**Request:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "piece_name": "Coronation Egg",
    "marks": "Fabergé, M. P. in Cyrillic, 56, kokoshnik"
  }'
```

## Workflow Avançado: Pipeline Completo

```
1. Webhook Trigger (Novo upload de imagem/dados)
   ↓
2. Extract Text from Image (OCR - se aplicável)
   ↓
3. Call Faberge Analysis API
   ↓
4. Validate Results (Score >= 0.5)
   ↓
   ├─→ High Confidence: Store in Database
   │                     Send to Expert System
   │                     Update Catalog
   │
   └─→ Low Confidence: Flag for Manual Review
                       Send Email to Curator
                       Store in Review Queue
```

## Monitoramento e Logs

### Log Analysis Results

```javascript
// N8N Function Node
const result = items[0].json.result;

// Log para console N8N
console.log(`Analyzed: ${result.piece_name}`);
console.log(`Confidence: ${result.confidence_score}`);

// Enviar para sistema de log
if (result.confidence_score < 0.3) {
  // Alertar baixa confiança
  return {
    alert: true,
    message: `Low confidence analysis: ${result.piece_name}`
  };
}

return items;
```

## Troubleshooting

### Erro: "Python script not found"
```bash
# Verificar caminho
ls -la /opt/catalogo-faberge/faberge_hallmark_analyzer.py

# Verificar permissões
chmod +x /opt/catalogo-faberge/*.py
```

### Erro: "Module not found"
```bash
# Verificar PYTHONPATH
export PYTHONPATH=/opt/catalogo-faberge:$PYTHONPATH

# Ou adicionar ao script
import sys
sys.path.insert(0, '/opt/catalogo-faberge')
```

### Erro: "JSON decode error"
```bash
# Testar script manualmente
cd /opt/catalogo-faberge
python3 analyze_single.py "Test Piece" "Fabergé, 56"

# Verificar output
python3 analyze_single.py "Test" "56" | jq .
```

## Performance e Otimização

### Cache de Resultados

```python
# Adicionar cache simples
import hashlib
import json
from pathlib import Path

CACHE_DIR = Path("/tmp/faberge_cache")
CACHE_DIR.mkdir(exist_ok=True)

def get_cache_key(marks_text):
    return hashlib.md5(marks_text.encode()).hexdigest()

def get_cached_result(marks_text):
    cache_file = CACHE_DIR / f"{get_cache_key(marks_text)}.json"
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return None

def cache_result(marks_text, result):
    cache_file = CACHE_DIR / f"{get_cache_key(marks_text)}.json"
    with open(cache_file, 'w') as f:
        json.dump(result, f)
```

### Processamento em Paralelo

Para grandes coleções, usar multiprocessing:

```python
from multiprocessing import Pool

def process_batch(items, num_workers=4):
    with Pool(num_workers) as pool:
        results = pool.map(analyze_item, items)
    return results
```

## Segurança

### Validação de Input

```javascript
// N8N Function Node - Validação
const input = items[0].json;

// Validar campos obrigatórios
if (!input.piece_name || !input.marks) {
  throw new Error('Missing required fields');
}

// Sanitizar input
input.piece_name = input.piece_name.substring(0, 200);
input.marks = input.marks.substring(0, 1000);

return items;
```

### Rate Limiting

Configurar no N8N ou API:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("100 per hour")
def analyze_single():
    # ...
```

## Próximos Passos

1. Implementar webhooks para notificações
2. Adicionar autenticação API
3. Criar dashboard de visualização
4. Integrar com banco de dados central
5. Adicionar suporte a OCR para análise de imagens

## Recursos Adicionais

- [Documentação N8N](https://docs.n8n.io)
- [EasyPanel Docs](https://easypanel.io/docs)
- [README Sistema](./README_SISTEMA_PUNCOES.md)

---

**Versão**: 1.0  
**Data**: Janeiro 2026
