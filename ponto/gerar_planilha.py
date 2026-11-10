"""Gera planilhas/ponto-mario-car.xlsx a partir de ponto/registros.json.

Uso direto:  python3 ponto/gerar_planilha.py
(Normalmente é chamado por ponto/registrar.py.)
"""
import datetime as dt
import json
import pathlib

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

RAIZ = pathlib.Path(__file__).resolve().parent.parent
REGISTROS = RAIZ / "ponto" / "registros.json"
SAIDA = RAIZ / "planilhas" / "ponto-mario-car.xlsx"

INICIO = (2026, 11)
FIM = (2027, 12)

MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
         "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
ABREV = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
DIAS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
        "Sexta-feira", "Sábado", "Domingo"]
OBS_OPCOES = ["Folga", "Falta", "Atestado", "Feriado"]
CAMPOS_HORA = ["chegada", "saida_almoco", "volta_almoco", "saida"]

# ---- estilos ----
F = "Arial"
f_base = Font(name=F, size=10)
f_bold = Font(name=F, size=10, bold=True)
f_title = Font(name=F, size=14, bold=True, color="FFFFFF")
f_head = Font(name=F, size=10, bold=True, color="FFFFFF")
f_input = Font(name=F, size=10, color="0000FF")
f_note = Font(name=F, size=9, italic=True, color="555555")
f_link = Font(name=F, size=10, color="008000")
fill_title = PatternFill("solid", fgColor="1F3864")
fill_head = PatternFill("solid", fgColor="2F5496")
fill_input = PatternFill("solid", fgColor="FFF2CC")
fill_sun = PatternFill("solid", fgColor="D9D9D9")
fill_week = PatternFill("solid", fgColor="DDEBF7")
fill_sum = PatternFill("solid", fgColor="E2EFDA")
fill_alert = PatternFill("solid", fgColor="F8CBAD")
fill_late = PatternFill("solid", fgColor="F4B183")
thin = Side(style="thin", color="BFBFBF")
border = Border(left=thin, right=thin, top=thin, bottom=thin)
center = Alignment(horizontal="center", vertical="center")
left_wrap = Alignment(horizontal="left", vertical="center", wrap_text=True)
wrapc = Alignment(horizontal="center", vertical="center", wrap_text=True)
TF = "[h]:mm"

# ---- colunas das abas mensais ----
HEAD = ["Data", "Dia da semana", "Chegada", "Saída para almoço", "Volta do almoço",
        "Saída", "Horas trabalhadas", "Tempo de almoço", "Horas previstas",
        "Diferença do dia", "Observação", "Anotação (motivo)", "Acima de 44h (semana)",
        "Dif. (cálculo)"]
WIDTH = [11, 14, 10, 11, 11, 10, 12, 11, 11, 11, 13, 34, 13, 10]
# A..N
cA, cB, cC, cD, cE, cF, cG, cH, cI, cJ, cK, cL, cM, cN = range(1, 15)
HIDDEN = "N"

# ---- configuração (aba Resumo) ----
CFG_SEMANA = "Resumo!$C$5"
CFG_SAB = "Resumo!$C$6"
CFG_LIMITE = "Resumo!$C$7"
CFG_ENTRADA = "Resumo!$C$8"


def saldo_txt(ref):
    return f'=IF({ref}="","",IF({ref}<0,"-","+")&TEXT(ABS({ref}),"[h]:mm"))'


def rng(col, rows):
    out, start, prev = [], rows[0], rows[0]
    for x in rows[1:]:
        if x != prev + 1:
            out.append(f"{col}{start}:{col}{prev}")
            start = x
        prev = x
    out.append(f"{col}{start}:{col}{prev}")
    return ",".join(out)


def hora(txt):
    h, m = map(int, txt.split(":"))
    return dt.time(h, m)


def lista_meses():
    y, m = INICIO
    out = []
    while (y, m) <= FIM:
        out.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def texto_anotacoes(dia):
    notas = dia.get("anotacoes") or []
    return "; ".join(f"{n['tipo']}: {n['texto']}" if n.get("tipo") else n["texto"] for n in notas)


def gerar(registros, saida=SAIDA):
    wb = Workbook()
    res = wb.active
    res.title = "Resumo"
    meses = lista_meses()
    prev = None
    resumo_links = []

    for idx, (y, m) in enumerate(meses):
        name = f"{ABREV[m-1]}-{y}"
        ws = wb.create_sheet(name)
        ultimo_mes = idx == len(meses) - 1
        for i, w in enumerate(WIDTH):
            ws.column_dimensions[get_column_letter(i + 1)].width = w
        ws.column_dimensions[HIDDEN].hidden = True

        ws["A1"] = f"Controle de Ponto – Mario Car – {MESES[m-1]} de {y}"
        ws["A1"].font = f_title
        for c in range(1, cM + 1):
            ws.cell(1, c).fill = fill_title
        ws.row_dimensions[1].height = 24
        ws["A2"] = ("Células amarelas = entrada de dados. Horários em hh:mm (ex.: 08:00). Observação: Folga, Falta, "
                    "Atestado ou Feriado. Anotação: o motivo (atraso, falta, saída antecipada…).")
        ws["A2"].font = f_note
        ws["A3"] = ("Chegada em laranja = depois do horário de entrada. Folga, Feriado e Atestado zeram as horas previstas; "
                    "Falta sem horários conta o dia todo como negativo. Semanas que cruzam o mês são totalizadas no mês em que terminam.")
        ws["A3"].font = f_note
        ws["N2"] = f"={CFG_ENTRADA}"  # cópia local da hora de entrada (usada na formatação condicional)
        ws["N2"].number_format = "hh:mm"

        HR = 4
        for c, h in enumerate(HEAD, 1):
            cell = ws.cell(HR, c, h)
            cell.font = f_head
            cell.fill = fill_head
            cell.alignment = wrapc
            cell.border = border
        ws.row_dimensions[HR].height = 30
        ws.freeze_panes = "B5"

        dv_time = DataValidation(type="time", operator="between", formula1="0", formula2="0.999988426",
                                 allow_blank=True, showErrorMessage=True, errorStyle="warning",
                                 errorTitle="Horário", error="Digite o horário no formato hh:mm, ex.: 08:00")
        dv_obs = DataValidation(type="list", formula1='"' + ",".join(OBS_OPCOES) + '"', allow_blank=True,
                                showErrorMessage=False)
        ws.add_data_validation(dv_time)
        ws.add_data_validation(dv_obs)

        r = HR + 1
        day = dt.date(y, m, 1)
        data_rows, week_rows = [], []
        state = {"week_start": r, "first": day,
                 "carry": prev if (prev and day.weekday() != 0) else None}

        def write_week(end_date, partial_next):
            nonlocal r
            rows = [x for x in data_rows if x >= state["week_start"]]
            carry = state["carry"]
            ws.cell(r, cA, "Total semana")
            ws.cell(r, cB, f"{state['first']:%d/%m} a {end_date:%d/%m}")

            def sumf(col):
                s = f"SUM({col}{rows[0]}:{col}{rows[-1]})"
                if carry:
                    s += f"+'{carry[0]}'!{col}{carry[1]}"
                return "=" + s

            for c, col in ((cG, "G"), (cH, "H"), (cI, "I"), (cN, "N")):
                ws.cell(r, c, sumf(col))
            ws.cell(r, cJ, saldo_txt(f"N{r}"))
            if partial_next:
                ws.cell(r, cL, "Semana continua no próximo mês")
            else:
                ws.cell(r, cM, f"=MAX(0,ROUND((G{r}-{CFG_LIMITE})*1440,0)/1440)")
                if carry:
                    ws.cell(r, cL, "Inclui dias do mês anterior")
                if ultimo_mes and end_date.weekday() != 6:
                    ws.cell(r, cL, "Semana termina em 2028")
            for c in range(1, cN + 1):
                cell = ws.cell(r, c)
                cell.fill = fill_week
                cell.border = border
                cell.font = f_note if c == cL else f_bold
                cell.alignment = left_wrap if c == cL else center
                if c in (cG, cH, cI, cM, cN):
                    cell.number_format = TF
            week_rows.append(r)
            r += 1

        last = day
        while day.month == m:
            wd = day.weekday()
            reg = registros.get(day.isoformat(), {})
            ws.cell(r, cA, day).number_format = "dd/mm/yyyy"
            ws.cell(r, cB, DIAS[wd])
            for c, campo in zip((cC, cD, cE, cF), CAMPOS_HORA):
                if reg.get(campo):
                    ws.cell(r, c, hora(reg[campo]))
            if reg.get("observacao"):
                ws.cell(r, cK, reg["observacao"])
            notas = texto_anotacoes(reg)
            if notas:
                ws.cell(r, cL, notas)
            ws.cell(r, cG, f'=IF(OR(C{r}="",F{r}=""),"",MOD(F{r}-C{r},1)-IF(OR(D{r}="",E{r}=""),0,MOD(E{r}-D{r},1)))')
            ws.cell(r, cH, f'=IF(OR(D{r}="",E{r}=""),"",MOD(E{r}-D{r},1))')
            ws.cell(r, cI, f'=IF(OR(K{r}="Folga",K{r}="Feriado",K{r}="Atestado"),0,'
                           f'CHOOSE(WEEKDAY(A{r},2),{CFG_SEMANA},{CFG_SEMANA},{CFG_SEMANA},{CFG_SEMANA},{CFG_SEMANA},{CFG_SAB},0))')
            ws.cell(r, cN, f'=IF(G{r}="",IF(K{r}="Falta",-I{r},""),ROUND((G{r}-I{r})*1440,0)/1440)')
            ws.cell(r, cJ, saldo_txt(f"N{r}"))
            for c in range(1, cN + 1):
                cell = ws.cell(r, c)
                cell.border = border
                cell.font = f_base
                cell.alignment = left_wrap if c == cL else center
                if c in (cC, cD, cE, cF):
                    cell.number_format = "hh:mm"
                    cell.font = f_input
                if c in (cC, cD, cE, cF, cK, cL):
                    cell.fill = fill_sun if wd == 6 else fill_input
                elif wd == 6:
                    cell.fill = fill_sun
                if c in (cG, cH, cI, cN):
                    cell.number_format = TF
            dv_time.add(f"C{r}:F{r}")
            dv_obs.add(f"K{r}")
            data_rows.append(r)
            last = day
            r += 1
            day += dt.timedelta(days=1)
            if wd == 6:
                write_week(last, False)
                state.update(week_start=r, first=day, carry=None)

        trailing = None
        if state["week_start"] < r:
            partial = not ultimo_mes
            write_week(last, partial)
            if partial:
                trailing = (name, r - 1)

        # ---- resumo do mês ----
        r += 1
        ws.cell(r, cA, "Resumo do mês").font = Font(name=F, size=11, bold=True)
        r += 1
        d0, d1 = data_rows[0], data_rows[-1]
        linhas = [
            ("Total trabalhado", f"=SUM({rng('G', data_rows)})", TF),
            ("Total previsto", f"=SUM({rng('I', data_rows)})", TF),
            ("Saldo do mês", None, None),
            ("Horas acima de 44h (soma das semanas)", f"=SUM({rng('M', week_rows)})", TF),
            ("Chegadas após o horário", f'=COUNTIF(C{d0}:C{d1},">"&$N$2)', "0"),
            ("Dias de folga", f'=COUNTIF(K{d0}:K{d1},"Folga")', "0"),
            ("Faltas", f'=COUNTIF(K{d0}:K{d1},"Falta")', "0"),
            ("Atestados", f'=COUNTIF(K{d0}:K{d1},"Atestado")', "0"),
            ("Feriados", f'=COUNTIF(K{d0}:K{d1},"Feriado")', "0"),
        ]
        sumrows = {}
        for label, formula, fmt in linhas:
            ws.cell(r, cA, label).font = f_bold
            for c in range(1, cG + 1):
                ws.cell(r, c).fill = fill_sum
                ws.cell(r, c).border = border
            if label == "Saldo do mês":
                ws.cell(r, cN, f"=SUM({rng('N', data_rows)})").number_format = TF
                ws.cell(r, cG, saldo_txt(f"N{r}"))
            else:
                ws.cell(r, cG, formula).number_format = fmt
            ws.cell(r, cG).font = f_bold
            ws.cell(r, cG).alignment = center
            sumrows[label] = r
            r += 1

        # ---- formatação condicional ----
        first, lastr = HR + 1, r
        ws.conditional_formatting.add(f"C{d0}:C{d1}", FormulaRule(
            formula=[f'AND(ISNUMBER(C{d0}),C{d0}>$N$2)'], fill=fill_late, font=Font(name=F, bold=True, color="833C0B")))
        ws.conditional_formatting.add(f"M{first}:M{lastr}", FormulaRule(
            formula=[f'AND(ISNUMBER(M{first}),M{first}>0)'], fill=fill_alert,
            font=Font(name=F, bold=True, color="C00000")))
        ws.conditional_formatting.add(f"J{first}:J{lastr}", FormulaRule(
            formula=[f'AND(ISNUMBER(N{first}),N{first}<0)'], font=Font(name=F, color="C00000")))
        ws.conditional_formatting.add(f"J{first}:J{lastr}", FormulaRule(
            formula=[f'AND(ISNUMBER(N{first}),N{first}>0)'], font=Font(name=F, color="00803C")))
        s = sumrows["Saldo do mês"]
        ws.conditional_formatting.add(f"G{s}", FormulaRule(
            formula=[f"N{s}<0"], font=Font(name=F, bold=True, color="C00000")))
        a = sumrows["Horas acima de 44h (soma das semanas)"]
        ws.conditional_formatting.add(f"G{a}", FormulaRule(
            formula=[f"G{a}>0"], fill=fill_alert, font=Font(name=F, bold=True, color="C00000")))

        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.print_title_rows = "4:4"

        resumo_links.append((name, MESES[m - 1], y, sumrows))
        prev = trailing

    _aba_resumo(res, resumo_links)
    _aba_agenda(wb.create_sheet("Agenda", 1), registros)
    saida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(saida)
    return saida


def _aba_resumo(res, resumo_links):
    for i, w in enumerate([4, 30, 14, 14, 14, 14, 11, 10, 10, 10, 10, 10]):
        res.column_dimensions[get_column_letter(i + 1)].width = w
    res.column_dimensions["M"].hidden = True
    res["A1"] = "Controle de Ponto – Mario Car – Resumo Geral (nov/2026 a dez/2027)"
    res["A1"].font = f_title
    for c in range(1, 13):
        res.cell(1, c).fill = fill_title
    res.row_dimensions[1].height = 24
    res["B2"] = ("Cada aba mensal tem as datas preenchidas. Preencha só as células amarelas. "
                 "Esta aba se atualiza sozinha; as anotações ficam na aba Agenda.")
    res["B2"].font = f_note

    res["B4"] = "Configuração da jornada"
    res["B4"].font = Font(name=F, size=11, bold=True)
    cfg = [("Horas previstas seg. a sex.", dt.time(8, 0), "Jornada 8h–17h com 1h de almoço (informado pela usuária)"),
           ("Horas previstas sábado", dt.time(7, 0), "Jornada 8h–16h com 1h de almoço (informado pela usuária)"),
           ("Limite semanal (CLT)", 44 / 24, "44h por semana – CLT art. 58 / CF art. 7º, XIII"),
           ("Horário de entrada", dt.time(8, 0), "Chegada depois deste horário fica em laranja (informado pela usuária)")]
    for i, (lab, val, note) in enumerate(cfg):
        rr = 5 + i
        res.cell(rr, 2, lab).font = f_base
        res.cell(rr, 2).border = border
        c = res.cell(rr, 3, val)
        c.number_format = "hh:mm" if "entrada" in lab else TF
        c.font = f_input
        c.fill = fill_input
        c.alignment = center
        c.border = border
        res.cell(rr, 4, note).font = f_note

    TR = 11
    heads = ["Mês", "Total trabalhado", "Total previsto", "Saldo", "Acima de 44h",
             "Chegadas após horário", "Folgas", "Faltas", "Atestados", "Feriados"]
    for c, h in enumerate(heads, 2):
        cell = res.cell(TR, c, h)
        cell.font = f_head
        cell.fill = fill_head
        cell.alignment = wrapc
        cell.border = border
    res.row_dimensions[TR].height = 30
    res.freeze_panes = f"C{TR+1}"
    rr = TR + 1
    for name, mes, y, s in resumo_links:
        q = f"'{name}'!"
        res.cell(rr, 2, f"{mes}/{y}")
        res.cell(rr, 3, f"={q}G{s['Total trabalhado']}").number_format = TF
        res.cell(rr, 4, f"={q}G{s['Total previsto']}").number_format = TF
        res.cell(rr, 13, f"={q}N{s['Saldo do mês']}").number_format = TF
        res.cell(rr, 5, saldo_txt(f"M{rr}"))
        res.cell(rr, 6, f"={q}G{s['Horas acima de 44h (soma das semanas)']}").number_format = TF
        res.cell(rr, 7, f"={q}G{s['Chegadas após o horário']}")
        res.cell(rr, 8, f"={q}G{s['Dias de folga']}")
        res.cell(rr, 9, f"={q}G{s['Faltas']}")
        res.cell(rr, 10, f"={q}G{s['Atestados']}")
        res.cell(rr, 11, f"={q}G{s['Feriados']}")
        for c in range(2, 12):
            res.cell(rr, c).font = f_link if c > 2 else f_base
            res.cell(rr, c).border = border
            res.cell(rr, c).alignment = center
        rr += 1
    first, lastd = TR + 1, rr - 1
    res.cell(rr, 2, "TOTAL")
    for c in (3, 4, 6, 7, 8, 9, 10, 11, 13):
        col = get_column_letter(c)
        res.cell(rr, c, f"=SUM({col}{first}:{col}{lastd})").number_format = TF if c in (3, 4, 6, 13) else "0"
    res.cell(rr, 5, saldo_txt(f"M{rr}"))
    for c in range(2, 12):
        res.cell(rr, c).font = f_bold
        res.cell(rr, c).fill = fill_sum
        res.cell(rr, c).border = border
        res.cell(rr, c).alignment = center
    res.conditional_formatting.add(f"E{first}:E{rr}", FormulaRule(
        formula=[f"AND(ISNUMBER(M{first}),M{first}<0)"], font=Font(name=F, bold=True, color="C00000")))
    res.conditional_formatting.add(f"F{first}:F{rr}", FormulaRule(
        formula=[f"AND(ISNUMBER(F{first}),F{first}>0)"], fill=fill_alert,
        font=Font(name=F, bold=True, color="C00000")))
    res.cell(rr + 2, 2, "Saldo = horas trabalhadas − horas previstas. \"Acima de 44h\" = soma, semana a semana, "
                        "do que passou do limite semanal (possível hora extra ou banco de horas).").font = f_note
    res.cell(rr + 3, 2, "Valores em verde vêm das abas mensais. As células amarelas da configuração podem ser ajustadas.").font = f_note


def _aba_agenda(ws, registros):
    for col, w in zip("ABCDEFG", [11, 14, 22, 18, 50, 10, 10]):
        ws.column_dimensions[col].width = w
    ws["A1"] = "Agenda – anotações do ponto"
    ws["A1"].font = f_title
    for c in range(1, 8):
        ws.cell(1, c).fill = fill_title
    ws.row_dimensions[1].height = 24
    ws["A2"] = "Motivos de atraso, falta, saída antecipada, folga etc. Uma linha por anotação, em ordem de data."
    ws["A2"].font = f_note
    heads = ["Data", "Dia da semana", "Horários do dia", "Tipo", "Anotação", "Chegada", "Saída"]
    for c, h in enumerate(heads, 1):
        cell = ws.cell(4, c, h)
        cell.font = f_head
        cell.fill = fill_head
        cell.alignment = wrapc
        cell.border = border
    ws.freeze_panes = "A5"
    r = 5
    for iso in sorted(registros):
        dia = registros[iso]
        notas = dia.get("anotacoes") or []
        if not notas and not dia.get("observacao"):
            continue
        d = dt.date.fromisoformat(iso)
        horarios = " · ".join(dia[k] for k in CAMPOS_HORA if dia.get(k)) or "—"
        if not notas:
            notas = [{"tipo": dia["observacao"], "texto": ""}]
        for n in notas:
            ws.cell(r, 1, d).number_format = "dd/mm/yyyy"
            ws.cell(r, 2, DIAS[d.weekday()])
            ws.cell(r, 3, horarios)
            ws.cell(r, 4, n.get("tipo") or "")
            ws.cell(r, 5, n.get("texto") or "")
            if dia.get("chegada"):
                ws.cell(r, 6, hora(dia["chegada"])).number_format = "hh:mm"
            if dia.get("saida"):
                ws.cell(r, 7, hora(dia["saida"])).number_format = "hh:mm"
            for c in range(1, 8):
                cell = ws.cell(r, c)
                cell.font = f_base
                cell.border = border
                cell.alignment = left_wrap if c == 5 else center
            r += 1
    if r == 5:
        ws.cell(5, 1, "Nenhuma anotação ainda.").font = f_note


def carregar():
    if REGISTROS.exists():
        return json.loads(REGISTROS.read_text(encoding="utf-8"))
    return {}


if __name__ == "__main__":
    print(gerar(carregar()))
