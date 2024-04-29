import tkinter as tk
from tkinter import messagebox, filedialog
import re

archivo_actual = None  # Variable global para almacenar la ruta del archivo actualmente abierto

class Token:
    def __init__(self, valor, fila, columna):
        self.valor = valor
        self.fila = fila
        self.columna = columna

    def __str__(self):
        return f"{self.valor} - Columna: {self.fila}, Fila: {self.columna}"

class PalabraToken(Token):
    def __init__(self, valor, fila, columna):
        super().__init__(valor, fila, columna)
        self.tipo = "Palabra"

    def __str__(self):
        return f"{self.tipo}: - {self.valor} - Columna: {self.fila}, Fila: {self.columna}"

class SimboloToken(Token):
    def __init__(self, valor, fila, columna):
        super().__init__(valor, fila, columna)
        self.tipo = "Simbolo"

    def __str__(self):
        return f"{self.tipo}: - {self.valor} - Columna: {self.fila}, Fila: {self.columna}"

class ErrorToken(Token):
    def __init__(self, valor, fila, columna):
        super().__init__(valor, fila, columna)
        self.tipo = "Error"

    def __str__(self):
        return f"{self.tipo}: - {self.valor} - Columna: {self.fila}, Fila: {self.columna}"

def analizador_sintactico(tokens):
    # Diccionario de palabras clave y sus estructuras sintácticas esperadas
    estructuras_sintacticas = {
        "CrearBD": ["CrearBD", "Palabra", "=", "nueva", "CrearBD()", ";" ],
        "EliminarBD": ["EliminarBD", "Palabra", "=", "nueva", "EliminarBD()", ";"],
        "CrearColeccion": ["CrearColeccion", "Palabra", "=", "nueva", "CrearColeccion(Palabra)"],
        "EliminarColeccion": ["EliminarColeccion", "Palabra", "=", "nueva", "eliminarColeccion", "Simbolo", "Palabra", "Simbolo", "Palabra", "Simbolo"],
        "InsertarUnico": ["InsertarUnico", "Palabra", "=", "nueva", "insertarUnico", "Simbolo", "Palabra", "Simbolo", "Palabra", "Simbolo"],
        "ActualizarUnico": ["ActualizarUnico", "Palabra", "=", "nueva", "actualizarUnico", "Simbolo", "Palabra", "(", "Palabra", ")"],
        "EliminarUnico": ["EliminarUnico", "Palabra", "=", "nueva", "eliminarUnico", "Simbolo", "Palabra", "Simbolo", "Palabra", "Simbolo"],
        "BuscarTodo": ["BuscarTodo", "Palabra", "=", "nueva", "buscarTodo", "Simbolo", "Palabra", "Simbolo"],
        "BuscarUnico": ["BuscarUnico", "Palabra", "=", "nueva", "buscarUnico", "Simbolo", "Palabra", "Simbolo"]
    }

    # Variables para controlar el estado del análisis
    estado = "inicio"
    ultima_palabra = None
    errores = []

    for token in tokens:
        if estado == "inicio":
            if token.valor in estructuras_sintacticas:
                ultima_palabra = token
                estado = "analizando_estructura"
            else:
                errores.append(f"Error sintáctico en la línea {token.fila}: Se esperaba una palabra clave, pero se encontró {token.valor}")
                estado = "error"

        elif estado == "analizando_estructura":
            estructura_esperada = estructuras_sintacticas[ultima_palabra.valor]
            if token.tipo == estructura_esperada[len(ultima_palabra.valor.split())]:
                if len(estructura_esperada) > len(ultima_palabra.valor.split()) + 1:
                    estado = "analizando_argumentos"
                else:
                    estado = "inicio"
            else:
                errores.append(f"Error sintáctico en la línea {token.fila}: Se esperaba {estructura_esperada[len(ultima_palabra.valor.split())]} después de '{ultima_palabra.valor}', pero se encontró {token.valor}")
                estado = "error"

        elif estado == "analizando_argumentos":
            # Aquí podrías agregar la lógica para analizar los argumentos de la sentencia si es necesario
            pass

    if estado == "error":
        for error in errores:
            print(error)
        return False
    else:
        if errores:
            for error in errores:
                print(error)
        else:
            print("El análisis sintáctico fue exitoso.")
        return True

def obtener_tokens(contenido):
    patron = r'\b\w+\b|[^\s\w]'
    tokens = []
    errores = []
    fila_actual = 1
    for match in re.finditer(patron, contenido):
        valor = match.group(0)
        columna_actual = match.start() - contenido.rfind('\n', 0, match.start()) + 1
        if columna_actual == 1:
            fila_actual += 1
        if valor.isalpha():
            tokens.append(PalabraToken(valor, fila_actual, columna_actual))
        elif valor in ["%", "*", "#", "@", "/"] or valor.isdigit():
            errores.append(ErrorToken(valor, fila_actual, columna_actual))
        else:
            tokens.append(SimboloToken(valor, fila_actual, columna_actual))
    return tokens, errores

def ver_tokens(code_area):
    contenido = code_area.get("1.0", "end-1c")
    tokens, errores = obtener_tokens(contenido)
    reporte_tokens = "\n".join(str(token) for token in tokens)
    messagebox.showinfo("Tokens", "Reporte de Tokens:\n\n" + reporte_tokens)

def ver_errores(code_area):
    contenido = code_area.get("1.0", "end-1c")
    tokens, errores = obtener_tokens(contenido)
    if errores:
        reporte_errores = "\n".join(str(error) for error in errores)
        messagebox.showinfo("Errores", "Reporte de Errores:\n\n" + reporte_errores)
    else:
        messagebox.showinfo("Errores", "No se encontraron errores en el archivo.")

def nuevo_archivo(code_area, master):
    contenido_actual = code_area.get("1.0", "end-1c")
    if contenido_actual.strip():
        respuesta = messagebox.askyesnocancel("Nuevo archivo", "¿Desea guardar los cambios en el archivo actual antes de crear uno nuevo?")
        if respuesta is None:
            return
        elif respuesta:
            guardar_como_archivo(code_area)
    code_area.delete("1.0", "end")

def abrir_archivo(code_area):
    global archivo_actual
    ruta_archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
    if ruta_archivo:
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as file:
                contenido = file.read()
        except UnicodeDecodeError:
            with open(ruta_archivo, "r", encoding="latin1") as file:
                contenido = file.read()
        code_area.delete("1.0", "end")
        code_area.insert("1.0", contenido)
        archivo_actual = ruta_archivo

def guardar_archivo(code_area):
    global archivo_actual
    if archivo_actual:
        contenido = code_area.get("1.0", "end-1c")
        with open(archivo_actual, "w") as file:
            file.write(contenido)
    else:
        guardar_como_archivo(code_area)

def guardar_como_archivo(code_area):
    global archivo_actual
    ruta_archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
    if ruta_archivo:
        contenido = code_area.get("1.0", "end-1c")
        with open(ruta_archivo, "w") as file:
            file.write(contenido)
        archivo_actual = ruta_archivo
    code_area.delete("1.0", "end")

def salir(master):
    confirmar_salir = messagebox.askyesno("Salir", "¿Está seguro que desea salir del programa?")
    if confirmar_salir:
        print("Saliendo del programa")
        master.destroy()

def Lexer_NoSQL(code_area):
    contenido = code_area.get("1.0", "end-1c")
    sentencias = []
    inicio_crear = contenido.find("CrearBD")
    inicio_eliminar = contenido.find("EliminarBD")
    inicio_crear_coleccion = contenido.find("CrearColeccion")
    inicio_eliminar_coleccion = contenido.find("EliminarColeccion")
    inicio_insertar_unico = contenido.find("InsertarUnico")
    inicio_actualizar_unico = contenido.find("ActualizarUnico")
    inicio_eliminar_unico = contenido.find("EliminarUnico")
    inicio_buscar_todo = contenido.find("BuscarTodo")
    inicio_buscar_unico = contenido.find("BuscarUnico")

    while inicio_crear != -1 or inicio_eliminar != -1 or inicio_crear_coleccion != -1 or inicio_eliminar_coleccion != -1 or inicio_insertar_unico != -1 or inicio_actualizar_unico != -1 or inicio_eliminar_unico != -1 or inicio_buscar_todo != -1 or inicio_buscar_unico != -1:
        if inicio_crear != -1:
            fin_crear = contenido.find(";", inicio_crear)
            sentencia = contenido[inicio_crear:fin_crear]
            nombre_BD = sentencia.split()[1]  # Obtenemos el nombre de la base de datos
            sentencias.append(f"use ('{nombre_BD}');")
            inicio_crear = contenido.find("CrearBD", fin_crear)

        if inicio_eliminar != -1:
            fin_eliminar = contenido.find(";", inicio_eliminar)
            sentencias.append("db.dropDatabase();")
            inicio_eliminar = contenido.find("EliminarBD", fin_eliminar)

        if inicio_crear_coleccion != -1:
            inicio_parentesis = contenido.find("(", inicio_crear_coleccion)
            fin_parentesis = contenido.find(")", inicio_parentesis)
            nombre_coleccion = contenido[inicio_parentesis + 1: fin_parentesis].strip('\"')
            sentencias.append(f"db.createCollection('{nombre_coleccion}');")
            inicio_crear_coleccion = contenido.find("CrearColeccion", fin_parentesis)

        if inicio_eliminar_coleccion != -1:
            inicio_parentesis = contenido.find("(", inicio_eliminar_coleccion)
            fin_parentesis = contenido.find(")", inicio_parentesis)
            nombre_coleccion = contenido[inicio_parentesis + 1: fin_parentesis].strip('\"')
            sentencias.append(f"db.{nombre_coleccion}.drop();")
            inicio_eliminar_coleccion = contenido.find("EliminarColeccion", fin_parentesis)

        if inicio_insertar_unico != -1:
            inicio_parentesis = contenido.find("(", inicio_insertar_unico)
            fin_parentesis = contenido.find(")", inicio_parentesis)
            elementos = contenido[inicio_parentesis + 1: fin_parentesis].split(",", 1)
            nombre_coleccion = elementos[0].strip('\" ')
            documento = elementos[1].strip('\" {}')
            sentencias.append(f"db.{nombre_coleccion}.insertOne({documento})")
            inicio_insertar_unico = contenido.find("InsertarUnico", fin_parentesis)

        if inicio_actualizar_unico != -1:
            inicio_parentesis = contenido.find("(", inicio_actualizar_unico)
            fin_parentesis = contenido.find(")", inicio_parentesis)
            elementos = contenido[inicio_parentesis + 1: fin_parentesis].split(",", 2)
            nombre_coleccion = elementos[0].strip('\" ')
            filtro = elementos[1].strip('\" {}')
            actualizacion = elementos[2].strip('\" {}')
            sentencias.append(f"db.{nombre_coleccion}.updateOne({filtro}, {actualizacion})")
            inicio_actualizar_unico = contenido.find("ActualizarUnico", fin_parentesis)

        if inicio_eliminar_unico != -1:
            inicio_parentesis = contenido.find("(", inicio_eliminar_unico)
            fin_parentesis = contenido.find(")", inicio_parentesis)
            elementos = contenido[inicio_parentesis + 1: fin_parentesis].split(",", 1)
            nombre_coleccion = elementos[0].strip('\" ')
            filtro = elementos[1].strip('\" {}')
            sentencias.append(f"db.{nombre_coleccion}.deleteOne({filtro})")
            inicio_eliminar_unico = contenido.find("EliminarUnico", fin_parentesis)

        if inicio_buscar_todo != -1:
            inicio_parentesis = contenido.find("(", inicio_buscar_todo)
            fin_parentesis = contenido.find(")", inicio_parentesis)
            nombre_coleccion = contenido[inicio_parentesis + 1: fin_parentesis].strip('\" ')
            sentencias.append(f"db.{nombre_coleccion}.find();")
            inicio_buscar_todo = contenido.find("BuscarTodo", fin_parentesis)

        if inicio_buscar_unico != -1:
            inicio_parentesis = contenido.find("(", inicio_buscar_unico)
            fin_parentesis = contenido.find(")", inicio_parentesis)
            nombre_coleccion = contenido[inicio_parentesis + 1: fin_parentesis].strip('\" ')
            sentencias.append(f"db.{nombre_coleccion}.findOne();")
            inicio_buscar_unico = contenido.find("BuscarUnico", fin_parentesis)

    code_area.delete("1.0", "end")
    for sentencia in sentencias:
        code_area.insert("end", sentencia + "\n")

    print("Traducción a MongoDB completada.")

def generar_mongodb(code_area):
    contenido = code_area.get("1.0", "end-1c")
    tokens, errores = obtener_tokens(contenido)

    if not errores:
        if analizador_sintactico(tokens):
            Lexer_NoSQL(code_area)
    else:
        for error in errores:
            print(error)

def ventana():
    root = tk.Tk()
    root.title("Proyecto #2 - LFP - Keitlyn Tunchez - 202201139")

    window_width = 800  # Ancho 
    window_height = 600  # Alto 
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

    # Barra de menú
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # Crear los menús
    file_menu = tk.Menu(menubar)
    edit_menu = tk.Menu(menubar)
    view_menu = tk.Menu(menubar)
    help_menu = tk.Menu(menubar)
    errors_menu = tk.Menu(menubar)

    menubar.add_cascade(label="Archivo", menu=file_menu)
    menubar.add_cascade(label="Análisis", menu=edit_menu)
    menubar.add_cascade(label="Tokens", menu=view_menu)
    menubar.add_cascade(label="Errores", menu=errors_menu)

    # Opciones del menú Archivo
    file_menu.add_command(label="Nuevo", command=lambda: nuevo_archivo(code_area, root))
    file_menu.add_command(label="Abrir", command=lambda: abrir_archivo(code_area))
    file_menu.add_command(label="Guardar", command=lambda: guardar_archivo(code_area))
    file_menu.add_command(label="Guardar Como", command=lambda: guardar_como_archivo(code_area))
    file_menu.add_separator()
    file_menu.add_command(label="Salir", command=lambda: salir(root))

    # Opción del menú Análisis
    edit_menu.add_command(label="Generar sentencias MongoDB", command=lambda: generar_mongodb(code_area))

    # Opción del menú Tokens
    view_menu.add_command(label="Ver Tokens", command=lambda: ver_tokens(code_area))

    # Opción del menú Errores
    errors_menu.add_command(label="Ver Errores", command=lambda: ver_errores(code_area))

    # Crear el área de edición de código
    code_label = tk.Label(root, text="Archivo de entrada:")
    code_label.pack(anchor="w", padx=10, pady=5)

    code_area = tk.Text(root, font=("Consolas", 12), height=20, width=100)
    code_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    root.mainloop()

if __name__ == "__main__":
    ventana()
