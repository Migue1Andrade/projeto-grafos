# Projeto Grafos - Parte 1

Este projeto processa dados de bairros do Recife, constrói grafos de adjacências e gera endereços fictícios.

## Estrutura
- `data/bairros_recife.csv`: matriz de bairros fornecida
- `data/adjacencias_bairros.csv`: gerado automaticamente
- `data/enderecos.csv`: gerado automaticamente
- `src/graphs/`: código para grafos e algoritmos
- `src/cli.py`: interface de linha de comando
- `tests/`: testes unitários

## Como usar
1. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Gere adjacências e endereços:
   ```bash
   python src/cli.py --construir
   ```
3. Rode os testes:
   ```bash
   pytest
   ```

## Algoritmos implementados
- BFS
- DFS
- Dijkstra
- Bellman-Ford

## Observações
- O arquivo `adjacencias_bairros.csv` é gerado a partir da matriz de bairros, considerando vizinhos horizontais e verticais.
- O arquivo `enderecos.csv` contém endereços fictícios para cada bairro.