# StudyFlow — agenda de estudos

Projeto de Estruturas de Dados e Algoritmos II. A parte da pessoa 1 organiza
tarefas por prazo em uma árvore AVL e roda de forma independente no terminal.

## Requisitos

- Python 3.10 ou mais recente
- Nenhuma biblioteca externa

## Executar

Abra o terminal na pasta do projeto e execute:

```bash
python3 agenda_avl.py
```

O menu permite cadastrar, listar, consultar a próxima tarefa, buscar e remover
por ID e consultar os fatores de balanceamento. O prazo deve estar no formato
`AAAA-MM-DD`; duas tarefas podem ter o mesmo prazo, pois o ID desempata a chave.

Para ver dados de exemplo, a busca, remoção e exemplos de rotações:

```bash
python3 agenda_avl.py --demo
```

O módulo também pode ser chamado por uma futura integração com o menu geral:

```python
from agenda_avl import executar_agenda

executar_agenda()
```

## Estrutura e custos

Cada nó guarda uma tarefa, filhos esquerdo e direito e a altura da subárvore.
O fator é `altura(esquerda) - altura(direita)` e deve ficar entre `-1` e `1`.
Inserção e remoção reequilibram os nós com rotações simples ou duplas. A AVL
ordena pela chave `(prazo, ID)`.

- Inserção: `O(log n)`.
- Busca por chave (prazo e ID): `O(log n)`; busca por ID: `O(1)` usando índice auxiliar.
- Remoção por ID: `O(log n)` após localizar a tarefa pelo índice auxiliar.
- Próxima tarefa: `O(log n)` ao percorrer até o menor nó.
- Listagem completa: `O(n)`.

Na demonstração, inserir prazos crescentes provoca uma rotação simples à
esquerda; inserir na ordem primeiro, terceiro, segundo provoca uma rotação
dupla esquerda-direita. Os fatores resultantes são exibidos para facilitar a
explicação da estrutura.
