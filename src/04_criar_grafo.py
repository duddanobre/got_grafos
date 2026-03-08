import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def criar_grafo():
    print("Criando grafo...")

    # carregar dataset
    df = pd.read_csv("datasets/interacoes.csv")

    # filtrar interações diretas (single)
    df_direct = df[df["tipo_interacao"] == "single"]

    # agrupar e contar interações
    df_grouped = df_direct.groupby(['falante', 'ouvinte']).size().reset_index(name='weight')

    # criar grafo eficientemente
    G = nx.from_pandas_edgelist(df_grouped, 'falante', 'ouvinte', 
                                 edge_attr='weight', create_using=nx.Graph())

    print("Número de nós:", G.number_of_nodes())
    print("Número de arestas:", G.number_of_edges())

    edges = sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)

    print("\nTop 10 interações:")
    for u, v, data in edges[:10]:
        print(f"  {u} <-> {v}: {data['weight']} interações")

    return G

def filtrar_grafo(G, peso_minimo=5):

    G_filtrado = nx.Graph()

    for u, v, data in G.edges(data=True):
        if data["weight"] >= peso_minimo:
            G_filtrado.add_edge(u, v, weight=data["weight"])

    return G_filtrado

def subgrafo_top_personagens(G, top_n=20):

    # usar peso total das interações ao invés de grau simples
    weighted_degree = {n: G.degree(n, weight='weight') for n in G.nodes()}

    top_nodes = sorted(weighted_degree, key=weighted_degree.get, reverse=True)[:top_n]

    return G.subgraph(top_nodes).copy()

def visualizar_grafo(G, mostrar_pesos=True, peso_minimo_label=50):

    plt.figure(figsize=(16,16))

    # layout reproduzível
    pos = nx.spring_layout(G, k=1.2, iterations=100, seed=42)
    
    # tamanho do nó proporcional ao peso total das interações
    node_size = [G.degree(n, weight='weight')*10 for n in G.nodes()]

    # cores por importância (peso total)
    node_colors = [G.degree(n, weight='weight') for n in G.nodes()]

    # desenhar nós
    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=node_size,
        node_color=node_colors,
        cmap=plt.cm.YlOrRd,
        alpha=0.9
    )

    # espessura das arestas proporcional ao peso
    widths = [G[u][v]['weight']/10 for u,v in G.edges()]

    # desenhar arestas
    nx.draw_networkx_edges(
        G,
        pos,
        width=widths,
        alpha=0.5,
        edge_color='gray'
    )

    # nomes dos personagens
    nx.draw_networkx_labels(
        G,
        pos,
        font_size=9,
        font_weight='bold'
    )

    # mostrar apenas pesos significativos
    if mostrar_pesos:
        edge_labels = {(u,v): w for u,v,w in G.edges(data='weight') if w >= peso_minimo_label}
        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=edge_labels,
            font_size=7
        )

    plt.title("Rede de Interações de Game of Thrones", fontsize=20, fontweight='bold')
    plt.axis("off")
    plt.tight_layout()
    plt.savefig('saidas/grafo_interacoes.png', dpi=300, bbox_inches='tight')
    print("[OK] Grafo salvo em: saidas/grafo_interacoes.png")
    plt.show()

def main():
    G = criar_grafo()
    
    print("\nCriando visualização dos top 20 personagens...")
    G_top = subgrafo_top_personagens(G, 20)
    
    print(f"Subgrafo: {G_top.number_of_nodes()} nós, {G_top.number_of_edges()} arestas")
    
    visualizar_grafo(G_top, mostrar_pesos=True, peso_minimo_label=30)


if __name__ == "__main__":
    main()