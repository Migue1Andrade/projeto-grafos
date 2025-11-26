import csv
import re
from typing import List, Tuple

def load_bairros_csv(filepath: str) -> Tuple[List[str], List[List[str]]]:
    with open(filepath, encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = [row for row in reader]
    return headers, rows


def melt_bairros(headers: List[str], rows: List[List[str]]) -> List[str]:
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
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerows(data)


def validate_bairros(bairros: List[str]) -> bool:
    return len(bairros) == len(set(bairros)) and all(bairros)

def load_adjacencias(filepath: str):
    adj = []
    with open(filepath, encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            nums = re.findall(r'[-+]?\d*\.?\d+', line)
            if not nums:

                continue
            peso = float(nums[-1])

            peso_str = nums[-1]
            idx = line.rfind(peso_str)
            base = line[:idx].rstrip().rstrip(',')

            parts = base.split(',')
            if len(parts) < 2:
                continue

            origem = parts[0].strip()
            destino = parts[1].strip()
            descricao = ",".join(parts[2:]).strip() if len(parts) > 2 else ""
            logradouro = descricao
            observacao = ""

            adj.append((origem, destino, logradouro, observacao, peso))

    return adj