# IA-EDITOR
EDITOR DE VIDEOS MARIO CAR

Nossa forma de recriar trends virais com IA: **copiar a estrutura, não o vídeo**.

```
vídeo de referência ─► analisar ─► receita.json ─► (você escreve os prompts) ─► montar ─► final.mp4
                         cortes, tempos,             sujeito, ação, câmera       IA gera cada cena
                         quadro de cada cena                                    no tempo exato + áudio
```

## Uso

```bash
pip install -r requirements.txt

# 1. Extrai as cenas e os tempos da trend
python -m ia_editor analisar trend.mp4 saida/minha-trend

# 2. Edite saida/minha-trend/receita.json:
#    - "prompt" de cada cena (sujeito, ação, movimento de câmera)
#    - "imagem_inicial": foto SUA (ou do cliente) para a IA animar
#    - "estilo_global" e "modelo"

# 3. Teste o ritmo de graça (sem IA, só zoom nos quadros)
python -m ia_editor montar saida/minha-trend --provedor rascunho

# 4. Gera de verdade com IA (fal.ai hospeda Kling, Veo, Wan, Seedance, Hailuo...)
export FAL_KEY=sua_chave
python -m ia_editor montar saida/minha-trend --provedor fal
```

Cenas já geradas (`gerado_XX.mp4`) não são refeitas; apague uma para regerar só ela.
Por padrão o áudio original da referência é reaproveitado (`--sem-audio` para desligar).

## Receitas prontas

- `receitas/danca-whip-pan-reacao.json` — dança em grande-angular → whip pan → selfie → push-in para close de reação.

## Dicas de câmera para os prompts

- **whip pan**: "ends with a fast whip pan to the right with motion blur"
- **push-in**: "camera pushes in fast to an extreme close-up"
- **grande-angular de celular**: "ultra wide 0.5x lens, low angle, handheld"
