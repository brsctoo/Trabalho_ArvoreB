from pagina import Pagina, NULO, ORDEM, TAMANHO_CABECALHO, TAMANHO_INT

# numChaves + chaves + offsets + filhos
TAMANHO_PAGINA = TAMANHO_INT + (ORDEM - 1) * TAMANHO_INT + TAMANHO_INT * (ORDEM - 1) + ORDEM * TAMANHO_INT

def calcular_byte_offset(rrn: int) -> int:
    """Calcula o byte-offset da página no arquivo btree.dat a partir do RRN."""
    return TAMANHO_CABECALHO + (rrn * TAMANHO_PAGINA)

def ler_pagina(arqArvb, rrn: int) -> Pagina:
    """Lê a página do arquivo a partir de um RRN."""
    offset = calcular_byte_offset(rrn)
    arqArvb.seek(offset)

    dados = arqArvb.read(TAMANHO_PAGINA)
    pag = Pagina()
    if dados:
        pag.desampacotar(dados)
    return pag

def escrever_pagina(rrn: int, pag: Pagina, arqArvb):
    """Escreve a página no arquivo no RRN correspondente."""
    offset = calcular_byte_offset(rrn)
    arqArvb.seek(offset)
    arqArvb.write(pag.empacotar())

def proximo_rrn(arqArvb) -> int:
    """Calcula o RRN da nova página."""
    arqArvb.seek(0, 2)
    offset_atual = arqArvb.tell()
    return (offset_atual - TAMANHO_CABECALHO) // TAMANHO_PAGINA

def ler_cabecalho(arquivo) -> int:
    """Lê a posição da raiz armazenada nos primeiros 4 bytes do arquivo."""
    arquivo.seek(0)
    dados = arquivo.read(TAMANHO_CABECALHO)
    if not dados:
        return 0
    return int.from_bytes(dados, 'little', signed=True)

def escrever_cabecalho(arquivo, raiz: int):
    """Escreve a posição da raiz nos primeiros 4 bytes do arquivo."""
    arquivo.seek(0)
    dados = raiz.to_bytes(TAMANHO_CABECALHO, 'little', signed=True)
    arquivo.write(dados)

def buscaNaPagina(chave: int, pag: Pagina) -> tuple:
    """Busca uma chave dentro de uma única página."""
    pos = 0
    while pos < pag.numChaves and chave > pag.chaves[pos]:
        pos += 1

    if pos < pag.numChaves and chave == pag.chaves[pos]:
        return True, pos
    else:
        return False, pos

def buscaNaArvore(chave: int, rrn: int, arqArvb) -> tuple:
    """Busca recursivamente uma chave na Árvore-B."""
    if rrn == NULO:
        return False, NULO, NULO

    pag = ler_pagina(arqArvb, rrn)
    achou, pos = buscaNaPagina(chave, pag)

    if achou:
        return True, rrn, pos
    else:
        return buscaNaArvore(chave, pag.filhos[pos], arqArvb)

def buscar(arqArvb, chave: int) -> int:
    """
    Função chamada pelo main.py.
    Retorna o byte-offset da chave caso encontrada, ou NULO se não existir.
    """
    raiz = ler_cabecalho(arqArvb)
    achou, rrn, pos = buscaNaArvore(chave, raiz, arqArvb)
    if achou:
        pag = ler_pagina(arqArvb, rrn)
        return pag.offsets[pos]
    return NULO

def insereChavePromo(chave: int, offset: int, filhoD: int, pag: Pagina):
    """Insere chave, OFFSET e filho direito na página."""
    if pag.esta_cheia():
        pag.chaves.append(NULO)
        pag.offsets.append(NULO)
        pag.filhos.append(NULO)

    i = pag.numChaves

    while i > 0 and chave < pag.chaves[i - 1]:
        pag.chaves[i] = pag.chaves[i - 1]
        pag.offsets[i] = pag.offsets[i - 1]
        pag.filhos[i + 1] = pag.filhos[i]
        i -= 1

    pag.chaves[i] = chave
    pag.offsets[i] = offset
    pag.filhos[i + 1] = filhoD
    pag.numChaves += 1

def divide(chave: int, offset: int, filhoD: int, pag: Pagina, arqArvb):
    """Divide a página cheia e retorna a chave, offset e o filho que serão promovidos."""
    insereChavePromo(chave, offset, filhoD, pag)

    meio = ORDEM // 2
    chavePro = pag.chaves[meio]
    offsetPro = pag.offsets[meio]

    filhoDpro = proximo_rrn(arqArvb)
    pNova = Pagina()

    j = 0
    for i in range(meio + 1, pag.numChaves):
        pNova.chaves[j] = pag.chaves[i]
        pNova.offsets[j] = pag.offsets[i]
        pNova.filhos[j + 1] = pag.filhos[i + 1]
        j += 1

    pNova.numChaves = j
    pNova.filhos[0] = pag.filhos[meio + 1]

    # Atualiza a página que foi dividida
    pag.numChaves = meio
    pag.chaves = pag.chaves[:meio] + [NULO] * (ORDEM - 1 - meio)
    pag.offsets = pag.offsets[:meio] + [NULO] * (ORDEM - 1 - meio)
    pag.filhos = pag.filhos[:meio + 1] + [NULO] * (ORDEM - (meio + 1))

    return chavePro, offsetPro, filhoDpro, pag, pNova

def insereChave(chave: int, offset: int, rrnAtual: int, arqArvb) -> tuple:
    """Desce recursivamente. Retorna: (chavePro, offsetPro, filhoDpro, promo)"""
    if rrnAtual == NULO:
        return chave, offset, NULO, True

    pag = ler_pagina(arqArvb, rrnAtual)
    achou, pos = buscaNaPagina(chave, pag)

    if achou:
        raise ValueError("Chave duplicada")

    chavePro, offsetPro, filhoDpro, promo = insereChave(chave, offset, pag.filhos[pos], arqArvb)

    if not promo:
        return NULO, NULO, NULO, False
    else:
        if not pag.esta_cheia():
            insereChavePromo(chavePro, offsetPro, filhoDpro, pag)
            escrever_pagina(rrnAtual, pag, arqArvb)
            return NULO, NULO, NULO, False
        else:
            nova_chave, novo_offset, novo_filhoD, pag, novaPag = divide(chavePro, offsetPro, filhoDpro, pag, arqArvb)
            escrever_pagina(rrnAtual, pag, arqArvb)
            escrever_pagina(novo_filhoD, novaPag, arqArvb)
            return nova_chave, novo_offset, novo_filhoD, True

def insereNaArvore(chave: int, offset: int, raiz: int, arqArvb) -> int:
    """Crescimento da árvore criando nova raiz se necessário."""
    chavePro, offsetPro, filhoDireitoPro, promo = insereChave(chave, offset, raiz, arqArvb)

    if promo:
        pagNova = Pagina()
        pagNova.chaves[0] = chavePro
        pagNova.offsets[0] = offsetPro
        pagNova.filhos[0] = raiz
        pagNova.filhos[1] = filhoDireitoPro
        pagNova.numChaves += 1

        raiz_nova = proximo_rrn(arqArvb)
        escrever_pagina(raiz_nova, pagNova, arqArvb)
        return raiz_nova

    return raiz

def inserir(arqArvb, chave: int, offset: int):
    """Função chamada pelo main.py para inserir uma chave na árvore."""
    raiz = ler_cabecalho(arqArvb)
    nova_raiz = insereNaArvore(chave, offset, raiz, arqArvb)
    escrever_cabecalho(arqArvb, nova_raiz)

def criar_indice_b(caminho_dados, caminho_arvore) -> bool:
    """Lê o arquivo de dados completo e cria a árvore."""
    try:
        with open(caminho_arvore, 'w+b') as arqArvb:
            raiz = 0
            escrever_cabecalho(arqArvb, raiz)

            pag = Pagina()
            escrever_pagina(0, pag, arqArvb)

            with open(caminho_dados, 'rb') as dados:
                while True:
                    offset = dados.tell()
                    tamanho_bytes = dados.read(2)
                    if not tamanho_bytes or len(tamanho_bytes) < 2:
                        break

                    tamanho = int.from_bytes(tamanho_bytes, 'little')

                    # Lê o tamanho do registro
                    linha_bytes = dados.read(tamanho)

                    # Decodifica
                    linha_str = linha_bytes.decode('utf-8', errors='replace').strip()
                    if not linha_str:
                        continue

                    # Extrai a chave
                    partes = linha_str.split('|')
                    chave = int(partes[0])

                    try:
                        raiz = insereNaArvore(chave, offset, raiz, arqArvb)
                    except ValueError:
                        pass

            escrever_cabecalho(arqArvb, raiz)

        return True
    except Exception as e:
        print(f"Erro na criação do índice: {e}")
        return False
