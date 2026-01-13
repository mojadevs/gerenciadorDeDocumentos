import customtkinter as ctk
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, filedialog
import re
import unicodedata
import shutil
import os

# ========== CONFIGURAÇÕES ==========
NOME_APP = "SistemaDocumentosAdvocacia"
PASTA_BASE = Path(os.getenv("LOCALAPPDATA")) / NOME_APP / "temas"
PASTA_BASE.mkdir(parents=True, exist_ok=True)

EXTENSOES_PERMITIDAS = [".pdf", ".docx"]
tema_selecionado = None

VERDE = "#2e7d32"
VERDE_HOVER = "#1b5e20"
AZUL = "#1565c0"
AZUL_HOVER = "#0d47a1"
VERMELHO = "#b00020"
VERMELHO_HOVER = "#7f0015"

# ========== FUNÇÕES ==========
def padronizar_nome(nome):
    nome = unicodedata.normalize("NFKD", nome).encode("ASCII", "ignore").decode("ASCII")
    nome = nome.lower()
    nome = re.sub(r"\s+", "_", nome)
    nome = re.sub(r"[^a-z0-9_]", "", nome)
    return nome

def deletar_arquivo():
    if not tema_selecionado:
        messagebox.showwarning("Aviso", "Selecione um tema.")
        return

    selecao = lista_arquivos.curselection()
    if not selecao:
        messagebox.showwarning("Aviso", "Selecione um arquivo.")
        return

    nome = lista_arquivos.get(selecao[0])
    caminho = tema_selecionado / nome

    
    if caminho.exists():
        # Pergunta se o usuário realmente quer apagar
    
        if tk.messagebox.askyesno("Excluir Arquivo", f"Tem certeza que quer apagar '{nome}'?"):
            caminho.unlink() 
            atualizar_lista_arquivos() 


def abrir_arquivo(event):
    if not tema_selecionado:
        return

    selecao = lista_arquivos.curselection()
    if not selecao:
        return

    nome = lista_arquivos.get(selecao[0])
    caminho = tema_selecionado / nome

    if caminho.exists():
        os.startfile(caminho)


def atualizar_lista_temas():
    for w in frame_lista_temas.winfo_children():
        w.destroy()

    temas = sorted([p for p in PASTA_BASE.iterdir() if p.is_dir()])

    if not temas:
        ctk.CTkLabel(frame_lista_temas, text="Nenhum tema cadastrado").pack(pady=10)
        return

    for pasta in temas:
        ctk.CTkButton(
            frame_lista_temas,
            text=pasta.name,
            anchor="w",
            command=lambda p=pasta: selecionar_tema(p)
        ).pack(fill="x", padx=5, pady=4)


def atualizar_lista_arquivos():
    lista_arquivos.delete(0, "end")

    if not tema_selecionado:
        return

    arquivos = sorted(tema_selecionado.iterdir())

    if not arquivos:
        lista_arquivos.insert("end", "Nenhum arquivo neste tema")
        return

    for arq in arquivos:
        lista_arquivos.insert("end", arq.name)


def criar_tema():
    nome = entry_tema.get().strip()
    if not nome:
        messagebox.showerror("Erro", "Digite um nome para o tema.")
        return

    pasta_nome = padronizar_nome(nome)
    caminho = PASTA_BASE / pasta_nome

    if caminho.exists():
        messagebox.showwarning("Aviso", "Este tema já existe.")
        return

    caminho.mkdir()
    entry_tema.delete(0, "end")
    atualizar_lista_temas()


def editar_tema():
    if not tema_selecionado:
        messagebox.showwarning("Aviso", "Selecione um tema.")
        return

    novo_nome = simpledialog.askstring(
        "Editar Tema",
        "Novo nome do tema:",
        initialvalue=tema_selecionado.name
    )
    if not novo_nome:
        return

    novo_nome_norm = padronizar_nome(novo_nome)
    novo_caminho = PASTA_BASE / novo_nome_norm

    if novo_caminho.exists():
        messagebox.showerror("Erro", "Já existe um tema com esse nome.")
        return

    tema_selecionado.rename(novo_caminho)
    selecionar_tema(novo_caminho)
    atualizar_lista_temas()


def excluir_tema():
    global tema_selecionado

    if not tema_selecionado:
        messagebox.showwarning("Aviso", "Selecione um tema.")
        return

    if not messagebox.askyesno(
        "Excluir Tema",
        f"O tema '{tema_selecionado.name}' será excluído com todos os arquivos.\nDeseja continuar?"
    ):
        return

    for arq in tema_selecionado.iterdir():
        arq.unlink()
    tema_selecionado.rmdir()

    tema_selecionado = None
    label_tema_atual.configure(text="Tema selecionado: nenhum")
    lista_arquivos.delete(0, "end")
    atualizar_lista_temas()


def selecionar_tema(pasta):
    global tema_selecionado
    tema_selecionado = pasta
    label_tema_atual.configure(text=f"Tema selecionado: {pasta.name}")
    atualizar_lista_arquivos()


def adicionar_arquivo():
    if not tema_selecionado:
        messagebox.showwarning("Aviso", "Selecione um tema antes.")
        return

    caminho = filedialog.askopenfilename(
        title="Selecionar arquivo",
        filetypes=[("PDF e DOCX", "*.pdf *.docx")]
    )
    if not caminho:
        return

    origem = Path(caminho)
    if origem.suffix.lower() not in EXTENSOES_PERMITIDAS:
        messagebox.showerror("Erro", "Tipo de arquivo não permitido.")
        return

    destino = tema_selecionado / origem.name
    if destino.exists():
        messagebox.showwarning("Aviso", "Este arquivo já existe no tema.")
        return

    shutil.copy2(origem, destino)
    atualizar_lista_arquivos()

# ========== INTERFACE ==========
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Sistema de Gestão de Arquivos")
app.geometry("900x520")
app.resizable(False, False)

frame_principal = ctk.CTkFrame(app)
frame_principal.pack(expand=True, fill="both", padx=15, pady=15)

# ----- TEMAS -----
frame_temas = ctk.CTkFrame(frame_principal, width=300)
frame_temas.pack(side="left", fill="y", padx=10)

ctk.CTkLabel(
    frame_temas,
    text="Temas",
    font=ctk.CTkFont(size=18, weight="bold")
).pack(pady=10)

entry_tema = ctk.CTkEntry(frame_temas, placeholder_text="Novo tema")
entry_tema.pack(fill="x", padx=10, pady=5)

ctk.CTkButton(
    frame_temas,
    text="Criar Tema",
    command=criar_tema,
    fg_color=VERDE,
    hover_color=VERDE_HOVER
).pack(pady=5)

ctk.CTkButton(
    frame_temas,
    text="Editar Tema",
    command=editar_tema,
    fg_color=AZUL,
    hover_color=AZUL_HOVER
).pack(pady=5)

ctk.CTkButton(
    frame_temas,
    text="Excluir Tema",
    command=excluir_tema,
    fg_color=VERMELHO,
    hover_color=VERMELHO_HOVER
).pack(pady=5)

ctk.CTkButton(
    frame_temas,
    text="Excluir Arquivo",
    command=deletar_arquivo,
    fg_color=VERMELHO,
    hover_color=VERMELHO_HOVER
).pack(pady=5)

frame_lista_temas = ctk.CTkScrollableFrame(frame_temas)
frame_lista_temas.pack(fill="both", expand=True, padx=10, pady=10)

# ----- ARQUIVOS -----
frame_arquivos = ctk.CTkFrame(frame_principal)
frame_arquivos.pack(side="right", fill="both", expand=True, padx=10)

label_tema_atual = ctk.CTkLabel(
    frame_arquivos,
    text="Tema selecionado: nenhum",
    font=ctk.CTkFont(size=16, weight="bold")
)
label_tema_atual.pack(pady=10)

ctk.CTkButton(
    frame_arquivos,
    text="Adicionar Arquivo (PDF/DOCX)",
    command=adicionar_arquivo,
    fg_color=VERDE,
    hover_color=VERDE_HOVER
).pack(pady=5)

lista_arquivos = tk.Listbox(
    frame_arquivos,
    font=("Segoe UI", 11),
    activestyle="none"
)

lista_arquivos.pack(fill="both", expand=True, padx=10, pady=10)
lista_arquivos.bind("<Double-Button-1>", abrir_arquivo)

# ========== INÍCIO ==========
atualizar_lista_temas()
app.mainloop()
