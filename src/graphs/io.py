import csv
import re
from typing import List, Tuple

def load_bairros_csv(filepath: str) -> Tuple[List[str], List[List[str]]]:
    """
    Carrega o CSV de bairros e retorna:
    - headers: lista com os títulos das colunas (ex.: ['1.1', '1.2', ...])
    - rows: matriz de bairros (cada linha é uma lista de strings)
    """
    with open(filepath, encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = [row for row in reader]
    return headers, rows


def melt_bairros(headers: List[str], rows: List[List[str]]) -> List[str]:
    """
    "Derrete" a matriz de bairros em uma lista única de nomes de bairros,
    sem repetições e sem células vazias.
    """
    bairros: List[str] = []
    vistos = set()

    for row in rows:
        for cell in row:
            if not cell:
                continue
            nome = cell.strip()
            if not nome:
                continue
            if nome not in vistos:
                vistos.add(nome)
                bairros.append(nome)

    return bairros


def save_csv(filepath: str, data: List[List[str]], header: List[str] = None):
    """
    Salva uma matriz de dados em CSV.
    """
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerows(data)


def validate_bairros(bairros: List[str]) -> bool:
    """
    Valida se há bairros duplicados ou vazios.
    Retorna True se:
      - não há duplicados
      - nenhum nome é vazio
    """
    return len(bairros) == len(set(bairros)) and all(bairros)

def load_adjacencias(filepath: str):
    """
    Lê o arquivo de adjacências mesmo que ele não esteja em CSV perfeito.
    Assume o formato geral:
        bairro_origem, bairro_destino, ... , peso

    - Primeiro campo  -> bairro origem
    - Segundo campo   -> bairro destino
    - Último número da linha -> peso
    - O que estiver no meio a gente junta como descrição (logradouro/observação).
    """
    adj = []
    with open(filepath, encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            # 1) Pegar o último número da linha (o peso)
            nums = re.findall(r'[-+]?\d*\.?\d+', line)
            if not nums:
                # linha sem número, ignora
                continue
            peso = float(nums[-1])

            # 2) Remover o peso do final da linha (para sobrar só os textos)
            #    Vamos remover a última ocorrência desse número
            peso_str = nums[-1]
            idx = line.rfind(peso_str)
            base = line[:idx].rstrip().rstrip(',')

            # 3) Agora separa pelos dois primeiros campos (origem, destino)
            parts = base.split(',')
            if len(parts) < 2:
                # linha malformada demais
                continue

            origem = parts[0].strip()
            destino = parts[1].strip()

            # 4) O resto a gente considera como "descrição"
            #    (logradouro + observação misturados mesmo, não faz mal pros algoritmos)
            descricao = ",".join(parts[2:]).strip() if len(parts) > 2 else ""

            logradouro = descricao  # por enquanto guardamos tudo aqui
            observacao = ""        # se quiser, depois dá pra refinar

            adj.append((origem, destino, logradouro, observacao, peso))

    return adj