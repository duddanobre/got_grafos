import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
from criar_grafo import criar_grafo
from sklearn.preprocessing import MinMaxScaler
import numpy as np

def calcular_centralidade_grau(G, top_n=10):
    """Centralidade de Grau: Quem tem mais conexões diretas?"""
    output = []
    output.append("[1] CENTRALIDADE DE GRAU (Degree Centrality)")
    output.append("    Mede quantas conexoes diretas cada personagem tem\n")
    
    degree_cent = nx.degree_centrality(G)
    top_degree = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    output.append(f"Top {top_n} personagens com mais conexões:")
    for i, (personagem, score) in enumerate(top_degree, 1):
        num_conexoes = G.degree(personagem)
        output.append(f"  {i:2d}. {personagem:25s} - {score:.4f} ({num_conexoes} conexoes)")
    
    return degree_cent, output

def calcular_centralidade_intermediacao(G, top_n=10):
    """Centralidade de Intermediação: Quem conecta diferentes grupos?"""
    output = []
    output.append("\n[2] CENTRALIDADE DE INTERMEDIACAO (Betweenness Centrality)")
    output.append("    Mede quem serve de ponte entre diferentes grupos\n")
    
    betweenness_cent = nx.betweenness_centrality(G, weight='weight')
    top_betweenness = sorted(betweenness_cent.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    output.append(f"Top {top_n} personagens que conectam grupos:")
    for i, (personagem, score) in enumerate(top_betweenness, 1):
        output.append(f"  {i:2d}. {personagem:25s} - {score:.4f}")
    
    return betweenness_cent, output

def calcular_pagerank(G, top_n=10):
    """PageRank: Quem é mais influente considerando a rede toda?"""
    output = []
    output.append("\n[3] PAGERANK (Influencia)")
    output.append("    Mede a importancia considerando conexoes de qualidade\n")
    
    pagerank = nx.pagerank(G, weight='weight')
    top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    output.append(f"Top {top_n} personagens mais influentes:")
    for i, (personagem, score) in enumerate(top_pagerank, 1):
        output.append(f"  {i:2d}. {personagem:25s} - {score:.4f}")
    
    return pagerank, output

def calcular_centralidade_proximidade(G, top_n=10):
    """Centralidade de Proximidade: Quem está mais próximo de todos?"""
    output = []
    output.append("\n[4] CENTRALIDADE DE PROXIMIDADE (Closeness Centrality)")
    output.append("    Mede quao proximo um personagem esta de todos os outros\n")
    
    closeness_cent = nx.closeness_centrality(G, distance='weight')
    top_closeness = sorted(closeness_cent.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    output.append(f"Top {top_n} personagens mais centrais:")
    for i, (personagem, score) in enumerate(top_closeness, 1):
        output.append(f"  {i:2d}. {personagem:25s} - {score:.4f}")
    
    return closeness_cent, output

def calcular_eigenvector_centrality(G, top_n=10):
    """Eigenvector Centrality: Importância baseada na importância dos vizinhos"""
    output = []
    output.append("\n[5] EIGENVECTOR CENTRALITY (Importancia dos Aliados)")
    output.append("    Mede importancia baseada na importancia dos vizinhos\n")
    
    try:
        eigenvector_cent = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
    except:
        eigenvector_cent = nx.eigenvector_centrality_numpy(G, weight='weight')
    
    top_eigenvector = sorted(eigenvector_cent.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    output.append(f"Top {top_n} personagens com aliados importantes:")
    for i, (personagem, score) in enumerate(top_eigenvector, 1):
        output.append(f"  {i:2d}. {personagem:25s} - {score:.4f}")
    
    return eigenvector_cent, output

def calcular_weighted_degree(G, top_n=10):
    """Weighted Degree: Frequência total de interações"""
    output = []
    output.append("\n[6] WEIGHTED DEGREE (Frequencia de Interacoes)")
    output.append("    Considera a frequencia das interacoes, nao so o numero\n")
    
    weighted_degree = dict(G.degree(weight='weight'))
    top_weighted = sorted(weighted_degree.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    output.append(f"Top {top_n} personagens com mais interacoes:")
    for i, (personagem, score) in enumerate(top_weighted, 1):
        output.append(f"  {i:2d}. {personagem:25s} - {score:.0f} interacoes")
    
    return weighted_degree, output

def detectar_comunidades(G, top_n=5):
    """Detecção de Comunidades: Identifica grupos de poder"""
    output = []
    output.append("\n[7] DETECCAO DE COMUNIDADES (Grupos de Poder)")
    output.append("    Identifica clusters naturais na rede\n")
    
    try:
        import community as community_louvain
        communities = community_louvain.best_partition(G, weight='weight')
    except ImportError:
        import os
        os.system("pip install python-louvain")
        import community as community_louvain
        communities = community_louvain.best_partition(G, weight='weight')
    
    community_counts = Counter(communities.values())
    output.append(f"Total de comunidades detectadas: {len(community_counts)}\n")
    
    for comm_id, count in community_counts.most_common(top_n):
        membros = [p for p, c in communities.items() if c == comm_id]
        output.append(f"Comunidade {comm_id + 1} ({count} membros):")
        output.append(f"  {', '.join(membros[:10])}")
        if count > 10:
            output.append(f"  ... e mais {count - 10} personagens")
        output.append("")
    
    return communities, output

def ranking_consolidado(degree, betweenness, pagerank, closeness, eigenvector, weighted_degree, top_n=15):
    """Cria ranking consolidado com normalização e pesos por importância"""
    output = []
    output.append("\n[8] RANKING CONSOLIDADO - PERSONAGEM MAIS IMPORTANTE")
    output.append("    Metricas normalizadas com pesos por importancia\n")
    output.append("    Pesos: PageRank(30%), Betweenness(25%), Degree(25%), Closeness(20%)\n")
    
    personagens = list(degree.keys())
    
    # Criar arrays para normalização
    scaler = MinMaxScaler()
    norm_pr = scaler.fit_transform(np.array([pagerank[p] for p in personagens]).reshape(-1, 1)).flatten()
    norm_bt = scaler.fit_transform(np.array([betweenness[p] for p in personagens]).reshape(-1, 1)).flatten()
    norm_dc = scaler.fit_transform(np.array([degree[p] for p in personagens]).reshape(-1, 1)).flatten()
    norm_cc = scaler.fit_transform(np.array([closeness[p] for p in personagens]).reshape(-1, 1)).flatten()
    
    # Calcular score ponderado
    scores = {}
    for i, p in enumerate(personagens):
        score = norm_pr[i] * 0.30 + norm_bt[i] * 0.25 + norm_dc[i] * 0.25 + norm_cc[i] * 0.20
        scores[p] = score
    
    top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    output.append(f"Top {top_n} personagens MAIS IMPORTANTES matematicamente:\n")
    for i, (personagem, score) in enumerate(top_scores, 1):
        output.append(f"  {i:2d}. {personagem:25s} - Score: {score:.4f}")
        output.append(f"      PageRank: {pagerank[personagem]:.4f} | "
              f"Betweenness: {betweenness[personagem]:.4f} | "
              f"Degree: {degree[personagem]:.4f} | "
              f"Closeness: {closeness[personagem]:.4f}")
    
    return scores, output

def visualizar_top_personagens(G, scores, top_n=20):
    """Visualiza os top personagens com suas métricas"""
    print(f"\n[*] Gerando visualizacao dos top {top_n} personagens...")
    
    # Selecionar top personagens
    top_personagens = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_nodes = [p for p, _ in top_personagens]
    
    # Criar subgrafo
    G_top = G.subgraph(top_nodes).copy()
    
    plt.figure(figsize=(18, 12))
    
    # Layout
    pos = nx.spring_layout(G_top, k=2, iterations=50, seed=42)
    
    # Tamanho dos nós baseado no score
    node_sizes = [scores[n] * 5000 for n in G_top.nodes()]
    
    # Cores baseadas no score
    node_colors = [scores[n] for n in G_top.nodes()]
    
    # Desenhar nós
    nx.draw_networkx_nodes(
        G_top, pos,
        node_size=node_sizes,
        node_color=node_colors,
        cmap=plt.cm.Reds,
        alpha=0.9,
        edgecolors='black',
        linewidths=2
    )
    
    # Desenhar arestas
    widths = [G_top[u][v]['weight'] / 15 for u, v in G_top.edges()]
    nx.draw_networkx_edges(
        G_top, pos,
        width=widths,
        alpha=0.3,
        edge_color='gray'
    )
    
    # Labels
    nx.draw_networkx_labels(
        G_top, pos,
        font_size=10,
        font_weight='bold',
        font_family='sans-serif'
    )
    
    plt.title(f"Top {top_n} Personagens Mais Importantes - Game of Thrones", 
              fontsize=18, fontweight='bold', pad=20)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('saidas/grafo_top_personagens.png', dpi=300, bbox_inches='tight')
    print("[OK] Visualizacao salva em: saidas/grafo_top_personagens.png")
    plt.show()

def main():
    all_output = []
    all_output.append("="*70)
    all_output.append("  ANALISE DE CENTRALIDADE - GAME OF THRONES")
    all_output.append("  Quem e matematicamente o personagem mais importante?")
    all_output.append("="*70 + "\n")
    
    print("\n".join(all_output))
    
    print("[*] Carregando dataset e criando grafo...\n")
    G = criar_grafo()
    print()
    
    degree, out1 = calcular_centralidade_grau(G, top_n=10)
    all_output.extend(out1)
    print("\n".join(out1))
    
    betweenness, out2 = calcular_centralidade_intermediacao(G, top_n=10)
    all_output.extend(out2)
    print("\n".join(out2))
    
    pagerank, out3 = calcular_pagerank(G, top_n=10)
    all_output.extend(out3)
    print("\n".join(out3))
    
    closeness, out4 = calcular_centralidade_proximidade(G, top_n=10)
    all_output.extend(out4)
    print("\n".join(out4))
    
    eigenvector, out5 = calcular_eigenvector_centrality(G, top_n=10)
    all_output.extend(out5)
    print("\n".join(out5))
    
    weighted_deg, out6 = calcular_weighted_degree(G, top_n=10)
    all_output.extend(out6)
    print("\n".join(out6))
    
    communities, out7 = detectar_comunidades(G, top_n=5)
    all_output.extend(out7)
    print("\n".join(out7))
    
    scores, out8 = ranking_consolidado(degree, betweenness, pagerank, closeness, eigenvector, weighted_deg, top_n=15)
    all_output.extend(out8)
    print("\n".join(out8))
    
    visualizar_top_personagens(G, scores, top_n=20)
    
    footer = ["\n" + "="*70, "[OK] ANALISE COMPLETA!", "="*70]
    all_output.extend(footer)
    print("\n".join(footer))
    
    with open('saidas/analise_centralidade.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(all_output))
    print("\n[OK] Relatorio salvo em: saidas/analise_centralidade.txt")

if __name__ == "__main__":
    main()
