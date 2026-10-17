"""Plano da etapa 13: as 48 linhas de animais trocados (rc.1) com o visual/nome
da etapa 12, corrigidos pelas revisoes 01/02/03.

linha: (modelo, nome, motivo da mudanca em relacao a etapa 12 ou None)
  modelo = linha de enemy_param cujo .chr/paleta/tamanho/sombra e usado
  (a paleta final e sempre uma paleta NOVA so desta linha; ver build.py).

As linhas 1-4 (variantes originais de Saibaman: J./C./K./T. Sai) NAO estao
aqui: voltam exatamente aos valores da rc.1 (= jogo original).

Pesos atk1-atk4: NAO vem do modelo. Sao os do jogo original para a propria
linha (o efeito de cada golpe esta em btl/ene/eneEff.bin, por linha, e nao
no sprite). So quando o sprite doador nao tem a animacao de um slot usado o
peso desse slot e redistribuido (regra em build.py, documentada no relatorio).
"""

PLANO13 = {
 74: (11, 'Mecha Patrulheiro', None),
 75: (12, 'Mecha de Combate', None),
 76: (71, 'Lanceiro Nômade', 'nome repetido ("Errante") e paleta clone do Homem Desconfiado (dist. 1)'),
 80: (56, 'Lutador Errante', None),
 81: (60, 'Guarda da Mansão', None),
 82: (167, 'Robô Sentinela', 'Castelo do Pilaf: era "Corsária Venenosa" (pirata, confundido com a Caverna)'),
 95: (32, 'Batedor do Ermo', None),
 96: (39, 'Batedora do Deserto', None),
 97: (34, 'Mercenário de Elite', None),
 98: (8, 'Piloto Renegado', None),
 99: (9, 'Piloto Mercenário', None),
 100: (10, 'Piloto Veterano', None),
 101: (56, 'Arruaceiro do Bambu', None),
 102: (27, 'Mercenário da Neve', None),
 103: (69, 'Guardião da Floresta', None),
 104: (32, 'Atirador da Montanha', None),
 105: (24, 'Guerreira do Gelo', 'nome repetido ("Errante")'),
 106: (34, 'Atirador Veterano', None),
 107: (14, 'Ex-Soldado RR', 'quase igual a "Desertor da RR" (linha 14)'),
 108: (15, 'Espião Red Ribbon', None),
 109: (42, 'Guarda do Castelo', 'Castelo do Pilaf: era "Sentinela Pirata" (sprite de corsária); guarda de turbante, como o castelo de estilo árabe'),
 110: (26, 'Brutamontes do Ermo', 'sprite do Fugitivo (golpe 3 = animação de chamar reforço) trocado pelo do Bandido'),
 111: (57, 'Lutador Veterano', None),
 112: (27, 'Brutamontes Glacial', 'sprite do Fugitivo trocado pelo do Bandido da Neve; slot 3 tinha 35% sem golpe definido'),
 113: (63, 'Saqueador do Ermo', None),
 114: (25, 'Bandida Glacial', None),
 115: (58, 'Instrutor Rival', 'nome repetido ("Errante"; e "Mestre" já existe no mesmo mapa)'),
 116: (53, 'Discípulo Rebelde', 'quase igual a "Aluno Expulso" (linha 54)'),
 117: (70, 'Guardião Peregrino', None),
 118: (28, 'Capitão da Guarda', 'Castelo do Pilaf: era "Corsária Veterana" (pirata); brutamontes de espada'),
 119: (5, 'Robô Mergulhador', 'nome repetido ("Patrulheiro" / "de Patrulha")'),
 120: (6, 'Robô da Caverna', None),
 121: (7, 'Robô das Areias', None),
 131: (125, 'Vampiro Jovem', 'nome repetido ("Errante")'),
 132: (126, 'Vampiro Sanguinário', None),
 133: (127, 'Vampiro Ancião', None),
 134: (44, 'Capanga da Caverna', None),
 135: (45, 'Capanga da Fonte', None),
 136: (46, 'Capanga Sombrio', None),
 149: (42, 'Ladrão do Deserto', 'sprite de 6 animações não tem o golpe 4 (20% no original); doador com 7 animações'),
 150: (70, 'Xamã do Vulcão', 'sprite de 6 animações não tem o golpe 4 (20%, o mais forte); doador com 7 animações'),
 151: (50, 'Aprendiz da Floresta', None),
 155: (62, 'Batedor Escavador', None),
 156: (54, 'Lutador Noturno', None),
 157: (33, 'Batedor Venenoso', None),
 161: (23, 'Recruta Escavadora', 'gênero: sprite feminino (Bandida)'),
 162: (51, 'Aprendiz Noturna', 'gênero: sprite feminino (Aluna)'),
 163: (40, 'Batedora Venenosa', None),
}

# Linhas que voltam a rc.1 (variantes originais de Saibaman, canonicas no cap. 14)
REVERTIDAS = (1, 2, 3, 4)

# Tom sugerido pelo nome (so usado ao gerar a paleta nova): (matiz em graus ou None, brilho)
# gelo/neve = azul-claro, fogo = vermelho-alaranjado, veneno = roxo, noturno/sombrio = escuro.
TEMAS = {
 105: (195, 1.0), 112: (200, 1.0), 114: (210, 1.0),
 150: (15, 1.0),
 157: (285, 1.0), 163: (290, 1.0),
 156: (230, 0.72), 162: (235, 0.72), 136: (None, 0.72),
}
