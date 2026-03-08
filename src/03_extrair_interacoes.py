import csv
import re
import os

def carregar_dicionario():
    try:
        mapa = {}
        with open('datasets/personagens_dicionario.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                oficial = row['NOME_OFICIAL']
                variacoes = row['VARIACOES'].split('|')
                for variacao in variacoes:
                    mapa[variacao.strip()] = oficial
        return mapa
    except:
        mapa = {}
        with open('datasets/personagens.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Status'] == 'Ativo':
                    mapa[row['NOME']] = row['NOME']
        return mapa

def extrair_interacoes(arquivo, temporada, episodio, dicionario):
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    linhas = conteudo.split('\n')
    cenas = []
    cena_atual = {'descricao': '', 'falas': []}
    
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        
        match = re.match(r'^([A-Z][A-Za-z\s\']+):\s*(.+)$', linha)
        if match:
            falante = match.group(1).strip()
            fala = match.group(2).strip()
            if falante in dicionario:
                falante_oficial = dicionario[falante]
                cena_atual['falas'].append({'falante': falante_oficial, 'fala': fala})
            elif falante.upper() in dicionario:
                falante_oficial = dicionario[falante.upper()]
                cena_atual['falas'].append({'falante': falante_oficial, 'fala': fala})
        else:
            if cena_atual['falas']:
                cenas.append(cena_atual)
                cena_atual = {'descricao': linha, 'falas': []}
            else:
                cena_atual['descricao'] += ' ' + linha if cena_atual['descricao'] else linha
    
    if cena_atual['falas']:
        cenas.append(cena_atual)
    
    interacoes = []
    for idx_cena, cena in enumerate(cenas):
        personagens_cena = list(set([f['falante'] for f in cena['falas']]))
        num_personagens = len(personagens_cena)
        tipo = 'group' if num_personagens > 2 else 'single'
        
        for fala_info in cena['falas']:
            falante = fala_info['falante']
            fala = fala_info['fala']
            tamanho = len(fala)
            
            ouvintes = [p for p in personagens_cena if p != falante]
            if not ouvintes:
                ouvintes = [falante]
            
            for ouvinte in ouvintes:
                interacoes.append({
                    'NTemporada': temporada,
                    'NEpisodio': episodio,
                    'NCena': idx_cena,
                    'falante': falante,
                    'ouvinte': ouvinte,
                    'fala': fala,
                    'tamanho_fala': tamanho,
                    'descricao_cena': cena['descricao'][:200],
                    'num_personagens_cena': num_personagens,
                    'tipo_interacao': tipo
                })
    
    return interacoes

def processar_todos():
    dicionario = carregar_dicionario()
    todas_interacoes = []
    
    for temp in range(1, 9):
        pasta = f'genius/s{temp:02d}'
        if not os.path.exists(pasta):
            continue
        
        arquivos = sorted([f for f in os.listdir(pasta) if f.endswith('.txt')])
        for arquivo in arquivos:
            match = re.search(r's(\d+)e(\d+)', arquivo)
            if match:
                ep = int(match.group(2))
                caminho = os.path.join(pasta, arquivo)
                print(f'Processando S{temp:02d}E{ep:02d}...')
                interacoes = extrair_interacoes(caminho, temp, ep, dicionario)
                todas_interacoes.extend(interacoes)
                print(f'  {len(interacoes)} interações extraídas')
    
    return todas_interacoes

def salvar_csv(interacoes):
    with open('datasets/interacoes.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['NTemporada', 'NEpisodio', 'NCena', 'falante', 'ouvinte', 'fala', 'tamanho_fala', 'descricao_cena', 'num_personagens_cena', 'tipo_interacao'])
        writer.writeheader()
        writer.writerows(interacoes)

if __name__ == '__main__':
    print('Extraindo interações...')
    interacoes = processar_todos()
    salvar_csv(interacoes)
    print(f'\nTotal de interações: {len(interacoes)}')
    print(f'Arquivo salvo: datasets/interacoes.csv')
