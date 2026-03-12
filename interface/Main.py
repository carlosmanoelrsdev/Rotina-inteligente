import customtkinter as ctk
import sys
from pathlib import Path
from tkinter import messagebox
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parents[1]))
from login.regras_login import validar_login
from calendario_climatico.calendario_dia import obter_data_atual
from clima.climarequisicoes import buscar_clima
from chat_ai.definicoeschat import ChatAtividadesService
from database.regrasDados import (
    atualizar_tarefa,
    buscar_tarefa_por_id,
    excluir_tarefa,
    inicializar_banco,
    inserir_tarefa,
    listar_tarefas,
)

ctk.set_appearance_mode("dark")


class Interface(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Rotina Inteligente")
        self.geometry("1100x700")
        self.resizable(False, False)

        self.cidade_logada = None  # Armazena a cidade do login

        self.frame_telaLogin = FrameTelaLogin(self)
        self.frame_telaprincipal = FrameTelaPrincipal(self)
        self.frame_telaprincipal.pack_forget()


class FrameTelaLogin(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.label_title = ctk.CTkLabel(
            self,
            text="Bem-vindo ao Rotina Inteligente",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.label_title.pack(pady=40)

        self.campo_usuario = ctk.CTkEntry(self, placeholder_text="Usuário")
        self.campo_usuario.pack(pady=10)

        self.campo_senha = ctk.CTkEntry(self, placeholder_text="Senha", show="*")
        self.campo_senha.pack(pady=10)

        self.campo_cidade = ctk.CTkEntry(self, placeholder_text="Cidade")
        self.campo_cidade.pack(pady=10)

        self.botao_login = ctk.CTkButton(self, text="Login", command=self.login)
        self.botao_login.pack(pady=20)

    def login(self):
        usuario = self.campo_usuario.get()
        senha = self.campo_senha.get()
        cidade = self.campo_cidade.get().strip()

        valido, mensagem = validar_login(usuario, senha)
        if valido:
            # Armazena a cidade para o dashboard
            self.master.cidade_logada = cidade

            messagebox.showinfo("Resultado do Login", mensagem)
            self.pack_forget()
            self.master.frame_telaprincipal.pack(fill="both", expand=True)
            self.master.frame_telaprincipal.show_page("dashboard")

        else:
            messagebox.showerror("Resultado do Login", mensagem)


# -------------------- PÁGINAS SEPARADAS --------------------


class DashboardPagina(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        inicializar_banco()
        self.tarefas = []

        self.label_titulo_dash = ctk.CTkLabel(
            self, text="DASHBOARD 📆", font=("Arial", 20, "bold"), justify="left"
        )
        self.label_titulo_dash.pack(pady=10, anchor="w", padx=10)

        self.label_tarefas = ctk.CTkLabel(
            self, text="TAREFAS DO DIA", font=("Arial", 16), justify="left"
        )
        self.label_tarefas.pack(pady=1, anchor="w", padx=10)

        self.frame_clima = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_clima.pack(pady=1, anchor="w", padx=10)

        self.label_clima = ctk.CTkLabel(
            self.frame_clima,
            text="CLIMA: Informe a cidade no login",
            font=("Arial", 14),
            justify="left",
        )
        self.label_clima.pack(side="left", padx=(0, 8))

        self.botao_refresh_clima = ctk.CTkButton(
            self.frame_clima,
            text="↻",
            width=32,
            height=26,
            command=self.atualizar_clima_dashboard,
        )
        self.botao_refresh_clima.pack(side="left")

        self.label_feedback_clima = ctk.CTkLabel(
            self.frame_clima,
            text="",
            font=("Arial", 11),
            text_color="gray",
        )
        self.label_feedback_clima.pack(side="left", padx=(8, 0))

        # Atualiza o clima logo que o dashboard for carregado
        self.after(100, self.atualizar_clima_dashboard)

        self.barrapesquisa = ctk.CTkEntry(
            self, placeholder_text="Pesquisar... ", width=400
        )
        self.barrapesquisa.pack(pady=5, anchor="w", padx=10)
        self.barrapesquisa.bind("<KeyRelease>", self.filtrar)

        # Container com grid para lado a lado
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=0)
        container.grid_rowconfigure(0, weight=1)

        # Frame com scroll para cards (esquerda)
        self.frame_scroll = ctk.CTkScrollableFrame(container, fg_color="#181818")
        self.frame_scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.frame_scroll.grid_columnconfigure(0, weight=1)

        # Frame de detalhes (direita) - tamanho fixo sempre igual
        self.frame_detalhes = ctk.CTkFrame(
            container, fg_color="#181818", width=320, height=600, corner_radius=12
        )
        self.frame_detalhes.grid(row=0, column=1, sticky="nsew")
        self.frame_detalhes.grid_propagate(False)
        self.frame_detalhes.pack_propagate(False)

        # Mensagem inicial
        self.mostrar_mensagem_inicial()

        # Cria cards dinamicamente (1 coluna)
        self.recarregar_tarefas()

    def mostrar_mensagem_inicial(self):
        """Mostra mensagem inicial no painel de detalhes"""
        for widget in self.frame_detalhes.winfo_children():
            widget.destroy()

        label_placeholder = ctk.CTkLabel(
            self.frame_detalhes,
            text="Esperando tarefa",
            font=("Arial", 14),
            text_color="gray",
        )
        label_placeholder.pack(expand=True)

    def obter_cor_status(self, status):
        """Retorna a cor baseado no status - preparado para banco de dados"""
        status_lower = status.lower()
        if status_lower == "concluida":
            return "#77CB42"  # Verde
        elif status_lower == "em andamento":
            return "#CD8500"  # Laranja
        elif status_lower == "pendente":
            return "#C40404"  # Vermelho

    def filtrar(self, event):
        termo = self.barrapesquisa.get().lower()
        filtradas = [
            t
            for t in self.tarefas
            if termo in t["atividade"].lower()
            or termo in (t.get("descricao") or "").lower()
            or termo in t["status"].lower()
        ]
        self.atualizar_lista(filtradas)

    def atualizar_lista(self, lista):
        for widget in self.frame_scroll.winfo_children():
            widget.destroy()

        for i, item in enumerate(lista):
            self.criar_card(
                i, 0, item["atividade"], item["hora"], item["status"], item["id"]
            )

    def atualizar_clima_dashboard(self):
        """Busca e exibe o clima no dashboard"""
        self.label_feedback_clima.configure(text="Atualizando...", text_color="gray")
        try:
            interface = self.winfo_toplevel()
            cidade = interface.cidade_logada

            if not cidade:
                self.label_clima.configure(text="CLIMA: Informe a cidade no login")
                self.label_feedback_clima.configure(
                    text="Sem cidade", text_color="#CD8500"
                )
                self.after(
                    2000,
                    lambda: self.label_feedback_clima.configure(
                        text="", text_color="gray"
                    ),
                )
                return

            clima_resultado = buscar_clima(cidade)
            temperatura = clima_resultado.get("temperatura", "N/A")
            descricao = clima_resultado.get("descricao", "Sem dados")

            if temperatura != "N/A":
                texto_clima = f"CLIMA: {descricao}, {temperatura}°C"
                self.label_feedback_clima.configure(
                    text="Atualizado", text_color="#77CB42"
                )
            else:
                texto_clima = f"CLIMA: {descricao}"
                self.label_feedback_clima.configure(text="Falha", text_color="#C40404")

            self.label_clima.configure(text=texto_clima)
            self.after(
                2000,
                lambda: self.label_feedback_clima.configure(text="", text_color="gray"),
            )
        except Exception as e:
            print(f"[DEBUG] Erro ao atualizar clima no dashboard: {e}")
            self.label_clima.configure(text="CLIMA: Erro ao buscar")
            self.label_feedback_clima.configure(text="Falha", text_color="#C40404")
            self.after(
                2000,
                lambda: self.label_feedback_clima.configure(text="", text_color="gray"),
            )

    def recarregar_tarefas(self):
        self.tarefas = listar_tarefas()
        self.atualizar_lista(self.tarefas)
        self.mostrar_mensagem_inicial()

    def carregar_cards(self):
        self.atualizar_lista(self.tarefas)

    def criar_card(self, linha, coluna, atividade, hora, status, tarefa_id):
        card = ctk.CTkFrame(self.frame_scroll, corner_radius=12, height=100, width=350)
        card.grid(row=linha, column=coluna, sticky="w", padx=8, pady=5)
        card.grid_propagate(False)

        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)
        card.grid_columnconfigure(2, weight=0)
        card.grid_rowconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        label_atividade = ctk.CTkLabel(
            card,
            text=atividade,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        label_atividade.grid(row=0, column=0, sticky="w", padx=12, pady=(5, 0))

        botao_expandir = ctk.CTkButton(
            card,
            text="Detalhes",
            width=70,
            corner_radius=15,
            command=lambda: self.mostrar_detalhes(tarefa_id),
        )
        botao_expandir.grid(row=0, column=1, sticky="ne", padx=12, pady=5)

        label_hora = ctk.CTkLabel(card, text=hora, font=ctk.CTkFont(size=11))
        label_hora.grid(row=1, column=0, sticky="sw", padx=12, pady=(0, 5))

        cor = self.obter_cor_status(status)
        label_status = ctk.CTkLabel(
            card,
            text=status,
            font=ctk.CTkFont(size=12),
            fg_color=cor,
            corner_radius=15,
            padx=8,
            pady=4,
        )
        label_status.grid(row=1, column=1, sticky="se", padx=12, pady=5)

    def mostrar_detalhes(self, tarefa_id):
        """Mostra os detalhes da tarefa no painel direito"""
        tarefa = buscar_tarefa_por_id(tarefa_id)
        if not tarefa:
            self.mostrar_mensagem_inicial()
            return

        # Limpa o frame de detalhes
        for widget in self.frame_detalhes.winfo_children():
            widget.destroy()

        # Título
        titulo = ctk.CTkLabel(
            self.frame_detalhes, text="DETALHES DA TAREFA", font=("Arial", 16, "bold")
        )
        titulo.pack(pady=(10, 20), padx=10, anchor="w")

        # Atividade
        label_ativ_nome = ctk.CTkLabel(
            self.frame_detalhes, text="Atividade:", font=("Arial", 12, "bold")
        )
        label_ativ_nome.pack(padx=10, anchor="w")
        label_ativ_valor = ctk.CTkLabel(
            self.frame_detalhes, text=tarefa["atividade"], font=("Arial", 11)
        )
        label_ativ_valor.pack(padx=10, pady=(0, 10), anchor="w")

        # Descrição
        label_desc_nome = ctk.CTkLabel(
            self.frame_detalhes, text="Descrição:", font=("Arial", 12, "bold")
        )
        label_desc_nome.pack(padx=10, anchor="w")
        label_desc_valor = ctk.CTkLabel(
            self.frame_detalhes,
            text=tarefa["descricao"],
            font=("Arial", 11),
            wraplength=270,
        )
        label_desc_valor.pack(padx=10, pady=(0, 10), anchor="w")

        # Data de Criação
        label_data_nome = ctk.CTkLabel(
            self.frame_detalhes, text="Data de Criação:", font=("Arial", 12, "bold")
        )
        label_data_nome.pack(padx=10, anchor="w")
        label_data_valor = ctk.CTkLabel(
            self.frame_detalhes, text=tarefa["data_criacao"], font=("Arial", 11)
        )
        label_data_valor.pack(padx=10, pady=(0, 20), anchor="w")

        # Menu Notificação
        label_notif_nome = ctk.CTkLabel(
            self.frame_detalhes, text="Notificação:", font=("Arial", 12, "bold")
        )
        label_notif_nome.pack(padx=10, anchor="w")

        self.opcao_notificacao = ctk.CTkOptionMenu(
            self.frame_detalhes,
            values=["15 minutos antes", "30 minutos antes", "1 hora antes"],
            width=260,
        )
        self.opcao_notificacao.pack(padx=10, pady=(0, 10))

        botao_enviar_notif = ctk.CTkButton(
            self.frame_detalhes,
            text="🔔 Enviar Notificação",
            width=260,
            command=lambda: self.enviar_notificacao(tarefa["atividade"]),
        )
        botao_enviar_notif.pack(padx=10, pady=(0, 20))

        # Botão Editar Tarefa
        botao_editar = ctk.CTkButton(
            self.frame_detalhes,
            text="✏️ Editar Tarefa",
            width=260,
            fg_color="#CD8500",
            hover_color="#A66A00",
            command=lambda: self.editar_tarefa(tarefa_id),
        )
        botao_editar.pack(padx=10, pady=5)

        botao_excluir = ctk.CTkButton(
            self.frame_detalhes,
            text="🗑 Excluir Tarefa",
            width=260,
            fg_color="#C40404",
            hover_color="#8F0303",
            command=lambda: self.excluir_tarefa_ui(tarefa_id),
        )
        botao_excluir.pack(padx=10, pady=5)

    def enviar_notificacao(self, atividade):
        """Apenas imprime no terminal por enquanto"""
        tempo = self.opcao_notificacao.get()
        print(f"[NOTIFICAÇÃO] Tarefa '{atividade}' - Lembrete: {tempo}")

    def hora_valida(self, hora):
        if len(hora) != 5 or hora[2] != ":":
            return False

        hh, mm = hora.split(":")
        if not (hh.isdigit() and mm.isdigit()):
            return False

        h = int(hh)
        m = int(mm)
        return 0 <= h <= 23 and 0 <= m <= 59

    def filtrar_hora_numerica(self, entry_hora):
        """Permite somente numeros na digitacao e formata para HH:MM."""
        valor_atual = entry_hora.get()
        numeros = "".join(ch for ch in valor_atual if ch.isdigit())[:4]

        if len(numeros) >= 3:
            formatado = f"{numeros[:2]}:{numeros[2:]}"
        else:
            formatado = numeros

        if valor_atual != formatado:
            entry_hora.delete(0, "end")
            entry_hora.insert(0, formatado)

    def editar_tarefa(self, tarefa_id):
        """Abre uma janela para editar os dados da tarefa."""
        tarefa = buscar_tarefa_por_id(tarefa_id)
        if not tarefa:
            messagebox.showerror("Erro", "Tarefa nao encontrada.")
            return

        janela = ctk.CTkToplevel(self)
        janela.title("Editar Tarefa")
        janela.geometry("500x450")
        janela.resizable(False, False)
        janela.transient(self)
        janela.grab_set()

        ctk.CTkLabel(
            janela,
            text="EDITAR TAREFA",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(20, 15))

        entry_atividade = ctk.CTkEntry(janela, width=420)
        entry_atividade.pack(pady=8)
        entry_atividade.insert(0, tarefa["atividade"])

        entry_hora = ctk.CTkEntry(janela, width=420)
        entry_hora.pack(pady=8)
        entry_hora.insert(0, tarefa["hora"])
        entry_hora.bind(
            "<KeyRelease>", lambda event: self.filtrar_hora_numerica(entry_hora)
        )

        option_status = ctk.CTkOptionMenu(
            janela,
            values=["Pendente", "Em andamento", "Concluida"],
            width=420,
        )
        option_status.pack(pady=8)
        option_status.set(tarefa["status"])

        ctk.CTkLabel(janela, text="Descrição:", font=ctk.CTkFont(size=13)).pack(
            pady=(12, 5)
        )
        text_descricao = ctk.CTkTextbox(janela, width=420, height=120)
        text_descricao.pack(pady=8)
        text_descricao.insert("1.0", tarefa.get("descricao") or "")

        def salvar_edicao():
            atividade = entry_atividade.get().strip()
            self.filtrar_hora_numerica(entry_hora)
            hora = entry_hora.get().strip()
            status = option_status.get().strip()
            descricao = text_descricao.get("1.0", "end").strip()

            if not atividade or not hora:
                messagebox.showwarning(
                    "Campos obrigatorios", "Preencha atividade e hora."
                )
                return

            if not self.hora_valida(hora):
                messagebox.showwarning(
                    "Hora invalida", "Use o formato HH:MM (ex.: 08:30)."
                )
                return

            sucesso = atualizar_tarefa(
                tarefa_id,
                atividade,
                hora,
                status,
                descricao,
                tarefa["data_criacao"],
            )

            if not sucesso:
                messagebox.showerror("Erro", "Nao foi possivel atualizar a tarefa.")
                return

            print(f"[EDITAR] Tarefa '{atividade}' atualizada com sucesso.")
            janela.destroy()
            self.recarregar_tarefas()
            self.mostrar_detalhes(tarefa_id)

        ctk.CTkButton(
            janela,
            text="Salvar Alterações",
            width=420,
            command=salvar_edicao,
        ).pack(pady=(10, 20))

    def excluir_tarefa_ui(self, tarefa_id):
        tarefa = buscar_tarefa_por_id(tarefa_id)
        if not tarefa:
            messagebox.showerror("Erro", "Tarefa nao encontrada.")
            return

        confirmar = messagebox.askyesno(
            "Excluir Tarefa",
            f"Deseja excluir a tarefa '{tarefa['atividade']}'?",
        )
        if not confirmar:
            return

        sucesso = excluir_tarefa(tarefa_id)
        if not sucesso:
            messagebox.showerror("Erro", "Nao foi possivel excluir a tarefa.")
            return

        print(f"[EXCLUIR] Tarefa '{tarefa['atividade']}' removida.")
        self.recarregar_tarefas()


class NovaTarefaPagina(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        ctk.CTkLabel(
            self, text="NOVA TAREFA", font=ctk.CTkFont(size=34, weight="bold")
        ).pack(pady=30)

        self.entry_atividade = ctk.CTkEntry(
            self, placeholder_text="Atividade", width=450
        )
        self.entry_atividade.pack(pady=8)

        self.entry_hora = ctk.CTkEntry(self, placeholder_text="Hora (HH:MM)", width=450)
        self.entry_hora.pack(pady=8)
        self.entry_hora.bind("<KeyRelease>", self.filtrar_hora_numerica)

        self.option_status = ctk.CTkOptionMenu(
            self,
            values=["Pendente", "Em andamento", "Concluida"],
            width=450,
        )
        self.option_status.pack(pady=8)

        self.label_desc = ctk.CTkLabel(
            self, text="Descrição:", font=ctk.CTkFont(size=14)
        )
        self.label_desc.pack(pady=(20, 5), anchor="center", padx=10)

        self.text_descricao = ctk.CTkTextbox(self, width=450, height=160)
        self.text_descricao.pack(pady=8)

        botao_salvar = ctk.CTkButton(
            self, text="Salvar Tarefa", width=450, command=self.salvar_tarefa
        )
        botao_salvar.pack(pady=10)

    def filtrar_hora_numerica(self, event=None):
        """Permite somente numeros na digitacao e formata para HH:MM."""
        valor_atual = self.entry_hora.get()
        numeros = "".join(ch for ch in valor_atual if ch.isdigit())[:4]

        if len(numeros) >= 3:
            formatado = f"{numeros[:2]}:{numeros[2:]}"
        else:
            formatado = numeros

        if valor_atual != formatado:
            self.entry_hora.delete(0, "end")
            self.entry_hora.insert(0, formatado)

    def hora_valida(self, hora):
        if len(hora) != 5 or hora[2] != ":":
            return False

        hh, mm = hora.split(":")
        if not (hh.isdigit() and mm.isdigit()):
            return False

        h = int(hh)
        m = int(mm)
        return 0 <= h <= 23 and 0 <= m <= 59

    def salvar_tarefa(self):
        atividade = self.entry_atividade.get().strip()
        self.filtrar_hora_numerica()
        hora = self.entry_hora.get().strip()
        status = self.option_status.get().strip()
        descricao = self.text_descricao.get("1.0", "end").strip()

        if not atividade or not hora:
            messagebox.showwarning("Campos obrigatorios", "Preencha atividade e hora.")
            return

        if not self.hora_valida(hora):
            messagebox.showwarning("Hora invalida", "Use o formato HH:MM (ex.: 08:30).")
            return

        data_criacao = datetime.now().strftime("%d/%m/%Y")
        inserir_tarefa(atividade, hora, status, descricao, data_criacao)
        messagebox.showinfo("Sucesso", "Tarefa salva com sucesso.")

        self.entry_atividade.delete(0, "end")
        self.entry_hora.delete(0, "end")
        self.text_descricao.delete("1.0", "end")
        self.option_status.set("Pendente")

        frame_principal = self.master.master
        if hasattr(frame_principal, "pages") and "dashboard" in frame_principal.pages:
            frame_principal.pages["dashboard"].recarregar_tarefas()


class AssistentePagina(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.chat_service = None
        self.atividade_base = None

        self.label_titulo_assistente = ctk.CTkLabel(
            self, text="ASSISTENTE IA", font=ctk.CTkFont(size=34, weight="bold")
        )
        self.label_titulo_assistente.pack(pady=(20, 8))

        self.label_subtitulo_assistente = ctk.CTkLabel(
            self,
            text="Defina a atividade base e converse normalmente no chat.",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        self.label_subtitulo_assistente.pack(pady=(0, 14))

        self.frame_base_atividade = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_base_atividade.pack(fill="x", padx=30, pady=(0, 10))

        self.label_base_atividade = ctk.CTkLabel(
            self.frame_base_atividade,
            text="Atividade base:",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.label_base_atividade.pack(side="left", padx=(0, 8))

        self.opcoes_atividades = self._obter_opcoes_atividades()
        self.menu_atividade_base = ctk.CTkOptionMenu(
            self.frame_base_atividade,
            values=self.opcoes_atividades,
            width=500,
        )
        self.menu_atividade_base.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.botao_definir_base = ctk.CTkButton(
            self.frame_base_atividade,
            text="Usar",
            width=80,
            command=self.definir_atividade_base,
        )
        self.botao_definir_base.pack(side="left")

        self.frame_chat = ctk.CTkFrame(self, fg_color="#181818", corner_radius=12)
        self.frame_chat.pack(fill="both", expand=True, padx=30, pady=(0, 12))

        self.area_mensagens = ctk.CTkScrollableFrame(
            self.frame_chat,
            fg_color="transparent",
        )
        self.area_mensagens.pack(fill="both", expand=True, padx=10, pady=10)

        self.label_msg_inicial = ctk.CTkLabel(
            self.area_mensagens,
            text="Assistente pronto. Defina uma atividade base e envie sua mensagem.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
            justify="left",
        )
        self.label_msg_inicial.pack(anchor="w", padx=4, pady=4)

        self.frame_input_chat = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_input_chat.pack(fill="x", padx=30, pady=(0, 18))

        self.campo_mensagem = ctk.CTkEntry(
            self.frame_input_chat,
            placeholder_text="Digite sua mensagem...",
            height=36,
        )
        self.campo_mensagem.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.botao_enviar_mensagem = ctk.CTkButton(
            self.frame_input_chat,
            text="Enviar",
            width=90,
            height=36,
            command=self.enviar_mensagem_chat,
        )
        self.botao_enviar_mensagem.pack(side="left")

        self.campo_mensagem.bind("<Return>", self.enviar_mensagem_chat_event)

    def _obter_opcoes_atividades(self):
        tarefas = listar_tarefas()
        atividades = []
        for tarefa in tarefas:
            atividade = (tarefa.get("atividade") or "").strip()
            if atividade and atividade not in atividades:
                atividades.append(atividade)

        if not atividades:
            return ["Nenhuma atividade cadastrada"]
        return atividades

    def adicionar_bolha_mensagem(self, texto, autor):
        if autor == "usuario":
            cor_fundo = "#2E4A62"
            cor_texto = "#FFFFFF"
            anchor = "e"
        else:
            cor_fundo = "#2B2B2B"
            cor_texto = "#DDDDDD"
            anchor = "w"

        bolha = ctk.CTkLabel(
            self.area_mensagens,
            text=texto,
            justify="left",
            wraplength=560,
            fg_color=cor_fundo,
            text_color=cor_texto,
            corner_radius=10,
            padx=12,
            pady=8,
        )
        bolha.pack(anchor=anchor, padx=6, pady=5)

    def definir_atividade_base(self):
        atividade = self.menu_atividade_base.get().strip()
        if atividade == "Nenhuma atividade cadastrada":
            self.adicionar_bolha_mensagem(
                "Cadastre uma atividade na tela Nova Tarefa para usar o chat.",
                "assistente",
            )
            return

        self.atividade_base = atividade
        self.chat_service = ChatAtividadesService(atividade)

        for widget in self.area_mensagens.winfo_children():
            widget.destroy()

        self.adicionar_bolha_mensagem(
            self.chat_service.mensagem_inicial(), "assistente"
        )

    def enviar_mensagem_chat_event(self, event):
        self.enviar_mensagem_chat()

    def enviar_mensagem_chat(self):
        mensagem = self.campo_mensagem.get().strip()
        if not mensagem:
            return

        self.campo_mensagem.delete(0, "end")
        self.adicionar_bolha_mensagem(mensagem, "usuario")

        if not self.chat_service:
            resposta = "Selecione a atividade base e clique em 'Usar'."
            self.adicionar_bolha_mensagem(resposta, "assistente")
            return

        resposta = self.chat_service.enviar_mensagem(mensagem)
        self.adicionar_bolha_mensagem(resposta, "assistente")

    def resetar_interface(self):
        """Reseta os campos e mensagens visuais ao sair da aba assistente."""
        self.opcoes_atividades = self._obter_opcoes_atividades()
        self.menu_atividade_base.configure(values=self.opcoes_atividades)
        self.menu_atividade_base.set(self.opcoes_atividades[0])

        self.campo_mensagem.delete(0, "end")
        self.chat_service = None
        self.atividade_base = None

        for widget in self.area_mensagens.winfo_children():
            widget.destroy()

        self.label_msg_inicial = ctk.CTkLabel(
            self.area_mensagens,
            text="Assistente pronto. Selecione a atividade base e clique em 'Usar'.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
            justify="left",
        )
        self.label_msg_inicial.pack(anchor="w", padx=4, pady=4)


# -------------------- TELA PRINCIPAL --------------------


class FrameTelaPrincipal(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.pagina_atual = None

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.criar_sidebar()
        self.criar_content_area()
        self.criar_pages()

        self.show_page("dashboard")

    def criar_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        titulo = ctk.CTkLabel(
            self.sidebar,
            text="TAREFAS\nDIÁRIAS",
            font=ctk.CTkFont(size=28, weight="bold"),
            justify="left",
        )
        titulo.pack(padx=20, pady=(10, 5), anchor="w")

        data_atual = obter_data_atual()
        label_data_atual = ctk.CTkLabel(
            self.sidebar, text=data_atual, font=ctk.CTkFont(size=12), padx=8, pady=4
        )
        label_data_atual.pack(padx=20, pady=(0, 30), anchor="w")

        self.botao_dashboard = ctk.CTkButton(
            self.sidebar,
            text="📊 Dashboard",
            command=lambda: self.show_page("dashboard"),
        )
        self.botao_dashboard.pack(fill="x", padx=15, pady=8)

        self.botao_nova = ctk.CTkButton(
            self.sidebar,
            text="➕ Nova Tarefa",
            command=lambda: self.show_page("nova_tarefa"),
        )
        self.botao_nova.pack(fill="x", padx=15, pady=8)

        self.botao_ai = ctk.CTkButton(
            self.sidebar,
            text="🚀 Assistente IA",
            command=lambda: self.show_page("assistente"),
        )
        self.botao_ai.pack(fill="x", padx=15, pady=8)

    def criar_content_area(self):
        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def criar_pages(self):
        self.pages = {
            "dashboard": DashboardPagina(self.content),
            "nova_tarefa": NovaTarefaPagina(self.content),
            "assistente": AssistentePagina(self.content),
        }

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, page_name):
        if self.pagina_atual == "assistente" and page_name != "assistente":
            self.pages["assistente"].resetar_interface()

        self.pages[page_name].tkraise()
        self._reset_buttons()

        if page_name == "dashboard":
            self.botao_dashboard.configure(fg_color=("#1f6aa5", "#144870"))
            self.pages["dashboard"].atualizar_clima_dashboard()
        elif page_name == "nova_tarefa":
            self.botao_nova.configure(fg_color=("#1f6aa5", "#144870"))
        elif page_name == "assistente":
            self.botao_ai.configure(fg_color=("#1f6aa5", "#144870"))

        self.pagina_atual = page_name

    def _reset_buttons(self):
        normal = ("#3B8ED0", "#1F6AA5")
        self.botao_dashboard.configure(fg_color=normal)
        self.botao_nova.configure(fg_color=normal)
        self.botao_ai.configure(fg_color=normal)
