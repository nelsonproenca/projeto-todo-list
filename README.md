# Foco 3 — lista de tarefas enxuta

Uma lista de tarefas que não deixa você acumular. Só 3 tarefas pendentes no dia: para entrar uma quarta, conclua uma das três ou guarde-a em **Para depois**.

- **Limite de 3 por dia** com painel "Seu dia está cheio" (concluir e adicionar, ou guardar para depois).
- **Energia** por tarefa (Leve, Média, Pesada) e filtro **Estou cansado**, que mostra só as leves.
- **Modo foco**: uma tarefa por vez, com cronômetro; ao concluir, aparece a próxima.

Uso pessoal, sem login. A especificação completa está em `specs/001-foco-tres-tarefas/`.

## Rodar

```
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Abra http://127.0.0.1:8000/.

## Testes

```
uv run pytest
uv run pytest --cov=tasks --cov-report=term-missing
```
