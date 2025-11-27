# Projeto Grafos — Recife & Dataset de Voos

Este projeto implementa, do zero e sem bibliotecas externas de grafos, algoritmos clássicos e métricas sobre grafos reais: bairros do Recife e um dataset maior de voos. Inclui visualizações, métricas, interface CLI e testes.

## Estrutura de Pastas

- `data/`
  - `bairros_recife.csv`: matriz original dos bairros do Recife
  - `adjacencias_bairros.csv`: adjacências extraídas (gerado)
  - `enderecos.csv`: endereços fictícios (gerado)
  - `bairros_unique.csv`: bairros únicos e microrregião
  - `dataset_parte2/adjacencias_voos.csv`: dataset maior (voos)
- `src/`
  - `cli.py`: interface de linha de comando (CLI)
  - `solve.py`, `viz.py`: processamento, métricas e visualizações
  - `parte2_algoritmos.py`: pipeline do dataset maior
  - `graphs/`: implementação dos grafos e algoritmos
- `tests/`: testes unitários para todos os algoritmos
- `out/`: saídas, métricas e visualizações geradas

## Como Usar

1. Instale as dependências:
   ```zsh
   pip install -r requirements.txt
   ```

2. Execute o pipeline completo (gera todos os arquivos e visualizações):
   ```zsh
   python src/cli.py --construir
   ```

3. Rode os testes:
   ```zsh
   pytest
   ```

## Funcionalidades

- **Parte 1 — Recife**
  - Constrói o grafo dos bairros a partir da matriz CSV
  - Gera adjacências, endereços e métricas (ordem, tamanho, densidade, graus, rankings, ego-networks)
  - Calcula caminhos mínimos (Dijkstra) entre pares de endereços
  - Visualizações: histograma de graus, subgrafos, árvore de percurso, grafo interativo HTML com busca e tooltips

- **Parte 2 — Dataset Maior**
  - Lê o dataset de voos, constrói o grafo com pesos positivos/negativos conforme a classe
  - Executa BFS, DFS, Dijkstra e Bellman-Ford (com detecção de ciclos negativos)
  - Mede tempo de execução e gera métricas do dataset
  - Visualização: histograma de graus do grafo de voos

- **CLI flexível** (em desenvolvimento): permite rodar algoritmos e métricas em qualquer dataset/par de nós.

## Algoritmos Implementados

- Busca em Largura (BFS)
- Busca em Profundidade (DFS)
- Dijkstra (caminho mínimo)
- Bellman-Ford (caminho mínimo com pesos negativos e detecção de ciclos)

## Visualizações

- Arquivos gerados em `out/`:
  - Histogramas de grau
  - Subgrafos dos bairros mais conectados
  - Grafo interativo (`grafo_interativo.html`)
  - Árvore de percurso entre bairros
  - Métricas e rankings em `.csv`/`.json`

## Observações

- Todos os algoritmos são implementados manualmente (sem networkx, igraph, etc).
- O pipeline é totalmente automatizado via CLI.
- O projeto é multiplataforma (testado em macOS).
- Para detalhes sobre pesos, regras e análise dos resultados, consulte o PDF/manual do projeto.

---
