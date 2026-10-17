# Revisão de coerência — DBZ Attack of the Saiyans NDS

Revisão local concluída em 11/10/2026. ROM candidata pronta para teste jogável.

## O que foi corrigido

Mantida a substituição dos 48 animais do projeto. Foram revistos os modelos, nomes e paletas para evitar a presença antecipada de Saiyajins e Saibamans nessas entradas. A abertura do Kuririn usa agora adversários terrestres, como Arruaceiro do Bambu, Lutador Errante e Discípulo Expulso. Outras áreas usam mercenários, corsários, robôs, lutadores e guardiões conforme os mapas em que cada entrada aparece.

A auditoria encontrou também quatro variantes de Saibaman da própria base original em conjuntos de encontros anteriores ao momento pretendido. Essas quatro entradas receberam substitutos terrestres, totalizando 52 entradas revisadas. O Saibaman básico foi preservado.

As entradas compartilhadas por diversos mapas receberam nomes genéricos, evitando atribuir filiações ou identidades específicas sem apoio na história. A lista completa de mudanças, mapas e motivos está em revisao_inimigos.csv e revisao_inimigos.json.

## Verificações realizadas

- 2.143 grupos de encontros em 183 arquivos de mapas conferidos.
- Comparação das tabelas: somente os campos permitidos de apresentação/modelo e nomes foram alterados. Ajustados também os campos atk1–atk4 usados pela apresentação do modelo. Atributos numéricos de combate, recompensas e resistências preservados.
- Arquivos de roteiro e código ARM9 idênticos à base; alterações limitadas a 21 arquivos de sprites/paletas e seis tabelas de idiomas.
- Sprites e animações dos modelos reaproveitados, com paletas acrescentadas; renderização dos 21 modelos conferida.
- Checagem de largura dos nomes e de conflitos de nome/aparência nos grupos de encontros.
- Dois patches BPS gerados e reaplicados: ambos reproduzem exatamente a ROM candidata.

## Limites e teste necessário

Esta é uma revisão das entradas de inimigos e dos encontros decodificados, não uma validação completa da campanha jogando. A conservação dos roteiros não garante, sozinha, que uma entrada compartilhada não afete a apresentação de uma batalha de evento. As quatro variantes originais foram alteradas globalmente; isso deve ser observado também nos encontros posteriores da saga Saiyajin. O Saibaman básico permanece disponível.

Testar prioritariamente: abertura do Kuririn e saída do templo, floresta de bambu, Monte Paozu, caverna dos piratas, áreas de Enma e batalhas posteriores com Nappa. Conferir nomes, posições, animações, transições e adequação dos adversários ao diálogo. IDs compartilhados podem exigir uma segunda revisão por encontro para diferenciação mais específica entre fases.

## Arquivos para uso

ROM candidata: DBZ Attack of the Saiyans PT-BR Coerencia.nds
SHA256: 130b4ad843d85d760c4e844de26c35021bde0b43b6c5f34d6c3c639b2f5a9edd

Patch incremental: Coerencia_sobre_PTBR_1.0.0-rc.1.bps
Exige a ROM modificada anterior com SHA256 41412a4727328d5341ba2f7d17fa567c84db137d8cd082bc32389c6d27643a5f.

Patch completo: DBZ_PTBR_Coerencia_completo.bps
Exige a base original aots.nds recuperada no backup, CRC32 a9f0b8f9.

A ROM principal anterior, os saves e o cartão do Switch não foram sobrescritos por esta revisão. Para testar no atalho existente, fazer backup da ROM do cartão e colocar a candidata no mesmo caminho e com o mesmo nome da ROM anterior, preservando o arquivo .sav. Evitar salvar durante a primeira conferência até confirmar o carregamento do progresso correto.
