"""Etapa 2: gera cada cena com um modelo de vídeo por IA.

Provedores:
  - "rascunho": não usa IA; cria um clipe a partir do quadro de referência
    (ou da imagem inicial) com zoom lento. Serve para testar o ritmo grátis.
  - "fal": usa a API de fila do fal.ai (precisa da variável FAL_KEY). O fal
    hospeda Kling, Veo, Wan, Seedance, Hailuo etc.; troque o campo
    "modelo" da receita para mudar de IA.
"""
import base64
import json
import mimetypes
import os
import time
import urllib.request
from pathlib import Path

from . import ff


def rascunho(cena: dict, pasta: Path, formato: dict, destino: Path) -> None:
    img = pasta / (cena.get("imagem_inicial") or cena["quadro_referencia"])
    w, h, fps = formato["largura"], formato["altura"], int(formato["fps"])
    frames = max(1, int(cena["duracao"] * fps))
    ff.run([
        "-loop", "1", "-i", str(img),
        "-vf", (
            f"scale={w * 2}:{h * 2},"
            f"zoompan=z='min(zoom+0.0015,1.2)':d={frames}:s={w}x{h}:fps={fps},"
            "format=yuv420p"
        ),
        "-t", str(cena["duracao"]), "-c:v", "libx264", str(destino),
    ])


def _http(url: str, dados: dict | None = None) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(dados).encode() if dados is not None else None,
        headers={
            "Authorization": f"Key {os.environ['FAL_KEY']}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def _data_uri(caminho: Path) -> str:
    mime = mimetypes.guess_type(caminho.name)[0] or "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(caminho.read_bytes()).decode()}"


def fal(cena: dict, pasta: Path, receita: dict, destino: Path) -> None:
    if "FAL_KEY" not in os.environ:
        raise SystemExit("Defina FAL_KEY para usar o provedor fal (https://fal.ai).")
    img = pasta / (cena.get("imagem_inicial") or cena["quadro_referencia"])
    prompt = f"{cena['prompt']}. {receita['estilo_global']}"
    entrada = {
        "prompt": prompt,
        "image_url": _data_uri(img),
        "duration": "5" if cena["duracao"] <= 5 else "10",
        "aspect_ratio": "9:16",
    }
    fila = _http(f"https://queue.fal.run/{receita['modelo']}", entrada)
    while True:
        status = _http(fila["status_url"])["status"]
        if status == "COMPLETED":
            break
        if status not in ("IN_QUEUE", "IN_PROGRESS"):
            raise RuntimeError(f"cena {cena['id']}: status {status}")
        time.sleep(5)
    resultado = _http(fila["response_url"])
    url_video = resultado["video"]["url"]
    bruto = destino.with_suffix(".bruto.mp4")
    urllib.request.urlretrieve(url_video, bruto)
    # A IA gera 5s/10s; cortamos para caber exatamente no tempo da cena original.
    f = receita["formato"]
    ff.run([
        "-i", str(bruto), "-t", str(cena["duracao"]),
        "-vf", f"scale={f['largura']}:{f['altura']}:force_original_aspect_ratio=increase,"
               f"crop={f['largura']}:{f['altura']},fps={int(f['fps'])},format=yuv420p",
        "-an", "-c:v", "libx264", str(destino),
    ])
    bruto.unlink(missing_ok=True)
