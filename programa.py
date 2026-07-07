import sys
import os
from arvore_b import (
    criar_indice_b, buscar, inserir,
    ler_pagina, ler_cabecalho, proximo_rrn
)
from pagina import NULO

CAMINHO_DADOS  = "games.dat"
CAMINHO_ARVORE = "btree.dat"

# -b  Criação do índice
def opcao_criar():
    if not os.path.exists(CAMINHO_DADOS):
        print(f"Erro: arquivo '{CAMINHO_DADOS}' não encontrado.")
        return

    print("Iniciando criação do índice...")
    sucesso = criar_indice_b(CAMINHO_DADOS, CAMINHO_ARVORE)

    if sucesso:
        print("Índice criado com sucesso!")
    else:
        print("Erro: não foi possível criar o índice.")

# -e  Execução do arquivo de operações
def opcao_executar(nome_arquivo_operacao):
    for caminho in (CAMINHO_DADOS, CAMINHO_ARVORE):
        if not os.path.exists(caminho):
            print(f"Erro: arquivo '{caminho}' não encontrado.")
            return

    if not os.path.exists(nome_arquivo_operacao):
        print(f"Erro: arquivo de operações '{nome_arquivo_operacao}' não encontrado.")
        return

    with open(nome_arquivo_operacao, 'r', encoding='utf-8') as arq_operacoes:
        arqDados = open(CAMINHO_DADOS, 'r+b')
        arqArvb = open(CAMINHO_ARVORE, 'r+b')

        for linha in arq_operacoes:
            linha = linha.strip()
            if not linha:
                continue

            partes_operacoes = linha.split(' ', 1)
            if len(partes_operacoes) < 2:
                continue

            operacao = partes_operacoes[0].lower()
            argumento = partes_operacoes[1].strip()

            if operacao == 'b':
                executar_busca(arqArvb, arqDados, argumento)
            elif operacao == 'i':
                executar_insercao(arqArvb, arqDados, argumento)

            print()

        arqDados.close()
        arqArvb.close()

    print(f'As operações do arquivo "{nome_arquivo_operacao}" foram executadas com sucesso!')

def executar_busca(arqArvb, arqDados, chave_str):
    chave = int(chave_str)
    print(f'Busca pelo registro de chave "{chave}"')

    offset_dado = buscar(arqArvb, chave)

    if offset_dado == NULO:
        print(f'Erro: chave "{chave}" não encontrada')
    else:
        # Pula para a posição correta, lê os 2 bytes do tamanho e depois a string
        arqDados.seek(offset_dado)
        tamanho_bytes = arqDados.read(2)
        tamanho = int.from_bytes(tamanho_bytes, 'little')

        registro_bytes = arqDados.read(tamanho)
        registro_str = registro_bytes.decode('utf-8', errors='replace')

        print(f'{registro_str} ({tamanho} bytes - offset {offset_dado})')

def executar_insercao(arqArvb, arqDados, registro_str):
    partes = registro_str.split('|')
    chave  = int(partes[0])
    print(f'Inserção do registro de chave "{chave}"')

    if buscar(arqArvb, chave) != NULO:
        print(f'Erro: chave "{chave}" duplicada')
        return

    # Escreve no fim do arquivo games.dat
    arqDados.seek(0, 2)
    offset_dado = arqDados.tell()

    registro_bytes = registro_str.encode('utf-8')
    tamanho = len(registro_bytes)

    # Grava os 2 bytes indicando o tamanho, seguido da string
    arqDados.write(tamanho.to_bytes(2, 'little'))
    arqDados.write(registro_bytes)

    inserir(arqArvb, chave, offset_dado)

    print(f'{registro_str} ({tamanho} bytes - offset {offset_dado})')

# -p  Impressão da árvore-B
def formatar_lista(nome, lista):
    resultado = f'{nome} = '
    tamanho = len(lista)

    for i in range(tamanho):
        resultado += str(lista[i])

        if i < tamanho - 1:
            resultado += ' | '

    return resultado

def opcao_imprimir():
    if not os.path.exists(CAMINHO_ARVORE):
        print(f"Erro: arquivo '{CAMINHO_ARVORE}' não encontrado.")
        return

    with open(CAMINHO_ARVORE, 'rb') as arqArvb:
        rrn_raiz = ler_cabecalho(arqArvb)
        total_pags = proximo_rrn(arqArvb)

        for rrn in range(total_pags):
            pag = ler_pagina(arqArvb, rrn)

            if rrn == rrn_raiz:
                print('- ' * 20 + 'Raiz ' + '- ' * 20)

            print(f'Página {rrn}:')
            print(formatar_lista('Chaves ', pag.chaves))
            print(formatar_lista('Offsets', pag.offsets))
            print(formatar_lista('Filhos ', pag.filhos))

            if rrn == rrn_raiz:
                print('- ' * 45)

            print()

# Main
def main():
    if len(sys.argv) < 2:
        print("Uso: python programa.py -b | -e <arquivo_ops> | -p")
        return

    flag = sys.argv[1]

    if flag == '-b':
        opcao_criar()
    elif flag == '-e':
        if len(sys.argv) < 3:
            print("Erro: informe o arquivo de operações. Ex: python programa.py -e operacoes.txt")
            return
        opcao_executar(sys.argv[2])
    elif flag == '-p':
        opcao_imprimir()
    else:
        print(f"Erro: flag desconhecida '{flag}'. Use -b, -e ou -p.")

if __name__ == '__main__':
    main()
