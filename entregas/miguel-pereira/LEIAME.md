# Miguel Pereira: vlog da viagem (82,8 s, 1920×1080, 30 fps)

Edição dos vídeos da pasta do Drive, seguindo o estilo do `MODELO.mov`:
selfie falando → título amarelo "MIGUEL PEREIRA" digitando letra a letra sobre cortes-relâmpago → montagem no ritmo da música → volta à fala no final.

## Arquivos

| Arquivo | O que é |
|---|---|
| `Miguel_Pereira_viagem.mp4` | Vídeo final (H.264 + AAC, -14,7 LUFS) |
| `Miguel_Pereira_timeline.fcpxml` | Timeline para o DaVinci Resolve (FCPXML 1.9) |
| `titulo_MIGUEL_PEREIRA_alpha.mov` | Título com fundo transparente (usado pela timeline) |
| `trilha_musica.wav` | Trilha instrumental já com os "ducks" nas falas (usada pela timeline) |
| `scripts/` | Scripts que geraram o corte (EDL, render, mixagem, título, FCPXML) |

## Estrutura do corte

| Tempo | Trecho |
|---|---|
| 0:00 | Abertura: "Ah, perdão, é que eu esqueço que eu tô repleta de amigas" |
| 0:04 | Título MIGUEL PEREIRA digitando sobre 12 flashes de 0,2 s |
| 0:09 | Sábado: mercado, chegada, piscina (pulos + risadas) |
| 0:30 | Noite no quarto: "Esquece! Eu não quero mais morrer!", "Ai, cheirou" (risadas), violão |
| 0:41 | **Cozinhando**: hambúrguer, "Calma, gente, tô estudando o processo", "A faca tá tremendo ou você tá tremendo?", salada, risadas na cozinha |
| 0:57 | Domingo: trilha, ponte, parque dos dinossauros, pulo na piscina na chuva, noite |
| 1:13 | Segunda: o muro, a despedida |
| 1:17 | Fecho na cozinha: "A gente não mostra… mas olha como a gente trabalha bem" |

## Abrir no DaVinci Resolve

1. Baixe os vídeos originais da pasta do Drive para uma pasta chamada `MIDIA`.
2. Coloque `Miguel_Pereira_timeline.fcpxml`, `titulo_MIGUEL_PEREIRA_alpha.mov` e `trilha_musica.wav` na pasta que contém `MIDIA`.
3. No Resolve: **File → Import → Timeline…**, escolha o `.fcpxml`. Se ele pedir a mídia, aponte para a pasta `MIDIA`.

Notas sobre a timeline:
- Os clipes com nome UUID (ex.: `4A409023-….mov`) foram gravados de lado sem metadado de rotação. Na timeline eles vão com rotação de 90° e escala de 1,778. Se algum aparecer torto, ajuste em Inspector → Transform.
- Os clipes verticais vão centralizados com barras laterais. No MP4 eles têm fundo desfocado. No Resolve dá para refazer isso com uma cópia do clipe por baixo, ampliada e com blur.
- A trilha fica na faixa de áudio da música, e o volume do som direto já vem ajustado por clipe. A trilha é instrumental gerada para este vídeo, sem direitos de terceiros, e pode ser trocada por outra música.
- O color (leve dessaturação, tom quente e vinheta suave) só está no MP4. A timeline vem sem grade.
