import subprocess
import sys

scripts = [
    '01_extrair_personagens.py',
    '02_identificar_duplicados.py',
    '03_extrair_interacoes.py'
]

print('=== PIPELINE GOT - Análise de Personagens e Interações ===\n')

for i, script in enumerate(scripts, 1):
    print(f'[{i}/{len(scripts)}] Executando {script}...')
    result = subprocess.run([sys.executable, f'src/{script}'], cwd='.')
    
    if result.returncode != 0:
        print(f'\n❌ ERRO ao executar {script}')
        sys.exit(1)
    
    print(f'✓ {script} concluído\n')

print('=== Pipeline concluído com sucesso! ===')
