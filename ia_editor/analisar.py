"""Etapa 1: analisa um vídeo de referência e gera uma receita (JSON).

A receita guarda a *estrutura* do vídeo viral: duração de cada cena,
onde estão os cortes e um quadro-chave de cada cena. Depois você
descreve cada cena com um prompt e a IA gera o seu próprio vídeo
seguindo o mesmo ritmo.
"""
import json
import re
from pathlib import Path

from . import ff


def _info(video: Path) -> dict:
    log = ff.run(["-i", str(video), "-f", "null", "-t", "0", "-"])
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", log)
    res = re.search(r"Video: .*?, (\d{2,5})x(\d{2,5})", log)
    fps = re.search(r"([\d.]+) fps", log)
    h, m, s = dur.groups()
    return {
        "duracao": round(int(h) * 3600 + int(m) * 60 + float(s), 3),
        "largura": int(res.group(1)),
        "altura": int(res.group(2)),
        "fps": float(fps.group(1)) if fps else 30.0,
        "tem_audio": "Audio:" in log,
    }


def _cortes(video: Path, limiar: float) -> list[float]:
    log = ff.run([
        "-i", str(video),
        "-vf", f"select='gt(scene,{limiar})',showinfo",
        "-f", "null", "-",
    ])
    return [float(t) for t in re.findall(r"pts_time:([\d.]+)", log)]


def analisar(video: Path, saida: Path, limiar: float = 0.25, cena_min: float = 0.8) -> dict:
    saida.mkdir(parents=True, exist_ok=True)
    info = _info(video)

    # Junta cortes muito próximos (transições tipo whip pan geram vários).
    pontos = [0.0]
    for t in _cortes(video, limiar):
        if t - pontos[-1] >= cena_min and info["duracao"] - t >= cena_min:
            pontos.append(round(t, 3))
    pontos.append(info["duracao"])

    cenas = []
    for i, (ini, fim) in enumerate(zip(pontos, pontos[1:]), start=1):
        quadro = saida / f"cena_{i:02d}.jpg"
        ff.run(["-ss", str((ini + fim) / 2), "-i", str(video), "-frames:v", "1", str(quadro)])
        cenas.append({
            "id": i,
            "inicio": ini,
            "fim": fim,
            "duracao": round(fim - ini, 3),
            "quadro_referencia": quadro.name,
            "imagem_inicial": None,
            "prompt": "DESCREVA A CENA: sujeito, ação, câmera (ex: grande-angular, whip pan, selfie, close com zoom lento)",
            "transicao": "corte",
        })

    receita = {
        "referencia": video.name,
        "formato": {"largura": info["largura"], "altura": info["altura"], "fps": info["fps"]},
        "duracao_total": info["duracao"],
        "estilo_global": "vídeo vertical de celular, luz natural de fim de tarde, estilo trend de TikTok/Reels",
        "modelo": "fal-ai/kling-video/v2.1/standard/image-to-video",
        "audio": str(video.resolve()) if info["tem_audio"] else None,
        "cenas": cenas,
    }
    (saida / "receita.json").write_text(json.dumps(receita, ensure_ascii=False, indent=2))
    return receita
