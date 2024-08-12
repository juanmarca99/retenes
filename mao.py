import sqlite3
import os
import sys
import win32com.client
from tkinter import *
from tkinter import ttk, messagebox

# Crear y configurar la base de datos
def crear_bd():
    conn = sqlite3.connect('inventario_autopartes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Marcas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Autos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca_id INTEGER,
            modelo TEXT NOT NULL,
            anio INTEGER,
            motor TEXT,
            FOREIGN KEY (marca_id) REFERENCES Marcas(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            cantidad INTEGER NOT NULL,
            descripcion TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ProductosAutos (
            id_producto INTEGER,
            id_auto INTEGER,
            FOREIGN KEY (id_producto) REFERENCES Productos(id),
            FOREIGN KEY (id_auto) REFERENCES Autos(id),
            PRIMARY KEY (id_producto, id_auto)
        )
    ''')
    conn.commit()
    conn.close()

# Función para agregar productos
def agregar_producto():
    nombre = entry_nombre.get()
    categoria = categoria_combobox.get()
    precio = entry_precio.get()
    cantidad = entry_cantidad.get()
    descripcion = entry_descripcion.get()
    
    if not nombre or not categoria or not precio or not cantidad:
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return
    
    try:
        precio = float(precio)
        cantidad = int(cantidad)
    except ValueError:
        messagebox.showerror("Error", "Precio y cantidad deben ser numéricos")
        return

    conn = sqlite3.connect('inventario_autopartes.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Productos (nombre, categoria, precio, cantidad, descripcion)
        VALUES (?, ?, ?, ?, ?)
    ''', (nombre, categoria, precio, cantidad, descripcion))
    conn.commit()
    conn.close()
    
    messagebox.showinfo("Éxito", "Producto agregado exitosamente")

# Función para agregar autos
def agregar_auto():
    marca = marca_combobox_autos.get()
    modelo = entry_modelo.get()
    anio = entry_anio.get()
    motor = entry_motor.get()

    if not marca or not modelo or not anio or not motor:
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return

    try:
        anio = int(anio)
    except ValueError:
        messagebox.showerror("Error", "Año debe ser numérico")
        return

    conn = sqlite3.connect('inventario_autopartes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM Marcas WHERE nombre=?', (marca,))
    marca_id = cursor.fetchone()
    if marca_id:
        marca_id = marca_id[0]
    else:
        messagebox.showerror("Error", "Marca no encontrada")
        conn.close()
        return

    cursor.execute('''
        INSERT INTO Autos (marca_id, modelo, anio, motor)
        VALUES (?, ?, ?, ?)
    ''', (marca_id, modelo, anio, motor))
    conn.commit()
    conn.close()
    
    messagebox.showinfo("Éxito", "Auto agregado exitosamente")

# Función para enlazar productos con autos
def enlazar_producto_auto():
    producto = entry_producto_enlazar.get()
    auto = lista_autos.get(ACTIVE)

    if not producto or not auto:
        messagebox.showerror("Error", "Seleccione un producto y un auto")
        return

    conn = sqlite3.connect('inventario_autopartes.db')
    cursor = conn.cursor()
    
    auto_info = auto.split(", ")
    cursor.execute('SELECT id FROM Autos WHERE modelo=? AND anio=? AND motor=?', (auto_info[1], int(auto_info[2]), auto_info[3]))
    auto_id = cursor.fetchone()
    if auto_id:
        auto_id = auto_id[0]
    else:
        messagebox.showerror("Error", "Auto no encontrado")
        conn.close()
        return

    cursor.execute('SELECT id FROM Productos WHERE nombre=?', (producto,))
    producto_id = cursor.fetchone()
    if producto_id:
        producto_id = producto_id[0]
    else:
        messagebox.showerror("Error", "Producto no encontrado")
        conn.close()
        return

    cursor.execute('SELECT 1 FROM ProductosAutos WHERE id_producto=? AND id_auto=?', (producto_id, auto_id))
    if cursor.fetchone():
        messagebox.showinfo("Información", "El producto ya está enlazado con este auto")
    else:
        cursor.execute('''
            INSERT INTO ProductosAutos (id_producto, id_auto)
            VALUES (?, ?)
        ''', (producto_id, auto_id))
        conn.commit()
        messagebox.showinfo("Éxito", "Producto y Auto enlazados exitosamente")

    conn.close()

# Función para cargar la lista de autos en la pestaña de enlace
def cargar_lista_autos():
    lista_autos.delete(0, END)
    conn = sqlite3.connect('inventario_autopartes.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.id, a.modelo, a.anio, a.motor, m.nombre 
        FROM Autos a 
        JOIN Marcas m ON a.marca_id = m.id
    ''')
    autos = cursor.fetchall()
    conn.close()
    for auto in autos:
        display_text = f"{auto[1]}, {auto[2]}, {auto[3]}, {auto[4]}"
        lista_autos.insert(END, display_text)

# Función para cargar las opciones de desplegables en la pestaña de búsqueda
def cargar_opciones_busqueda():
    conn = sqlite3.connect('inventario_autopartes.db')
    cursor = conn.cursor()
    
    # Cargar marcas
    cursor.execute('SELECT nombre FROM Marcas')
    marcas = [row[0] for row in cursor.fetchall()]
    marca_combobox['values'] = marcas

    # Cargar modelos y otros
    marca = marca_combobox.get()
    if marca:
        cursor.execute('SELECT id FROM Marcas WHERE nombre=?', (marca,))
        marca_id = cursor.fetchone()
        if marca_id:
            marca_id = marca_id[0]
            cursor.execute('SELECT DISTINCT modelo FROM Autos WHERE marca_id=?', (marca_id,))
            modelos = [row[0] for row in cursor.fetchall()]
            modelo_combobox['values'] = modelos

            cursor.execute('SELECT DISTINCT anio FROM Autos WHERE marca_id=?', (marca_id,))
            anos = [row[0] for row in cursor.fetchall()]
            anio_combobox['values'] = anos

            cursor.execute('SELECT DISTINCT motor FROM Autos WHERE marca_id=?', (marca_id,))
            motores = [row[0] for row in cursor.fetchall()]
            motor_combobox['values'] = motores

    conn.close()

# Función para buscar productos
def buscar_producto():
    marca = marca_combobox.get()
    modelo = modelo_combobox.get()
    anio = anio_combobox.get()
    motor = motor_combobox.get()

    query = '''
        SELECT p.id, p.nombre, p.categoria, p.precio, p.cantidad, p.descripcion,
               a.modelo, a.anio, a.motor, m.nombre
        FROM Productos p
        LEFT JOIN ProductosAutos pa ON p.id = pa.id_producto
        LEFT JOIN Autos a ON pa.id_auto = a.id
        LEFT JOIN Marcas m ON a.marca_id = m.id
        WHERE 1=1
    '''
    params = []

    if marca:
        query += ' AND m.nombre=?'
        params.append(marca)
    if modelo:
        query += ' AND a.modelo=?'
        params.append(modelo)
    if anio:
        query += ' AND a.anio=?'
        params.append(anio)
    if motor:
        query += ' AND a.motor=?'
        params.append(motor)

    conn = sqlite3.connect('inventario_autopartes.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()

    tree_buscar.delete(*tree_buscar.get_children())
    for resultado in resultados:
        tree_buscar.insert('', 'end', values=resultado)

# Función para eliminar productos
def eliminar_producto():
    selected_item = tree_mostrar_todos.selection()
    if not selected_item:
        messagebox.showerror("Error", "Seleccione un producto para eliminar")
        return

    producto_id = tree_mostrar_todos.item(selected_item[0], 'values')[0]
    conn = sqlite3.connect('inventario_autopartes.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Productos WHERE id=?', (producto_id,))
    cursor.execute('DELETE FROM ProductosAutos WHERE id_producto=?', (producto_id,))
    conn.commit()
    conn.close()
    tree_mostrar_todos.delete(selected_item)
    messagebox.showinfo("Éxito", "Producto eliminado exitosamente")

def editar_producto():
    selected_item = tree_mostrar_todos.selection()
    if not selected_item:
        messagebox.showerror("Error", "Seleccione un producto para editar")
        return

    producto_id = tree_mostrar_todos.item(selected_item[0], 'values')[0]

    # Obtener datos del producto
    conn = sqlite3.connect('inventario_autopartes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Productos WHERE id=?', (producto_id,))
    producto = cursor.fetchone()
    conn.close()

    if not producto:
        messagebox.showerror("Error", "Producto no encontrado")
        return

    # Mostrar ventana de edición
    def guardar_cambios():
        nombre = entry_nombre_edit.get()
        categoria = categoria_combobox_edit.get()
        precio = entry_precio_edit.get()
        cantidad = entry_cantidad_edit.get()
        descripcion = entry_descripcion_edit.get()

        if not nombre or not categoria or not precio or not cantidad:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        try:
            precio = float(precio)
            cantidad = int(cantidad)
        except ValueError:
            messagebox.showerror("Error", "Precio y cantidad deben ser numéricos")
            return

        conn = sqlite3.connect('inventario_autopartes.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Productos
            SET nombre=?, categoria=?, precio=?, cantidad=?, descripcion=?
            WHERE id=?
        ''', (nombre, categoria, precio, cantidad, descripcion, producto_id))
        conn.commit()
        conn.close()
        
        ventana_editar.destroy()
        messagebox.showinfo("Éxito", "Producto actualizado exitosamente")
        cargar_lista_productos()

    ventana_editar = Toplevel()
    ventana_editar.title("Editar Producto")
    ventana_editar.geometry("300x250")
    
    Label(ventana_editar, text="Nombre").pack()
    entry_nombre_edit = Entry(ventana_editar)
    entry_nombre_edit.insert(0, producto[1])
    entry_nombre_edit.pack()

    Label(ventana_editar, text="Categoría").pack()
    categoria_combobox_edit = ttk.Combobox(ventana_editar, values=['Categoría 1', 'Categoría 2', 'Categoría 3'])
    categoria_combobox_edit.set(producto[2])
    categoria_combobox_edit.pack()

    Label(ventana_editar, text="Precio").pack()
    entry_precio_edit = Entry(ventana_editar)
    entry_precio_edit.insert(0, producto[3])
    entry_precio_edit.pack()

    Label(ventana_editar, text="Cantidad").pack()
    entry_cantidad_edit = Entry(ventana_editar)
    entry_cantidad_edit.insert(0, producto[4])
    entry_cantidad_edit.pack()

    Label(ventana_editar, text="Descripción").pack()
    entry_descripcion_edit = Entry(ventana_editar)
    entry_descripcion_edit.insert(0, producto[5])
    entry_descripcion_edit.pack()

    Button(ventana_editar, text="Guardar Cambios", command=guardar_cambios).pack()

def actualizar_lista_productos():
    conn = sqlite3.connect('inventario_autopartes.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Productos
    ''')
    productos = cursor.fetchall()
    conn.close()
    
    tree_mostrar_todos.delete(*tree_mostrar_todos.get_children())
    for producto in productos:
        tree_mostrar_todos.insert('', 'end', values=producto)

# Configurar ventana principal
ventana = Tk()
ventana.title("Gestión de Inventario de Autopartes")
ventana.geometry("800x600")

# Configurar pestañas
notebook = ttk.Notebook(ventana)
notebook.pack(fill='both', expand=True)

# Pestaña Agregar Producto
pestana_agregar_producto = Frame(notebook)
notebook.add(pestana_agregar_producto, text='Agregar Producto')

Label(pestana_agregar_producto, text="Nombre").pack()
entry_nombre = Entry(pestana_agregar_producto)
entry_nombre.pack()

Label(pestana_agregar_producto, text="Categoría").pack()
categoria_combobox = ttk.Combobox(pestana_agregar_producto, values=['Categoría 1', 'Categoría 2', 'Categoría 3'])
categoria_combobox.pack()

Label(pestana_agregar_producto, text="Precio").pack()
entry_precio = Entry(pestana_agregar_producto)
entry_precio.pack()

Label(pestana_agregar_producto, text="Cantidad").pack()
entry_cantidad = Entry(pestana_agregar_producto)
entry_cantidad.pack()

Label(pestana_agregar_producto, text="Descripción").pack()
entry_descripcion = Entry(pestana_agregar_producto)
entry_descripcion.pack()

Button(pestana_agregar_producto, text="Agregar Producto", command=agregar_producto).pack()

# Pestaña Agregar Auto
pestana_agregar_auto = Frame(notebook)
notebook.add(pestana_agregar_auto, text='Agregar Auto')

Label(pestana_agregar_auto, text="Marca").pack()
marca_combobox_autos = ttk.Combobox(pestana_agregar_auto)
marca_combobox_autos.pack()

Label(pestana_agregar_auto, text="Modelo").pack()
entry_modelo = Entry(pestana_agregar_auto)
entry_modelo.pack()

Label(pestana_agregar_auto, text="Año").pack()
entry_anio = Entry(pestana_agregar_auto)
entry_anio.pack()

Label(pestana_agregar_auto, text="Motor").pack()
entry_motor = Entry(pestana_agregar_auto)
entry_motor.pack()

Button(pestana_agregar_auto, text="Agregar Auto", command=agregar_auto).pack()

# Pestaña Enlazar Producto con Auto
pestana_enlazar_producto_auto = Frame(notebook)
notebook.add(pestana_enlazar_producto_auto, text='Enlazar Producto con Auto')

Label(pestana_enlazar_producto_auto, text="Producto").pack()
entry_producto_enlazar = Entry(pestana_enlazar_producto_auto)
entry_producto_enlazar.pack()

Label(pestana_enlazar_producto_auto, text="Auto").pack()
lista_autos = Listbox(pestana_enlazar_producto_auto)
lista_autos.pack()

Button(pestana_enlazar_producto_auto, text="Cargar Autos", command=cargar_lista_autos).pack()
Button(pestana_enlazar_producto_auto, text="Enlazar Producto con Auto", command=enlazar_producto_auto).pack()

# Pestaña Buscar Producto
pestana_buscar_producto = Frame(notebook)
notebook.add(pestana_buscar_producto, text='Buscar Producto')

Label(pestana_buscar_producto, text="Marca").pack()
marca_combobox = ttk.Combobox(pestana_buscar_producto)
marca_combobox.pack()
marca_combobox.bind("<<ComboboxSelected>>", lambda event: cargar_opciones_busqueda())

Label(pestana_buscar_producto, text="Modelo").pack()
modelo_combobox = ttk.Combobox(pestana_buscar_producto)
modelo_combobox.pack()

Label(pestana_buscar_producto, text="Año").pack()
anio_combobox = ttk.Combobox(pestana_buscar_producto)
anio_combobox.pack()

Label(pestana_buscar_producto, text="Motor").pack()
motor_combobox = ttk.Combobox(pestana_buscar_producto)
motor_combobox.pack()

Button(pestana_buscar_producto, text="Buscar", command=buscar_producto).pack()

tree_buscar = ttk.Treeview(pestana_buscar_producto, columns=("id", "nombre", "categoria", "precio", "cantidad", "descripcion", "modelo", "anio", "motor", "marca"), show="headings")
tree_buscar.pack(fill='both', expand=True)
tree_buscar.heading("id", text="ID")
tree_buscar.heading("nombre", text="Nombre")
tree_buscar.heading("categoria", text="Categoría")
tree_buscar.heading("precio", text="Precio")
tree_buscar.heading("cantidad", text="Cantidad")
tree_buscar.heading("descripcion", text="Descripción")
tree_buscar.heading("modelo", text="Modelo")
tree_buscar.heading("anio", text="Año")
tree_buscar.heading("motor", text="Motor")
tree_buscar.heading("marca", text="Marca")

# Pestaña Mostrar Todos
pestana_mostrar_todos = Frame(notebook)
notebook.add(pestana_mostrar_todos, text='Mostrar Todos')

tree_mostrar_todos = ttk.Treeview(pestana_mostrar_todos, columns=("id", "nombre", "categoria", "precio", "cantidad", "descripcion"), show="headings")
tree_mostrar_todos.pack(fill='both', expand=True)
tree_mostrar_todos.heading("id", text="ID")
tree_mostrar_todos.heading("nombre", text="Nombre")
tree_mostrar_todos.heading("categoria", text="Categoría")
tree_mostrar_todos.heading("precio", text="Precio")
tree_mostrar_todos.heading("cantidad", text="Cantidad")
tree_mostrar_todos.heading("descripcion", text="Descripción")

Button(pestana_mostrar_todos, text="Actualizar Lista de Productos", command=actualizar_lista_productos).pack()
Button(pestana_mostrar_todos, text="Eliminar Producto", command=eliminar_producto).pack()
Button(pestana_mostrar_todos, text="Editar Producto", command=editar_producto).pack()

# Inicializar la base de datos
if not os.path.exists('inventario_autopartes.db'):
    crear_bd()

# Cargar datos iniciales
cargar_opciones_busqueda()

ventana.mainloop()