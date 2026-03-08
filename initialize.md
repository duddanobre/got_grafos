# Guia de Inicialização do Projeto GOT-Grafos

Este documento descreve o passo a passo para inicializar e processar os dados do projeto.

## Passo 1: Extrair Personagens

O primeiro passo é extrair todos os personagens dos arquivos de transcrição dos episódios.

### Comando
```bash
python src/01_extrair_personagens.py
```

### O que faz
- Lê todos os arquivos `.txt` da pasta `genius/` (temporadas s01 a s08)
- Identifica personagens pelo padrão `[NOME]:` (nomes em maiúsculas seguidos de dois pontos)
- Conta o número de falas de cada personagem
- Filtra personagens usando a lista de palavras bloqueadas em `src/bloq.txt`
- Gera o arquivo `datasets/personagens.csv`

### Arquivo de saída
`datasets/personagens.csv` com as colunas:
- **NOME**: Nome do personagem
- **Status**: `Ativo` ou `Bloqueado`
- **Falas**: Número total de falas do personagem

### Configuração de bloqueio
Para adicionar ou remover palavras bloqueadas, edite o arquivo `src/bloq.txt` (palavras separadas por vírgula).

---

## Passo 2: Identificar Personagens Duplicados

Identifica personagens com nomes diferentes que são a mesma pessoa (erros de digitação, apelidos, variações).

### Pré-requisito
Crie o arquivo `src/deepkey.txt` com sua chave da API DeepSeek (apenas a chave, sem espaços ou quebras de linha extras).

### Comando
```bash
python src/02_identificar_duplicados.py
```

### O que faz
- Lê personagens ativos de `datasets/personagens.csv`
- Processa em blocos de 50 nomes (limitação da API)
- Usa DeepSeek para identificar duplicatas e variações
- Salva respostas brutas em `compile/deepseek_bloco_N.txt`
- Mescla resultados pela chave NOME_OFICIAL
- Gera o arquivo `datasets/personagens_dicionario.csv`

### Arquivo de saída
`datasets/personagens_dicionario.csv` com as colunas:
- **NOME_OFICIAL**: Nome principal/correto do personagem
- **VARIACOES**: Todas as variações do nome (separadas por `|`)
- **FAMILIA_GRUPO**: Casa ou grupo do personagem (ex: Casa Stark, Night's Watch)

---

## Passo 3: Extrair Interações

Extrai todas as interações entre personagens dos episódios.

### Comando
```bash
python src/03_extrair_interacoes.py
```

### O que faz
- Lê todos os arquivos `.txt` da pasta `genius/`
- Identifica cenas e falas de personagens
- Descarta cenas sem falas
- Em conversas em grupo, cria um registro para cada par falante-ouvinte
- Gera o arquivo `datasets/interacoes.csv`

### Arquivo de saída
`datasets/interacoes.csv` com as colunas:
- **NTemporada**: Número da temporada
- **NEpisodio**: Número do episódio
- **NCena**: Número da cena
- **falante**: Personagem que fala
- **ouvinte**: Personagem que ouve
- **fala**: Texto da fala
- **tamanho_fala**: Número de caracteres da fala
- **descricao_cena**: Descrição da cena (primeiros 200 caracteres)
- **num_personagens_cena**: Quantidade de personagens na cena
- **tipo_interacao**: `single` (2 personagens) ou `group` (3+ personagens)
