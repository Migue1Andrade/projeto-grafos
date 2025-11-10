import csv
from typing import Dict, List, Tuple

def load_bairros_csv(filepath: str) -> Tuple[List[str], List[List[str]]]:
    """
    Carrega o CSV de bairros e retorna os cabeçalhos e matriz de bairros.
    """
    with open(filepath, encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = [row for row in reader]
    return headers, rows

def melt_bairros(headers: List[str], rows: List[List[str]]) -> List[str]:
    """
    Derrete a matriz de bairros para uma lista única de nomes de bairros.
    """
    bairros = set()
    for row in rows:
        for bairro in row:
            if bairro and bairro.strip():
                bairros.add(bairro.strip())
    return sorted(bairros)

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
    """
    return len(bairros) == len(set(bairros)) and all(bairros)
