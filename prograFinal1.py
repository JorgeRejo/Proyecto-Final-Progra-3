import tkinter as tk
from tkinter import filedialog
import re
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt

class DOMViewer(tk.Toplevel):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.title("DOM Mapa Mental")

        self.canvas = tk.Canvas(self)
        self.canvas.pack(side="left", fill="both", expand=True)

    def update_dom_tree(self, soup):
        G = self.create_dom_graph(soup)
        self.draw_dom_graph(G)

    def create_dom_graph(self, soup):
        G = nx.DiGraph()

        def add_node_and_edges(node):
            if node.name:
                G.add_node(node.name)
                for child in node.children:
                    if child.name:
                        G.add_edge(node.name, child.name)
                    add_node_and_edges(child)

        add_node_and_edges(soup)

        return G

    def draw_dom_graph(self, G):
        pos = nx.spring_layout(G, seed=42)  # Posicionamiento del grafo

        plt.figure(figsize=(8, 6))  # Tamaño de la figura
        nx.draw(G, pos, with_labels=True, node_size=2000, font_size=10, node_color="lightblue", edge_color="gray", width=1.0)  # Dibujar el grafo
        plt.axis("off")  # Ocultar los ejes

        plt.tight_layout()  # Ajustar el diseño de la figura
        plt.savefig("dom_graph.png")  # Guardar el gráfico como imagen
        plt.close()

        self.canvas.delete("all")  # Borrar contenido anterior del lienzo
        img = tk.PhotoImage(file="dom_graph.png")  # Cargar la imagen del gráfico
        self.canvas.create_image(0, 0, anchor="nw", image=img)  # Mostrar la imagen en el lienzo
        self.canvas.image = img  # Guardar una referencia para evitar que la imagen sea eliminada por el recolector de basura

class SyntaxHighlightText(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.linenumbers = tk.Text(self, width=4, padx=5, pady=5, takefocus=0, border=0, background="#f0f0f0", state="disabled")
        self.linenumbers.pack(side="left", fill="y")

        self.text_widget = tk.Text(self)
        self.text_widget.pack(side="right", fill="both", expand=True)

        self.text_widget.bind("<KeyRelease>", self.highlight_syntax)
        self.text_widget.bind("<Return>", self.update_linenumbers)
        self.text_widget.bind("<MouseWheel>", self.on_mousewheel)
        self.text_widget.bind("<Configure>", self.on_configure)

        self.tag_configure("open_tag", foreground="blue")
        self.tag_configure("close_tag", foreground="red")
        self.tag_configure("unclosed_tag", underline=True, underlinefg="green")

        self.create_menu()

        self.dom_viewer = None

    def tag_configure(self, tag, **kwargs):
        self.text_widget.tag_configure(tag, **kwargs)

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Abrir", command=self.open_file)
        file_menu.add_command(label="Guardar", command=self.save_file)
        file_menu.add_command(label="Guardar como...", command=self.guardar_como)
        file_menu.add_command(label="Imprimir", command=self.imprimir)
        file_menu.add_command(label="Salir", command=self.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Actualizar", command=self.update_syntax_highlight)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Buscar", command=self.buscar)
        edit_menu.add_command(label="Reemplazar", command=self.reemplazar)
        edit_menu.add_command(label="Ir a...", command=self.ir_a)

    # Función para abrir un archivo
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_widget.delete("1.0", "end")
                self.text_widget.insert("1.0", content)
                self.update_linenumbers()

    # Función para guardar un archivo
    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            content = self.text_widget.get("1.0", "end")
            with open(file_path, "w") as file:
                file.write(content)

    # Función para guardar como un nuevo archivo
    def guardar_como():
        contenido = texto.get("1.0", tk.END)
        ruta_archivo = filedialog.asksaveasfilename(filetypes=[("Archivos HTML", "*.html")])
        if ruta_archivo:
            with open(ruta_archivo, "w") as archivo:
                archivo.write(contenido)
            messagebox.showinfo("Guardado", "El archivo ha sido guardado correctamente.")

    # Función para imprimir
    def imprimir():
        messagebox.showinfo("Imprimir", "Imprimiendo...")

    # Función para buscar una palabra
    def buscar():
        palabra = simpledialog.askstring("Buscar", "Ingrese la palabra a buscar:")
        if palabra:
            contenido = texto.get("1.0", tk.END)
            if palabra in contenido:
                messagebox.showinfo("Resultado de la búsqueda", "La palabra '{}' fue encontrada.".format(palabra))
            else:
                messagebox.showinfo("Resultado de la búsqueda", "La palabra '{}' no fue encontrada.".format(palabra))

    # Función para reemplazar una palabra
    def reemplazar():
        palabra_antigua = simpledialog.askstring("Reemplazar", "Ingrese la palabra a reemplazar:")
        if palabra_antigua:
            palabra_nueva = simpledialog.askstring("Reemplazar", "Ingrese la nueva palabra:")
            if palabra_nueva:
                contenido = texto.get("1.0", tk.END)
                contenido_modificado = contenido.replace(palabra_antigua, palabra_nueva)
                texto.delete("1.0", tk.END)
                texto.insert(tk.END, contenido_modificado)

    # Función para ir a una línea específica
    def ir_a():
        linea = simpledialog.askinteger("Ir a", "Ingrese el número de línea:")
        if linea:
            linea_actual = int(texto.index(tk.INSERT).split(".")[0])
            linea_destino = min(max(1, linea), texto.index(tk.END).split(".")[0])
            if linea_actual != linea_destino:
                texto.mark_set(tk.INSERT, "{}.0".format(linea_destino))
                texto.see(tk.INSERT)
                texto.focus_set()

    def on_mousewheel(self, event):
        self.linenumbers.yview("scroll", -event.delta, "units")
        self.text_widget.yview("scroll", -event.delta, "units")

    def on_configure(self, event=None):
        self.linenumbers.configure(height=self.text_widget.winfo_height())
        self.update_linenumbers()

    def highlight_syntax(self, event):
        self.text_widget.tag_remove("open_tag", "1.0", "end")
        self.text_widget.tag_remove("close_tag", "1.0", "end")
        self.text_widget.tag_remove("unclosed_tag", "1.0", "end")

        html_text = self.text_widget.get("1.0", "end")
        self.highlight_tags(html_text)
        self.highlight_unclosed_tags(html_text)
        self.update_linenumbers()

        # Mostrar el DOM en tiempo real
        self.show_dom_tree()

    def highlight_tags(self, text):
        tag_pattern = r"<\/?(\w+)>"
        tags = re.findall(tag_pattern, text)
        keywords = ["html", "head", "body", "div", "p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "a", "img", "table", "tr", "td", "th", "input", "form", "button", "label", "title"]

        for tag in tags:
            if tag.lower() in keywords:
                start = "1.0"
                while True:
                    start = self.text_widget.search(f"<{tag}>", start, stopindex="end", regexp=True)
                    if not start:
                        break
                    end = f"{start}+{len(tag)+2}c"
                    self.text_widget.tag_add("open_tag", start, end)
                    start = end

            close_tag = f"</{tag}>"
            start = "1.0"
            while True:
                start = self.text_widget.search(close_tag, start, stopindex="end", regexp=True)
                if not start:
                    break
                end = f"{start}+{len(close_tag)}c"
                self.text_widget.tag_add("close_tag", start, end)
                start = end

    def highlight_unclosed_tags(self, text):
        open_tag_pattern = r"<(\w+)>"
        close_tag_pattern = r"<\/(\w+)>"
        open_tags = re.findall(open_tag_pattern, text)
        close_tags = re.findall(close_tag_pattern, text)

        unclosed_tags = list(set(open_tags) - set(close_tags))

        for tag in unclosed_tags:
            start = "1.0"
            while True:
                start = self.text_widget.search(f"<{tag}>", start, stopindex="end", regexp=True)
                if not start:
                    break
                end = f"{start}+{len(tag)+2}c"
                self.text_widget.tag_add("unclosed_tag", start, end)
                start = end

    def update_linenumbers(self, event=None):
        self.linenumbers.configure(state="normal")
        self.linenumbers.delete("1.0", "end")

        line_count = self.text_widget.get("1.0", "end").count("\n")
        line_numbers_text = "\n".join(str(i) for i in range(1, line_count+2))

        self.linenumbers.insert("end", line_numbers_text)
        self.linenumbers.configure(state="disabled")

    def update_syntax_highlight(self):
        html_text = self.text_widget.get("1.0", "end")
        self.highlight_syntax(html_text)

        # Mostrar el DOM actualizado en tiempo real
        self.show_dom_tree()

    def show_dom_tree(self):
        html_text = self.text_widget.get("1.0", "end")
        soup = BeautifulSoup(html_text, "html.parser")

        if not self.dom_viewer:
            self.dom_viewer = DOMViewer(self.master)
        self.dom_viewer.update_dom_tree(soup)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Editor de HTML")

    syntax_highlight_text = SyntaxHighlightText(root)
    syntax_highlight_text.pack(fill="both", expand=True)

    root.mainloop()

























