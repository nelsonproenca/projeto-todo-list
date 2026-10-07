# Implementation Plan: Lista de Tarefas com Foco em 3 Tarefas do Dia

**Branch**: `001-foco-tres-tarefas` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-foco-tres-tarefas/spec.md`

## Summary

Site de lista de tarefas de uma única pessoa, com limite rígido de 3 tarefas pendentes no dia, lista "Para depois", nível de energia (leve/média/pesada) com filtro "Estou cansado" e modo foco de tela cheia com cronômetro. A abordagem é um app Django renderizado no servidor (templates + formulários POST), com um app `tasks` na raiz do repositório e SQLite. A regra do limite de 3 fica numa camada de serviço transacional, que é a única porta de escrita. JavaScript só atualiza o cronômetro na tela. O tempo decorrido é calculado no servidor, então sobrevive a recargas (ver [research.md](research.md)).

## Technical Context

**Language/Version**: Python >= 3.12 (Django >= 6.1)

**Primary Dependencies**: Django (já instalado); nenhuma dependência nova. Front-end com templates Django, CSS próprio e um pequeno JS vanilla para o cronômetro.

**Storage**: SQLite (`db.sqlite3`, já configurado)

**Testing**: pytest + pytest-django + factory_boy + pytest-cov (skill `django-tdd`, TDD obrigatório); `uv run pytest`

**Target Platform**: Navegadores modernos, desktop e celular (layout responsivo)

**Project Type**: web-application (monólito Django renderizado no servidor)

**Performance Goals**: Páginas respondem de forma imperceptível (< 200 ms no uso local); o cronômetro atualiza a cada segundo sem requisições.

**Constraints**: Sem login nem multiusuário; sem telas de configuração; interface em pt-BR; modo foco com apenas tarefa, cronômetro e controles.

**Scale/Scope**: Uma pessoa; 3 telas (início, foco, Para depois) mais edição de tarefa; centenas de tarefas no máximo.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` ainda é o template em branco, sem princípios ratificados. Não há gates a avaliar. Os princípios implícitos do projeto (CLAUDE.md) são seguidos: app novo na raiz ao lado de `core/`, registrado em `INSTALLED_APPS`, sem tocar em `src/`. Passa antes e depois do design.

## Project Structure

### Documentation (this feature)

```text
specs/001-foco-tres-tarefas/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/
│   └── ui-routes.md     # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
core/                         # projeto Django (settings: INSTALLED_APPS, LANGUAGE_CODE/TIME_ZONE, urls)
tasks/                        # novo app Django
├── models.py                 # Task
├── services.py               # regras: limite de 3, mover, concluir, foco (transacional)
├── forms.py                  # TaskForm (título + energia)
├── views.py                  # views finas que chamam services
├── urls.py
├── migrations/
├── templates/tasks/
│   ├── base.html
│   ├── home.html             # lista do dia, filtro, painel "dia cheio"
│   ├── later.html            # Para depois
│   ├── edit.html
│   └── focus.html            # modo foco (sem navegação)
├── static/tasks/
│   ├── app.css
│   └── focus.js              # cronômetro
└── tests/
    ├── conftest.py           # fixture `clock`
    ├── factories.py          # TaskFactory
    ├── test_models.py
    ├── test_forms.py
    ├── test_services.py      # limite, mover, concluir, foco
    ├── test_views.py         # fluxos de tela
    ├── test_templates.py
    └── test_integration.py   # jornadas end-to-end
```

**Structure Decision**: Um único app Django `tasks` na raiz, ao lado de `core/`, conforme o CLAUDE.md. As regras de negócio ficam em `services.py` para que o limite de 3 seja testável sem passar por HTTP e não possa ser burlado por nenhuma view.

## Complexity Tracking

Sem violações; seção não aplicável.
