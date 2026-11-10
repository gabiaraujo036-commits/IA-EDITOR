"""Registra horários e anotações do ponto e regenera a planilha.

Exemplos:
  python3 ponto/registrar.py hoje --chegada 08:54
  python3 ponto/registrar.py 10/11 --saida-almoco 12:00 --volta-almoco 13:00 --saida 17:30
  python3 ponto/registrar.py ontem --obs Falta --nota "Consulta médica" --tipo Falta
  python3 ponto/registrar.py 10/11 --nota "Ônibus atrasou" --tipo Atraso
  python3 ponto/registrar.py 10/11 --apagar saida            (limpa um campo)
  python3 ponto/registrar.py 10/11 --mostrar                  (só mostra o dia e a semana)

Datas aceitas: hoje, ontem, anteontem, DD/MM, DD/MM/AAAA, AAAA-MM-DD.
"Hoje" usa o fuso de São Paulo.
"""
import argparse
import datetime as dt
import glob
import json
import subprocess
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import gerar_planilha as gp  # noqa: E402

FUSO = ZoneInfo("America/Sao_Paulo")
CAMPOS = {"chegada": "chegada", "saida_almoco": "saída p/ almoço",
          "volta_almoco": "volta do almoço", "saida": "saída"}
PREVISTO = {0: 8, 1: 8, 2: 8, 3: 8, 4: 8, 5: 7, 6: 0}


def parse_data(txt):
    hoje = dt.datetime.now(FUSO).date()
    t = txt.strip().lower()
    if t == "hoje":
        return hoje
    if t == "ontem":
        return hoje - dt.timedelta(days=1)
    if t == "anteontem":
        return hoje - dt.timedelta(days=2)
    if "-" in t:
        return dt.date.fromisoformat(t)
    partes = [int(p) for p in t.split("/")]
    if len(partes) == 3:
        d, m, y = partes
        y += 2000 if y < 100 else 0
    else:
        d, m = partes
        y = hoje.year
        cand = dt.date(y, m, d)
        if cand > hoje + dt.timedelta(days=31):  # ex.: "30/12" digitado em janeiro
            y -= 1
    return dt.date(y, m, d)


def parse_hora(txt):
    t = txt.strip().lower().replace("h", ":").replace(".", ":")
    if t.endswith(":"):
        t += "00"
    if ":" not in t:
        t += ":00"
    h, m = t.split(":")
    h, m = int(h), int(m or 0)
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError(f"Horário inválido: {txt}")
    return f"{h:02d}:{m:02d}"


def minutos(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def fmt(mins, sinal=False):
    s = "-" if mins < 0 else ("+" if sinal else "")
    mins = abs(mins)
    return f"{s}{mins // 60}h{mins % 60:02d}"


def calc_dia(d, reg):
    """Retorna (trabalhado, previsto, diferença) em minutos; trabalhado None se incompleto."""
    obs = reg.get("observacao")
    prev = 0 if obs in ("Folga", "Feriado", "Atestado") else PREVISTO[d.weekday()] * 60
    if reg.get("chegada") and reg.get("saida"):
        t = (minutos(reg["saida"]) - minutos(reg["chegada"])) % 1440
        if reg.get("saida_almoco") and reg.get("volta_almoco"):
            t -= (minutos(reg["volta_almoco"]) - minutos(reg["saida_almoco"])) % 1440
        return t, prev, t - prev
    if obs == "Falta":
        return None, prev, -prev
    return None, prev, None


def mostrar(d, regs):
    reg = regs.get(d.isoformat(), {})
    print(f"\n{d:%d/%m/%Y} ({gp.DIAS[d.weekday()]})")
    for k, nome in CAMPOS.items():
        print(f"  {nome:<16} {reg.get(k) or '—'}")
    if reg.get("observacao"):
        print(f"  observação       {reg['observacao']}")
    for n in reg.get("anotacoes") or []:
        print(f"  anotação         {(n.get('tipo') + ': ') if n.get('tipo') else ''}{n['texto']}")
    t, p, dif = calc_dia(d, reg)
    if reg.get("chegada") and d.weekday() != 6:
        atraso = minutos(reg["chegada"]) - 8 * 60
        if atraso > 0:
            print(f"  ⚠ chegada {fmt(atraso)} depois das 08:00")
    if t is not None:
        print(f"  trabalhado {fmt(t)} | previsto {fmt(p)} | diferença {fmt(dif, True)}")
    elif reg.get("chegada") and not reg.get("saida") and p:
        almoco = 60
        if reg.get("saida_almoco") and reg.get("volta_almoco"):
            almoco = (minutos(reg["volta_almoco"]) - minutos(reg["saida_almoco"])) % 1440
        print(f"  para completar {fmt(p)} hoje, a saída seria às "
              f"{fmt(minutos(reg['chegada']) + p + almoco).replace('h', ':')}")
    # semana (segunda a domingo)
    seg = d - dt.timedelta(days=d.weekday())
    tot = dias_ok = 0
    for i in range(7):
        di = seg + dt.timedelta(days=i)
        ti, _, _ = calc_dia(di, regs.get(di.isoformat(), {}))
        if ti is not None:
            tot += ti
            dias_ok += 1
    print(f"  semana {seg:%d/%m}–{seg + dt.timedelta(days=6):%d/%m}: {fmt(tot)} trabalhadas em {dias_ok} dia(s) "
          f"completo(s); acima de 44h: {fmt(max(0, tot - 44 * 60))}")


def recalcular(caminho):
    scripts = sorted(glob.glob("/root/.claude/skills/**/xlsx/scripts/recalc.py", recursive=True))
    if not scripts:
        print("AVISO: recalc.py não encontrado; a planilha recalcula ao ser aberta.")
        return
    out = subprocess.run([sys.executable, scripts[0], str(caminho), "120"], capture_output=True, text=True)
    try:
        res = json.loads(out.stdout)
    except json.JSONDecodeError:
        print("AVISO: falha ao recalcular:", out.stdout, out.stderr)
        return
    if res.get("status") != "success":
        print("ERRO no recálculo:", json.dumps(res, ensure_ascii=False))
        sys.exit(1)
    print(f"Planilha recalculada: {res['total_formulas']} fórmulas, 0 erros.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data")
    ap.add_argument("--chegada")
    ap.add_argument("--saida-almoco")
    ap.add_argument("--volta-almoco")
    ap.add_argument("--saida")
    ap.add_argument("--obs", help="Folga, Falta, Atestado, Feriado ou 'limpar'")
    ap.add_argument("--nota", action="append", help="texto da anotação (pode repetir)")
    ap.add_argument("--tipo", help="tipo da anotação: Atraso, Falta, Saída antecipada, Almoço longo, Folga, "
                                   "Atestado, Hora extra, Outro")
    ap.add_argument("--apagar", action="append", choices=list(CAMPOS) + ["anotacoes"])
    ap.add_argument("--mostrar", action="store_true", help="só mostra, não altera")
    a = ap.parse_args()

    d = parse_data(a.data)
    ini, fim = dt.date(*gp.INICIO, 1), dt.date(gp.FIM[0], gp.FIM[1], 31)
    if not (ini <= d <= fim):
        sys.exit(f"Data {d:%d/%m/%Y} fora do período da planilha ({ini:%d/%m/%Y} a {fim:%d/%m/%Y}).")
    regs = gp.carregar()
    if a.mostrar:
        mostrar(d, regs)
        return

    reg = regs.setdefault(d.isoformat(), {})
    for campo in CAMPOS:
        v = getattr(a, campo)
        if v:
            reg[campo] = parse_hora(v)
    for campo in a.apagar or []:
        reg.pop(campo, None)
    if a.obs:
        if a.obs.lower() == "limpar":
            reg.pop("observacao", None)
        else:
            opc = {o.lower(): o for o in gp.OBS_OPCOES}
            if a.obs.lower() not in opc:
                sys.exit(f"Observação deve ser uma de: {', '.join(gp.OBS_OPCOES)} (ou 'limpar').")
            reg["observacao"] = opc[a.obs.lower()]
    agora = dt.datetime.now(FUSO).strftime("%Y-%m-%d %H:%M")
    for texto in a.nota or []:
        reg.setdefault("anotacoes", []).append(
            {"tipo": (a.tipo or "").strip(), "texto": texto.strip(), "registrado_em": agora})
    if not reg:
        regs.pop(d.isoformat())

    gp.REGISTROS.write_text(json.dumps(dict(sorted(regs.items())), ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    gp.gerar(regs)
    recalcular(gp.SAIDA)
    mostrar(d, regs)


if __name__ == "__main__":
    main()
