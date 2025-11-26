import os
import json
import csv

from pyvis.network import Network
import matplotlib.pyplot as plt

from src.solve import construir_grafo
from src.graphs.io import load_adjacencias

MICRO_CORES = {
    "1": "#1E88E5",
    "2": "#43A047",
    "3": "#FB8C00",
    "4": "#8E24AA",
    "5": "#F4511E",
    "6": "#00897B",
}

CONFIG_ARVORE_PERCURSO = '''
{
    "interaction": {
        "hover": true,
        "zoomView": true,
        "dragView": true,
        "navigationButtons": true
    },
    "nodes": {
        "shape": "dot",
        "borderWidth": 1,
        "borderWidthSelected": 3,
        "shadow": true,
        "font": {
            "size": 18,
            "face": "arial"
        }
    },
    "edges": {
        "smooth": {
            "type": "continuous",
            "roundness": 0.6
        }
    },
    "physics": {
        "enabled": true,
        "barnesHut": {
            "gravitationalConstant": -8000,
            "springLength": 180,
            "springConstant": 0.02,
            "damping": 0.09
        }
    }
}
'''

CONFIG_GRAFO_INTERATIVO = '''
{
  "interaction": {
    "hover": true,
    "zoomView": true,
    "dragView": true,
    "navigationButtons": true
  },
  "nodes": {
    "shape": "dot",
    "borderWidth": 1,
    "borderWidthSelected": 3,
    "shadow": true,
    "font": {
      "size": 16,
      "face": "arial"
    }
  },
  "edges": {
    "color": {
      "inherit": false
    },
    "smooth": {
      "type": "continuous",
      "roundness": 0.4
    }
  },
  "physics": {
    "enabled": true,
    "barnesHut": {
      "gravitationalConstant": -12000,
      "springLength": 160,
      "springConstant": 0.04,
      "damping": 0.09
    }
  }
}
'''

CONFIG_SUB_GRAFO_TOP10= '''
{
  "interaction": {
    "hover": true,
    "zoomView": true,
    "dragView": true,
    "navigationButtons": true
  },
  "nodes": {
    "shape": "dot",
    "shadow": true,
    "font": {
      "size": 18,
      "face": "arial"
    }
  },
  "edges": {
    "smooth": {
      "type": "continuous",
      "roundness": 0.4
    }
  },
  "physics": {
    "enabled": true
  }
}
'''

def carregar_caminho(percurso: str):
    with open(percurso, encoding="utf-8") as f:
        data = json.load(f)

    caminho = data.get("caminho", [])

    return caminho

def carregar_ego(ego_csv_path: str):
    dado = {}

    if not os.path.exists(ego_csv_path):
        return dado

    with open(ego_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for linha in reader:
            bairro = linha["bairro"]
            dado[bairro] = {
                "grau": float(linha["grau"]),
                "ordem_ego": float(linha["ordem_ego"]),
                "tamanho_ego": float(linha["tamanho_ego"]),
                "densidade_ego": float(linha["densidade_ego"]),
            }

    return dado

def carregar_microrregioes(bairros_unique_path: str):
    mapeamento = {}

    if not os.path.exists(bairros_unique_path):

        return mapeamento

    with open(bairros_unique_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for linha in reader:
            mapeamento[linha["bairro"]] = linha["microrregiao"]

    return mapeamento

def carregar_ranking(path: str):
    if not os.path.exists(path):
        return {}

    with open(path, encoding="utf-8") as f:
        return json.load(f)

def gerar_arvore_percurso_html(percurso_json_path: str = "out/percurso_nova_descoberta_setubal.json", html_path: str = "out/arvore_percurso.html"):
    if not os.path.exists(percurso_json_path):
        raise FileNotFoundError(
            f"Arquivo de percurso não encontrado: {percurso_json_path}"
        )

    caminho = carregar_caminho(percurso_json_path)

    if not caminho:
        raise ValueError("Caminho vazio no JSON de percurso.")

    net = Network(
        height="700px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#222222",
        directed=False,
    )

    net.barnes_hut()

    origem = caminho[0]
    destino = caminho[-1]

    for bairro in caminho:
        if bairro == origem:
            color = "#43A047"
            size = 26
        elif bairro == destino:
            color = "#F4511E"
            size = 26
        else:
            color = "#1E88E5"
            size = 18

        net.add_node(
            bairro,
            label=bairro,
            color=color,
            size=size,
            title=bairro,
        )

    for i in range(len(caminho) - 1):
        atual = caminho[i]
        prox = caminho[i + 1]
        net.add_edge(
            atual,
            prox,
            color="#EF6C00",
            width=4,
            smooth={"type": "continuous", "roundness": 0.5},
        )

    net.set_options(CONFIG_ARVORE_PERCURSO)

    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    net.write_html(html_path)
    print(html_path)

def gerar_grafo_interativo_html(
    filepath_adjacencias: str = "data/adjacencias_bairros.csv",
    bairros_unique_path: str = "data/bairros_unique.csv",
    ego_csv_path: str = "out/ego_bairro.csv",
    ranking_path: str = "out/ranking_bairros.json",
    percurso_json_path: str = "out/percurso_nova_descoberta_setubal.json",
    html_path: str = "out/grafo_interativo.html",
):
    grafo = construir_grafo(filepath_adjacencias)
    ego = carregar_ego(ego_csv_path)
    micro_map = carregar_microrregioes(bairros_unique_path)
    ranking = carregar_ranking(ranking_path)
    maior_grau = ranking.get("maior_grau", {})
    maior_denso = ranking.get("maior_densidade_ego", {})
    bairro_top_grau = maior_grau.get("bairro")
    bairro_top_denso = maior_denso.get("bairro")
    caminho_destacado = []

    if os.path.exists(percurso_json_path):
        caminho_destacado = carregar_caminho(percurso_json_path)

    arestas_caminho = set()

    if caminho_destacado:
        for i in range(len(caminho_destacado) - 1):
            u = caminho_destacado[i]
            v = caminho_destacado[i + 1]
            arestas_caminho.add((u, v))
            arestas_caminho.add((v, u))

    net = Network(
        height="800px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#222222",
        directed=False,
    )

    net.barnes_hut()

    for bairro in grafo.nodes():
        info_ego = ego.get(bairro, {})
        grau = info_ego.get("grau", float(len(grafo.neighbors(bairro))))
        dens_ego = info_ego.get("densidade_ego", 0.0)
        microrregiao = micro_map.get(bairro, "?")

        size = 8 + min(max(grau, 1), 12) * 1.3
        color = MICRO_CORES.get(str(microrregiao), "#90A4AE")
        border_width = 1

        if bairro == bairro_top_grau or bairro == bairro_top_denso:
            border_width = 3
            size += 4
            color = "#FDD835"

        title = (
            f"<b>{bairro}</b><br>"
            f"Microrregião: {microrregiao}<br>"
            f"Grau: {grau:.0f}<br>"
            f"Densidade ego: {dens_ego:.3f}"
        )

        net.add_node(
            bairro,
            label=bairro,
            title=title,
            color=color,
            size=size,
            borderWidth=border_width,
        )

    for origem, destino, peso in grafo.edges():
        flag_percurso = 1 if (origem, destino) in arestas_caminho else 0
        color = "#CFD8DC"
        width = 1

        net.add_edge(
            origem,
            destino,
            color=color,
            width=width,
            title=f"peso: {peso}",
            percurso=flag_percurso,
        )

    net.set_options(CONFIG_GRAFO_INTERATIVO)

    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    net.write_html(html_path)

    with open(html_path, encoding="utf-8") as f:
        html = f.read()

        extra_html = '''
                <div style="
                    position: fixed;
                    top: 10px;
                    left: 10px;
                    z-index: 9999;
                    background: #ffffff;
                    padding: 10px;
                    border-radius: 8px;
                    box-shadow: 0 0 6px rgba(0,0,0,0.3);
                    font-family: Arial, sans-serif;
                    max-width: 320px;
                ">
                <div style="margin-bottom: 6px;">
                    <label for="busca-bairro" style="font-weight:bold; font-size:13px;">
                    Buscar bairro:
                    </label><br>
                    <input id="busca-bairro"
                        type="text"
                        list="lista-bairros"
                        placeholder="Digite o nome"
                        style="width: 100%; padding: 4px; font-size: 13px;">
                </div>

                <button id="btn-buscar-bairro" type="button"
                        style="width: 100%; margin-bottom: 8px;
                                padding: 6px 8px; font-size: 13px;
                                border-radius: 6px; border: none;
                                background:#455A64; color:white; cursor:pointer;">
                    Buscar bairro
                </button>

                <hr style="margin: 6px 0;">

                <div style="margin-bottom: 6px;">
                    <label for="origem-bairro" style="font-weight:bold; font-size:13px;">
                    Origem:
                    </label><br>
                    <input id="origem-bairro"
                        type="text"
                        list="lista-bairros"
                        placeholder="Ex: Nova Descoberta"
                        style="width: 100%; padding: 4px; font-size: 13px;">
                </div>

                <div style="margin-bottom: 8px;">
                    <label for="destino-bairro" style="font-weight:bold; font-size:13px;">
                    Destino:
                    </label><br>
                    <input id="destino-bairro"
                        type="text"
                        list="lista-bairros"
                        placeholder="Ex: Boa Viagem (Setúbal)"
                        style="width: 100%; padding: 4px; font-size: 13px;">
                </div>

                <button id="btn-tracar" type="button"
                        style="width: 100%; margin-bottom: 6px;
                                padding: 6px 8px; font-size: 13px;
                                border-radius: 6px; border: none;
                                background:#388E3C; color:white; cursor:pointer;">
                    Traçar caminho
                </button>

                <button id="btn-percurso-nd-bv" type="button"
                        style="width: 100%;
                                padding: 6px 8px; font-size: 13px;
                                border-radius: 6px; border: none;
                                background:#1976D2; color:white; cursor:pointer;">
                    Traçar caminho Nova Descoberta → Boa Viagem (Setúbal)
                </button>

                <!-- lista compartilhada de bairros (autocomplete) -->
                <datalist id="lista-bairros"></datalist>
                </div>

                <script type="text/javascript">
                // --- PREENCHE A DATALIST COM OS BAIRROS (labels dos nós) ---
                function popularDatalistBairros() {
                    var dl = document.getElementById('lista-bairros');
                    if (!dl) return;

                    dl.innerHTML = "";
                    var dataNodes = nodes.get();

                    dataNodes.forEach(function(n) {
                    if (n.label) {
                        var opt = document.createElement('option');
                        opt.value = n.label;
                        dl.appendChild(opt);
                    }
                    });
                }

                function selecionarBairroPorNome(nome) {
                    if (!nome) return;
                    var ids = [];
                    var dataNodes = nodes.get();

                    nome = nome.toLowerCase();

                    dataNodes.forEach(function(n) {
                    if (n.label && n.label.toLowerCase().includes(nome)) {
                        ids.push(n.id);
                    }
                    });

                    if (ids.length > 0) {
                    network.selectNodes(ids);
                    network.focus(ids[0], {
                        scale: 1.4,
                        animation: { duration: 800, easingFunction: 'easeInOutQuad' }
                    });
                    } else {
                    alert("Bairro não encontrado: " + nome);
                    }
                }

                var inputBusca = document.getElementById('busca-bairro');
                inputBusca.addEventListener('keyup', function(e) {
                    if (e.key === 'Enter') {
                    selecionarBairroPorNome(this.value);
                    }
                });

                document.getElementById('btn-buscar-bairro').addEventListener('click', function() {
                    selecionarBairroPorNome(inputBusca.value);
                });

                function encontrarNoPorNome(nome) {
                    if (!nome) return null;
                    nome = nome.toLowerCase();
                    var dataNodes = nodes.get();
                    for (var i = 0; i < dataNodes.length; i++) {
                    var n = dataNodes[i];
                    if (n.label && n.label.toLowerCase() === nome) {
                        return n.id;
                    }
                    }
                    return null;
                }

                function construirAdjacencia() {
                    var dataEdges = edges.get();
                    var adj = {};
                    dataEdges.forEach(function(e) {
                    if (!adj[e.from]) adj[e.from] = [];
                    if (!adj[e.to]) adj[e.to] = [];
                    adj[e.from].push(e.to);
                    adj[e.to].push(e.from);
                    });
                    return adj;
                }

                function calcularCaminhoMaisCurto(origemId, destinoId, adj) {
                    var fila = [origemId];
                    var visitado = {};
                    var pai = {};

                    visitado[origemId] = true;

                    while (fila.length > 0) {
                    var u = fila.shift();
                    if (u === destinoId) break;

                    var vizinhos = adj[u] || [];
                    for (var i = 0; i < vizinhos.length; i++) {
                        var v = vizinhos[i];
                        if (!visitado[v]) {
                        visitado[v] = true;
                        pai[v] = u;
                        fila.push(v);
                        }
                    }
                    }

                    if (!visitado[destinoId]) {
                    return null;
                    }

                    var caminho = [];
                    var atual = destinoId;
                    while (atual !== undefined) {
                    caminho.push(atual);
                    if (atual === origemId) break;
                    atual = pai[atual];
                    }
                    caminho.reverse();
                    return caminho;
                }

                var ultimasArestasDestacadas = [];

                function destacarCaminho(caminho) {
                    var dataEdges = edges.get();

                    if (ultimasArestasDestacadas.length > 0) {
                    dataEdges.forEach(function(e) {
                        if (ultimasArestasDestacadas.indexOf(e.id) !== -1) {
                        e.color = "#CFD8DC";
                        e.width = 1;
                        }
                    });
                    }

                    var novasArestas = [];

                    for (var i = 0; i < caminho.length - 1; i++) {
                    var u = caminho[i];
                    var v = caminho[i + 1];

                    dataEdges.forEach(function(e) {
                        if ((e.from === u && e.to === v) || (e.from === v && e.to === u)) {
                        e.color = "#E53935";
                        e.width = 3;
                        novasArestas.push(e.id);
                        }
                    });
                    }

                    ultimasArestasDestacadas = novasArestas;
                    edges.update(dataEdges);

                    network.fit({
                    nodes: caminho,
                    animation: { duration: 800, easingFunction: 'easeInOutQuad' }
                    });
                }

                function tratarTracarCaminho() {
                    var origemNome = document.getElementById('origem-bairro').value.trim();
                    var destinoNome = document.getElementById('destino-bairro').value.trim();

                    if (!origemNome || !destinoNome) {
                    alert("Preencha origem e destino.");
                    return;
                    }

                    var origemId = encontrarNoPorNome(origemNome);
                    var destinoId = encontrarNoPorNome(destinoNome);

                    if (!origemId) {
                    alert("Origem não encontrada: " + origemNome);
                    return;
                    }
                    if (!destinoId) {
                    alert("Destino não encontrado: " + destinoNome);
                    return;
                    }

                    var adj = construirAdjacencia();
                    var caminho = calcularCaminhoMaisCurto(origemId, destinoId, adj);

                    if (!caminho) {
                    alert("Não há caminho entre " + origemNome + " e " + destinoNome + ".");
                    return;
                    }

                    destacarCaminho(caminho);
                }

                document.getElementById('btn-tracar').addEventListener('click', tratarTracarCaminho);

                document.getElementById('btn-percurso-nd-bv').addEventListener('click', function() {
                    document.getElementById('origem-bairro').value = "Nova Descoberta";
                    document.getElementById('destino-bairro').value = "Boa Viagem";
                    tratarTracarCaminho();
                });

                popularDatalistBairros();
                </script>
                '''

    html = html.replace("</body>", extra_html + "\n</body>")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(html_path)

def gerar_subgrafo_top10_grau_html(
    filepath_adjacencias: str = "data/adjacencias_bairros.csv",
    graus_csv_path: str = "out/graus.csv",
    html_path: str = "out/subgrafo_top10_grau.html",
):
    if not os.path.exists(graus_csv_path):
        return

    grafo = construir_grafo(filepath_adjacencias)

    dados = []
    with open(graus_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for linha in reader:
            dados.append((linha["bairro"], int(linha["grau"])))
    dados.sort(key=lambda x: x[1], reverse=True)
    top10_bairros = {b for b, _ in dados[:10]}

    net = Network(height="700px", width="100%", bgcolor="#ffffff", font_color="#222222")

    net.barnes_hut()

    for bairro in grafo.nodes():
        if bairro in top10_bairros:
            net.add_node(
                bairro,
                label=bairro,
                color="#1E88E5",
                size=22,
                title=f"Top 10 por grau",
            )

    for prim_no, seg_no, peso in grafo.edges():
        if prim_no in top10_bairros and seg_no in top10_bairros:
            net.add_edge(prim_no, seg_no, color="#90CAF9", width=2, title=f"peso: {peso}")

    net.set_options(CONFIG_SUB_GRAFO_TOP10)

    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    net.write_html(html_path)
    print(html_path)

def plot_histograma_graus(
    graus_csv_path: str = "out/graus.csv",
    out_path: str = "out/histograma_graus.png",
):
    if not os.path.exists(graus_csv_path):
        return

    graus = []

    with open(graus_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for linha in reader:
            graus.append(int(linha["grau"]))

    plt.figure(figsize=(8, 5))
    plt.hist(graus, bins=10)
    plt.xlabel("Grau")
    plt.ylabel("Frequência")
    plt.title("Distribuição dos graus dos bairros")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def plot_top10_grau(
    graus_csv_path: str = "out/graus.csv",
    out_path: str = "out/top10_grau.png",
):
    if not os.path.exists(graus_csv_path):
        return

    dados = []

    with open(graus_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for linha in reader:
            dados.append((linha["bairro"], int(linha["grau"])))

    dados.sort(key=lambda x: x[1], reverse=True)
    top10 = dados[:10]

    labels = [x[0] for x in top10]
    valores = [x[1] for x in top10]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, valores)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Grau")
    plt.title("Top 10 bairros por grau")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def init_visualizacao():

    gerar_arvore_percurso_html()
    gerar_grafo_interativo_html()
    plot_histograma_graus()
    plot_top10_grau()
    gerar_subgrafo_top10_grau_html()
