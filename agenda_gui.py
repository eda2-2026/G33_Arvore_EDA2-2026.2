"""Interface gráfica da agenda StudyFlow, feita com Tkinter."""

from __future__ import annotations

import tkinter as tk
from datetime import date, timedelta
from tkinter import messagebox, ttk

from agenda_avl import AgendaAVL, Tarefa


class AgendaApp:
    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.agenda = AgendaAVL()
        self._carregar_exemplos()

        raiz.title("StudyFlow | Agenda de estudos")
        raiz.geometry("1040x700")
        raiz.minsize(820, 580)
        raiz.configure(bg="#f4f6fa")

        self._configurar_estilos()
        self._montar_interface()
        self._atualizar_tabela()

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self.raiz)
        estilo.theme_use("clam")
        estilo.configure("App.TFrame", background="#f4f6fa")
        estilo.configure("Card.TFrame", background="#ffffff")
        estilo.configure("Title.TLabel", background="#f4f6fa", foreground="#172033", font=("TkDefaultFont", 23, "bold"))
        estilo.configure("Subtitle.TLabel", background="#f4f6fa", foreground="#667085", font=("TkDefaultFont", 10))
        estilo.configure("CardTitle.TLabel", background="#ffffff", foreground="#172033", font=("TkDefaultFont", 12, "bold"))
        estilo.configure("Field.TLabel", background="#ffffff", foreground="#475467", font=("TkDefaultFont", 9, "bold"))
        estilo.configure("Status.TLabel", background="#f4f6fa", foreground="#667085", font=("TkDefaultFont", 9))
        estilo.configure("Primary.TButton", font=("TkDefaultFont", 10, "bold"), padding=(14, 9), background="#4f46e5", foreground="#ffffff")
        estilo.map("Primary.TButton", background=[("active", "#4338ca"), ("disabled", "#a5b4fc")])
        estilo.configure("TButton", font=("TkDefaultFont", 9), padding=(10, 7))
        estilo.configure("Treeview", rowheight=34, background="#ffffff", fieldbackground="#ffffff", foreground="#172033", font=("TkDefaultFont", 10), borderwidth=0)
        estilo.configure("Treeview.Heading", background="#f8fafc", foreground="#475467", font=("TkDefaultFont", 9, "bold"), padding=(8, 10), relief="flat")
        estilo.map("Treeview", background=[("selected", "#e0e7ff")], foreground=[("selected", "#172033")])

    def _carregar_exemplos(self) -> None:
        hoje = date.today()
        exemplos = (
            (1, 1, "Revisar árvores AVL", "EDA2", "alta"),
            (2, 3, "Resolver lista de exercícios", "EDA2", "média"),
            (3, 3, "Ler capítulo sobre derivadas", "Cálculo", "baixa"),
            (4, 6, "Preparar resumo da aula", "Banco de Dados", "média"),
        )
        for identificador, dias, nome, disciplina, dificuldade in exemplos:
            self.agenda.inserir(
                Tarefa(
                    identificador,
                    (hoje + timedelta(days=dias)).isoformat(),
                    nome,
                    disciplina,
                    dificuldade,
                )
            )

    def _montar_interface(self) -> None:
        conteudo = ttk.Frame(self.raiz, style="App.TFrame", padding=(30, 24))
        conteudo.pack(fill="both", expand=True)

        cabecalho = ttk.Frame(conteudo, style="App.TFrame")
        cabecalho.pack(fill="x", pady=(0, 20))
        ttk.Label(cabecalho, text="StudyFlow", style="Title.TLabel").pack(anchor="w")
        ttk.Label(cabecalho, text="Organize suas tarefas por prazo e acompanhe o que vem primeiro.", style="Subtitle.TLabel").pack(anchor="w", pady=(4, 0))

        cartao_form = ttk.Frame(conteudo, style="Card.TFrame", padding=18)
        cartao_form.pack(fill="x", pady=(0, 14))
        ttk.Label(cartao_form, text="Nova tarefa", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 14))

        campos = (
            ("ID", "id", 10),
            ("Prazo (AAAA-MM-DD)", "prazo", 18),
            ("Atividade", "nome", 30),
            ("Disciplina", "disciplina", 22),
            ("Dificuldade", "dificuldade", 16),
        )
        self.campos: dict[str, ttk.Entry] = {}
        for coluna, (rotulo, chave, largura) in enumerate(campos):
            ttk.Label(cartao_form, text=rotulo, style="Field.TLabel").grid(row=1, column=coluna, sticky="w", padx=(0 if coluna == 0 else 10, 0), pady=(0, 6))
            entrada = ttk.Entry(cartao_form, width=largura)
            entrada.grid(row=2, column=coluna, sticky="ew", padx=(0 if coluna == 0 else 10, 0))
            self.campos[chave] = entrada
        cartao_form.columnconfigure(2, weight=1)
        self.campos["id"].bind("<Return>", lambda _evento: self._cadastrar())
        self.campos["dificuldade"].insert(0, "não informada")

        acoes_form = ttk.Frame(cartao_form, style="Card.TFrame")
        acoes_form.grid(row=3, column=0, columnspan=5, sticky="ew", pady=(14, 0))
        ttk.Button(acoes_form, text="Adicionar tarefa", style="Primary.TButton", command=self._cadastrar).pack(side="left")
        ttk.Label(acoes_form, text="O ID deve ser único. Tarefas podem compartilhar o mesmo prazo.", style="Subtitle.TLabel").pack(side="left", padx=12)

        cartao_lista = ttk.Frame(conteudo, style="Card.TFrame", padding=18)
        cartao_lista.pack(fill="both", expand=True)
        topo_lista = ttk.Frame(cartao_lista, style="Card.TFrame")
        topo_lista.pack(fill="x", pady=(0, 12))
        ttk.Label(topo_lista, text="Sua agenda", style="CardTitle.TLabel").pack(side="left")

        acoes = ttk.Frame(topo_lista, style="Card.TFrame")
        acoes.pack(side="right")
        ttk.Button(acoes, text="Próxima tarefa", command=self._selecionar_proxima).pack(side="left", padx=(0, 7))
        ttk.Button(acoes, text="Buscar por ID", command=self._buscar).pack(side="left", padx=(0, 7))
        ttk.Button(acoes, text="Remover selecionada", command=self._remover).pack(side="left")

        busca = ttk.Frame(cartao_lista, style="Card.TFrame")
        busca.pack(fill="x", pady=(0, 12))
        ttk.Label(busca, text="ID para busca:", style="Field.TLabel").pack(side="left", padx=(0, 8))
        self.busca_id = ttk.Entry(busca, width=12)
        self.busca_id.pack(side="left")
        self.busca_id.bind("<Return>", lambda _evento: self._buscar())

        tabela_area = ttk.Frame(cartao_lista, style="Card.TFrame")
        tabela_area.pack(fill="both", expand=True)
        colunas = ("id", "prazo", "nome", "disciplina", "dificuldade", "fator")
        self.tabela = ttk.Treeview(tabela_area, columns=colunas, show="headings", selectmode="browse")
        titulos = {"id": "ID", "prazo": "Prazo", "nome": "Atividade", "disciplina": "Disciplina", "dificuldade": "Dificuldade", "fator": "Fator AVL"}
        larguras = {"id": 58, "prazo": 115, "nome": 260, "disciplina": 170, "dificuldade": 130, "fator": 85}
        for coluna in colunas:
            self.tabela.heading(coluna, text=titulos[coluna])
            self.tabela.column(coluna, width=larguras[coluna], anchor="w", stretch=coluna in {"nome", "disciplina"})
        self.tabela.column("id", anchor="center")
        self.tabela.column("fator", anchor="center")
        barra = ttk.Scrollbar(tabela_area, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=barra.set)
        self.tabela.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.status = tk.StringVar(value="Tarefas de exemplo carregadas — você pode removê-las ou adicionar as suas.")
        ttk.Label(conteudo, textvariable=self.status, style="Status.TLabel").pack(anchor="w", pady=(10, 0))

    def _atualizar_tabela(self, selecionar_id: int | None = None) -> None:
        self.tabela.delete(*self.tabela.get_children())
        fatores = {tarefa.id: fator for tarefa, fator in self.agenda.fatores()}
        tarefas = self.agenda.listar()
        for tarefa in tarefas:
            self.tabela.insert(
                "", "end", iid=str(tarefa.id),
                values=(tarefa.id, tarefa.prazo, tarefa.nome, tarefa.disciplina, tarefa.dificuldade, f"{fatores[tarefa.id]:+d}"),
            )
        if selecionar_id is not None and self.tabela.exists(str(selecionar_id)):
            item = str(selecionar_id)
            self.tabela.selection_set(item)
            self.tabela.focus(item)
            self.tabela.see(item)
        quantidade = len(tarefas)
        self.status.set(f"{quantidade} tarefa{'s' if quantidade != 1 else ''} na agenda · os exemplos podem ser removidos")

    def _cadastrar(self) -> None:
        try:
            tarefa = Tarefa(
                id=int(self.campos["id"].get().strip()),
                prazo=self.campos["prazo"].get().strip(),
                nome=self.campos["nome"].get().strip(),
                disciplina=self.campos["disciplina"].get().strip(),
                dificuldade=self.campos["dificuldade"].get().strip() or "não informada",
            )
            self.agenda.inserir(tarefa)
        except ValueError as erro:
            messagebox.showerror("Não foi possível cadastrar", str(erro), parent=self.raiz)
            return
        self._atualizar_tabela(tarefa.id)
        self.status.set(f"Tarefa #{tarefa.id} cadastrada.")
        for chave in ("id", "prazo", "nome", "disciplina"):
            self.campos[chave].delete(0, "end")
        self.campos["dificuldade"].delete(0, "end")
        self.campos["dificuldade"].insert(0, "não informada")
        self.campos["id"].focus_set()

    def _buscar(self) -> None:
        try:
            identificador = int(self.busca_id.get().strip())
        except ValueError:
            messagebox.showerror("Busca por ID", "Informe um ID numérico.", parent=self.raiz)
            return
        tarefa = self.agenda.buscar(identificador)
        if tarefa is None:
            self.status.set(f"Nenhuma tarefa encontrada com o ID {identificador}.")
            messagebox.showinfo("Busca por ID", "Tarefa não encontrada.", parent=self.raiz)
            return
        self._atualizar_tabela(tarefa.id)
        self.status.set(f"Tarefa #{tarefa.id} encontrada e selecionada.")

    def _selecionar_proxima(self) -> None:
        tarefa = self.agenda.proxima_tarefa()
        if tarefa is None:
            self.status.set("A agenda está vazia.")
            return
        self._atualizar_tabela(tarefa.id)
        self.status.set(f"Próxima tarefa: {tarefa.nome} · {tarefa.prazo}")

    def _remover(self) -> None:
        selecionados = self.tabela.selection()
        if not selecionados:
            messagebox.showinfo("Remover tarefa", "Selecione uma tarefa na tabela primeiro.", parent=self.raiz)
            return
        identificador = int(selecionados[0])
        removida = self.agenda.remover(identificador)
        self._atualizar_tabela()
        self.status.set(f"Tarefa #{identificador} removida." if removida else "A tarefa selecionada não existe mais.")


def executar_interface() -> None:
    raiz = tk.Tk()
    AgendaApp(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    executar_interface()
