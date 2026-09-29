"""Etapa 3: gera as cenas e monta o vídeo final no ritmo da referência."""
import json
from pathlib import Path

from . import ff, provedores


def montar(pasta: Path, provedor: str = "rascunho", usar_audio: bool = True) -> Path:
    receita = json.loads((pasta / "receita.json").read_text())
    clipes = []
    for cena in receita["cenas"]:
        destino = pasta / f"gerado_{cena['id']:02d}.mp4"
        if not destino.exists():
            print(f"gerando cena {cena['id']} ({cena['duracao']}s) via {provedor}...")
            if provedor == "fal":
                provedores.fal(cena, pasta, receita, destino)
            else:
                provedores.rascunho(cena, pasta, receita["formato"], destino)
        clipes.append(destino)

    lista = pasta / "lista.txt"
    lista.write_text("".join(f"file '{c.name}'\n" for c in clipes))
    final = pasta / "final.mp4"
    args = ["-f", "concat", "-safe", "0", "-i", str(lista)]
    if usar_audio and receita.get("audio"):
        args += ["-i", receita["audio"], "-map", "0:v", "-map", "1:a", "-shortest"]
    ff.run([*args, "-c:v", "libx264", "-pix_fmt", "yuv420p", str(final)])
    return final
