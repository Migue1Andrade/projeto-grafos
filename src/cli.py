import argparse
from src.solve import construir_adjacencias, construir_enderecos
from src.graphs.io import load_bairros_csv, melt_bairros

def main():
    parser = argparse.ArgumentParser(description="Processa grafos de bairros do Recife")
    parser.add_argument('--bairros', default='data/bairros_recife.csv', help='CSV de bairros')
    parser.add_argument('--adjacencias', default='data/adjacencias_bairros.csv', help='CSV de adjacências')
    parser.add_argument('--enderecos', default='data/enderecos.csv', help='CSV de endereços')
    parser.add_argument('--construir', action='store_true', help='Construir adjacências e endereços')
    args = parser.parse_args()

    if args.construir:
        headers, rows = load_bairros_csv(args.bairros)
        bairros = melt_bairros(headers, rows)
        graph = construir_adjacencias(args.bairros, args.adjacencias)
        enderecos = construir_enderecos(bairros, args.enderecos)
        print(f"Adjacências salvas em {args.adjacencias}")
        print(f"Endereços salvos em {args.enderecos}")
    else:
        print("Use --construir para gerar os arquivos de adjacências e endereços.")

if __name__ == "__main__":
    main()
