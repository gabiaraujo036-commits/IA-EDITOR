# Instruções para o Claude

Responda sempre em português do Brasil.

## Controle de ponto (Mario Car)

A usuária manda pelo chat, todos os dias, seus horários de trabalho e anotações
(ex.: "cheguei 08:54", "saí pro almoço 12h", "hoje faltei porque meu filho ficou doente",
"me atrasei, o ônibus quebrou"). Cada mensagem dessas deve ser registrada no sistema abaixo.

- Fonte oficial dos dados: `ponto/registros.json` (nunca editar a planilha à mão).
- Planilha gerada: `planilhas/ponto-mario-car.xlsx` (nov/2026 a dez/2027).
- Registro: `python3 ponto/registrar.py <data> [opções]` — atualiza o JSON, regenera e recalcula a planilha
  e imprime o resumo do dia e da semana. `--help` mostra todas as opções.

Opções: `--chegada`, `--saida-almoco`, `--volta-almoco`, `--saida` (hh:mm),
`--obs Folga|Falta|Atestado|Feriado|limpar`, `--nota "texto"` com `--tipo`
(Atraso, Falta, Saída antecipada, Almoço longo, Folga, Atestado, Hora extra, Outro),
`--apagar <campo>`, `--mostrar`.
Datas: `hoje`, `ontem`, `DD/MM`, `DD/MM/AAAA` (fuso de São Paulo).

### Fluxo a cada mensagem
1. Interpretar a mensagem: qual dia (sem data = hoje, no horário de Brasília), quais horários, qual motivo.
   Se algo for ambíguo (ex.: não dá para saber se "13h" é volta do almoço ou saída), perguntar antes.
2. Rodar `ponto/registrar.py` com os dados. Anotar o motivo com as palavras dela em `--nota`.
   Falta → `--obs Falta`; folga (inclusive a folga extra do mês) → `--obs Folga`; atestado → `--obs Atestado`.
3. Conferir que o recálculo terminou com 0 erros.
4. Commit (mensagem curta em português, ex.: "Ponto 10/11: chegada 08:54") e push no branch de trabalho
   (`claude/planilha-ponto-mario-car`, a menos que a sessão indique outro).
5. Responder em poucas linhas o que foi registrado e o resumo do dia/semana impresso pelo script
   (atraso, horário para completar a jornada, saldo, horas acima de 44h). Enviar a planilha com
   SendUserFile quando ela pedir ou no fim do dia (quando registrar a saída).

Jornada: seg–sex 8h–17h (8h trabalhadas), sábado 8h–16h (7h), 1h de almoço, domingo folga,
1 folga extra por mês. Limite CLT: 44h/semana.
