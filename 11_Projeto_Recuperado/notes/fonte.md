# Fonte do jogo: já tem acentos

Arquivos na raiz do cartucho: `latin0.fnt` (grande) e `latin1.fnt` (pequena).
Script: `scripts/ver_fonte.py` (desenha os 256 glifos)

## Formato

| Arquivo | Tamanho | Glifo | Bytes/glifo |
|---|---|---|---|
| `latin0.fnt` | 4.096 | 10×12 px, 1 bit/pixel, MSB primeiro | 15 |
| `latin1.fnt` | 2.816 | 8×10 px, 1 bit/pixel, MSB primeiro | 10 |

- Bytes 0–255: largura de avanço de cada caractere (proporcional; espaço = 3)
- Depois: 256 glifos seguidos, indexados pelo código do caractere
- Codificação: **Windows-1252 / Latin-1**. Os códigos que não existem no
  1252 (0x81, 0x8D…) têm um glifo de listras (placeholder).

## Cobertura

As duas fontes têm tudo o que o português precisa:
á à â ã é ê í ó ô õ ú ü ç e as maiúsculas Á À Â Ã É Ê Í Ó Ô Õ Ú Ç, além de
ª º « » ¿ ¡ € ™ © ®.

## Teste no jogo

Nome de inimigo gravado como "Ação Espião Robô Çé" (bytes Latin-1 via
`bdat_strings.gravar_str`): aparece certo na etiqueta de alvo da batalha
(`saida/acento/zoom.png`). O motor de texto aceita bytes ≥ 0x80 como
caractere.

## Consequência

- **Nenhum trabalho de fonte** é necessário para a tradução PT-BR.
- O "sem acento" do hack dos bichos era só cautela. Os nomes voltaram a
  ter acento (Espião, Campeão, Robô, Ártico, Mansão…).
- Ainda falta ver se as caixas de diálogo (scripts `.sb`) usam a mesma
  fonte e aceitam os mesmos bytes. A etiqueta de batalha vem das tabelas.
