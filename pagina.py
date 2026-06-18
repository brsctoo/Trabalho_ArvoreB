# Constante global
ORDEM = 5
NULO = -1

TAMANHO_CABECALHO = 4 # Tamanho do cabeçalho
TAMANHO_INT = 4 # Usaremos 4 bytes para representar cada inteiro
FORMATO = f'i {ORDEM-1}i {ORDEM-1}i {ORDEM}i'

class Pagina:
  def __init__(self) -> None:
    self.numChaves = 0
    self.chaves = [NULO] * (ORDEM-1)
    self.offsets = [NULO] * (ORDEM - 1)
    self.filhos = [NULO] * ORDEM

  def eh_folha(self) -> bool:
    return self.filhos[0] == NULO

  def esta_cheia(self) -> bool:
    return self.numChaves == ORDEM - 1

  def empacotar(self) -> bytes:
    """Transforma a página em bytes usando uma lista normal."""
    partes_bytes = [] # Uma lista comum do Python

    # 1. Guarda o numChaves
    partes_bytes.append(self.numChaves.to_bytes(TAMANHO_INT, 'little', signed=True))

    # 2. Guarda todas as chaves
    for chave in self.chaves:
        partes_bytes.append(chave.to_bytes(TAMANHO_INT, 'little', signed=True))

    # 3. Guarda todos os offsets
    for offset in self.offsets:
        partes_bytes.append(offset.to_bytes(TAMANHO_INT, 'little', signed=True))

    # 4. Guarda todos os filhos
    for filho in self.filhos:
        partes_bytes.append(filho.to_bytes(TAMANHO_INT, 'little', signed=True))

    # O b''.join() pega a lista de pedaços e "cola" tudo em uma coisa só
    return b''.join(partes_bytes)

  def desampacotar(self, dados_binarios: bytes) -> None:
    """Reconstrói a página"""
    pos = 0

    # 1. Recupera o numChaves
    fatia = dados_binarios[pos : pos + TAMANHO_INT]
    self.numChaves = int.from_bytes(fatia, 'little', signed=True)
    pos += TAMANHO_INT

    # 2. Recupera as chaves
    for i in range(ORDEM - 1):
        fatia = dados_binarios[pos : pos + TAMANHO_INT]
        self.chaves[i] = int.from_bytes(fatia, 'little', signed=True)
        pos += TAMANHO_INT

    # 3. Recupera os offsets
    for i in range(ORDEM - 1):
        fatia = dados_binarios[pos : pos + TAMANHO_INT]
        self.offsets[i] = int.from_bytes(fatia, 'little', signed=True)
        pos += TAMANHO_INT

    # 4. Recupera os filhos
    for i in range(ORDEM):
        fatia = dados_binarios[pos : pos + TAMANHO_INT]
        self.filhos[i] = int.from_bytes(fatia, 'little', signed=True)
        pos += TAMANHO_INT
