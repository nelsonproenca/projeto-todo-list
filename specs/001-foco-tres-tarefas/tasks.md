---

description: "Task list for Lista de Tarefas com Foco em 3 Tarefas do Dia"
---

# Tasks: Lista de Tarefas com Foco em 3 Tarefas do Dia

**Input**: Design documents from `/specs/001-foco-tres-tarefas/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ui-routes.md, quickstart.md

**Tests**: OBRIGATÓRIOS (TDD, regra do `CLAUDE.md`). Siga a skill `.claude/skills/django-tdd` (pytest-django + factory_boy): **Red → Green → Refactor**. Em cada fase, as tarefas de teste vêm antes da implementação e devem ser vistas falhando antes de implementar. Cada funcionalidade cobre cinco níveis: **models, forms, views, templates e integração**. Só marque uma história como concluída com todos os níveis verdes.

**Organization**: Tasks agrupadas por user story para implementação e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependência de tarefa incompleta)
- **[Story]**: User story da spec.md (US1, US2, US3)
- Todos os caminhos são relativos à raiz do repositório (`E:\Python\projeto-todo-list`)

## Path Conventions

Monólito Django: app `tasks/` na raiz, ao lado de `core/` (ver plan.md, "Project Structure"). Não tocar em `src/`. Testes em `tasks/tests/`, um arquivo por nível: `test_models.py`, `test_forms.py`, `test_services.py`, `test_views.py`, `test_templates.py`, `test_integration.py`.

---

## Phase 1: Setup

**Purpose**: Criar o app, ligá-lo ao projeto e montar a infraestrutura de testes

- [X] T001 Criar o app Django na raiz com `uv run python manage.py startapp tasks`, gerando `tasks/` ao lado de `core/`; criar as pastas `tasks/templates/tasks/`, `tasks/static/tasks/` e `tasks/tests/` (com `__init__.py`), e remover o `tasks/tests.py` gerado
- [X] T002 Em `core/settings.py`, adicionar `'tasks'` a `INSTALLED_APPS`, trocar `LANGUAGE_CODE` para `'pt-br'` e `TIME_ZONE` para `'America/Sao_Paulo'`
- [X] T003 Criar `tasks/urls.py` com `app_name = 'tasks'` e `urlpatterns = []`, e incluí-lo em `core/urls.py` (`path('', include('tasks.urls'))`), mantendo a rota `admin/` (depende de T001; pode rodar em paralelo com T002)
- [X] T004 Adicionar as dependências de teste com `uv add --dev pytest pytest-django factory-boy pytest-cov` e criar em `pyproject.toml` a seção `[tool.pytest.ini_options]` com `DJANGO_SETTINGS_MODULE = "core.settings"`, `testpaths = ["tasks/tests"]`, `python_files = ["test_*.py"]`, `addopts = "--strict-markers"` e o marcador `integration`
- [X] T005 [P] Criar `tasks/tests/conftest.py` com a fixture `clock` (substitui `django.utils.timezone.now` em `tasks.services` por um relógio controlável com `advance(seconds)`, para testar o cronômetro de forma determinística) e `tasks/tests/factories.py` com `TaskFactory` (`factory.django.DjangoModelFactory` do modelo `Task`: `title` por `factory.Sequence`, `energy='medium'`, `status='today'`) mais as variantes `LaterTaskFactory` e `DoneTaskFactory`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Modelo, formulário, regra-base e base visual de que todas as histórias dependem. Testes primeiro.

**⚠️ CRITICAL**: Nenhuma user story começa antes desta fase terminar

### Tests (Red) — models, forms e template base

- [X] T006 [P] Escrever `tasks/tests/test_models.py`: campos e padrões (`energy='medium'`, `status='today'`, `focus_seconds=0`, `completed_at` e `focus_started_at` nulos); `title` com `max_length` 120; rótulos Leve/Média/Pesada e os três valores de `status`; `__str__` devolve o título; ordenação por `created_at`; as constraints do banco recusam `focus_seconds < 0` e recusam `completed_at` preenchido fora de `status='done'` (e `done` sem `completed_at`)
- [X] T007 [P] Escrever `tasks/tests/test_forms.py` para `TaskForm`: título obrigatório; título só com espaços é recusado com mensagem em português pedindo um título; espaços nas pontas são removidos (`clean_title`); título com mais de 120 caracteres é recusado; energia ausente vira `medium`; energia inválida é recusada
- [X] T008 [P] Escrever em `tasks/tests/test_templates.py` os testes do `base.html`: renderiza os links do dia e de "Para depois" dentro de `{% block nav %}`; exibe as mensagens do framework de mensagens; um template filho que sobrescreve `nav` vazio não mostra os links

### Implementation (Green)

- [X] T009 Criar o modelo `Task` em `tasks/models.py` com os campos de data-model.md: `title` (texto curto, até 120, obrigatório, sem espaços nas pontas, não pode ficar vazio), `energy` (escolha `light`/`medium`/`heavy`, rótulos Leve/Média/Pesada, padrão `medium`), `status` (escolha `today`/`later`/`done`, padrão `today`), `created_at` (automático), `completed_at` (opcional, preenchido se, e somente se, `status = done`), `focus_seconds` (inteiro >= 0, padrão 0) e `focus_started_at` (opcional, não nulo apenas enquanto em foco). `Meta.ordering = ['created_at']`; `CheckConstraint` para `focus_seconds >= 0` e para a regra de `completed_at`; `__str__` devolve o título
- [X] T010 Gerar e aplicar a migração: `uv run python manage.py makemigrations tasks && uv run python manage.py migrate`, criando `tasks/migrations/0001_initial.py`; rodar `uv run pytest tasks/tests/test_models.py` até ficar verde
- [X] T011 [P] Criar `tasks/services.py` com `DAY_LIMIT = 3`, a exceção `DayFullError` e `day_tasks()` (tarefas com `status = today` por `created_at`); as funções de escrita entram nas histórias
- [X] T012 [P] Criar `tasks/forms.py` com `TaskForm` (campos `title` e `energy`), `clean_title` que remove espaços e recusa vazio com mensagem em português, e `energy` caindo em `medium` quando não escolhido (FR-001, FR-008); rodar `test_forms.py` até ficar verde
- [X] T013 [P] Criar `tasks/templates/tasks/base.html` (cabeçalho com links para o dia e "Para depois" dentro de `{% block nav %}`, área de mensagens, `{% block content %}`, uma coluna centralizada e responsiva) e `tasks/static/tasks/app.css` (variáveis de cor e tipografia grande; classes `energy-light`, `energy-medium`, `energy-heavy`, sempre com rótulo em texto; botões; mensagens amigáveis); rodar `test_templates.py` até ficar verde
- [X] T014 Refatorar mantendo a suíte verde: `uv run pytest`

**Checkpoint**: Modelo, formulário, serviço-base e base visual prontos, com testes de models, forms e template base verdes

---

## Phase 3: User Story 1 - Limite de 3 tarefas no dia (Priority: P1) 🎯 MVP

**Goal**: Planejar o dia com no máximo 3 tarefas; a quarta é bloqueada e oferece concluir uma ou guardar para depois.

**Independent Test**: Adicionar 3 tarefas, tentar a quarta e ver o painel "Seu dia está cheio" com as saídas "Guardar para depois" e "Concluir e adicionar" (quickstart, passo 1).

### Tests for User Story 1 (Red)

- [X] T015 [P] [US1] Em `tasks/tests/test_services.py`, testar o limite: criar 3 em `today` funciona; a quarta levanta `DayFullError` e não cria nada; criar em `later` com dia cheio funciona; mover `later → today` com dia cheio levanta `DayFullError`; mover `today → later` libera vaga; concluir define `completed_at` e libera vaga; concluir com nova tarefa associada cria a nova em `today` na mesma transação (e, se a criação falhar, a conclusão é desfeita); título vazio é recusado; editar e excluir
- [X] T016 [P] [US1] Em `tasks/tests/test_views.py`, testar as views: criar redireciona para `home`; a quarta devolve 200 com o painel "Seu dia está cheio" e nada é criado; "Guardar para depois" cria em Para depois; `task_complete` com `novo_title` conclui e adiciona; `task_move` com dia cheio mostra mensagem amigável e não move; título só com espaços reexibe o formulário com erro (200); editar e excluir redirecionam; só aceitam POST as rotas de escrita (GET devolve 405); ids inexistentes dão 404
- [X] T017 [P] [US1] Em `tasks/tests/test_templates.py`, testar a renderização: `home.html` mostra o título das tarefas, o formulário (título e energia), os botões concluir/mover/editar/excluir e o estado vazio; com o dia cheio mostra o painel com o rascunho em campos ocultos, o botão "Guardar para depois" e um "Concluir e adicionar" por tarefa; `later.html` lista as tarefas com "Trazer para o dia" e mostra o estado vazio; `edit.html` mostra o formulário e os erros em português; todos os formulários POST trazem o token CSRF
- [X] T018 [P] [US1] Criar `tasks/tests/test_integration.py` (marcador `integration`) com o fluxo completo: criar 3 tarefas; tentar a quarta e ver o painel; "Guardar para depois" e conferir Para depois; repetir a quarta e usar "Concluir e adicionar" (uma concluída, a nova no dia); trazer de Para depois com o dia cheio e ver a mensagem sem mudança

### Implementation for User Story 1 (Green)

- [X] T019 [US1] Em `tasks/services.py`, implementar `create_task(title, energy, destination)` e `move_task(task, to)`, ambos dentro de `transaction.atomic()` com `select_for_update()` na contagem de `today`, levantando `DayFullError` quando já houver `DAY_LIMIT` pendentes no destino `today` (FR-002, FR-003, FR-005). Mapeamento dos termos da interface: `hoje → today`, `depois → later`
- [X] T020 [US1] Em `tasks/services.py`, implementar `complete_task(task, new_title=None, new_energy=None)` (define `status = done` e `completed_at`; se `new_title` vier preenchido, cria a nova em `today` na mesma transação) (FR-006), além de `update_task(task, title, energy)` e `delete_task(task)` (FR-007); rodar `test_services.py` até ficar verde
- [X] T021 [US1] Em `tasks/views.py`, implementar `home`, `later`, `task_create`, `task_complete`, `task_move`, `task_update` (GET e POST de editar) e `task_delete` conforme contracts/ui-routes.md, usando `TaskForm`; as views só chamam `services`; as rotas de escrita aceitam só POST (`require_POST`); `task_create` e `task_move` capturam `DayFullError` (painel de dia cheio no primeiro, mensagem amigável em `later` no segundo); 404 para ids inexistentes
- [X] T022 [US1] Registrar as rotas de T021 em `tasks/urls.py`: `/` (`home`), `/depois/` (`later`), `/tarefas/nova/`, `/tarefas/<id>/concluir/`, `/tarefas/<id>/mover/`, `/tarefas/<id>/editar/`, `/tarefas/<id>/excluir/`
- [X] T023 [US1] Criar `tasks/templates/tasks/home.html`: lista do dia (até 3) com ações concluir, mover para depois, editar e excluir; formulário de nova tarefa (título e energia); estado vazio; mensagem de dia concluído; painel "Seu dia está cheio" com o rascunho em campos ocultos, "Guardar para depois" e, ao lado de cada tarefa, "Concluir e adicionar"
- [X] T024 [P] [US1] Criar `tasks/templates/tasks/later.html` (lista de Para depois com "Trazer para o dia" e excluir, e estado vazio) e `tasks/templates/tasks/edit.html` (formulário de título e energia com erros em português)
- [X] T025 [US1] Rodar `uv run pytest` até todos os níveis da US1 (models, forms, views, templates e integração) ficarem verdes; refatorar mantendo a suíte verde

**Checkpoint**: US1 funciona sozinha e é o MVP

---

## Phase 4: User Story 2 - Modo foco com cronômetro (Priority: P2)

**Goal**: Clicar em "Fazer agora", ver só a tarefa e um cronômetro, e ao concluir ver a próxima.

**Independent Test**: Com 2 tarefas no dia, iniciar o foco, recarregar (o cronômetro continua), concluir e ver a próxima; concluir a última e ver a mensagem de dia concluído (quickstart, passo 3).

### Tests for User Story 2 (Red)

- [X] T026 [P] [US2] Em `tasks/tests/test_services.py` (nova classe), testar o foco usando a fixture `clock`: `start_focus` marca `focus_started_at`; **chamar `start_focus` de novo na mesma tarefa (recarga da página) não reinicia `focus_started_at` nem o tempo decorrido**; iniciar foco em outra tarefa encerra o foco da anterior e acumula o tempo; `leave_focus` soma o intervalo em `focus_seconds` e zera `focus_started_at`; `elapsed_seconds` = acumulado + decorrido; `complete_task` em foco também acumula o tempo; mover para depois ou excluir encerra o foco; `next_task` devolve a pendente mais antiga do dia ou `None`
- [X] T027 [P] [US2] Em `tasks/tests/test_views.py` (nova classe), testar: `focus` responde 404 se a tarefa não estiver em `today`; abrir `focus` duas vezes mantém o tempo (usando `clock`); `focus_complete` redireciona para o foco da próxima, ou para `home` com a mensagem de dia concluído; `focus_leave` mantém a tarefa pendente e acumula o tempo; ambas só aceitam POST
- [X] T028 [P] [US2] Em `tasks/tests/test_templates.py`, testar `focus.html`: contém o título da tarefa, o cronômetro com o tempo inicial em atributo `data-` e os botões "Concluir" e "Sair do foco"; **não** contém os links da navegação base (bloco `nav` vazio) nem o formulário de nova tarefa; `home.html` mostra "Fazer agora" em cada tarefa do dia
- [X] T029 [P] [US2] Em `tasks/tests/test_integration.py`, testar a jornada: com 2 tarefas, "Fazer agora"; recarregar a página de foco e conferir que o tempo continua (com `clock`); concluir e cair no foco da segunda; concluir a última e ver o dia concluído; em outra tarefa, "Sair do foco" mantém pendente

### Implementation for User Story 2 (Green)

- [X] T030 [US2] Em `tasks/services.py`, implementar `start_focus(task)` (encerra qualquer outro foco ativo; só define `focus_started_at = agora` se ainda for nulo), `leave_focus(task)` (soma o intervalo em `focus_seconds`, que nunca fica negativo, e zera `focus_started_at`), `elapsed_seconds(task)` e `next_task(only_light=False)` (a pendente mais antiga do dia); ajustar `complete_task`, `move_task` (para `later`) e `delete_task` para encerrarem o foco antes de mudar o estado (invariante 2 do data-model.md); rodar `test_services.py` até ficar verde
- [X] T031 [US2] Em `tasks/views.py`, implementar `focus` (GET: 404 se não estiver em `today`, chama `start_focus`, entrega `elapsed_seconds` ao template), `focus_complete` (conclui; redireciona para `/foco/<proxima>/` ou para `home` com a mensagem de dia concluído) e `focus_leave` (chama `leave_focus` e volta para `home`); registrar `/foco/<id>/`, `/foco/<id>/concluir/` e `/foco/<id>/sair/` em `tasks/urls.py` (as duas últimas só POST)
- [X] T032 [US2] Criar `tasks/templates/tasks/focus.html` estendendo `base.html` e sobrescrevendo `{% block nav %}` vazio: somente título da tarefa, cronômetro e os botões "Concluir" e "Sair do foco" (FR-012)
- [X] T033 [P] [US2] Criar `tasks/static/tasks/focus.js`: lê o tempo inicial do atributo `data-` e atualiza o cronômetro (`mm:ss`, ou `h:mm:ss` a partir de 1 hora) a cada segundo, sem requisições
- [X] T034 [US2] Adicionar o botão "Fazer agora" (leva a `/foco/<id>/`) a cada tarefa em `tasks/templates/tasks/home.html` e os estilos da tela de foco (texto grande, cronômetro centralizado, fundo limpo) em `tasks/static/tasks/app.css`
- [X] T035 [US2] Rodar `uv run pytest` até todos os níveis da US2 ficarem verdes; refatorar mantendo a suíte verde

**Checkpoint**: US1 e US2 funcionam de forma independente

---

## Phase 5: User Story 3 - Nível de energia e filtro "Estou cansado" (Priority: P3)

**Goal**: Ver o nível de cada tarefa e filtrar só as leves quando estiver cansado.

**Independent Test**: Criar tarefas leve, média e pesada, ativar "Estou cansado" e ver só as leves; sem leves, ver o aviso (quickstart, passo 2).

**Regras definidas nesta fase (resolvem lacunas da análise)**:
- O parâmetro `cansado=1` viaja nos formulários POST por um campo oculto `cansado` e nos links por querystring; os redirecionamentos o preservam.
- Se, com o filtro ativo, a pessoa conclui a última tarefa leve e ainda restam tarefas pendentes de outros níveis, `focus_complete` volta para `home?cansado=1` com a mensagem "Acabaram as tarefas leves de hoje. Desative o filtro para ver as outras." Só aparece "dia concluído" quando não resta nenhuma pendente.

### Tests for User Story 3 (Red)

- [X] T036 [P] [US3] Em `tasks/tests/test_services.py`, testar o filtro: `day_tasks(only_light=True)` devolve só `energy = light`; `next_task(only_light=True)` ignora médias e pesadas e devolve `None` se não houver leves
- [X] T037 [P] [US3] Em `tasks/tests/test_views.py`, testar: `home?cansado=1` lista apenas leves (SC-004); sem leves, o contexto sinaliza o aviso; `focus_complete` com `cansado` vai para a próxima leve; ao concluir a última leve com outras pendentes, redireciona para `home?cansado=1` com a mensagem "Acabaram as tarefas leves de hoje…"; sem nenhuma pendente, mensagem de dia concluído; um POST (concluir, mover, excluir, criar) com o campo `cansado=1` redireciona preservando `?cansado=1`
- [X] T038 [P] [US3] Em `tasks/tests/test_templates.py`, testar: cada tarefa mostra um selo com o rótulo em texto (Leve, Média ou Pesada) e a classe `energy-*` correspondente; o alternador "Estou cansado" aparece ligado ou desligado conforme o parâmetro; o aviso "não há tarefas leves" traz o link para desativar o filtro; os formulários POST incluem o campo oculto `cansado` quando o filtro está ativo
- [X] T039 [P] [US3] Em `tasks/tests/test_integration.py`, testar a jornada: criar tarefas leve, média e pesada (sem escolher nível = Média); ativar "Estou cansado" e ver só a leve; iniciar foco e concluir a leve; ver a mensagem "Acabaram as tarefas leves…"; desativar o filtro e ver as demais

### Implementation for User Story 3 (Green)

- [X] T040 [US3] Em `tasks/services.py`, adicionar `only_light=False` a `day_tasks()`, filtrando por `energy = light` quando verdadeiro (`next_task` já o aceita desde T030); adicionar `has_pending(only_light=False)` para distinguir "sem leves" de "sem pendentes"; rodar `test_services.py` até ficar verde
- [X] T041 [US3] Em `tasks/views.py`, ler `cansado` da querystring (GET) ou do campo oculto (POST) em `home`, `later`, `task_*` e `focus_*`, passar `only_light` aos serviços, preservar o parâmetro nos redirecionamentos e aplicar a regra da mensagem "Acabaram as tarefas leves…" em `focus_complete` (research.md, item 6)
- [X] T042 [US3] Em `tasks/templates/tasks/home.html` e `later.html`, exibir o selo de energia com rótulo em texto em cada tarefa, o alternador "Estou cansado" (liga e desliga), o aviso "não há tarefas leves" com o link para desativar o filtro, e o campo oculto `cansado` em todos os formulários POST quando o filtro estiver ativo
- [X] T043 [P] [US3] Em `tasks/static/tasks/app.css`, definir as cores dos selos `energy-light`, `energy-medium` e `energy-heavy` com contraste legível e o estilo do alternador
- [X] T044 [US3] Rodar `uv run pytest` até todos os níveis da US3 ficarem verdes; refatorar mantendo a suíte verde

**Checkpoint**: As três histórias funcionam de forma independente

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T045 [P] Escrever em `README.md` uma descrição curta da app e os comandos (`uv sync`, `migrate`, `runserver`, `uv run pytest`)
- [X] T046 Rodar a suíte completa com cobertura: `uv run pytest --cov=tasks --cov-report=term-missing`; confirmar que models, forms, views, templates e integração estão verdes e cobrir qualquer linha de regra de negócio sem teste
- [X] T047 Percorrer o roteiro manual de `specs/001-foco-tres-tarefas/quickstart.md` (passos 1 a 5) com `uv run python manage.py runserver` e corrigir divergências
- [X] T048 [P] Revisar o layout em largura de celular (aprox. 375 px) e em desktop: sem rolagem horizontal, botões tocáveis, selos de energia legíveis (FR-009, SC-007)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências; T003 depende de T001; T005 depende de T004
- **Foundational (Phase 2)**: depende do Setup; bloqueia todas as histórias
- **User Stories (Phases 3 a 5)**: dependem da Foundational
  - US1 é o MVP e não depende de outra história
  - US2 reaproveita `home.html`, `views.py` e `services.py` da US1, então vem depois dela
  - US3 altera `home.html`, `views.py` e `services.py`; implementar depois de US1 e US2 (`next_task` nasce na US2)
- **Polish (Phase 6)**: depende das histórias desejadas

### Within Each User Story (TDD)

- Testes de models, forms, views, templates e integração primeiro, vistos falhando (Red)
- Depois serviços, views/rotas e templates (Green)
- Fechar com refatoração e `uv run pytest` verde
- `services.py`, `views.py`, `home.html` e os arquivos de teste são compartilhados entre histórias, por isso as histórias seguem em sequência (P1 → P2 → P3)

### Parallel Opportunities

- Setup: T002 em paralelo com T003; T005 em paralelo com as demais depois de T004
- Foundational: T006, T007 e T008 em paralelo (testes); T011, T012 e T013 em paralelo depois de T010
- US1: T015 a T018 em paralelo (testes); T024 em paralelo com outras tarefas de template
- US2: T026 a T029 em paralelo; T033 em paralelo com T031/T032
- US3: T036 a T039 em paralelo; T043 em paralelo com T040 a T042
- Polish: T045 e T048 em paralelo

### Parallel Example: User Story 1

```text
# Testes (Red) juntos:
T015 tasks/tests/test_services.py
T016 tasks/tests/test_views.py
T017 tasks/tests/test_templates.py
T018 tasks/tests/test_integration.py
```

---

## Implementation Strategy

### MVP First (apenas User Story 1)

1. Phase 1 (Setup) e Phase 2 (Foundational)
2. Phase 3 (US1), com Red → Green → Refactor
3. **PARAR e VALIDAR**: `uv run pytest` verde nos cinco níveis e o passo 1 do quickstart
4. Já é utilizável como planejador diário com limite de 3

### Incremental Delivery

1. Setup + Foundational: base pronta e testada
2. US1: limite de 3 e Para depois (MVP)
3. US2: modo foco com cronômetro
4. US3: energia e filtro "Estou cansado"
5. Polish: README, cobertura e roteiro manual

## Notes

- [P] = arquivos diferentes, sem dependência de tarefa incompleta
- Confirmar que cada teste falha pelo motivo certo antes de implementar
- Fazer commit ao fim de cada tarefa ou grupo lógico
- Toda escrita que leve tarefas a `today` passa por `services.py`; nenhuma view contorna o limite
- O `select_for_update()` é ignorado pelo SQLite, mas a transação já serializa as escritas; mantê-lo deixa o código correto se o banco mudar
- O `CLAUDE.md` cita `manage.py test` como comando geral; esta feature usa `pytest` conforme a skill `django-tdd` exigida pelo mesmo arquivo
