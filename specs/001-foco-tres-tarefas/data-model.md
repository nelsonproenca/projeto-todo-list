# Data Model: Lista de Tarefas com Foco em 3 Tarefas do Dia

Um único modelo persistido, `Task` (app `tasks`). "Lista do dia", "Para depois" e "Sessão de foco" são visões e estados derivados dele.

## Task

| Campo | Tipo | Regras |
|-------|------|--------|
| `title` | texto curto (até 120) | Obrigatório; espaços nas pontas removidos; não pode ficar vazio (FR-001, edge case) |
| `energy` | escolha: `light`, `medium`, `heavy` | Padrão `medium` (FR-008); rótulos: Leve, Média, Pesada |
| `status` | escolha: `today`, `later`, `done` | Padrão `today` no modelo, mas a criação passa pelo serviço |
| `created_at` | data/hora | Automático; define a ordem de exibição e a "próxima tarefa" |
| `completed_at` | data/hora, opcional | Preenchido ao concluir; nulo caso contrário |
| `focus_seconds` | inteiro >= 0 | Tempo acumulado em foco; padrão 0 |
| `focus_started_at` | data/hora, opcional | Não nulo apenas enquanto a tarefa está em foco |

### Visões derivadas

- **Lista do dia**: `status = today`, ordenada por `created_at`. Máximo 3 linhas (FR-002).
- **Para depois**: `status = later`, sem limite (FR-004).
- **Concluídas**: `status = done`; não ocupam vaga (FR-006).
- **Filtro "Estou cansado"**: restringe qualquer visão acima a `energy = light` (FR-010).
- **Tempo em foco exibido**: `focus_seconds` + (agora − `focus_started_at`), se este não for nulo.

## Invariantes

1. Nunca existem mais de 3 tarefas com `status = today`. Garantido em `services` dentro de transação (ver research.md, item 3).
2. `focus_started_at` não nulo implica `status = today`. Mover para Para depois, concluir ou excluir encerra o foco (acumula o tempo e zera `focus_started_at`).
3. Apenas uma tarefa em foco por vez: iniciar o foco em outra encerra o foco anterior.
4. `completed_at` não nulo se, e somente se, `status = done`.

## Transições de estado

```text
        criar (se há vaga)                       concluir
 (novo) ───────────────────► today ─────────────────────────► done
   │                          │  ▲                              │
   │ criar / guardar          │  │ mover para o dia (se há vaga)│ (sem reabrir nesta versão)
   └────────────► later ◄─────┘  │                              
                    │ ▲  mover p/ depois                        
                    └─┴──────────────────────────────────────────
                    concluir direto de later: não oferecido
```

- `today → later`: sempre permitido.
- `later → today`: só se houver menos de 3 em `today`; senão `DayFullError`.
- `today → done`: sempre permitido; libera a vaga.
- `done` é terminal nesta versão (reabrir está fora do escopo). Concluídas podem ser excluídas.
- Excluir é permitido em qualquer estado.

## Erros de domínio

- `DayFullError`: criar em `today` ou mover para `today` com 3 pendentes. A view converte em painel "Seu dia está cheio" (research.md, item 4).
- Validação de título vazio é feita no formulário (`TaskForm`) e também no serviço.
