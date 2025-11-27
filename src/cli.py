import argparse
from src.solve import init
from src.viz import init_visualizacao, gerar_index_html, gerar_visualizacao_parte2
from src.parte2_algoritmos import main as parte2_main  

def main():
    parser = argparse.ArgumentParser(description="Processa grafos de bairros do Recife")
    parser.add_argument('--construir', action='store_true', help='Construir adjacências e endereços')
    args = parser.parse_args()

    if args.construir:
        init()
        init_visualizacao()
        parte2_main()
        gerar_visualizacao_parte2()
        gerar_index_html()          
        print("O projeto foi inicializado com Sucesso")
    else:
        print("Use --construir para gerar os arquivos de adjacências e endereços.")

if __name__ == "__main__":
    main()
