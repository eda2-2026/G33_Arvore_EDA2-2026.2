"""Recomendador de estudos usando uma Árvore Binária de Decisão.

Execute com ``python3 recomendador.py`` para iniciar a interação no terminal.
"""

from __future__ import annotations
from dataclasses import dataclass
import sys

@dataclass
class NoDecisao:
    """Nó da árvore: pode ser uma pergunta (nó interno) ou uma recomendação (folha)."""
    texto: str
    sim: NoDecisao | None = None
    nao: NoDecisao | None = None

    @property
    def eh_folha(self) -> bool:
        """Se não tem filhos, é uma folha (recomendação final)."""
        return self.sim is None and self.nao is None


def construir_arvore() -> NoDecisao:
    """Constrói a árvore de decisão fixa baseada em prazo, dificuldade e tempo."""
    
    # Folhas (Recomendações finais)
    rec_exercicios = NoDecisao("Sugestão: Foque em resolver exercícios e revisar seus resumos agora mesmo.")
    rec_revisao = NoDecisao("Sugestão: Faça uma revisão rápida e leia o material complementar.")
    rec_pomodoro = NoDecisao("Sugestão: Inicie uma sessão de estudo profundo de 30 min (técnica Pomodoro).")
    rec_etapas = NoDecisao("Sugestão: Divida a tarefa em etapas menores e faça apenas a primeira agora.")

    # Nós internos (Perguntas)
    # Nível 1
    perg_dificuldade = NoDecisao("O conteúdo dessa avaliação está difícil?", sim=rec_exercicios, nao=rec_revisao)
    perg_tempo = NoDecisao("Você tem pelo menos 30 minutos disponíveis agora?", sim=rec_pomodoro, nao=rec_etapas)

    # Raiz
    raiz = NoDecisao("Você tem alguma avaliação ou prazo nos próximos dois dias?", sim=perg_dificuldade, nao=perg_tempo)
    
    return raiz


def percorrer_arvore(raiz: NoDecisao) -> None:
    """Navega na árvore de decisão validando a entrada do usuário."""
    atual = raiz
    
    print("\n--- Recomendador de Estudos ---")
    print("Responda com 'sim' ou 'não' para receber uma sugestão do que fazer a seguir.\n")
    
    # O custo da recomendação é O(h), sendo h a altura da árvore.
    while not atual.eh_folha:
        resposta = input(f"{atual.texto} (sim/não): ").strip().lower()
        
        if resposta in ("sim", "s"):
            atual = atual.sim
        elif resposta in ("não", "nao", "n"):
            atual = atual.nao
        else:
            print("-> Resposta inválida. Por favor, digite apenas 'sim' ou 'não'.\n")
            
    print(f"\n{atual.texto}")
    print("-" * 31)


def demonstracao() -> None:
    """Executa a demonstração independente do recomendador."""
    print("StudyFlow — Demonstração do Recomendador (Árvore de Decisão)")
    print("A busca percorre a altura da árvore, custando O(h). Como a árvore é pequena, é instantâneo.")
    
    arvore = construir_arvore()
    
    while True:
        percorrer_arvore(arvore)
        
        continuar = input("\nDeseja simular outro cenário de respostas? (sim/não): ").strip().lower()
        if continuar not in ("sim", "s"):
            print("Encerrando o recomendador. Bons estudos!")
            break


def executar_recomendador() -> None:
    """Função de entrada que será chamada pelo menu principal (main.py)."""
    arvore = construir_arvore()
    percorrer_arvore(arvore)


if __name__ == "__main__":
    # Permite rodar o módulo sozinho para testes e gravação do vídeo
    demonstracao()