import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv
import hashlib
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime, timedelta

class BibliotecaDigital:
    def __init__(self):
        # Configurar el adaptador de fechas para SQLite
        def adapt_datetime(val):
            return val.strftime("%Y-%m-%d %H:%M:%S")

        def convert_datetime(val):
            return datetime.strptime(val.decode(), "%Y-%m-%d %H:%M:%S")

        sqlite3.register_adapter(datetime, adapt_datetime)
        sqlite3.register_converter("datetime", convert_datetime)
        
        self.root = tk.Tk()
        self.root.title("Biblioteca Digital")
        self.root.geometry("1200x800")
        
        # Crear las tablas necesarias
        self.inicializar_base_datos()
        
        # Crear variables para los campos
        self.titulo_var = tk.StringVar()
        self.autor_var = tk.StringVar()
        self.isbn_var = tk.StringVar()
        self.categoria_var = tk.StringVar()
        self.cantidad_var = tk.StringVar()
        self.estudiante_var = tk.StringVar()
        self.hora_var = tk.StringVar()
        self.minuto_var = tk.StringVar()
        
        # Configurar la interfaz
        self.configurar_interfaz()
        
        # Iniciar la aplicación
        self.root.mainloop()

    def inicializar_base_datos(self):
        try:
            conn = sqlite3.connect('biblioteca.db')
            c = conn.cursor()
            
            # Eliminar tablas si existen
            c.execute('DROP TABLE IF EXISTS prestamos')
            c.execute('DROP TABLE IF EXISTS libros')
            
            # Crear tabla de libros
            c.execute('''CREATE TABLE libros
                        (id INTEGER PRIMARY KEY,
                         titulo TEXT NOT NULL,
                         autor TEXT NOT NULL,
                         isbn TEXT UNIQUE,
                         categoria TEXT NOT NULL,
                         cantidad INTEGER,
                         disponibles INTEGER)''')
            
            # Crear tabla de préstamos
            c.execute('''CREATE TABLE prestamos
                        (id INTEGER PRIMARY KEY,
                         libro_id INTEGER,
                         estudiante TEXT NOT NULL,
                         fecha_prestamo DATETIME,
                         fecha_devolucion DATETIME,
                         fecha_devolucion_real DATETIME,
                         devuelto BOOLEAN DEFAULT 0,
                         deposito_devuelto BOOLEAN DEFAULT 0,
                         estado_multa TEXT DEFAULT 'PENDIENTE',
                         FOREIGN KEY (libro_id) REFERENCES libros (id))''')
            
            # Insertar algunos libros de ejemplo
            libros_ejemplo = [
                ('Don Quijote de la Mancha', 'Miguel de Cervantes', '9788424112912', 'Literatura', 3, 3),
                ('Cien años de soledad', 'Gabriel García Márquez', '9780307474728', 'Literatura', 2, 2),
                ('El principito', 'Antoine de Saint-Exupéry', '9788498381498', 'Literatura', 4, 4)
            ]
            
            c.executemany('INSERT INTO libros (titulo, autor, isbn, categoria, cantidad, disponibles) VALUES (?, ?, ?, ?, ?, ?)',
                         libros_ejemplo)
            
            conn.commit()
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al inicializar la base de datos: {str(e)}")
        finally:
            if conn:
                conn.close()

    def mostrar_usuario_actual(self):
        frame_usuario = ttk.Frame(self.root)
        frame_usuario.pack(fill='x', padx=10, pady=5)
        
        usuario_texto = f"Usuario actual: {self.usuario}" if self.usuario else "Sesión: Invitado"
        
        ttk.Label(frame_usuario, text=usuario_texto, 
                 style="Title.TLabel").pack(side='left')

    def deshabilitar_funciones_admin(self):
        # Deshabilitar botones de administración en todas las pestañas
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and child['text'] in ['Agregar', 'Actualizar', 'Eliminar']:
                        child['state'] = 'disabled'
        
        # Deshabilitar entradas de texto en el formulario de libros
        for var in [self.titulo_var, self.autor_var, self.isbn_var, self.cantidad_var]:
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Entry) and widget.cget('textvariable') == str(var):
                    widget['state'] = 'disabled'
        
        # Deshabilitar el combobox de categoría
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Combobox) and widget.cget('textvariable') == str(self.categoria_var):
                widget['state'] = 'disabled'

    def crear_base_datos(self):
        try:
            conn = sqlite3.connect('biblioteca.db')
            c = conn.cursor()
            
            # Crear tabla de libros con la estructura correcta
            c.execute('''CREATE TABLE IF NOT EXISTS libros
                        (id INTEGER PRIMARY KEY,
                         titulo TEXT NOT NULL,
                         autor TEXT NOT NULL,
                         isbn TEXT UNIQUE,
                         categoria TEXT NOT NULL,
                         cantidad INTEGER,
                         disponibles INTEGER)''')
            
            # Crear tabla de préstamos
            c.execute('''CREATE TABLE IF NOT EXISTS prestamos
                        (id INTEGER PRIMARY KEY,
                         libro_id INTEGER,
                         estudiante TEXT NOT NULL,
                         fecha_prestamo DATETIME,
                         fecha_devolucion DATETIME,
                         fecha_devolucion_real DATETIME,
                         devuelto BOOLEAN DEFAULT 0,
                         deposito_devuelto BOOLEAN DEFAULT 0,
                         estado_multa TEXT DEFAULT 'PENDIENTE',
                         FOREIGN KEY (libro_id) REFERENCES libros (id))''')
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al crear la base de datos: {str(e)}")
        finally:
            if conn:
                conn.close()

    def crear_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # Menú Archivo
        archivo_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Gestión
        gestion_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Gestión", menu=gestion_menu)
        gestion_menu.add_command(label="Gestionar Estados de Préstamos", 
                               command=self.gestionar_estado_prestamo)
        gestion_menu.add_command(label="Mostrar Inventario", 
                               command=self.mostrar_inventario)
        gestion_menu.add_command(label="Mostrar Estadísticas", 
                               command=self.mostrar_estadisticas)
        
        # Agregar atajo de teclado para la calculadora
        self.root.bind('<Alt-c>', lambda e: self.mostrar_calculadora())

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro que desea cerrar sesión?"):
            self.root.destroy()
            BibliotecaDigital()

    def crear_pestaña_libros(self):
        tab_libros = ttk.Frame(self.notebook)
        self.notebook.add(tab_libros, text='Gestión de Libros')
        
        # Panel izquierdo para el formulario
        panel_izquierdo = ttk.Frame(tab_libros)
        panel_izquierdo.pack(side='left', fill='y', padx=10, pady=5)
        
        # Formulario para agregar libros
        frame_form = ttk.LabelFrame(panel_izquierdo, text="Agregar/Editar Libro", padding=10)
        frame_form.pack(fill='x', pady=5)
        
        ttk.Label(frame_form, text="Título:", style="Title.TLabel").grid(row=0, column=0, padx=5, pady=5)
        self.titulo_var = tk.StringVar()
        ttk.Entry(frame_form, textvariable=self.titulo_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Autor:", style="Title.TLabel").grid(row=1, column=0, padx=5, pady=5)
        self.autor_var = tk.StringVar()
        ttk.Entry(frame_form, textvariable=self.autor_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="ISBN:", style="Title.TLabel").grid(row=2, column=0, padx=5, pady=5)
        self.isbn_var = tk.StringVar()
        ttk.Entry(frame_form, textvariable=self.isbn_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Categoría:", style="Title.TLabel").grid(row=3, column=0, padx=5, pady=5)
        self.categoria_var = tk.StringVar()
        categorias = ['Ficción', 'No Ficción', 'Ciencia', 'Tecnología', 'Historia', 'Arte', 'Literatura']
        ttk.Combobox(frame_form, textvariable=self.categoria_var, values=categorias, width=27).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Cantidad:", style="Title.TLabel").grid(row=4, column=0, padx=5, pady=5)
        self.cantidad_var = tk.StringVar()
        ttk.Entry(frame_form, textvariable=self.cantidad_var, width=30).grid(row=4, column=1, padx=5, pady=5)
        
        # Frame para búsqueda avanzada
        frame_busqueda = ttk.LabelFrame(panel_izquierdo, text="Búsqueda Avanzada", padding=10)
        frame_busqueda.pack(fill='x', pady=5)
        
        ttk.Label(frame_busqueda, text="Filtrar por:").grid(row=0, column=0, padx=5, pady=5)
        self.filtro_var = tk.StringVar(value="titulo")
        ttk.Radiobutton(frame_busqueda, text="Título", variable=self.filtro_var, value="titulo").grid(row=0, column=1)
        ttk.Radiobutton(frame_busqueda, text="Autor", variable=self.filtro_var, value="autor").grid(row=0, column=2)
        ttk.Radiobutton(frame_busqueda, text="ISBN", variable=self.filtro_var, value="isbn").grid(row=0, column=3)
        
        ttk.Label(frame_busqueda, text="Categoría:").grid(row=1, column=0, padx=5, pady=5)
        self.filtro_categoria = tk.StringVar()
        ttk.Combobox(frame_busqueda, textvariable=self.filtro_categoria, values=['Todas'] + categorias, width=20).grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        self.filtro_categoria.set('Todas')
        
        # Botones
        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(frame_botones, text="Agregar", command=self.agregar_libro, 
                  style="Custom.TButton").pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Actualizar", command=self.actualizar_libro, 
                  style="Custom.TButton").pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Eliminar", command=self.eliminar_libro, 
                  style="Custom.TButton").pack(side='left', padx=5)
        
        # Panel derecho para la lista de libros
        panel_derecho = ttk.Frame(tab_libros)
        panel_derecho.pack(side='right', fill='both', expand=True, padx=10, pady=5)
        
        # Lista de libros
        self.tree_libros = ttk.Treeview(panel_derecho, 
                                       columns=('ID', 'Título', 'Autor', 'ISBN', 'Categoría', 'Cantidad', 'Disponibles'),
                                       show='headings', height=20)
        
        self.tree_libros.heading('ID', text='ID')
        self.tree_libros.heading('Título', text='Título')
        self.tree_libros.heading('Autor', text='Autor')
        self.tree_libros.heading('ISBN', text='ISBN')
        self.tree_libros.heading('Categoría', text='Categoría')
        self.tree_libros.heading('Cantidad', text='Cantidad')
        self.tree_libros.heading('Disponibles', text='Disponibles')
        
        self.tree_libros.column('ID', width=50)
        self.tree_libros.column('Título', width=200)
        self.tree_libros.column('Autor', width=150)
        self.tree_libros.column('ISBN', width=100)
        self.tree_libros.column('Categoría', width=100)
        self.tree_libros.column('Cantidad', width=70)
        self.tree_libros.column('Disponibles', width=70)
        
        scrollbar = ttk.Scrollbar(panel_derecho, orient="vertical", command=self.tree_libros.yview)
        self.tree_libros.configure(yscrollcommand=scrollbar.set)
        
        self.tree_libros.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree_libros.bind('<<TreeviewSelect>>', self.seleccionar_libro)
        self.actualizar_lista_libros()

    def crear_pestaña_prestamos(self):
        tab_prestamos = ttk.Frame(self.notebook)
        self.notebook.add(tab_prestamos, text='Préstamos')
        
        # Panel izquierdo
        panel_izquierdo = ttk.Frame(tab_prestamos)
        panel_izquierdo.pack(side='left', fill='y', padx=10, pady=5)
        
        # Formulario para préstamos
        frame_prestamo = ttk.LabelFrame(panel_izquierdo, text="Registrar Préstamo", padding=10)
        frame_prestamo.pack(fill='x', pady=5)
        
        ttk.Label(frame_prestamo, text="Estudiante:", style="Title.TLabel").grid(row=0, column=0, padx=5, pady=5)
        self.estudiante_var = tk.StringVar()
        ttk.Entry(frame_prestamo, textvariable=self.estudiante_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_prestamo, text="Libros:", style="Title.TLabel").grid(row=1, column=0, padx=5, pady=5)
        self.libros_seleccionados = []
        self.lista_libros = tk.Listbox(frame_prestamo, width=40, height=5, selectmode=tk.MULTIPLE)
        self.lista_libros.grid(row=1, column=1, padx=5, pady=5)
        self.actualizar_lista_libros_disponibles()
        
        ttk.Label(frame_prestamo, text="Fecha Devolución:", style="Title.TLabel").grid(row=2, column=0, padx=5, pady=5)
        self.fecha_devolucion = DateEntry(frame_prestamo, width=27, background='darkblue',
                                        foreground='white', borderwidth=2)
        self.fecha_devolucion.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame_prestamo, text="Hora Devolución:", style="Title.TLabel").grid(row=3, column=0, padx=5, pady=5)
        frame_hora = ttk.Frame(frame_prestamo)
        frame_hora.grid(row=3, column=1, padx=5, pady=5)
        
        self.hora_var = tk.StringVar(value="12")
        self.minuto_var = tk.StringVar(value="00")
        
        ttk.Spinbox(frame_hora, from_=0, to=23, width=5, textvariable=self.hora_var).pack(side='left', padx=2)
        ttk.Label(frame_hora, text=":").pack(side='left')
        ttk.Spinbox(frame_hora, from_=0, to=59, width=5, textvariable=self.minuto_var).pack(side='left', padx=2)
        
        ttk.Button(frame_prestamo, text="Registrar Préstamo", 
                  command=self.registrar_prestamo, style="Custom.TButton").grid(row=4, column=0, columnspan=2, pady=10)
        
        # Panel derecho para préstamos activos
        panel_derecho = ttk.Frame(tab_prestamos)
        panel_derecho.pack(side='right', fill='both', expand=True, padx=10, pady=5)
        
        ttk.Label(panel_derecho, text="Préstamos Activos", style="Title.TLabel").pack(pady=5)
        
        # Lista de préstamos
        self.tree_prestamos = ttk.Treeview(panel_derecho, 
                                          columns=('ID', 'Libro', 'Estudiante', 'Fecha Préstamo', 'Fecha Devolución'),
                                          show='headings', height=15)
        
        self.tree_prestamos.heading('ID', text='ID')
        self.tree_prestamos.heading('Libro', text='Libro')
        self.tree_prestamos.heading('Estudiante', text='Estudiante')
        self.tree_prestamos.heading('Fecha Préstamo', text='Fecha Préstamo')
        self.tree_prestamos.heading('Fecha Devolución', text='Fecha Devolución')
        
        self.tree_prestamos.column('ID', width=50)
        self.tree_prestamos.column('Libro', width=200)
        self.tree_prestamos.column('Estudiante', width=150)
        self.tree_prestamos.column('Fecha Préstamo', width=100)
        self.tree_prestamos.column('Fecha Devolución', width=100)
        
        scrollbar = ttk.Scrollbar(panel_derecho, orient="vertical", command=self.tree_prestamos.yview)
        self.tree_prestamos.configure(yscrollcommand=scrollbar.set)
        
        self.tree_prestamos.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        ttk.Button(panel_derecho, text="Registrar Devolución", 
                  command=self.registrar_devolucion, style="Custom.TButton").pack(pady=10)
        
        self.actualizar_lista_prestamos()

    def crear_pestaña_reportes(self):
        tab_reportes = ttk.Frame(self.notebook)
        self.notebook.add(tab_reportes, text='Reportes')
        
        # Frame para los botones de reportes
        frame_botones = ttk.Frame(tab_reportes)
        frame_botones.pack(pady=20)
        
        ttk.Button(frame_botones, text="Libros Prestados", 
                  command=self.mostrar_libros_prestados, style="Custom.TButton").pack(pady=5)
        ttk.Button(frame_botones, text="Libros No Devueltos", 
                  command=self.mostrar_no_devueltos, style="Custom.TButton").pack(pady=5)
        ttk.Button(frame_botones, text="Inventario", 
                  command=self.mostrar_inventario, style="Custom.TButton").pack(pady=5)
        ttk.Button(frame_botones, text="Estadísticas", 
                  command=self.mostrar_estadisticas, style="Custom.TButton").pack(pady=5)

    def agregar_libro(self):
        try:
            titulo = self.titulo_var.get()
            autor = self.autor_var.get()
            isbn = self.isbn_var.get()
            categoria = self.categoria_var.get()
            cantidad = int(self.cantidad_var.get())
            
            if not all([titulo, autor, isbn, categoria, cantidad]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            conn = sqlite3.connect('biblioteca.db')
            c = conn.cursor()
            c.execute("INSERT INTO libros (titulo, autor, isbn, categoria, cantidad, disponibles) VALUES (?, ?, ?, ?, ?, ?)",
                     (titulo, autor, isbn, categoria, cantidad, cantidad))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", "Libro agregado correctamente")
            self.limpiar_campos_libro()
            self.actualizar_lista_libros()
            self.actualizar_lista_libros_disponibles()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "ISBN duplicado")
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número")

    def actualizar_libro(self):
        try:
            seleccion = self.tree_libros.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor, seleccione un libro para actualizar")
                return
            
            libro_id = self.tree_libros.item(seleccion[0])['values'][0]
            titulo = self.titulo_var.get()
            autor = self.autor_var.get()
            isbn = self.isbn_var.get()
            categoria = self.categoria_var.get()
            cantidad = int(self.cantidad_var.get())
            
            if not all([titulo, autor, isbn, categoria, cantidad]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            conn = sqlite3.connect('biblioteca.db')
            c = conn.cursor()
            c.execute("""UPDATE libros 
                        SET titulo = ?, autor = ?, isbn = ?, categoria = ?, cantidad = ?
                        WHERE id = ?""",
                     (titulo, autor, isbn, categoria, cantidad, libro_id))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", "Libro actualizado correctamente")
            self.limpiar_campos_libro()
            self.actualizar_lista_libros()
            self.actualizar_lista_libros_disponibles()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "ISBN duplicado")
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número")

    def eliminar_libro(self):
        seleccion = self.tree_libros.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un libro para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este libro?"):
            libro_id = self.tree_libros.item(seleccion[0])['values'][0]
            
            conn = sqlite3.connect('biblioteca.db')
            c = conn.cursor()
            
            # Verificar si hay préstamos activos
            c.execute("SELECT COUNT(*) FROM prestamos WHERE libro_id = ? AND devuelto = 0", (libro_id,))
            if c.fetchone()[0] > 0:
                messagebox.showerror("Error", "No se puede eliminar un libro con préstamos activos")
                conn.close()
                return
            
            c.execute("DELETE FROM libros WHERE id = ?", (libro_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", "Libro eliminado correctamente")
            self.limpiar_campos_libro()
            self.actualizar_lista_libros()
            self.actualizar_lista_libros_disponibles()

    def registrar_prestamo(self):
        try:
            estudiante = self.estudiante_var.get().strip()
            seleccion = self.lista_libros.curselection()
            
            # Validaciones mejoradas
            if not estudiante:
                messagebox.showerror("Error", "El nombre del estudiante es obligatorio")
                return
            
            if len(estudiante) < 3:
                messagebox.showerror("Error", "El nombre del estudiante debe tener al menos 3 caracteres")
                return
                
            if not seleccion:
                messagebox.showerror("Error", "Debe seleccionar al menos un libro")
                return
            
            if len(seleccion) > 3:
                messagebox.showerror("Error", "No se pueden prestar más de 3 libros al mismo tiempo")
                return
            
            # Obtener fecha y hora de devolución
            fecha_dev = self.fecha_devolucion.get_date()
            hora = int(self.hora_var.get())
            minuto = int(self.minuto_var.get())
            
            # Validar fecha y hora
            fecha_devolucion = datetime.combine(fecha_dev, datetime.min.time().replace(hour=hora, minute=minuto))
            fecha_actual = datetime.now()
            
            if fecha_devolucion <= fecha_actual:
                messagebox.showerror("Error", "La fecha de devolución debe ser posterior a la fecha actual")
                return
            
            if (fecha_devolucion - fecha_actual).days > 30:
                if not messagebox.askyesno("Advertencia", "El período de préstamo es mayor a 30 días. ¿Desea continuar?"):
                    return
            
            conn = sqlite3.connect('biblioteca.db')
            
            # Configurar el adaptador de fechas
            def adapt_datetime(val):
                return val.strftime("%Y-%m-%d %H:%M:%S")

            def convert_datetime(val):
                return datetime.strptime(val.decode(), "%Y-%m-%d %H:%M:%S")

            sqlite3.register_adapter(datetime, adapt_datetime)
            sqlite3.register_converter("datetime", convert_datetime)
            
            c = conn.cursor()
            
            try:
                # Verificar préstamos duplicados
                for idx in seleccion:
                    libro_titulo = self.lista_libros.get(idx).split(" (")[0]
                    c.execute("""
                        SELECT COUNT(*) FROM prestamos p
                        JOIN libros l ON p.libro_id = l.id
                        WHERE l.titulo = ? AND p.estudiante = ? AND p.devuelto = 0
                    """, (libro_titulo, estudiante))
                    if c.fetchone()[0] > 0:
                        messagebox.showerror("Error", f"El estudiante ya tiene prestado el libro: {libro_titulo}")
                        conn.close()
                        return
                
                # Verificar si el estudiante tiene préstamos vencidos
                c.execute("""
                    SELECT COUNT(*) FROM prestamos 
                    WHERE estudiante = ? AND devuelto = 0 
                    AND fecha_devolucion < ?
                """, (estudiante, fecha_actual.strftime("%Y-%m-%d %H:%M:%S")))
                
                if c.fetchone()[0] > 0:
                    messagebox.showerror("Error", 
                                       "El estudiante tiene préstamos vencidos pendientes.\n"
                                       "Debe devolver los libros vencidos antes de realizar un nuevo préstamo.")
                    return
                
                # Verificar si el estudiante ya tiene 3 o más libros prestados
                c.execute("""
                    SELECT COUNT(*) FROM prestamos 
                    WHERE estudiante = ? AND devuelto = 0
                """, (estudiante,))
                
                prestamos_actuales = c.fetchone()[0]
                if prestamos_actuales + len(seleccion) > 3:
                    messagebox.showerror("Error", 
                                       f"El estudiante ya tiene {prestamos_actuales} libros prestados.\n"
                                       "No puede exceder el límite de 3 libros por estudiante.")
                    return
                
                # Confirmar depósito (5$ por libro)
                total_deposito = len(seleccion) * 5
                if not messagebox.askyesno("Depósito", 
                                         f"Se requiere un depósito de ${total_deposito} (${5} por libro).\n"
                                         f"Número de libros: {len(seleccion)}\n"
                                         f"Fecha de devolución: {fecha_devolucion.strftime('%d/%m/%Y %H:%M')}\n"
                                         f"¿El estudiante ha pagado el depósito?"):
                    return
                
                # Registrar cada préstamo
                libros_prestados = []
                libros_no_disponibles = []
                
                for idx in seleccion:
                    libro_titulo = self.lista_libros.get(idx).split(" (")[0]
                    
                    # Verificar disponibilidad
                    c.execute("""
                        SELECT id, disponibles, cantidad 
                        FROM libros 
                        WHERE titulo = ?
                    """, (libro_titulo,))
                    resultado = c.fetchone()
                    
                    if not resultado:
                        libros_no_disponibles.append(f"{libro_titulo} (no encontrado)")
                        continue
                    
                    libro_id, disponibles, cantidad = resultado
                    
                    if disponibles <= 0:
                        libros_no_disponibles.append(f"{libro_titulo} (sin ejemplares)")
                        continue
                    
                    # Registrar el préstamo
                    c.execute("""
                        INSERT INTO prestamos 
                        (libro_id, estudiante, fecha_prestamo, fecha_devolucion, devuelto)
                        VALUES (?, ?, ?, ?, ?)
                    """, (libro_id, estudiante, fecha_actual.strftime("%Y-%m-%d %H:%M:%S"), 
                         fecha_devolucion.strftime("%Y-%m-%d %H:%M:%S"), False))
                    
                    # Actualizar disponibles
                    c.execute("""
                        UPDATE libros 
                        SET disponibles = disponibles - 1 
                        WHERE id = ?
                    """, (libro_id,))
                    
                    # Registrar el depósito en caja de ahorros
                    c.execute("""
                        INSERT INTO caja_ahorros (fecha, monto, descripcion)
                        VALUES (?, 5, ?)
                    """, (fecha_actual.strftime("%Y-%m-%d"), 
                         f"Depósito por préstamo - Libro: {libro_titulo} - Estudiante: {estudiante}"))
                    
                    libros_prestados.append(libro_titulo)
                    
                    # Actualizar estadísticas diarias
                    c.execute("""
                        INSERT INTO estadisticas_diarias (fecha, prestamos_nuevos)
                        VALUES (?, 1)
                        ON CONFLICT(fecha) DO UPDATE SET
                        prestamos_nuevos = prestamos_nuevos + 1
                    """, (fecha_actual.date(),))
                
                if libros_no_disponibles:
                    mensaje_error = "Los siguientes libros no pudieron ser prestados:\n"
                    mensaje_error += "\n".join(libros_no_disponibles)
                    messagebox.showwarning("Advertencia", mensaje_error)
                
                if libros_prestados:
                    mensaje_exito = "Se han registrado los siguientes préstamos:\n"
                    mensaje_exito += "\n".join(f"- {libro}" for libro in libros_prestados)
                    mensaje_exito += f"\n\nFecha de devolución: {fecha_devolucion.strftime('%d/%m/%Y %H:%M')}"
                    messagebox.showinfo("Éxito", mensaje_exito)
                    
                    conn.commit()
                    
                    # Limpiar campos solo si se registró al menos un préstamo
                    self.limpiar_campos_prestamo()
                    self.actualizar_lista_prestamos()
                    self.actualizar_lista_libros()
                    self.actualizar_lista_libros_disponibles()
                else:
                    messagebox.showerror("Error", "No se pudo registrar ningún préstamo")
                    conn.rollback()
                
            except sqlite3.Error as e:
                conn.rollback()
                messagebox.showerror("Error de Base de Datos", f"Error al registrar los préstamos: {str(e)}")
            finally:
                conn.close()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Error en los datos ingresados: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")

    def registrar_devolucion(self):
        try:
            seleccion = self.tree_prestamos.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor, seleccione un préstamo para registrar la devolución")
                return
            
            prestamo_id = self.tree_prestamos.item(seleccion[0])['values'][0]
            
            conn = sqlite3.connect('biblioteca.db')
            c = conn.cursor()
            
            try:
                # Obtener información del préstamo
                c.execute("""
                    SELECT p.libro_id, p.estudiante, p.fecha_devolucion,
                           julianday('now') - julianday(p.fecha_devolucion) as dias_vencido,
                           l.titulo, p.devuelto, p.deposito_devuelto
                    FROM prestamos p
                    JOIN libros l ON p.libro_id = l.id
                    WHERE p.id = ?
                """, (prestamo_id,))
                
                resultado = c.fetchone()
                if not resultado:
                    messagebox.showerror("Error", "No se encontró el préstamo seleccionado")
                    return
                
                libro_id, estudiante, fecha_devolucion, dias_vencido, titulo, devuelto, deposito_devuelto = resultado
                
                if devuelto:
                    messagebox.showerror("Error", "Este libro ya ha sido devuelto")
                    return
                
                fecha_actual = datetime.now()
                
                # Verificar estado del libro
                estado_libro = messagebox.askyesno("Estado del Libro", 
                                                 "¿El libro se encuentra en buen estado?")
                
                if not estado_libro:
                    if messagebox.askyesno("Libro Dañado", 
                                         "El libro está dañado. ¿Desea reportarlo como perdido?"):
                        self.reportar_libro_perdido()
                        return
                
                # Calcular multa si está vencido
                multa = 0
                if dias_vencido > 0:
                    multa = dias_vencido * 1  # $1 por día de retraso
                    mensaje_multa = (
                        f"El libro '{titulo}' tiene {int(dias_vencido)} días de retraso.\n"
                        f"Multa a pagar: ${multa:.2f}\n"
                        f"Estudiante: {estudiante}\n"
                        f"Fecha límite: {fecha_devolucion}"
                    )
                    if not messagebox.askyesno("Multa por Retraso", 
                                             f"{mensaje_multa}\n\n¿El estudiante ha pagado la multa?"):
                        return
                    
                    # Registrar la multa en caja de ahorros
                    c.execute("""
                        INSERT INTO caja_ahorros (fecha, monto, descripcion)
                        VALUES (date('now'), ?, ?)
                    """, (multa, f"Multa por retraso - Libro: {titulo} - Estudiante: {estudiante} - Días: {int(dias_vencido)}"))
                    
                    # Actualizar estado de la multa
                    c.execute("""
                        UPDATE prestamos 
                        SET estado_multa = 'PAGADO'
                        WHERE id = ?
                    """, (prestamo_id,))
                
                # Actualizar el préstamo
                c.execute("""
                    UPDATE prestamos 
                    SET devuelto = 1, 
                        deposito_devuelto = ?,
                        fecha_devolucion_real = ?
                    WHERE id = ?
                """, (1 if dias_vencido <= 0 else 0, fecha_actual, prestamo_id))
                
                # Actualizar disponibles
                c.execute("""
                    UPDATE libros 
                    SET disponibles = disponibles + 1 
                    WHERE id = ?
                """, (libro_id,))
                
                # Si no está vencido, devolver el depósito
                if dias_vencido <= 0:
                    c.execute("""
                        INSERT INTO caja_ahorros (fecha, monto, descripcion)
                        VALUES (date('now'), -5, ?)
                    """, (f"Devolución de depósito - Libro: {titulo} - Estudiante: {estudiante}",))
                
                # Actualizar estadísticas diarias
                c.execute("""
                    INSERT INTO estadisticas_diarias (fecha, devoluciones)
                    VALUES (?, 1)
                    ON CONFLICT(fecha) DO UPDATE SET
                    devoluciones = devoluciones + 1
                """, (fecha_actual.date(),))
                
                conn.commit()
                
                mensaje = f"Devolución registrada correctamente\nLibro: {titulo}\nEstudiante: {estudiante}"
                if multa > 0:
                    mensaje += f"\nMulta pagada: ${multa:.2f}"
                if dias_vencido <= 0:
                    mensaje += "\nSe ha devuelto el depósito de $5"
                else:
                    mensaje += "\nNo se devuelve el depósito por devolución tardía"
                
                messagebox.showinfo("Éxito", mensaje)
                
                self.actualizar_lista_prestamos()
                self.actualizar_lista_libros()
                self.actualizar_lista_libros_disponibles()
                
            except sqlite3.Error as e:
                conn.rollback()
                messagebox.showerror("Error de Base de Datos", f"Error al registrar la devolución: {str(e)}")
            finally:
                conn.close()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")

    def reportar_libro_perdido(self):
        seleccion = self.tree_prestamos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un préstamo para reportar pérdida")
            return
        
        if not messagebox.askyesno("Confirmar", "¿Está seguro de reportar este libro como perdido?\nEl depósito de $5 se agregará a la caja de ahorros."):
            return
        
        prestamo_id = self.tree_prestamos.item(seleccion[0])['values'][0]
        
        conn = sqlite3.connect('biblioteca.db')
        c = conn.cursor()
        
        # Obtener información del préstamo
        c.execute("""SELECT libro_id, estudiante FROM prestamos WHERE id = ?""", (prestamo_id,))
        libro_id, estudiante = c.fetchone()
        
        # Registrar libro perdido
        c.execute("""INSERT INTO libros_perdidos (libro_id, estudiante, fecha_perdida)
                    VALUES (?, ?, date('now'))""",
                 (libro_id, estudiante))
        
        # Agregar depósito a caja de ahorros
        c.execute("""INSERT INTO caja_ahorros (fecha, monto, descripcion)
                    VALUES (date('now'), 5, ?)""",
                 (f"Depósito retenido por libro perdido - Estudiante: {estudiante}",))
        
        # Actualizar préstamo
        c.execute("UPDATE prestamos SET devuelto = 1, deposito_devuelto = 0 WHERE id = ?", (prestamo_id,))
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Éxito", "Libro marcado como perdido\nEl depósito se ha agregado a la caja de ahorros")
        self.actualizar_lista_prestamos()
        self.actualizar_lista_libros()

    def actualizar_lista_libros(self):
        try:
            # Limpiar la lista actual
            for item in self.tree_libros.get_children():
                self.tree_libros.delete(item)
            
            conn = sqlite3.connect('biblioteca.db')
            c = conn.cursor()
            
            # Consulta actualizada para obtener los libros con la cantidad de préstamos activos
            c.execute("""
                SELECT l.id, l.titulo, l.autor, l.isbn, l.categoria, 
                       l.cantidad, l.disponibles,
                       COUNT(CASE WHEN p.devuelto = 0 THEN 1 END) as prestados
                FROM libros l
                LEFT JOIN prestamos p ON l.id = p.libro_id
                GROUP BY l.id, l.titulo, l.autor, l.isbn, l.categoria, l.cantidad, l.disponibles
                ORDER BY l.titulo
            """)
            
            # Insertar los datos en el treeview
            for row in c.fetchall():
                self.tree_libros.insert("", "end", values=row)
            
            conn.close()
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al actualizar la lista de libros: {str(e)}")

    def actualizar_lista_prestamos(self):
        for item in self.tree_prestamos.get_children():
            self.tree_prestamos.delete(item)
        
        conn = sqlite3.connect('biblioteca.db')
        c = conn.cursor()
        c.execute("""SELECT p.id, l.titulo, p.estudiante, p.fecha_prestamo, p.fecha_devolucion
                    FROM prestamos p
                    JOIN libros l ON p.libro_id = l.id
                    WHERE p.devuelto = 0
                    ORDER BY p.fecha_prestamo DESC""")
        
        for prestamo in c.fetchall():
            self.tree_prestamos.insert("", "end", values=prestamo)
        
        conn.close()

    def seleccionar_libro(self, event):
        seleccion = self.tree_libros.selection()
        if seleccion:
            libro = self.tree_libros.item(seleccion[0])['values']
            self.titulo_var.set(libro[1])
            self.autor_var.set(libro[2])
            self.isbn_var.set(libro[3])
            self.categoria_var.set(libro[4])
            self.cantidad_var.set(libro[5])

    def buscar_libros(self, *args):
        busqueda = self.busqueda_var.get().lower()
        categoria = self.filtro_categoria.get()
        campo = self.filtro_var.get()
        
        for item in self.tree_libros.get_children():
            self.tree_libros.delete(item)
        
        conn = sqlite3.connect('biblioteca.db')
        c = conn.cursor()
        
        if categoria == 'Todas':
            c.execute(f"""SELECT * FROM libros 
                        WHERE lower({campo}) LIKE ?
                        ORDER BY titulo""",
                     ('%' + busqueda + '%',))
        else:
            c.execute(f"""SELECT * FROM libros 
                        WHERE lower({campo}) LIKE ? AND categoria = ?
                        ORDER BY titulo""",
                     ('%' + busqueda + '%', categoria))
        
        for libro in c.fetchall():
            self.tree_libros.insert("", "end", values=libro)
        
        conn.close()

    def mostrar_inventario(self):
        # Crear una nueva ventana para el inventario
        inventario_window = tk.Toplevel(self.root)
        inventario_window.title("Inventario de Libros")
        inventario_window.geometry("1200x800")
        
        # Frame superior para filtros
        frame_filtros = ttk.LabelFrame(inventario_window, text="Filtros", padding=10)
        frame_filtros.pack(fill='x', padx=10, pady=5)
        
        # Filtro por categoría
        ttk.Label(frame_filtros, text="Categoría:").pack(side='left', padx=5)
        categoria_var = tk.StringVar(value='Todas')
        categorias = ['Todas', 'Ficción', 'No Ficción', 'Ciencia', 'Tecnología', 'Historia', 'Arte', 'Literatura']
        ttk.Combobox(frame_filtros, textvariable=categoria_var, values=categorias, width=15).pack(side='left', padx=5)
        
        # Filtro por estado
        ttk.Label(frame_filtros, text="Estado:").pack(side='left', padx=5)
        estado_var = tk.StringVar(value='Todos')
        estados = ['Todos', 'Disponibles', 'Prestados', 'Agotados']
        ttk.Combobox(frame_filtros, textvariable=estado_var, values=estados, width=15).pack(side='left', padx=5)
        
        # Frame para gráficos y resumen
        frame_superior = ttk.Frame(inventario_window)
        frame_superior.pack(fill='x', padx=10, pady=5)
        
        # Frame para gráficos
        frame_graficos = ttk.LabelFrame(frame_superior, text="Estadísticas", padding=10)
        frame_graficos.pack(side='left', fill='both', expand=True)
        
        # Crear figura con subplots
        fig = plt.Figure(figsize=(8, 4))
        canvas = FigureCanvasTkAgg(fig, master=frame_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=5)
        
        # Frame para resumen
        frame_resumen = ttk.LabelFrame(frame_superior, text="Resumen", padding=10)
        frame_resumen.pack(side='right', fill='y')
        
        # Crear el Treeview
        tree = ttk.Treeview(inventario_window, 
                           columns=('ID', 'Título', 'Autor', 'ISBN', 'Categoría', 'Total', 'Disponibles', 'Prestados', 'Estado'),
                           show='headings')
        
        # Configurar las columnas
        tree.heading('ID', text='ID')
        tree.heading('Título', text='Título')
        tree.heading('Autor', text='Autor')
        tree.heading('ISBN', text='ISBN')
        tree.heading('Categoría', text='Categoría')
        tree.heading('Total', text='Total')
        tree.heading('Disponibles', text='Disponibles')
        tree.heading('Prestados', text='Prestados')
        tree.heading('Estado', text='Estado')
        
        tree.column('ID', width=50)
        tree.column('Título', width=200)
        tree.column('Autor', width=150)
        tree.column('ISBN', width=100)
        tree.column('Categoría', width=100)
        tree.column('Total', width=70)
        tree.column('Disponibles', width=100)
        tree.column('Prestados', width=100)
        tree.column('Estado', width=100)
        
        def actualizar_lista():
            try:
                conn = sqlite3.connect('biblioteca.db')
                c = conn.cursor()
                
                for item in tree.get_children():
                    tree.delete(item)
                
                categoria = categoria_var.get()
                estado = estado_var.get()
                
                query = """
                    SELECT l.id, l.titulo, l.autor, l.isbn, l.categoria, l.cantidad, l.disponibles,
                           (l.cantidad - l.disponibles) as prestados,
                           CASE 
                               WHEN l.disponibles = 0 THEN 'Agotado'
                               WHEN l.disponibles = l.cantidad THEN 'Disponible'
                               ELSE 'Parcialmente Prestado'
                           END as estado
                    FROM libros l
                    WHERE 1=1
                """
                
                params = []
                if categoria != 'Todas':
                    query += " AND l.categoria = ?"
                    params.append(categoria)
                
                if estado != 'Todos':
                    if estado == 'Disponibles':
                        query += " AND l.disponibles = l.cantidad"
                    elif estado == 'Prestados':
                        query += " AND l.disponibles < l.cantidad"
                    elif estado == 'Agotados':
                        query += " AND l.disponibles = 0"
                
                query += " ORDER BY l.titulo"
                
                c.execute(query, params)
                for row in c.fetchall():
                    tree.insert("", "end", values=row)
                    
                # Actualizar estadísticas
                c.execute("SELECT categoria, COUNT(*) FROM libros GROUP BY categoria")
                categorias_data = c.fetchall()
                
                # Actualizar gráficas
                fig.clear()
                
                # Gráfica de pastel para categorías
                ax1 = fig.add_subplot(121)
                categorias = [x[0] for x in categorias_data]
                valores = [x[1] for x in categorias_data]
                ax1.pie(valores, labels=categorias, autopct='%1.1f%%')
                ax1.set_title('Distribución por Categorías')
                
                # Gráfica de barras para disponibilidad
                ax2 = fig.add_subplot(122)
                c.execute("""
                    SELECT 'Disponibles' as estado, SUM(disponibles) as cantidad FROM libros
                    UNION ALL
                    SELECT 'Prestados', SUM(cantidad - disponibles) FROM libros
                """)
                disponibilidad_data = c.fetchall()
                estados = [x[0] for x in disponibilidad_data]
                cantidades = [x[1] for x in disponibilidad_data]
                ax2.bar(estados, cantidades)
                ax2.set_title('Estado de Libros')
                
                canvas.draw()
                
                # Actualizar resumen
                c.execute("""
                    SELECT 
                        COUNT(DISTINCT titulo) as total_titulos,
                        SUM(cantidad) as total_ejemplares,
                        SUM(disponibles) as total_disponibles,
                        SUM(cantidad - disponibles) as total_prestados,
                        COUNT(CASE WHEN disponibles = 0 THEN 1 END) as agotados
                    FROM libros
                """)
                stats = c.fetchone()
                
                for widget in frame_resumen.winfo_children():
                    widget.destroy()
                
                ttk.Label(frame_resumen, text=f"Total de Títulos: {stats[0]}", style="Title.TLabel").pack(anchor='w', pady=2)
                ttk.Label(frame_resumen, text=f"Total de Ejemplares: {stats[1]}", style="Title.TLabel").pack(anchor='w', pady=2)
                ttk.Label(frame_resumen, text=f"Libros Disponibles: {stats[2]}", style="Title.TLabel").pack(anchor='w', pady=2)
                ttk.Label(frame_resumen, text=f"Libros Prestados: {stats[3]}", style="Title.TLabel").pack(anchor='w', pady=2)
                ttk.Label(frame_resumen, text=f"Títulos Agotados: {stats[4]}", style="Title.TLabel").pack(anchor='w', pady=2)
                
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al actualizar la lista: {str(e)}")
            finally:
                if 'conn' in locals():
                    conn.close()
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(inventario_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        scrollbar.pack(side='right', fill='y')
        
        # Frame para botones
        frame_botones = ttk.Frame(inventario_window)
        frame_botones.pack(fill='x', padx=10, pady=5)
        
        def exportar_detallado():
            try:
                conn = sqlite3.connect('biblioteca.db')
                c = conn.cursor()
                
                with open('inventario_detallado.csv', 'w', encoding='utf-8-sig', newline='') as f:
                    # Escribir encabezado con estadísticas generales
                    c.execute("""
                        SELECT 
                            COUNT(DISTINCT titulo) as total_titulos,
                            SUM(cantidad) as total_ejemplares,
                            SUM(disponibles) as total_disponibles,
                            SUM(cantidad - disponibles) as total_prestados,
                            COUNT(CASE WHEN disponibles = 0 THEN 1 END) as agotados
                        FROM libros
                    """)
                    stats = c.fetchone()
                    
                    f.write("RESUMEN DEL INVENTARIO\n")
                    f.write(f"Total de Títulos,{stats[0]}\n")
                    f.write(f"Total de Ejemplares,{stats[1]}\n")
                    f.write(f"Libros Disponibles,{stats[2]}\n")
                    f.write(f"Libros Prestados,{stats[3]}\n")
                    f.write(f"Títulos Agotados,{stats[4]}\n\n")
                    
                    # Escribir distribución por categorías
                    c.execute("SELECT categoria, COUNT(*) FROM libros GROUP BY categoria")
                    categorias_data = c.fetchall()
                    
                    f.write("DISTRIBUCIÓN POR CATEGORÍAS\n")
                    for cat, val in categorias_data:
                        f.write(f"{cat},{val}\n")
                    f.write("\n")
                    
                    # Escribir inventario detallado
                    f.write("INVENTARIO DETALLADO\n")
                    f.write("ID,Título,Autor,ISBN,Categoría,Total,Disponibles,Prestados,Estado\n")
                    for item in tree.get_children():
                        valores = tree.item(item)['values']
                        valores = [str(v).replace('"', '""') for v in valores]
                        f.write(f'"{",".join(map(str, valores))}"\n')
                
                messagebox.showinfo("Éxito", "Inventario exportado a 'inventario_detallado.csv'")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")
            finally:
                if 'conn' in locals():
                    conn.close()
        
        ttk.Button(frame_botones, text="Actualizar", 
                  command=actualizar_lista).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Exportar Detallado", 
                  command=exportar_detallado).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Cerrar", 
                  command=inventario_window.destroy).pack(side='right', padx=5)
        
        # Vincular cambios en filtros
        categoria_var.trace('w', lambda *args: actualizar_lista())
        estado_var.trace('w', lambda *args: actualizar_lista())
        
        # Mostrar datos iniciales
        actualizar_lista()

    def mostrar_estadisticas(self):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estadísticas del Inventario")
        stats_window.geometry("1000x800")
        
        notebook = ttk.Notebook(stats_window)
        notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Pestaña de Resumen General con Gráficas
        tab_resumen = ttk.Frame(notebook)
        notebook.add(tab_resumen, text='Resumen General')
        
        conn = sqlite3.connect('biblioteca.db')
        c = conn.cursor()
        
        # Crear figura para las gráficas
        fig = plt.Figure(figsize=(12, 6))
        canvas = FigureCanvasTkAgg(fig, master=tab_resumen)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)
        
        # Frame para estadísticas numéricas
        info_frame = ttk.Frame(tab_resumen)
        info_frame.pack(pady=10)
        
        # Botón de actualización
        ttk.Button(tab_resumen, text="Actualizar Estadísticas",
                  command=lambda: self.actualizar_estadisticas(tab_resumen, info_frame, canvas, c)).pack(pady=5)
        
        # Mostrar estadísticas iniciales
        self.actualizar_estadisticas(tab_resumen, info_frame, canvas, c)
        
        # Pestaña de Libros Vencidos
        tab_vencidos = ttk.Frame(notebook)
        notebook.add(tab_vencidos, text='Libros Vencidos')
        
        ttk.Label(tab_vencidos, text="Libros con Fecha Vencida", style="Title.TLabel").pack(pady=10)
        
        # Lista de libros vencidos
        tree_vencidos = ttk.Treeview(tab_vencidos, 
                                    columns=('ID', 'Libro', 'Estudiante', 'Fecha Préstamo', 'Fecha Límite', 'Días Vencido', 'Estado'),
                                    show='headings')
        
        tree_vencidos.heading('ID', text='ID')
        tree_vencidos.heading('Libro', text='Libro')
        tree_vencidos.heading('Estudiante', text='Estudiante')
        tree_vencidos.heading('Fecha Préstamo', text='Fecha Préstamo')
        tree_vencidos.heading('Fecha Límite', text='Fecha Límite')
        tree_vencidos.heading('Días Vencido', text='Días Vencido')
        tree_vencidos.heading('Estado', text='Estado')
        
        tree_vencidos.column('ID', width=50)
        tree_vencidos.column('Libro', width=200)
        tree_vencidos.column('Estudiante', width=150)
        tree_vencidos.column('Fecha Préstamo', width=100)
        tree_vencidos.column('Fecha Límite', width=100)
        tree_vencidos.column('Días Vencido', width=100)
        tree_vencidos.column('Estado', width=100)
        
        frame_botones = ttk.Frame(tab_vencidos)
        frame_botones.pack(pady=10)
        
        ttk.Button(frame_botones, text="Marcar como Pagado", 
                  command=lambda: self.marcar_como_pagado(tree_vencidos, c)).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Marcar como Devuelto", 
                  command=lambda: self.marcar_como_devuelto(tree_vencidos, c)).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Actualizar Lista", 
                  command=lambda: self.actualizar_lista_vencidos(tree_vencidos, c)).pack(side='left', padx=5)
        
        scrollbar = ttk.Scrollbar(tab_vencidos, orient="vertical", command=tree_vencidos.yview)
        tree_vencidos.configure(yscrollcommand=scrollbar.set)
        
        tree_vencidos.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        scrollbar.pack(side='right', fill='y')
        
        # Mostrar datos iniciales de libros vencidos
        self.actualizar_lista_vencidos(tree_vencidos, c)
        
        def on_closing():
            conn.close()
            stats_window.destroy()
        
        stats_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Botón para cerrar
        ttk.Button(stats_window, text="Cerrar", 
                  command=on_closing).pack(pady=10)

    def limpiar_campos_libro(self):
        self.titulo_var.set("")
        self.autor_var.set("")
        self.isbn_var.set("")
        self.categoria_var.set("")
        self.cantidad_var.set("")

    def limpiar_campos_prestamo(self):
        self.estudiante_var.set("")
        self.lista_libros.selection_clear(0, tk.END)
        self.fecha_devolucion.set_date(datetime.now().date())
        self.hora_var.set("12")
        self.minuto_var.set("00")

    def mostrar_acerca_de(self):
        messagebox.showinfo("Acerca de BDI",
                          "Biblioteca Digital Inteligente (BDI)\n\n"
                          "Un sistema de gestión de biblioteca escolar\n"
                          "que ayuda a prevenir la pérdida de libros y\n"
                          "optimizar los recursos educativos.\n\n"
                          "Versión 2.0")

    def mostrar_libros_prestados(self):
        self.mostrar_reporte("SELECT l.titulo, p.estudiante, p.fecha_prestamo, p.fecha_devolucion "
                           "FROM prestamos p JOIN libros l ON p.libro_id = l.id "
                           "WHERE p.devuelto = 0")

    def mostrar_no_devueltos(self):
        self.mostrar_reporte("SELECT l.titulo, p.estudiante, p.fecha_prestamo, p.fecha_devolucion "
                           "FROM prestamos p JOIN libros l ON p.libro_id = l.id "
                           "WHERE p.devuelto = 0 AND p.fecha_devolucion < date('now')")

    def mostrar_reporte(self, query):
        # Crear una nueva ventana para el reporte
        reporte_window = tk.Toplevel(self.root)
        reporte_window.title("Reporte")
        reporte_window.geometry("600x400")
        
        # Crear un Treeview para mostrar los datos
        tree = ttk.Treeview(reporte_window)
        tree.pack(fill='both', expand=True)
        
        # Configurar las columnas según la consulta
        conn = sqlite3.connect('biblioteca.db')
        c = conn.cursor()
        c.execute(query)
        
        # Configurar las columnas basadas en los nombres de las columnas de la consulta
        columnas = [description[0] for description in c.description]
        tree["columns"] = columnas
        tree["show"] = "headings"
        
        for col in columnas:
            tree.heading(col, text=col.title())
            tree.column(col, width=100)
        
        # Insertar los datos
        datos = c.fetchall()
        if datos:
            for row in datos:
                tree.insert("", "end", values=row)
        else:
            # Insertar una fila que indique que no hay datos
            valores_vacios = ["Vacío"] * len(columnas)
            tree.insert("", "end", values=valores_vacios)
        
        conn.close()

    def verificar_prestamos_vencidos(self):
        try:
            conn = sqlite3.connect('biblioteca.db')
            
            # Configurar el adaptador de fechas
            def adapt_datetime(val):
                return val.strftime("%Y-%m-%d %H:%M:%S")

            def convert_datetime(val):
                return datetime.strptime(val.decode(), "%Y-%m-%d %H:%M:%S")

            sqlite3.register_adapter(datetime, adapt_datetime)
            sqlite3.register_converter("datetime", convert_datetime)
            
            c = conn.cursor()
            fecha_actual = datetime.now()
            
            # Buscar préstamos vencidos sin notificación
            c.execute("""
                SELECT p.id, l.titulo, p.estudiante, p.fecha_devolucion,
                       julianday(?) - julianday(p.fecha_devolucion) as dias_vencido
                FROM prestamos p
                JOIN libros l ON p.libro_id = l.id
                WHERE p.devuelto = 0 
                AND p.fecha_devolucion < ?
                AND NOT EXISTS (
                    SELECT 1 FROM notificaciones n 
                    WHERE n.prestamo_id = p.id
                )
            """, (fecha_actual.strftime("%Y-%m-%d %H:%M:%S"), 
                  fecha_actual.strftime("%Y-%m-%d %H:%M:%S")))
            
            prestamos_vencidos = c.fetchall()
            
            for prestamo in prestamos_vencidos:
                prestamo_id, titulo, estudiante, fecha_devolucion, dias_vencido = prestamo
                mensaje = (
                    f"El libro '{titulo}' prestado a {estudiante}\n"
                    f"está vencido desde {fecha_devolucion}\n"
                    f"Días de retraso: {int(dias_vencido)}"
                )
                
                # Crear notificación
                c.execute("""
                    INSERT INTO notificaciones (prestamo_id, mensaje, fecha, leida)
                    VALUES (?, ?, ?, 0)
                """, (prestamo_id, mensaje, fecha_actual.strftime("%Y-%m-%d %H:%M:%S")))
                
                # Mostrar notificación
                messagebox.showwarning("Préstamo Vencido", mensaje)
            
            conn.commit()
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al verificar préstamos vencidos: {str(e)}")
        finally:
            if conn:
                conn.close()

    def mostrar_calculadora(self):
        calc = tk.Toplevel(self.root)
        calc.title("Calculadora")
        calc.geometry("300x400")
        
        # Display
        display_var = tk.StringVar()
        display = ttk.Entry(calc, textvariable=display_var, justify='right', font=('Arial', 20))
        display.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky='nsew')
        
        # Botones
        botones = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]
        
        def click_boton(key):
            if key == '=':
                try:
                    resultado = eval(display_var.get())
                    display_var.set(resultado)
                except:
                    display_var.set('Error')
            else:
                display_var.set(display_var.get() + key)
        
        row = 1
        col = 0
        for boton in botones:
            cmd = lambda x=boton: click_boton(x)
            ttk.Button(calc, text=boton, command=cmd).grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        # Botón Clear
        ttk.Button(calc, text='C', command=lambda: display_var.set('')).grid(row=row, column=0, columnspan=4, pady=5)
        
        # Atajo de teclado para cerrar (Esc)
        calc.bind('<Escape>', lambda e: calc.destroy())

    def ver_caja_ahorros(self):
        # Crear ventana
        ventana = tk.Toplevel(self.root)
        ventana.title("Caja de Ahorros")
        ventana.geometry("600x400")
        
        # Frame superior para el total
        frame_total = ttk.Frame(ventana, padding=10)
        frame_total.pack(fill='x')
        
        conn = sqlite3.connect('biblioteca.db')
        c = conn.cursor()
        
        # Obtener total
        c.execute("SELECT SUM(monto) FROM caja_ahorros")
        total = c.fetchone()[0] or 0
        
        ttk.Label(frame_total, text=f"Total en Caja: ${total:.2f}", 
                 style="Title.TLabel").pack()
        
        # Lista de movimientos
        frame_lista = ttk.Frame(ventana)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=5)
        
        tree = ttk.Treeview(frame_lista, columns=('Fecha', 'Monto', 'Descripción'),
                           show='headings')
        
        tree.heading('Fecha', text='Fecha')
        tree.heading('Monto', text='Monto')
        tree.heading('Descripción', text='Descripción')
        
        tree.column('Fecha', width=100)
        tree.column('Monto', width=100)
        tree.column('Descripción', width=350)
        
        # Obtener movimientos
        c.execute("SELECT fecha, monto, descripcion FROM caja_ahorros ORDER BY fecha DESC")
        for row in c.fetchall():
            tree.insert('', 'end', values=row)
        
        conn.close()
        
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def guardar_libros(self):
        try:
            conn = sqlite3.connect('biblioteca.db')
            c = conn.cursor()
            
            # Obtener todos los libros
            c.execute("SELECT * FROM libros")
            libros = c.fetchall()
            
            # Convertir a lista de diccionarios
            libros_data = []
            for libro in libros:
                libros_data.append({
                    'id': libro[0],
                    'titulo': libro[1],
                    'autor': libro[2],
                    'isbn': libro[3],
                    'categoria': libro[4],
                    'cantidad': libro[5],
                    'disponibles': libro[6]
                })
            
            # Guardar en archivo JSON
            with open('libros_backup.json', 'w', encoding='utf-8') as f:
                json.dump(libros_data, f, ensure_ascii=False, indent=4)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar los libros: {str(e)}")

    def cargar_libros(self):
        try:
            # Verificar si existe el archivo de respaldo
            if not os.path.exists('libros_backup.json'):
                return
            
            with open('libros_backup.json', 'r', encoding='utf-8') as f:
                libros_data = json.load(f)
            
            conn = sqlite3.connect('biblioteca.db')
            c = conn.cursor()
            
            # Insertar los libros en la base de datos
            for libro in libros_data:
                try:
                    c.execute("""INSERT INTO libros 
                                (id, titulo, autor, isbn, categoria, cantidad, disponibles)
                                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                             (libro['id'], libro['titulo'], libro['autor'], 
                              libro['isbn'], libro['categoria'], 
                              libro['cantidad'], libro['disponibles']))
                except sqlite3.IntegrityError:
                    # Si el libro ya existe, actualizar sus datos
                    c.execute("""UPDATE libros 
                                SET titulo = ?, autor = ?, categoria = ?,
                                    cantidad = ?, disponibles = ?
                                WHERE isbn = ?""",
                             (libro['titulo'], libro['autor'], libro['categoria'],
                              libro['cantidad'], libro['disponibles'], libro['isbn']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los libros: {str(e)}")

    def cerrar_aplicacion(self):
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea cerrar la aplicación?"):
            self.guardar_libros()
            self.root.destroy()

    def actualizar_lista_libros_disponibles(self):
        self.lista_libros.delete(0, tk.END)
        conn = sqlite3.connect('biblioteca.db')
        c = conn.cursor()
        
        try:
            c.execute("""
                SELECT l.titulo, l.disponibles 
                FROM libros l 
                WHERE l.disponibles > 0 
                ORDER BY l.titulo
            """)
            
            for libro in c.fetchall():
                self.lista_libros.insert(tk.END, f"{libro[0]} ({libro[1]} disponibles)")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al actualizar la lista de libros disponibles: {str(e)}")
        finally:
            conn.close()

    def actualizar_lista_vencidos(self, tree_vencidos, c):
        for item in tree_vencidos.get_children():
            tree_vencidos.delete(item)
        
        c.execute("""
            SELECT p.id, l.titulo, p.estudiante, p.fecha_prestamo, p.fecha_devolucion,
                   julianday('now') - julianday(p.fecha_devolucion) as dias_vencido,
                   COALESCE(p.estado_multa, 'PENDIENTE') as estado
            FROM prestamos p
            JOIN libros l ON p.libro_id = l.id
            WHERE p.devuelto = 0 AND p.fecha_devolucion < datetime('now')
            ORDER BY dias_vencido DESC
        """)
        
        for row in c.fetchall():
            tree_vencidos.insert("", "end", values=row)

    def actualizar_estadisticas(self, tab_resumen, info_frame, canvas, c):
        # Limpiar frame de información
        for widget in info_frame.winfo_children():
            widget.destroy()
        
        # Actualizar datos estadísticos
        c.execute("""
            SELECT 
                'Prestados' as estado, COUNT(*) as cantidad
            FROM prestamos 
            WHERE devuelto = 0
            UNION ALL
            SELECT 
                'Devueltos', COUNT(*)
            FROM prestamos 
            WHERE devuelto = 1
            UNION ALL
            SELECT 
                'Vencidos', COUNT(*)
            FROM prestamos 
            WHERE devuelto = 0 AND fecha_devolucion < datetime('now')
        """)
        estado_libros = c.fetchall()
        
        c.execute("""
            SELECT strftime('%Y-%m', fecha_prestamo) as mes, COUNT(*) 
            FROM prestamos 
            GROUP BY mes 
            ORDER BY mes DESC 
            LIMIT 6
        """)
        prestamos_mensuales = c.fetchall()
        
        # Actualizar gráficas
        fig = canvas.figure
        fig.clear()
        
        # Gráfica de barras para estado de libros
        ax1 = fig.add_subplot(121)
        estados = [x[0] for x in estado_libros]
        cantidades = [x[1] for x in estado_libros]
        ax1.bar(estados, cantidades)
        ax1.set_title('Estado de Préstamos')
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Gráfica de barras para préstamos mensuales
        ax2 = fig.add_subplot(122)
        meses = [x[0] for x in prestamos_mensuales]
        cantidades = [x[1] for x in prestamos_mensuales]
        ax2.bar(meses, cantidades)
        ax2.set_title('Préstamos Mensuales')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        canvas.draw()
        
        # Actualizar estadísticas numéricas
        c.execute("SELECT COUNT(*) FROM libros")
        total_libros = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM prestamos WHERE devuelto = 0")
        prestamos_activos = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM prestamos WHERE devuelto = 1")
        libros_devueltos = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM prestamos WHERE devuelto = 0 AND fecha_devolucion < datetime('now')")
        libros_vencidos = c.fetchone()[0]
        
        c.execute("SELECT SUM(monto) FROM caja_ahorros")
        total_fondos = c.fetchone()[0] or 0
        
        ttk.Label(info_frame, text=f"Total de Libros en Inventario: {total_libros}", style="Title.TLabel").pack(pady=5)
        ttk.Label(info_frame, text=f"Préstamos Activos: {prestamos_activos}", style="Title.TLabel").pack(pady=5)
        ttk.Label(info_frame, text=f"Libros Devueltos: {libros_devueltos}", style="Title.TLabel").pack(pady=5)
        ttk.Label(info_frame, text=f"Libros Vencidos: {libros_vencidos}", style="Title.TLabel").pack(pady=5)
        ttk.Label(info_frame, text=f"Total en Fondos: ${total_fondos:.2f}", style="Title.TLabel").pack(pady=5)

    def marcar_como_devuelto(self, tree_vencidos, c):
        try:
            seleccion = tree_vencidos.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor, seleccione un préstamo")
                return
            
            item = tree_vencidos.item(seleccion[0])
            prestamo_id = item['values'][0]
            libro = item['values'][1]
            estudiante = item['values'][2]
            dias_vencido = float(item['values'][5])
            
            if messagebox.askyesno("Confirmar", 
                                 f"¿Está seguro que desea marcar este libro como devuelto?\n"
                                 f"No se devolverá el depósito por estar vencido {int(dias_vencido)} días."):
                # Actualizar el estado del préstamo
                c.execute("""
                    UPDATE prestamos 
                    SET devuelto = 1,
                        deposito_devuelto = 0,
                        fecha_devolucion_real = datetime('now')
                    WHERE id = ?
                """, (prestamo_id,))
                
                # Actualizar disponibles del libro
                c.execute("""
                    UPDATE libros 
                    SET disponibles = disponibles + 1 
                    WHERE id = (SELECT libro_id FROM prestamos WHERE id = ?)
                """, (prestamo_id,))
                
                # Registrar en estadísticas diarias
                c.execute("""
                    INSERT INTO estadisticas_diarias (fecha, devoluciones)
                    VALUES (date('now'), 1)
                    ON CONFLICT(fecha) DO UPDATE SET
                    devoluciones = devoluciones + 1
                """)
                
                messagebox.showinfo("Éxito", 
                                  f"Libro '{libro}' marcado como devuelto\n"
                                  f"El depósito no será devuelto debido al retraso")
                
                self.actualizar_lista_vencidos(tree_vencidos, c)
        
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al marcar como devuelto: {str(e)}")

    def marcar_como_pagado(self, tree_vencidos, c):
        try:
            seleccion = tree_vencidos.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor, seleccione un préstamo")
                return
            
            item = tree_vencidos.item(seleccion[0])
            prestamo_id = item['values'][0]
            libro = item['values'][1]
            estudiante = item['values'][2]
            dias_vencido = float(item['values'][5])
            
            # Calcular multa ($1 por día)
            multa = dias_vencido * 1
            
            if messagebox.askyesno("Confirmar", 
                                 f"Multa a pagar: ${multa:.2f}\n"
                                 f"¿El estudiante ha pagado la multa?"):
                
                # Registrar el pago de la multa
                c.execute("""
                    INSERT INTO caja_ahorros (fecha, monto, descripcion)
                    VALUES (date('now'), ?, ?)
                """, (multa, f"Multa por retraso - Libro: {libro} - Estudiante: {estudiante}"))
                
                # Actualizar estado de la multa
                c.execute("""
                    UPDATE prestamos 
                    SET estado_multa = 'PAGADO'
                    WHERE id = ?
                """, (prestamo_id,))
                
                messagebox.showinfo("Éxito", 
                                  f"Multa de ${multa:.2f} registrada como pagada\n"
                                  f"Ahora puede proceder a registrar la devolución del libro")
                
                self.actualizar_lista_vencidos(tree_vencidos, c)
        
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al registrar el pago: {str(e)}")

    def configurar_interfaz(self):
        # Configurar el estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Custom.TButton", padding=5, font=('Arial', 10))
        self.style.configure("Title.TLabel", font=('Arial', 12, 'bold'))
        
        # Crear el menú principal
        self.crear_menu()
        
        # Crear el notebook para las diferentes secciones
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Crear las diferentes pestañas
        self.crear_pestaña_libros()
        self.crear_pestaña_prestamos()
        self.crear_pestaña_reportes()
        
        # Verificar préstamos vencidos
        self.verificar_prestamos_vencidos()
        
        # Configurar el evento de cierre de la ventana
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    def gestionar_estado_prestamo(self):
        # Crear ventana de gestión
        estado_window = tk.Toplevel(self.root)
        estado_window.title("Gestionar Estado de Préstamo")
        estado_window.geometry("800x600")
        
        # Frame para la lista de préstamos
        frame_lista = ttk.LabelFrame(estado_window, text="Préstamos Activos", padding=10)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Crear Treeview
        columns = ('ID', 'Libro', 'Estudiante', 'Fecha Préstamo', 'Fecha Devolución', 'Estado', 'Multa')
        tree = ttk.Treeview(frame_lista, columns=columns, show='headings')
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.column('Libro', width=200)
        tree.column('Estudiante', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Frame para botones de acción
        frame_acciones = ttk.Frame(estado_window)
        frame_acciones.pack(fill='x', padx=10, pady=5)
        
        def actualizar_lista():
            try:
                conn = sqlite3.connect('biblioteca.db')
                c = conn.cursor()
                
                # Limpiar lista actual
                for item in tree.get_children():
                    tree.delete(item)
                
                # Obtener préstamos
                c.execute("""
                    SELECT p.id, l.titulo, p.estudiante, p.fecha_prestamo, p.fecha_devolucion,
                           CASE 
                               WHEN p.devuelto = 1 THEN 'Devuelto'
                               WHEN p.estado_multa = 1 THEN 'Pagado'
                               ELSE 'No Devuelto'
                           END as estado,
                           CASE 
                               WHEN p.estado_multa = 1 THEN '$5'
                               ELSE '-'
                           END as multa
                    FROM prestamos p
                    JOIN libros l ON p.libro_id = l.id
                    ORDER BY p.fecha_prestamo DESC
                """)
                
                for row in c.fetchall():
                    tree.insert("", "end", values=row)
                
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al cargar préstamos: {str(e)}")
            finally:
                if 'conn' in locals():
                    conn.close()
        
        def cambiar_estado(nuevo_estado):
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Advertencia", "Por favor seleccione un préstamo")
                return
            
            prestamo_id = tree.item(selected[0])['values'][0]
            
            try:
                conn = sqlite3.connect('biblioteca.db')
                c = conn.cursor()
                
                # Verificar estado actual
                c.execute("SELECT devuelto, estado_multa FROM prestamos WHERE id = ?", (prestamo_id,))
                estado_actual = c.fetchone()
                
                if estado_actual is None:
                    messagebox.showerror("Error", "Préstamo no encontrado")
                    return
                
                if nuevo_estado == 'devuelto':
                    # Marcar como devuelto y devolver depósito
                    c.execute("""
                        UPDATE prestamos 
                        SET devuelto = 1, 
                            estado_multa = 0,
                            deposito_devuelto = 1,
                            fecha_devolucion_real = datetime('now')
                        WHERE id = ?
                    """, (prestamo_id,))
                    
                    # Actualizar disponibilidad del libro
                    c.execute("""
                        UPDATE libros 
                        SET disponibles = disponibles + 1 
                        WHERE id = (SELECT libro_id FROM prestamos WHERE id = ?)
                    """, (prestamo_id,))
                    
                    messagebox.showinfo("Éxito", "Libro devuelto y depósito reembolsado")
                    
                elif nuevo_estado == 'pagado':
                    # Marcar como pagado (con multa, no se devuelve depósito)
                    c.execute("""
                        UPDATE prestamos 
                        SET devuelto = 1,
                            estado_multa = 1,
                            deposito_devuelto = 0,
                            fecha_devolucion_real = datetime('now')
                        WHERE id = ?
                    """, (prestamo_id,))
                    
                    # Actualizar disponibilidad del libro
                    c.execute("""
                        UPDATE libros 
                        SET disponibles = disponibles + 1 
                        WHERE id = (SELECT libro_id FROM prestamos WHERE id = ?)
                    """, (prestamo_id,))
                    
                    messagebox.showinfo("Éxito", "Libro devuelto con multa registrada")
                    
                elif nuevo_estado == 'no_devuelto':
                    # Marcar como no devuelto
                    c.execute("""
                        UPDATE prestamos 
                        SET devuelto = 0,
                            estado_multa = 0,
                            deposito_devuelto = 0,
                            fecha_devolucion_real = NULL
                        WHERE id = ?
                    """, (prestamo_id,))
                    
                    # Actualizar disponibilidad del libro
                    c.execute("""
                        UPDATE libros 
                        SET disponibles = disponibles - 1 
                        WHERE id = (SELECT libro_id FROM prestamos WHERE id = ?)
                    """, (prestamo_id,))
                    
                    messagebox.showinfo("Éxito", "Préstamo marcado como no devuelto")
                
                conn.commit()
                actualizar_lista()
                
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al actualizar estado: {str(e)}")
            finally:
                if 'conn' in locals():
                    conn.close()
        
        # Botones de acción
        ttk.Button(frame_acciones, text="Marcar como Devuelto", 
                  command=lambda: cambiar_estado('devuelto')).pack(side='left', padx=5)
        ttk.Button(frame_acciones, text="Marcar como No Devuelto", 
                  command=lambda: cambiar_estado('no_devuelto')).pack(side='left', padx=5)
        ttk.Button(frame_acciones, text="Marcar como Pagado (Con Multa)", 
                  command=lambda: cambiar_estado('pagado')).pack(side='left', padx=5)
        ttk.Button(frame_acciones, text="Actualizar", 
                  command=actualizar_lista).pack(side='left', padx=5)
        ttk.Button(frame_acciones, text="Cerrar", 
                  command=estado_window.destroy).pack(side='right', padx=5)
        
        # Mostrar datos iniciales
        actualizar_lista()

if __name__ == "__main__":
    BibliotecaDigital() 