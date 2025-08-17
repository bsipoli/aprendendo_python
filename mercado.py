import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Controle de Estoque de Mercado")
        self.geometry("800x600")
        self.create_widgets()
        self.create_db()
        self.load_products()

    def create_db(self):
        self.conn = sqlite3.connect("estoque.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                descricao TEXT,
                codigo_barras TEXT UNIQUE,
                preco_compra REAL,
                preco_venda REAL,
                quantidade INTEGER
            )
        """)
        self.conn.commit()

    def create_widgets(self):
        # Frame para os campos de entrada
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10)

        ttk.Label(input_frame, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
        self.nome_entry = ttk.Entry(input_frame)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Descrição:").grid(row=1, column=0, padx=5, pady=5)
        self.descricao_entry = ttk.Entry(input_frame)
        self.descricao_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Cód. Barras:").grid(row=0, column=2, padx=5, pady=5)
        self.codigo_barras_entry = ttk.Entry(input_frame)
        self.codigo_barras_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Preço Compra:").grid(row=1, column=2, padx=5, pady=5)
        self.preco_compra_entry = ttk.Entry(input_frame)
        self.preco_compra_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Preço Venda:").grid(row=0, column=4, padx=5, pady=5)
        self.preco_venda_entry = ttk.Entry(input_frame)
        self.preco_venda_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(input_frame, text="Quantidade:").grid(row=1, column=4, padx=5, pady=5)
        self.quantidade_entry = ttk.Entry(input_frame)
        self.quantidade_entry.grid(row=1, column=5, padx=5, pady=5)

        # Frame para os botões
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Adicionar", command=self.add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Atualizar", command=self.update_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deletar", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpar Campos", command=self.clear_entries).pack(side=tk.LEFT, padx=5)

        # Treeview para exibir os produtos
        self.tree = ttk.Treeview(self, columns=("ID", "Nome", "Cód. Barras", "Preço Venda", "Qtd"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Cód. Barras", text="Código de Barras")
        self.tree.heading("Preço Venda", text="Preço de Venda")
        self.tree.heading("Qtd", text="Quantidade")
        self.tree.pack(pady=20, padx=10, fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_product_select)


    def load_products(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.cursor.execute("SELECT id, nome, codigo_barras, preco_venda, quantidade FROM produtos")
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def add_product(self):
        nome = self.nome_entry.get()
        descricao = self.descricao_entry.get()
        codigo_barras = self.codigo_barras_entry.get()
        preco_compra = self.preco_compra_entry.get()
        preco_venda = self.preco_venda_entry.get()
        quantidade = self.quantidade_entry.get()

        if not all([nome, codigo_barras, preco_venda, quantidade]):
            messagebox.showerror("Erro", "Todos os campos marcados são obrigatórios!")
            return

        try:
            self.cursor.execute("""
                INSERT INTO produtos (nome, descricao, codigo_barras, preco_compra, preco_venda, quantidade)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nome, descricao, codigo_barras, float(preco_compra), float(preco_venda), int(quantidade)))
            self.conn.commit()
            self.load_products()
            self.clear_entries()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Código de barras já cadastrado!")
        except ValueError:
            messagebox.showerror("Erro", "Preço e quantidade devem ser números!")

    def update_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione um produto para atualizar!")
            return

        selected_id = self.tree.item(selected_item, "values")[0]
        nome = self.nome_entry.get()
        descricao = self.descricao_entry.get()
        codigo_barras = self.codigo_barras_entry.get()
        preco_compra = self.preco_compra_entry.get()
        preco_venda = self.preco_venda_entry.get()
        quantidade = self.quantidade_entry.get()

        if not all([nome, codigo_barras, preco_venda, quantidade]):
            messagebox.showerror("Erro", "Todos os campos marcados são obrigatórios!")
            return

        try:
            self.cursor.execute("""
                UPDATE produtos SET nome = ?, descricao = ?, codigo_barras = ?, preco_compra = ?, preco_venda = ?, quantidade = ?
                WHERE id = ?
            """, (nome, descricao, codigo_barras, float(preco_compra), float(preco_venda), int(quantidade), selected_id))
            self.conn.commit()
            self.load_products()
            self.clear_entries()
        except ValueError:
            messagebox.showerror("Erro", "Preço e quantidade devem ser números!")

    def delete_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione um produto para deletar!")
            return

        selected_id = self.tree.item(selected_item, "values")[0]
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja deletar este produto?"):
            self.cursor.execute("DELETE FROM produtos WHERE id = ?", (selected_id,))
            self.conn.commit()
            self.load_products()
            self.clear_entries()

    def clear_entries(self):
        self.nome_entry.delete(0, tk.END)
        self.descricao_entry.delete(0, tk.END)
        self.codigo_barras_entry.delete(0, tk.END)
        self.preco_compra_entry.delete(0, tk.END)
        self.preco_venda_entry.delete(0, tk.END)
        self.quantidade_entry.delete(0, tk.END)

    def on_product_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        selected_id = self.tree.item(selected_item, "values")[0]
        self.cursor.execute("SELECT * FROM produtos WHERE id = ?", (selected_id,))
        product = self.cursor.fetchone()

        self.clear_entries()
        self.nome_entry.insert(0, product[1])
        self.descricao_entry.insert(0, product[2])
        self.codigo_barras_entry.insert(0, product[3])
        self.preco_compra_entry.insert(0, product[4])
        self.preco_venda_entry.insert(0, product[5])
        self.quantidade_entry.insert(0, product[6])

if __name__ == "__main__":
    app = App()
    app.mainloop()