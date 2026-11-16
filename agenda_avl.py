"""Agenda de estudos organizada por uma árvore AVL.

Execute com ``python3 agenda_avl.py`` para abrir o menu interativo ou com
``python3 agenda_avl.py --demo`` para ver uma demonstração dos casos de rotação.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from typing import Iterator


@dataclass(frozen=True)
class Tarefa:
    """Atividade de estudo armazenada na agenda."""

    id: int
    prazo: str
    nome: str
    disciplina: str
    dificuldade: str = "não informada"

    def __post_init__(self) -> None:
        try:
            date.fromisoformat(self.prazo)
        except ValueError as erro:
            raise ValueError("O prazo deve usar o formato AAAA-MM-DD.") from erro
        if self.id < 1:
            raise ValueError("O identificador deve ser um número positivo.")
        if not self.nome.strip() or not self.disciplina.strip():
            raise ValueError("Nome e disciplina não podem ficar vazios.")

    @property
    def chave(self) -> tuple[str, int]:
        """Prazo primeiro; o identificador desempata tarefas do mesmo dia."""

        return self.prazo, self.id


@dataclass
class NoAVL:
    tarefa: Tarefa
    esquerda: NoAVL | None = None
    direita: NoAVL | None = None
    altura: int = 1


def altura(no: NoAVL | None) -> int:
    return no.altura if no else 0


def fator_balanceamento(no: NoAVL | None) -> int:
    if no is None:
        return 0
    return altura(no.esquerda) - altura(no.direita)


def _atualizar_altura(no: NoAVL) -> None:
    no.altura = 1 + max(altura(no.esquerda), altura(no.direita))


def _rotacao_direita(raiz: NoAVL) -> NoAVL:
    nova_raiz = raiz.esquerda
    if nova_raiz is None:
        return raiz
    galho = nova_raiz.direita
    nova_raiz.direita = raiz
    raiz.esquerda = galho
    _atualizar_altura(raiz)
    _atualizar_altura(nova_raiz)
    return nova_raiz


def _rotacao_esquerda(raiz: NoAVL) -> NoAVL:
    nova_raiz = raiz.direita
    if nova_raiz is None:
        return raiz
    galho = nova_raiz.esquerda
    nova_raiz.esquerda = raiz
    raiz.direita = galho
    _atualizar_altura(raiz)
    _atualizar_altura(nova_raiz)
    return nova_raiz


def _rebalancear(no: NoAVL) -> NoAVL:
    _atualizar_altura(no)
    fator = fator_balanceamento(no)

    if fator > 1:
        if fator_balanceamento(no.esquerda) < 0:
            no.esquerda = _rotacao_esquerda(no.esquerda)  # caso esquerda-direita
        return _rotacao_direita(no)
    if fator < -1:
        if fator_balanceamento(no.direita) > 0:
            no.direita = _rotacao_direita(no.direita)  # caso direita-esquerda
        return _rotacao_esquerda(no)
    return no


class AgendaAVL:
    """Agenda em memória; operações de busca e atualização custam O(log n)."""

    def __init__(self) -> None:
        self.raiz: NoAVL | None = None
        self._por_id: dict[int, Tarefa] = {}

    def inserir(self, tarefa: Tarefa) -> None:
        """Insere tarefa pela chave (prazo, identificador)."""

        def _inserir(no: NoAVL | None) -> NoAVL:
            if no is None:
                return NoAVL(tarefa)
            if tarefa.chave < no.tarefa.chave:
                no.esquerda = _inserir(no.esquerda)
            elif tarefa.chave > no.tarefa.chave:
                no.direita = _inserir(no.direita)
            else:
                raise ValueError(f"Já existe uma tarefa com ID {tarefa.id}.")
            return _rebalancear(no)

        if tarefa.id in self._por_id:
            raise ValueError(f"Já existe uma tarefa com ID {tarefa.id}.")
        self.raiz = _inserir(self.raiz)
        self._por_id[tarefa.id] = tarefa

    def buscar(self, identificador: int) -> Tarefa | None:
        """Busca pelo identificador único em índice auxiliar O(1)."""

        return self._por_id.get(identificador)

    def buscar_por_chave(self, prazo: str, identificador: int) -> Tarefa | None:
        """Busca na AVL pela chave completa (prazo, identificador), em O(log n)."""

        chave = (prazo, identificador)
        atual = self.raiz
        while atual is not None:
            if chave == atual.tarefa.chave:
                return atual.tarefa
            atual = atual.esquerda if chave < atual.tarefa.chave else atual.direita
        return None

    def remover(self, identificador: int) -> Tarefa | None:
        """Remove pelo ID e rebalanceia os ancestrais do nó removido."""
        removida: Tarefa | None = None

        def menor(no: NoAVL) -> NoAVL:
            while no.esquerda is not None:
                no = no.esquerda
            return no

        # O índice auxiliar encontra o prazo; a remoção na AVL custa O(log n).
        tarefa = self.buscar(identificador)
        if tarefa is None:
            return None
        removida = tarefa

        def _remover_chave(no: NoAVL | None, chave: tuple[str, int]) -> NoAVL | None:
            if no is None:
                return None
            if chave < no.tarefa.chave:
                no.esquerda = _remover_chave(no.esquerda, chave)
            elif chave > no.tarefa.chave:
                no.direita = _remover_chave(no.direita, chave)
            else:
                if no.esquerda is None:
                    return no.direita
                if no.direita is None:
                    return no.esquerda
                sucessor = menor(no.direita)
                no.tarefa = sucessor.tarefa
                no.direita = _remover_chave(no.direita, sucessor.tarefa.chave)
            return _rebalancear(no)

        self.raiz = _remover_chave(self.raiz, tarefa.chave)
        self._por_id.pop(identificador, None)
        return removida

    def listar(self) -> list[Tarefa]:
        """Retorna todas as tarefas em ordem crescente de prazo (O(n))."""

        resultado: list[Tarefa] = []

        def _em_ordem(no: NoAVL | None) -> None:
            if no is None:
                return
            _em_ordem(no.esquerda)
            resultado.append(no.tarefa)
            _em_ordem(no.direita)

        _em_ordem(self.raiz)
        return resultado

    def proxima_tarefa(self) -> Tarefa | None:
        """Retorna a tarefa com prazo mais próximo (menor chave)."""

        atual = self.raiz
        if atual is None:
            return None
        while atual.esquerda is not None:
            atual = atual.esquerda
        return atual.tarefa

    def fatores(self) -> Iterator[tuple[Tarefa, int]]:
        """Percorre a árvore e expõe os fatores para fins didáticos."""

        def _percorrer(no: NoAVL | None) -> Iterator[tuple[Tarefa, int]]:
            if no is None:
                return
            yield from _percorrer(no.esquerda)
            yield no.tarefa, fator_balanceamento(no)
            yield from _percorrer(no.direita)

        return _percorrer(self.raiz)


def _formatar(tarefa: Tarefa) -> str:
    return (
        f"#{tarefa.id} | {tarefa.prazo} | {tarefa.nome} | "
        f"{tarefa.disciplina} | dificuldade: {tarefa.dificuldade}"
    )


def _ler_tarefa(agenda: AgendaAVL) -> Tarefa:
    identificador = int(input("ID único: ").strip())
    prazo = input("Prazo (AAAA-MM-DD): ").strip()
    nome = input("Atividade: ").strip()
    disciplina = input("Disciplina: ").strip()
    dificuldade = input("Dificuldade (opcional): ").strip() or "não informada"
    tarefa = Tarefa(identificador, prazo, nome, disciplina, dificuldade)
    agenda.inserir(tarefa)
    return tarefa


def _demonstrar_rotacoes() -> None:
    print("Demonstração de rotações AVL (fator = altura esquerda - altura direita):")
    simples = AgendaAVL()
    for identificador, prazo in enumerate(("2026-11-10", "2026-11-11", "2026-11-12"), 1):
        simples.inserir(Tarefa(identificador, prazo, f"Tarefa {identificador}", "EDA2"))
    print("\nInserção crescente (caso direita-direita, rotação simples à esquerda):")
    for tarefa, fator in simples.fatores():
        print(f"  {_formatar(tarefa)} | fator {fator:+d}")

    dupla = AgendaAVL()
    for identificador, prazo in enumerate(("2026-11-12", "2026-11-10", "2026-11-11"), 1):
        dupla.inserir(Tarefa(identificador, prazo, f"Tarefa {identificador}", "EDA2"))
    print("\nInserção esquerda-direita (rotação dupla):")
    for tarefa, fator in dupla.fatores():
        print(f"  {_formatar(tarefa)} | fator {fator:+d}")


def _agenda_de_exemplo() -> AgendaAVL:
    agenda = AgendaAVL()
    exemplos = (
        Tarefa(1, "2026-11-20", "Lista de exercícios", "EDA2", "média"),
        Tarefa(2, "2026-11-18", "Revisar árvores AVL", "EDA2", "alta"),
        Tarefa(3, "2026-11-20", "Ler capítulo 4", "Cálculo", "baixa"),
        Tarefa(4, "2026-11-25", "Preparar resumo", "Banco de Dados", "média"),
    )
    for tarefa in exemplos:
        agenda.inserir(tarefa)
    return agenda


def demonstracao() -> None:
    agenda = _agenda_de_exemplo()
    print("StudyFlow — demonstração da agenda AVL")
    print("\nTarefas em ordem de prazo:")
    for tarefa in agenda.listar():
        print(f"  {_formatar(tarefa)}")
    print("\nPróxima tarefa:")
    proxima = agenda.proxima_tarefa()
    print(f"  {_formatar(proxima)}" if proxima else "  Agenda vazia.")
    encontrada = agenda.buscar(3)
    print("\nBusca pelo ID 3:")
    print(f"  {_formatar(encontrada)}" if encontrada else "  Tarefa não encontrada.")
    removida = agenda.remover(2)
    print("\nRemoção do ID 2:")
    print(f"  {_formatar(removida)}" if removida else "  Tarefa não encontrada.")
    _demonstrar_rotacoes()


def executar_agenda() -> None:
    """Abre o menu independente da agenda; também pode ser chamado pelo main."""

    agenda = AgendaAVL()
    while True:
        print("\nStudyFlow — Agenda de estudos (AVL)")
        print("1. Cadastrar tarefa")
        print("2. Listar por prazo")
        print("3. Consultar próxima tarefa")
        print("4. Buscar por ID")
        print("5. Remover por ID")
        print("6. Mostrar fatores de balanceamento")
        print("0. Sair")
        opcao = input("Escolha: ").strip()

        try:
            if opcao == "1":
                tarefa = _ler_tarefa(agenda)
                print(f"Tarefa cadastrada: {_formatar(tarefa)}")
            elif opcao == "2":
                tarefas = agenda.listar()
                if not tarefas:
                    print("A agenda está vazia.")
                for tarefa in tarefas:
                    print(f"  {_formatar(tarefa)}")
            elif opcao == "3":
                tarefa = agenda.proxima_tarefa()
                print(_formatar(tarefa) if tarefa else "A agenda está vazia.")
            elif opcao == "4":
                identificador = int(input("ID para buscar: ").strip())
                tarefa = agenda.buscar(identificador)
                print(_formatar(tarefa) if tarefa else "Tarefa não encontrada.")
            elif opcao == "5":
                identificador = int(input("ID para remover: ").strip())
                tarefa = agenda.remover(identificador)
                print(f"Removida: {_formatar(tarefa)}" if tarefa else "Tarefa não encontrada.")
            elif opcao == "6":
                fatores = list(agenda.fatores())
                if not fatores:
                    print("A agenda está vazia.")
                for tarefa, fator in fatores:
                    print(f"  ID {tarefa.id}: fator {fator:+d}")
            elif opcao == "0":
                print("Até a próxima sessão de estudos!")
                return
            else:
                print("Opção inválida. Escolha uma opção do menu.")
        except (ValueError, EOFError) as erro:
            print(f"Entrada inválida: {erro}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demonstracao()
    else:
        executar_agenda()
