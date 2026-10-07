# Feature Specification: Lista de Tarefas com Foco em 3 Tarefas do Dia

**Feature Branch**: `001-foco-tres-tarefas`

**Created**: 2026-10-03

**Status**: Draft

**Input**: User description: "Aplicativo/site bem simples de lista de tarefas, enxuto e 'inteligente': no máximo 3 tarefas no dia (a 4ª exige concluir uma ou guardar para depois), nível de energia por tarefa (leve, média ou pesada) com filtro para quando estiver cansado, modo foco com uma tarefa por vez e cronômetro, visual limpo e sem muitas configurações."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Limite de 3 tarefas no dia (Priority: P1)

A pessoa monta o seu dia com no máximo 3 tarefas. Ao tentar adicionar uma quarta, o app impede e oferece duas saídas: concluir uma das três tarefas atuais ou guardar a nova tarefa em uma lista "Para depois". Isso evita o acúmulo de dezenas de itens e a sensação de sobrecarga.

**Why this priority**: É a ideia central do produto. Sem o limite, o app é só mais uma lista tradicional.

**Independent Test**: Adicionar 3 tarefas ao dia, tentar adicionar uma quarta e verificar que o app bloqueia a adição direta e oferece "concluir uma" ou "guardar para depois". Entrega valor sozinho como um planejador diário enxuto.

**Acceptance Scenarios**:

1. **Given** o dia tem 0, 1 ou 2 tarefas, **When** a pessoa adiciona uma nova tarefa, **Then** ela aparece na lista do dia.
2. **Given** o dia já tem 3 tarefas pendentes, **When** a pessoa tenta adicionar uma quarta, **Then** o app não a coloca no dia e apresenta as opções "concluir uma das três" ou "guardar para depois".
3. **Given** o app apresentou as opções ao tentar adicionar a quarta, **When** a pessoa escolhe "guardar para depois", **Then** a nova tarefa vai para a lista "Para depois" e o dia continua com 3 tarefas.
4. **Given** o app apresentou as opções, **When** a pessoa conclui uma das três tarefas, **Then** abre-se uma vaga e a nova tarefa entra no dia.
5. **Given** o dia tem 3 tarefas, **When** a pessoa move uma tarefa do dia para "Para depois", **Then** a vaga é liberada.
6. **Given** a lista "Para depois" tem tarefas e o dia tem menos de 3, **When** a pessoa traz uma tarefa de "Para depois" para o dia, **Then** ela entra no dia; se o dia já tem 3, o mesmo bloqueio se aplica.

---

### User Story 2 - Modo foco com cronômetro (Priority: P2)

Ao decidir fazer uma tarefa, a pessoa clica em um botão e vê somente aquela tarefa na tela, com um cronômetro e sem nenhum outro elemento de distração. Ao concluir, o app mostra a próxima tarefa do dia.

**Why this priority**: É o diferencial no momento da execução. Já entrega valor com qualquer lista de tarefas do dia.

**Independent Test**: Com ao menos 2 tarefas no dia, iniciar o foco em uma, verificar que só ela e o cronômetro aparecem, concluí-la e ver a próxima tarefa ser apresentada.

**Acceptance Scenarios**:

1. **Given** o dia tem tarefas pendentes, **When** a pessoa clica em "Fazer agora" em uma tarefa, **Then** a tela mostra apenas o título dessa tarefa, um cronômetro rodando e os controles de concluir e sair do foco.
2. **Given** a tarefa está em foco, **When** a pessoa a conclui, **Then** o app mostra a próxima tarefa pendente do dia.
3. **Given** a tarefa concluída era a última pendente do dia, **When** a pessoa a conclui, **Then** o app exibe uma mensagem de dia concluído e volta à tela principal.
4. **Given** a tarefa está em foco, **When** a pessoa sai do foco sem concluir, **Then** a tarefa continua pendente e a pessoa volta à lista do dia.

---

### User Story 3 - Nível de energia e filtro "estou cansado" (Priority: P3)

Cada tarefa recebe um nível de energia: leve, média ou pesada. Quando está cansada, a pessoa pode filtrar a lista para ver apenas as tarefas leves.

**Why this priority**: Aumenta a utilidade do app em dias de baixa energia, mas o produto já funciona sem isso.

**Independent Test**: Criar tarefas com níveis diferentes, ativar o filtro de cansaço e verificar que só as leves aparecem; desativar e ver todas de novo.

**Acceptance Scenarios**:

1. **Given** a pessoa cria ou edita uma tarefa, **When** escolhe leve, média ou pesada, **Then** o nível fica visível na tarefa com identificação visual clara.
2. **Given** a pessoa não escolhe um nível, **When** salva a tarefa, **Then** ela recebe o nível "média" por padrão.
3. **Given** o dia tem tarefas de níveis variados, **When** a pessoa ativa "Estou cansado", **Then** só as tarefas leves são exibidas.
4. **Given** o filtro está ativo e não há tarefas leves pendentes, **When** a lista é exibida, **Then** o app informa que não há tarefas leves e oferece desativar o filtro.
5. **Given** o filtro "Estou cansado" está ativo, **When** a pessoa conclui uma tarefa em foco, **Then** a próxima tarefa sugerida respeita o filtro.

---

### Edge Cases

- A pessoa tenta adicionar uma quarta tarefa e fecha as opções sem escolher: nada é criado e o dia continua com 3 tarefas.
- A pessoa tenta criar uma tarefa sem título (ou só com espaços): o app recusa e pede um título.
- Todas as tarefas do dia estão concluídas: o app mostra um estado vazio convidando a planejar mais ou descansar.
- A pessoa fecha ou recarrega a página com o cronômetro rodando: tarefas e estados não se perdem e o tempo já decorrido da sessão de foco é retomado.
- Passou a meia-noite com tarefas pendentes: elas continuam no dia atual, sem serem apagadas.
- A lista "Para depois" cresce muito: ela fica separada da tela principal para não gerar sobrecarga visual.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST permitir criar uma tarefa com título obrigatório e nível de energia (leve, média ou pesada).
- **FR-002**: O sistema MUST manter no máximo 3 tarefas pendentes na lista do dia ao mesmo tempo.
- **FR-003**: Ao tentar adicionar uma tarefa quando o dia já tem 3 pendentes, o sistema MUST impedir a adição ao dia e oferecer as opções "concluir uma das três" ou "guardar para depois".
- **FR-004**: O sistema MUST manter uma lista "Para depois" para tarefas guardadas, separada da lista do dia.
- **FR-005**: A pessoa MUST poder mover tarefas entre o dia e "Para depois" (respeitando o limite de 3 no dia).
- **FR-006**: A pessoa MUST poder marcar uma tarefa como concluída, o que libera uma vaga no dia.
- **FR-007**: A pessoa MUST poder editar o título e o nível de energia de uma tarefa e excluí-la.
- **FR-008**: O sistema MUST definir o nível "média" como padrão quando nenhum nível for escolhido.
- **FR-009**: O sistema MUST exibir o nível de energia de cada tarefa com identificação visual distinta (por exemplo, cor e rótulo) para cada nível.
- **FR-010**: A pessoa MUST poder ativar um filtro "Estou cansado" que exibe apenas tarefas leves, e desativá-lo a qualquer momento.
- **FR-011**: A pessoa MUST poder iniciar um modo foco a partir de qualquer tarefa pendente do dia.
- **FR-012**: No modo foco, o sistema MUST exibir apenas a tarefa atual, um cronômetro e os controles de concluir e sair do foco, sem outros elementos da interface.
- **FR-013**: O cronômetro MUST iniciar ao entrar no foco e mostrar o tempo decorrido.
- **FR-014**: Ao concluir uma tarefa em foco, o sistema MUST apresentar a próxima tarefa pendente do dia (respeitando o filtro "Estou cansado", se ativo) ou uma mensagem de dia concluído se não houver mais.
- **FR-015**: O sistema MUST preservar tarefas, níveis, estados e a lista "Para depois" entre acessos (fechar e reabrir).
- **FR-016**: O sistema MUST exibir mensagens claras e amigáveis quando uma ação for bloqueada ou inválida.
- **FR-017**: O sistema MUST permitir o uso completo sem nenhuma configuração prévia.

### Key Entities *(include if feature involves data)*

- **Tarefa**: Algo a fazer. Atributos: título, nível de energia (leve, média ou pesada), situação (no dia, para depois ou concluída), momento da conclusão e tempo total gasto em foco.
- **Lista do dia**: Conjunto de até 3 tarefas pendentes que a pessoa se comprometeu a fazer hoje.
- **Para depois**: Conjunto de tarefas guardadas, fora do dia, sem limite de quantidade.
- **Sessão de foco**: Período em que uma única tarefa está em foco, com o tempo decorrido medido pelo cronômetro.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% das tentativas de adicionar uma quarta tarefa ao dia, o sistema bloqueia a adição e oferece as duas saídas (concluir ou guardar para depois).
- **SC-002**: Uma pessoa nova consegue criar sua primeira tarefa com nível de energia em menos de 30 segundos, sem instruções.
- **SC-003**: Uma pessoa vai da lista do dia ao modo foco com um único clique.
- **SC-004**: Com o filtro "Estou cansado" ativo, 100% das tarefas exibidas são leves.
- **SC-005**: No modo foco, a tela contém somente a tarefa atual, o cronômetro e os controles de concluir/sair.
- **SC-006**: Ao reabrir o app, 100% das tarefas e seus estados estão como foram deixados.
- **SC-007**: Pelo menos 90% das pessoas em teste de usabilidade descrevem a interface como "limpa" ou "simples" e completam o ciclo planejar, focar e concluir sem ajuda.

## Assumptions

- Uso por uma única pessoa, sem contas, login ou compartilhamento.
- O produto é um site responsivo, utilizável em computador e celular; aplicativo nativo está fora do escopo.
- O limite de 3 conta apenas tarefas pendentes do dia; tarefas concluídas não ocupam vaga.
- Tarefas pendentes não concluídas permanecem no dia seguinte, sem serem apagadas ou movidas automaticamente.
- A lista "Para depois" não tem limite de quantidade.
- O cronômetro apenas mede o tempo decorrido (não é um timer regressivo/Pomodoro); o tempo gasto é guardado na tarefa.
- Fora do escopo desta versão: datas de vencimento, categorias, etiquetas, lembretes, tarefas recorrentes, subtarefas, estatísticas e notificações.
- O idioma da interface é o português do Brasil.
