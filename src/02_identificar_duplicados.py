import csv
import json
import requests
import os
import time

API_URL = "https://api.deepseek.com/v1/chat/completions"

def carregar_api_key():
    try:
        with open('src/deepkey.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        key = input('\nAPI Key do DeepSeek não encontrada.\nDigite sua chave (ou Enter para sair): ').strip()
        if key:
            os.makedirs('src', exist_ok=True)
            with open('src/deepkey.txt', 'w', encoding='utf-8') as f:
                f.write(key)
            print('✓ Chave salva em src/deepkey.txt\n')
        return key

API_KEY = carregar_api_key()

def carregar_personagens():
    personagens = []
    falas_map = {}
    with open('datasets/personagens.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Status'] == 'Ativo':
                personagens.append(row['NOME'])
                falas_map[row['NOME']] = int(row['Falas'])
    return personagens, falas_map

def processar_bloco(nomes, bloco_num, tentativa=1):
    prompt = f"""Analise os seguintes personagens de Game of Thrones e identifique duplicatas (erros de digitação, apelidos, variações de nome).

Personagens: {', '.join(nomes)}

Retorne APENAS um JSON válido no formato:
[
  {{"NOME_OFICIAL": "Nome Principal", "VARIACOES": ["variacao1", "variacao2"], "FAMILIA_GRUPO": "Casa/Grupo"}},
  ...
]

Regras:
- NOME_OFICIAL: preferencialmente 'Nome + Sobrenome' completo (ex: 'Jon Snow', 'Arya Stark', 'Tyrion Lannister'). Use apenas primeiro nome se o personagem não tiver sobrenome conhecido
- VARIACOES: lista de todas as variações (incluindo o oficial)
- FAMILIA_GRUPO: Casa Stark, Casa Lannister, Night's Watch, etc.
- Retorne TODOS os personagens enviados, mesmo sem variações"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        resultado = response.json()['choices'][0]['message']['content']
        
        with open(f'compile/deepseek_bloco_{bloco_num}.txt', 'w', encoding='utf-8') as f:
            f.write(resultado)
        
        json_start = resultado.find('[')
        json_end = resultado.rfind(']') + 1
        if json_start != -1 and json_end > json_start:
            return json.loads(resultado[json_start:json_end])
        return []
    except Exception as e:
        if tentativa < 3:
            print(f"Erro no bloco {bloco_num} (tentativa {tentativa}): {e}")
            print(f"Aguardando 10s antes de tentar novamente...")
            time.sleep(10)
            return processar_bloco(nomes, bloco_num, tentativa + 1)
        print(f"Erro no bloco {bloco_num} após 3 tentativas: {e}")
        return []

def verificar_duplicados_oficiais(nomes_oficiais):
    prompt = f"""Analise os seguintes nomes oficiais de personagens de Game of Thrones e identifique quais são a MESMA pessoa.

Nomes: {', '.join(nomes_oficiais)}

Retorne APENAS um JSON válido no formato:
[
  ["Nome1", "Nome2", "Nome3"],
  ["Nome4", "Nome5"]
]

Onde cada array interno contém nomes que são a mesma pessoa. Retorne apenas os grupos de duplicados, não inclua nomes únicos."""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        resultado = response.json()['choices'][0]['message']['content']
        
        with open('compile/deepseek_duplicados_oficiais.txt', 'w', encoding='utf-8') as f:
            f.write(resultado)
        
        json_start = resultado.find('[')
        json_end = resultado.rfind(']') + 1
        if json_start != -1 and json_end > json_start:
            return json.loads(resultado[json_start:json_end])
        return []
    except Exception as e:
        print(f"Erro ao verificar duplicados oficiais: {e}")
        return []

def mesclar_resultados(todos_resultados):
    mapa = {}
    for item in todos_resultados:
        oficial = item['NOME_OFICIAL']
        if oficial in mapa:
            mapa[oficial]['VARIACOES'].extend(item['VARIACOES'])
            mapa[oficial]['VARIACOES'] = list(set(mapa[oficial]['VARIACOES']))
        else:
            mapa[oficial] = item
    return list(mapa.values())

def mesclar_duplicados_oficiais(resultados, duplicados):
    if not duplicados:
        return resultados
    
    mapa = {r['NOME_OFICIAL']: r for r in resultados}
    
    for grupo in duplicados:
        if len(grupo) < 2:
            continue
        
        principal = grupo[0]
        if principal not in mapa:
            continue
        
        for nome in grupo[1:]:
            if nome in mapa:
                mapa[principal]['VARIACOES'].extend(mapa[nome]['VARIACOES'])
                mapa[principal]['VARIACOES'] = list(set(mapa[principal]['VARIACOES']))
                del mapa[nome]
    
    return list(mapa.values())

def salvar_dicionario(resultados, falas_map):
    with open('datasets/personagens_dicionario.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['NOME_OFICIAL', 'VARIACOES', 'FAMILIA_GRUPO', 'TOTAL_FALAS'])
        for item in resultados:
            total_falas = sum(falas_map.get(var, 0) for var in item['VARIACOES'])
            writer.writerow([
                item['NOME_OFICIAL'].upper(),
                '|'.join(item['VARIACOES']),
                item['FAMILIA_GRUPO'],
                total_falas
            ])

if __name__ == '__main__':
    os.makedirs('compile', exist_ok=True)
    
    personagens, falas_map = carregar_personagens()
    print(f'Total de personagens ativos: {len(personagens)}')
    
    if not API_KEY:
        print('\nOperação cancelada.')
        exit(1)
    
    blocos = [personagens[i:i+50] for i in range(0, len(personagens), 50)]
    todos_resultados = []
    
    for i, bloco in enumerate(blocos, 1):
        print(f'Processando bloco {i}/{len(blocos)} ({len(bloco)} personagens)...')
        resultado = processar_bloco(bloco, i)
        todos_resultados.extend(resultado)
        print(f'Bloco {i}: {len(resultado)} personagens identificados')
        if i < len(blocos):
            time.sleep(2)
    
    resultados_finais = mesclar_resultados(todos_resultados)
        
    print(f'\nDicionário criado: datasets/personagens_dicionario.csv')
    print(f'Total de personagens oficiais: {len(resultados_finais)}')
