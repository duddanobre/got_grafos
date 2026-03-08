import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
try:
    import community as community_louvain
except ImportError:
    print("Instalando python-louvain...")
    import os
    os.system("pip install python-louvain")
    import community as community_louvain

def criar_grafo_completo():
    """Cria grafo completo com todos os personagens"""
    print("Carregando dados...")
    df = pd.read_csv("datasets/interacoes.csv")
    df_grouped = df.groupby(['falante', 'ouvinte']).size().reset_index(name='weight')
    G = nx.from_pandas_edgelist(df_grouped, 'falante', 'ouvinte', edge_attr='weight', create_using=nx.Graph())
    
    print(f"✅ Grafo completo: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas")
    return G

def detectar_comunidades(G):
    """Detecta comunidades usando algoritmo Louvain"""
    print("\nDetectando comunidades...")
    communities = community_louvain.best_partition(G, weight='weight', random_state=42)
    
    num_communities = len(set(communities.values()))
    print(f"✅ {num_communities} comunidades detectadas")
    
    from collections import Counter
    community_counts = Counter(communities.values())
    
    print("\n🏘️  Principais comunidades:")
    for comm_id, count in community_counts.most_common(10):
        membros = [p for p, c in communities.items() if c == comm_id]
        print(f"   Comunidade {comm_id + 1}: {count} membros")
        print(f"      Principais: {', '.join(membros[:5])}")
    
    return communities

def visualizar_grafo_comunidades(G, communities, peso_minimo_aresta=10):
    """Visualiza grafo completo com comunidades coloridas"""
    
    G_filtrado = nx.Graph()
    for u, v, data in G.edges(data=True):
        if data['weight'] >= peso_minimo_aresta:
            G_filtrado.add_edge(u, v, weight=data['weight'])
    
    print(f"\nGrafo filtrado (peso >= {peso_minimo_aresta}): {G_filtrado.number_of_nodes()} nós, {G_filtrado.number_of_edges()} arestas")
    
    fig, ax = plt.subplots(figsize=(40, 40), facecolor='white')
    
    print("Calculando layout...")
    pos = nx.spring_layout(G_filtrado, k=5, iterations=200, seed=42)
    
    # Cores distintas para comunidades (palette expandida)
    num_communities = len(set(communities.values()))
    if num_communities <= 20:
        colors = plt.cm.tab20(np.linspace(0, 1, 20))
    else:
        colors = plt.cm.hsv(np.linspace(0, 1, num_communities))
    
    node_colors = [colors[communities[n] % len(colors)] for n in G_filtrado.nodes()]
    
    # Tamanho dos nós proporcional à importância (weighted degree)
    weighted_degree = {n: G_filtrado.degree(n, weight='weight') for n in G_filtrado.nodes()}
    max_degree = max(weighted_degree.values())
    min_degree = min(weighted_degree.values())
    
    # Normalizar tamanhos (300 a 3500)
    node_sizes = [300 + ((weighted_degree[n] - min_degree) / (max_degree - min_degree)) * 3200 
                  for n in G_filtrado.nodes()]
    
    # Arestas com transparência
    edge_weights = [G_filtrado[u][v]['weight'] for u, v in G_filtrado.edges()]
    max_weight = max(edge_weights)
    widths = [0.3 + (G_filtrado[u][v]['weight'] / max_weight) * 5 for u, v in G_filtrado.edges()]
    
    # Desenhar arestas (fundo)
    nx.draw_networkx_edges(
        G_filtrado,
        pos,
        width=widths,
        alpha=0.12,
        edge_color='#CCCCCC'
    )
    
    # Desenhar nós com bordas pretas
    nx.draw_networkx_nodes(
        G_filtrado,
        pos,
        node_size=node_sizes,
        node_color=node_colors,
        alpha=0.95,
        edgecolors='black',
        linewidths=2.5
    )
    
    # Labels dos personagens mais importantes
    top_nodes = sorted(weighted_degree, key=weighted_degree.get, reverse=True)[:80]
    labels = {n: n for n in G_filtrado.nodes() if n in top_nodes}
    
    nx.draw_networkx_labels(
        G_filtrado,
        pos,
        labels=labels,
        font_size=11,
        font_weight='bold',
        font_color='black',
        font_family='sans-serif'
    )
    
    # Legenda das comunidades
    from collections import Counter
    community_counts = Counter(communities.values())
    top_communities = [c for c, _ in community_counts.most_common(15)]
    
    legend_elements = []
    for comm_id in top_communities:
        membros = [p for p, c in communities.items() if c == comm_id]
        count = len(membros)
        # Pegar os 3 mais importantes da comunidade
        membros_importantes = sorted(membros, key=lambda x: weighted_degree.get(x, 0), reverse=True)[:3]
        principais = ', '.join(membros_importantes)
        legend_elements.append(
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor=colors[comm_id % len(colors)], 
                      markersize=15, 
                      markeredgecolor='black',
                      markeredgewidth=2,
                      label=f'Comunidade {comm_id+1} ({count} membros): {principais}')
        )
    
    legend = ax.legend(handles=legend_elements, loc='upper left', fontsize=13, 
                      framealpha=0.95, title='Comunidades Detectadas (Algoritmo Louvain)',
                      title_fontsize=15, edgecolor='black', fancybox=True, shadow=True)
    
    # Título e subtítulo
    plt.suptitle("Rede de Interações - Game of Thrones",
                fontsize=32, fontweight='bold', y=0.98)
    plt.title(f"{G_filtrado.number_of_nodes()} personagens • {num_communities} comunidades • "
             f"Cores = Comunidades • Tamanho = Importância",
              fontsize=20, pad=20, style='italic')
    
    # Adicionar nota explicativa
    fig.text(0.5, 0.02, 
            'Tamanho dos nós proporcional ao peso total de interações | '
            'Cores representam comunidades detectadas | '
            f'Arestas filtradas (peso ≥ {peso_minimo_aresta})',
            ha='center', fontsize=14, style='italic', color='#555555')
    
    plt.axis('off')
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    
    plt.savefig('saidas/grafo_completo_comunidades.png', dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none')
    print("✅ Grafo com comunidades salvo em: saidas/grafo_completo_comunidades.png")
    
    plt.show()

def visualizar_grafo_comunidades_agrupado(G, communities, peso_minimo_aresta=5):
    """Visualiza grafo com comunidades fisicamente agrupadas"""
    
    G_filtrado = nx.Graph()
    for u, v, data in G.edges(data=True):
        if data['weight'] >= peso_minimo_aresta:
            G_filtrado.add_edge(u, v, weight=data['weight'])
    
    print(f"\nGrafo agrupado (peso >= {peso_minimo_aresta}): {G_filtrado.number_of_nodes()} nós")
    
    fig, ax = plt.subplots(figsize=(45, 35), facecolor='white')
    
    print("Calculando layout agrupado por comunidades...")
    
    pos = {}
    num_communities = len(set(communities.values()))
    
    # Palette de cores expandida
    if num_communities <= 20:
        colors_map = plt.cm.tab20(np.linspace(0, 1, 20))
    else:
        colors_map = plt.cm.hsv(np.linspace(0, 1, num_communities))
    
    # Organizar comunidades em círculo
    angle_step = 2 * np.pi / num_communities
    radius = 18
    
    for comm_id in set(communities.values()):
        nodes_in_comm = [n for n in G_filtrado.nodes() if communities[n] == comm_id]
        subG = G_filtrado.subgraph(nodes_in_comm)
        
        sub_pos = nx.spring_layout(subG, k=2.5, iterations=80, seed=comm_id)
        
        angle = comm_id * angle_step
        center_x = radius * np.cos(angle)
        center_y = radius * np.sin(angle)
        
        for node in sub_pos:
            pos[node] = (sub_pos[node][0] * 3.5 + center_x, sub_pos[node][1] * 3.5 + center_y)
    
    # Cores e tamanhos
    node_colors = [colors_map[communities[n] % len(colors_map)] for n in G_filtrado.nodes()]
    weighted_degree = {n: G_filtrado.degree(n, weight='weight') for n in G_filtrado.nodes()}
    max_degree = max(weighted_degree.values())
    min_degree = min(weighted_degree.values())
    
    # Normalizar tamanhos
    node_sizes = [250 + ((weighted_degree[n] - min_degree) / (max_degree - min_degree)) * 2500 
                  for n in G_filtrado.nodes()]
    
    # Arestas
    edge_weights = [G_filtrado[u][v]['weight'] for u, v in G_filtrado.edges()]
    max_weight = max(edge_weights)
    widths = [0.2 + (G_filtrado[u][v]['weight'] / max_weight) * 4 for u, v in G_filtrado.edges()]
    
    edges_between = [(u, v) for u, v in G_filtrado.edges() if communities[u] != communities[v]]
    edges_within = [(u, v) for u, v in G_filtrado.edges() if communities[u] == communities[v]]
    
    # Arestas dentro das comunidades (cinza claro)
    if edges_within:
        nx.draw_networkx_edges(
            G_filtrado,
            pos,
            edgelist=edges_within,
            width=[widths[list(G_filtrado.edges()).index((u, v))] for u, v in edges_within],
            alpha=0.15,
            edge_color='#BBBBBB'
        )
    
    # Arestas entre comunidades (vermelho tracejado)
    if edges_between:
        nx.draw_networkx_edges(
            G_filtrado,
            pos,
            edgelist=edges_between,
            width=[widths[list(G_filtrado.edges()).index((u, v))] * 0.6 for u, v in edges_between],
            alpha=0.4,
            edge_color='#FF4444',
            style='dashed'
        )
    
    # Nós
    nx.draw_networkx_nodes(
        G_filtrado,
        pos,
        node_size=node_sizes,
        node_color=node_colors,
        alpha=0.95,
        edgecolors='black',
        linewidths=3
    )
    
    # Labels
    top_nodes = sorted(weighted_degree, key=weighted_degree.get, reverse=True)[:90]
    labels = {n: n for n in G_filtrado.nodes() if n in top_nodes}
    
    nx.draw_networkx_labels(
        G_filtrado,
        pos,
        labels=labels,
        font_size=10,
        font_weight='bold',
        font_family='sans-serif'
    )
    
    # Legenda detalhada
    from collections import Counter
    community_counts = Counter(communities.values())
    top_communities = [c for c, _ in community_counts.most_common(15)]
    
    legend_elements = []
    for comm_id in top_communities:
        membros = [p for p, c in communities.items() if c == comm_id]
        count = len(membros)
        # Pegar os mais importantes da comunidade
        membros_importantes = sorted(membros, key=lambda x: weighted_degree.get(x, 0), reverse=True)[:4]
        principais = ', '.join(membros_importantes)
        legend_elements.append(
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor=colors_map[comm_id % len(colors_map)], 
                      markersize=16, 
                      markeredgecolor='black',
                      markeredgewidth=2.5,
                      label=f'Comunidade {comm_id+1} ({count}): {principais}')
        )
    
    # Adicionar legenda de arestas
    legend_elements.append(plt.Line2D([0], [0], color='#BBBBBB', linewidth=3, 
                                     label='Interações dentro da comunidade'))
    legend_elements.append(plt.Line2D([0], [0], color='#FF4444', linewidth=3, 
                                     linestyle='--', label='Interações entre comunidades'))
    
    legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=12, 
                      framealpha=0.95, title='Comunidades e Conexões',
                      title_fontsize=14, edgecolor='black', fancybox=True, shadow=True)
    
    # Títulos
    plt.suptitle("Rede de Interações - Comunidades Agrupadas",
                fontsize=34, fontweight='bold', y=0.98)
    plt.title(f"Game of Thrones • {num_communities} comunidades (Algoritmo Louvain) • "
             f"Cores = Comunidades • Tamanho = Importância",
              fontsize=22, pad=20, style='italic')
    
    # Nota explicativa
    fig.text(0.5, 0.02, 
            'Comunidades agrupadas espacialmente | '
            'Tamanho dos nós proporcional ao peso de interações | '
            'Linhas vermelhas tracejadas conectam comunidades diferentes',
            ha='center', fontsize=15, style='italic', color='#555555')
    
    plt.axis('off')
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    
    plt.savefig('saidas/grafo_completo_comunidades_agrupado.png', dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none')
    print("✅ Grafo agrupado salvo em: saidas/grafo_completo_comunidades_agrupado.png")
    
    plt.show()

def gerar_estatisticas(G):
    """Gera estatísticas do grafo completo"""
    print("\n" + "="*60)
    print("ESTATÍSTICAS DO GRAFO COMPLETO")
    print("="*60)
    
    print(f"\n📊 Estrutura:")
    print(f"   Nós (personagens): {G.number_of_nodes()}")
    print(f"   Arestas (interações): {G.number_of_edges()}")
    
    densidade = nx.density(G)
    print(f"   Densidade: {densidade:.4f}")
    
    componentes = nx.number_connected_components(G)
    print(f"   Componentes conectados: {componentes}")
    
    graus = [G.degree(n) for n in G.nodes()]
    print(f"   Grau médio: {sum(graus)/len(graus):.2f}")
    
    peso_total = sum(data['weight'] for u, v, data in G.edges(data=True))
    print(f"   Total de interações: {peso_total:,}")
    
    weighted_degree = {n: G.degree(n, weight='weight') for n in G.nodes()}
    top_10 = sorted(weighted_degree.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print(f"\n🏆 Top 10 Personagens (por peso total):")
    for i, (personagem, peso) in enumerate(top_10, 1):
        print(f"   {i:2d}. {personagem:30s} - {peso:,} interações")
    
    print("\n" + "="*60)

def main():
    print("="*60)
    print("GERAÇÃO DE GRAFO COMPLETO COM COMUNIDADES")
    print("Game of Thrones")
    print("="*60 + "\n")
    
    G = criar_grafo_completo()
    gerar_estatisticas(G)
    
    communities = detectar_comunidades(G)
    
    print("\n📊 Gerando visualizações...\n")
    
    print("[1/2] Grafo com comunidades coloridas (peso mínimo: 10)")
    visualizar_grafo_comunidades(G, communities, peso_minimo_aresta=10)
    
    print("\n[2/2] Grafo com comunidades agrupadas (peso mínimo: 5)")
    visualizar_grafo_comunidades_agrupado(G, communities, peso_minimo_aresta=5)
    
    print("\n" + "="*60)
    print("✅ CONCLUÍDO! Salvo em saidas/")
    print("="*60)

if __name__ == "__main__":
    main()
