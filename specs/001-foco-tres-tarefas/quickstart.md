# Quickstart: validar a feature de ponta a ponta

## Pré-requisitos

```
uv sync   # inclui pytest, pytest-django, factory-boy e pytest-cov
uv run python manage.py makemigrations tasks
uv run python manage.py migrate
```

O app `tasks` precisa estar em `INSTALLED_APPS` e as rotas incluídas em `core/urls.py` (ver [plan.md](plan.md)).

## Testes automatizados

```
uv run pytest --cov=tasks --cov-report=term-missing
```

Esperado: todos passam, incluindo os que cobrem o limite de 3, mover entre listas, nível de energia e filtro, fluxo de foco e jornadas de integração (models, forms, views, templates).

## Rodar o site

```
uv run python manage.py runserver
```

Abra http://127.0.0.1:8000/.

## Roteiro manual

Rotas e campos: [contracts/ui-routes.md](contracts/ui-routes.md). Campos e regras: [data-model.md](data-model.md).

1. **Limite de 3 (US1, SC-001)**
   - Crie 3 tarefas. Todas aparecem no dia.
   - Tente criar a quarta. Esperado: nada é criado e aparece "Seu dia está cheio" com as saídas "Guardar para depois" e "Concluir e adicionar" ao lado de cada tarefa.
   - Escolha "Guardar para depois". Esperado: a tarefa aparece em Para depois e o dia segue com 3.
   - Repita a quarta e use "Concluir e adicionar". Esperado: uma tarefa fica concluída e a nova entra no dia.
   - Em Para depois, tente "Trazer para o dia" com o dia cheio. Esperado: mensagem amigável e nada muda.
2. **Energia e filtro (US3, SC-004)**
   - Crie tarefas leve, média e pesada. Cada uma mostra rótulo e cor próprios. Sem escolher nível, vale "Média".
   - Ative "Estou cansado". Esperado: só as leves. Sem leves, aparece o aviso com opção de desativar o filtro.
3. **Foco (US2, SC-003, SC-005)**
   - Clique em "Fazer agora". Esperado: tela só com a tarefa, o cronômetro rodando e "Concluir" / "Sair do foco".
   - Recarregue a página. Esperado: o cronômetro continua do tempo decorrido, sem reiniciar.
   - Clique em "Concluir". Esperado: aparece a próxima tarefa do dia (só leves se o filtro estiver ativo).
   - Conclua a última. Esperado: mensagem de dia concluído na tela inicial.
   - Em outra tarefa, use "Sair do foco". Esperado: ela continua pendente.
4. **Persistência (SC-006)**: pare e reinicie o servidor. Esperado: tarefas, níveis e estados iguais.
5. **Título vazio**: envie o formulário só com espaços. Esperado: erro pedindo um título.
