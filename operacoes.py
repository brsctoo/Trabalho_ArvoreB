import os
from pagina import Pagina, NULO, ORDEM, TAMANHO_CABECALHO, TAMANHO_INT

# numChaves + chaves + offset + filhos
TAMANHO_PAGINA = TAMANHO_INT + ((ORDEM - 1) * TAMANHO_INT) + ((ORDEM - 1) * TAMANHO_INT) + (ORDEM * TAMANHO_INT)

def ler_pagina_do_disco(arquivo, rrn: int) -> Pagina:
  """
  Função auxiliar para ir até a posição correta no arquivo,
  ler os bytes e reconstruir a Pagina
  """

  posicao_byte = TAMANHO_CABECALHO + (rrn * TAMANHO_PAGINA)
  arquivo.seek(posicao_byte)
  dados_binario = arquivo.read(TAMANHO_PAGINA)

  paginaDados = Pagina()
  paginaDados.desampacotar(dados_binario)
  return paginaDados

def busca_na_pagina(chave: int, pagina: Pagina):
  """
  Busca sequencial dentro das chaves de uma página carregada na memória.
  """

  pos = 0

  while pos < pagina.numChaves and chave > pagina.chaves[pos]:
    pos += 1

  if pos < pagina.numChaves and chave == pagina.chaves[pos]:
    return (True, pos)
  else:
    return (False, pos)

def busca_na_arvore(chave: int, rrn: int, arquivo):
  """
  Busca recursiva pelas páginas no disco.
  """

  if rrn == NULO:
    return (False, NULO, NULO)

  pagina = ler_pagina_do_disco(arquivo, rrn)
  (achou, pos) = busca_na_pagina(chave, pagina)

  if achou:
      return (True, rrn, pos)
  else:
      rrn_filho = pagina.filhos[pos]
      return busca_na_arvore(chave, rrn_filho, arquivo)
