import os
import csv
import re

def carregar_bloqueados():
    try:
        with open('src/bloq.txt', 'r', encoding='utf-8') as f:
            conteudo = f.read().strip()
            return [palavra.strip().lower() for palavra in conteudo.split(',') if palavra.strip()]
    except:
        return []

def extrair_personagens(pasta_genius, palavras_bloqueadas):
    personagens = {}
    personagens_txt = set()
    
    for root, dirs, files in os.walk(pasta_genius):
        for file in files:
            if file.endswith('.txt'):
                caminho = os.path.join(root, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    matches = re.findall(r'^([A-Z][A-Z\s\']+):', conteudo, re.MULTILINE)
                    for m in matches:
                        # Remover quebras de linha do nome
                        nome_limpo = m.replace('\n', ' ').replace('\r', ' ').strip()
                        personagens[nome_limpo] = personagens.get(nome_limpo, 0) + 1
                    personagens_txt.update([m.lower().strip() for m in matches])
    
    personagens_filtrados = []
    for p in sorted(personagens.keys()):
        nome_lower = p.lower().strip()
        bloqueado = False
        for palavra in palavras_bloqueadas:
            if nome_lower == palavra or nome_lower.startswith(palavra + ' ') or nome_lower.endswith(' ' + palavra):
                bloqueado = True
                break
        status = 'Bloqueado' if bloqueado else 'Ativo'
        personagens_filtrados.append((p.strip(), status, personagens[p]))
    
    return personagens_filtrados

def salvar_csv(personagens, caminho_saida):
    with open(caminho_saida, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['NOME', 'Status', 'Falas'])
        writer.writerows(personagens)

if __name__ == '__main__':
    pasta_genius = 'genius'
    pasta_datasets = 'datasets'
    
    os.makedirs(pasta_datasets, exist_ok=True)
    
    palavras_bloqueadas = carregar_bloqueados()
    personagens = extrair_personagens(pasta_genius, palavras_bloqueadas)
    caminho_saida = os.path.join(pasta_datasets, 'personagens.csv')
    salvar_csv(personagens, caminho_saida)
    
    print(f'Dataset criado: {caminho_saida}')
    print(f'Total de personagens: {len(personagens)}')
    print(f'Ativos: {sum(1 for _, s, _ in personagens if s == "Ativo")}')
    print(f'Bloqueados: {sum(1 for _, s, _ in personagens if s == "Bloqueado")}')
    print(f'Total de falas: {sum(f for _, _, f in personagens)}')
