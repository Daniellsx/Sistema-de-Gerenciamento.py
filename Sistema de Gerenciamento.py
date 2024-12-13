import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Configurações do banco de dados
def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
              id INTEGER PRIMARY KEY,
              title TEXT,
              description TEXT,
              category TEXT,
              priority TEXT,
              completed INTEGER
              )''')
    conn.commit()
    conn.close()

# Funções de manipulação de tarefas
def add_task(title, description, category, priority):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("INSERT INTO tasks (title, description, category, priority, completed) VALUES (?, ?, ?, ?, ?)",
              (title, description, category, priority, 0))  # 0 para não concluído
    conn.commit()
    conn.close()

def get_tasks(completed=False):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE completed = ?", (1 if completed else 0,))
    tasks = c.fetchall()
    conn.close()
    return tasks

def mark_task_completed(task_id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# Geração de relatório em PDF
def generate_pdf_report():
    try:
        # Busca as tarefas concluídas e pendentes
        tasks_completed = get_tasks(completed=True)
        tasks_pending = get_tasks(completed=False)

        # Nome do arquivo PDF
        pdf_file = f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

        # Gera o relatório em PDF
        c = canvas.Canvas(pdf_file, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(50, 750, "Relatório de Tarefas")
        c.drawString(50, 730, f"Tarefas Concluídas: {len(tasks_completed)}")
        c.drawString(50, 710, f"Tarefas Pendentes: {len(tasks_pending)}")

        # Geração do gráfico de pizza
        labels = ['Concluídas', 'Pendentes']
        sizes = [len(tasks_completed), len(tasks_pending)]
        plt.figure(figsize=(5, 5))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')
        chart_path = "task_report_chart.png"
        plt.savefig(chart_path)  # Salva o gráfico como imagem
        plt.close()

        # Adiciona o gráfico ao PDF
        if os.path.exists(chart_path):
            c.drawImage(chart_path, 50, 400, width=500, height=300)  # Ajusta as dimensões do gráfico no PDF

        # Finaliza o PDF
        c.save()

        # Remove o arquivo temporário do gráfico
        if os.path.exists(chart_path):
            os.remove(chart_path)

        # Exibe uma mensagem de sucesso
        messagebox.showinfo("Relatório", f"Relatório gerado com sucesso: {pdf_file}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar o relatório: {e}")

# Interface gráfica aprimorada
class TaskManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerenciador de Tarefas")
        self.geometry("800x600")
        self.configure(bg="white")

        self.current_theme = "light"  # Alternância de tema
        self.create_widgets()

    def create_widgets(self):
        self.configure(bg="white" if self.current_theme == "light" else "black")

        # Título da aplicação
        title_frame = ttk.Frame(self, padding=10)
        title_frame.pack(fill="x")

        title_label = ttk.Label(
            title_frame, 
            text="Gerenciador de Tarefas", 
            font=("Helvetica", 18, "bold"),
            foreground="black" if self.current_theme == "light" else "white"
        )
        title_label.pack(side="left", padx=10)

        theme_button = ttk.Button(title_frame, text="Alternar Tema", command=self.toggle_theme)
        theme_button.pack(side="right", padx=10)

        # Frame principal
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Seção de entrada
        input_frame = ttk.Labelframe(main_frame, text="Nova Tarefa", padding=10)
        input_frame.pack(side="left", fill="y", padx=10, pady=10)

        ttk.Label(input_frame, text="Título:").pack(anchor="w", pady=2)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.pack(pady=2)

        ttk.Label(input_frame, text="Descrição:").pack(anchor="w", pady=2)
        self.desc_entry = ttk.Entry(input_frame, width=30)
        self.desc_entry.pack(pady=2)

        ttk.Label(input_frame, text="Categoria:").pack(anchor="w", pady=2)
        self.cat_combobox = ttk.Combobox(input_frame, values=["Trabalho", "Estudo", "Pessoal"], state="readonly")
        self.cat_combobox.pack(pady=2)

        ttk.Label(input_frame, text="Prioridade:").pack(anchor="w", pady=2)
        self.priority_combobox = ttk.Combobox(input_frame, values=["Alta", "Média", "Baixa"], state="readonly")
        self.priority_combobox.pack(pady=2)

        ttk.Button(input_frame, text="Adicionar Tarefa", command=self.add_task_action).pack(pady=10)
        ttk.Button(input_frame, text="Gerar Relatório em PDF", command=generate_pdf_report).pack(pady=10)

        # Seção de tarefas
        task_frame = ttk.Labelframe(main_frame, text="Tarefas", padding=10)
        task_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.task_list = ttk.Treeview(task_frame, columns=("Title", "Category", "Priority"), show="headings")
        self.task_list.heading("Title", text="Título")
        self.task_list.heading("Category", text="Categoria")
        self.task_list.heading("Priority", text="Prioridade")
        self.task_list.pack(fill="both", expand=True)

        self.populate_task_list()

    def populate_task_list(self):
        for row in self.task_list.get_children():
            self.task_list.delete(row)

        tasks = get_tasks(completed=False)
        for task in tasks:
            self.task_list.insert("", "end", values=(task[1], task[3], task[4]))

    def add_task_action(self):
        title = self.title_entry.get()
        description = self.desc_entry.get()
        category = self.cat_combobox.get()
        priority = self.priority_combobox.get()

        if title and category and priority:
            add_task(title, description, category, priority)
            self.populate_task_list()
        else:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos obrigatórios.")

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.create_widgets()

# Inicialização
if __name__ == "__main__":
    init_db()
    app = TaskManagerApp()
    app.mainloop()
