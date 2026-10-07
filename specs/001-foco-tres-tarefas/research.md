# Research: Lista de Tarefas com Foco em 3 Tarefas do Dia

Não havia itens `NEEDS CLARIFICATION` no Technical Context. As decisões abaixo fecham as escolhas de design.

## 1. Renderização e interatividade

- **Decision**: Templates Django com formulários POST e redirecionamento (POST/Redirect/GET). JS vanilla apenas para o cronômetro.
- **Rationale**: O pedido é "simples, limpo, sem configurações". Páginas renderizadas no servidor mantêm o estado correto (limite de 3) sem lógica duplicada no cliente e sem build de front-end.
- **Alternatives considered**: SPA com API REST (mais código e regra duplicada); HTMX (útil, mas uma dependência a mais sem ganho claro para 3 telas).

## 2. Persistência e usuário

- **Decision**: SQLite via ORM do Django, sem autenticação. Os dados pertencem à instância do app.
- **Rationale**: A spec assume uma única pessoa e que os dados sobrevivem a fechar e reabrir. O banco já está configurado.
- **Alternatives considered**: `localStorage` (perde dados ao limpar o navegador e não compartilha entre dispositivos); contas de usuário (fora do escopo).
- **Risco anotado**: se o site for exposto publicamente, qualquer visitante vê e altera as mesmas tarefas. Adequado para uso local ou pessoal; autenticação seria uma feature futura.

## 3. Aplicação do limite de 3

- **Decision**: Camada de serviço com transação e `select_for_update` no ponto único de escrita. Toda criação ou movimentação para o dia passa por `services`, que conta as tarefas com status "hoje" e levanta `DayFullError` se já houver 3. Views e testes usam o serviço.
- **Rationale**: O limite é a regra central do produto (SC-001, 100%). Centralizar evita caminhos que o contornem (por exemplo, mover de "Para depois" ou editar).
- **Alternatives considered**: Constraint de banco (SQLite não expressa "no máximo 3 linhas com status X" sem triggers); validação só no formulário (burlável por outras views).

## 4. Fluxo "quarta tarefa"

- **Decision**: Ao receber `DayFullError`, a view reexibe a tela inicial com um painel "Seu dia está cheio" contendo o rascunho (título e energia em campos ocultos) e duas saídas: "Guardar para depois" (cria direto em Para depois) ou, ao lado de cada uma das 3 tarefas, "Concluir e adicionar" (conclui a tarefa e cria o rascunho no dia, numa única transação). Ignorar o painel não cria nada.
- **Rationale**: Atende às acceptance scenarios 2 a 4 da US1 sem modal em JS e sem estado de rascunho persistido.
- **Alternatives considered**: Criar o rascunho em Para depois automaticamente (tira da pessoa a escolha pedida na spec).

## 5. Cronômetro e persistência do tempo

- **Decision**: A tarefa guarda `focus_seconds` (acumulado) e `focus_started_at` (nulo quando fora de foco). Tempo exibido = `focus_seconds` + (agora − `focus_started_at`). O servidor entrega o valor inicial e o JS só incrementa na tela a cada segundo. Ao concluir ou sair do foco, o servidor soma o intervalo em `focus_seconds` e zera `focus_started_at`.
- **Rationale**: Recarregar ou fechar a página não perde nem reinicia o tempo (edge case da spec), e não há requisições por segundo.
- **Alternatives considered**: Contar só no cliente (perde ao recarregar); enviar batidas periódicas (tráfego desnecessário).
- **Nota**: se a pessoa fechar a aba sem sair do foco, o relógio continua correndo até ela voltar e sair ou concluir. É um comportamento aceito e simples; o tempo exibido reflete o tempo real desde o início do foco.

## 6. Próxima tarefa e filtro "Estou cansado"

- **Decision**: O filtro vive no parâmetro de URL `cansado=1`, repassado nos links e redirecionamentos. Após concluir em foco, o serviço escolhe a próxima tarefa pendente do dia (ordem de criação), restrita a leves se o filtro estiver ativo. Sem próxima: tela inicial com mensagem de dia concluído.
- **Rationale**: Sem sessão nem configuração; o estado é visível e compartilhável.
- **Alternatives considered**: Guardar o filtro na sessão ou no banco (estado oculto, contrário a "sem configurações").

## 7. Virada do dia

- **Decision**: Não existe "dia" como entidade. A lista do dia é o conjunto de tarefas com status "hoje"; pendentes continuam nela após a meia-noite.
- **Rationale**: Está na spec (Assumptions). Evita job agendado e perda de tarefas.
- **Alternatives considered**: Rolagem diária automática para Para depois (contraria a suposição documentada).

## 8. Localização

- **Decision**: Ajustar `LANGUAGE_CODE` para `pt-br` e `TIME_ZONE` para `America/Sao_Paulo` em `core/settings.py`; textos da interface escritos direto nos templates em português.
- **Rationale**: A spec define pt-BR. Uma única língua não justifica catálogo de traduções.
- **Alternatives considered**: `gettext` em todos os textos (desnecessário agora).

## 9. Visual

- **Decision**: CSS próprio, pouco e claro: uma coluna centralizada, tipografia grande, cores distintas por nível (leve, média, pesada) sempre acompanhadas de rótulo de texto, foco com tela quase vazia.
- **Rationale**: "Limpo e direto ao ponto"; a cor nunca é o único sinal (acessibilidade).
- **Alternatives considered**: Framework CSS (peso e dependência para 4 telas).
