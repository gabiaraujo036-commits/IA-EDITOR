# Reels – Feirão Black em cartas (IPVA 2027 pago)

25 s · 1080×1920 · 30 fps. Visual: preto predominante, detalhes em vermelho e moldura dourada. Seis carros do estoque viram cartas de jogo que deslizam para o lado,
com um "dedo" mostrando a escolha. No fim aparece o leque com as 6 cartas e a chamada
"Escolheu a sua? Leva com IPVA 2027 pago! Chama no direct".
Sem locução: só a batida, o whoosh de cada carta e um impacto no final.

- `reels-feirao-black-cartas.mp4`: o vídeo final
- `capa.png`: capa (tela final)
- `cartas/`: cada carta em PNG, para usar nos stories
- Refazer: `python3 trilha.py trilha.wav` e `python3 cartas.py <pasta com 1.webp..6.webp> <saída>`;
  depois juntar o vídeo com a trilha no ffmpeg. Os carros ficam na lista `CARROS` do `cartas.py`.

## Legenda sugerida
🃏 FEIRÃO BLACK MARIO CAR: qual carta é a sua? 🃏
C4 Cactus, Nivus, Aircross 7 lugares, Duster, Oroch ou Elantra. Escolheu? Leva com o IPVA 2027 PAGO! 🚗💨
É a última semana, corre! Chama no direct.
*Consulte condições na loja.
#FeirãoBlack #MarioCar #IPVA2027 #Seminovos #CarroNovo
## Versões
- `reels-feirao-black-cartas-v2.mp4` (atual): carta estilo vitrine (foto grande sem deformar, nome à esquerda,
  fita diagonal "IPVA 2027 PAGO"), preto com detalhes em vermelho, sem dourado. Capa: `capa-v2.png`.
- `reels-feirao-black-cartas-sem-dourado.mp4` e `reels-feirao-black-cartas.mp4`: versões anteriores.
- `cartas.py` gera a v2 por padrão (`--dourado` volta as cores com dourado no fundo).
- Post estático: `post-feed.png` (1080×1350) e `post-story.png` (1080×1920), gerados por `python3 post.py` a partir das cartas.
