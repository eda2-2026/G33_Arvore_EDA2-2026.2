"""Agenda de estudos organizada por uma árvore AVL.

Execute com ``python3 agenda_avl.py`` para abrir o menu interativo ou com
``python3 agenda_avl.py --demo`` para ver uma demonstração dos casos de rotação.
"""

from __future__ import annotations

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

        def _remover_chave(no: NoAVL | None, chave: tuple[str, int]) -> NoAVL | None:
            nonlocal removida
            if no is None:
                return None
            if chave < no.tarefa.chave:
                no.esquerda = _remover_chave(no.esquerda, chave)
            elif chave > no.tarefa.chave:
                no.direita = _remover_chave(no.direita, chave)
            else:
                removida = no.tarefa
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
