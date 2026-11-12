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
4. Commit (mensagem curta em português, ex.: "Ponto 10/11: chegada 08:54") e push **direto no `main`**
   (`git push origin HEAD:main`). A usuária pediu que tudo fique no `main`, para qualquer conversa nova
   encontrar o diário atualizado. Antes de registrar, rodar `git pull origin main` para pegar a versão mais recente.
5. Responder em poucas linhas o que foi registrado e o resumo do dia/semana impresso pelo script
   (atraso, horário para completar a jornada, saldo, horas acima de 44h). Enviar a planilha com
   SendUserFile quando ela pedir ou no fim do dia (quando registrar a saída).

Jornada: seg–sex 8h–17h (8h trabalhadas), sábado 8h–16h (7h), 1h de almoço, domingo folga,
1 folga extra por mês. Limite CLT: 44h/semana.

## Pauta do dia (checklist de vídeos)

Ela manda pelo chat o que vai fazer no dia (gravar, editar, enviar pro grupo do marketing, programar, postar,
jogar no Garagem…). Cada dia vira um checklist na página **Pauta do Dia**:
https://claude.ai/artifact/JjaVpTX7ePsXvYbzN4TtaX (código: `pauta/pauta-do-dia.html`).

- Os dados ficam no banco da página (ferramenta `ArtifactData`, `url` acima), coleção `dias`,
  um documento por dia com id `AAAA-MM-DD` (fuso de São Paulo).
- Formato: `{"data": "AAAA-MM-DD", "tarefas": [{"id", "titulo", "tags": ["com o Otávio"],
  "condicao": "Se o Mário aparecer" (opcional), "pulada": false (opcional), "etapas": [...]}], "atualizado": "<ISO>"}`.
- Regra dela: **toda tarefa tem sempre 3 etapas**, nesta ordem:
  `{"nome": "Gravar", "feito": false}`, `{"nome": "Editar", "feito": false}`,
  `{"nome": "Programar ou postar", "opcoes": ["Programar", "Postar"], "escolha": null, "feito": false, "enviado": false}`.
  Na última, ao concluir: `"escolha": "Programar"` ou `"Postar"` e `"feito": true`.
  `"enviado": true` = enviado pro grupo do marketing. Isso NÃO conclui o vídeo: ela ainda programa ou posta depois.
  (Não usar "Enviar pra Rafa": o envio é sempre pro grupo do marketing.)
  Se a tarefa já chegou gravada (ex.: "editar o vídeo X"), criar com Gravar já `feito: true`.
- Ela marca as etapas tocando na página. Quando ela disser no chat que fez algo, ler o documento
  (`get`) e atualizar com `if_version`. Para totalizar o dia, ler o documento e resumir o que foi feito,
  o que ficou pendente e o que "não rolou" (tarefas com `pulada: true`).
- Pendências que ela quiser levar para o dia seguinte: copiar só as etapas não feitas para o novo dia.

- Aba "Para outro dia": tarefas sem data ficam no documento `listas/depois` (`{"tarefas": [...]}`,
  com `adiadaDe` = dia de origem). Tarefas adiadas com data vão direto para o documento daquele dia
  (`dias/AAAA-MM-DD`), também com `adiadaDe`. Quando ela pedir no chat para deixar algo para outro dia,
  fazer o mesmo: tirar do dia atual e pôr no dia escolhido ou em `listas/depois`.
