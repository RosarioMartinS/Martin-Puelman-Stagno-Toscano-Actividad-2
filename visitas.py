import sqlite3
import datetime
"""
Cada persona que ingresa debe quedar registrada con:

apellido y nombre
dni
fecha y hora de ingreso (en formato ISO8601 básico  ej. 20220414T0913 → 14 de abril de 2022 a las 9 horas, 13 minutos)
teléfono móvil 
destino (a qué oficina se dirige: rectoría, secretaría, tesorería, etc.)


En la base de datos existen dos tablas:

—------------------------
personas
—------------------------
dni	
apellido
nombre
movil


—------------------------
ingresos_egresos
—------------------------
id
dni
fechahora_in
fechahora_out
destino


Si la persona que ingresa ya tiene registrado su DNI (ej. un docente) no es necesario cargar los datos.

Al retirarse, utilizando el DNI se registra fecha y hora de egreso (en formato ISO8601 básico  ej. 20220414T0913)

Completar el módulo con las siguientes funciones:

ingresa_visita(persona)

Guarda los datos de una persona al ingresar


egresa_visita (dni)
Coloca fecha y hora de egreso al visitante con dni dado


lista_visitantes_en_institucion ()

Devuelve una lista de objetos Persona presentes en la institución 

 
busca_vistantes(fecha_desde, fecha_hasta, destino, dni)

Devuelve una lista de objetos Persona de acuerdo a uno o varios criterios (rango de fechas, a qué ámbito ingresó y/o dni)

"""

"""
datetime.datetime.now().replace(microsecond=0).isoformat()

devuelve fecha hora actual en formato ISO8601 simple

yyyymmddThh:mm:ss

"""

class Persona:
    def __init__(self, dni, apellido, nombre='', movil=''):
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido
        self.movil= movil



def ingresa_visita(persona, unDestino):
    """Guarda los datos de una persona al ingresar"""
    conn = sqlite3.connect('recepcion.db')
    
    fecha= datetime.datetime.now().replace(microsecond=0).isoformat()

    q = f"""SELECT dni 
            FROM personas   
            WHERE dni = '{persona.dni}';"""         # La persona esta ingresada?
    resuQ = conn.execute(q)

    personaConsultada = resuQ.fetchone()

    m = f"""SELECT fechahora_out                            
            FROM ingresos_egresos
            WHERE dni = '{persona.dni}';"""          # La persona salio del hotel?   
    resuM = conn.execute(m)

    salioDelHotel = resuM.fetchall()
    print(personaConsultada)

    if personaConsultada != (None,) and (None,) in salioDelHotel:     # La persona esta en la base Y todavia no salio del hotel
        print("La persona ya está ingresada en el hotel y todavía no se fue!")

    else:
        if personaConsultada == None:                           # La persona todavia no se ingreso a la base
            q = f"""INSERT INTO personas (dni, nombre, apellido, movil)
                    VALUES ('{persona.dni}',
                            '{persona.nombre}',
                            '{persona.apellido}',
                            '{persona.movil}');"""
    
            conn.execute(q)
            conn.commit()
            print("porfa")
    
        # Agrega datos de la persona a ingresos_egresos, ya sea por primera vez (persona no esta en la base) o nuevamente (persona ya esta en la base)
        m = f"""INSERT INTO ingresos_egresos (dni, fechahora_in, destino)               
                    VALUES ('{persona.dni}',
                            '{fecha}',
                            '{unDestino}');"""         

        conn.execute(m)
        conn.commit()
        print("Se completó existosamente el check in!")
                        
    conn.close()


def egresa_visita (dni):
    """Coloca fecha y hora de egreso al visitante con dni dado"""
    fecha_y_hora_actual = datetime.datetime.now().replace(microsecond=0).isoformat()

    conn = sqlite3.connect('recepcion.db')
    q = f"""SELECT fechahora_out 
        FROM ingresos_egresos 
        WHERE dni LIKE '{dni}' ;"""
    resu = conn.execute(q)
    yaEgreso = resu.fetchall()

    if not (None,) in yaEgreso:
        print("El usuario ya egresó")
    else:
        m = f"""UPDATE ingresos_egresos
                SET fechahora_out = ?
                WHERE dni = ? ;"""
        conn.execute(m, (fecha_y_hora_actual, dni, ))
        conn.commit()
        print("Check out Completado!")

    conn.close()


def lista_visitantes_en_institucion():
    """Devuelve una lista de objetos Persona presentes en la institución"""
    
    conn = sqlite3.connect('recepcion.db')
    q = f"""SELECT nombre, apellido, personas.dni, movil
        FROM personas
        INNER JOIN ingresos_egresos ON personas.dni = ingresos_egresos.dni 
        WHERE fechahora_out IS NULL;"""

    resu = conn.execute(q)
    listaVisitantes = resu.fetchall()
    
    if listaVisitantes != None:
        for fila in listaVisitantes:       # Imprime las consultas
            print(f"Nombre: {fila[0]}  |  Apellido: {fila[1]}  |  DNI: {fila[2]}  |  Movil: {fila[3]}")
    else:
        print("No hay visitantes en la institución!")  
    
    conn.close()      


def busca_vistantes(fecha_desde, fecha_hasta, destino, dni):
    """ busca visitantes segun criterios """
    criterios = [f'{fecha_desde}%', f'{fecha_hasta}%',destino,dni]
    criteriosFormatoSQL = [f"ingresos_egresos.fechahora_in", 
                            f"ingresos_egresos.fechahora_out", 
                            f"ingresos_egresos.destino", 
                            f"ingresos_egresos.dni"]
    c = ""

    for i in range(len(criterios)):
        if criterios[i] == "":
            criterios.pop(i)
            break

        if criterios[i] == "-%" or criterios[i] == "-":
            c += f""" {criteriosFormatoSQL[i]} IS NULL AND """

        elif criterios[i] != "%" and criterios[i] != "-":
            c += f""" {criteriosFormatoSQL[i]} LIKE '{criterios[i]}' AND """

        
    c = c[:-5] # elimina el ultimo OR

    conn = sqlite3.connect('recepcion.db')
    
    q = f"""SELECT DISTINCT nombre, apellido, personas.dni 
    FROM personas 
    INNER JOIN ingresos_egresos 
    ON personas.dni = ingresos_egresos.dni 
    WHERE {c} ;
    """
    resu = conn.execute(q)
    persona = resu.fetchall()

    if persona:
        print("Coincidencias encontradas:")
        for i in persona:
            print(f"Nombre: {i[0]}  |  Apellido: {i[1]}  |  DNI: {i[2]}")
    else:
        print("No se encotro nada")
    
    
    conn.close()


def iniciar():
    conn = sqlite3.connect('recepcion.db')

    qry = '''CREATE TABLE IF NOT EXISTS
                            personas
                    (dni TEXT NOT NULL PRIMARY KEY,
                     nombre   TEXT,
                     apellido TEXT  NOT NULL,
                     movil    TEXT  NOT NULL

           );'''

    conn.execute(qry)

    qry = '''CREATE TABLE IF NOT EXISTS
                            ingresos_egresos
                    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                     dni TEXT NOT NULL,
                     fechahora_in TEXT  NOT NULL,
                     fechahora_out TEXT,
                     destino TEXT

           );'''

    conn.execute(qry)

def menu():
    opcion = str(input("""
Ingrese 1, 2, 3 o 4 dependiendo de la acción que desee ejecutar:
    1. Check-In visitantes
    2. Check-Out visitantes
    3. Lista de personas hospedadas
    4. Consultar visitantes
    5. Salir
>>>"""))
    opciones = ['1','2','3','4','5']
    while opcion not in opciones:
        opcion = str(input("La opción solo puede ser 1, 2, 3, 4 o 5! Volver a intentar\n>>> "))

    return opcion



if __name__ == '__main__':
    iniciar()
    salir = False

    while salir == False:
        opcion = menu()
        if opcion == '1':
            print("-----------------------------------")
            doc = input("Ingrese dni> ")
            apellido = input("Igrese apellido> ")
            nombre = input("nombre> ")
            movil = input("móvil > ")
            destino = input("destino > ")
            print("-----------------------------------\n")

            p = Persona(doc, apellido, nombre, movil)
        
            ingresa_visita(p, destino)

        elif opcion == '2':
            dni_visitante = str(input("Ingrese el DNI de la persona > "))
            egresa_visita(dni_visitante)

        elif opcion == '3':
            lista_visitantes_en_institucion()

        elif opcion == '4':
            print("-----------------------------------\nIngrese - si quiere buscar los visitantes que NO presenten información en ese campo, no ingrese nada en los campos que no desee buscar")
            dni = input("Ingrese dni > ")
            fecha_in = input('Ingrese fecha de ingreso > ')
            fecha_out = input('Ingrese fecha de egreso > ')
            destino = input("Ingrese destino > ")
            print("-----------------------------------\n")

            busca_vistantes(fecha_in, fecha_out, destino, dni)
        
        elif opcion == '5':
            salir == True
            break


    quit()
        
    