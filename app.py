# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        proyecto Atom
# Purpose:
#
# Author:      Ruben Machado
#
# Created:     18/05/2020
# Copyright:   (c) Ruben Machado 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from tkinter import (Tk, ttk, Label, Button, Entry, LabelFrame, Frame,
PhotoImage, StringVar, Checkbutton, Radiobutton, ANCHOR, DISABLED,
messagebox, IntVar, Text, Canvas, Toplevel, filedialog, END)
from datetime import datetime
import calendar
import sqlite3

#funcion que se encargara de recuperar datos de la base
def rec_uno(query):
    with sqlite3.connect("comim.db") as conn:
        cursor = conn.cursor()
        result = cursor.execute(query).fetchone()
        conn.commit()
    return result

def rec_todos(query):
    with sqlite3.connect("comim.db") as conn:
        cursor = conn.cursor()
        result = cursor.execute(query).fetchall()
        conn.commit()
    return result

#funcion que se ecnargara de guardar datos en la base
def guardar_datos(query, parametros = ()):
    with sqlite3.connect("comim.db") as conn:
        cursor = conn.cursor()
        result = cursor.execute(query, parametros)
        conn.commit()
    return result

#funcion para verificar campos
def verificar_campos(listado):
    listaFinal = []
    for campo in listado:
        if(len(campo) == 0):
            listaFinal.append(campo)

    return len(listaFinal) == 0


#veirificamos que el usuario se encuentra conectado y exista
def user(matricula):
    query = ("SELECT * FROM privilegios WHERE matricula='{}'".format(matricula))
    consulta = rec_uno(query)
    return consulta[5] == "no"


#formato para cedula 1.234.567-8 (11 caracteres en total)
class cedula:
    """Pendiente para termianr
    """
    def __init__(self, lugar, textvariable):
        self.lugar = lugar
        self.textvariable = textvariable

        self.eny = Entry(self.lugar, textvariable=self.textvariable, width=10)
        if(self.textvariable != None):
            self.textvariable.trace("w", lambda *args: self.limite())
            self.textvariable.trace("w", lambda *args: self.formato())

    def grid(self, fila, columna, columnas):
        self.eny.grid(row=fila, column=columna, columnspan=columnas, sticky="we")

    def limite(self):
        self.textvariable.set(self.textvariable.get()[:11])

    def formato(self):
        mostrar = self.textvariable.get()
        #print(mostrar[0] + "." + mostrar[1:4] + "." + mostrar[4:7] + "-" + mostrar[7:8])
        if(len(mostrar) == 8):
            self.textvariable.set("{}.{}.{}-{}".format(mostrar[0], mostrar[1:4], mostrar[4:7], mostrar[7:8]))
        else:
            self.textvariable.set("")
            self.textvariable.set(mostrar)

#constructor de etiquetas
class label:
    def __init__(self, lugar, text, anchor="center"):
        self.lugar = lugar
        self.lbl = Label(self.lugar, text=text, anchor=anchor)

    def grid(self, fila, columna, columnas):
        self.lbl.grid(row=fila, column=columna, columnspan=columnas, sticky="we")

#constructor de campos para ingresar datos
class entry:
    def __init__(self, lugar, textvariable, limite=20, state="normal", show="", foco="no"):
        self.lugar = lugar
        self.textvariable = textvariable
        self.foco = foco
        self.eny = Entry(self.lugar, textvariable=self.textvariable, width=10, state=state, show=show)
        if(self.foco == "si"):
            self.focus()

        if(self.textvariable != None):
            self.textvariable.trace("w", lambda *args: self.limitador(limite))

    def grid(self, fila, columna, columnas):
        self.eny.grid(row=fila, column=columna, columnspan=columnas, sticky="we")

    def focus(self):
        return self.eny.focus()

    def limitador(self, limite):
        self.limite = limite
        self.textvariable.set(self.textvariable.get().title()[:limite])

#constructor de botones
class button:
    def __init__(self, lugar, text, command):
        self.lugar = lugar
        self.btn = Button(self.lugar, text=text, command=command)

    def grid(self, fila, columna, columnas):
        self.btn.grid(row=fila, column=columna, columnspan=columnas, sticky="we")

    def config(self, estado):
        if(estado == "disabled"):
            self.btn.config(state="disabled")
        elif(estado == "normal"):
            self.btn.config(state="normal")


#constructor de botones de radio
class radiobutton:
    def __init__(self, lugar, text, value, variable):
        self.lugar = lugar
        self.rdo = Radiobutton(self.lugar, text=text, value=value, variable=variable, anchor="w")

    def grid(self, fila, columna, columnas):
        self.rdo.grid(row=fila, column=columna, columnspan=columnas, sticky="we")

#constructor de una lista desplegable
class combobox:
    def __init__(self, lugar, textvariable, listado, mostrar, funcion=None):
        self.lugar = lugar
        self.listado = listado
        self.mostrar = mostrar
        self.box = ttk.Combobox(self.lugar, state="readonly", textvariable=textvariable, width=10)
        self.box["values"] = self.listado
        self.box.set(self.mostrar)
        self.box.bind("<<ComboboxSelected>>", funcion)

    def grid(self, fila, columna, columnas):
        self.box.grid(row=fila, column=columna, columnspan=columnas, sticky="we")

#constructor de campo para edad
class spinbox:
    def __init__(self, lugar, desde, hasta, textvariable):
        self.lugar = lugar
        self.desde = desde
        self.hasta = hasta
        self.spin = ttk.Spinbox(self.lugar, from_=self.desde, to=self.hasta, textvariable=textvariable, state="readonly", width=10,)

    def grid(self, fila, columna, columnas):
        self.spin.grid(row=fila, column=columna, columnspan=columnas, sticky="we")

#constructor para campos de check
class check:
    def __init__(self, lugar, variable, texto):
        self.lugar = lugar
        self.cheq = Checkbutton(self.lugar, text=texto, variable=variable, onvalue=texto, offvalue="")

    def grid(self, fila, columna, columnas):
        self.cheq.grid(row=fila, column=columna, columnspan=columnas, sticky="we")

class calendario:
    """
    Al parametro de columnas pasarle una columna menos del total
    Este Objeto fue creado para mostrar un calendario para asi poder
    mostrar una forma mas facil de elegir una fecha y poder de esta
    forma tener un formato general para todos
    """

    def __init__(self, lugar):
        self.lugar = lugar
        self.mostrar = {}

        self.var_fecha = StringVar()

        self.campo = Entry(self.lugar, textvariable=self.var_fecha, state="disabled")
        self.boton = Button(self.lugar, text="...", command=self.popup)

    def grid(self, fila, columna, columnas):
        self.campo.grid(row=fila, column=columna, columnspan=columnas, sticky="we")
        self.boton.grid(row=fila, column=(columna + 3), columnspan=1, sticky="we")

    def popup(self):
        self.boton.config(state="disabled")

        dt = datetime.now()
        self.year = dt.year
        self.month = dt.month

        self.nuevaVentana = Toplevel(self.lugar)
        self.nuevaVentana.title("Elige una Fecha")
        ancho = self.nuevaVentana.winfo_screenwidth()
        alto = self.nuevaVentana.winfo_screenheight()
        var_ancho = (int(ancho / 2) - 150)
        var_alto = (int(alto / 2) - 150)
        self.nuevaVentana.geometry("300x300+{0}+{1}".format(var_ancho, var_alto))
        self.nuevaVentana.resizable(0,0)
        self.nuevaVentana.protocol("WM_DELETE_WINDOW", self.on_exit)

        contenedor = Frame(self.nuevaVentana)
        contenedor.pack()

        for i in range(4):
            Label(contenedor).grid(row=i, column=0)

        encabezado = Frame(contenedor)
        encabezado.grid(row=0, column=0)

        self.meses = ["Enero", "Febrebro", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre"]

        anios = []
        iniciarEn = 1950
        for _ in range(100):
            anios.append(iniciarEn)
            iniciarEn += 1

        self.mes = StringVar()
        self.anio = IntVar()

        label(encabezado, text="Mes").grid(1, 0, 1)
        combobox(encabezado, textvariable=self.mes, listado=self.meses, mostrar=self.meses[self.month - 1], funcion=self.go).grid(1, 1, 1)
        label(encabezado, text="Año").grid(1, 2, 1)
        combobox(encabezado, textvariable=self.anio, listado=anios, mostrar=self.year, funcion=self.go).grid(1, 3, 1)

        cuerpo = Frame(contenedor)
        cuerpo.grid(row=2, column=0)

        self.Calendar(cuerpo, self.mostrar)

    def Calendar(self, parent, values):
        self.values = values
        self.parent = parent
        self.cal = calendar.TextCalendar(calendar.SUNDAY)
        dt = datetime.now()
        self.year = dt.year
        self.month = dt.month
        self.wid = []
        self.day_selected = dt.day
        self.month_selected = self.month
        self.year_selected = self.year
        self.day_name = ""

        self.setup(self.year, self.month)

    def clear(self):
        for w in self.wid[:]:
            w.grid_forget()
            #w.destroy()
            self.wid.remove(w)

    def go(self, event=None):
        self.year = self.anio.get()
        self.month = int(self.meses.index(self.mes.get())) + 1
        self.clear()
        self.setup(self.year, self.month)

    def selection(self, day):
        self.day_selected = day
        self.month_selected = self.month
        self.year_selected = self.year

        self.values["El dia"] = day
        self.values["del Mes"] = self.month
        self.values["del Anio"] = self.year

        self.clear()
        self.setup(self.year, self.month)

    def setup(self, y, m):

        days = ["Domingo", "Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]
        for num, name in enumerate(days):
            t = Label(self.parent, text=name[:3])
            self.wid.append(t)
            t.grid(row=0, column=num, pady=10)

        for w, week in enumerate(self.cal.monthdayscalendar(y, m), 2):
            for d, day in enumerate(week):
                if(day):
                    b = Button(self.parent, width=1, text=day, command=lambda day=day: self.selection(day))
                    self.wid.append(b)
                    b.grid(row=w, column=d, sticky="we")

        sel = Label(self.parent, height=2, text='{} {} {}'.format(self.day_selected, self.meses[self.month_selected - 1], self.year_selected))
        self.wid.append(sel)
        sel.grid(row=8, column=0, columnspan=7)

        ok = Button(self.parent, width=5, text="Seleccionar", command=self.kill_and_save)
        self.wid.append(ok)
        ok.grid(row=9, column=0, columnspan=7, sticky="we")

    def kill_and_save(self):
        self.var_fecha.set("")
        texto = "{} / {} / {}".format(self.mostrar["El dia"], self.mostrar["del Mes"], self.mostrar["del Anio"])
        self.var_fecha.set(texto)
        self.on_exit()

    def on_exit(self):
        self.boton.config(state="normal")
        self.nuevaVentana.destroy()

#notebook que contendra la pestaña para crear perfiles temporales y la pestaña donde se mostraran los perfiles temporales
class nuevoRegistro:
    def __init__(self, lugar, matricula):
        self.lugar = lugar
        self.matricula = matricula

        #veirificamos que el usuario se encuentra conectado y exista
        if(user(self.matricula)):
            ##inicioDeSesion(self.lugar)
            pass
        else:
            self.cont = Frame(self.lugar)
            self.cont.pack()

            #creamos una tabla invisible
            for i in range(12):
                Label(self.cont, width=5).grid(row=0, column=i)

            for i in range(18):
                Label(self.cont, width=5).grid(row=i, column=0, pady=3)

            #variables que almacenaran lo que el usuario escriba en los campos
            self.var_lugar = StringVar() #variable para almacenar la ruta de la foto
            self.var_nombres = StringVar()
            self.var_apellidos = StringVar()
            self.var_matricula = StringVar()
            self.var_edad = IntVar()
            self.var_edad.set(18)
            self.var_sexo = StringVar()
            self.var_sexo.set("Hombre")

            #widgets para nuevo registro
            self.lbl = Label(self.cont, text="Foto de Perfil", relief="solid", bd=1)
            self.lbl.grid(row=1, column=2, columnspan=8, rowspan=8, sticky="wesn")

            button(self.cont, text="Elegir Foto", command=self.cargar_foto).grid(10, 2, 2)

            entry(self.cont, textvariable=self.var_lugar, limite=None).grid(10, 4, 6)

            label(self.cont, text="Nombre", anchor="w").grid(12, 2, 2)
            entry(self.cont, textvariable=self.var_nombres, limite=25, foco="si").grid(12, 4, 6)

            label(self.cont, text="Apellidos", anchor="w").grid(13, 2, 2)
            entry(self.cont, textvariable=self.var_apellidos, limite=25).grid(13, 4, 6)

            label(self.cont, text="Matricula", anchor="w").grid(14, 2, 2)
            entry(self.cont, textvariable=self.var_matricula, limite=6).grid(14, 4, 2)

            label(self.cont, text="Edad").grid(14, 6, 1)

            spinbox(self.cont, desde=18, hasta=30, textvariable=self.var_edad).grid(14, 7, 3)

            label(self.cont, text="Sexo", anchor="w").grid(15, 2, 2)
            radiobutton(self.cont, text="Hombre", value="Hombre", variable=self.var_sexo).grid(15, 4, 3)
            radiobutton(self.cont, text="Mujer", value="Mujer", variable=self.var_sexo).grid(15, 7, 3)

            button(self.cont, text="Agregar", command=self.agregarRegistro).grid(16, 2, 8)

            button(self.cont, text="Cancelar", command=self.cancelar).grid(17, 2, 8)

    #funcion que se encarga de cargar y mostrar la imagen de perfil
    def cargar_foto(self):
        img1 = filedialog.askopenfilename(title="Atom - Elegir Foto", filetypes=(("Imagenes", "*.png*"),
                                                                          ("Todos los Archivos", "**")))
        if(len(img1) != 0):
            self.lbl.forget()
            img = PhotoImage(file="{}".format(img1))
            img = img.zoom(20)
            img = img.subsample(32)
            self.perfil = Label(self.cont, image=img, height=60)
            self.perfil.forget()
            self.perfil.image=img
            self.perfil.grid(row=1, column=2, columnspan=8, rowspan=8, sticky="wens")
            self.var_lugar.set(img1)
        else:
            Label(self.cont, text="Foto de Perfil", relief="solid", bd=1).grid(row=1, column=2, columnspan=8, rowspan=8, sticky="wens")
            self.var_lugar.set("")

    #funcion que se ecargara de limpiar los campos de nuevo Registro
    def cancelar(self):
        Label(self.cont, text="Foto de Perfil", relief="solid", bd=1).grid(row=1, column=2, columnspan=8, rowspan=8, sticky="wens")
        self.var_lugar.set("")
        self.var_nombres.set("")
        self.var_apellidos.set("")
        self.var_matricula.set("")
        self.var_edad.set("18")

    #Esta funcion se encargara de verificar que los campos contengan datos aparte de ver que la matricula sean numeros enteros
    def config(self):
        nombres = self.var_nombres.get()
        apellidos = self.var_apellidos.get()
        matricula = self.var_matricula.get()
        if(len(nombres) != 0 and len(apellidos) != 0 and len(matricula) != 0):
            try:
               int(matricula)
               return True
            except:
                messagebox.showerror("Atom", "Debes completar el Campo Matricula con numeros enteros")
                self.var_matricula.set("")
                return False
        else:
            messagebox.showerror("Atom", "Debes completar Todos los Campos")

    #funcion que se encargara de agregar los datos a la tabla temporal en la base de datos
    def agregarRegistro(self):
        if(self.config()):
            direDeFoto = self.var_lugar.get()
            nombres = self.var_nombres.get()
            apellidos = self.var_apellidos.get()
            matricula = self.var_matricula.get()
            edad = self.var_edad.get()
            sexo = self.var_sexo.get()
            listado = (matricula, nombres, apellidos, edad, sexo, direDeFoto, "ESIM")

            #Hacemos una consulta a la base de datos
            query = "SELECT matricula FROM  registrostemp WHERE matricula='{}'".format(matricula)
            consulta = rec_uno(query)

            #verificamos si ese tripulante ya no fue registrado anteriormente
            if(consulta):
                messagebox.showwarning("Atom", "Ya existe un Tripulante con la Matricula {}".format(consulta[0]))
                self.var_matricula.set("")
            else: #en caso de que no este registrado lo almacenamos
                query = ("INSERT INTO registrostemp VALUES(?,?,?,?,?,?,?)")
                guardar_datos(query, listado)
                self.cancelar() #limpiamos los campos
                messagebox.showinfo("Atom", "Tripulante agregado con exito")


#Todos los Perfiles
class todosLosPerfiles:
    def __init__(self, lugar, matricula):
        self.lugar = lugar
        self.matricula = matricula

        if(user(matricula)):
            inicioDeSesion(self.lugar)
        else:
            self.cont = Frame(self.lugar)
            self.cont.pack()

            #creamos una tabla invisible
            for i in range(12):
                Label(self.cont, width=5).grid(row=0, column=i)

            for i in range(18):
                Label(self.cont, width=5).grid(row=i, column=0, pady=3)

            #configuracion de la tabla
            self.tree = ttk.Treeview(self.cont)
            self.tree["columns"]=("one","two","three")
            self.tree.column("#0", width=20, minwidth=20)
            self.tree.column("one", width=20, minwidth=20)
            self.tree.column("two", width=20, minwidth=20)
            self.tree.column("three", width=20, minwidth=20)
            self.tree.heading("#0",text="Matricula",anchor="w")
            self.tree.heading("one", text="Nombre",anchor="w")
            self.tree.heading("two", text="Apellido",anchor="w")
            self.tree.heading("three", text="sexo",anchor="w")
            self.recuperarDatos()
            self.tree.grid(row=0, column=0, columnspan=12, rowspan=17, sticky="wens")

            button(self.cont, text="Actualizar", command=self.recuperarDatos).grid(17, 0, 3)
            button(self.cont, text="Editar", command=self.editarRegistos).grid(17, 6, 3)
            button(self.cont, text="Eliminar", command=self.eliminarDato).grid(17, 9, 3)


    def recuperarDatos(self):
        records = self.tree.get_children()
        #limpiamos la tabla
        for element in records:
            self.tree.delete(element)

        #conectamos a la base
        query = ("SELECT * FROM registrostemp")
        consulta = rec_todos(query)

        for row in consulta:
            self.tree.insert("", END, text=row[0], values=(row[1], row[2], row[4]))

    #funcion que se encargara de eliminar algun dato Temporal
    def eliminarDato(self):
        try:
            id = self.tree.selection()[0]
            values = self.tree.item(id)["text"]
            pregunta = messagebox.askyesno("Atom", "Desea Elimiar este Elemento?")
            if(pregunta):
                query = ("DELETE FROM registrostemp WHERE matricula='{}'".format(values))
                guardar_datos(query)
                self.recuperarDatos()
                messagebox.showinfo("Atom", "Elemento eliminado con Exito")
        except:
            messagebox.showerror("Atom", "Selecciona un elemento para ELIMINAR")
            return


    #funcion que editara los perfiles
    def editarRegistos(self):
        try:
            id = self.tree.selection()[0]
            values = self.tree.item(id)["text"]
            nuevaVentana = Toplevel(self.lugar)
            ancho = nuevaVentana.winfo_screenwidth()
            alto = nuevaVentana.winfo_screenheight()
            var_ancho = (int(ancho / 2) - 300)
            var_alto = (int(alto / 2) - 350)
            nuevaVentana.resizable(0, 0)
            nuevaVentana.geometry("600x700+{0}+{1}".format(var_ancho, var_alto))
            perfilTemp(nuevaVentana, values)
        except:
            messagebox.showerror("Atom", "selecciona un elemento para EDITAR")


class infoHijos:
    def __init__(self, lugar, matricula):
        self.lugar = lugar
        self.matricula = matricula

        #contenedor para los botones y un mensaje
        self.datosBase = Frame(self.lugar)
        self.datosBase.pack()

        #Este mensaje se mostrara en caso de que no hayan datos que mostrar
        self.mensaje = Label(self.datosBase, text="No hay Datos que Mostrar", anchor="center")

        for i in range(12):
            Label(self.datosBase, width=5).grid(row=0, column=i)
        for i in range(4):
            Label(self.datosBase, width=5).grid(row=i, column=0)

        #configuracion de la tabla
        self.tree = ttk.Treeview(self.datosBase)
        self.tree["columns"]=("one","two","three")
        self.tree.column("#0", width=20, minwidth=20)
        self.tree.column("one", width=20, minwidth=20)
        self.tree.column("two", width=20, minwidth=20)
        self.tree.column("three", width=20, minwidth=20)
        self.tree.heading("#0",text="Nombres",anchor="w")
        self.tree.heading("one", text="Apellidos",anchor="w")
        self.tree.heading("two", text="Nacimiento",anchor="w")
        self.tree.heading("three", text="Cédula",anchor="w")

        #creamos botones especiales para poder descarivarlos si no tenemos datos que mostrar
        self.editar = Button(self.datosBase, text="Editar", command=self.editDatos)
        self.editar.grid(row=3, column=0, columnspan=4, sticky="we")
        self.eliminar = Button(self.datosBase, text="Eliminar", command=self.eliminarDato)
        self.eliminar.grid(row=3, column=4, columnspan=4, sticky="we")

        button(self.datosBase, text="Agregar", command=self.nuevoDato).grid(3, 8, 4)

        #formulario para agregar nuevos datos
        self.contenedor = Frame(self.lugar)

        for i in range(11):
            Label(self.contenedor, width=5).grid(row=0, column=i)
        for i in range(14):
            Label(self.contenedor, width=5).grid(row=i, column=0)

        #variables
        self.varNombres = StringVar()
        self.varApellidos = StringVar()
        self.varCi = StringVar()
        self.varFecNac = StringVar()
        self.varGenero = StringVar()
        self.varGenero.set("Niño")
        self.varNomTutor = StringVar()
        self.varApeTutor = StringVar()
        self.varCiTutor = StringVar()
        self.varFecTutor = StringVar()

        #widgets
        label(self.contenedor, text="Nombres:", anchor="w").grid(2, 3, 2)
        entry(self.contenedor, textvariable=self.varNombres, limite=20, foco="si").grid(2, 5, 4)

        label(self.contenedor, text="Apellidos:", anchor="w").grid(3, 3, 2)
        entry(self.contenedor, textvariable=self.varApellidos, limite=20).grid(3, 5, 4)

        label(self.contenedor, text="CI:", anchor="w").grid(4, 3, 1)
        cedula(self.contenedor, textvariable=self.varCi).grid(4, 5, 2)

        check(self.contenedor, variable=self.varCi, texto="No Sabe").grid(4, 7, 2)
        #entry(self.contenedor, textvariable=self.varCi, limite=11).grid(4, 2, 2)

        label(self.contenedor, text="Fecha de Nacimiento:", anchor="w").grid(5, 3, 3)
        entry(self.contenedor, textvariable=self.varFecNac, limite=10).grid(5, 6, 3)

        label(self.contenedor, text="Genero:", anchor="w").grid(6, 3, 3)
        combobox(self.contenedor, textvariable=self.varGenero, listado=["Niño", "Niña"], mostrar="Niño").grid(6, 5, 4)

        con = rec_uno("SELECT * FROM registrostemp WHERE matricula='{}'".format(self.matricula))
        genero = con[4] #Hombre, Mujer
        if(genero == "Hombre"):
            label(self.contenedor, text="Informacion {}".format("de la Madre"), anchor="w").grid(8, 3, 4)
        else:
            label(self.contenedor, text="Informacion {}".format("del Padre"), anchor="w").grid(8, 3, 4)

        label(self.contenedor, text="Nombres:", anchor="w").grid(9, 3, 2)
        entry(self.contenedor, textvariable=self.varNomTutor, limite=20).grid(9, 5, 4)

        label(self.contenedor, text="Apellidos:", anchor="w").grid(10, 3, 2)
        entry(self.contenedor, textvariable=self.varApeTutor, limite=20).grid(10, 5, 4)

        label(self.contenedor, text="CI:", anchor="w").grid(11, 3, 1)
        #entry(self.contenedor, textvariable=self.varCiMadre, limite=11).grid(11, 4, 2)
        cedula(self.contenedor, textvariable=self.varCiTutor).grid(11, 5, 2)

        check(self.contenedor, variable=self.varCiTutor, texto="No Sabe").grid(11, 7, 2)

        label(self.contenedor, text="Fecha de Nacimiento", anchor="w").grid(12, 3, 3)
        entry(self.contenedor, textvariable=self.varFecTutor).grid(12, 6, 3)

        button(self.contenedor, text="Cancelar", command=self.cancelar).grid(14, 3, 3)
        #button(self.contenedor, text="Agregar", command=self.config).grid(14, 6, 3)

        #creamos un boton especial para poder editar su nombre y su funcion
        self.btn = Button(self.contenedor, text="Guardar", command=self.config)
        self.btn.grid(row=14, column=6, columnspan=3, sticky="we")

        button(self.contenedor, text="<< Volver", command=self.recDatos).grid(15, 3, 6)

        self.recDatos()

    def recDatos(self):
        self.tree.grid_forget()
        self.contenedor.pack_forget()
        self.datosBase.pack()

        con = "SELECT * FROM hijos WHERE matricula={}".format(self.matricula)
        consulta = rec_todos(con)

        if(len(consulta) != 0):
            self.editar.config(state="normal")
            self.eliminar.config(state="normal")
            self.tree.grid(row=1, column=0, columnspan=12, sticky="wens")

            self.mensaje.grid_forget()

            records = self.tree.get_children()
            #limpiamos la tabla
            for element in records:
                self.tree.delete(element)

            for row in consulta:
                self.tree.insert("", END, text=row[1], values=(row[2], row[4], row[3]))
        else:
            self.mensaje.grid(row=1, column=0, columnspan=12, sticky="we")
            self.editar.config(state="disabled")
            self.eliminar.config(state="disabled")


    def editDatos(self):

        try:
            id = self.tree.selection()[0]
            values = self.tree.item(id)["values"]

            self.datosBase.pack_forget()
            self.contenedor.pack()

            con = "SELECT * FROM hijos WHERE ci='{}'".format(values[2])
            consulta = rec_uno(con)

            self.varNombres.set(consulta[1])
            self.varApellidos.set(consulta[2])
            self.varCi.set(consulta[3])
            self.varFecNac.set(consulta[4])
            self.varNomTutor.set(consulta[7])
            self.varApeTutor.set(consulta[8])
            self.varCiTutor.set(consulta[9])
            self.varFecTutor.set(consulta[10])

            self.btn.config(text="Actualizar", command=self.actualizarDatos)
        except:
            messagebox.showerror("Atom", "Selecciona un Elemento Para Editar", parent=self.lugar)

    #funcion que actualizara informacion de un hijo en base a su cedula
    def actualizarDatos(self):

        consulta = "SELECT ci FROM hijos WHERE ci='{}'".format(self.varCi.get())
        cedula = rec_uno(consulta)

        nombres = self.varNombres.get()
        apellidos = self.varApellidos.get()
        ci = self.varCi.get()
        fecha = self.varFecNac.get()
        genero = self.varGenero.get()
        nomTutor = self.varNomTutor.get()
        apeTutor = self.varApeTutor.get()
        ciTutor = self.varCiTutor.get()
        fechaTutor = self.varFecTutor.get()

        listado = (nombres, apellidos, ci, fecha, nomTutor, apeTutor, ciTutor, fechaTutor)

        if(verificar_campos(listado)):
            query = ("UPDATE hijos SET nombres='{1}', apellidos='{2}', ci='{3}', fechaNac='{4}', genero='{5}', nomTutor='{6}', apeTutor='{7}', ciTutor='{8}', fechaTutor='{9}' WHERE ci='{0}'".format(cedula[0], nombres, apellidos, ci, fecha, genero, nomTutor, apeTutor, ciTutor, fechaTutor))
            guardar_datos(query)
            messagebox.showerror("Atom", "Dato Actualizado con Exito", parent=self.lugar)
            self.btn.config(text="Guardar", command=self.config)
            self.cancelar()
            self.recDatos()
        else:
            messagebox.showerror("Atom", "Debes completar todos los campos", parent=self.lugar)

    #funcion que se encargara de eliminar algun dato
    def eliminarDato(self):
        try:
            id = self.tree.selection()[0]
            values = self.tree.item(id)["values"]

            pregunta = messagebox.askyesno("Atom", "Desea Elimiar este Elemento?", parent=self.lugar)
            if(pregunta):
                query = ("DELETE FROM hijos WHERE ci='{}'".format(values[2]))
                guardar_datos(query)
                self.recDatos()
                messagebox.showinfo("Atom", "Elemento Eliminado con Exito", pareny=self.lugar)
        except:
            pass

    def nuevoDato(self):
        self.cancelar()
        self.btn.config(text="Guardar", command=self.config)
        self.datosBase.pack_forget()
        self.contenedor.pack()

    def config(self):
        nombres = self.varNombres.get()
        apellidos = self.varApellidos.get()
        ci = self.varCi.get()
        fecha = self.varFecNac.get()
        genero = self.varGenero.get()
        nomTutor = self.varNomTutor.get()
        apeTutor = self.varApeTutor.get()
        ciTutor = self.varCiTutor.get()
        fechaTutor = self.varFecTutor.get()

        listado = (nombres, apellidos, ci, fecha, nomTutor, apeTutor, ciTutor, fechaTutor)
        listado_guardar = (self.matricula, nombres, apellidos, ci, fecha, genero, 'Null', nomTutor, apeTutor, ciTutor, fechaTutor)

        if(verificar_campos(listado)):
            query = ("INSERT INTO hijos VALUES(?,?,?,?,?,?,?,?,?,?,?)")
            guardar_datos(query, listado_guardar)
            messagebox.showinfo("Atom", "Dato Guardado con Exito", parent=self.lugar)
            self.cancelar()
        else:
            messagebox.showerror("Atom", "Debes Completar Todos los Campos", parent=self.lugar)

    def cancelar(self):
        self.varNombres.set("")
        self.varApellidos.set("")
        self.varCi.set("")
        self.varFecNac.set("")
        self.varNomTutor.set("")
        self.varApeTutor.set("")
        self.varCiTutor.set("")
        self.varFecTutor.set("")

class infoConducta:
    def __init__(self, lugar, matricula):
        self.lugar = lugar
        self.matricula = matricula

        self.cont = Frame(self.lugar)
        self.cont.pack()

        #mensjae que se mostrara encaso de que no tengamos datos que mostrar
        self.mensaje = Label(self.cont, text="No hay Datos que Mostrar", anchor="center")

        for i in range(12):
            Label(self.cont, width=5).grid(row=0, column=i)
        for i in range(4):
            Label(self.cont, width=5).grid(row=i, column=0)

        #Variables
        self.var_numeroOD = StringVar()
        self.var_tipo = StringVar()
        self.var_fechaInicio = StringVar()
        self.var_porOrden = StringVar()
        self.var_limitePena = StringVar()
        self.var_causa = StringVar()
        self.var_legajo = StringVar()

        #configuracion de la tabla
        self.tree = ttk.Treeview(self.cont)
        self.tree["columns"]=("one","two","three")
        self.tree.column("#0", width=20, minwidth=20)
        self.tree.column("one", width=20, minwidth=20)
        self.tree.column("two", width=20, minwidth=20)
        self.tree.column("three", width=20, minwidth=20)
        self.tree.heading("#0",text="N° OD",anchor="w")
        self.tree.heading("one", text="Tipo",anchor="w")
        self.tree.heading("two", text="Inicio",anchor="w")
        self.tree.heading("three", text="Dias",anchor="w")

        #creamos un boton especial para poder trabajar con el y dejarlo descativado si no hay datos que mostrar
        self.btnEditar = Button(self.cont, text="Editar", command=self.editDatos)
        self.btnEditar.grid(row=3, column=0, columnspan=4, sticky="we")
        self.btnEliminar = Button(self.cont, text="Eliminar", command=self.eliminarDato)
        self.btnEliminar.grid(row=3, column=4, columnspan=4, sticky="we")

        button(self.cont, text="Agregar", command=self.agregarDatos).grid(3, 8, 4)

        self.formulario = Frame(self.lugar)

        for i in range(13):
            Label(self.formulario, width=5).grid(row=0, column=i)
        for i in range(10):
            Label(self.formulario, width=5).grid(row=i, column=0)

        label(self.formulario, text="Se ha Dispuesto su", anchor="e").grid(1, 0, 3)
        #entry(self.formulario, textvariable=self.var_tipo).grid(1, 3, 3)

        listado = ["Arresto Simple", "Arresto Riguroso", "Recargo de Servicio Mecanico"]

        combobox(self.formulario, textvariable=self.var_tipo, listado=listado, mostrar="Arresto Simple").grid(1, 3, 3)

        label(self.formulario, text="Numero de OD", anchor="e").grid(1, 6, 3)
        entry(self.formulario, textvariable=self.var_numeroOD).grid(1, 9, 3)

        label(self.formulario, text="Fecha de Inicio", anchor="e").grid(2, 0, 3)
        entry(self.formulario, textvariable=self.var_fechaInicio, limite=10).grid(2, 3, 3)

        label(self.formulario, text="Limite de Pena", anchor="e").grid(2, 6, 3)
        entry(self.formulario, textvariable=self.var_limitePena, limite=2).grid(2, 9, 3)

        label(self.formulario, text="Por Orden del", anchor="e").grid(3, 0, 3)
        entry(self.formulario, textvariable=self.var_porOrden, limite=40).grid(3, 3, 3)

        label(self.formulario, text="Matricula", anchor="e").grid(3, 7, 2)
        entry(self.formulario, textvariable=self.var_legajo).grid(3, 9, 3)

        label(self.formulario, text="Causa", anchor="e").grid(4, 0, 3)
        entry(self.formulario, textvariable=self.var_causa).grid(4, 3, 9)

        label(self.formulario, text="Memorando", anchor="e").grid(5, 0, 3)
        self.var_Memo = Text(self.formulario, width=5, height=2)
        self.var_Memo.grid(row=5, column=3, rowspan=3, columnspan=9, sticky="wesn")

        button(self.formulario, text="Guardar", command=self.config).grid(9, 3, 3)
        button(self.formulario, text="<< Volver", command=self.recDatos).grid(9, 6, 3)
        button(self.formulario, text="Cancelar", command=self.cancelar).grid(9, 9, 3)

        self.recDatos()


    def recDatos(self):
        self.tree.grid_forget()
        self.formulario.pack_forget()
        self.cont.pack()

        query = ("SELECT * FROM conducta WHERE matricula='{}'".format(self.matricula))
        consulta = rec_todos(query)

        if(len(consulta) != 0 ):
            self.tree.grid(row=1, column=0, columnspan=12, sticky="wens")
            self.btnEditar.config(state="normal")
            self.btnEliminar.config(state="normal")
            self.mensaje.grid_forget()

            records = self.tree.get_children()
            #limpiamos la tabla
            for element in records:
                self.tree.delete(element)

            for row in consulta:
                self.tree.insert("", END, text=row[1], values=(row[2], row[3], row[4]))

        else:
            self.mensaje.grid(row=1, column=0, columnspan=12, sticky="we")
            self.btnEditar.config(state="disabled")
            self.btnEliminar.config(state="disabled")

    def editDatos(self):
        messagebox.showinfo("Atom", "Estamos Trabajando para Usted\nPerdone las Molestias", parent=self.lugar)

    #funcion que se encargara de eliminar los datos
    def eliminarDato(self):
        try:
            id = self.tree.selection()[0]
            values = self.tree.item(id)["text"]

            pregunta = messagebox.askyesno("Atom", "Desea Elimiar este Elemento?", parent=self.lugar)
            if(pregunta):
                query = ("DELETE FROM conducta WHERE numerood='{}'".format(values))
                guardar_datos(query)
                self.recDatos()
                messagebox.showinfo("Atom", "Elemento Eliminado con Exito", parent=self.lugar)
        except:
            pass

    def agregarDatos(self):
        self.cont.pack_forget()
        self.formulario.pack()

    def config(self):
        numeroOD = self.var_numeroOD.get()
        tipo = self.var_tipo.get()
        inicio = self.var_fechaInicio.get()
        limite = self.var_limitePena.get()
        orden = self.var_porOrden.get()
        legajo = self.var_legajo.get()
        causa = self.var_causa.get()
        memo = self.var_Memo.get(1.0, 'end')

        lista = (numeroOD, inicio, limite, orden, legajo, causa, memo)
        lista_guardar = (self.matricula, numeroOD, tipo, inicio, limite, orden, legajo, causa, memo)

        if(verificar_campos(lista)):
            query = "INSERT INTO conducta VALUES(?,?,?,?,?,?,?,?,?)"
            guardar_datos(query, lista_guardar)
            messagebox.showinfo("Atom", "Dato Guardado con Exito", parent=self.lugar)
            self.cancelar()
        else:
            messagebox.showerror("Atom", "Debes Completar todos los Campos", parent=self.lugar)

    def cancelar(self):
        self.var_numeroOD.set("")
        self.var_fechaInicio.set("")
        self.var_limitePena.set("")
        self.var_porOrden.set("")
        self.var_legajo.set("")
        self.var_causa.set("")
        self.var_Memo.delete(1.0, 'end')


class infoLogistica:
    def __init__(self, lugar, matricula):
        self.lugar = lugar
        self.matricula = matricula

        #contenedor para la tabla donde mostrara los datos existentes
        self.tabla = Frame(self.lugar)
        self.tabla.pack()

        for i in range(8):
            Label(self.tabla, width=5).grid(row=0, column=i)

        for i in range(4):
            Label(self.tabla).grid(row=i, column=0)

        #Tabla
        self.tree = ttk.Treeview(self.tabla)
        self.tree["columns"]=("one","two")
        self.tree.column("#0", width=100)
        self.tree.column("one", width=15)
        self.tree.column("two", width=15)
        self.tree.heading("#0",text="Articulo", anchor="w")
        self.tree.heading("one", text="Rol", anchor="w")
        self.tree.heading("two", text="Cantidad", anchor="w")

        #creamos un contenedor que almacenera todos los elementos para editar y agregar nuevos datos
        self.contenedor = Frame(self.lugar)
        #self.contenedor.pack()

        for i in range(9):
            Label(self.contenedor, width=5).grid(row=0, column=i)

        for i in range(21):
            Label(self.contenedor).grid(row=i, column=0)

        #canvas es una ventana que nos permitira colocar barras desplazables
        canvas = Canvas(self.contenedor, width=100, highlightthickness=0)
        canvas.grid(row=2, column=0, columnspan=8, rowspan=17, sticky="wesn")

        self.mensaje = Label(self.tabla, text="No hay Datos que mostrar")
        button(self.tabla, text="Agregar", command=self.agregarDatos).grid(3, 4, 4)

        #creamos la barra que se encargara de desplazar la ventana de forma vertical
        yscrollbar = ttk.Scrollbar(self.contenedor, orient="vertical")
        yscrollbar.grid(row=2, column=8, rowspan=20, sticky="sn")
        yscrollbar.config(command=canvas.yview)

        canvas.config(scrollregion=(0, 0, 0, 460), yscrollcommand=yscrollbar.set)

        label(self.contenedor, text="Articulo", anchor="w").grid(1, 0, 4)
        label(self.contenedor, text="Rol", anchor="w").grid(1, 4, 2)
        label(self.contenedor, text="Cantidad", anchor="w").grid(1, 6, 2)

        #creamos un contenedor para todos los elementos de la lista de logistica
        self.cont3 = Frame(canvas)

        for i in range(21):
            Label(self.cont3, width=5).grid(row=i, column=0)

        for i in range(8):
            Label(self.cont3, width=5).grid(row=0, column=i)

        #creamos un listado con todas las variables que almaceran el ROL
        self.var_almohada = StringVar()
        self.var_botasCombate = StringVar()
        self.var_botasGoma = StringVar()
        self.var_buzoT = StringVar()
        self.var_buzoLana = StringVar()
        self.var_buzoPolar = StringVar()
        self.var_campera = StringVar()
        self.var_cinturon = StringVar()
        self.var_colcha = StringVar()
        self.var_colchon = StringVar()
        self.var_distintivos = StringVar()
        self.var_eqdeAgua = StringVar()
        self.var_eqGimnacia = StringVar()
        self.var_frazada = StringVar()
        self.var_gorro = StringVar()
        self.var_jarro = StringVar()
        self.var_juegoCubiertos = StringVar()
        self.var_medias = StringVar()
        self.var_sabanas = StringVar()
        self.var_camisa = StringVar()
        self.var_pantalon = StringVar()

        #variable para la cantidad
        self.cant_almohada = StringVar()
        self.cant_botasCombate = StringVar()
        self.cant_botasGoma = StringVar()
        self.cant_buzoT = StringVar()
        self.cant_buzoLana = StringVar()
        self.cant_buzoPolar = StringVar()
        self.cant_campera = StringVar()
        self.cant_cinturon = StringVar()
        self.cant_colcha = StringVar()
        self.cant_colchon = StringVar()
        self.cant_distintivos = StringVar()
        self.cant_eqdeAgua = StringVar()
        self.cant_eqGimnacia = StringVar()
        self.cant_frazada = StringVar()
        self.cant_gorro = StringVar()
        self.cant_jarro = StringVar()
        self.cant_juegoCubiertos = StringVar()
        self.cant_medias = StringVar()
        self.cant_sabanas = StringVar()
        self.cant_camisa = StringVar()
        self.cant_pantalon = StringVar()


        #lista de variables para el Rol
        self.listaRol = [self.var_almohada, self.var_botasCombate, self.var_botasGoma, self.var_buzoT, self.var_buzoLana, self.var_buzoPolar,
                    self.var_campera, self.var_cinturon, self.var_colcha, self.var_colchon, self.var_distintivos, self.var_eqdeAgua,
                    self.var_eqGimnacia, self.var_frazada, self.var_gorro, self.var_jarro, self.var_juegoCubiertos, self.var_medias,
                    self.var_sabanas, self.var_camisa, self.var_pantalon]

        #lista de variables para la cantidad
        self.listaCant = [self.cant_almohada, self.cant_botasCombate, self.cant_botasGoma, self.cant_buzoT, self.cant_buzoLana, self.cant_buzoPolar,
                    self.cant_campera, self.cant_cinturon, self.cant_colcha, self.cant_colchon, self.cant_distintivos, self.cant_eqdeAgua,
                    self.cant_eqGimnacia, self.cant_frazada, self.cant_gorro, self.cant_jarro, self.cant_juegoCubiertos, self.cant_medias,
                    self.cant_sabanas, self.cant_camisa, self.cant_pantalon]

        #cramos una lista que contenga todos los elementos de los articulos para ahorrarnos codigo inecesario
        self.listaDeArticulos = ["Almohada", "Botas de Combate", "Botas de Goma", "Buzo T Verde", "Buzo de Lana Ingles",
                            "Buzo Polar", "Campera Pixelada", "Cintuton BDU", "Colcha de Cama", "Colchon N°", "Distintivo e Insignias",
                            "Equipo de Agua", "Eq. de Gimnacia Verde", "Frazada N°", "Gorro Pixelado", "Jarro de Aluminio",
                            "Juego de Cubiertos", "Medias Verdes", "Sabanas con Funda", "Camisa Pixelada", "Pantalon Pixelado"]

        #Bucle que se encargara de agregar un widget para cada elemento de la lista
        for i in range(len(self.listaDeArticulos)):
            label(self.cont3, text="{}".format(self.listaDeArticulos[i]), anchor="w").grid(i, 0, 4)
            entry(self.cont3, textvariable=self.listaRol[i]).grid(i, 4, 2)
            spinbox(self.cont3, desde=1, hasta=5, textvariable=self.listaCant[i]).grid(i, 6, 2)

        canvas.create_window(0, 0, anchor="nw", window=self.cont3)

        #el boton para guardar los datos
        self.btn = Button(self.contenedor, text="Guardar", command=self.config)
        self.btn.grid(row=23, column=4, columnspan=4, sticky="we")

        button(self.contenedor, text="<< Volver", command=self.recuperarDatos).grid(23, 0, 4)

        self.recuperarDatos()

    def recuperarDatos(self):
        self.contenedor.pack_forget()
        self.tabla.pack()

        log = "SELECT * FROM logistica WHERE matricula='{}'".format(self.matricula)
        logistica = rec_uno(log)

        cant = "SELECT * FROM cantidad WHERE matricula='{}'".format(self.matricula)
        cantidad = rec_uno(cant)

        if(logistica and cantidad):
            self.mensaje.grid_forget()
            self.tree.grid(row=1, column=0, columnspan=8, sticky="wesn")

            records = self.tree.get_children()
            #limpiamos la tabla
            for element in records:
                self.tree.delete(element)

            inicio = 1

            for row in range(len(self.listaDeArticulos)):
                self.tree.insert("", END,  text=self.listaDeArticulos[row], values=(logistica[inicio], cantidad[inicio]))
                inicio = inicio + 1

        else:
            self.mensaje.grid(row=1, column=0, columnspan=8, sticky="we")


    def agregarDatos(self):
        self.tabla.pack_forget()
        self.contenedor.pack()

    #funcion que se encargara de guardar los datos
    def config(self):
        #creamos una tabla nueva que contendra los datos nuevos o los campos vacios
        almacenarRol = [self.matricula]
        almacenarCant = [self.matricula]

        for i in range(len(self.listaRol)):

            if(len(self.listaRol[i].get()) != 0):
                almacenarRol.append(self.listaRol[i].get())
            else:
                almacenarRol.append("No tiene")
                almacenarCant.append(0)

        Rol = "INSERT INTO logistica VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        guardar_datos(Rol, almacenarRol)

        Cant = "INSERT INTO cantidad VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        guardar_datos(Cant, almacenarCant)

        messagebox.showinfo("Atom", "Datos Almacenados con Exito", parent=self.lugar)

class otrosDatos:
    def __init__(self, lugar):
        self.lugar = lugar

        self.cont = Frame(self.lugar)
        self.cont.pack()

        for i in range(12):
            Label(self.cont, width=5).grid(row=0, column=i)
        for i in range(20):
            Label(self.cont).grid(row=i, column=0)

        #variables
        self.var_contrato = StringVar()
        self.var_trabaja = StringVar()
        self.var_estudia = StringVar()
        self.var_servicios = StringVar()
        self.var_retencion = StringVar()

        self.var_retencion.set("No")
        self.var_estudia.set("No")

        label(self.cont, text="Fecha del Ultimo Ascenso", anchor="w").grid(1, 1, 4)
        entry(self.cont, textvariable=None, state="readonly").grid(1, 5, 3)

        label(self.cont, text="Vencimiento de Documentos", anchor="w").grid(3, 1, 4)
        label(self.cont, text="Contrato", anchor="w").grid(4, 1, 2)
        entry(self.cont, textvariable=self.var_contrato).grid(4, 5, 3)

        label(self.cont, text="Carne de Salud", anchor="w").grid(5, 1, 3)
        entry(self.cont, textvariable=None).grid(5, 5, 3)

        label(self.cont, text="T.I.M", anchor="w").grid(6, 1, 1)
        entry(self.cont, textvariable=None).grid(6, 5, 3)
        #calendario(self.cont).grid(6, 8, 1)

        label(self.cont, text="Trabaja Afuera?", anchor="w").grid(8, 1, 4)
        radiobutton(self.cont, text="Si", value="Si", variable=self.var_trabaja).grid(8, 5, 1)
        radiobutton(self.cont, text="No", value="No", variable=self.var_trabaja).grid(8, 6, 1)

        label(self.cont, text="Realiza Servicio Especial?", anchor="w").grid(9, 1, 4)
        radiobutton(self.cont, text="Si", value="Si", variable=self.var_servicios).grid(9, 5, 1)
        radiobutton(self.cont, text="No", value="No", variable=self.var_servicios).grid(9, 6, 1)

        label(self.cont, text="Direccion Completa", anchor="w").grid(10, 1, 4)
        entry(self.cont, textvariable=None).grid(10, 5, 6)

        label(self.cont, text="Seccional Policial", anchor="w").grid(11, 1, 4)
        entry(self.cont, textvariable=None).grid(11, 5, 3)

        label(self.cont, text="Profeccion Diplimado", anchor="w").grid(12, 1, 4)
        entry(self.cont, textvariable=None).grid(12, 5, 3)

        label(self.cont, text="Estudia Afuera", anchor="w").grid(13, 1, 4)
        radiobutton(self.cont, text="Si", value="Si", variable=self.var_estudia).grid(13, 5, 1)
        radiobutton(self.cont, text="No", value="No", variable=self.var_estudia).grid(13, 6, 1)

        label(self.cont, text="Retencion Judicial", anchor="w").grid(14, 1, 4)
        radiobutton(self.cont, text="Si", value="Si", variable=self.var_retencion).grid(14, 5, 1)
        radiobutton(self.cont, text="No", value="No", variable=self.var_retencion).grid(14, 6, 1)

        label(self.cont, text="Grupo Sanguineo", anchor="w").grid(15, 1, 4)
        entry(self.cont, textvariable=None).grid(15, 5, 3)

        label(self.cont, text="Contacto", anchor="w").grid(17, 1, 4)

        label(self.cont, text="Celular", anchor="w").grid(18, 1, 4)
        entry(self.cont, textvariable=None).grid(18, 5, 3)

        label(self.cont, text="Telefono", anchor="w").grid(19, 1, 4)
        entry(self.cont, textvariable=None).grid(19, 5, 3)

        button(self.cont, text="Guardar", command=None).grid(21, 9, 3)


class perfilTemp:
    def __init__(self, lugar, matricula):
        self.lugar = lugar
        self.matricula = matricula

        #nos conectamos a la base de datos segun matricula que nos pasan
        query = ("SELECT * FROM registrostemp WHERE matricula='{}'".format(matricula))
        consulta = rec_uno(query)
        #contenedor para las pestanias
        ventanas = ttk.Notebook(self.lugar, height=500)

        #contenedor para informacion basica
        self.info = Frame(self.lugar)
        self.info.pack()

        for i in range(12):
            Label(self.info, width=5).grid(row=0, column=i)

        for i in range(6):
            Label(self.info, width=5).grid(row=i, column=0)

        #variables vacias
        self.var_subunidad = StringVar()
        self.var_nombre = StringVar()
        #self.var_apellido = StringVar()
        self.var_matricula = StringVar()
        self.var_sexo = StringVar()
        self.var_lugar = StringVar()

        #le asignamos datos a las varibales
        self.var_nombre.set("{} {}".format(consulta[1], consulta[2]))
        #self.var_apellido.set(consulta[2])
        self.var_matricula.set(consulta[0])
        self.var_sexo.set(consulta[4])
        self.var_lugar.set(consulta[5])
        self.var_subunidad.set(consulta[6])

        #perfil
        if(self.cargar_foto(consulta[5])):
            img1 = consulta[5]
            img = PhotoImage(file="{}".format(img1))
            img = img.zoom(10)
            img = img.subsample(32)
            perfil = Label(self.info, image=img, height=60)
            perfil.image=img
            perfil.grid(row=1, column=0, columnspan=4, rowspan=6, sticky="wens")
        else:
            perfil = Label(self.info, text="Error al Cargar \n la Foto de Perfil", relief="solid", bd=1)
            perfil.grid(row=1, column=0, columnspan=4, rowspan=6, sticky="wens")


        #widget
        label(self.info, text="Grado / Esp", anchor="w").grid(1, 4, 2)
        #entry(self.info, textvariable=None).grid(1, 7, 5)

        listadoGrado = ["Marinero de Primera", "Cabo de Segunda", "Cabo de Primera", "Sub Oficial de Segunda", "Sub Oficial de Primera", "Sub Oficial de Cargo"]

        combobox(self.info, textvariable=None, listado=listadoGrado, mostrar="Marinero de Primera").grid(1, 6, 4)

        combobox(self.info, textvariable=None, listado=["(FUS)", "(PM)"], mostrar="(FUS)").grid(1, 10, 2)

        label(self.info, text="Nombre", anchor="w").grid(2, 4, 2)
        entry(self.info, textvariable=self.var_nombre, state="readonly").grid(2, 6, 6)

        label(self.info, text="Matricula", anchor="w").grid(3, 4, 2)
        entry(self.info, textvariable=self.var_matricula, state="readonly").grid(3, 6, 6)

        label(self.info, text="Sexo", anchor="w").grid(4, 4, 2)
        entry(self.info, textvariable=self.var_sexo, state="readonly").grid(4, 6, 6)

        label(self.info, text="Sub Unidad", anchor="w").grid(5, 4, 2)

        listado = ["Compañia 1", "Compañia 2", "Compañia 3", "Compañia 4", "COSER", "COFFEE", "EMCOMIM S-1", "EMCOMIM S-2",
                    "EMCOMIM S-3", "EMCOMIM S-4", "EMCOMIM S-5", "Suino", "ESIM", "K-9"]

        combobox(self.info, textvariable=self.var_subunidad, listado=listado, mostrar="{}".format(consulta[6]), funcion=self.subUnidad).grid(5, 6, 6)

        button(self.info, text="Cambiar Foto", command=self.recargar_foto).grid(6, 4, 2)

        entry(self.info, textvariable=self.var_lugar, limite=None).grid(6, 6, 6)

        #contenedor para datos personales
        contenedor_datos = Frame(ventanas)
        self.cont1 = Frame(contenedor_datos)
        self.cont1.pack()

        #variables
        self.var_nacidoen = StringVar()
        self.var_eldia = StringVar()
        self.var_madre = StringVar()
        self.var_padre = StringVar()

        self.var_antiguedad = StringVar()

        #asignamos algunos datos variables
        self.var_madre.set("Nombre de la Madre...")
        self.var_padre.set("Nombre del Padre...")
        self.var_antiguedad.set("Se genera de Forma Automatica")

        for i in range(12):
            Label(self.cont1, width=5).grid(row=0, column=i)
        for i in range(13):
            Label(self.cont1, width=5).grid(row=i, column=0, pady=3)

        #variables
        #widgets
        label(self.cont1, text="Nacido en").grid(1, 0, 2)

        listadeDepartamentos = ["Artigas", "Canelones", "Cerro Largo", "Colonia", "Durazno", "Flores", "Florida", "Lavalleja", "Maldonado", "Montevideo",
                    "Paysandú", "Rio Negro", "rivera", "Rocha", "Salto", "San José", "Soriano", "Tacuarembó", "Treinta y Tres"]

        combobox(self.cont1, textvariable=None, listado=listadeDepartamentos, mostrar="Artigas").grid(1, 2, 4)

        label(self.cont1, text="el Dia").grid(1, 6, 2)
        #entry(self.cont1, textvariable=None, state="readonly").grid(1, 8, 3)
        calendario(self.cont1).grid(1, 8, 3)
        
        label(self.cont1, text="Hijo de").grid(2, 0, 2)

        entry(self.cont1, textvariable=self.var_madre).grid(2, 2, 4)
        label(self.cont1, text="de Nacionalidad").grid(2, 6, 3)

        entry(self.cont1, textvariable=None).grid(2, 9, 3)
        label(self.cont1, text="y de").grid(3, 0, 2)

        entry(self.cont1, textvariable=self.var_padre).grid(3, 2, 4)
        label(self.cont1, text="de Nacionalidad").grid(3, 6, 3)

        entry(self.cont1, textvariable=None).grid(3, 9, 3)
        label(self.cont1, text="Ingreso a la Armada en Clase de").grid(4, 0, 5)

        combobox(self.cont1, textvariable=None, listado=["Marinero de Primera", "Otro"], mostrar="Marinero de Primera").grid(4, 5, 7)

        label(self.cont1, text="el Dia").grid(5, 0, 1)
        calendario(self.cont1).grid(5, 1, 3)

        label(self.cont1, text="Antiguedad").grid(5, 6, 2)
        entry(self.cont1, textvariable=self.var_antiguedad).grid(5, 8, 4)

        label(self.cont1, text="Credencial Civica Serie").grid(6, 0, 4)
        entry(self.cont1, textvariable=None).grid(6, 4, 4)

        label(self.cont1, text="Numero").grid(6, 8, 2)
        entry(self.cont1, textvariable=None).grid(6, 10, 2)

        label(self.cont1, text="CI:").grid(7, 0, 1)
        entry(self.cont1, textvariable=None).grid(7, 1, 3)

        label(self.cont1, text="Juro la Bandera").grid(7, 4, 3)
        calendario(self.cont1).grid(7, 7, 3)

        label(self.cont1, text="A quien llamar en caso de Accidente:", anchor="w").grid(9, 0, 6)
        label(self.cont1, text="Nombre").grid(10, 0, 2)
        entry(self.cont1, textvariable=None).grid(10, 2, 4)

        label(self.cont1, text="Contacto").grid(10, 6, 2)
        entry(self.cont1, textvariable=None).grid(10, 8, 4)

        label(self.cont1, text="Relacion con el Tripulante").grid(11, 0, 5)
        entry(self.cont1, textvariable=None).grid(11, 4, 4)

        button(self.cont1, text="Guardar", command=self.mensaje).grid(13, 8, 4)

        #contenedor para otros datos de interes
        contenedor_otrosDatos = Frame(ventanas)
        otrosDatos(contenedor_otrosDatos)

        #contenedor para los datos de los hijos
        contenedor_hijos = Frame(ventanas)
        infoHijos(contenedor_hijos, self.matricula)

        #contenedor para sanciones diciplinarias
        contenedor_conducta = Frame(ventanas)
        infoConducta(contenedor_conducta, self.matricula)

        #contenedor para logistica
        contenedor_logistica = Frame(ventanas)
        infoLogistica(contenedor_logistica, self.matricula)

        #contenedores - faltan ordenarlos
        #estos contenedores no tienen nada aun nungun widget estan vacios simplemente
        #los cree para que aparezcan en el menu

        #contenedor para las calificaciones anuales
        #contenedor_calificaciones = Frame(ventanas)
        #self.construccion(contenedor_calificaciones)

        #contenedor para los datos de licencias anuales, por enfernedad o especiales
        #contenedor_licencias = Frame(ventanas)

        #contenedor para los datos de navegacion es posible que no lo agreguemos pero por ahora es parte
        #contenedor_navegacion = Frame(ventanas)

        #contenedpr para los datos de los cursos
        #contenedor_cursos = Frame(ventanas)

        #creamos las pestanias
        ventanas.add(contenedor_datos, text="Datos Personales")
        ventanas.add(contenedor_otrosDatos, text="Otros Datos de Interes")
        ventanas.add(contenedor_hijos, text="Hijos")
        ventanas.add(contenedor_conducta, text="Conducta")
        ventanas.add(contenedor_logistica, text="Logistica")
        #ventanas.add(contenedor_calificaciones, text="Calificaciones, proximamente.. Cursos, Navegacion, Licencias")
        #ventanas.add(contenedor_cursos, text="Cursos")
        #ventanas.add(contenedor_navegacion, text="Navegacion")
        #ventanas.add(contenedor_licencias, text="Licencias")
        ventanas.pack(pady=10, ipadx=5)


    def construccion(self, lugar):
        self.lugar = lugar
        self.cont5 = Frame(lugar)
        self.cont5.pack()
        for i in range(12):
            Label(self.cont5, width=5).grid(row=0, column=i)
        for i in range(20):
            Label(self.cont5, width=5).grid(row=i, column=0)
        #widgets
        label(self.cont5, text="Zona en construccion...").grid(1, 0, 12)
        label(self.cont5, text="Estamos Trabajando para Usted, Disculpe las molestias").grid(2, 0, 12)
        #imagen
        img2 = "zona_en_construcion.png"
        img = PhotoImage(file="{}".format(img2))
        img = img.zoom(15)
        img = img.subsample(32)
        perfil = Label(self.cont5, image=img, height=60)
        perfil.image=img
        perfil.grid(row=3, column=0, columnspan=12, rowspan=17, sticky="wens")

    #Funcion que se encargara de verificar si la direccion donde esta la imagen existe
    def cargar_foto(self, filePath):
        try:
            with open(filePath, 'r'):
                return True
        except:
            return False

    def mensaje(self, event=None):
        messagebox.showinfo("Atom", "Estamos Trabajando para Usted Perdone las Molestias", parent=self.lugar)

    #funcion que se encarga poder cambiar la foto de perfil en caso de que no tenga una o actualizacion
    def recargar_foto(self):
        img1 = filedialog.askopenfilename(title="Atom - Elegir Foto", filetypes=(("Imagenes", "*.png*"),
                                                                          ("Todos los Archivos", "**")), parent=self.lugar)
        if(len(img1) != 0):
            img = PhotoImage(file="{}".format(img1))
            img = img.zoom(10)
            img = img.subsample(32)
            self.perfil = Label(self.info, image=img, height=60)
            self.perfil.forget()
            self.perfil.image=img
            self.perfil.grid(row=1, column=0, columnspan=4, rowspan=6, sticky="wens")
            self.var_lugar.set(img1)

            query = "UPDATE registrostemp SET dirDeFoto='{1}' WHERE matricula='{0}'".format(self.matricula, img1)
            guardar_datos(query)
            messagebox.showinfo("Atom", "Foto Actualizada con Exito", parent=self.lugar)
        else:
            self.var_lugar.set("")

    #Esta funcion se encargara de Actualizar los pases de brigadas
    def subUnidad(self, event=None):
        query = "UPDATE registrostemp SET subunidad='{1}' WHERE matricula='{0}'".format(self.matricula, self.var_subunidad.get())
        guardar_datos(query)
        messagebox.showinfo("Atom", "Dato Actualizado con Exito", parent=self.lugar)


#esta funcion es se encargara de iniciar sesionn siempre y cuando el usuario exista y este tengra privilegios
#o puede que inicie como invitado lo cual lo limitara a solo observar los datos
class inicioDeSesion:
    def __init__(self, lugar):
        self.lugar = lugar

        #contenedor Principal
        self.cont = Frame(self.lugar)
        self.cont.pack(pady=50)

        for i in range(12):
            Label(self.cont, width=5).grid(row=0, column=i)
        for i in range(19):
            Label(self.cont, width=5).grid(row=i, column=0)

        #imagen
        img = PhotoImage(file="escudo.png")
        perfil = Label(self.cont, image=img, bg="#fff")
        perfil.image=img
        perfil.grid(row=0, column=0, columnspan=12, rowspan=15, sticky="wens")
        #contenedor para el formulario
        self.cont1 = LabelFrame(self.cont, text="Iniciar Sesion", pady=10)
        self.cont1.grid(row=15, column=0, rowspan=4, columnspan=12, sticky="wens")

        for i in range(12):
            Label(self.cont1, width=5).grid(row=0, column=i)
        for i in range(4):
            Label(self.cont1, width=5).grid(row=i, column=0)

        #variables
        self.var_matricula = StringVar()
        self.var_codigo = StringVar()

        #widgets
        label(self.cont1, text="Matricula").grid(0, 1, 2)
        entry(self.cont1, textvariable=self.var_matricula, limite=6, foco="si").grid(0, 3, 7)

        label(self.cont1, text="Codigo").grid(1, 1, 2)
        entry(self.cont1, textvariable=self.var_codigo, limite=15, show="*").grid(1, 3, 7)

        button(self.cont1, text="Ingresar", command=self.config).grid(2, 3, 7)
        button(self.cont1, text="Ingresar Como Invitado", command=None).grid(3, 3, 7)

    def config(self):
        matricula = self.var_matricula.get()
        codigo = self.var_codigo.get()
        listado = (matricula, codigo)

        if(verificar_campos(listado)):
            if(self.verEntero(matricula)):
                query = ("SELECT * FROM privilegios WHERE matricula='{}'".format(matricula))
                con = rec_uno(query)
                if(con):
                    if(con[3] == codigo):
                        query = ("UPDATE privilegios SET online='si' WHERE matricula='{}'".format(con[0]))
                        guardar_datos(query)
                        self.cont.pack_forget()
                        menuPrincipal(self.lugar, con[0])
                    else:
                        messagebox.showerror("Atom", "La Contraseña es incorrecta")
                        self.var_codigo.set("")
                else:
                    messagebox.showerror("Atom", "El Tripulante no existe")
                    self.var_matricula.set("")
                    self.var_codigo.set("")
            else:
                messagebox.showerror("Atom", "Completa el campo Matricula con numeros enteros")
                self.var_matricula.set("")
        else:
            messagebox.showerror("Atom", "Debes completar todos los campos")

    def verEntero(self, entero):
        try:
            int(entero)
            return True
        except:
            return False

#contenedor del menu principal
class menuPrincipal:
    def __init__(self, lugar, matricula):
        self.lugar = lugar
        self.matricula = matricula
        estilo = ttk.Style(self.lugar)
        estilo.configure("lefttab.TNotebook", tabposition="wn")

##        config = {
##            "lefttab.TNotebook": {
##                "configure": {
##                    "tabposition": "wn"}
##                    },
##
##            "lefttab.TNotebook.Tab": {
##                "configure": {
##
##                    "padding": [10, 10],
##                    "width": 30,
##                    "anchor": "center",
##                    "background": "#fdd57e" },
##
##                "map": {
##                    "background": [("selected", "#C70039"), ("active", "#fc9292")],
##                    "foreground": [("selected", "#ffffff"), ("active", "#000000")]
##                    }
##                }
##            }
##
##        estilo.theme_create("miestilo", settings=config)
##        estilo.theme_use("miestilo")


        notebook = ttk.Notebook(self.lugar, style="lefttab.TNotebook")

        #Vamos a colocar una seccion donde nos aparezca los datos del admin mas sus privilegios

        #pestania que muestra el formulario para crar perfil temporal y perfiles temporales creados
        #f1 = Frame(notebook, bg="blue")

        f2 = Frame(notebook)
        nuevoRegistro(f2, self.matricula)

        f3 = Frame(notebook)
        todosLosPerfiles(f3, self.matricula)

        #f4 = Frame(notebook, bg="green")

        #creamos las pestanias
        #notebook.add(f1, text='Notificaciones')
        notebook.add(f2, text='Nuevo Perfil')
        notebook.add(f3, text="Todos los Perfiles")
        #notebook.add(f4, text="Asignar Privilgios")
        notebook.pack(pady=50)

#Ventana principal
class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Comando de Infanteria de Marina")
        ancho = self.winfo_screenwidth()
        alto = self.winfo_screenheight()
        var_ancho = (int(ancho / 2) - 475)
        var_alto = (int(alto / 2) - 350)
        self.geometry("950x700+{0}+{1}".format(var_ancho, var_alto))
        self.minsize(950, 700)
        #funcion que se encarga de preguntar antes de cerrar la ventana
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        inicioDeSesion(self)
        #nuevoRegistro(self, 190029)
        #perfilTemp(self, 190029)

    def on_exit(self):
        if messagebox.askyesno("Atom", "Salir?"):
            query = ("SELECT * FROM privilegios WHERE online='si'")
            consulta = rec_uno(query)
            if(consulta):
                query = ("UPDATE privilegios SET online='no' WHERE matricula='{}'".format(consulta[0]))
                guardar_datos(query)
                print("Adios {} {}".format(consulta[1].title(), consulta[2].title()))
                self.destroy()
            else:
                self.destroy()


if __name__ == '__main__':
    App().mainloop()
