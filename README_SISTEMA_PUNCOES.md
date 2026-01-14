# Sistema de Análise de Punções Fabergé

## Visão Geral

Sistema automatizado de análise de marcas de joalheiro (punções/hallmarks) para peças Fabergé, implementado em Python e preparado para integração com automações N8N.

## Características Principais

### 1. Método Zolonitsky
Identifica padrões de pureza de metal segundo o sistema russo de zolotniki:
- **84 zolotniki** = 875/1000 prata
- **88 zolotniki** = 916/1000 prata (equivalente a sterling)
- **91 zolotniki** = 947/1000 prata (alto grau)
- **56 zolotniki** = 583/1000 ouro (14kt)
- **72 zolotniki** = 750/1000 ouro (18kt)

### 2. Marcas de Ensaiadores Russos
Sistema completo de identificação de marcas de ensaio:

#### Pré-1899
- **Âncoras cruzadas e cetro**: Marca de São Petersburgo antes de 1899
- Indica período Alexandre III e início de Nicolau II

#### Pós-1908
- **Kokoshnik**: Sistema moderno com cabeça feminina usando kokoshnik (chapéu tradicional russo)
- **Direção**: Identifica se a cabeça está voltada para esquerda ou direita
- **Monogramas de ensaiadores**: Como Y.L. (Yakov Lyapunov)

### 3. Marcas da Casa Fabergé
Identifica todas as variantes conhecidas:
- **К.ФАБЕРЖЕ** - Nome completo em cirílico
- **ФАБЕРЖЕ** - Sobrenome em cirílico
- **FABERGE** / **FABERGÉ** - Grafia latina
- **K.FABERGE** - Inicial e sobrenome
- **K** - Marca reduzida
- **КФ** - Monograma

### 4. Marcas Imperiais
- **Águia bicéfala** (bicéfalo imperial)
- Indica autorização da Corte Imperial
- Presente em peças com patronagem imperial

### 5. Workmasters (Mestres-de-Obra)
Identifica assinaturas de todos os principais workmasters:
- **M.P. / М.П.** - Mikhail Perkhin (1886-1903)
- **H.W.** - Henrik Wigström (1903-1917)
- **A.H. / АН** - August Holmström (até 1903)
- **E.K. / EK** - Erik Kollin (1870-1901)
- **I.P. / I.Р.** - Julius Alexander Rappoport (1883-1908)
- **O.P. / OP** - Oscar Pihl Senior (1887-1897)
- E outros

### 6. Detecção de Marcas Repetidas
- Identifica quando as punções aparecem múltiplas vezes na mesma peça
- Comum em peças Fabergé por questões de autenticidade

## Arquivos do Sistema

### 1. `faberge_hallmark_analyzer.py`
Módulo principal do sistema com todas as classes e funções de análise.

**Classes principais:**
- `MetalStandard`: Enum com padrões de metal Zolonitsky
- `AssayerMark`: Marca de ensaiador russo
- `ImperialMark`: Marca imperial
- `WorkmasterMark`: Marca de workmaster
- `FabergeMark`: Marca da Casa Fabergé
- `HallmarkAnalysisResult`: Resultado completo da análise
- `FabergeHallmarkAnalyzer`: Analisador principal

**Uso standalone:**
```bash
python3 faberge_hallmark_analyzer.py
```

### 2. `processar_puncoes_colecao.py`
Script para processar coleções completas de peças.

**Uso:**
```bash
python3 processar_puncoes_colecao.py
```

**Entrada:**
- Arquivo `ovos_extraidos.json` com dados da coleção

**Saída:**
- `analise_puncoes_colecao_completa.json` - Análise completa em JSON
- `analise_puncoes_resumo.json` - Resumo em JSON
- `RELATORIO_ANALISE_PUNCOES.md` - Relatório detalhado em Markdown

## Formato de Entrada

### JSON de Coleção
```json
[
  {
    "nome": "Coronation Egg",
    "ano": "1897",
    "workmaster": "Mikhail Perkhin",
    "marks": "Fabergé, M. P. in Cyrillic, 56, crossed anchors and scepter",
    "materials": "Gold, enamel, diamonds",
    "dimensions": "Height 127mm",
    "provenance": "Imperial collection..."
  }
]
```

## Formato de Saída

### JSON Completo
```json
{
  "piece_name": "Coronation Egg (1897)",
  "raw_marks_text": "Fabergé, M. P. in Cyrillic, 56, crossed anchors and scepter",
  "confidence_score": 0.9,
  "repeated_marks": false,
  "metal_standard": {
    "mark": "56",
    "purity": 0.583,
    "description": "583/1000 gold - 14kt"
  },
  "assayer_mark": {
    "type": "crossed_anchors_scepter",
    "period": "pre-1899",
    "direction": null,
    "assayer_monogram": null,
    "description": "Âncoras cruzadas e cetro - marca de São Petersburgo pré-1899"
  },
  "faberge_mark": {
    "variant": "FABERGE",
    "script": "Latin",
    "period": "1882-1917",
    "description": "Marca Fabergé (variante latina)"
  },
  "workmaster_mark": {
    "initials": "M.P.",
    "name": "Mikhail Perkhin",
    "period": "1886-1903",
    "workshop_location": "St. Petersburg"
  }
}
```

## Score de Confiança

O sistema calcula um score de confiança (0.0 a 1.0) baseado nas marcas identificadas:

- **Padrão de metal**: 0.2
- **Marca de ensaiador**: 0.2
- **Marca Fabergé**: 0.3
- **Marca de workmaster**: 0.2
- **Marca imperial**: 0.1

**Score máximo**: 1.0 (todas as marcas identificadas)

### Interpretação:
- **≥ 0.5**: Marcação completa e confiável
- **0.3 - 0.5**: Marcação parcial
- **< 0.3**: Marcação incompleta ou ausente

## Integração com N8N

### Workflow Básico

```
1. Trigger (Webhook/Schedule)
   ↓
2. Read File (ovos_extraidos.json)
   ↓
3. Execute Command (python3 processar_puncoes_colecao.py)
   ↓
4. Read JSON Output (analise_puncoes_colecao_completa.json)
   ↓
5. Process/Filter Results
   ↓
6. Output (Database/API/Email/etc.)
```

### Exemplo de Integração via API

```python
from faberge_hallmark_analyzer import FabergeHallmarkAnalyzer

# Criar analisador
analyzer = FabergeHallmarkAnalyzer()

# Analisar marcas individuais
result = analyzer.analyze_marks(
    marks_text="Fabergé, H.W., 72, kokoshnik",
    piece_name="Example Egg"
)

# Obter resultado em dicionário (pronto para JSON)
output = result.to_dict()

# Ou processar coleção
collection = [
    {"nome": "Egg 1", "marks": "..."},
    {"nome": "Egg 2", "marks": "..."}
]
results = analyzer.analyze_collection(collection)
```

### Endpoints N8N Sugeridos

1. **Análise Individual**
   - Input: `{"piece_name": "...", "marks": "..."}`
   - Output: JSON com análise completa

2. **Análise em Lote**
   - Input: Array de peças
   - Output: Array de resultados

3. **Estatísticas**
   - Input: Array de resultados
   - Output: Relatório resumido

## Estatísticas da Coleção Atual

Baseado na análise de 47 ovos imperiais:

- **Ovos com marca Fabergé**: 63.8%
- **Ovos com workmaster identificado**: 44.7%
- **Ovos com marca de ensaiador**: 57.4%
- **Score médio de confiança**: 0.51

### Distribuição de Workmasters
1. Mikhail Perkhin: 38.3% (18 ovos)
2. August Holmström: 4.3% (2 ovos)
3. Henrik Wigström: 2.1% (1 ovo)

### Distribuição de Padrões de Metal
1. 56 zolotniki (ouro 14kt): 36.2% (17 ovos)
2. 72 zolotniki (ouro 18kt): 14.9% (7 ovos)
3. 88 zolotniki (prata sterling): 2.1% (1 ovo)
4. 91 zolotniki (prata alto grau): 2.1% (1 ovo)

### Períodos de Marcação
- Pré-1899 (âncoras cruzadas): 25.5% (12 ovos)
- Pós-1908 (kokoshnik): 31.9% (15 ovos)
- Período não identificado: 42.6% (20 ovos)

## Casos de Uso

### 1. Catalogação de Coleções
Automatizar a análise de marcas em coleções completas de objetos Fabergé

### 2. Autenticação
Verificar presença e consistência de marcas esperadas

### 3. Datação
Determinar período de fabricação baseado no tipo de marca de ensaiador

### 4. Atribuição
Identificar workmaster responsável pela fabricação

### 5. Análise de Mercado
Gerar estatísticas sobre distribuição de características

## Requisitos

- Python 3.7+
- Bibliotecas padrão (json, re, dataclasses, enum)
- Nenhuma dependência externa

## Instalação

```bash
# Clonar repositório
git clone https://github.com/condevialbrunetto/catalogo-faberge.git

# Navegar para o diretório
cd catalogo-faberge

# Executar análise de exemplo
python3 faberge_hallmark_analyzer.py

# Processar coleção completa
python3 processar_puncoes_colecao.py
```

## Limitações Conhecidas

1. **Marcas ilegíveis ou danificadas**: Sistema depende de descrição textual das marcas
2. **Variações de nomenclatura**: Algumas variações podem não ser detectadas
3. **Marcas não documentadas**: Workmasters menos conhecidos podem não estar no banco de dados
4. **Contexto histórico**: Sistema não analisa contexto histórico ou proveniência

## Melhorias Futuras

1. **Reconhecimento de imagem**: Análise direta de fotos de marcas
2. **Machine Learning**: Classificação automática melhorada
3. **Base de dados expandida**: Mais workmasters e variações
4. **Integração com bases externas**: API para verificação cruzada
5. **Análise de autenticidade**: Score de probabilidade de falsificação

## Suporte e Contribuições

Para questões, sugestões ou contribuições, utilize o sistema de issues do GitHub.

## Referências

1. von Habsburg, Géza & Lopato, Marina. *Fabergé: Imperial Jeweller*. London, 1993.
2. Tillander-Godenhielm, Ulla. *The Russian Imperial Award System*. Helsinki, 2005.
3. McCanless, Christel Ludewig. *Fabergé and the Russian Master Goldsmiths*. New York, 2019.
4. Sistema de hallmarks russos: kokoshnik, âncoras cruzadas, zolotniki

## Licença

Este projeto faz parte do Catálogo Raisonné Fabergé.

---

**Versão**: 1.0  
**Data**: Janeiro 2026  
**Autor**: Sistema de Análise Fabergé
