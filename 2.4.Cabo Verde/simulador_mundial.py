import random
import numpy as np
import pandas as pd
from itertools import combinations

from simulacion_base import simular_partido

# CONFIGURACIÓN
N_SIMULACIONES = 100000

# GRUPOS DEL MUNDIAL
GRUPOS = {
    "A": [
        "México",
        "Sudáfrica",
        "Corea del Sur",
        "República Checa"
    ],

    "B": [
        "Suiza",
        "Canadá",
        "Bosnia y Herzegovina",
        "Catar"
    ],

    "C": [
        "Brasil",
        "Marruecos",
        "Escocia",
        "Haití"
    ],

    "D": [
        "Estados Unidos",
        "Australia",
        "Paraguay",
        "Turquía"
    ],

    "E": [
        "Alemania",
        "Costa de Marfil",
        "Ecuador",
        "Curazao"
    ],

    "F": [
        "Países Bajos",
        "Japón",
        "Suecia",
        "Túnez"
    ],

    "G": [
        "Bélgica",
        "Egipto",
        "Irán",
        "Nueva Zelanda"
    ],

    "H": [
        "España",
        "Cabo Verde",
        "Uruguay",
        "Arabia Saudita"
    ],

    "I": [
        "Francia",
        "Noruega",
        "Senegal",
        "Irak"
    ],

    "J": [
        "Argentina",
        "Austria",
        "Argelia",
        "Jordania"
    ],

    "K": [
        "Colombia",
        "Portugal",
        "República Democrática del Congo",
        "Uzbekistán"
    ],

    "L": [
        "Inglaterra",
        "Croacia",
        "Ghana",
        "Panamá"
    ]
}

# CARGAR ELO
def cargar_elo(
    ruta="Data/elo_limpio.csv"
):

    df_elo = pd.read_csv(ruta)

    elo_dict = dict(
        zip(
            df_elo["equipo"],
            df_elo["elo_rating"]
        )
    )

    return elo_dict

# VERIFICAR LOS 48 EQUIPOS
def verificar_equipos(elo_dict):

    equipos_mundial = []

    for grupo in GRUPOS.values():

        equipos_mundial.extend(grupo)

    faltantes = [
        equipo
        for equipo in equipos_mundial
        if equipo not in elo_dict
    ]

    if faltantes:

        print("\nERROR: faltan ratings Elo para:")

        for equipo in faltantes:
            print(f"   - {equipo}")

        raise ValueError(
            "No se puede ejecutar la simulación "
            "porque faltan ratings Elo."
        )

    print(
        f"\nVerificación completada: "
        f"{len(equipos_mundial)} equipos encontrados."
    )

# CREAR TABLA
def crear_tabla(equipos):

    tabla = {}

    for equipo in equipos:

        tabla[equipo] = {

            "PJ": 0,
            "G": 0,
            "E": 0,
            "P": 0,
            "GF": 0,
            "GC": 0,
            "DG": 0,
            "Pts": 0
        }

    return tabla

# ACTUALIZAR TABLA
def actualizar_tabla(
    tabla,
    equipo_a,
    equipo_b,
    puntos_a,
    puntos_b,
    goles_a,
    goles_b
):
    tabla[equipo_a]["PJ"] += 1
    tabla[equipo_b]["PJ"] += 1

    tabla[equipo_a]["GF"] += goles_a
    tabla[equipo_a]["GC"] += goles_b

    tabla[equipo_b]["GF"] += goles_b
    tabla[equipo_b]["GC"] += goles_a

    tabla[equipo_a]["DG"] = (
        tabla[equipo_a]["GF"]
        -
        tabla[equipo_a]["GC"]
    )

    tabla[equipo_b]["DG"] = (
        tabla[equipo_b]["GF"]
        -
        tabla[equipo_b]["GC"]
    )

    tabla[equipo_a]["Pts"] += puntos_a
    tabla[equipo_b]["Pts"] += puntos_b

    if puntos_a == 3:

        tabla[equipo_a]["G"] += 1
        tabla[equipo_b]["P"] += 1

    elif puntos_b == 3:

        tabla[equipo_b]["G"] += 1
        tabla[equipo_a]["P"] += 1

    else:

        tabla[equipo_a]["E"] += 1
        tabla[equipo_b]["E"] += 1

# SIMULAR UN GRUPO
def simular_grupo(
    equipos,
    elo_dict
):
    tabla = crear_tabla(equipos)

    partidos = list(
        combinations(equipos, 2)
    )

    resultados_partidos = []

    for equipo_a, equipo_b in partidos:

        (
            puntos_a,
            puntos_b,
            goles_a,
            goles_b,
            resultado
        ) = simular_partido(
            equipo_a,
            equipo_b,
            elo_dict,
            neutral=True
        )

        actualizar_tabla(
            tabla,
            equipo_a,
            equipo_b,
            puntos_a,
            puntos_b,
            goles_a,
            goles_b
        )

        resultados_partidos.append(
            {
                "Equipo A": equipo_a,
                "Equipo B": equipo_b,
                "Goles A": goles_a,
                "Goles B": goles_b,
                "Resultado": resultado
            }
        )

    return tabla, resultados_partidos

# ORDENAR TABLA
def ordenar_grupo(
    tabla,
    elo_dict
):
    equipos = list(tabla.keys())

    equipos.sort(
        key=lambda equipo: (

            tabla[equipo]["Pts"],

            tabla[equipo]["DG"],

            tabla[equipo]["GF"],

            elo_dict[equipo]

        ),

        reverse=True
    )

    return equipos

# CONVERTIR TABLA A DATAFRAME
def convertir_tabla_dataframe(
    tabla,
    elo_dict
):

    equipos_ordenados = ordenar_grupo(
        tabla,
        elo_dict
    )

    filas = []

    for posicion, equipo in enumerate(
        equipos_ordenados,
        start=1
    ):

        fila = tabla[equipo].copy()

        fila["Pos"] = posicion
        fila["Equipo"] = equipo

        filas.append(fila)

    columnas = [
        "Pos",
        "Equipo",
        "PJ",
        "G",
        "E",
        "P",
        "GF",
        "GC",
        "DG",
        "Pts"
    ]

    return pd.DataFrame(
        filas,
        columns=columnas
    )

# SIMULAR LOS 12 GRUPOS
def simular_mundial(
    elo_dict
):
    resultados_grupos = {}

    terceros = []

    for grupo, equipos in GRUPOS.items():

        tabla, partidos = simular_grupo(
            equipos,
            elo_dict
        )

        ordenados = ordenar_grupo(
            tabla,
            elo_dict
        )

        resultados_grupos[grupo] = {
            "tabla": tabla,
            "partidos": partidos
        }

        # Tercer lugar del grupo
        equipo_tercero = ordenados[2]

        datos_tercero = tabla[
            equipo_tercero
        ].copy()

        datos_tercero["Equipo"] = (
            equipo_tercero
        )

        datos_tercero["Grupo"] = grupo

        terceros.append(
            datos_tercero
        )

    return resultados_grupos, terceros

# Simula todos los grupos excepto el Grupo H y obtiene el tercer lugar de cada uno de los once grupos restantes.
def simular_grupos_sin_h(elo_dict):
    terceros = []

    for grupo, equipos in GRUPOS.items():

        if grupo == "H":
            continue

        tabla, _ = simular_grupo(
            equipos,
            elo_dict
        )

        ordenados = ordenar_grupo(
            tabla,
            elo_dict
        )

        equipo_tercero = ordenados[2]

        datos_tercero = tabla[
            equipo_tercero
        ].copy()

        datos_tercero["Equipo"] = equipo_tercero
        datos_tercero["Grupo"] = grupo

        terceros.append(
            datos_tercero
        )

    return terceros

# ORDENAR LOS 12 TERCEROS
def ordenar_terceros(
    terceros,
    elo_dict
):
    terceros_ordenados = sorted(
        terceros,

        key=lambda tercero: (

            tercero["Pts"],

            tercero["DG"],

            tercero["GF"],

            elo_dict[
                tercero["Equipo"]
            ]
        ),
        reverse=True
    )

    return terceros_ordenados

# DATAFRAME DE LOS 12 TERCEROS
def terceros_dataframe(
    terceros,
    elo_dict
):
    terceros_ordenados = ordenar_terceros(
        terceros,
        elo_dict
    )

    filas = []

    for posicion, tercero in enumerate(
        terceros_ordenados,
        start=1
    ):

        filas.append({

            "Posicion": posicion,

            "Grupo": tercero["Grupo"],

            "Equipo": tercero["Equipo"],

            "PJ": tercero["PJ"],

            "G": tercero["G"],

            "E": tercero["E"],

            "P": tercero["P"],

            "GF": tercero["GF"],

            "GC": tercero["GC"],

            "DG": tercero["DG"],

            "Pts": tercero["Pts"]

        })

    return pd.DataFrame(
        filas
    )

# PROGRAMA PRINCIPAL
if __name__ == "__main__":

    print("=" * 75)
    print("SIMULACIÓN COMPLETA DE LOS 12 GRUPOS")
    print("COPA MUNDIAL 2026")
    print("=" * 75)

    # Semillas
    random.seed(42)
    np.random.seed(42)

    # Cargar Elo
    elo_dict = cargar_elo()

    verificar_equipos(
        elo_dict
    )

    # Mostrar ratings utilizados
    print("\nRATINGS ELO DE LOS 48 EQUIPOS:")

    for grupo, equipos in GRUPOS.items():

        print(f"\nGrupo {grupo}:")

        for equipo in equipos:

            print(
                f"   {equipo:<35} "
                f"{elo_dict[equipo]:.0f}"
            )

    # Una simulación completa
    resultados_grupos, terceros = (
        simular_mundial(
            elo_dict
        )
    )

    # Mostrar cada grupo
    for grupo in GRUPOS:

        print("\n")
        print(f"GRUPO {grupo}")

        datos = resultados_grupos[
            grupo
        ]

        for partido in datos["partidos"]:

            print(
                f"{partido['Equipo A']} "
                f"{partido['Goles A']}-"
                f"{partido['Goles B']} "
                f"{partido['Equipo B']}"
            )

        print("\nTabla:")

        df_grupo = convertir_tabla_dataframe(
            datos["tabla"],
            elo_dict
        )

        print(
            df_grupo.to_string(
                index=False
            )
        )

    # Terceros
    print("\n")
    print("LOS 12 TERCEROS LUGARES")

    df_terceros = terceros_dataframe(
        terceros,
        elo_dict
    )

    print(
        df_terceros.to_string(
            index=False
        )
    )

    # Cabo Verde
    fila_cv = df_terceros[
        df_terceros["Equipo"]
        == "Cabo Verde"
    ]

    if not fila_cv.empty:

        posicion_cv = int(
            fila_cv.iloc[0]["Posicion"]
        )

        print("\n")
        print("CABO VERDE")

        print(
            f"Cabo Verde terminó "
            f"{posicion_cv}° entre los 12 terceros."
        )

        if posicion_cv <= 8:

            print("En esta simulación, Cabo Verde estaría dentro de los ocho mejores terceros.")
        
        else:
            print("En esta simulación, Cabo Verde no estaría dentro de los ocho mejores terceros.")

    # Guardar CSV
    df_terceros.to_csv(
        "Data/terceros_una_simulacion.csv",
        index=False
    )

    print("\n")
    print(
        "Archivo generado:"
    )

    print(
        "Data/terceros_una_simulacion.csv"
    )