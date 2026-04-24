"""
╔══════════════════════════════════════════════╗
║         MERCADO DO POVO - Sistema de Caixa   ║
║         Versão 1.0 - Projeto Acadêmico       ║
╚══════════════════════════════════════════════╝
Requisitos: Python 3.8+  |  Biblioteca: tkinter (padrão), sqlite3
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
import os
from datetime import datetime

# ─────────────────────────────────────────────
#  CONFIGURAÇÕES GLOBAIS
# ─────────────────────────────────────────────
COR_AZUL        = "#1565C0"
COR_AZUL_ESCURO = "#0D47A1"
COR_AZUL_CLARO  = "#1E88E5"
COR_LARANJA     = "#F57C00"
COR_LARANJA_VIF = "#FF9800"
COR_BRANCO      = "#FFFFFF"
COR_FUNDO       = "#E3F2FD"
COR_CINZA       = "#ECEFF1"
COR_TEXTO       = "#212121"
COR_VERDE       = "#2E7D32"
COR_VERMELHO    = "#C62828"

DB_PATH = "mercado_do_povo.db"

USUARIO_FIXO = "admin"
SENHA_FIXA   = "1234"

# ─────────────────────────────────────────────
#  BANCO DE DADOS
# ─────────────────────────────────────────────
def inicializar_banco():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo      TEXT    NOT NULL UNIQUE,
            nome        TEXT    NOT NULL,
            preco       REAL    NOT NULL,
            estoque     INTEGER NOT NULL DEFAULT 0,
            cadastrado  TEXT    NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora   TEXT    NOT NULL,
            total       REAL    NOT NULL,
            pago        REAL    NOT NULL,
            troco       REAL    NOT NULL,
            itens       TEXT    NOT NULL
        )
    """)

    # Produtos de exemplo
    exemplos = [
        ("7891000315507", "Leite Integral 1L",   4.99,  50),
        ("7891910000244", "Arroz 5kg",           22.90,  30),
        ("7896004004922", "Feijão Carioca 1kg",   8.75,  40),
        ("7896016102055", "Açúcar Cristal 1kg",   4.50,  60),
        ("7891080040475", "Café Torrado 500g",   14.99,  25),
        ("7894321722016", "Óleo de Soja 900ml",   7.80,  35),
        ("7891000100103", "Macarrão Espaguete",   3.99,  70),
        ("7896523304038", "Sal Refinado 1kg",     2.29,  80),
    ]
    for cod, nome, preco, estoque in exemplos:
        cur.execute("""
            INSERT OR IGNORE INTO produtos (codigo, nome, preco, estoque, cadastrado)
            VALUES (?, ?, ?, ?, ?)
        """, (cod, nome, preco, estoque, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

def buscar_produto_por_codigo(codigo):
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("SELECT id, codigo, nome, preco, estoque FROM produtos WHERE codigo = ?", (codigo,))
    row = cur.fetchone()
    conn.close()
    return row

def buscar_todos_produtos():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("SELECT id, codigo, nome, preco, estoque, cadastrado FROM produtos ORDER BY nome")
    rows = cur.fetchall()
    conn.close()
    return rows

def cadastrar_produto(codigo, nome, preco, estoque):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO produtos (codigo, nome, preco, estoque, cadastrado)
            VALUES (?, ?, ?, ?, ?)
        """, (codigo, nome, preco, estoque, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return True, "Produto cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Código de barras já cadastrado."
    except Exception as e:
        return False, f"Erro: {e}"

def atualizar_produto(produto_id, nome, preco, estoque):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur  = conn.cursor()
        cur.execute("""
            UPDATE produtos SET nome=?, preco=?, estoque=? WHERE id=?
        """, (nome, preco, estoque, produto_id))
        conn.commit()
        conn.close()
        return True, "Produto atualizado!"
    except Exception as e:
        return False, f"Erro: {e}"

def excluir_produto(produto_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur  = conn.cursor()
        cur.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
        conn.commit()
        conn.close()
        return True, "Produto excluído!"
    except Exception as e:
        return False, f"Erro: {e}"

def registrar_venda(total, pago, troco, itens_texto):
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO vendas (data_hora, total, pago, troco, itens)
        VALUES (?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), total, pago, troco, itens_texto))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
#  HELPERS DE ESTILO
# ─────────────────────────────────────────────
def estilo_botao(btn, cor_fundo=COR_LARANJA, cor_texto=COR_BRANCO,
                 largura=18, altura=1, tamanho=11):
    btn.configure(
        bg=cor_fundo, fg=cor_texto,
        activebackground=COR_LARANJA_VIF, activeforeground=COR_BRANCO,
        font=("Helvetica", tamanho, "bold"),
        width=largura, height=altura,
        bd=0, relief="flat", cursor="hand2"
    )

def label_titulo(pai, texto, tamanho=22, cor=COR_BRANCO):
    tk.Label(pai, text=texto,
             bg=COR_AZUL_ESCURO, fg=cor,
             font=("Helvetica", tamanho, "bold")).pack(pady=(18, 4))

# ─────────────────────────────────────────────
#  APLICATIVO PRINCIPAL
# ─────────────────────────────────────────────
class MercadoDoPovo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mercado do Povo – Sistema de Caixa")
        self.geometry("1050x680")
        self.resizable(True, True)
        self.configure(bg=COR_FUNDO)
        self.minsize(900, 600)

        # Estado
        self.usuario_logado = None
        self.carrinho        = []          # lista de dicts {codigo, nome, preco, qtd}

        # Container único (frames empilhados)
        self.container = tk.Frame(self, bg=COR_FUNDO)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for FrameClass in (TelaLogin, TelaPrincipal, TelaProdutos):
            nome = FrameClass.__name__
            frame = FrameClass(self.container, self)
            self.frames[nome] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.mostrar_tela("TelaLogin")

    def mostrar_tela(self, nome):
        frame = self.frames[nome]
        frame.tkraise()
        if hasattr(frame, "ao_abrir"):
            frame.ao_abrir()

    def fazer_login(self, usuario, senha):
        if usuario == USUARIO_FIXO and senha == SENHA_FIXA:
            self.usuario_logado = usuario
            self.mostrar_tela("TelaPrincipal")
        else:
            messagebox.showerror("Acesso Negado",
                                 "Usuário ou senha incorretos!\n\nUsuário: admin\nSenha: 1234")

    def fazer_logout(self):
        if messagebox.askyesno("Sair", "Deseja realmente sair do sistema?"):
            self.carrinho.clear()
            self.usuario_logado = None
            self.mostrar_tela("TelaLogin")


# ─────────────────────────────────────────────
#  TELA 1 – LOGIN
# ─────────────────────────────────────────────
class TelaLogin(tk.Frame):
    def __init__(self, pai, app):
        super().__init__(pai, bg=COR_AZUL_ESCURO)
        self.app = app
        self._construir()

    def _construir(self):
        # Cabeçalho
        cab = tk.Frame(self, bg=COR_AZUL_ESCURO)
        cab.pack(fill="x")
        tk.Label(cab, text="🛒", bg=COR_AZUL_ESCURO, fg=COR_BRANCO,
                 font=("Helvetica", 52)).pack(pady=(40, 4))
        tk.Label(cab, text="MERCADO DO POVO",
                 bg=COR_AZUL_ESCURO, fg=COR_BRANCO,
                 font=("Helvetica", 28, "bold")).pack()
        tk.Label(cab, text="Sistema de Caixa",
                 bg=COR_AZUL_ESCURO, fg=COR_LARANJA_VIF,
                 font=("Helvetica", 13)).pack(pady=(0, 30))

        # Card de login
        card = tk.Frame(self, bg=COR_BRANCO, bd=0, relief="flat",
                        padx=50, pady=40)
        card.pack(ipadx=20, ipady=10)

        tk.Label(card, text="Faça seu login", bg=COR_BRANCO, fg=COR_AZUL_ESCURO,
                 font=("Helvetica", 16, "bold")).pack(pady=(0, 20))

        # Usuário
        tk.Label(card, text="Usuário:", bg=COR_BRANCO, fg=COR_TEXTO,
                 font=("Helvetica", 11, "bold"), anchor="w").pack(fill="x")
        self.ent_usuario = tk.Entry(card, font=("Helvetica", 12),
                                    bd=1, relief="solid", width=28)
        self.ent_usuario.pack(pady=(2, 12), ipady=6)
        self.ent_usuario.insert(0, "admin")

        # Senha
        tk.Label(card, text="Senha:", bg=COR_BRANCO, fg=COR_TEXTO,
                 font=("Helvetica", 11, "bold"), anchor="w").pack(fill="x")
        self.ent_senha = tk.Entry(card, font=("Helvetica", 12),
                                   show="●", bd=1, relief="solid", width=28)
        self.ent_senha.pack(pady=(2, 20), ipady=6)
        self.ent_senha.insert(0, "1234")

        # Botão entrar
        btn = tk.Button(card, text="  ENTRAR  →",
                        command=self._login,
                        bg=COR_LARANJA, fg=COR_BRANCO,
                        font=("Helvetica", 13, "bold"),
                        bd=0, relief="flat", cursor="hand2",
                        activebackground=COR_LARANJA_VIF,
                        activeforeground=COR_BRANCO)
        btn.pack(fill="x", ipady=8)

        # Dica
        tk.Label(card, text="Usuário: admin  |  Senha: 1234",
                 bg=COR_BRANCO, fg="#9E9E9E",
                 font=("Helvetica", 9)).pack(pady=(14, 0))

        # Enter aciona login
        self.ent_senha.bind("<Return>", lambda e: self._login())
        self.ent_usuario.bind("<Return>", lambda e: self.ent_senha.focus())

        # Rodapé
        tk.Label(self, text="© 2025 Mercado do Povo – Projeto Acadêmico",
                 bg=COR_AZUL_ESCURO, fg="#90CAF9",
                 font=("Helvetica", 9)).pack(side="bottom", pady=14)

    def _login(self):
        u = self.ent_usuario.get().strip()
        s = self.ent_senha.get().strip()
        self.app.fazer_login(u, s)


# ─────────────────────────────────────────────
#  TELA 2 – PRINCIPAL (CAIXA)
# ─────────────────────────────────────────────
class TelaPrincipal(tk.Frame):
    def __init__(self, pai, app):
        super().__init__(pai, bg=COR_FUNDO)
        self.app = app
        self._construir()

    # ── Construção ──────────────────────────
    def _construir(self):
        # Barra superior
        barra = tk.Frame(self, bg=COR_AZUL_ESCURO, height=56)
        barra.pack(fill="x")
        barra.pack_propagate(False)

        tk.Label(barra, text="🛒  MERCADO DO POVO – CAIXA",
                 bg=COR_AZUL_ESCURO, fg=COR_BRANCO,
                 font=("Helvetica", 16, "bold")).pack(side="left", padx=18)

        self.lbl_hora = tk.Label(barra, text="",
                                  bg=COR_AZUL_ESCURO, fg=COR_LARANJA_VIF,
                                  font=("Helvetica", 11))
        self.lbl_hora.pack(side="right", padx=10)

        btn_prod = tk.Button(barra, text="📦 Produtos",
                             command=lambda: self.app.mostrar_tela("TelaProdutos"),
                             bg=COR_AZUL_CLARO, fg=COR_BRANCO,
                             font=("Helvetica", 10, "bold"),
                             bd=0, relief="flat", cursor="hand2",
                             activebackground=COR_AZUL, padx=10)
        btn_prod.pack(side="right", pady=10, padx=4)

        btn_sair = tk.Button(barra, text="🚪 Sair",
                              command=self.app.fazer_logout,
                              bg=COR_VERMELHO, fg=COR_BRANCO,
                              font=("Helvetica", 10, "bold"),
                              bd=0, relief="flat", cursor="hand2",
                              activebackground="#B71C1C", padx=10)
        btn_sair.pack(side="right", pady=10, padx=4)

        # Corpo
        corpo = tk.Frame(self, bg=COR_FUNDO)
        corpo.pack(fill="both", expand=True, padx=14, pady=10)
        corpo.grid_columnconfigure(0, weight=2)
        corpo.grid_columnconfigure(1, weight=1)
        corpo.grid_rowconfigure(0, weight=1)

        # ── Coluna esquerda: scanner + carrinho ──
        esq = tk.Frame(corpo, bg=COR_FUNDO)
        esq.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Entrada de código
        scan_frame = tk.LabelFrame(esq, text=" 📷 Leitura de Código / Busca ",
                                   bg=COR_FUNDO, fg=COR_AZUL_ESCURO,
                                   font=("Helvetica", 11, "bold"),
                                   bd=2, relief="groove")
        scan_frame.pack(fill="x", pady=(0, 8))

        linha_scan = tk.Frame(scan_frame, bg=COR_FUNDO)
        linha_scan.pack(fill="x", padx=10, pady=8)

        tk.Label(linha_scan, text="Código de barras:", bg=COR_FUNDO,
                 font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=(0, 6))

        self.ent_codigo = tk.Entry(linha_scan, font=("Helvetica", 13),
                                    bd=2, relief="solid", width=24)
        self.ent_codigo.grid(row=0, column=1, padx=(0, 6), ipady=5)
        self.ent_codigo.bind("<Return>", lambda e: self._adicionar_item())

        tk.Label(linha_scan, text="Qtd:", bg=COR_FUNDO,
                 font=("Helvetica", 10, "bold")).grid(row=0, column=2, padx=(0, 4))

        self.spin_qtd = ttk.Spinbox(linha_scan, from_=1, to=999, width=5,
                                     font=("Helvetica", 12))
        self.spin_qtd.set(1)
        self.spin_qtd.grid(row=0, column=3, padx=(0, 6), ipady=4)

        btn_add = tk.Button(linha_scan, text="➕ Adicionar",
                             command=self._adicionar_item,
                             bg=COR_AZUL_CLARO, fg=COR_BRANCO,
                             font=("Helvetica", 10, "bold"),
                             bd=0, relief="flat", cursor="hand2",
                             activebackground=COR_AZUL, padx=8)
        btn_add.grid(row=0, column=4, padx=2)

        # Busca por nome
        linha2 = tk.Frame(scan_frame, bg=COR_FUNDO)
        linha2.pack(fill="x", padx=10, pady=(0, 8))

        tk.Label(linha2, text="Busca por nome:", bg=COR_FUNDO,
                 font=("Helvetica", 10)).grid(row=0, column=0, padx=(0, 6))
        self.ent_busca = tk.Entry(linha2, font=("Helvetica", 11),
                                   bd=2, relief="solid", width=30)
        self.ent_busca.grid(row=0, column=1, padx=(0, 6), ipady=4)
        self.ent_busca.bind("<KeyRelease>", self._buscar_nome)

        self.lbl_busca_res = tk.Label(linha2, text="", bg=COR_FUNDO,
                                       fg=COR_AZUL_CLARO, font=("Helvetica", 9))
        self.lbl_busca_res.grid(row=0, column=2, padx=4)

        # Listbox de sugestões
        self.lista_sugestoes = tk.Listbox(scan_frame, height=4,
                                           font=("Helvetica", 10),
                                           bd=1, relief="solid",
                                           selectbackground=COR_LARANJA,
                                           activestyle="none")
        self.lista_sugestoes.pack(fill="x", padx=10, pady=(0, 6))
        self.lista_sugestoes.bind("<Double-Button-1>", self._selecionar_sugestao)
        self.lista_sugestoes.bind("<Return>", self._selecionar_sugestao)

        # Carrinho
        cart_frame = tk.LabelFrame(esq, text=" 🛒 Carrinho de Compras ",
                                    bg=COR_FUNDO, fg=COR_AZUL_ESCURO,
                                    font=("Helvetica", 11, "bold"),
                                    bd=2, relief="groove")
        cart_frame.pack(fill="both", expand=True, pady=(0, 8))

        cols = ("Cód.", "Produto", "Qtd", "Unit. R$", "Subtotal R$")
        self.tree = ttk.Treeview(cart_frame, columns=cols,
                                  show="headings", height=12,
                                  selectmode="browse")
        larg = [100, 260, 50, 80, 100]
        for c, l in zip(cols, larg):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=l, anchor="center")
        self.tree.column("Produto", anchor="w")

        sb = ttk.Scrollbar(cart_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Botões do carrinho
        btn_row = tk.Frame(esq, bg=COR_FUNDO)
        btn_row.pack(fill="x")

        btn_rem = tk.Button(btn_row, text="🗑 Remover Item",
                             command=self._remover_item,
                             bg=COR_VERMELHO, fg=COR_BRANCO,
                             font=("Helvetica", 10, "bold"),
                             bd=0, relief="flat", cursor="hand2",
                             activebackground="#B71C1C", padx=10)
        btn_rem.pack(side="left", padx=4, pady=4)

        btn_limpar = tk.Button(btn_row, text="🔄 Limpar Tudo",
                                command=self._limpar_carrinho,
                                bg="#546E7A", fg=COR_BRANCO,
                                font=("Helvetica", 10, "bold"),
                                bd=0, relief="flat", cursor="hand2",
                                activebackground="#37474F", padx=10)
        btn_limpar.pack(side="left", padx=4, pady=4)

        # ── Coluna direita: totais + pagamento ──
        dir_ = tk.Frame(corpo, bg=COR_BRANCO, bd=2, relief="groove")
        dir_.grid(row=0, column=1, sticky="nsew")

        tk.Label(dir_, text="RESUMO DA COMPRA",
                 bg=COR_AZUL_ESCURO, fg=COR_BRANCO,
                 font=("Helvetica", 13, "bold")).pack(fill="x", pady=0)

        pad = {"bg": COR_BRANCO, "padx": 16, "pady": 6, "fill": "x"}

        # Itens
        fi = tk.Frame(dir_, bg=COR_BRANCO); fi.pack(**{"bg": COR_BRANCO, "fill": "x", "padx": 16, "pady": 8})
        tk.Label(fi, text="Itens:", bg=COR_BRANCO, font=("Helvetica", 11)).pack(side="left")
        self.lbl_itens = tk.Label(fi, text="0", bg=COR_BRANCO,
                                   font=("Helvetica", 11, "bold"), fg=COR_AZUL_CLARO)
        self.lbl_itens.pack(side="right")

        # Separator
        ttk.Separator(dir_, orient="horizontal").pack(fill="x", padx=10)

        # Total
        ft = tk.Frame(dir_, bg=COR_AZUL_ESCURO); ft.pack(fill="x", padx=0, pady=10)
        tk.Label(ft, text="TOTAL:", bg=COR_AZUL_ESCURO, fg=COR_BRANCO,
                 font=("Helvetica", 15, "bold")).pack(side="left", padx=16)
        self.lbl_total = tk.Label(ft, text="R$ 0,00",
                                   bg=COR_AZUL_ESCURO, fg=COR_LARANJA_VIF,
                                   font=("Helvetica", 18, "bold"))
        self.lbl_total.pack(side="right", padx=16)

        # Pagamento
        pg = tk.LabelFrame(dir_, text=" 💳 Pagamento ",
                            bg=COR_BRANCO, fg=COR_AZUL_ESCURO,
                            font=("Helvetica", 10, "bold"),
                            bd=2, relief="groove")
        pg.pack(fill="x", padx=12, pady=8)

        tk.Label(pg, text="Valor pago (R$):", bg=COR_BRANCO,
                 font=("Helvetica", 11, "bold")).pack(anchor="w", padx=10, pady=(8, 2))

        self.ent_pago = tk.Entry(pg, font=("Helvetica", 16),
                                  bd=2, relief="solid", justify="right")
        self.ent_pago.pack(fill="x", padx=10, pady=(0, 6), ipady=6)
        self.ent_pago.bind("<Return>", lambda e: self._calcular_troco())

        # Botões de nota rápida
        notas_frame = tk.Frame(pg, bg=COR_BRANCO)
        notas_frame.pack(fill="x", padx=10, pady=(0, 8))
        tk.Label(notas_frame, text="Notas rápidas:", bg=COR_BRANCO,
                 font=("Helvetica", 9)).pack(anchor="w")
        notas_row = tk.Frame(notas_frame, bg=COR_BRANCO)
        notas_row.pack(fill="x")
        for nota in [10, 20, 50, 100, 200]:
            tk.Button(notas_row,
                      text=f"R${nota}",
                      command=lambda n=nota: self._nota_rapida(n),
                      bg=COR_CINZA, fg=COR_AZUL_ESCURO,
                      font=("Helvetica", 9, "bold"),
                      bd=1, relief="solid", cursor="hand2",
                      width=5).pack(side="left", padx=2)

        btn_calc = tk.Button(pg, text="💰 CALCULAR TROCO",
                              command=self._calcular_troco,
                              bg=COR_LARANJA, fg=COR_BRANCO,
                              font=("Helvetica", 12, "bold"),
                              bd=0, relief="flat", cursor="hand2",
                              activebackground=COR_LARANJA_VIF)
        btn_calc.pack(fill="x", padx=10, pady=(0, 4), ipady=8)

        # Troco
        tr = tk.Frame(dir_, bg=COR_VERDE); tr.pack(fill="x", padx=12, pady=2)
        tk.Label(tr, text="TROCO:", bg=COR_VERDE, fg=COR_BRANCO,
                 font=("Helvetica", 13, "bold")).pack(side="left", padx=14, pady=6)
        self.lbl_troco = tk.Label(tr, text="R$ 0,00",
                                   bg=COR_VERDE, fg=COR_BRANCO,
                                   font=("Helvetica", 17, "bold"))
        self.lbl_troco.pack(side="right", padx=14)

        # Status
        self.lbl_status = tk.Label(dir_, text="",
                                    bg=COR_BRANCO, fg=COR_VERMELHO,
                                    font=("Helvetica", 10, "bold"),
                                    wraplength=220)
        self.lbl_status.pack(padx=12, pady=4)

        # Finalizar venda
        btn_fin = tk.Button(dir_, text="✅  FINALIZAR VENDA",
                             command=self._finalizar_venda,
                             bg=COR_AZUL_ESCURO, fg=COR_BRANCO,
                             font=("Helvetica", 13, "bold"),
                             bd=0, relief="flat", cursor="hand2",
                             activebackground=COR_AZUL_CLARO)
        btn_fin.pack(fill="x", padx=12, pady=8, ipady=10)

        # ── Iniciar relógio ──
        self._atualizar_hora()

    # ── Relógio ─────────────────────────────
    def _atualizar_hora(self):
        agora = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
        self.lbl_hora.configure(text=agora)
        self.after(1000, self._atualizar_hora)

    # ── Ao abrir tela ────────────────────────
    def ao_abrir(self):
        self.ent_codigo.focus()

    # ── Adicionar item ───────────────────────
    def _adicionar_item(self):
        codigo = self.ent_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Aviso", "Digite o código do produto.")
            return
        try:
            qtd = int(self.spin_qtd.get())
            if qtd < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida.")
            return

        produto = buscar_produto_por_codigo(codigo)
        if not produto:
            messagebox.showerror("Não encontrado",
                                 f"Código '{codigo}' não cadastrado.")
            self.ent_codigo.delete(0, "end")
            return

        pid, cod, nome, preco, estoque = produto

        # Verificar se já está no carrinho
        for item in self.app.carrinho:
            if item["codigo"] == cod:
                item["qtd"] += qtd
                break
        else:
            self.app.carrinho.append({
                "codigo": cod, "nome": nome,
                "preco": preco, "qtd": qtd
            })

        self.ent_codigo.delete(0, "end")
        self.spin_qtd.set(1)
        self._atualizar_carrinho()
        self.ent_codigo.focus()

    # ── Busca por nome ───────────────────────
    def _buscar_nome(self, event=None):
        termo = self.ent_busca.get().strip().lower()
        self.lista_sugestoes.delete(0, "end")
        if not termo:
            return
        todos = buscar_todos_produtos()
        achou = [p for p in todos if termo in p[2].lower()]
        for p in achou[:8]:
            self.lista_sugestoes.insert("end",
                f"{p[1]}  |  {p[2]}  |  R$ {p[3]:.2f}")
        self._sugestoes_cache = achou

    def _selecionar_sugestao(self, event=None):
        sel = self.lista_sugestoes.curselection()
        if not sel:
            return
        idx = sel[0]
        produto = self._sugestoes_cache[idx]
        self.ent_codigo.delete(0, "end")
        self.ent_codigo.insert(0, produto[1])
        self.lista_sugestoes.delete(0, "end")
        self.ent_busca.delete(0, "end")
        self._adicionar_item()

    # ── Atualizar visão do carrinho ──────────
    def _atualizar_carrinho(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        total = 0.0
        total_itens = 0
        for item in self.app.carrinho:
            sub = item["preco"] * item["qtd"]
            total += sub
            total_itens += item["qtd"]
            self.tree.insert("", "end", values=(
                item["codigo"],
                item["nome"],
                item["qtd"],
                f"{item['preco']:.2f}",
                f"{sub:.2f}"
            ))

        self.lbl_itens.configure(text=str(total_itens))
        self.lbl_total.configure(text=f"R$ {total:,.2f}".replace(",", "X")
                                  .replace(".", ",").replace("X", "."))
        self.lbl_status.configure(text="")

    # ── Remover item selecionado ─────────────
    def _remover_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um item para remover.")
            return
        idx = self.tree.index(sel[0])
        del self.app.carrinho[idx]
        self._atualizar_carrinho()

    def _limpar_carrinho(self):
        if not self.app.carrinho:
            return
        if messagebox.askyesno("Limpar", "Deseja remover todos os itens?"):
            self.app.carrinho.clear()
            self._atualizar_carrinho()
            self.lbl_troco.configure(text="R$ 0,00")
            self.ent_pago.delete(0, "end")

    # ── Nota rápida ─────────────────────────
    def _nota_rapida(self, valor):
        self.ent_pago.delete(0, "end")
        self.ent_pago.insert(0, str(valor))

    # ── Calcular troco ───────────────────────
    def _calcular_troco(self):
        if not self.app.carrinho:
            messagebox.showwarning("Aviso", "Carrinho vazio.")
            return

        total = sum(i["preco"] * i["qtd"] for i in self.app.carrinho)

        pago_txt = self.ent_pago.get().strip().replace(",", ".")
        try:
            pago = float(pago_txt)
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor de pagamento válido.")
            return

        if pago < total:
            falta = total - pago
            self.lbl_status.configure(
                text=f"⚠ Valor insuficiente!\nFaltam R$ {falta:.2f}",
                fg=COR_VERMELHO)
            self.lbl_troco.configure(text="R$ 0,00")
            return

        troco = pago - total
        self.lbl_troco.configure(
            text=f"R$ {troco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.lbl_status.configure(
            text=f"✔ Total: R$ {total:.2f}  |  Pago: R$ {pago:.2f}",
            fg=COR_VERDE)

    # ── Finalizar venda ──────────────────────
    def _finalizar_venda(self):
        if not self.app.carrinho:
            messagebox.showwarning("Aviso", "Carrinho vazio.")
            return

        total = sum(i["preco"] * i["qtd"] for i in self.app.carrinho)

        pago_txt = self.ent_pago.get().strip().replace(",", ".")
        try:
            pago = float(pago_txt)
        except ValueError:
            messagebox.showerror("Erro", "Informe o valor pago antes de finalizar.")
            return

        if pago < total:
            messagebox.showerror("Pagamento insuficiente",
                                 f"O valor pago (R$ {pago:.2f}) é menor que o total (R$ {total:.2f}).")
            return

        troco = pago - total

        # Cupom
        itens_txt = "\n".join(
            f"{i['nome']} x{i['qtd']} = R$ {i['preco']*i['qtd']:.2f}"
            for i in self.app.carrinho
        )

        cupom = (
            "=" * 40 + "\n"
            "       MERCADO DO POVO\n"
            f"  {datetime.now().strftime('%d/%m/%Y  %H:%M:%S')}\n"
            "=" * 40 + "\n"
            + itens_txt + "\n"
            "–" * 40 + "\n"
            f"  TOTAL:   R$ {total:>10.2f}\n"
            f"  PAGO:    R$ {pago:>10.2f}\n"
            f"  TROCO:   R$ {troco:>10.2f}\n"
            "=" * 40 + "\n"
            "   Obrigado pela preferência!\n"
            "=" * 40
        )

        # Salvar no banco
        registrar_venda(total, pago, troco, itens_txt)

        messagebox.showinfo("Venda Finalizada! ✅", cupom)

        # Limpar
        self.app.carrinho.clear()
        self._atualizar_carrinho()
        self.ent_pago.delete(0, "end")
        self.lbl_troco.configure(text="R$ 0,00")
        self.lbl_status.configure(text="")


# ─────────────────────────────────────────────
#  TELA 3 – CADASTRO DE PRODUTOS
# ─────────────────────────────────────────────
class TelaProdutos(tk.Frame):
    def __init__(self, pai, app):
        super().__init__(pai, bg=COR_FUNDO)
        self.app = app
        self._produto_selecionado_id = None
        self._construir()

    def _construir(self):
        # Barra superior
        barra = tk.Frame(self, bg=COR_AZUL_ESCURO, height=52)
        barra.pack(fill="x")
        barra.pack_propagate(False)

        tk.Label(barra, text="📦  CADASTRO DE PRODUTOS",
                 bg=COR_AZUL_ESCURO, fg=COR_BRANCO,
                 font=("Helvetica", 15, "bold")).pack(side="left", padx=18)

        btn_voltar = tk.Button(barra, text="← Voltar ao Caixa",
                                command=lambda: self.app.mostrar_tela("TelaPrincipal"),
                                bg=COR_LARANJA, fg=COR_BRANCO,
                                font=("Helvetica", 10, "bold"),
                                bd=0, relief="flat", cursor="hand2",
                                activebackground=COR_LARANJA_VIF, padx=12)
        btn_voltar.pack(side="right", pady=8, padx=10)

        # Corpo
        corpo = tk.Frame(self, bg=COR_FUNDO)
        corpo.pack(fill="both", expand=True, padx=12, pady=10)
        corpo.grid_columnconfigure(0, weight=1)
        corpo.grid_columnconfigure(1, weight=2)
        corpo.grid_rowconfigure(0, weight=1)

        # ── Coluna esquerda: formulário ──────
        form = tk.LabelFrame(corpo, text=" ✏ Cadastrar / Editar Produto ",
                              bg=COR_BRANCO, fg=COR_AZUL_ESCURO,
                              font=("Helvetica", 11, "bold"),
                              bd=2, relief="groove")
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        campos = [
            ("Código de Barras*:", "ent_cod"),
            ("Nome do Produto*:",  "ent_nome"),
            ("Preço (R$)*:",       "ent_preco"),
            ("Estoque*:",          "ent_estoque"),
        ]
        self._entradas = {}
        for i, (label, nome) in enumerate(campos):
            tk.Label(form, text=label, bg=COR_BRANCO,
                     font=("Helvetica", 10, "bold")).grid(
                row=i*2, column=0, columnspan=2, sticky="w", padx=18, pady=(12, 0))
            ent = tk.Entry(form, font=("Helvetica", 12),
                           bd=2, relief="solid", width=26)
            ent.grid(row=i*2+1, column=0, columnspan=2,
                     sticky="ew", padx=18, ipady=5)
            self._entradas[nome] = ent

        # Dica leitor de código
        tk.Label(form, text="💡 Com leitor USB: posicione o cursor em 'Código'\n"
                            "    e leia o código de barras normalmente.",
                 bg=COR_BRANCO, fg="#607D8B",
                 font=("Helvetica", 9), justify="left").grid(
            row=8, column=0, columnspan=2, padx=18, pady=10, sticky="w")

        # Botões do formulário
        bf = tk.Frame(form, bg=COR_BRANCO)
        bf.grid(row=9, column=0, columnspan=2, pady=12, padx=18, sticky="ew")

        btn_salvar = tk.Button(bf, text="💾 Salvar",
                                command=self._salvar_produto,
                                bg=COR_AZUL_CLARO, fg=COR_BRANCO,
                                font=("Helvetica", 11, "bold"),
                                bd=0, relief="flat", cursor="hand2",
                                activebackground=COR_AZUL, padx=12)
        btn_salvar.pack(side="left", padx=4, ipady=6, expand=True, fill="x")

        btn_novo = tk.Button(bf, text="🆕 Novo",
                              command=self._limpar_form,
                              bg="#546E7A", fg=COR_BRANCO,
                              font=("Helvetica", 11, "bold"),
                              bd=0, relief="flat", cursor="hand2",
                              activebackground="#37474F", padx=12)
        btn_novo.pack(side="left", padx=4, ipady=6, expand=True, fill="x")

        btn_excl = tk.Button(bf, text="🗑 Excluir",
                              command=self._excluir_produto,
                              bg=COR_VERMELHO, fg=COR_BRANCO,
                              font=("Helvetica", 11, "bold"),
                              bd=0, relief="flat", cursor="hand2",
                              activebackground="#B71C1C", padx=12)
        btn_excl.pack(side="left", padx=4, ipady=6, expand=True, fill="x")

        self.lbl_form_status = tk.Label(form, text="",
                                         bg=COR_BRANCO, fg=COR_VERDE,
                                         font=("Helvetica", 10, "bold"),
                                         wraplength=260)
        self.lbl_form_status.grid(row=10, column=0, columnspan=2, pady=6)

        # ── Coluna direita: tabela de produtos ──
        lista_frame = tk.LabelFrame(corpo, text=" 📋 Produtos Cadastrados ",
                                     bg=COR_FUNDO, fg=COR_AZUL_ESCURO,
                                     font=("Helvetica", 11, "bold"),
                                     bd=2, relief="groove")
        lista_frame.grid(row=0, column=1, sticky="nsew")

        # Busca
        busca_row = tk.Frame(lista_frame, bg=COR_FUNDO)
        busca_row.pack(fill="x", padx=8, pady=8)
        tk.Label(busca_row, text="🔍 Filtrar:", bg=COR_FUNDO,
                 font=("Helvetica", 10)).pack(side="left", padx=4)
        self.ent_filtro = tk.Entry(busca_row, font=("Helvetica", 11),
                                    bd=2, relief="solid", width=28)
        self.ent_filtro.pack(side="left", padx=4, ipady=4)
        self.ent_filtro.bind("<KeyRelease>", lambda e: self._carregar_tabela())

        self.lbl_qtd_prod = tk.Label(busca_row, text="", bg=COR_FUNDO,
                                      fg=COR_AZUL_CLARO,
                                      font=("Helvetica", 10, "bold"))
        self.lbl_qtd_prod.pack(side="right", padx=8)

        # Treeview
        cols = ("Código", "Nome", "Preço R$", "Estoque", "Cadastrado")
        self.tree_prod = ttk.Treeview(lista_frame, columns=cols,
                                       show="headings", height=20,
                                       selectmode="browse")
        larg = [130, 220, 80, 70, 130]
        for c, l in zip(cols, larg):
            self.tree_prod.heading(c, text=c,
                                   command=lambda col=c: self._ordenar(col))
            self.tree_prod.column(c, width=l, anchor="center")
        self.tree_prod.column("Nome", anchor="w")

        sb2 = ttk.Scrollbar(lista_frame, orient="vertical",
                             command=self.tree_prod.yview)
        self.tree_prod.configure(yscrollcommand=sb2.set)
        self.tree_prod.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")

        self.tree_prod.bind("<<TreeviewSelect>>", self._ao_selecionar)

    # ── Ao abrir ─────────────────────────────
    def ao_abrir(self):
        self._carregar_tabela()
        self._limpar_form()

    # ── Carregar tabela ──────────────────────
    def _carregar_tabela(self):
        filtro = self.ent_filtro.get().strip().lower()
        for row in self.tree_prod.get_children():
            self.tree_prod.delete(row)

        todos = buscar_todos_produtos()
        mostrados = 0
        for p in todos:
            if filtro and filtro not in p[2].lower() and filtro not in p[1].lower():
                continue
            self.tree_prod.insert("", "end", iid=str(p[0]), values=(
                p[1], p[2],
                f"{p[3]:.2f}", p[4], p[5]
            ))
            mostrados += 1

        self.lbl_qtd_prod.configure(text=f"{mostrados} produto(s)")

    # ── Ao selecionar linha ──────────────────
    def _ao_selecionar(self, event=None):
        sel = self.tree_prod.selection()
        if not sel:
            return
        iid = sel[0]
        vals = self.tree_prod.item(iid, "values")
        self._produto_selecionado_id = int(iid)

        self._entradas["ent_cod"].configure(state="normal")
        self._limpar_form(manter_id=True)

        self._entradas["ent_cod"].insert(0, vals[0])
        self._entradas["ent_cod"].configure(state="disabled")
        self._entradas["ent_nome"].insert(0, vals[1])
        self._entradas["ent_preco"].insert(0, vals[2])
        self._entradas["ent_estoque"].insert(0, vals[3])

    # ── Limpar formulário ────────────────────
    def _limpar_form(self, manter_id=False):
        if not manter_id:
            self._produto_selecionado_id = None
        for e in self._entradas.values():
            e.configure(state="normal")
            e.delete(0, "end")
        self.lbl_form_status.configure(text="")

    # ── Salvar (inserir ou atualizar) ────────
    def _salvar_produto(self):
        cod    = self._entradas["ent_cod"].get().strip()
        nome   = self._entradas["ent_nome"].get().strip()
        preco  = self._entradas["ent_preco"].get().strip().replace(",", ".")
        estoque = self._entradas["ent_estoque"].get().strip()

        if not cod or not nome or not preco or not estoque:
            self.lbl_form_status.configure(
                text="⚠ Preencha todos os campos!", fg=COR_VERMELHO)
            return
        try:
            preco_f   = float(preco)
            estoque_i = int(estoque)
            if preco_f <= 0 or estoque_i < 0:
                raise ValueError
        except ValueError:
            self.lbl_form_status.configure(
                text="⚠ Preço e estoque inválidos!", fg=COR_VERMELHO)
            return

        if self._produto_selecionado_id:
            ok, msg = atualizar_produto(
                self._produto_selecionado_id, nome, preco_f, estoque_i)
        else:
            ok, msg = cadastrar_produto(cod, nome, preco_f, estoque_i)

        cor = COR_VERDE if ok else COR_VERMELHO
        self.lbl_form_status.configure(text=msg, fg=cor)

        if ok:
            self._limpar_form()
            self._carregar_tabela()

    # ── Excluir produto ──────────────────────
    def _excluir_produto(self):
        if not self._produto_selecionado_id:
            messagebox.showinfo("Aviso", "Selecione um produto na lista.")
            return
        if messagebox.askyesno("Excluir", "Confirma a exclusão do produto?"):
            ok, msg = excluir_produto(self._produto_selecionado_id)
            cor = COR_VERDE if ok else COR_VERMELHO
            self.lbl_form_status.configure(text=msg, fg=cor)
            if ok:
                self._limpar_form()
                self._carregar_tabela()

    # ── Ordenar coluna ───────────────────────
    def _ordenar(self, coluna):
        dados = [(self.tree_prod.set(c, coluna), c)
                 for c in self.tree_prod.get_children("")]
        dados.sort()
        for idx, (_, c) in enumerate(dados):
            self.tree_prod.move(c, "", idx)


# ─────────────────────────────────────────────
#  ENTRADA PRINCIPAL
# ─────────────────────────────────────────────
if __name__ == "__main__":
    inicializar_banco()
    app = MercadoDoPovo()

    # Ícone opcional (ignora se não existir)
    try:
        app.iconbitmap("icone.ico")
    except Exception:
        pass

    app.mainloop()