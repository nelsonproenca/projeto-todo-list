# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Freshly scaffolded Django project (Django >= 6.1, Python >= 3.12, managed with `uv`). No todo app exists yet: `INSTALLED_APPS` contains only Django's built-ins, and `core/urls.py` only routes `admin/`. README.md is empty.

## Commands

```
uv sync                              # install dependencies
uv run python manage.py runserver    # dev server
uv run python manage.py startapp <name>   # create an app (then add it to INSTALLED_APPS in core/settings.py)
uv run python manage.py makemigrations && uv run python manage.py migrate
uv run python manage.py test                       # run all tests
uv run python manage.py test <app>.tests.<Class>.<test_method>   # single test
```

No linter or formatter is configured.

## Layout

- `core/` is the Django project package (settings, root URLconf, ASGI/WSGI). `manage.py` uses `core.settings`.
- Database is SQLite at `db.sqlite3` in the repo root (currently untracked in git).
- `src/projeto_todo_list/` is the uv-packaged Python module (`pyproject.toml` uses the `uv_build` backend, with a placeholder `projeto-todo-list` console script). It is unrelated to the Django project in `core/`; new Django apps should be created at the repo root alongside `core/`, not inside `src/`, unless the layout is deliberately changed.

## TDD workflow (mandatory for every new feature)

Para cada nova funcionalidade, siga obrigatoriamente a skill [`.claude/skills/django-tdd`](.claude/skills/django-tdd) — escreva os testes **antes** da implementação (Red → Green → Refactor). 

Cobertura mínima exigida por funcionalidade: 
- **Models** — campos, validações, métodos, `__str__`, constraints. 
- **Forms** — validação de campos, `clean_*`, mensagens de erro. 
- **Views** — status codes, contexto, permissões, redirecionamentos. 
- **Templates** — renderização, blocos, presença de elementos esperados. 
- **Integração** — fluxo end-to-end cobrindo a jornada do usuário. 

Só marque a funcionalidade como concluída depois que todos esses níveis de testes estiverem verdes. 
