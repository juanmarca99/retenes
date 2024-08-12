import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# Conectar a la base de datos y crear la tabla si no existe
def conectar_db():
    conn = sqlite3.connect('refaccionaria.db')  # Archivo de base de datos persistente
    c = conn.cursor()
    
    # Crear la tabla si no existe
    c.execute('''
        CREATE TABLE IF NOT EXISTS piezas (
            id INTEGER PRIMARY KEY,
            numero_pieza TEXT NOT NULL,
            tipo_pieza TEXT NOT NULL,
            medida_interior TEXT NOT NULL,
            medida_exterior TEXT NOT NULL,
            medida_altura TEXT
        )
    ''')
    
    conn.commit()
    return conn, c

# Función para agregar una pieza
def agregar_pieza():
    numero_pieza = numero_pieza_var.get()
    tipo_pieza = tipo_pieza_var.get()
    medida_interior = medida_interior_var.get() 
    medida_exterior = medida_exterior_var.get() 
    medida_altura = medida_altura_var.get() or None  # Permitir que altura sea opcional
    
    # Verificar si ya existe una pieza con los mismos datos
    c.execute('''
        SELECT COUNT(*) FROM piezas
        WHERE numero_pieza = ? AND tipo_pieza = ? AND medida_interior = ? AND medida_exterior = ? AND medida_altura = ?
    ''', (numero_pieza, tipo_pieza, medida_interior, medida_exterior, medida_altura))
    if c.fetchone()[0] > 0:
        messagebox.showwarning("Advertencia", "Ya existe una pieza con esos datos")
        return

    if numero_pieza and tipo_pieza and medida_interior and medida_exterior:
        c.execute('''
            INSERT INTO piezas (numero_pieza, tipo_pieza, medida_interior, medida_exterior, medida_altura)
            VALUES (?, ?, ?, ?, ?)
        ''', (numero_pieza, tipo_pieza, medida_interior, medida_exterior, medida_altura))
        conn.commit()
        messagebox.showinfo("Éxito", "Pieza agregada correctamente")
        numero_pieza_var.set("")
        tipo_pieza_var.set("")
        medida_interior_var.set("")
        medida_exterior_var.set("")
        medida_altura_var.set("")
        mostrar_todos()  # Actualizar la lista de todas las piezas
    else:
        messagebox.showwarning("Advertencia", "Todos los campos obligatorios deben ser llenados")

# Función para buscar piezas
def buscar_piezas():
    medida_interior = buscar_interior_var.get()
    medida_exterior = buscar_exterior_var.get()
    medida_altura = buscar_altura_var.get() or None
    if medida_interior and medida_exterior:
        query = '''
            SELECT numero_pieza, tipo_pieza, medida_interior, medida_exterior, medida_altura
            FROM piezas
            WHERE medida_interior LIKE ? AND medida_exterior LIKE ?
        '''
        params = (f'%{medida_interior}%', f'%{medida_exterior}%')
        if medida_altura:
            query += ' AND medida_altura LIKE ?'
            params += (f'%{medida_altura}%',)
        c.execute(query, params)
        resultados = c.fetchall()
        mostrar_resultados(resultados)
    else:
        messagebox.showwarning("Advertencia", "Medidas interior y exterior son obligatorias")

# Función para mostrar los resultados de búsqueda
def mostrar_resultados(resultados):
    for item in tree_buscar.get_children():
        tree_buscar.delete(item)
    for resultado in resultados:
        tree_buscar.insert("", tk.END, values=resultado)

# Función para mostrar todas las piezas
def mostrar_todos():
    c.execute('''
        SELECT numero_pieza, tipo_pieza, medida_interior, medida_exterior, medida_altura
        FROM piezas
        ORDER BY numero_pieza ASC
    ''')
    resultados = c.fetchall()
    for item in tree_modificar_eliminar.get_children():
        tree_modificar_eliminar.delete(item)
    for resultado in resultados:
        tree_modificar_eliminar.insert("", tk.END, values=resultado)

# Función para eliminar una pieza
def eliminar_pieza():
    selected_item = tree_modificar_eliminar.selection()
    if selected_item:
        item_numero_pieza = tree_modificar_eliminar.item(selected_item, 'values')[0]
        c.execute('''
            DELETE FROM piezas WHERE numero_pieza = ?
        ''', (item_numero_pieza,))
        conn.commit()
        mostrar_todos()
    else:
        messagebox.showwarning("Advertencia", "Seleccione una pieza para eliminar")

# Función para modificar una pieza
def modificar_pieza():
    selected_item = tree_modificar_eliminar.selection()
    if selected_item:
        item_numero_pieza = tree_modificar_eliminar.item(selected_item, 'values')[0]
        numero_pieza = numero_pieza_mod_var.get()
        tipo_pieza = tipo_pieza_mod_var.get()
        medida_interior = medida_interior_mod_var.get()
        medida_exterior = medida_exterior_mod_var.get()
        medida_altura = medida_altura_mod_var.get() or None

        # Construir la consulta de actualización dinámica
        updates = []
        params = []
        if numero_pieza:
            updates.append("numero_pieza = ?")
            params.append(numero_pieza)
        if tipo_pieza:
            updates.append("tipo_pieza = ?")
            params.append(tipo_pieza)
        if medida_interior:
            updates.append("medida_interior = ?")
            params.append(medida_interior)
        if medida_exterior:
            updates.append("medida_exterior = ?")
            params.append(medida_exterior)
        if medida_altura is not None:
            updates.append("medida_altura = ?")
            params.append(medida_altura)

        if updates:
            query = f'''
                UPDATE piezas
                SET {", ".join(updates)}
                WHERE numero_pieza = ?
            '''
            params.append(item_numero_pieza)
            c.execute(query, params)
            conn.commit()
            messagebox.showinfo("Éxito", "Pieza modificada correctamente")
            numero_pieza_mod_var.set("")
            tipo_pieza_mod_var.set("")
            medida_interior_mod_var.set("")
            medida_exterior_mod_var.set("")
            medida_altura_mod_var.set("")
            mostrar_todos()
        else:
            messagebox.showwarning("Advertencia", "No se ha especificado ningún campo para modificar")
    else:
        messagebox.showwarning("Advertencia", "Seleccione una pieza para modificar")

# Función para buscar pieza en la pestaña de modificar/eliminar
def buscar_pieza_modificar():
    numero_pieza_buscar = buscar_numero_pieza_var.get()
    if numero_pieza_buscar:
        c.execute('''
            SELECT numero_pieza, tipo_pieza, medida_interior, medida_exterior, medida_altura
            FROM piezas
            WHERE numero_pieza = ?
        ''', (numero_pieza_buscar,))
        resultado = c.fetchone()
        if resultado:
            for i, val in enumerate(resultado):
                if i == 0:
                    numero_pieza_mod_var.set(val)
                elif i == 1:
                    tipo_pieza_mod_var.set(val)
                elif i == 2:
                    medida_interior_mod_var.set(val)
                elif i == 3:
                    medida_exterior_mod_var.set(val)
                elif i == 4:
                    medida_altura_mod_var.set(val)
        else:
            messagebox.showwarning("Advertencia", "No se encontró ninguna pieza con ese número")
    else:
        messagebox.showwarning("Advertencia", "Ingrese un número de pieza para buscar")

# Crear la ventana principal
root = tk.Tk()
root.title("Catalogador de Baleros y Retenes")

# Crear el Notebook (pestañas)
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Pestaña de Buscar Pieza
frame_buscar = tk.Frame(notebook, padx=10, pady=10)
notebook.add(frame_buscar, text="Buscar Pieza")

tk.Label(frame_buscar, text="Medida Interior").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
buscar_interior_var = tk.StringVar()
tk.Entry(frame_buscar, textvariable=buscar_interior_var).grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_buscar, text="Medida Exterior").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
buscar_exterior_var = tk.StringVar()
tk.Entry(frame_buscar, textvariable=buscar_exterior_var).grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_buscar, text="Medida Altura (Opcional)").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
buscar_altura_var = tk.StringVar()
tk.Entry(frame_buscar, textvariable=buscar_altura_var).grid(row=2, column=1, padx=5, pady=5)

tk.Button(frame_buscar, text="Buscar", command=buscar_piezas).grid(row=3, columnspan=2, pady=10)

# Crear el árbol para mostrar los resultados de búsqueda
columns_buscar = ("numero_pieza", "tipo_pieza", "medida_interior", "medida_exterior", "medida_altura")
tree_buscar = ttk.Treeview(frame_buscar, columns=columns_buscar, show="headings")
tree_buscar.heading("numero_pieza", text="Número de Pieza")
tree_buscar.heading("tipo_pieza", text="Tipo de Pieza")
tree_buscar.heading("medida_interior", text="Medida Interior")
tree_buscar.heading("medida_exterior", text="Medida Exterior")
tree_buscar.heading("medida_altura", text="Medida Altura")
tree_buscar.grid(row=4, columnspan=2, pady=10, sticky="nsew")

# Pestaña de Agregar Pieza
frame_agregar = tk.Frame(notebook, padx=10, pady=10)
notebook.add(frame_agregar, text="Agregar Pieza")

tk.Label(frame_agregar, text="Número de Pieza").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
numero_pieza_var = tk.StringVar()
tk.Entry(frame_agregar, textvariable=numero_pieza_var).grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_agregar, text="Tipo de Pieza").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
tipo_pieza_var = tk.StringVar()
tk.Entry(frame_agregar, textvariable=tipo_pieza_var).grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_agregar, text="Medida Interior").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
medida_interior_var = tk.StringVar()
tk.Entry(frame_agregar, textvariable=medida_interior_var).grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_agregar, text="Medida Exterior").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
medida_exterior_var = tk.StringVar()
tk.Entry(frame_agregar, textvariable=medida_exterior_var).grid(row=3, column=1, padx=5, pady=5)

tk.Label(frame_agregar, text="Medida Altura (Opcional)").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
medida_altura_var = tk.StringVar()
tk.Entry(frame_agregar, textvariable=medida_altura_var).grid(row=4, column=1, padx=5, pady=5)

tk.Button(frame_agregar, text="Agregar Pieza", command=agregar_pieza).grid(row=5, columnspan=2, pady=10)

# Pestaña de Modificar/Eliminar Pieza
frame_modificar_eliminar = tk.Frame(notebook, padx=10, pady=10)
notebook.add(frame_modificar_eliminar, text="Modificar/Eliminar Pieza")

tk.Label(frame_modificar_eliminar, text="Número de Pieza a Buscar").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
buscar_numero_pieza_var = tk.StringVar()
tk.Entry(frame_modificar_eliminar, textvariable=buscar_numero_pieza_var).grid(row=0, column=1, padx=5, pady=5)

tk.Button(frame_modificar_eliminar, text="Buscar", command=buscar_pieza_modificar).grid(row=1, columnspan=2, pady=10)

tk.Label(frame_modificar_eliminar, text="Número de Pieza").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
numero_pieza_mod_var = tk.StringVar()
tk.Entry(frame_modificar_eliminar, textvariable=numero_pieza_mod_var).grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_modificar_eliminar, text="Tipo de Pieza").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
tipo_pieza_mod_var = tk.StringVar()
tk.Entry(frame_modificar_eliminar, textvariable=tipo_pieza_mod_var).grid(row=3, column=1, padx=5, pady=5)

tk.Label(frame_modificar_eliminar, text="Medida Interior").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
medida_interior_mod_var = tk.StringVar()
tk.Entry(frame_modificar_eliminar, textvariable=medida_interior_mod_var).grid(row=4, column=1, padx=5, pady=5)

tk.Label(frame_modificar_eliminar, text="Medida Exterior").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
medida_exterior_mod_var = tk.StringVar()
tk.Entry(frame_modificar_eliminar, textvariable=medida_exterior_mod_var).grid(row=5, column=1, padx=5, pady=5)

tk.Label(frame_modificar_eliminar, text="Medida Altura (Opcional)").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
medida_altura_mod_var = tk.StringVar()
tk.Entry(frame_modificar_eliminar, textvariable=medida_altura_mod_var).grid(row=6, column=1, padx=5, pady=5)

tk.Button(frame_modificar_eliminar, text="Modificar Pieza", command=modificar_pieza).grid(row=7, column=0, pady=10)
tk.Button(frame_modificar_eliminar, text="Eliminar Pieza", command=eliminar_pieza).grid(row=7, column=1, pady=10)
tk.Button(frame_modificar_eliminar, text="Actualizar", command=mostrar_todos).grid(row=8, columnspan=2, pady=10)

# Crear el árbol para mostrar todas las piezas
columns_modificar_eliminar = ("numero_pieza", "tipo_pieza", "medida_interior", "medida_exterior", "medida_altura")
tree_modificar_eliminar = ttk.Treeview(frame_modificar_eliminar, columns=columns_modificar_eliminar, show="headings")
tree_modificar_eliminar.heading("numero_pieza", text="Número de Pieza")
tree_modificar_eliminar.heading("tipo_pieza", text="Tipo de Pieza")
tree_modificar_eliminar.heading("medida_interior", text="Medida Interior")
tree_modificar_eliminar.heading("medida_exterior", text="Medida Exterior")
tree_modificar_eliminar.heading("medida_altura", text="Medida Altura")
tree_modificar_eliminar.grid(row=9, columnspan=2, pady=10, sticky="nsew")

# Conectar a la base de datos y mostrar todas las piezas al inicio
conn, c = conectar_db()
mostrar_todos()

root.mainloop()
