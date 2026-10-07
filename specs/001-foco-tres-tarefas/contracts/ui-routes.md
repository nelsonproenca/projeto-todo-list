# UI Contract: Rotas e telas

O app não expõe API para terceiros. O contrato é o conjunto de rotas HTML e formulários. Todas as escritas são `POST` com CSRF e terminam em redirecionamento (exceto quando o dia está cheio). O parâmetro `cansado=1` (filtro "Estou cansado") é preservado em links (querystring), em formulários POST (campo oculto `cansado`) e em redirecionamentos.

## Telas (GET)

| Rota | Nome | Conteúdo |
|------|------|----------|
| `/` | `home` | Lista do dia (até 3), formulário "nova tarefa" (título + energia), alternador "Estou cansado", link para Para depois. Botão "Fazer agora" em cada tarefa. Estado vazio e mensagem de dia concluído. |
| `/depois/` | `later` | Tarefas de Para depois com ações "Trazer para o dia" e excluir. |
| `/tarefas/<id>/editar/` | `edit` | Formulário de título e energia. |
| `/foco/<id>/` | `focus` | Somente: título da tarefa, cronômetro, botões "Concluir" e "Sair do foco". Sem navegação nem outros elementos. Ao abrir, marca o início do foco. Responde 404 se a tarefa não estiver em `today`. |

## Ações (POST)

| Rota | Nome | Entrada | Resultado |
|------|------|---------|-----------|
| `/tarefas/nova/` | `task_create` | `title`, `energy`, `destino` (`hoje` padrão, ou `depois`) | Cria a tarefa e redireciona para `home`. Se `destino=hoje` e o dia está cheio: **200** renderizando `home` com o painel "dia cheio" (nada é criado). Título inválido: reexibe o formulário com erro. |
| `/tarefas/<id>/concluir/` | `task_complete` | opcionais `novo_title`, `novo_energy` | Conclui a tarefa. Se `novo_title` vier preenchido (fluxo "Concluir e adicionar"), cria também a nova tarefa em `today` na mesma transação. Redireciona para `home`. |
| `/tarefas/<id>/mover/` | `task_move` | `para` (`hoje`/`depois`) | Move a tarefa. `para=hoje` com dia cheio: reexibe `later` com mensagem de erro amigável, sem mover. |
| `/tarefas/<id>/editar/` | `task_update` | `title`, `energy` | Atualiza e redireciona para `home`. |
| `/tarefas/<id>/excluir/` | `task_delete` | nenhuma | Exclui e redireciona para `home`. |
| `/foco/<id>/concluir/` | `focus_complete` | nenhuma | Acumula o tempo, conclui, e redireciona para `/foco/<proxima>/` respeitando `cansado`; sem próxima, redireciona para `home` com a mensagem de dia concluído. Com `cansado` ativo e sem mais leves, mas com outras tarefas pendentes, redireciona para `home?cansado=1` com a mensagem "Acabaram as tarefas leves de hoje. Desative o filtro para ver as outras." |
| `/foco/<id>/sair/` | `focus_leave` | nenhuma | Acumula o tempo, mantém a tarefa pendente e redireciona para `home`. |

## Regras de contrato

- Toda criação ou movimentação para `today` passa pelo serviço que impõe o limite de 3 (FR-002, FR-003).
- Respostas de erro usam mensagens em português, curtas e sem jargão (FR-016).
- A tela de foco não carrega o cabeçalho, o rodapé nem os links da base (FR-012, SC-005).
- Nenhuma rota exige login ou configuração (FR-017).
- IDs inexistentes respondem 404.
