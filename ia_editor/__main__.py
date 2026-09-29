"""CLI do IA-EDITOR.

  python -m ia_editor analisar video.mp4 saida/trend
  python -m ia_editor montar saida/trend --provedor rascunho
  python -m ia_editor montar saida/trend --provedor fal
"""
import argparse
from pathlib import Path

from .analisar import analisar
from .montar import montar


def main() -> None:
    p = argparse.ArgumentParser(prog="ia_editor")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analisar", help="extrai a receita (cenas e tempos) de um vídeo")
    a.add_argument("video", type=Path)
    a.add_argument("saida", type=Path)
    a.add_argument("--limiar", type=float, default=0.25, help="sensibilidade de corte (0-1)")

    m = sub.add_parser("montar", help="gera as cenas com IA e monta o vídeo final")
    m.add_argument("pasta", type=Path)
    m.add_argument("--provedor", choices=["rascunho", "fal"], default="rascunho")
    m.add_argument("--sem-audio", action="store_true")

    args = p.parse_args()
    if args.cmd == "analisar":
        r = analisar(args.video, args.saida, args.limiar)
        print(f"{len(r['cenas'])} cenas encontradas -> {args.saida / 'receita.json'}")
        for c in r["cenas"]:
            print(f"  cena {c['id']}: {c['inicio']:.2f}s - {c['fim']:.2f}s")
    else:
        print(f"pronto: {montar(args.pasta, args.provedor, not args.sem_audio)}")


if __name__ == "__main__":
    main()
