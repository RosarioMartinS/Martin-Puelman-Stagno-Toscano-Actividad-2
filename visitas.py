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



def ingresa_visita(persona):
    """Guarda los datos de una persona al ingresar"""
    conn = sqlite3.connect('recepcion.db')
    

    q = f"""SELECT dni FROM personas   
            WHERE dni = '{persona.dni}'"""
            
            
    fecha= datetime.datetime.now().replace(microsecond=0).isoformat()
    resu = conn.execute(q)
    

    if resu.fetchone():
        print("ya existe")
    else:
        q = f"""INSERT INTO personas (dni, nombre, apellido, movil)
                VALUES ('{persona.dni}',
                        '{persona.nombre}',
                        '{persona.apellido}',
                        '{persona.movil}');"""
                        
        
        
        print(q)
        conn.execute(q)
        
    m = f"""INSERT INTO ingresos_egresos (dni, fechahora_in, destino)
                VALUES ('{persona.dni}',
                        '{fecha}',
                        '{p}');"""
    print(m)
    conn.execute(m)
    conn.commit()
                        
    conn.close()


def egresa_visita (dni):
    """Coloca fecha y hora de egreso al visitante con dni dado"""

    conn = sqlite3.connect('recepcion.db')
    q = f"""SELECT fechahora_out FROM ingresos_egresos WHERE dni LIKE '{dni}'"""
    resu = conn.execute(q)

    fecha_y_hora_actual = datetime.datetime.now().replace(microsecond=0).isoformat()

    if resu.fetchone() != None:
        print("El usuario ya egresó")
    else:
        conn.execute(f"""UPDATE ingresos_egresos
                SET fechahora_out = ?
                WHERE dni = ? ;""", (fecha_y_hora_actual, dni))
        conn.commit()
    conn.close()


def lista_visitantes_en_institucion ():
    """Devuelve una lista de objetos Persona presentes en la institución"""
    
    conn = sqlite3.connect('recepcion.db')
    q = f"""SELECT * FROM personas
            INNER JOIN ingresos_egresos ON personas.dni = ingresos_egresos.dni 
            WHERE fechahora_out IS NULL;"""

    resu = conn.execute(q)
    
    for fila in resu:       # Imprime las consultas
        print(fila)
    conn.close()        


def busca_vistantes(fecha_desde, fecha_hasta, destino, dni):
    """ busca visitantes segun criterios """
    conn = sqlite3.connect('recepcion.db')
    
    q = f"""SELECT dni FROM personas 
    INNER JOIN ingresos_egresos ON personas.dni = ingresos_egresos.dni 
    WHERE dni = '{dni}' AND fechahora_in='{fecha_desde}'AND fechahora_out=NULL AND destino=NULL
    """

    # INNER JOIN ingresos_egresos ON personas.dni = ingresos_egresos.dni
    
    resu = conn.execute(q)
    if resu.fetchone():
        print(q)
         
    
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


if __name__ == '__main__':
    iniciar()

    p = Persona('28123456', 'Álavarez', 'Ana', '02352-456789')

    ingresa_visita(p)

    doc = input("Igrese dni> ")
    apellido = input("Igrese apellido> ")
    nombre = input("nombre> ")
    movil = input("móvil > ")

    p = Persona(doc, apellido, nombre, movil)
    
    ingresa_visita(p)
    
    # lista_visitantes_en_institucion()
    