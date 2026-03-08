import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import os

def criar_grafo():
    """Cria grafo a partir do dataset de interações"""
    df = pd.read_csv("datasets/interacoes.csv")
    df_grouped = df.groupby(['falante', 'ouvinte']).size().reset_index(name='weight')
    G = nx.from_pandas_edgelist(df_grouped, 'falante', 'ouvinte', edge_attr='weight', create_using=nx.Graph())
    return G

def calcular_centralidade_grau(G, top_n=10):
    """Centralidade de Grau: Quem tem mais conexões diretas?"""
    degree_cent = nx.degree_centrality(G)
    top_degree = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    print("\n[1] CENTRALIDADE DE GRAU (Degree Centrality)")
    print("    Mede quantas conexoes diretas cada personagem tem\n")
    for i, (personagem, score) in enumerate(top_degree, 1):
        print(f"  {i:2d}. {personagem:25s} - {score:.6f}")
    
    return degree_cent

def calcular_centralidade_intermediacao(G, top_n=10):
    """Centralidade de Intermediação: Quem conecta diferentes grupos?"""
    betweenness_cent = nx.betweenness_centrality(G, weight='weight')
    top_betweenness = sorted(betweenness_cent.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    print("\n[2] CENTRALIDADE DE INTERMEDIACAO (Betweenness Centrality)")
    print("    Mede quem serve de ponte entre diferentes grupos\n")
    for i, (personagem, score) in enumerate(top_betweenness, 1):
        print(f"  {i:2d}. {personagem:25s} - {score:.6f}")
    
    return betweenness_cent

def calcular_pagerank(G, top_n=10):
    """PageRank: Quem é mais influente considerando a rede toda?"""
    pagerank = nx.pagerank(G, weight='weight', max_iter=100, tol=1e-06)
    top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    print("\n[3] PAGERANK (Influencia)")
    print("    Mede a importancia considerando conexoes de qualidade\n")
    for i, (personagem, score) in enumerate(top_pagerank, 1):
        print(f"  {i:2d}. {personagem:25s} - {score:.6f}")
    
    return pagerank

def calcular_centralidade_proximidade(G, top_n=10):
    """Centralidade de Proximidade: Quem está mais próximo de todos?"""
    closeness_cent = nx.closeness_centrality(G, distance='weight')
    top_closeness = sorted(closeness_cent.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    print("\n[4] CENTRALIDADE DE PROXIMIDADE (Closeness Centrality)")
    print("    Mede quao proximo um personagem esta de todos os outros\n")
    for i, (personagem, score) in enumerate(top_closeness, 1):
        print(f"  {i:2d}. {personagem:25s} - {score:.6f}")
    
    return closeness_cent

def calcular_weighted_degree(G, top_n=10):
    """Weighted Degree: Frequência total de interações"""
    weighted_degree = dict(G.degree(weight='weight'))
    top_weighted = sorted(weighted_degree.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    print("\n[5] WEIGHTED DEGREE (Frequencia de Interacoes)")
    print("    Considera a frequencia das interacoes, nao so o numero\n")
    for i, (personagem, score) in enumerate(top_weighted, 1):
        print(f"  {i:2d}. {personagem:25s} - {score:.0f} interacoes")
    
    return weighted_degree

def ranking_consolidado(degree, betweenness, pagerank, closeness, top_n=20):
    """Cria ranking consolidado com normalização e pesos por importância"""
    personagens = list(degree.keys())
    scaler = MinMaxScaler()
    
    norm_pr = scaler.fit_transform(np.array([pagerank[p] for p in personagens]).reshape(-1, 1)).flatten()
    norm_bt = scaler.fit_transform(np.array([betweenness[p] for p in personagens]).reshape(-1, 1)).flatten()
    norm_dc = scaler.fit_transform(np.array([degree[p] for p in personagens]).reshape(-1, 1)).flatten()
    norm_cc = scaler.fit_transform(np.array([closeness[p] for p in personagens]).reshape(-1, 1)).flatten()
    
    scores = {p: norm_pr[i]*0.3 + norm_bt[i]*0.25 + norm_dc[i]*0.25 + norm_cc[i]*0.2 for i,p in enumerate(personagens)}
    top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    print("\n[6] RANKING CONSOLIDADO - PERSONAGEM MAIS IMPORTANTE")
    print("    Metricas normalizadas com pesos por importancia")
    print("    Pesos: PageRank(30%), Betweenness(25%), Degree(25%), Closeness(20%)\n")
    
    for i, (personagem, score) in enumerate(top_scores, 1):
        print(f"  {i:2d}. {personagem:25s} - Score: {score:.6f}")
        print(f"      PageRank: {pagerank[personagem]:.6f} | Betweenness: {betweenness[personagem]:.6f} | "
              f"Degree: {degree[personagem]:.6f} | Closeness: {closeness[personagem]:.6f}")
    
    return scores

def main():
    output = []
    output.append("=" * 80)
    output.append("ANALISE DE CENTRALIDADE - GAME OF THRONES")
    output.append("Quem e matematicamente o personagem mais importante?")
    output.append("=" * 80)
    output.append("")
    
    print("\n".join(output))
    
    output.append("[*] Carregando dados e criando grafo...")
    G = criar_grafo()
    msg = f"[OK] Grafo: {G.number_of_nodes()} nos, {G.number_of_edges()} arestas"
    output.append(msg)
    output.append("")
    print(msg)
    
    degree_cent = calcular_centralidade_grau(G)
    output.append("\n[1] CENTRALIDADE DE GRAU (Degree Centrality)")
    output.append("    Mede quantas conexoes diretas cada personagem tem\n")
    for i, (p, s) in enumerate(sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:10], 1):
        output.append(f"  {i:2d}. {p:25s} - {s:.6f}")
    
    betweenness_cent = calcular_centralidade_intermediacao(G)
    output.append("\n[2] CENTRALIDADE DE INTERMEDIACAO (Betweenness Centrality)")
    output.append("    Mede quem serve de ponte entre diferentes grupos\n")
    for i, (p, s) in enumerate(sorted(betweenness_cent.items(), key=lambda x: x[1], reverse=True)[:10], 1):
        output.append(f"  {i:2d}. {p:25s} - {s:.6f}")
    
    pagerank = calcular_pagerank(G)
    output.append("\n[3] PAGERANK (Influencia)")
    output.append("    Mede a importancia considerando conexoes de qualidade\n")
    for i, (p, s) in enumerate(sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10], 1):
        output.append(f"  {i:2d}. {p:25s} - {s:.6f}")
    
    closeness_cent = calcular_centralidade_proximidade(G)
    output.append("\n[4] CENTRALIDADE DE PROXIMIDADE (Closeness Centrality)")
    output.append("    Mede quao proximo um personagem esta de todos os outros\n")
    for i, (p, s) in enumerate(sorted(closeness_cent.items(), key=lambda x: x[1], reverse=True)[:10], 1):
        output.append(f"  {i:2d}. {p:25s} - {s:.6f}")
    
    weighted_degree = calcular_weighted_degree(G)
    output.append("\n[5] WEIGHTED DEGREE (Frequencia de Interacoes)")
    output.append("    Considera a frequencia das interacoes, nao so o numero\n")
    for i, (p, s) in enumerate(sorted(weighted_degree.items(), key=lambda x: x[1], reverse=True)[:10], 1):
        output.append(f"  {i:2d}. {p:25s} - {s:.0f} interacoes")
    
    scores = ranking_consolidado(degree_cent, betweenness_cent, pagerank, closeness_cent)
    output.append("\n[6] RANKING CONSOLIDADO - PERSONAGEM MAIS IMPORTANTE")
    output.append("    Metricas normalizadas com pesos por importancia")
    output.append("    Pesos: PageRank(30%), Betweenness(25%), Degree(25%), Closeness(20%)\n")
    for i, (p, s) in enumerate(sorted(scores.items(), key=lambda x: x[1], reverse=True)[:20], 1):
        output.append(f"  {i:2d}. {p:25s} - Score: {s:.6f}")
        output.append(f"      PageRank: {pagerank[p]:.6f} | Betweenness: {betweenness_cent[p]:.6f} | "
                     f"Degree: {degree_cent[p]:.6f} | Closeness: {closeness_cent[p]:.6f}")
    
    output.append("\n" + "=" * 80)
    output.append("ANALISE CONCLUIDA")
    output.append("=" * 80)
    print("\n" + "=" * 80)
    print("ANALISE CONCLUIDA")
    print("=" * 80)
    
    os.makedirs('saidas', exist_ok=True)
    with open('saidas/analise_centralidade.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(output))
    print("\n[OK] Relatorio salvo em: saidas/analise_centralidade.txt")

if __name__ == "__main__":
    main()